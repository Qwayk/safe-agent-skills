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


COMMAND_FAMILY = "calendar-events-v3"
BASE_PATH = "/calendar/v3/events"
BULK_PATH = "/calendar/v3/bulk/events"


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _optional_text(raw: Any, *, field: str) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    return value or None


def _read_json_arg(raw: Any, *, field: str) -> Any:
    value = _coerce_text(raw, field=field)
    if value.startswith("@"):
        path = Path(value[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        value = path.read_text(encoding="utf-8").strip()
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc


def _read_json_object(raw: Any, *, field: str, allow_empty: bool = False) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not allow_empty and not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _read_json_list(raw: Any, *, field: str, min_items: int = 1, max_items: int | None = None) -> list[Any]:
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, list):
        raise ValidationError(f"--{field} must be a JSON array")
    if len(payload) < min_items:
        raise ValidationError(f"--{field} must contain at least {min_items} item(s)")
    if max_items is not None and len(payload) > max_items:
        raise ValidationError(f"--{field} cannot contain more than {max_items} item(s)")
    return payload


def _read_string_list(raw: Any, *, field: str, min_items: int = 1, max_items: int | None = None) -> list[str]:
    payload = _read_json_list(raw, field=field, min_items=min_items, max_items=max_items)
    values: list[str] = []
    for item in payload:
        if not isinstance(item, str) or not item.strip():
            raise ValidationError(f"--{field} must contain only non-empty strings")
        values.append(item.strip())
    return values


def _optional_bool(raw: Any, *, field: str) -> bool | None:
    if raw is None:
        return None
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        value = raw.strip().lower()
        if value in {"1", "true", "yes"}:
            return True
        if value in {"0", "false", "no"}:
            return False
    raise ValidationError(f"--{field} must be true or false")


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
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": method})
        return 0
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _normalize_event_body(raw: Any, *, event_id: str | None = None, require_revision: bool = False) -> dict[str, Any]:
    payload = _read_json_object(raw, field="event-json")
    body = dict(payload) if "event" in payload else {"event": payload}
    event = body.get("event")
    if not isinstance(event, dict) or not event:
        raise ValidationError("--event-json must include a non-empty event object")
    if event_id is not None:
        payload_id = event.get("id")
        if payload_id is not None and str(payload_id).strip() != event_id:
            raise SafetyError("Refused: event id in body does not match --event-id")
        event.setdefault("id", event_id)
    if require_revision and not str(event.get("revision") or "").strip():
        raise ValidationError("--event-json event.revision is required for update")
    return body


def _body_with_common_options(body: dict[str, Any], args: Any) -> dict[str, Any]:
    result = dict(body)
    time_zone = _optional_text(getattr(args, "time_zone", None), field="time-zone")
    if time_zone:
        result["timeZone"] = time_zone
    return_entity = _optional_bool(getattr(args, "return_entity", None), field="return-entity")
    if return_entity is not None:
        result["returnEntity"] = return_entity
    participant_notification = getattr(args, "participant_notification_json", None)
    if participant_notification is not None:
        result["participantNotification"] = _read_json_object(participant_notification, field="participant-notification-json", allow_empty=True)
    return result


def _read_query_body(args: Any) -> dict[str, Any]:
    body = _read_json_object(getattr(args, "query_json", None) or "{}", field="query-json", allow_empty=True)
    time_zone = _optional_text(getattr(args, "time_zone", None), field="time-zone")
    if time_zone:
        body["timeZone"] = time_zone
    from_local_date = _optional_text(getattr(args, "from_local_date", None), field="from-local-date")
    if from_local_date:
        body["fromLocalDate"] = from_local_date
    to_local_date = _optional_text(getattr(args, "to_local_date", None), field="to-local-date")
    if to_local_date:
        body["toLocalDate"] = to_local_date
    recurrence_type = getattr(args, "recurrence_type_json", None)
    if recurrence_type is not None:
        body["recurrenceType"] = _read_string_list(recurrence_type, field="recurrence-type-json", max_items=5)
    fields = getattr(args, "fields_json", None)
    if fields is not None:
        body["fields"] = _read_string_list(fields, field="fields-json", max_items=1)
    return body


def _read_list_params(args: Any) -> dict[str, Any]:
    params: dict[str, Any] = {"eventIds": _read_string_list(getattr(args, "event_ids_json", None), field="event-ids-json", max_items=100)}
    fields = getattr(args, "fields_json", None)
    if fields is not None:
        params["fields"] = _read_string_list(fields, field="fields-json", max_items=1)
    time_zone = _optional_text(getattr(args, "time_zone", None), field="time-zone")
    if time_zone:
        params["timeZone"] = time_zone
    return params


def _read_participant_list_params(args: Any, *, include_event_ids: bool) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for attr, key in (("from_local_date", "fromLocalDate"), ("to_local_date", "toLocalDate"), ("time_zone", "timeZone"), ("app_id", "appId")):
        value = _optional_text(getattr(args, attr, None), field=attr.replace("_", "-"))
        if value:
            params[key] = value
    if include_event_ids and getattr(args, "event_ids_json", None) is not None:
        params["eventIds"] = _read_string_list(getattr(args, "event_ids_json", None), field="event-ids-json", max_items=100)
    for attr, key in (("cursor_paging_json", "cursorPaging"), ("sort_json", "sort")):
        raw = getattr(args, attr, None)
        if raw is not None:
            params[key] = _read_json_object(raw, field=attr.replace("_", "-"), allow_empty=True)
    has_cursor = "cursorPaging" in params
    has_event_ids = "eventIds" in params
    has_date_window = "fromLocalDate" in params and "toLocalDate" in params
    if not has_cursor and not has_event_ids and not has_date_window:
        raise ValidationError("--from-local-date and --to-local-date are required unless cursor paging or event IDs are provided")
    return params


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
        "state_capture": {"before_state_available": False, "notes": "Calendar Events V3 plans do not capture a full before-state snapshot in this boundary."},
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Use Calendar Events V3 reads and the Wix dashboard for manual recovery when possible."},
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
    body: dict[str, Any],
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    ctx: dict[str, Any],
    requires_ack: bool = False,
    risk_reasons: list[str] | None = None,
    verification_notes: str = "Provider response confirms the request was accepted; inspect the event afterward with Calendar Events V3 reads.",
) -> int:
    auth = _resolve_auth(ctx)
    request = {"method": http_method, "path": path, "body": body}
    plan = _build_plan(
        method_name=method_name,
        request=request,
        selector=selector,
        proposed_changes=proposed_changes,
        ctx=ctx,
        requires_ack=requires_ack,
        risk_reasons=risk_reasons or ["wix-calendar-events-v3-write"],
        verification_notes=verification_notes,
    )
    apply_allowed = reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=method_name)
    if not apply_allowed:
        plan_out = ctx.get("plan_out")
        out = {"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth["mode"], "plan": plan, "plan_out": write_json_file(plan_out, plan) if plan_out else None}
        ctx["audit"].write(f"{method_name}.plan", out)
        ctx["out"].emit(out)
        return 0
    loaded_plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], params=None, json_body=body, ctx=ctx)
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
    receipt_out = ctx.get("receipt_out")
    out = {"ok": True, "dry_run": False, "method": method_name, "auth_mode": auth["mode"], "receipt": receipt, "receipt_out": write_json_file(receipt_out, receipt) if receipt_out else None}
    ctx["audit"].write(f"{method_name}.apply", out)
    ctx["out"].emit(out)
    return 0


