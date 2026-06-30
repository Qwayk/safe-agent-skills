from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from ..authz import resolve_auth_mode
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested


COMMAND_FAMILY = "events-categories"
BASE_PATH = "/events/v1/categories"


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


def _split_csv(raw: Any, *, field: str) -> list[str]:
    value = _coerce_text(raw, field=field)
    items = [item.strip() for item in value.split(",") if item.strip()]
    if not items:
        raise ValidationError(f"--{field} must include at least one ID")
    return items


def _events_query(event_ids: list[str]) -> str:
    return urlencode([("eventId", event_id) for event_id in event_ids])


def _bulk_query(category_ids: list[str], event_ids: list[str]) -> str:
    pairs = [("categoryId", category_id) for category_id in category_ids]
    pairs.extend(("eventId", event_id) for event_id in event_ids)
    return urlencode(pairs)


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
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> int:
    auth = _resolve_auth(ctx)
    payload = _request_json(method=http_method, path=path, headers=auth["headers"], params=params, json_body=body, ctx=ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if params is not None:
        request["params"] = params
    if body is not None:
        request["body"] = body
    out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": request, "response": payload}
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
        "state_capture": {"before_state_available": False, "notes": "Events Categories plans do not capture a full before-state snapshot in this slice."},
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Verify with category reads and the Wix dashboard when needed."},
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
    verification_notes: str = "Provider response confirms the request was accepted.",
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
        risk_reasons=risk_reasons or ["wix-events-categories-write"],
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


def cmd_events_categories_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _read_json_arg(getattr(args, "category_json", None), field="category-json")
        return _run_write(method_name=method, http_method="POST", path=BASE_PATH, body=body, selector={"kind": COMMAND_FAMILY, "operation": "create"}, proposed_changes=[{"operation": "create-event-category"}], ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_categories_bulk_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-create"
    try:
        body = _read_json_arg(getattr(args, "categories_json", None), field="categories-json")
        return _run_write(method_name=method, http_method="POST", path="/events/v1/bulk/categories/create", body=body, selector={"kind": COMMAND_FAMILY, "operation": "bulk-create"}, proposed_changes=[{"operation": "bulk-create-event-categories"}], ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_categories_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        category_id = _coerce_text(getattr(args, "category_id", None), field="category-id")
        body = _read_json_arg(getattr(args, "category_json", None), field="category-json")
        return _run_write(method_name=method, http_method="PATCH", path=f"{BASE_PATH}/{category_id}", body=body, selector={"kind": COMMAND_FAMILY, "category_id": category_id}, proposed_changes=[{"operation": "update-event-category", "category_id": category_id}], ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_categories_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        category_id = _coerce_text(getattr(args, "category_id", None), field="category-id")
        return _run_write(method_name=method, http_method="DELETE", path=f"{BASE_PATH}/{category_id}", body=None, selector={"kind": COMMAND_FAMILY, "category_id": category_id}, proposed_changes=[{"operation": "delete-event-category", "category_id": category_id}], ctx=ctx, requires_ack=True, risk_reasons=["wix-events-categories-delete", "event-discovery-impact"], verification_notes="Provider response confirms the category deletion request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_categories_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        body = _read_json_arg(getattr(args, "query_json", "{}"), field="query-json")
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/query", ctx=ctx, body=body)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_categories_assign_events(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.assign-events"
    try:
        category_id = _coerce_text(getattr(args, "category_id", None), field="category-id")
        body = _read_json_arg(getattr(args, "events_json", None), field="events-json")
        return _run_write(method_name=method, http_method="POST", path=f"{BASE_PATH}/{category_id}/events", body=body, selector={"kind": COMMAND_FAMILY, "category_id": category_id}, proposed_changes=[{"operation": "assign-events-to-category", "category_id": category_id}], ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_categories_unassign_events(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.unassign-events"
    try:
        category_id = _coerce_text(getattr(args, "category_id", None), field="category-id")
        event_ids = _split_csv(getattr(args, "event_ids", None), field="event-ids")
        path = f"{BASE_PATH}/{category_id}/events?{_events_query(event_ids)}"
        return _run_write(method_name=method, http_method="DELETE", path=path, body=None, selector={"kind": COMMAND_FAMILY, "category_id": category_id, "event_ids": event_ids}, proposed_changes=[{"operation": "unassign-events-from-category", "category_id": category_id, "event_ids": event_ids}], ctx=ctx, requires_ack=True, risk_reasons=["wix-events-categories-unassign-events", "event-discovery-impact"], verification_notes="Provider response confirms the event unassignment request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_categories_bulk_assign_events(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-assign-events"
    try:
        body = _read_json_arg(getattr(args, "request_json", None), field="request-json")
        return _run_write(method_name=method, http_method="POST", path="/events/v1/bulk/categories/events", body=body, selector={"kind": COMMAND_FAMILY, "operation": "bulk-assign-events"}, proposed_changes=[{"operation": "bulk-assign-events-to-categories"}], ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_categories_bulk_unassign_events(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-unassign-events"
    try:
        category_ids = _split_csv(getattr(args, "category_ids", None), field="category-ids")
        event_ids = _split_csv(getattr(args, "event_ids", None), field="event-ids")
        path = f"/events/v1/bulk/categories/events?{_bulk_query(category_ids, event_ids)}"
        return _run_write(method_name=method, http_method="DELETE", path=path, body=None, selector={"kind": COMMAND_FAMILY, "category_ids": category_ids, "event_ids": event_ids}, proposed_changes=[{"operation": "bulk-unassign-events-from-categories", "category_ids": category_ids, "event_ids": event_ids}], ctx=ctx, requires_ack=True, risk_reasons=["wix-events-categories-bulk-unassign-events", "event-discovery-impact"], verification_notes="Provider response confirms the bulk event unassignment request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_categories_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        category_id = _coerce_text(getattr(args, "category_id", None), field="category-id")
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/{category_id}", ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_categories_reorder_events(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.reorder-events"
    try:
        category_id = _coerce_text(getattr(args, "category_id", None), field="category-id")
        body = _read_json_arg(getattr(args, "request_json", None), field="request-json")
        return _run_write(method_name=method, http_method="POST", path=f"{BASE_PATH}/{category_id}/reorder", body=body, selector={"kind": COMMAND_FAMILY, "category_id": category_id}, proposed_changes=[{"operation": "reorder-category-events", "category_id": category_id}], ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
