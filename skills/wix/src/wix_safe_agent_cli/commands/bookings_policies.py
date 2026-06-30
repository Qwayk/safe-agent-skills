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


COMMAND_FAMILY = "bookings-policies"
BASE_PATH = "/bookings/v1/booking-policies"


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


def _normalize_query_body(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _coerce_json_object(raw, field="query-json", allow_empty=True)
    if "query" in payload:
        if not isinstance(payload.get("query"), dict):
            raise ValidationError("--query-json query must be a JSON object")
        return payload
    return {"query": payload}


def _normalize_count_body(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _coerce_json_object(raw, field="filter-json", allow_empty=True)
    if "filter" in payload:
        return payload
    return {"filter": payload}


def _normalize_request_body(raw: Any, *, field: str) -> dict[str, Any]:
    return _coerce_json_object(raw, field=field, allow_empty=True)


def _normalize_policy_body(raw: Any, *, booking_policy_id: str | None = None) -> dict[str, Any]:
    payload = _coerce_json_object(raw, field="policy-json")
    body = dict(payload) if "bookingPolicy" in payload else {"bookingPolicy": payload}
    policy = body.get("bookingPolicy")
    if not isinstance(policy, dict) or not policy:
        raise ValidationError("--policy-json must include a non-empty bookingPolicy object")
    if booking_policy_id is not None:
        payload_id = policy.get("id")
        if payload_id is not None and str(payload_id).strip() != booking_policy_id:
            raise SafetyError("Refused: booking policy id in body does not match --booking-policy-id")
        policy.setdefault("id", booking_policy_id)
        if not str(policy.get("revision") or "").strip():
            raise ValidationError("--policy-json bookingPolicy.revision is required for update")
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
        "risk_reasons": ["wix-bookings-policy-write"],
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {
            "before_state_available": False,
            "notes": "No useful before-state snapshot is captured for this Booking Policies provider-response write.",
        },
        "proposed_changes": proposed_changes,
        "verification_plan": {
            "type": "provider-response",
            "notes": "Provider-response-only in this boundary. Run get, query, count, or strictest-policy reads for live verification.",
        },
        "rollback": {"supported": False, "notes": "No automatic rollback. Recovery is manual and may require new reviewed policy plans."},
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
            "notes": "No useful before-state snapshot was available for this Booking Policies write.",
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {"automatic": False, "notes": "Recovery is manual only."},
    }


def _write_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, SafetyError):
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": method})
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
    receipt = _build_receipt(method=method_name, selector=selector, request=request, response=response, plan=loaded_plan, ctx=ctx)
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


def cmd_bookings_policies_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        booking_policy_id = _coerce_non_empty_text(getattr(args, "booking_policy_id", None), field="booking-policy-id")
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/{booking_policy_id}", body=None, ctx=ctx)
    except (ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_policies_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        body = _normalize_query_body(getattr(args, "query_json", None))
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/query", body=body, ctx=ctx)
    except (ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_policies_count(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.count"
    try:
        body = _normalize_count_body(getattr(args, "filter_json", None))
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/count", body=body, ctx=ctx)
    except (ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_policies_strictest(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.strictest"
    try:
        body = _normalize_request_body(getattr(args, "request_json", None), field="request-json")
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/strictest", body=body, ctx=ctx)
    except (ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_policies_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _normalize_policy_body(getattr(args, "policy_json", None))
        return _run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"kind": "bookings-policy", "operation": "create"},
            proposed_changes=[{"operation": "create", "body": body}],
            ctx=ctx,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_policies_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        booking_policy_id = _coerce_non_empty_text(getattr(args, "booking_policy_id", None), field="booking-policy-id")
        body = _normalize_policy_body(getattr(args, "policy_json", None), booking_policy_id=booking_policy_id)
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{booking_policy_id}",
            body=body,
            selector={"kind": "bookings-policy", "operation": "update", "booking_policy_id": booking_policy_id},
            proposed_changes=[{"operation": "update", "booking_policy_id": booking_policy_id, "body": body}],
            ctx=ctx,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_policies_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        booking_policy_id = _coerce_non_empty_text(getattr(args, "booking_policy_id", None), field="booking-policy-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{booking_policy_id}",
            body=None,
            selector={"kind": "bookings-policy", "operation": "delete", "booking_policy_id": booking_policy_id},
            proposed_changes=[{"operation": "delete", "booking_policy_id": booking_policy_id}],
            ctx=ctx,
            requires_ack=True,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_bookings_policies_set_default(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.set-default"
    try:
        booking_policy_id = _coerce_non_empty_text(getattr(args, "booking_policy_id", None), field="booking-policy-id")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{booking_policy_id}:setDefault",
            body=None,
            selector={"kind": "bookings-policy", "operation": "set-default", "booking_policy_id": booking_policy_id},
            proposed_changes=[{"operation": "set-default", "booking_policy_id": booking_policy_id}],
            ctx=ctx,
            requires_ack=True,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)
