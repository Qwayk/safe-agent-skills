from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote

from ..errors import SafetyError, ValidationError
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


def _build_plan(*, spec: OperationSpec, ctx: dict[str, Any], path: str, query: dict[str, str], form_fields: dict[str, str], body_json: Any | None, has_multipart: bool, out_path: str | None) -> dict[str, Any]:
    risk = "low" if not spec.is_write else ("high" if spec.method == "DELETE" else "medium")
    reasons = [spec.api_group]
    if spec.beta:
        reasons.append("beta")
    if spec.gated:
        reasons.append(spec.gated)
    if spec.requires_out:
        reasons.append("sensitive-or-binary-output")
    if spec.is_write:
        reasons.append("write-operation")

    plan = {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].env_fingerprint(),
        "command": ctx.get("command_str"),
        "selector": {
            "area": spec.area,
            "op_key": spec.op_key,
            "operation_id": spec.operation_id,
        },
        "risk_level": risk,
        "risk_reasons": reasons,
        "baseline": {
            "env_fingerprint": ctx["cfg"].env_fingerprint(),
            "method": spec.method,
            "path": path,
            "query": dict(query),
            "auth_scope": spec.auth_scope,
        },
        "request_plan": {
            "input_style": spec.input_style,
            "path": path,
            "query": dict(query),
            "fixed_form_fields": dict(spec.fixed_form_fields),
            "form_fields": dict(form_fields),
            "body_json_present": body_json is not None,
            "multipart_present": has_multipart,
            "out_path": out_path,
        },
        "verification_plan": {
            "method": "best_effort_read_back" if spec.is_write else "api_response_only",
            "notes": "The runner uses same-path GET read-back when available, otherwise it falls back to API success and Cloudinary identifiers when possible.",
        },
    }
    return _attach_write_safety_contract(plan=plan, spec=spec, path=path)


def _validate_plan_for_apply(*, plan: dict[str, Any], spec: OperationSpec, ctx: dict[str, Any], path: str, query: dict[str, str]) -> None:
    baseline = plan.get("baseline")
    selector = plan.get("selector")
    if not isinstance(baseline, dict) or not isinstance(selector, dict):
        raise SafetyError("Refusing to apply: plan is missing baseline or selector metadata.")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].env_fingerprint()):
        raise SafetyError("Refusing to apply: plan env_fingerprint does not match the current environment.")
    if str(selector.get("area") or "") != spec.area or str(selector.get("op_key") or "") != spec.op_key:
        raise SafetyError("Refusing to apply: plan target does not match the requested Cloudinary operation.")
    if str(baseline.get("method") or "") != spec.method or str(baseline.get("path") or "") != path:
        raise SafetyError("Refusing to apply: plan method or path does not match the current request.")
    if dict(baseline.get("query") or {}) != dict(query):
        raise SafetyError("Refusing to apply: plan query parameters do not match the current request.")


def _needs_ack(spec: OperationSpec) -> bool:
    if spec.method == "DELETE":
        return True
    if spec.api_group == "provisioning" and "/access_keys" in spec.path_template:
        return True
    return False


def _best_effort_verify(*, spec: OperationSpec, ctx: dict[str, Any], path: str, query: dict[str, str], form_fields: dict[str, str], response_json: Any | None) -> dict[str, Any]:
    if not spec.is_write:
        return {"ok": True, "method": "api_response_only"}

    same_get = find_by_method_path(method="GET", path_template=spec.path_template)
    if same_get is not None and same_get.auth_scope == spec.auth_scope:
        verify_response = ctx["http"].request_allow_error(
            "GET",
            ctx["base_url"] + path,
            headers=ctx["headers"],
            params=query or None,
        )
        if spec.method == "DELETE":
            return {
                "ok": verify_response.status >= 400,
                "method": "read_back_get_same_path_expected_missing",
                "http_status": verify_response.status,
            }
        body = verify_response.maybe_json()
        return {
            "ok": verify_response.status < 400,
            "method": "read_back_get_same_path",
            "http_status": verify_response.status,
            "evidence": body if isinstance(body, dict) else None,
        }

    if spec.auth_scope.startswith("product") and isinstance(response_json, dict):
        asset_id = str(response_json.get("asset_id") or "").strip()
        if asset_id and ctx["cfg"].has_product_basic_auth():
            verify = ctx["http"].request_allow_error(
                "GET",
                ctx["cfg"].product_v1_base_url() + f"/resources/{asset_id}",
                headers=ctx["cfg"].product_auth_header(),
            )
            return {
                "ok": verify.status < 400,
                "method": "admin_get_by_asset_id",
                "http_status": verify.status,
                "asset_id": asset_id,
            }

    if spec.auth_scope.startswith("product") and ctx["cfg"].has_product_basic_auth():
        public_id = str(form_fields.get("public_id") or "").strip()
        resource_type = str(form_fields.get("resource_type") or spec.path_defaults.get("resource_type") or "").strip()
        delivery_type = str(form_fields.get("type") or "upload").strip()
        if public_id and resource_type:
            verify = ctx["http"].request_allow_error(
                "GET",
                ctx["cfg"].product_v1_base_url() + f"/resources/{resource_type}/{delivery_type}/{public_id}",
                headers=ctx["cfg"].product_auth_header(),
            )
            if spec.method == "DELETE":
                return {
                    "ok": verify.status >= 400,
                    "method": "admin_get_by_public_id_expected_missing",
                    "http_status": verify.status,
                    "public_id": public_id,
                }
            return {
                "ok": verify.status < 400,
                "method": "admin_get_by_public_id",
                "http_status": verify.status,
                "public_id": public_id,
            }

    return {"ok": True, "method": "api_response_success"}


