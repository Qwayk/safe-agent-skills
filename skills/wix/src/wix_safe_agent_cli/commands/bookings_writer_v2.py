from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested


COMMAND_FAMILY = "bookings-writer-v2"


@dataclass(frozen=True)
class Operation:
    command: str
    http_method: str
    path_template: str
    write: bool
    body_field: str | None = "request-json"
    id_arg: str | None = None
    id_placeholder: str | None = None
    requires_ack: bool = False
    anonymous: bool = False
    bulk_create: bool = False

    @property
    def method_name(self) -> str:
        return f"{COMMAND_FAMILY}.{self.command}"


OPERATIONS: dict[str, Operation] = {
    "create": Operation("create", "POST", "/_api/bookings-service/v2/bookings", True, "booking-json"),
    "bulk-create": Operation("bulk-create", "POST", "/bookings/v2/bulk/bookings/create", True, "bookings-json", bulk_create=True),
    "bulk-calculate-allowed-actions": Operation("bulk-calculate-allowed-actions", "POST", "/bookings/v2/bulk/bookings/calculate_allowed_actions", False),
    "bulk-confirm-or-decline": Operation("bulk-confirm-or-decline", "POST", "/bookings/v2/bulk/bookings/confirmOrDecline", True, requires_ack=True),
    "confirm-or-decline": Operation("confirm-or-decline", "POST", "/bookings/v2/confirmation/{bookingId}:confirmOrDecline", True, id_arg="booking_id", id_placeholder="bookingId", requires_ack=True),
    "confirm": Operation("confirm", "POST", "/_api/bookings-service/v2/bookings/{bookingId}/confirm", True, id_arg="booking_id", id_placeholder="bookingId"),
    "decline": Operation("decline", "POST", "/_api/bookings-service/v2/bookings/{bookingId}/decline", True, id_arg="booking_id", id_placeholder="bookingId", requires_ack=True),
    "cancel": Operation("cancel", "POST", "/_api/bookings-service/v2/bookings/{bookingId}/cancel", True, id_arg="booking_id", id_placeholder="bookingId", requires_ack=True),
    "reschedule": Operation("reschedule", "POST", "/_api/bookings-service/v2/bookings/{bookingId}/reschedule", True, id_arg="booking_id", id_placeholder="bookingId", requires_ack=True),
    "mark-pending": Operation("mark-pending", "POST", "/_api/bookings-service/v2/bookings/{bookingId}/mark_booking_as_pending", True, id_arg="booking_id", id_placeholder="bookingId"),
    "set-submission-id": Operation("set-submission-id", "POST", "/_api/bookings-service/v2/bookings/{bookingId}/set-booking-submission-id", True, id_arg="booking_id", id_placeholder="bookingId"),
    "update-extended-fields": Operation("update-extended-fields", "POST", "/_api/bookings-service/v2/bookings/{id}/update_extended_fields", True, id_arg="booking_id", id_placeholder="id"),
    "update-participants": Operation("update-participants", "POST", "/_api/bookings-service/v2/bookings/{bookingId}/update_number_of_participants", True, id_arg="booking_id", id_placeholder="bookingId", requires_ack=True),
    "create-multi-service": Operation("create-multi-service", "POST", "/_api/bookings-service/v2/multi_service_bookings", True, "multi-service-booking-json"),
    "get-multi-service": Operation("get-multi-service", "GET", "/_api/bookings-service/v2/multi_service_bookings/{multiServiceBookingId}", False, None, "multi_service_booking_id", "multiServiceBookingId"),
    "get-multi-service-availability": Operation("get-multi-service-availability", "POST", "/_api/bookings-service/v2/multi_service_bookings/{multiServiceBookingId}/get_availability", False, id_arg="multi_service_booking_id", id_placeholder="multiServiceBookingId"),
    "add-to-multi-service": Operation("add-to-multi-service", "POST", "/_api/bookings-service/v2/multi_service_bookings/add_bookings_to_multi_service_booking", True),
    "remove-from-multi-service": Operation("remove-from-multi-service", "POST", "/_api/bookings-service/v2/multi_service_bookings/remove_bookings_from_multi_service_booking", True, requires_ack=True),
    "cancel-multi-service": Operation("cancel-multi-service", "POST", "/_api/bookings-service/v2/multi_service_bookings/{multiServiceBookingId}/cancel", True, id_arg="multi_service_booking_id", id_placeholder="multiServiceBookingId", requires_ack=True),
    "confirm-multi-service": Operation("confirm-multi-service", "POST", "/_api/bookings-service/v2/multi_service_bookings/{multiServiceBookingId}/confirm", True, id_arg="multi_service_booking_id", id_placeholder="multiServiceBookingId"),
    "decline-multi-service": Operation("decline-multi-service", "POST", "/_api/bookings-service/v2/multi_service_bookings/{multiServiceBookingId}/decline", True, id_arg="multi_service_booking_id", id_placeholder="multiServiceBookingId", requires_ack=True),
    "reschedule-multi-service": Operation("reschedule-multi-service", "POST", "/_api/bookings-service/v2/multi_service_bookings/{multiServiceBookingId}/reschedule", True, id_arg="multi_service_booking_id", id_placeholder="multiServiceBookingId", requires_ack=True),
    "mark-multi-service-pending": Operation("mark-multi-service-pending", "POST", "/_api/bookings-service/v2/multi_service_bookings/{multiServiceBookingId}/mark_as_pending", True, id_arg="multi_service_booking_id", id_placeholder="multiServiceBookingId"),
    "bulk-get-multi-service-allowed-actions": Operation("bulk-get-multi-service-allowed-actions", "POST", "/bookings/multiServiceBookings/v2/bulk/multi_service_bookings/get_allowed_actions", False),
    "get-anonymous-action-token": Operation("get-anonymous-action-token", "GET", "/v1/anonymous-bookings/{bookingId}/token", False, None, "booking_id", "bookingId"),
    "get-anonymous": Operation("get-anonymous", "GET", "/v1/anonymous-bookings/{token}", False, None, "token", "token", anonymous=True),
    "get-service-anonymous": Operation("get-service-anonymous", "GET", "/v1/anonymous-bookings/{token}/service", False, None, "token", "token", anonymous=True),
    "cancel-anonymous": Operation("cancel-anonymous", "POST", "/v1/anonymous-bookings/{token}/cancel", True, id_arg="token", id_placeholder="token", requires_ack=True, anonymous=True),
    "reschedule-anonymous": Operation("reschedule-anonymous", "POST", "/v1/anonymous-bookings/{token}/reschedule", True, id_arg="token", id_placeholder="token", requires_ack=True, anonymous=True),
}


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


