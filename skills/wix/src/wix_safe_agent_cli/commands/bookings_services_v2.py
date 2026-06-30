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


def _optional_json_object(raw: Any, *, field: str) -> dict[str, Any]:
    if raw is None:
        return {}
    return _coerce_json_object(raw, field=field, allow_empty=True)


def _request_body(raw: Any) -> dict[str, Any]:
    return _coerce_json_object(raw, field="request-json")


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
    if "filter" in payload:
        return payload
    return {"filter": payload}


def _normalize_service_body(raw: Any, *, service_id: str | None = None) -> dict[str, Any]:
    payload = _coerce_json_object(raw, field="service-json")
    body = dict(payload) if "service" in payload else {"service": payload}
    service = body.get("service")
    if not isinstance(service, dict) or not service:
        raise ValidationError("--service-json must include a non-empty service object")
    if service_id is not None:
        payload_id = service.get("id")
        if payload_id is not None and str(payload_id).strip() != service_id:
            raise SafetyError("Refused: service id in body does not match --service-id")
        service.setdefault("id", service_id)
    return body


def _normalize_services_body(raw: Any) -> dict[str, Any]:
    payload = _read_json_arg(raw, field="services-json")
    if isinstance(payload, list):
        services = payload
        body = {"services": services}
    elif isinstance(payload, dict):
        body = dict(payload)
        services = body.get("services")
    else:
        raise ValidationError("--services-json must be a JSON object or array")
    if not isinstance(services, list) or not services:
        raise ValidationError("--services-json must include a non-empty services array")
    if len(services) > 100:
        raise ValidationError("--services-json services array cannot include more than 100 services")
    return body


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="bookings-services-v2",
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
        "risk_reasons": ["wix-bookings-service-write"],
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {
            "before_state_available": False,
            "notes": "No useful before-state snapshot is captured for this Services V2 provider-response write.",
        },
        "proposed_changes": proposed_changes,
        "verification_plan": {
            "type": "provider-response",
            "notes": "Provider-response-only in this boundary. Run follow-up service reads, queries, or searches for live verification.",
        },
        "rollback": {"supported": False, "notes": "No automatic rollback. Recovery is manual and may require new reviewed service plans."},
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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="bookings-services-v2")


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
            "notes": "No useful before-state snapshot was available for this Services V2 write.",
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


