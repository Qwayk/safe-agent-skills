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


COMMAND_FAMILY = "bookings-resources-v2"


def _read_json_arg(raw: Any, *, field: str) -> Any:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a JSON string or @file path")
    text = raw.strip()
    if not text:
        raise ValidationError(f"--{field} cannot be empty")
    if text.startswith("@"):
        path = Path(text[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        text = path.read_text(encoding="utf-8").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc


def _coerce_non_empty_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_json_object(raw: Any, *, field: str, allow_empty: bool = False) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not allow_empty and not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _normalize_query_body(raw: Any, *, field: str, wrapper_key: str) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _coerce_json_object(raw, field=field, allow_empty=True)
    if wrapper_key in payload:
        nested = payload.get(wrapper_key)
        if not isinstance(nested, dict):
            raise ValidationError(f"--{field} {wrapper_key} must be a JSON object")
        return payload
    return {wrapper_key: payload}


def _normalize_count_body(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _coerce_json_object(raw, field="filter-json", allow_empty=True)
    if "filter" in payload or "search" in payload:
        return payload
    return {"filter": payload}


def _normalize_resource_body(raw: Any, *, resource_id: str | None = None) -> dict[str, Any]:
    payload = _coerce_json_object(raw, field="resource-json")
    body = dict(payload) if "resource" in payload else {"resource": payload}
    resource = body.get("resource")
    if not isinstance(resource, dict) or not resource:
        raise ValidationError("--resource-json must include a non-empty resource object")
    if resource_id is not None:
        payload_id = resource.get("id")
        if payload_id is not None and str(payload_id).strip() != resource_id:
            raise SafetyError("Refused: resource id in body does not match --resource-id")
        resource.setdefault("id", resource_id)
        if not str(resource.get("revision") or "").strip():
            raise ValidationError("--resource-json resource.revision is required for update")
    return body


def _normalize_resources_body(raw: Any, *, field: str) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if isinstance(payload, list):
        resources = payload
        body = {"resources": resources}
    elif isinstance(payload, dict):
        body = dict(payload)
        resources = body.get("resources")
    else:
        raise ValidationError(f"--{field} must be a JSON object or array")
    if not isinstance(resources, list) or not resources:
        raise ValidationError(f"--{field} must include a non-empty resources array")
    if len(resources) > 50:
        raise ValidationError(f"--{field} resources array cannot include more than 50 resources")
    return body


def _normalize_ids_body(raw: Any) -> dict[str, Any]:
    payload = _read_json_arg(raw, field="ids-json")
    if isinstance(payload, list):
        ids = payload
        body = {"ids": ids}
    elif isinstance(payload, dict):
        body = dict(payload)
        ids = body.get("ids")
    else:
        raise ValidationError("--ids-json must be a JSON object or array")
    if not isinstance(ids, list) or not ids:
        raise ValidationError("--ids-json must include a non-empty ids array")
    if len(ids) > 50:
        raise ValidationError("--ids-json ids array cannot include more than 50 ids")
    if any(not isinstance(item, str) or not item.strip() for item in ids):
        raise ValidationError("--ids-json ids array must contain non-empty strings")
    return body


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
    base_url: str,
    path: str,
    headers: dict[str, str],
    json_body: dict[str, Any] | None,
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
        request_headers["Content-Type"] = "application/json"
    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=None,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _emit_success(*, method: str, auth_mode: str, request: dict[str, Any], response: dict[str, Any], ctx: dict[str, Any]) -> None:
    out = {"ok": True, "method": method, "auth_mode": auth_mode, "request": request, "response": response}
    ctx["audit"].write(method, out)
    ctx["out"].emit(out)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    requires_ack: bool,
) -> dict[str, Any]:
    preconditions = [
        "env_fingerprint must match",
        "selector must match",
        "apply requires --plan-in, --apply, and --yes",
    ]
    if requires_ack:
        preconditions.append("apply also requires --ack-irreversible")
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": ["wix-bookings-resource-write"],
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {
            "before_state_available": False,
            "notes": "No useful before-state snapshot is captured for this Resources V2 provider-response write.",
        },
        "proposed_changes": proposed_changes,
        "verification_plan": {
            "type": "provider-response",
            "notes": "Provider-response-only in this boundary. Run follow-up resource reads, queries, or searches for live verification.",
        },
        "rollback": {"supported": False, "notes": "No automatic rollback. Recovery is manual and may require new reviewed resource plans."},
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


def _plan_out_if_needed(ctx: dict[str, Any], *, plan: dict[str, Any]) -> str | None:
    plan_out = ctx.get("plan_out")
    if plan_out and not bool(ctx.get("apply")):
        return write_json_file(plan_out, plan)
    return None


def _receipt_out_if_needed(ctx: dict[str, Any], *, receipt: dict[str, Any]) -> str | None:
    receipt_out = ctx.get("receipt_out")
    if receipt_out:
        return write_json_file(receipt_out, receipt)
    return None


def _should_apply(ctx: dict[str, Any], *, requires_ack: bool) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=COMMAND_FAMILY)


def _build_receipt(
    *,
    method: str,
    selector: dict[str, Any],
    request: dict[str, Any],
    response: dict[str, Any],
    plan: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "selector": selector,
        "request": request,
        "response": response,
        "changed": True,
        "verification": {"ok": True, "type": "provider-response"},
        "state_capture": {
            "before_state_available": False,
            "notes": "No useful before-state snapshot was available for this Resources V2 write.",
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {"automatic": False, "notes": "Recovery is manual only."},
    }


def _write_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
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


def _run_read(*, method_name: str, http_method: str, path: str, body: dict[str, Any] | None, ctx: dict[str, Any]) -> int:
    auth = _resolve_auth(ctx)
    payload = _request_json(
        method=http_method,
        base_url=ctx["cfg"].base_url,
        path=path,
        headers=auth["headers"],
        json_body=body,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    request = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    _emit_success(method=method_name, auth_mode=auth["mode"], request=request, response=payload, ctx=ctx)
    return 0


def _run_write(
    *,
    method_name: str,
    http_method: str,
    path: str,
    body: dict[str, Any] | None,
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    ctx: dict[str, Any],
    requires_ack: bool = False,
) -> int:
    auth = _resolve_auth(ctx)
    request = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    plan_in = ctx.get("plan_in")
    apply_allowed = bool(ctx.get("apply")) and bool(ctx.get("yes")) and _should_apply(ctx, requires_ack=requires_ack)
    if plan_in:
        plan = _load_plan(plan_in=str(plan_in), expected_method=method_name, expected_selector=selector, ctx=ctx)
    else:
        plan = _build_plan(
            method=method_name,
            request=request,
            selector=selector,
            ctx=ctx,
            proposed_changes=proposed_changes,
            requires_ack=requires_ack,
        )
    if not apply_allowed:
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "method": method_name,
                "auth_mode": auth["mode"],
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
        )
        return 0
    loaded_plan = _load_plan(plan_in=str(plan_in), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(
        method=http_method,
        base_url=ctx["cfg"].base_url,
        path=path,
        headers=auth["headers"],
        json_body=body,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    receipt = _build_receipt(
        method=method_name,
        selector=selector,
        request=request,
        response=response,
        plan=loaded_plan,
        ctx=ctx,
    )
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": False,
            "method": method_name,
            "auth_mode": auth["mode"],
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
    )
    return 0


def cmd_bookings_resources_v2_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        resource_id = _coerce_non_empty_text(getattr(args, "resource_id", None), field="resource-id")
        return _run_read(method_name=method, http_method="GET", path=f"/bookings/v2/resources/{resource_id}", body=None, ctx=ctx)
    except (ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_resources_v2_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        body = _normalize_query_body(getattr(args, "query_json", None), field="query-json", wrapper_key="query")
        return _run_read(method_name=method, http_method="POST", path="/bookings/v2/resources/query", body=body, ctx=ctx)
    except (ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_resources_v2_search(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.search"
    try:
        body = _normalize_query_body(getattr(args, "search_json", None), field="search-json", wrapper_key="search")
        return _run_read(method_name=method, http_method="POST", path="/bookings/v2/resources/search", body=body, ctx=ctx)
    except (ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_resources_v2_count(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.count"
    try:
        body = _normalize_count_body(getattr(args, "filter_json", None))
        return _run_read(method_name=method, http_method="POST", path="/bookings/v2/resources/count", body=body, ctx=ctx)
    except (ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_resources_v2_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _normalize_resource_body(getattr(args, "resource_json", None))
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/bookings/v2/resources",
            body=body,
            selector={"kind": "bookings-resource-v2", "operation": "create"},
            proposed_changes=[{"operation": "create", "body": body}],
            ctx=ctx,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_resources_v2_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        resource_id = _coerce_non_empty_text(getattr(args, "resource_id", None), field="resource-id")
        body = _normalize_resource_body(getattr(args, "resource_json", None), resource_id=resource_id)
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=f"/bookings/v2/resources/{resource_id}",
            body=body,
            selector={"kind": "bookings-resource-v2", "operation": "update", "resource_id": resource_id},
            proposed_changes=[{"operation": "update", "resource_id": resource_id, "body": body}],
            ctx=ctx,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_resources_v2_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        resource_id = _coerce_non_empty_text(getattr(args, "resource_id", None), field="resource-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=f"/bookings/v2/resources/{resource_id}",
            body=None,
            selector={"kind": "bookings-resource-v2", "operation": "delete", "resource_id": resource_id},
            proposed_changes=[{"operation": "delete", "resource_id": resource_id}],
            ctx=ctx,
            requires_ack=True,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_resources_v2_bulk_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-create"
    try:
        body = _normalize_resources_body(getattr(args, "resources_json", None), field="resources-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/bookings/v2/bulk/resources/create",
            body=body,
            selector={"kind": "bookings-resource-v2", "operation": "bulk-create"},
            proposed_changes=[{"operation": "bulk-create", "body": body}],
            ctx=ctx,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_resources_v2_bulk_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update"
    try:
        body = _normalize_resources_body(getattr(args, "resources_json", None), field="resources-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/bookings/v2/bulk/resources/update",
            body=body,
            selector={"kind": "bookings-resource-v2", "operation": "bulk-update"},
            proposed_changes=[{"operation": "bulk-update", "body": body}],
            ctx=ctx,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_resources_v2_bulk_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-delete"
    try:
        body = _normalize_ids_body(getattr(args, "ids_json", None))
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/bookings/v2/bulk/resources/delete",
            body=body,
            selector={"kind": "bookings-resource-v2", "operation": "bulk-delete"},
            proposed_changes=[{"operation": "bulk-delete", "body": body}],
            ctx=ctx,
            requires_ack=True,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)