def _normalize_body(args: Any, operation: Operation) -> dict[str, Any] | None:
    if operation.body_field is None:
        return None
    raw = getattr(args, operation.body_field.replace("-", "_"), None)
    body = _coerce_json_object(raw, field=operation.body_field, allow_empty=True)
    if operation.command == "create" and "booking" not in body:
        body = {"booking": body}
    if operation.command == "create-multi-service" and "multiServiceBooking" not in body:
        body = {"multiServiceBooking": body}
    if operation.bulk_create:
        items = body.get("createBookingsInfo")
        if not isinstance(items, list):
            raise ValidationError("--bookings-json must include createBookingsInfo array")
        if len(items) > 12:
            raise ValidationError("--bookings-json createBookingsInfo cannot include more than 12 bookings")
    return body


def _selector(args: Any, operation: Operation) -> dict[str, Any]:
    selector: dict[str, Any] = {"kind": "bookings-writer-v2", "operation": operation.command}
    if operation.id_arg:
        field_name = operation.id_arg.replace("_", "-")
        value = _coerce_non_empty_text(getattr(args, operation.id_arg, None), field=field_name)
        selector[operation.id_arg] = "<redacted-token>" if operation.anonymous and operation.id_arg == "token" else value
    return selector


def _path(args: Any, operation: Operation) -> str:
    path = operation.path_template
    if not operation.id_arg or not operation.id_placeholder:
        return path
    field_name = operation.id_arg.replace("_", "-")
    value = _coerce_non_empty_text(getattr(args, operation.id_arg, None), field=field_name)
    return path.replace("{" + operation.id_placeholder + "}", value)