def cmd_calendar_events_v3_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _body_with_common_options(_normalize_event_body(getattr(args, "event_json", None)), args)
        idempotency_key = _optional_text(getattr(args, "idempotency_key", None), field="idempotency-key")
        if idempotency_key:
            body["idempotencyKey"] = idempotency_key
        return _run_write(method_name=method, http_method="POST", path=BASE_PATH, body=body, selector={"kind": COMMAND_FAMILY, "operation": "create"}, proposed_changes=[{"operation": "create-calendar-event"}], ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_calendar_events_v3_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        event_id = _coerce_text(getattr(args, "event_id", None), field="event-id")
        params: dict[str, Any] = {}
        fields = getattr(args, "fields_json", None)
        if fields is not None:
            params["fields"] = _read_string_list(fields, field="fields-json", max_items=1)
        time_zone = _optional_text(getattr(args, "time_zone", None), field="time-zone")
        if time_zone:
            params["timeZone"] = time_zone
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/{event_id}", params=params or None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_calendar_events_v3_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        event_id = _coerce_text(getattr(args, "event_id", None), field="event-id")
        body = _body_with_common_options(_normalize_event_body(getattr(args, "event_json", None), event_id=event_id, require_revision=True), args)
        return _run_write(method_name=method, http_method="PATCH", path=f"{BASE_PATH}/{event_id}", body=body, selector={"kind": COMMAND_FAMILY, "event_id": event_id, "operation": "update"}, proposed_changes=[{"operation": "update-calendar-event", "event_id": event_id}], ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_calendar_events_v3_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/query", body=_read_query_body(args), ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_calendar_events_v3_list(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list"
    try:
        return _run_read(method_name=method, http_method="GET", path=BASE_PATH, params=_read_list_params(args), ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_calendar_events_v3_bulk_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-create"
    try:
        body = _body_with_common_options({"events": _read_json_list(getattr(args, "events_json", None), field="events-json", max_items=50)}, args)
        return _run_write(method_name=method, http_method="POST", path=f"{BULK_PATH}/create", body=body, selector={"kind": COMMAND_FAMILY, "operation": "bulk-create"}, proposed_changes=[{"operation": "bulk-create-calendar-events"}], ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_calendar_events_v3_bulk_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update"
    try:
        events = _read_json_list(getattr(args, "events_json", None), field="events-json", max_items=50)
        for index, item in enumerate(events):
            event = item.get("event") if isinstance(item, dict) else None
            if not isinstance(event, dict) or not str(event.get("revision") or "").strip():
                raise ValidationError(f"--events-json item {index} must include event.revision")
        body = _body_with_common_options({"events": events}, args)
        return _run_write(method_name=method, http_method="POST", path=f"{BULK_PATH}/update", body=body, selector={"kind": COMMAND_FAMILY, "operation": "bulk-update"}, proposed_changes=[{"operation": "bulk-update-calendar-events"}], ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_calendar_events_v3_bulk_cancel(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-cancel"
    try:
        body = _body_with_common_options({"eventIds": _read_string_list(getattr(args, "event_ids_json", None), field="event-ids-json", max_items=50)}, args)
        return _run_write(method_name=method, http_method="POST", path=f"{BULK_PATH}/cancel", body=body, selector={"kind": COMMAND_FAMILY, "operation": "bulk-cancel"}, proposed_changes=[{"operation": "bulk-cancel-calendar-events"}], ctx=ctx, requires_ack=True, risk_reasons=["wix-calendar-events-v3-bulk-cancel", "cancels-calendar-events", "may-notify-participants"])
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_calendar_events_v3_cancel(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.cancel"
    try:
        event_id = _coerce_text(getattr(args, "event_id", None), field="event-id")
        body = _body_with_common_options({}, args)
        return _run_write(method_name=method, http_method="POST", path=f"{BASE_PATH}/{event_id}/cancel", body=body, selector={"kind": COMMAND_FAMILY, "event_id": event_id, "operation": "cancel"}, proposed_changes=[{"operation": "cancel-calendar-event", "event_id": event_id}], ctx=ctx, requires_ack=True, risk_reasons=["wix-calendar-events-v3-cancel", "cancels-calendar-event", "may-notify-participants"])
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_calendar_events_v3_list_by_contact(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list-by-contact"
    try:
        contact_id = _coerce_text(getattr(args, "contact_id", None), field="contact-id")
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/contactId/{contact_id}", params=_read_participant_list_params(args, include_event_ids=False) or None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_calendar_events_v3_list_by_member(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list-by-member"
    try:
        member_id = _coerce_text(getattr(args, "member_id", None), field="member-id")
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/memberId/{member_id}", params=_read_participant_list_params(args, include_event_ids=True) or None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_calendar_events_v3_restore_defaults(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.restore-defaults"
    try:
        event_id = _coerce_text(getattr(args, "event_id", None), field="event-id")
        body = _body_with_common_options({"fields": _read_string_list(getattr(args, "fields_json", None), field="fields-json")}, args)
        return _run_write(method_name=method, http_method="POST", path=f"{BASE_PATH}/{event_id}/restore-defaults", body=body, selector={"kind": COMMAND_FAMILY, "event_id": event_id, "operation": "restore-defaults"}, proposed_changes=[{"operation": "restore-calendar-event-defaults", "event_id": event_id}], ctx=ctx, requires_ack=True, risk_reasons=["wix-calendar-events-v3-restore-defaults", "overwrites-event-fields-with-schedule-defaults"])
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_calendar_events_v3_split_recurring(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.split-recurring"
    try:
        recurring_event_id = _coerce_text(getattr(args, "recurring_event_id", None), field="recurring-event-id")
        body = _body_with_common_options({"splitLocalDate": _coerce_text(getattr(args, "split_local_date", None), field="split-local-date")}, args)
        body.pop("returnEntity", None)
        body.pop("participantNotification", None)
        return _run_write(method_name=method, http_method="POST", path=f"{BASE_PATH}/{recurring_event_id}/split", body=body, selector={"kind": COMMAND_FAMILY, "recurring_event_id": recurring_event_id, "operation": "split-recurring"}, proposed_changes=[{"operation": "split-recurring-calendar-event", "recurring_event_id": recurring_event_id}], ctx=ctx, requires_ack=True, risk_reasons=["wix-calendar-events-v3-split-recurring", "splits-recurring-series"])
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
