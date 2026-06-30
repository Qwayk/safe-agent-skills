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


COMMAND_FAMILY = "events-rsvps-v2"
BASE_PATH = "/events/v2/rsvps"


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


def _require_rsvp_revision(payload: dict[str, Any], *, field: str) -> None:
    rsvp = payload.get("rsvp")
    if not isinstance(rsvp, dict):
        raise ValidationError(f"--{field} must include an rsvp object")
    revision = rsvp.get("revision")
    if revision is None or str(revision).strip() == "":
        raise ValidationError(f"--{field} for update must include rsvp.revision")


def _require_bulk_rsvp_revisions(payload: dict[str, Any]) -> None:
    rsvps = payload.get("rsvps")
    if not isinstance(rsvps, list) or not rsvps:
        raise ValidationError("--rsvps-json must include a non-empty rsvps array")
    if len(rsvps) > 100:
        raise ValidationError("--rsvps-json can include at most 100 RSVPs")
    for index, item in enumerate(rsvps):
        rsvp = item.get("rsvp") if isinstance(item, dict) else None
        if not isinstance(rsvp, dict):
            raise ValidationError(f"--rsvps-json rsvps[{index}] must include an rsvp object")
        if not str(rsvp.get("id") or rsvp.get("_id") or "").strip():
            raise ValidationError(f"--rsvps-json rsvps[{index}].rsvp must include id")
        if not str(rsvp.get("revision") or "").strip():
            raise ValidationError(f"--rsvps-json rsvps[{index}].rsvp must include revision")


def _event_ids(raw: Any) -> list[str]:
    if raw is None:
        raise ValidationError("Missing --event-id")
    values = raw if isinstance(raw, list) else [raw]
    event_ids = [_coerce_text(value, field="event-id") for value in values]
    if len(event_ids) > 100:
        raise ValidationError("--event-id can be repeated at most 100 times")
    return event_ids


def _validate_check_in_request(payload: dict[str, Any], *, field: str) -> None:
    guest_ids = payload.get("guestIds")
    if guest_ids is not None:
        if not isinstance(guest_ids, list):
            raise ValidationError(f"--{field} guestIds must be a JSON array")
        if len(guest_ids) > 11:
            raise ValidationError(f"--{field} guestIds can include at most 11 guests")
        if len(guest_ids) == 0:
            raise ValidationError(f"--{field} guestIds cannot be empty when provided")


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