def _display_path(args: Any, operation: Operation) -> str:
    if operation.anonymous and operation.id_placeholder == "token":
        return operation.path_template.replace("{token}", "<redacted-token>")
    return _path(args, operation)


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
    )


def _auth_for_operation(ctx: dict[str, Any], operation: Operation) -> dict[str, Any]:
    if operation.anonymous:
        return {"mode": "anonymous_token", "headers": {}}
    return _resolve_auth(ctx)


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


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _build_plan(
    *,
    operation: Operation,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    preconditions = [
        "env_fingerprint must match",
        "selector must match",
        "apply requires --plan-in, --apply, and --yes",
        "check Time Slots V2 before create or reschedule requests when availability matters",
    ]
    if operation.requires_ack:
        preconditions.append("apply also requires --ack-irreversible")
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": operation.method_name,
        "risk_level": "high",
        "risk_reasons": ["wix-bookings-writer-v2-lifecycle-write"],
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {
            "before_state_available": False,
            "notes": "Writer V2 writes are provider-response-only in this CLI. Use Reader V2, multi-service reads, or anonymous reads for follow-up proof where applicable.",
        },
        "proposed_changes": [{"operation": operation.command, "request": request}],
        "verification_plan": {
            "type": "provider-response",
            "notes": "Confirm provider success, then run a matching Bookings Reader V2 or Writer V2 read when the official surface supports it.",
        },
        "rollback": {
            "supported": False,
            "notes": "No automatic rollback. Canceled, declined, rescheduled, or participant-changing bookings may require manual recovery.",
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


def _write_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, SafetyError):
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": method})
        return 0
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _run_operation(args: Any, ctx: dict[str, Any], operation: Operation) -> int:
    method_name = operation.method_name
    try:
        path = _path(args, operation)
        display_path = _display_path(args, operation)
        body = _normalize_body(args, operation)
        selector = _selector(args, operation)
        request: dict[str, Any] = {"method": operation.http_method, "path": display_path}
        if body is not None:
            request["body"] = body
        auth = _auth_for_operation(ctx, operation)
        if not operation.write:
            response = _request_json(
                method=operation.http_method,
                base_url=ctx["cfg"].base_url,
                path=path,
                headers=auth["headers"],
                json_body=body,
                timeout_s=float(ctx["cfg"].timeout_s),
                verbose=bool(ctx.get("verbose")),
            )
            out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": request, "response": response}
            if operation.anonymous:
                out["secret_note"] = "The token in this request is a credential. Do not store or share it unless needed."
            ctx["audit"].write(method_name, out)
            ctx["out"].emit(out)
            return 0
        plan_in = ctx.get("plan_in")
        apply_allowed = bool(ctx.get("apply")) and bool(ctx.get("yes")) and _should_apply(ctx, requires_ack=operation.requires_ack)
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method=method_name, expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(operation=operation, request=request, selector=selector, ctx=ctx)
        if not apply_allowed:
            ctx["out"].emit({"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth["mode"], "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)})
            return 0
        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method=method_name, expected_selector=selector, ctx=ctx)
        response = _request_json(
            method=operation.http_method,
            base_url=ctx["cfg"].base_url,
            path=path,
            headers=auth["headers"],
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
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
            "verification": {"ok": True, "type": "provider-response"},
            "state_capture": loaded_plan.get("state_capture") or {},
            "diff_applied": loaded_plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
            "recovery": {"automatic": False, "notes": "Recovery is manual only."},
        }
        ctx["out"].emit({"ok": True, "dry_run": False, "method": method_name, "auth_mode": auth["mode"], "receipt": receipt, "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt)})
        return 0
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method_name, exc=exc)


def _make_handler(command: str):
    def handler(args, ctx) -> int:
        return _run_operation(args, ctx, OPERATIONS[command])

    handler.__name__ = f"cmd_bookings_writer_v2_{command.replace('-', '_')}"
    return handler


for _command in OPERATIONS:
    globals()[f"cmd_bookings_writer_v2_{_command.replace('-', '_')}"] = _make_handler(_command)
