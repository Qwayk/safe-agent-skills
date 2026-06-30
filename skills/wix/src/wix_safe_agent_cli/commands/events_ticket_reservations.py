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


COMMAND_FAMILY = "events-ticket-reservations"
BASE_PATH = "/events/v1/ticket-reservations"


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_json_arg(raw: Any, *, field: str) -> dict[str, Any]:
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
    return payload


def _normalize_reservation_body(raw: Any, *, field: str) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    body = dict(payload) if "ticketReservation" in payload else {"ticketReservation": payload}
    reservation = body.get("ticketReservation")
    if not isinstance(reservation, dict) or not reservation:
        raise ValidationError(f"--{field} must include a non-empty ticketReservation object")
    tickets = reservation.get("tickets")
    if tickets is not None:
        if not isinstance(tickets, list):
            raise ValidationError(f"--{field} ticketReservation.tickets must be a JSON array")
        if not tickets:
            raise ValidationError(f"--{field} ticketReservation.tickets cannot be empty")
        if len(tickets) > 50:
            raise ValidationError(f"--{field} ticketReservation.tickets can include at most 50 line items")
    return body


def _validate_tag_request(payload: dict[str, Any], *, field: str, by_filter: bool) -> None:
    assign = payload.get("assign")
    unassign = payload.get("unassign")
    if assign is not None and not isinstance(assign, list):
        raise ValidationError(f"--{field} assign must be a JSON array when provided")
    if unassign is not None and not isinstance(unassign, list):
        raise ValidationError(f"--{field} unassign must be a JSON array when provided")
    if assign == [] and unassign == []:
        raise ValidationError(f"--{field} cannot have both assign and unassign empty")
    if not by_filter:
        ids = payload.get("ids")
        if not isinstance(ids, list) or not ids:
            raise ValidationError(f"--{field} must include a non-empty ids array")
        if len(ids) > 100:
            raise ValidationError(f"--{field} ids can include at most 100 ticket reservations")
    elif not payload:
        raise ValidationError(f"--{field} cannot be empty for bulk update tags by filter")


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
        params=None,
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


def _run_read(*, method_name: str, http_method: str, path: str, ctx: dict[str, Any]) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], json_body=None, ctx=ctx)
    out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": {"method": http_method, "path": path}, "response": response}
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
        "state_capture": {"before_state_available": False, "notes": "Events Ticket Reservations plans do not capture a full before-state snapshot in this slice."},
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Verify with Ticket Reservation reads and the Wix dashboard when needed."},
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
    verification_notes: str = "Provider response confirms the ticket reservation request was accepted.",
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
        risk_reasons=risk_reasons or ["wix-events-ticket-reservation-write"],
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


def cmd_events_ticket_reservations_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _normalize_reservation_body(getattr(args, "reservation_json", None), field="reservation-json")
        return _run_write(method_name=method, http_method="POST", path=BASE_PATH, body=body, selector={"kind": COMMAND_FAMILY, "operation": "create"}, proposed_changes=[{"operation": "create-ticket-reservation"}], ctx=ctx, risk_reasons=["wix-events-ticket-reservation-create", "temporary-ticket-hold"], verification_notes="Provider response confirms the ticket reservation create request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_ticket_reservations_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        reservation_id = _coerce_text(getattr(args, "ticket_reservation_id", None), field="ticket-reservation-id")
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/{reservation_id}", ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_ticket_reservations_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        reservation_id = _coerce_text(getattr(args, "ticket_reservation_id", None), field="ticket-reservation-id")
        return _run_write(method_name=method, http_method="DELETE", path=f"{BASE_PATH}/{reservation_id}", body=None, selector={"kind": COMMAND_FAMILY, "ticket_reservation_id": reservation_id}, proposed_changes=[{"operation": "delete-ticket-reservation", "ticket_reservation_id": reservation_id}], ctx=ctx, requires_ack=True, risk_reasons=["wix-events-ticket-reservation-delete", "cannot-be-undone", "releases-reserved-tickets"], verification_notes="Provider response confirms the ticket reservation delete request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_ticket_reservations_bulk_update_tags(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update-tags"
    try:
        body = _read_json_arg(getattr(args, "tags_json", None), field="tags-json")
        _validate_tag_request(body, field="tags-json", by_filter=False)
        return _run_write(method_name=method, http_method="POST", path="/events/v1/bulk/ticket-reservations/update-tags", body=body, selector={"kind": COMMAND_FAMILY, "operation": "bulk-update-tags"}, proposed_changes=[{"operation": "bulk-update-ticket-reservation-tags"}], ctx=ctx, risk_reasons=["wix-events-ticket-reservation-bulk-update-tags", "multi-reservation-tag-change"], verification_notes="Provider response confirms the bulk ticket reservation tag update request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_ticket_reservations_bulk_update_tags_by_filter(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update-tags-by-filter"
    try:
        body = _read_json_arg(getattr(args, "filter_json", None), field="filter-json")
        _validate_tag_request(body, field="filter-json", by_filter=True)
        return _run_write(method_name=method, http_method="POST", path="/events/v1/bulk/ticket-reservations/update-tags-by-filter", body=body, selector={"kind": COMMAND_FAMILY, "operation": "bulk-update-tags-by-filter"}, proposed_changes=[{"operation": "bulk-update-ticket-reservation-tags-by-filter"}], ctx=ctx, requires_ack=True, risk_reasons=["wix-events-ticket-reservation-bulk-update-tags-by-filter", "empty-filter-can-update-all-reservations", "async-large-scale-tag-change"], verification_notes="Provider response confirms the bulk ticket reservation tag update-by-filter request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_ticket_reservations_cancel(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.cancel"
    try:
        reservation_id = _coerce_text(getattr(args, "ticket_reservation_id", None), field="ticket-reservation-id")
        return _run_write(method_name=method, http_method="POST", path=f"{BASE_PATH}/{reservation_id}/cancel", body={}, selector={"kind": COMMAND_FAMILY, "ticket_reservation_id": reservation_id, "operation": "cancel"}, proposed_changes=[{"operation": "cancel-ticket-reservation", "ticket_reservation_id": reservation_id}], ctx=ctx, requires_ack=True, risk_reasons=["wix-events-ticket-reservation-cancel", "cannot-be-restored", "releases-reserved-tickets"], verification_notes="Provider response confirms the ticket reservation cancel request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
