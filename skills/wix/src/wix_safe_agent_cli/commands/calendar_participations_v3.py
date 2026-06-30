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


COMMAND_FAMILY = "calendar-participations-v3"
BASE_PATH = "/calendar/v3/participations"


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


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


def _normalize_participation_body(raw: Any, *, participation_id: str | None = None, require_revision: bool = False) -> dict[str, Any]:
    payload = _read_json_object(raw, field="participation-json")
    body = dict(payload) if "participation" in payload else {"participation": payload}
    participation = body.get("participation")
    if not isinstance(participation, dict) or not participation:
        raise ValidationError("--participation-json must include a non-empty participation object")
    if participation_id is not None:
        payload_id = participation.get("id")
        if payload_id is not None and str(payload_id).strip() != participation_id:
            raise SafetyError("Refused: participation id in body does not match --participation-id")
        participation.setdefault("id", participation_id)
    if require_revision and not str(participation.get("revision") or "").strip():
        raise ValidationError("--participation-json participation.revision is required for update")
    return body


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
    )


def _request_json(*, method: str, path: str, headers: dict[str, str], body: dict[str, Any] | None, ctx: dict[str, Any]) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
        request_headers["Content-Type"] = "application/json"
    client = HttpClient(timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")), user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=ctx["cfg"].base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=None,
        json_body=body,
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


def _run_read(*, method_name: str, http_method: str, path: str, body: dict[str, Any] | None, ctx: dict[str, Any]) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], body=body, ctx=ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
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
        "risk_reasons": ["wix-calendar-participations-v3-write", "updates-event-participants-and-remaining-capacity"],
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {"before_state_available": False, "notes": "Calendar Participations V3 plans do not capture a full before-state snapshot in this boundary."},
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response", "notes": "Provider response confirms the request was accepted; inspect the participation afterward when possible."},
        "rollback": {"supported": False, "notes": "No automatic rollback. Use Calendar Participations reads and the Wix dashboard for manual recovery when possible."},
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
) -> int:
    auth = _resolve_auth(ctx)
    request = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    plan = _build_plan(method_name=method_name, request=request, selector=selector, proposed_changes=proposed_changes, ctx=ctx, requires_ack=requires_ack)
    apply_allowed = reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=method_name)
    if not apply_allowed:
        plan_out = ctx.get("plan_out")
        out = {"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth["mode"], "plan": plan, "plan_out": write_json_file(plan_out, plan) if plan_out else None}
        ctx["audit"].write(f"{method_name}.plan", out)
        ctx["out"].emit(out)
        return 0
    loaded_plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], body=body, ctx=ctx)
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


def cmd_calendar_participations_v3_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _normalize_participation_body(getattr(args, "participation_json", None))
        return _run_write(method_name=method, http_method="POST", path=BASE_PATH, body=body, selector={"kind": COMMAND_FAMILY, "operation": "create"}, proposed_changes=[{"operation": "create-calendar-participation"}], ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_calendar_participations_v3_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        participation_id = _coerce_text(getattr(args, "participation_id", None), field="participation-id")
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/{participation_id}", body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_calendar_participations_v3_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        participation_id = _coerce_text(getattr(args, "participation_id", None), field="participation-id")
        body = _normalize_participation_body(getattr(args, "participation_json", None), participation_id=participation_id, require_revision=True)
        return _run_write(method_name=method, http_method="PATCH", path=f"{BASE_PATH}/{participation_id}", body=body, selector={"kind": COMMAND_FAMILY, "participation_id": participation_id, "operation": "update"}, proposed_changes=[{"operation": "update-calendar-participation", "participation_id": participation_id}], ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_calendar_participations_v3_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        participation_id = _coerce_text(getattr(args, "participation_id", None), field="participation-id")
        return _run_write(method_name=method, http_method="DELETE", path=f"{BASE_PATH}/{participation_id}", body=None, selector={"kind": COMMAND_FAMILY, "participation_id": participation_id, "operation": "delete"}, proposed_changes=[{"operation": "delete-calendar-participation", "participation_id": participation_id}], ctx=ctx, requires_ack=True)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_calendar_participations_v3_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        body = _read_json_object(getattr(args, "query_json", None) or "{}", field="query-json", allow_empty=True)
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/query", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