def _write_out(*, ctx: dict[str, Any], out_path: str, overwrite: bool, body: bytes, maybe_json: Any | None) -> str:
    target = resolve_safe_out_path(project_dir=Path(ctx["project_dir"]), out_path=out_path, overwrite=overwrite)
    if maybe_json is not None:
        target.write_text(json.dumps(maybe_json, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        target.write_bytes(body)
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
    multipart_files: dict[str, Any] | None = None
    if getattr(args, "multipart_spec_file", None):
        multipart_fields, multipart_files = _load_multipart(str(args.multipart_spec_file))

    if multipart_fields:
        form_fields.update(multipart_fields)

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
        has_multipart=bool(multipart_files),
        out_path=out_path,
    )

    plan_in = str(ctx.get("plan_in") or "").strip()
    if spec.is_write and plan_in:
        plan_obj = read_json_file(plan_in)
        if not isinstance(plan_obj, dict):
            raise ValidationError("Plan file must be a JSON object")
        _validate_plan_for_apply(plan=plan_obj, spec=spec, ctx=ctx, path=path, query=query)
        plan = _attach_write_safety_contract(plan=plan_obj, spec=spec, path=path)

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
        if _needs_ack(spec) and not bool(ctx.get("ack_irreversible")):
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

    if (not spec.is_write) or bool(ctx.get("apply")):
        base_url, headers = ctx["cfg"].runtime_base_and_headers_for(spec=spec, need_credentials=True)
        ctx["base_url"] = base_url
        ctx["headers"] = headers

    response = ctx["http"].request(
        spec.method,
        base_url + path,
        headers=headers,
        params=query or None,
        json_body=body_json if spec.input_style == "json" else None,
        data=form_fields or None,
        files=multipart_files or None,
    )
    response_json = response.maybe_json()

    persisted_out = None
    if out_path:
        persisted_out = _write_out(
            ctx=ctx,
            out_path=out_path,
            overwrite=overwrite,
            body=response.body,
            maybe_json=response_json,
        )

    if not spec.is_write:
        payload: dict[str, Any] = {
            "ok": True,
            "dry_run": False,
            "operation": {
                "area": spec.area,
                "op_key": spec.op_key,
                "method": spec.method,
                "path": path,
                "query": query,
            },
            "http_status": response.status,
        }
        if persisted_out:
            payload["out"] = persisted_out
        elif response_json is not None:
            payload["response"] = response_json
        else:
            payload["response_text"] = response.text()
        ctx["audit"].write("operation.read", {"operation_id": spec.operation_id, "status": response.status, "out": persisted_out})
        ctx["out"].emit(payload)
        return 0

    verification = _best_effort_verify(
        spec=spec,
        ctx=ctx,
        path=path,
        query=query,
        form_fields=form_fields,
        response_json=response_json,
    )
    receipt = {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].env_fingerprint(),
        "selector": {"area": spec.area, "op_key": spec.op_key, "operation_id": spec.operation_id},
        "request": {"method": spec.method, "path": path, "query": query},
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {"approved": True, "flag": "--ack-no-snapshot"},
        "recovery": plan.get("recovery"),
        "changed": True,
        "verification": verification,
        "out_path": persisted_out,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    ctx["audit"].write("operation.apply", {"operation_id": spec.operation_id, "status": response.status, "receipt_out": receipt_path})
    payload = {
        "ok": True,
        "dry_run": False,
        "operation": {"area": spec.area, "op_key": spec.op_key, "method": spec.method, "path": path},
        "http_status": response.status,
        "receipt": receipt,
        "receipt_out": receipt_path,
    }
    if persisted_out:
        payload["out"] = persisted_out
    elif response_json is not None and spec.sensitivity == "none":
        payload["response"] = response_json
    ctx["out"].emit(payload)
    return 0
