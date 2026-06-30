from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import SafetyError, ValidationError
from ..http import HttpClient, HttpResponse
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested


COMMAND_FAMILY = "interactive-form-sessions"
BASE_PATH = "/forms/ai/v1/interactive-form-sessions"


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_object(raw: Any, *, field: str) -> dict[str, Any]:
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
    if not isinstance(payload, dict) or not payload:
        raise ValidationError(f"--{field} must be a non-empty JSON object")
    return payload


def _require_field(body: dict[str, Any], *, field_name: str, arg_name: str) -> None:
    if field_name not in body:
        raise ValidationError(f"--{arg_name} must include {field_name}")


def _normalize_send_body(raw: Any) -> dict[str, Any]:
    body = _read_object(raw, field="message-json")
    input_value = body.get("input")
    if not isinstance(input_value, str) or not input_value.strip():
        raise ValidationError("--message-json must include input")
    if len(input_value) > 10000:
        raise ValidationError("--message-json.input supports at most 10000 characters")
    body["input"] = input_value
    return body


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
    )


def _response_payload(response: HttpResponse) -> dict[str, Any]:
    try:
        payload = response.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {"rawText": response.text(), "contentType": response.headers.get("content-type")}
    if isinstance(payload, dict):
        return payload
    return {"json": payload}


def _request(
    *,
    path: str,
    headers: dict[str, str],
    body: dict[str, Any],
    ctx: dict[str, Any],
    streamed: bool = False,
) -> dict[str, Any]:
    request_headers = dict(headers)
    request_headers["Content-Type"] = "application/json"
    if streamed:
        request_headers["Accept"] = "text/event-stream"
    client = HttpClient(
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
        user_agent="wix-safe-agent-cli",
    )
    response = client.request(
        method="POST",
        url=ctx["cfg"].base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=None,
        json_body=body,
    )
    return _response_payload(response)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _emit_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, SafetyError):
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "refused": True,
                "reasons": [str(exc)],
                "refusal_type": "SafetyError",
                "method": method,
            }
        )
        return 0
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _run_helper(*, method_name: str, path: str, body: dict[str, Any], ctx: dict[str, Any]) -> int:
    auth = _resolve_auth(ctx)
    response = _request(path=path, headers=auth["headers"], body=body, ctx=ctx)
    out = {
        "ok": True,
        "method": method_name,
        "auth_mode": auth["mode"],
        "request": {"method": "POST", "path": path, "body": body},
        "response": response,
    }
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _build_plan(
    *,
    method_name: str,
    path: str,
    body: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    streamed: bool,
    verification_notes: str,
) -> dict[str, Any]:
    request: dict[str, Any] = {"method": "POST", "path": path, "body": body}
    if streamed:
        request["headers"] = {"Accept": "text/event-stream"}
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "risk_level": "medium",
        "risk_reasons": ["interactive-form-session-ai-conversation"],
        "preconditions": ["env_fingerprint must match", "selector must match", "apply requires --plan-in, --apply, and --yes"],
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {
            "before_state_available": False,
            "notes": "Interactive Form Sessions are conversational session operations; this slice does not capture full before-state.",
        },
        "proposed_changes": [{"operation": method_name, "selector": selector}],
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {
            "supported": False,
            "notes": "No automatic rollback. Use dryRun in the official request body when testing conversational flows.",
        },
    }


def _load_plan(*, plan_in: str | None, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> None:
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


def _run_write(
    *,
    method_name: str,
    path: str,
    body: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    streamed: bool,
    verification_notes: str,
) -> int:
    auth = _resolve_auth(ctx)
    plan = _build_plan(
        method_name=method_name,
        path=path,
        body=body,
        selector=selector,
        ctx=ctx,
        streamed=streamed,
        verification_notes=verification_notes,
    )
    apply_allowed = reviewed_plan_apply_requested(ctx, requires_ack=False, command_label=method_name)
    if not apply_allowed:
        out = {"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth["mode"], "plan": plan}
        if not ctx.get("apply") and ctx.get("plan_out"):
            out["plan_out"] = write_json_file(ctx["plan_out"], plan)
        ctx["audit"].write(f"{method_name}.plan", out)
        ctx["out"].emit(out)
        return 0

    _load_plan(plan_in=ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request(path=path, headers=auth["headers"], body=body, ctx=ctx, streamed=streamed)
    receipt = {
        "ok": True,
        "dry_run": False,
        "method": method_name,
        "auth_mode": auth["mode"],
        "request": plan["request"],
        "response": response,
        "verified": {"type": "provider-response", "notes": verification_notes},
    }
    if ctx.get("receipt_out"):
        receipt["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
    ctx["audit"].write(f"{method_name}.apply", receipt)
    ctx["out"].emit(receipt)
    return 0


def cmd_interactive_form_sessions_create(args, ctx) -> int:
    method = "interactive-form-sessions.create"
    try:
        body = _read_object(args.session_json, field="session-json")
        _require_field(body, field_name="formId", arg_name="session-json")
        return _run_write(
            method_name=method,
            path=BASE_PATH,
            body=body,
            selector={"formId": body["formId"]},
            ctx=ctx,
            streamed=False,
            verification_notes="Inspect provider response for interactiveFormSession.id and responseChunks.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_interactive_form_sessions_create_streamed(args, ctx) -> int:
    method = "interactive-form-sessions.create-streamed"
    try:
        body = _read_object(args.session_json, field="session-json")
        _require_field(body, field_name="formId", arg_name="session-json")
        return _run_write(
            method_name=method,
            path=f"{BASE_PATH}/create-streamed",
            body=body,
            selector={"formId": body["formId"]},
            ctx=ctx,
            streamed=True,
            verification_notes="Inspect provider response or raw event-stream text for session chunks.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_interactive_form_sessions_send_message(args, ctx) -> int:
    method = "interactive-form-sessions.send-message"
    try:
        session_id = _coerce_text(args.session_id, field="session-id")
        body = _normalize_send_body(args.message_json)
        return _run_write(
            method_name=method,
            path=f"{BASE_PATH}/{session_id}/send-user-message",
            body=body,
            selector={"interactiveFormSessionId": session_id},
            ctx=ctx,
            streamed=False,
            verification_notes="Inspect provider response for updated interactive form session and responseChunks.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_interactive_form_sessions_send_message_streamed(args, ctx) -> int:
    method = "interactive-form-sessions.send-message-streamed"
    try:
        session_id = _coerce_text(args.session_id, field="session-id")
        body = _normalize_send_body(args.message_json)
        return _run_write(
            method_name=method,
            path=f"{BASE_PATH}/{session_id}/send-user-message-streamed",
            body=body,
            selector={"interactiveFormSessionId": session_id},
            ctx=ctx,
            streamed=True,
            verification_notes="Inspect provider response or raw event-stream text for updated session chunks.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_interactive_form_sessions_generate_summary(args, ctx) -> int:
    method = "interactive-form-sessions.generate-summary"
    try:
        body = _read_object(args.form_json, field="form-json")
        _require_field(body, field_name="form", arg_name="form-json")
        return _run_helper(method_name=method, path=f"{BASE_PATH}/generate-form-summary", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
