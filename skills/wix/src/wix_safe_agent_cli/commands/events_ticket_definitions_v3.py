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


COMMAND_FAMILY = "events-ticket-definitions-v3"
BASE_PATH = "/events-ticket-definitions/v3/ticket-definitions"


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


def _normalize_ticket_definition_body(
    raw: Any,
    *,
    field: str,
    ticket_definition_id: str | None = None,
    require_revision: bool = False,
) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    body = dict(payload) if "ticketDefinition" in payload else {"ticketDefinition": payload}
    ticket_definition = body.get("ticketDefinition")
    if not isinstance(ticket_definition, dict) or not ticket_definition:
        raise ValidationError(f"--{field} must include a non-empty ticketDefinition object")

    if ticket_definition_id is not None:
        payload_id = ticket_definition.get("id")
        if payload_id is not None and str(payload_id).strip() != ticket_definition_id:
            raise SafetyError("Refused: ticket definition id in body does not match --ticket-definition-id")
        ticket_definition["id"] = ticket_definition_id

    if require_revision:
        revision = ticket_definition.get("revision")
        if revision is None or (isinstance(revision, str) and not revision.strip()):
            raise ValidationError(f"--{field} ticketDefinition.revision is required for update")
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
    request = {"method": http_method, "path": path}
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
        "state_capture": {"before_state_available": False, "notes": "No useful before-state snapshot is captured for this slice."},
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Recovery is manual only."},
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
    verification_notes: str = "Provider response confirms the write request and response shape.",
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
        risk_reasons=risk_reasons or ["wix-events-ticket-definitions-v3-write"],
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


def cmd_events_ticket_definitions_v3_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _read_json_arg(getattr(args, "ticket_definition_json", None), field="ticket-definition-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "create"},
            proposed_changes=[{"operation": "create-ticket-definition"}],
            ctx=ctx,
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_ticket_definitions_v3_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        ticket_definition_id = _coerce_text(getattr(args, "ticket_definition_id", None), field="ticket-definition-id")
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/{ticket_definition_id}", ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_ticket_definitions_v3_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        ticket_definition_id = _coerce_text(getattr(args, "ticket_definition_id", None), field="ticket-definition-id")
        body = _normalize_ticket_definition_body(
            getattr(args, "ticket_definition_json", None),
            field="ticket-definition-json",
            ticket_definition_id=ticket_definition_id,
            require_revision=True,
        )
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{ticket_definition_id}",
            body=body,
            selector={"kind": COMMAND_FAMILY, "ticket_definition_id": ticket_definition_id},
            proposed_changes=[{"operation": "update-ticket-definition", "ticket_definition_id": ticket_definition_id}],
            ctx=ctx,
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_ticket_definitions_v3_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        ticket_definition_id = _coerce_text(getattr(args, "ticket_definition_id", None), field="ticket-definition-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{ticket_definition_id}",
            body={},
            selector={"kind": COMMAND_FAMILY, "ticket_definition_id": ticket_definition_id},
            proposed_changes=[{"operation": "delete-ticket-definition", "ticket_definition_id": ticket_definition_id}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-events-ticket-definitions-v3-delete", "potential-revenue-impact"],
            verification_notes="Provider response confirms the ticket definition deletion was accepted.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_ticket_definitions_v3_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        body = _read_json_arg(getattr(args, "query_json", "{}"), field="query-json")
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/query", ctx=ctx, body=body)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_ticket_definitions_v3_bulk_delete_by_filter(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-delete-by-filter"
    try:
        body = _read_json_arg(getattr(args, "filter_json", None), field="filter-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/events-ticket-definitions/v3/bulk/ticket-definitions/delete-by-filter",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "bulk-delete-by-filter"},
            proposed_changes=[{"operation": "bulk-delete-ticket-definitions-by-filter"}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-events-ticket-definitions-v3-bulk-delete", "potential-revenue-impact"],
            verification_notes="Provider response confirms bulk delete-by-filter request was accepted.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_ticket_definitions_v3_change_currency(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.change-currency"
    try:
        body = _read_json_arg(getattr(args, "request_json", None), field="request-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/currency",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "change-currency"},
            proposed_changes=[{"operation": "change-ticket-definition-currency"}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-events-ticket-definitions-v3-change-currency", "accounting-impact"],
            verification_notes="Provider response confirms currency change request was accepted.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_ticket_definitions_v3_count(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.count"
    try:
        body = _read_json_arg(getattr(args, "filter_json", "{}"), field="filter-json")
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/count", ctx=ctx, body=body)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_ticket_definitions_v3_reorder(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.reorder"
    try:
        body = _read_json_arg(getattr(args, "request_json", None), field="request-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/reorder",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "reorder"},
            proposed_changes=[{"operation": "reorder-ticket-definitions"}],
            ctx=ctx,
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
