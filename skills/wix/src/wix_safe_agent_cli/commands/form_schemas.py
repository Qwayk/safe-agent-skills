from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested


COMMAND_FAMILY = "form-schemas"
BASE_PATH = "/form-schema-service/v4"


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_object(raw: Any, *, field: str, allow_empty: bool = False) -> dict[str, Any]:
    value = _coerce_text(raw, field=field)
    if value.startswith("@"):
        path = Path(value[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        value = path.read_text(encoding="utf-8").strip()
    try:
        payload = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not allow_empty and not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
    )


def _request_json(
    *,
    method: str,
    path: str,
    headers: dict[str, str],
    params: dict[str, Any] | None,
    json_body: dict[str, Any] | None,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
        request_headers["Content-Type"] = "application/json"
    client = HttpClient(timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")), user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=ctx["cfg"].base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=params,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _emit_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, SafetyError):
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "refused": True,
                "reasons": [str(exc)],
                "refusal_type": "SafetyError",
                "method": method,
            }
        )
        return 0
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _run_read(
    *,
    method_name: str,
    http_method: str,
    path: str,
    ctx: dict[str, Any],
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], params=params, json_body=body, ctx=ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if params:
        request["params"] = params
    if body is not None:
        request["body"] = body
    out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": request, "response": response}
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _build_plan(
    *,
    method_name: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    requires_ack: bool,
    risk_reasons: list[str],
    verification_notes: str,
) -> dict[str, Any]:
    preconditions = ["env_fingerprint must match", "selector must match", "apply requires --plan-in, --apply, and --yes"]
    if requires_ack:
        preconditions.append("apply also requires --ack-irreversible")
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "risk_level": "high" if requires_ack else "medium",
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {
            "before_state_available": False,
            "notes": "Form Schemas plans in this slice do not capture full form schema before-state.",
        },
        "proposed_changes": [{"operation": method_name, "selector": selector}],
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {
            "supported": False,
            "notes": "No automatic rollback. Use form-schemas get, get-deleted, query, or list-deleted to inspect provider state.",
        },
    }


def _load_plan(*, plan_in: str | None, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan.get("method") or "") != expected_method:
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    return plan


