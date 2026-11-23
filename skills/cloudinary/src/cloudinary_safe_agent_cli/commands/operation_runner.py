from __future__ import annotations

import json
import os
import re
import tempfile
import time
from hashlib import sha256
from pathlib import Path
from typing import Any
from urllib.parse import quote

from ..errors import SafetyError, ToolError, ValidationError
from ..inventory import OperationSpec, find_by_method_path, require_operation
from ..json_files import read_json_file, write_json_file
from ..paths import resolve_safe_out_path

_COLON_PARAM_RE = re.compile(r":([A-Za-z_][A-Za-z0-9_]*)")
_BRACE_PARAM_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")
_INNERMOST_OPTIONAL_RE = re.compile(r"\([^()]*\)")
BEFORE_STATE_REFUSAL_REASON = (
    "Refusing to apply: this Cloudinary write has no saved before-state snapshot or provider backup. "
    "Review the plan, confirm the recovery limit, then re-run with --ack-no-snapshot."
)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _build_no_recovery_contract() -> dict[str, Any]:
    return {
        "automatic_rollback": False,
        "backups": [],
        "snapshots": [],
        "rollback_plan": None,
        "restore_note": (
            "This write path has not saved or recorded a Cloudinary backup before apply. "
            "Use explicit Cloudinary backup or restore endpoints only after a separate review."
        ),
    }


def _build_before_state_contract(*, spec: OperationSpec, path: str) -> dict[str, Any]:
    return {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "approval_required": "--ack-no-snapshot",
        "operation": spec.operation_id,
        "target": {
            "area": spec.area,
            "op_key": spec.op_key,
            "method": spec.method,
            "path": path,
        },
        "saved_path": None,
        "provider_backup_id": None,
        "reason": (
            "No useful before-state snapshot or provider backup is captured for this Cloudinary write. "
            "The write may still run after the reviewed plan and explicit no-snapshot approval."
        ),
    }


def _build_before_state_refusal_verification_plan() -> dict[str, Any]:
    return {
        "method": "best_effort_after_apply",
        "status": "requires-no-snapshot-approval",
        "requires_no_snapshot_approval": True,
        "notes": (
            "Apply can run after explicit no-snapshot approval, then records provider response "
            "and best-effort read-back when available."
        ),
    }


def _attach_write_safety_contract(*, plan: dict[str, Any], spec: OperationSpec, path: str) -> dict[str, Any]:
    if not spec.is_write:
        return plan
    previous_verification = plan.get("verification_plan")
    plan["before_state"] = _build_before_state_contract(spec=spec, path=path)
    plan["recovery"] = _build_no_recovery_contract()
    plan["verification_plan"] = _build_before_state_refusal_verification_plan()
    plan["post_apply_verification_plan"] = previous_verification or {
        "method": "best_effort_read_back",
        "notes": "After approved apply, verify with read-back when available or provider API success evidence.",
    }
    return plan


