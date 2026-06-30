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


COMMAND_FAMILY = "events-forms"
BASE_PATH = "/events/v1/events"


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


def _run_read(*, method_name: str, path: str, ctx: dict[str, Any]) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method="GET", path=path, headers=auth["headers"], ctx=ctx)
    out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": {"method": "GET", "path": path}, "response": response}
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
        "state_capture": {"before_state_available": False, "notes": "Events Forms plans do not capture a full before-state snapshot in this slice."},
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Verify with events-forms get-form and the Wix dashboard when needed."},
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
    verification_notes: str = "Provider response confirms the Events Forms request was accepted.",
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
        risk_reasons=risk_reasons or ["wix-events-form-write"],
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


def _form_path(event_id: str) -> str:
    return f"{BASE_PATH}/{event_id}/form"


def cmd_events_forms_get_form(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-form"
    try:
        event_id = _coerce_text(getattr(args, "event_id", None), field="event-id")
        return _run_read(method_name=method, path=_form_path(event_id), ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_forms_discard_draft(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.discard-draft"
    try:
        event_id = _coerce_text(getattr(args, "event_id", None), field="event-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=_form_path(event_id),
            body=None,
            selector={"kind": COMMAND_FAMILY, "event_id": event_id, "operation": "discard-draft"},
            proposed_changes=[{"operation": "discard-draft", "event_id": event_id}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-events-form-discard-draft", "deprecated-endpoint", "clears-draft-form-changes"],
            verification_notes="Provider response confirms the deprecated draft discard request was accepted; verify with events-forms get-form.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_forms_add_control(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.add-control"
    try:
        event_id = _coerce_text(getattr(args, "event_id", None), field="event-id")
        body = _read_json_arg(getattr(args, "control_json", None), field="control-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{_form_path(event_id)}/control",
            body=body,
            selector={"kind": COMMAND_FAMILY, "event_id": event_id, "operation": "add-control"},
            proposed_changes=[{"operation": "add-control", "event_id": event_id}],
            ctx=ctx,
            risk_reasons=["wix-events-form-add-control", "registration-form-change", "may-trigger-form-publishing"],
            verification_notes="Provider response confirms the control add request was accepted; verify with events-forms get-form.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_forms_update_control(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update-control"
    try:
        event_id = _coerce_text(getattr(args, "event_id", None), field="event-id")
        control_id = _coerce_text(getattr(args, "control_id", None), field="control-id")
        body = _read_json_arg(getattr(args, "control_json", None), field="control-json")
        return _run_write(
            method_name=method,
            http_method="PUT",
            path=f"{_form_path(event_id)}/controls/{control_id}",
            body=body,
            selector={"kind": COMMAND_FAMILY, "event_id": event_id, "control_id": control_id, "operation": "update-control"},
            proposed_changes=[{"operation": "update-control", "event_id": event_id, "control_id": control_id}],
            ctx=ctx,
            risk_reasons=["wix-events-form-update-control", "registration-form-change", "may-trigger-form-publishing"],
            verification_notes="Provider response confirms the control update request was accepted; verify with events-forms get-form.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_forms_delete_control(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete-control"
    try:
        event_id = _coerce_text(getattr(args, "event_id", None), field="event-id")
        control_id = _coerce_text(getattr(args, "control_id", None), field="control-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{_form_path(event_id)}/controls/{control_id}",
            body=None,
            selector={"kind": COMMAND_FAMILY, "event_id": event_id, "control_id": control_id, "operation": "delete-control"},
            proposed_changes=[{"operation": "delete-control", "event_id": event_id, "control_id": control_id}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-events-form-delete-control", "removes-registration-form-field", "may-trigger-form-publishing"],
            verification_notes="Provider response confirms the control delete request was accepted; verify with events-forms get-form.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_forms_update_messages(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update-messages"
    try:
        event_id = _coerce_text(getattr(args, "event_id", None), field="event-id")
        body = _read_json_arg(getattr(args, "messages_json", None), field="messages-json")
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{_form_path(event_id)}/messages",
            body=body,
            selector={"kind": COMMAND_FAMILY, "event_id": event_id, "operation": "update-messages"},
            proposed_changes=[{"operation": "update-messages", "event_id": event_id}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-events-form-update-messages", "visitor-facing-registration-copy-change"],
            verification_notes="Provider response confirms the message update request was accepted; verify with events-forms get-form.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_events_forms_publish_draft(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.publish-draft"
    try:
        event_id = _coerce_text(getattr(args, "event_id", None), field="event-id")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{_form_path(event_id)}/publish",
            body=None,
            selector={"kind": COMMAND_FAMILY, "event_id": event_id, "operation": "publish-draft"},
            proposed_changes=[{"operation": "publish-draft", "event_id": event_id}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-events-form-publish-draft", "deprecated-endpoint", "publishes-registration-form-draft"],
            verification_notes="Provider response confirms the deprecated draft publish request was accepted; verify with events-forms get-form.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