def _run_write(
    *,
    method_name: str,
    http_method: str,
    path: str,
    ctx: dict[str, Any],
    selector: dict[str, Any],
    body: dict[str, Any] | None,
    requires_ack: bool = False,
    risk_reasons: list[str] | None = None,
    verification_notes: str = "Inspect the Wix response and reread the form schema when applicable.",
) -> int:
    auth = _resolve_auth(ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    plan = _build_plan(
        method_name=method_name,
        request=request,
        selector=selector,
        ctx=ctx,
        requires_ack=requires_ack,
        risk_reasons=risk_reasons or ["wix-form-schema-write"],
        verification_notes=verification_notes,
    )
    apply_allowed = reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=method_name)
    if not apply_allowed:
        out = {"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth["mode"], "plan": plan}
        if not ctx.get("apply") and ctx.get("plan_out"):
            out["plan_out"] = write_json_file(ctx["plan_out"], plan)
        ctx["audit"].write(f"{method_name}.plan", out)
        ctx["out"].emit(out)
        return 0

    _load_plan(plan_in=ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], params=None, json_body=body, ctx=ctx)
    receipt = {
        "ok": True,
        "dry_run": False,
        "method": method_name,
        "auth_mode": auth["mode"],
        "request": request,
        "response": response,
        "verified": {"type": "provider-response", "notes": verification_notes},
    }
    if ctx.get("receipt_out"):
        receipt["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
    ctx["audit"].write(f"{method_name}.apply", receipt)
    ctx["out"].emit(receipt)
    return 0


def _params_from_args(args: Any) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for name in ("namespace", "limit", "offset"):
        value = getattr(args, name, None)
        if value is not None:
            key = "paging.limit" if name == "limit" else "paging.offset" if name == "offset" else name
            params[key] = value
    return params


def cmd_form_schemas_list(args, ctx) -> int:
    method = "form-schemas.list"
    try:
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/forms", ctx=ctx, params=_params_from_args(args))
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_form_schemas_get(args, ctx) -> int:
    method = "form-schemas.get"
    try:
        form_id = _coerce_text(args.form_id, field="form-id")
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/forms/{form_id}", ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_form_schemas_get_deleted(args, ctx) -> int:
    method = "form-schemas.get-deleted"
    try:
        form_id = _coerce_text(args.form_id, field="form-id")
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/forms/trash-bin/{form_id}", ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_form_schemas_list_deleted(args, ctx) -> int:
    method = "form-schemas.list-deleted"
    try:
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/forms/trash-bin", ctx=ctx, params=_params_from_args(args))
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_form_schemas_list_providers_configs(args, ctx) -> int:
    method = "form-schemas.list-providers-configs"
    try:
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/forms/providers-config", ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_form_schemas_get_summary(args, ctx) -> int:
    method = "form-schemas.get-summary"
    try:
        form_id = _coerce_text(args.form_id, field="form-id")
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/forms/{form_id}/summary", ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def _query_body(args: Any, *, field: str = "query-json") -> dict[str, Any]:
    body = _read_object(getattr(args, "query_json"), field=field, allow_empty=True)
    if "query" in body:
        return body
    return {"query": body}


def cmd_form_schemas_query(args, ctx) -> int:
    method = "form-schemas.query"
    try:
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/forms/query", ctx=ctx, body=_query_body(args))
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_form_schemas_count(args, ctx) -> int:
    method = "form-schemas.count"
    try:
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/forms/count-by-filter", ctx=ctx, body=_read_object(args.filter_json, field="filter-json", allow_empty=True))
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_form_schemas_query_deleted(args, ctx) -> int:
    method = "form-schemas.query-deleted"
    try:
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/forms/trash-bin/query", ctx=ctx, body=_query_body(args))
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_form_schemas_count_deleted(args, ctx) -> int:
    method = "form-schemas.count-deleted"
    try:
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/deleted-forms/count", ctx=ctx, body=_read_object(args.filter_json, field="filter-json", allow_empty=True))
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_form_schemas_create(args, ctx) -> int:
    method = "form-schemas.create"
    try:
        body = _read_object(args.form_json, field="form-json")
        return _run_write(method_name=method, http_method="POST", path=f"{BASE_PATH}/forms", ctx=ctx, selector={"operation": "create"}, body=body)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_form_schemas_bulk_create(args, ctx) -> int:
    method = "form-schemas.bulk-create"
    try:
        body = _read_object(args.bulk_json, field="bulk-json")
        return _run_write(method_name=method, http_method="POST", path=f"{BASE_PATH}/bulk/forms/create", ctx=ctx, selector={"operation": "bulk-create"}, body=body, risk_reasons=["wix-form-schema-bulk-write"])
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_form_schemas_update(args, ctx) -> int:
    method = "form-schemas.update"
    try:
        body = _read_object(args.form_json, field="form-json")
        form = body.get("form")
        form_id = form.get("id") if isinstance(form, dict) else None
        if not isinstance(form_id, str) or not form_id.strip():
            raise ValidationError("--form-json must include form.id for update")
        return _run_write(method_name=method, http_method="PATCH", path=f"{BASE_PATH}/forms/{form_id.strip()}", ctx=ctx, selector={"formId": form_id.strip()}, body=body)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_form_schemas_clone(args, ctx) -> int:
    method = "form-schemas.clone"
    try:
        form_id = _coerce_text(args.form_id, field="form-id")
        body = _read_object(args.clone_json, field="clone-json", allow_empty=True)
        return _run_write(method_name=method, http_method="POST", path=f"{BASE_PATH}/forms/{form_id}/clone", ctx=ctx, selector={"formId": form_id}, body=body)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_form_schemas_bulk_clone(args, ctx) -> int:
    method = "form-schemas.bulk-clone"
    try:
        body = _read_object(args.bulk_json, field="bulk-json")
        return _run_write(method_name=method, http_method="POST", path=f"{BASE_PATH}/bulk/forms/clone", ctx=ctx, selector={"operation": "bulk-clone"}, body=body, risk_reasons=["wix-form-schema-bulk-write"])
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_form_schemas_delete(args, ctx) -> int:
    method = "form-schemas.delete"
    try:
        form_id = _coerce_text(args.form_id, field="form-id")
        return _run_write(method_name=method, http_method="DELETE", path=f"{BASE_PATH}/forms/{form_id}", ctx=ctx, selector={"formId": form_id}, body=None, requires_ack=True, risk_reasons=["wix-form-schema-delete", "trash-bin-retention"])
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_form_schemas_bulk_delete(args, ctx) -> int:
    method = "form-schemas.bulk-delete"
    try:
        body = _read_object(args.bulk_json, field="bulk-json")
        return _run_write(method_name=method, http_method="POST", path=f"{BASE_PATH}/bulk/forms/delete", ctx=ctx, selector={"operation": "bulk-delete"}, body=body, requires_ack=True, risk_reasons=["wix-form-schema-bulk-delete", "trash-bin-retention"])
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_form_schemas_restore(args, ctx) -> int:
    method = "form-schemas.restore"
    try:
        form_id = _coerce_text(args.form_id, field="form-id")
        return _run_write(method_name=method, http_method="POST", path=f"{BASE_PATH}/forms/trash-bin/{form_id}/restore", ctx=ctx, selector={"formId": form_id}, body=None)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_form_schemas_remove_from_trash(args, ctx) -> int:
    method = "form-schemas.remove-from-trash"
    try:
        form_id = _coerce_text(args.form_id, field="form-id")
        return _run_write(method_name=method, http_method="DELETE", path=f"{BASE_PATH}/forms/trash-bin/{form_id}", ctx=ctx, selector={"formId": form_id}, body=None, requires_ack=True, risk_reasons=["wix-form-schema-permanent-delete", "submissions-delete"])
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_form_schemas_bulk_remove_deleted_field(args, ctx) -> int:
    method = "form-schemas.bulk-remove-deleted-field"
    try:
        body = _read_object(args.bulk_json, field="bulk-json")
        return _run_write(method_name=method, http_method="POST", path=f"{BASE_PATH}/forms/fields/delete", ctx=ctx, selector={"operation": "bulk-remove-deleted-field"}, body=body, requires_ack=True, risk_reasons=["wix-form-schema-field-permanent-delete"])
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