def cmd_bookings_services_v2_get(args, ctx) -> int:
    method = "bookings-services-v2.get"
    try:
        service_id = _coerce_non_empty_text(getattr(args, "service_id", None), field="service-id")
        return _run_read(method_name=method, http_method="GET", path=f"/_api/bookings/v2/services/{service_id}", body=None, ctx=ctx)
    except (ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_services_v2_query(args, ctx) -> int:
    method = "bookings-services-v2.query"
    try:
        body = _normalize_query_body(getattr(args, "query_json", None), field="query-json", wrapper_key="query")
        return _run_read(method_name=method, http_method="POST", path="/_api/bookings/v2/services/query", body=body, ctx=ctx)
    except (ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_services_v2_search(args, ctx) -> int:
    method = "bookings-services-v2.search"
    try:
        body = _normalize_query_body(getattr(args, "search_json", None), field="search-json", wrapper_key="search")
        return _run_read(method_name=method, http_method="POST", path="/_api/bookings/v2/services/search", body=body, ctx=ctx)
    except (ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_services_v2_count(args, ctx) -> int:
    method = "bookings-services-v2.count"
    try:
        body = _normalize_count_body(getattr(args, "filter_json", None))
        return _run_read(method_name=method, http_method="POST", path="/_api/bookings/v2/services/count", body=body, ctx=ctx)
    except (ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def _cmd_request_read(args, ctx, *, command: str, path: str, field: str = "request_json") -> int:
    method = f"bookings-services-v2.{command}"
    try:
        body = _optional_json_object(getattr(args, field, None), field="request-json")
        return _run_read(method_name=method, http_method="POST", path=path, body=body, ctx=ctx)
    except (ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def _cmd_request_write(
    args,
    ctx,
    *,
    command: str,
    http_method: str,
    path: str,
    selector: dict[str, Any],
    requires_ack: bool = False,
    body: dict[str, Any] | None = None,
) -> int:
    method = f"bookings-services-v2.{command}"
    try:
        request_body = _request_body(getattr(args, "request_json", None)) if body is None and http_method != "DELETE" else body
        return _run_write(
            method_name=method,
            http_method=http_method,
            path=path,
            body=request_body,
            selector=selector,
            proposed_changes=[{"operation": command, "body": request_body}],
            ctx=ctx,
            requires_ack=requires_ack,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_services_v2_create(args, ctx) -> int:
    method = "bookings-services-v2.create"
    try:
        body = _normalize_service_body(getattr(args, "service_json", None))
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/_api/bookings/v2/services",
            body=body,
            selector={"kind": "bookings-service-v2", "operation": "create"},
            proposed_changes=[{"operation": "create", "body": body}],
            ctx=ctx,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_services_v2_update(args, ctx) -> int:
    method = "bookings-services-v2.update"
    try:
        service_id = _coerce_non_empty_text(getattr(args, "service_id", None), field="service-id")
        body = _normalize_service_body(getattr(args, "service_json", None), service_id=service_id)
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=f"/_api/bookings/v2/services/{service_id}",
            body=body,
            selector={"kind": "bookings-service-v2", "operation": "update", "service_id": service_id},
            proposed_changes=[{"operation": "update", "service_id": service_id, "body": body}],
            ctx=ctx,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_services_v2_delete(args, ctx) -> int:
    method = "bookings-services-v2.delete"
    try:
        service_id = _coerce_non_empty_text(getattr(args, "service_id", None), field="service-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=f"/_api/bookings/v2/services/{service_id}",
            body=None,
            selector={"kind": "bookings-service-v2", "operation": "delete", "service_id": service_id},
            proposed_changes=[{"operation": "delete", "service_id": service_id}],
            ctx=ctx,
            requires_ack=True,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_services_v2_bulk_create(args, ctx) -> int:
    method = "bookings-services-v2.bulk-create"
    try:
        body = _normalize_services_body(getattr(args, "services_json", None))
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/bookings/v2/bulk/services/create",
            body=body,
            selector={"kind": "bookings-service-v2", "operation": "bulk-create"},
            proposed_changes=[{"operation": "bulk-create", "body": body}],
            ctx=ctx,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_services_v2_bulk_update(args, ctx) -> int:
    method = "bookings-services-v2.bulk-update"
    try:
        body = _normalize_services_body(getattr(args, "services_json", None))
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/bookings/v2/bulk/services/update",
            body=body,
            selector={"kind": "bookings-service-v2", "operation": "bulk-update"},
            proposed_changes=[{"operation": "bulk-update", "body": body}],
            ctx=ctx,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


_REQUEST_OPERATIONS: dict[str, tuple[str, str, bool]] = {
    "bulk-update-by-filter": ("POST", "/bookings/v2/bulk/services/update-by-filter", False),
    "bulk-delete": ("POST", "/bookings/v2/bulk/services/delete", True),
    "bulk-delete-by-filter": ("POST", "/bookings/v2/bulk/services/delete-by-filter", True),
    "set-service-locations": ("POST", "/_api/bookings/v2/services/{service_id}/locations", True),
    "enable-pricing-plans": ("POST", "/_api/bookings/v2/services/{service_id}/pricing-plans/add", False),
    "disable-pricing-plans": ("POST", "/_api/bookings/v2/services/{service_id}/pricing-plans/remove", True),
    "set-custom-slug": ("POST", "/_api/bookings/v2/services/{service_id}/slugs/custom", False),
    "clone": ("POST", "/_api/bookings/v2/services/clone", False),
    "create-add-on-group": ("POST", "/_api/bookings/v2/services/add-on-groups/create", False),
    "delete-add-on-group": ("POST", "/_api/bookings/v2/services/add-on-groups/delete", True),
    "set-add-ons-for-group": ("POST", "/_api/bookings/v2/services/add-on-groups/set-add-ons-for-group", True),
    "update-add-on-group": ("POST", "/_api/bookings/v2/services/add-on-groups/update", False),
}


def _run_named_request_operation(args, ctx, *, command: str) -> int:
    method = f"bookings-services-v2.{command}"
    try:
        http_method, path_template, requires_ack = _REQUEST_OPERATIONS[command]
        service_id = getattr(args, "service_id", None)
        selector: dict[str, Any] = {"kind": "bookings-service-v2", "operation": command}
        if "{service_id}" in path_template:
            service_id_value = _coerce_non_empty_text(service_id, field="service-id")
            path = path_template.format(service_id=service_id_value)
            selector["service_id"] = service_id_value
        else:
            path = path_template
        return _cmd_request_write(
            args,
            ctx,
            command=command,
            http_method=http_method,
            path=path,
            selector=selector,
            requires_ack=requires_ack,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_services_v2_bulk_update_by_filter(args, ctx) -> int:
    return _run_named_request_operation(args, ctx, command="bulk-update-by-filter")


def cmd_bookings_services_v2_bulk_delete(args, ctx) -> int:
    return _run_named_request_operation(args, ctx, command="bulk-delete")


def cmd_bookings_services_v2_bulk_delete_by_filter(args, ctx) -> int:
    return _run_named_request_operation(args, ctx, command="bulk-delete-by-filter")


def cmd_bookings_services_v2_query_policies(args, ctx) -> int:
    return _cmd_request_read(args, ctx, command="query-policies", path="/_api/bookings/v2/services/policies/query")


def cmd_bookings_services_v2_query_locations(args, ctx) -> int:
    return _cmd_request_read(args, ctx, command="query-locations", path="/_api/bookings/v2/services/locations/query")


def cmd_bookings_services_v2_query_categories(args, ctx) -> int:
    return _cmd_request_read(args, ctx, command="query-categories", path="/_api/bookings/v2/services/categories/query")


def cmd_bookings_services_v2_set_service_locations(args, ctx) -> int:
    return _run_named_request_operation(args, ctx, command="set-service-locations")


def cmd_bookings_services_v2_enable_pricing_plans(args, ctx) -> int:
    return _run_named_request_operation(args, ctx, command="enable-pricing-plans")


def cmd_bookings_services_v2_disable_pricing_plans(args, ctx) -> int:
    return _run_named_request_operation(args, ctx, command="disable-pricing-plans")


def cmd_bookings_services_v2_set_custom_slug(args, ctx) -> int:
    return _run_named_request_operation(args, ctx, command="set-custom-slug")


def cmd_bookings_services_v2_validate_slug(args, ctx) -> int:
    return _cmd_request_read(args, ctx, command="validate-slug", path="/_api/bookings/v2/services/slugs/validate")


def cmd_bookings_services_v2_clone(args, ctx) -> int:
    return _run_named_request_operation(args, ctx, command="clone")


def cmd_bookings_services_v2_create_add_on_group(args, ctx) -> int:
    return _run_named_request_operation(args, ctx, command="create-add-on-group")


def cmd_bookings_services_v2_delete_add_on_group(args, ctx) -> int:
    return _run_named_request_operation(args, ctx, command="delete-add-on-group")


def cmd_bookings_services_v2_list_add_on_groups_by_service_id(args, ctx) -> int:
    return _cmd_request_read(
        args,
        ctx,
        command="list-add-on-groups-by-service-id",
        path="/_api/bookings/v2/services/add-on-groups/list-add-on-groups-by-service-id",
    )


def cmd_bookings_services_v2_set_add_ons_for_group(args, ctx) -> int:
    return _run_named_request_operation(args, ctx, command="set-add-ons-for-group")


def cmd_bookings_services_v2_update_add_on_group(args, ctx) -> int:
    return _run_named_request_operation(args, ctx, command="update-add-on-group")
