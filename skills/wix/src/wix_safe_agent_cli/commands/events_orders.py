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


COMMAND_FAMILY = "events-orders"
ORDERS_PATH = "/events/v1/orders"
CHECKOUT_PATH = "/events/v1/checkout"


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_json_arg(raw: Any, *, field: str, allow_empty: bool = False) -> dict[str, Any]:
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


def _normalize_query_body(raw: Any, *, field: str) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field, allow_empty=True)
    limit = payload.get("limit")
    if limit is not None:
        if not isinstance(limit, int):
            raise ValidationError(f"--{field} limit must be an integer")
        if limit > 1000:
            raise ValidationError(f"--{field} limit can be at most 1000")
    offset = payload.get("offset")
    if offset is not None:
        if not isinstance(offset, int):
            raise ValidationError(f"--{field} offset must be an integer")
        if offset < 0:
            raise ValidationError(f"--{field} offset must be 0 or greater")
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
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
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
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": method})
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
    params: dict[str, Any] | None,
    body: dict[str, Any] | None,
    ctx: dict[str, Any],
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
    proposed_changes: list[dict[str, Any]],
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
        "state_capture": {"before_state_available": False, "notes": "Events Orders plans do not capture a full before-state snapshot in this slice."},
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Verify with Events Orders reads and the Wix dashboard when needed."},
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
    body: dict[str, Any] | None,
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    ctx: dict[str, Any],
    requires_ack: bool = False,
    risk_reasons: list[str] | None = None,
    verification_notes: str = "Provider response confirms the Events Orders request was accepted.",
) -> int:
    auth = _resolve_auth(ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    plan = _build_plan(
        method_name=method_name,
        request=request,
        selector=selector,
        proposed_changes=proposed_changes,
        ctx=ctx,
        requires_ack=requires_ack,
        risk_reasons=risk_reasons or ["wix-events-orders-write"],
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
    loaded_plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], json_body=body, ctx=ctx)
    receipt = {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "selector": selector,
        "request": request,
        "response": response,
        "changed": True,
        "verification": {"ok": True, "type": "provider-response", "notes": verification_notes},
        "diff_applied": loaded_plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {"automatic": False, "notes": "Recovery is manual only."},
    }
    out = {"ok": True, "dry_run": False, "method": method_name, "auth_mode": auth["mode"], "receipt": receipt}
    if ctx.get("receipt_out"):
        out["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
    ctx["audit"].write(f"{method_name}.apply", out)
    ctx["out"].emit(out)
    return 0


def cmd_events_orders_list(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list"
    try:
        params = _read_json_arg(getattr(args, "params_json", "{}"), field="params-json", allow_empty=True)
        return _run_read(method_name=method, http_method="GET", path=ORDERS_PATH, params=params or None, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_orders_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        event_id = _coerce_text(getattr(args, "event_id", None), field="event-id")
        order_number = _coerce_text(getattr(args, "order_number", None), field="order-number")
        return _run_read(method_name=method, http_method="GET", path=f"/events/v1/events/{event_id}/orders/{order_number}", params=None, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_orders_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        event_id = _coerce_text(getattr(args, "event_id", None), field="event-id")
        order_number = _coerce_text(getattr(args, "order_number", None), field="order-number")
        body = _read_json_arg(getattr(args, "order_json", None), field="order-json")
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=f"/events/v1/events/{event_id}/orders/{order_number}",
            body=body,
            selector={"kind": COMMAND_FAMILY, "event_id": event_id, "order_number": order_number},
            proposed_changes=[{"operation": "update-order", "event_id": event_id, "order_number": order_number}],
            ctx=ctx,
            risk_reasons=["wix-events-order-update", "checkout-form-or-archived-state-change"],
            verification_notes="Provider response confirms the order update request was accepted; verify with events-orders get.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_orders_bulk_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update"
    try:
        event_id = _coerce_text(getattr(args, "event_id", None), field="event-id")
        body = _read_json_arg(getattr(args, "orders_json", None), field="orders-json")
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=f"/events/v1/events/{event_id}/orders",
            body=body,
            selector={"kind": COMMAND_FAMILY, "event_id": event_id, "operation": "bulk-update"},
            proposed_changes=[{"operation": "bulk-update-orders", "event_id": event_id}],
            ctx=ctx,
            risk_reasons=["wix-events-orders-bulk-update", "multi-order-archived-state-change"],
            verification_notes="Provider response confirms the bulk order update request was accepted; verify affected orders with events-orders get/list.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_orders_confirm(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.confirm"
    try:
        event_id = _coerce_text(getattr(args, "event_id", None), field="event-id")
        body = _read_json_arg(getattr(args, "request_json", None), field="request-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"/events/v1/events/{event_id}/orders/confirm",
            body=body,
            selector={"kind": COMMAND_FAMILY, "event_id": event_id, "operation": "confirm-order"},
            proposed_changes=[{"operation": "confirm-order", "event_id": event_id}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-events-order-confirm", "payment-status-change", "ticket-confirmation-email-may-send"],
            verification_notes="Provider response confirms the order confirmation request was accepted; verify order status and buyer email side effects.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_orders_get_summary(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-summary"
    try:
        params = _read_json_arg(getattr(args, "params_json", "{}"), field="params-json", allow_empty=True)
        return _run_read(method_name=method, http_method="GET", path=f"{ORDERS_PATH}/summary", params=params or None, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_orders_get_checkout_options(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-checkout-options"
    try:
        params = _read_json_arg(getattr(args, "params_json", "{}"), field="params-json", allow_empty=True)
        return _run_read(method_name=method, http_method="GET", path=f"{CHECKOUT_PATH}/options", params=params or None, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_orders_list_available_tickets(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list-available-tickets"
    try:
        params = _read_json_arg(getattr(args, "params_json", "{}"), field="params-json", allow_empty=True)
        return _run_read(method_name=method, http_method="GET", path=f"{CHECKOUT_PATH}/available-tickets", params=params or None, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_orders_query_available_tickets(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query-available-tickets"
    try:
        body = _normalize_query_body(getattr(args, "query_json", "{}"), field="query-json")
        return _run_read(method_name=method, http_method="POST", path=f"{CHECKOUT_PATH}/available-tickets/query", params=None, body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_orders_create_reservation(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create-reservation"
    try:
        body = _read_json_arg(getattr(args, "reservation_json", None), field="reservation-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{CHECKOUT_PATH}/reservations",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "create-reservation"},
            proposed_changes=[{"operation": "create-reservation", "hold_minutes": 20}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-events-create-reservation", "deprecated-endpoint", "temporary-ticket-inventory-hold"],
            verification_notes="Provider response confirms the reservation request was accepted; verify reservation status or use the newer ticket-reservations family when possible.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_orders_cancel_reservation(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.cancel-reservation"
    try:
        reservation_id = _coerce_text(getattr(args, "reservation_id", None), field="reservation-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{CHECKOUT_PATH}/reservations/{reservation_id}",
            body=None,
            selector={"kind": COMMAND_FAMILY, "reservation_id": reservation_id, "operation": "cancel-reservation"},
            proposed_changes=[{"operation": "cancel-reservation", "reservation_id": reservation_id}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-events-cancel-reservation", "deprecated-endpoint", "releases-ticket-inventory-hold"],
            verification_notes="Provider response confirms the reservation cancellation request was accepted; verify inventory availability.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_orders_checkout(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.checkout"
    try:
        body = _read_json_arg(getattr(args, "checkout_json", None), field="checkout-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=CHECKOUT_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "checkout"},
            proposed_changes=[{"operation": "checkout"}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-events-checkout", "payment-adjacent-order-creation", "ticket-inventory-change", "contact-may-be-created"],
            verification_notes="Provider response confirms the checkout request was accepted; verify order, contact, payment, and ticket inventory side effects.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_orders_update_checkout(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update-checkout"
    try:
        order_number = _coerce_text(getattr(args, "order_number", None), field="order-number")
        body = _read_json_arg(getattr(args, "checkout_json", None), field="checkout-json")
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{CHECKOUT_PATH}/{order_number}",
            body=body,
            selector={"kind": COMMAND_FAMILY, "order_number": order_number, "operation": "update-checkout"},
            proposed_changes=[{"operation": "update-checkout", "order_number": order_number}],
            ctx=ctx,
            risk_reasons=["wix-events-update-checkout", "payment-adjacent-order-change"],
            verification_notes="Provider response confirms the checkout update request was accepted; verify before confirming or completing payment.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_orders_get_invoice(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-invoice"
    try:
        reservation_id = _coerce_text(getattr(args, "reservation_id", None), field="reservation-id")
        body = _read_json_arg(getattr(args, "invoice_json", "{}"), field="invoice-json", allow_empty=True)
        return _run_read(method_name=method, http_method="POST", path=f"{CHECKOUT_PATH}/invoices/{reservation_id}", params=None, body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