def _parse_kv_list(values: list[str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in values or []:
        text = str(raw or "")
        if "=" not in text:
            raise ValidationError(f"Invalid key=value: {text!r}")
        key, value = text.split("=", 1)
        key = key.strip()
        if not key:
            raise ValidationError(f"Invalid key=value (empty key): {text!r}")
        out[key] = value
    return out


def _optional_group_needed(group_text: str, values: dict[str, str]) -> bool:
    names = set(_COLON_PARAM_RE.findall(group_text)) | set(_BRACE_PARAM_RE.findall(group_text))
    return all(str(values.get(name, "") or "").strip() for name in names)


def _replace_required_placeholders(text: str, values: dict[str, str]) -> str:
    def _replace_colon(match: re.Match[str]) -> str:
        key = match.group(1)
        value = str(values.get(key, "") or "").strip()
        if not value:
            raise ValidationError(f"Missing path param: {key}")
        return quote(value, safe="")

    def _replace_brace(match: re.Match[str]) -> str:
        key = match.group(1)
        value = str(values.get(key, "") or "").strip()
        if not value:
            raise ValidationError(f"Missing path param: {key}")
        return quote(value, safe="")

    out = _COLON_PARAM_RE.sub(_replace_colon, text)
    out = _BRACE_PARAM_RE.sub(_replace_brace, out)
    return out


def _resolve_path_template(spec: OperationSpec, *, path_params: dict[str, str], query_params: dict[str, str]) -> tuple[str, dict[str, str]]:
    merged_path = dict(spec.path_defaults)
    merged_path.update({str(k): str(v) for k, v in path_params.items()})
    raw_path, _, raw_query = spec.path_template.partition("?")
    path = raw_path

    while True:
        match = _INNERMOST_OPTIONAL_RE.search(path)
        if not match:
            break
        group = match.group(0)
        inner = group[1:-1]
        replacement = inner if _optional_group_needed(inner, merged_path) else ""
        path = path[: match.start()] + replacement + path[match.end() :]

    path = _replace_required_placeholders(path, merged_path)
    if not path.startswith("/"):
        path = "/" + path

    resolved_query = dict(spec.fixed_query)
    resolved_query.update({str(k): str(v) for k, v in query_params.items()})

    if raw_query:
        for part in [chunk for chunk in raw_query.split("&") if chunk]:
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            value = value.strip()
            if value.startswith(":"):
                name = value[1:]
                actual = resolved_query.get(name) or merged_path.get(name) or query_params.get(name)
                if not actual:
                    raise ValidationError(f"Missing query param: {name}")
                resolved_query[key] = str(actual)
            else:
                resolved_query[key] = value

    return path, resolved_query


def _load_multipart(spec_file: str) -> tuple[dict[str, str], dict[str, Any]]:
    obj = read_json_file(spec_file)
    if not isinstance(obj, dict):
        raise ValidationError("Multipart spec must be a JSON object")
    fields = obj.get("fields") or {}
    files = obj.get("files") or []
    if not isinstance(fields, dict):
        raise ValidationError("Multipart spec 'fields' must be an object")
    if not isinstance(files, list):
        raise ValidationError("Multipart spec 'files' must be a list")

    request_files: dict[str, Any] = {}
    for entry in files:
        if not isinstance(entry, dict):
            raise ValidationError("Multipart spec file entries must be JSON objects")
        name = str(entry.get("name") or "").strip()
        file_path = str(entry.get("path") or "").strip()
        if not name or not file_path:
            raise ValidationError("Multipart spec file entries need 'name' and 'path'")
        path = Path(file_path)
        if not path.exists():
            raise ValidationError(f"Multipart file not found: {path}")
        filename = str(entry.get("filename") or path.name)
        content_type = str(entry.get("content_type") or "").strip() or None
        content = path.read_bytes()
        request_files[name] = (filename, content, content_type) if content_type else (filename, content)

    return ({str(k): str(v) for k, v in fields.items()}, request_files)


def _visible_fields(value: Any, cfg) -> Any:
    if isinstance(value, dict):
        return {
            key: "[REDACTED]"
            if key.lower().endswith(("api_key", "secret", "token", "password", "signature", "authorization"))
            else _visible_fields(item, cfg)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_visible_fields(item, cfg) for item in value]
    return cfg.redact(value) if isinstance(value, str) else value


def _build_plan(*, spec: OperationSpec, ctx: dict[str, Any], path: str, query: dict[str, str], form_fields: dict[str, str], body_json: Any | None, multipart_files: dict[str, tuple], out_path: str | None) -> dict[str, Any]:
    cfg = ctx["cfg"]
    confirm = _needs_ack(spec, form_fields)
    risk = "low" if not spec.is_write else ("high" if confirm else "medium")
    reasons = [spec.api_group]
    if spec.beta:
        reasons.append("beta")
    if spec.gated:
        reasons.append(spec.gated)
    if spec.requires_out:
        reasons.append("sensitive-or-binary-output")
    if spec.is_write:
        reasons.append("write-operation")

    files = {
        key: {
            "filename": part[0],
            "sha256": sha256(part[1]).hexdigest(),
            "content_type": part[2] if len(part) == 3 else None,
        }
        for key, part in multipart_files.items()
    }
    request_hash = sha256(
        json.dumps([path, query, form_fields, body_json, files], sort_keys=True).encode("utf-8")
    ).hexdigest()
    plan = {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].env_fingerprint(),
        "command": spec.command,
        "selector": {
            "area": spec.area,
            "op_key": spec.op_key,
            "operation_id": spec.operation_id,
        },
        "risk_level": risk,
        "risk_reasons": reasons,
        "requires_ack_irreversible": confirm,
        "baseline": {
            "env_fingerprint": ctx["cfg"].env_fingerprint(),
            "method": spec.method,
            "path": path,
            "query": _visible_fields(query, cfg),
            "auth_scope": spec.auth_scope,
            "request_sha256": request_hash,
        },
        "request_plan": {
            "input_style": spec.input_style,
            "path": path,
            "query": _visible_fields(query, cfg),
            "fixed_form_fields": dict(spec.fixed_form_fields),
            "form_fields": _visible_fields(form_fields, cfg),
            "body_json_present": body_json is not None,
            "body_json": _visible_fields(body_json, cfg),
            "multipart_present": bool(files),
            "files": _visible_fields(files, cfg),
            "out_path": out_path,
        },
        "verification_plan": {
            "method": "best_effort_read_back" if spec.is_write else "api_response_only",
            "notes": "The runner uses same-path GET read-back when available, otherwise it falls back to API success and Cloudinary identifiers when possible.",
        },
    }
    return _attach_write_safety_contract(plan=plan, spec=spec, path=path)


def _validate_plan_for_apply(*, plan: dict[str, Any], current: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    selector = plan.get("selector")
    if not isinstance(baseline, dict) or not isinstance(selector, dict):
        raise SafetyError("Refusing to apply: plan is missing baseline or selector metadata.")
    expected = current["baseline"]
    if baseline.get("env_fingerprint") != expected["env_fingerprint"]:
        raise SafetyError("Refusing to apply: plan env_fingerprint does not match the current environment.")
    if selector != current["selector"] or baseline.get("auth_scope") != expected["auth_scope"]:
        raise SafetyError("Refusing to apply: plan target does not match the requested Cloudinary operation.")
    if baseline.get("method") != expected["method"] or baseline.get("path") != expected["path"]:
        raise SafetyError("Refusing to apply: plan method or path does not match the current request.")
    if baseline.get("query") != expected["query"]:
        raise SafetyError("Refusing to apply: plan query parameters do not match the current request.")
    if not baseline.get("request_sha256"):
        raise SafetyError("Save and review a new Cloudinary plan before applying.")
    if baseline["request_sha256"] != expected["request_sha256"]:
        raise SafetyError("The body, form fields, or files changed. Review and save a new plan.")


def _is_destroy(spec: OperationSpec) -> bool:
    return spec.area == "upload" and spec.op_key in {"destroy-by-asset-id", "destroy-by-public-id"}


def _needs_ack(spec: OperationSpec, form_fields: dict[str, str]) -> bool:
    if spec.method == "DELETE" or _is_destroy(spec):
        return True
    if spec.api_group == "provisioning" and "/access_keys" in spec.path_template:
        return True
    return (
        spec.area == "upload"
        and spec.op_key == "upload-signed"
        and form_fields.get("overwrite", "false").strip().lower() not in {"false", "0"}
    )


def _verify_get(
    spec: OperationSpec,
    ctx: dict[str, Any],
    *,
    url: str,
    headers: dict[str, str],
    query: dict[str, str] | None = None,
    expected: dict[str, Any] | None = None,
    expect_missing: bool = False,
) -> dict[str, Any]:
    try:
        reply = ctx["http"].request_allow_error(
            "GET", url, headers=headers, params=query, private=spec.requires_out
        )
    except RuntimeError:
        return {"ok": None, "method": "follow_up_unavailable"}
    if expect_missing and reply.status == 404:
        return {"ok": True, "method": "target_missing", "http_status": reply.status}
    if not 200 <= reply.status < 300:
        return {"ok": None, "method": "follow_up_unavailable", "http_status": reply.status}
    if expect_missing:
        return {"ok": False, "method": "target_still_visible", "http_status": reply.status}
    body = reply.maybe_json()
    if expected and isinstance(body, dict) and all(
        key in body and json.dumps(value, sort_keys=True) == json.dumps(body[key], sort_keys=True)
        for key, value in expected.items()
    ):
        return {"ok": True, "method": "values_match", "http_status": reply.status}
    return {
        "ok": None,
        "method": "requested_values_not_confirmed",
        "http_status": reply.status,
    }


def _best_effort_verify(
    *,
    spec: OperationSpec,
    ctx: dict[str, Any],
    path: str,
    query: dict[str, str],
    form_fields: dict[str, str],
    body_json: Any | None,
    response_json: Any | None,
) -> dict[str, Any]:
    # An accepted request can still be unverified. Receipts only carry the
    # outcome of the follow-up, never the contents of the provider's reply.
    cfg = ctx["cfg"]
    if spec.requires_out:
        return {"ok": None, "method": "private_result_saved"}
    response = response_json if isinstance(response_json, dict) else {}
    if _is_destroy(spec):
        if response.get("result") == "not found":
            return {"ok": None, "method": "provider_reported_not_found"}
        if response.get("result") != "ok":
            return {"ok": None, "method": "deletion_not_confirmed"}
        dest = None
        asset_id = form_fields.get("asset_id")
        public_id = form_fields.get("public_id")
        if asset_id:
            dest = f"/resources/{quote(asset_id, safe='')}"
        elif public_id:
            resource_type = path.split("/")[1]
            delivery = quote(form_fields.get("type", "upload"), safe="")
            dest = f"/resources/{resource_type}/{delivery}/{quote(public_id, safe='')}"
        if dest:
            return _verify_get(
                spec, ctx, url=cfg.product_v1_base_url() + dest,
                headers=cfg.product_auth_header(), expect_missing=True,
            )
    same_get = find_by_method_path(method="GET", path_template=spec.path_template)
    if same_get is not None and same_get.auth_scope == spec.auth_scope and not same_get.requires_out:
        expected = body_json if isinstance(body_json, dict) else form_fields
        return _verify_get(
            spec, ctx, url=ctx["base_url"] + path, headers=ctx["headers"],
            query=query or None, expected=expected, expect_missing=spec.method == "DELETE",
        )
    asset_id = response.get("asset_id")
    version = response.get("version")
    if (
        spec.area == "upload" and spec.op_key in {"upload-signed", "upload-unsigned"}
        and isinstance(asset_id, str) and asset_id and version is not None
        and cfg.has_product_basic_auth()
    ):
        return _verify_get(
            spec, ctx, url=cfg.product_v1_base_url() + f"/resources/{quote(asset_id, safe='')}",
            headers=cfg.product_auth_header(), expected={"asset_id": asset_id, "version": version},
        )
    return {"ok": None, "method": "provider_reply_only"}


def _write_out(
    target: Path, *, overwrite: bool, body: bytes, maybe_json: Any | None, private: bool
) -> str:
    payload = (
        (json.dumps(maybe_json, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        if maybe_json is not None
        else body
    )
    if not private:
        with target.open("wb" if overwrite else "xb") as stream:
            stream.write(payload)
        return str(target)
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
        temp_path = Path(stream.name)
        try:
            stream.write(payload)
            stream.close()
            if overwrite:
                os.replace(temp_path, target)
            else:
                os.link(temp_path, target)
        finally:
            temp_path.unlink(missing_ok=True)
    return str(target)


def cmd_operation_call(args: Any, ctx: dict[str, Any]) -> int:
    spec = require_operation(
        area=str(getattr(args, "operation_area", "") or "").strip(),
        op_key=str(getattr(args, "operation_key", "") or "").strip(),
    )
    path_params = _parse_kv_list(getattr(args, "path_param", []))
    query_params = _parse_kv_list(getattr(args, "query", []))
    form_fields = _parse_kv_list(getattr(args, "form_field", []))
    path, query = _resolve_path_template(spec, path_params=path_params, query_params=query_params)

    body_json = None
    if getattr(args, "body_json_file", None):
        body_json = read_json_file(str(args.body_json_file))

    multipart_fields: dict[str, str] | None = None
    multipart_files: dict[str, Any] = {}
    if getattr(args, "multipart_spec_file", None):
        multipart_fields, multipart_files = _load_multipart(str(args.multipart_spec_file))

    if multipart_fields:
        form_fields.update(multipart_fields)

    if body_json is not None and (
        spec.input_style not in {"json", "json_or_form"} or form_fields or multipart_files
    ):
        raise ValidationError("Use a JSON body only with a command that accepts it, without form fields or files.")
    if (form_fields or multipart_files) and spec.input_style not in {"form", "json_or_form", "multipart_or_form"}:
        raise ValidationError("This command does not accept form fields or files.")
    if multipart_files and spec.input_style != "multipart_or_form":
        raise ValidationError("This command does not accept attached files.")
    for key, value in spec.fixed_form_fields.items():
        if key in form_fields and form_fields[key] != value:
            raise ValidationError(f"Form field {key!r} is fixed for this command and must be {value!r}.")
        form_fields[key] = value

    for key, value in spec.fixed_query.items():
        if key in query and query[key] != value:
            raise ValidationError(f"Query parameter {key!r} is fixed for this command and must be {value!r}.")
        query[key] = value

    if spec.body_required and body_json is None and not form_fields and not multipart_files:
        raise ValidationError("This Cloudinary operation requires a request body. Supply --body-json-file, --form-field, or --multipart-spec-file.")
    if spec.area == "upload" and spec.op_key == "upload-signed":
        form_fields.setdefault("overwrite", "false")

    base_url, headers = ctx["cfg"].runtime_base_and_headers_for(spec=spec, need_credentials=False)
    ctx["base_url"] = base_url
    ctx["headers"] = headers

    out_path = str(getattr(args, "out", "") or "").strip() or None
    overwrite = bool(getattr(args, "overwrite", False))
    plan = _build_plan(
        spec=spec,
        ctx=ctx,
        path=path,
        query=query,
        form_fields=form_fields,
        body_json=body_json,
        multipart_files=multipart_files,
        out_path=out_path,
    )

    plan_in = str(ctx.get("plan_in") or "").strip()
    if spec.is_write and plan_in:
        plan_obj = read_json_file(plan_in)
        if not isinstance(plan_obj, dict):
            raise ValidationError("Plan file must be a JSON object")
        _validate_plan_for_apply(plan=plan_obj, current=plan)

    if spec.is_write and not bool(ctx.get("apply")):
        plan_out = ctx.get("plan_out")
        plan_path = write_json_file(plan_out, plan) if plan_out else None
        ctx["audit"].write("operation.plan", {"operation_id": spec.operation_id, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    if spec.is_write:
        if not bool(ctx.get("apply")):
            raise SafetyError("Refusing to apply: this command is dry-run by default (pass --apply).")
        if not bool(ctx.get("yes")):
            raise SafetyError("Refusing to apply: Cloudinary writes require --yes.")
        if _needs_ack(spec, form_fields) and not bool(ctx.get("ack_irreversible")):
            raise SafetyError("Refusing to apply: this Cloudinary operation also needs --ack-irreversible.")

    if spec.requires_out and ((not spec.is_write) or bool(ctx.get("apply"))) and not out_path:
        raise SafetyError("Refusing to print sensitive or binary Cloudinary output. Re-run with --out.")

    if spec.is_write and bool(ctx.get("apply")) and not bool(ctx.get("ack_no_snapshot")):
        ctx["audit"].write(
            "operation.refused",
            {
                "operation_id": spec.operation_id,
                "reason": BEFORE_STATE_REFUSAL_REASON,
                "before_state": plan.get("before_state"),
            },
        )
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": False,
                "refused": True,
                "reasons": [BEFORE_STATE_REFUSAL_REASON],
                "refusal_type": "SafetyError",
                "plan": plan,
                "plan_out": None,
                "verification_plan": _build_before_state_refusal_verification_plan(),
            }
        )
        return 0

    if spec.is_write and not plan_in:
        raise SafetyError("Save and review a preview, then pass it with --plan-in before applying.")

    target = (
        resolve_safe_out_path(project_dir=Path(ctx["project_dir"]), out_path=out_path, overwrite=overwrite)
        if out_path else None
    )
    base_url, headers = ctx["cfg"].runtime_base_and_headers_for(spec=spec, need_credentials=True)
    ctx["base_url"] = base_url
    ctx["headers"] = headers

    response = ctx["http"].request(
        spec.method,
        base_url + path,
        headers=headers,
        params=query or None,
        json_body=body_json,
        data=form_fields or None,
        files=multipart_files or None,
        allow_error=spec.requires_out,
        private=spec.requires_out,
    )
    if not 200 <= response.status < 300:
        raise ToolError(f"Cloudinary returned HTTP {response.status} for {spec.command}.")
    response_json = response.maybe_json()

    persisted_out = None
    output_error = None
    if target is not None:
        try:
            persisted_out = _write_out(
                target, overwrite=overwrite, body=response.body, maybe_json=response_json,
                private=spec.requires_out,
            )
        except OSError as exc:
            output_error = f"Cloudinary replied, but the result could not be saved to {target}: {exc.strerror}."
            if not spec.is_write:
                raise ToolError(output_error) from None

    if not spec.is_write:
        payload: dict[str, Any] = {
            "ok": True,
            "dry_run": False,
            "operation": {
                "area": spec.area,
                "op_key": spec.op_key,
                "method": spec.method,
                "path": path,
                "query": _visible_fields(query, ctx["cfg"]),
            },
            "http_status": response.status,
        }
        if persisted_out:
            payload["out"] = persisted_out
        elif response_json is not None:
            payload["response"] = _visible_fields(response_json, ctx["cfg"])
        else:
            payload["response_text"] = ctx["cfg"].redact(response.text())
        ctx["audit"].write("operation.read", {"operation_id": spec.operation_id, "status": response.status, "out": persisted_out})
        ctx["out"].emit(payload)
        return 0

    verification = _best_effort_verify(
        spec=spec,
        ctx=ctx,
        path=path,
        query=query,
        form_fields=form_fields,
        body_json=body_json,
        response_json=response_json,
    )
    if output_error and spec.requires_out:
        verification = {"ok": None, "method": "private_result_not_saved"}
    no_change = isinstance(response_json, dict) and (
        (_is_destroy(spec) and response_json.get("result") == "not found")
        or (spec.area == "upload" and response_json.get("existing") is True)
    )
    receipt = {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].env_fingerprint(),
        "selector": {"area": spec.area, "op_key": spec.op_key, "operation_id": spec.operation_id},
        "request": {
            "method": spec.method, "path": path, "query": plan["baseline"]["query"],
            "request_sha256": plan["baseline"]["request_sha256"],
        },
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {"approved": True, "flag": "--ack-no-snapshot"},
        "recovery": plan.get("recovery"),
        "changed": False if no_change else True if verification["ok"] is True else None,
        "provider_replied": True,
        "verification": verification,
        "out_path": persisted_out,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = None
    if receipt_out:
        try:
            receipt_path = write_json_file(receipt_out, receipt)
        except OSError as exc:
            output_error = output_error or f"Cloudinary replied, but the receipt could not be saved: {exc.strerror}."
    ctx["audit"].write("operation.apply", {"operation_id": spec.operation_id, "status": response.status, "receipt_out": receipt_path})
    payload = {
        "ok": output_error is None,
        "dry_run": False,
        "operation": {"area": spec.area, "op_key": spec.op_key, "method": spec.method, "path": path},
        "http_status": response.status,
        "receipt": receipt,
        "receipt_out": receipt_path,
    }
    if persisted_out:
        payload["out"] = persisted_out
    elif response_json is not None and spec.sensitivity == "none":
        payload["response"] = _visible_fields(response_json, ctx["cfg"])
    if output_error:
        payload["error"] = output_error
    ctx["out"].emit(payload)
    return 1 if output_error else 0