def _run_read(
    *,
    method_name: str,
    http_method: str,
    path: str,
    ctx: dict[str, Any],
    body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], params=params, json_body=body, ctx=ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if params is not None:
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
        "state_capture": {"before_state_available": False, "notes": "Events RSVP V2 plans do not capture a full before-state snapshot in this slice."},
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Verify with RSVP reads and the Wix dashboard when needed."},
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
    verification_notes: str = "Provider response confirms the RSVP request was accepted.",
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
        risk_reasons=risk_reasons or ["wix-events-rsvp-v2-write"],
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
    out = {"ok": True, "dry_run": False, "method": method_name, "auth_mode": auth["mode"], "receipt": receipt}
    if ctx.get("receipt_out"):
        out["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
    ctx["audit"].write(f"{method_name}.apply", out)
    ctx["out"].emit(out)
    return 0


def cmd_events_rsvps_v2_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _read_json_arg(getattr(args, "rsvp_json", None), field="rsvp-json")
        return _run_write(method_name=method, http_method="POST", path=BASE_PATH, body=body, selector={"kind": COMMAND_FAMILY, "operation": "create"}, proposed_changes=[{"operation": "create-rsvp"}], ctx=ctx, risk_reasons=["wix-events-rsvp-v2-create", "confirmation-email-may-send"], verification_notes="Provider response confirms the RSVP create request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_rsvps_v2_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        rsvp_id = _coerce_text(getattr(args, "rsvp_id", None), field="rsvp-id")
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/{rsvp_id}", ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_rsvps_v2_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        rsvp_id = _coerce_text(getattr(args, "rsvp_id", None), field="rsvp-id")
        body = _read_json_arg(getattr(args, "rsvp_json", None), field="rsvp-json")
        _require_rsvp_revision(body, field="rsvp-json")
        return _run_write(method_name=method, http_method="PATCH", path=f"{BASE_PATH}/{rsvp_id}", body=body, selector={"kind": COMMAND_FAMILY, "rsvp_id": rsvp_id}, proposed_changes=[{"operation": "update-rsvp", "rsvp_id": rsvp_id}], ctx=ctx, risk_reasons=["wix-events-rsvp-v2-update", "guest-list-status-change"], verification_notes="Provider response confirms the RSVP update request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_rsvps_v2_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        rsvp_id = _coerce_text(getattr(args, "rsvp_id", None), field="rsvp-id")
        return _run_write(method_name=method, http_method="DELETE", path=f"{BASE_PATH}/{rsvp_id}", body=None, selector={"kind": COMMAND_FAMILY, "rsvp_id": rsvp_id}, proposed_changes=[{"operation": "delete-rsvp", "rsvp_id": rsvp_id}], ctx=ctx, requires_ack=True, risk_reasons=["wix-events-rsvp-v2-delete", "guest-list-removal"], verification_notes="Provider response confirms the RSVP delete request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_rsvps_v2_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        body = _read_json_arg(getattr(args, "query_json", "{}"), field="query-json")
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/query", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_rsvps_v2_search(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.search"
    try:
        body = _read_json_arg(getattr(args, "search_json", None), field="search-json")
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/search", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_rsvps_v2_count(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.count"
    try:
        body = _read_json_arg(getattr(args, "count_json", "{}"), field="count-json")
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/count", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_rsvps_v2_list_summary(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list-summary"
    try:
        event_ids = _event_ids(getattr(args, "event_id", None))
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/summaries", params={"eventId": event_ids}, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_rsvps_v2_bulk_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update"
    try:
        body = _read_json_arg(getattr(args, "rsvps_json", None), field="rsvps-json")
        _require_bulk_rsvp_revisions(body)
        return _run_write(method_name=method, http_method="PATCH", path="/events/v2/bulk/rsvps/update", body=body, selector={"kind": COMMAND_FAMILY, "operation": "bulk-update"}, proposed_changes=[{"operation": "bulk-update-rsvps"}], ctx=ctx, risk_reasons=["wix-events-rsvp-v2-bulk-update", "up-to-100-rsvps"], verification_notes="Provider response confirms the bulk RSVP update request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_rsvps_v2_bulk_delete_by_filter(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-delete-by-filter"
    try:
        body = _read_json_arg(getattr(args, "filter_json", None), field="filter-json")
        if not body:
            raise ValidationError("--filter-json cannot be empty for bulk delete")
        return _run_write(method_name=method, http_method="POST", path="/events/v2/bulk/rsvps/delete-by-filter", body=body, selector={"kind": COMMAND_FAMILY, "operation": "bulk-delete-by-filter"}, proposed_changes=[{"operation": "bulk-delete-rsvps-by-filter"}], ctx=ctx, requires_ack=True, risk_reasons=["wix-events-rsvp-v2-bulk-delete-by-filter", "multi-rsvp-removal"], verification_notes="Provider response confirms the bulk RSVP delete-by-filter request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_rsvps_v2_check_in(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.check-in"
    try:
        rsvp_id = _coerce_text(getattr(args, "rsvp_id", None), field="rsvp-id")
        body = _read_json_arg(getattr(args, "request_json", "{}"), field="request-json")
        _validate_check_in_request(body, field="request-json")
        return _run_write(method_name=method, http_method="POST", path=f"{BASE_PATH}/{rsvp_id}/check-in", body=body, selector={"kind": COMMAND_FAMILY, "rsvp_id": rsvp_id, "operation": "check-in"}, proposed_changes=[{"operation": "check-in-rsvp-guests", "rsvp_id": rsvp_id}], ctx=ctx, risk_reasons=["wix-events-rsvp-v2-check-in", "attendance-status-change"], verification_notes="Provider response confirms the RSVP guest check-in request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_rsvps_v2_cancel_check_in(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.cancel-check-in"
    try:
        rsvp_id = _coerce_text(getattr(args, "rsvp_id", None), field="rsvp-id")
        body = _read_json_arg(getattr(args, "request_json", "{}"), field="request-json")
        _validate_check_in_request(body, field="request-json")
        return _run_write(method_name=method, http_method="POST", path=f"{BASE_PATH}/{rsvp_id}/cancel-check-in", body=body, selector={"kind": COMMAND_FAMILY, "rsvp_id": rsvp_id, "operation": "cancel-check-in"}, proposed_changes=[{"operation": "cancel-rsvp-guest-check-in", "rsvp_id": rsvp_id}], ctx=ctx, requires_ack=True, risk_reasons=["wix-events-rsvp-v2-cancel-check-in", "attendance-proof-removal"], verification_notes="Provider response confirms the RSVP guest check-in cancellation request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
