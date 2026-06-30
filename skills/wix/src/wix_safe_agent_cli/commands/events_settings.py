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


def _read_json_arg(raw: Any, *, field: str) -> dict[str, Any]:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a JSON object or @file path")
    text = raw.strip()
    if not text:
        raise ValidationError(f"--{field} cannot be empty")
    if text.startswith("@"):
        path = Path(text[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        text = path.read_text(encoding="utf-8").strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    return value


def _coerce_required_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _resolve_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="events-settings",
    )
    return auth["headers"], auth["mode"]


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


def _settings_id_from_payload(payload: dict[str, Any]) -> str | None:
    settings = payload.get("eventsSettings", payload.get("settings"))
    if isinstance(settings, dict):
        raw_id = settings.get("id")
        if isinstance(raw_id, str) and raw_id.strip():
            return raw_id.strip()
    raw_id = payload.get("id")
    if isinstance(raw_id, str) and raw_id.strip():
        return raw_id.strip()
    return None


def _build_selector(*, settings_id: str) -> dict[str, Any]:
    return {"kind": "events-settings", "events_settings_id": settings_id}


def _build_plan(*, request: dict[str, Any], selector: dict[str, Any], ctx: dict[str, Any], before_state: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "events-settings.update",
        "risk_level": "medium",
        "risk_reasons": ["events-settings-write", "developer-preview", "payment-setting-change"],
        "preconditions": ["env_fingerprint must match", "selector must match", "apply requires --plan-in, --apply, and --yes"],
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": before_state},
        "proposed_changes": [{"operation": "update-events-settings", "events_settings_id": selector["events_settings_id"]}],
        "verification_plan": {"type": "read-after-write", "notes": "Verify by rereading Events Settings."},
        "rollback": {"supported": False, "notes": "No automatic rollback. Use before-state as a manual reference."},
    }


def _load_plan(*, plan_in: str | None, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan.get("method") or "") != "events-settings.update":
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    return plan


def _emit_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, SafetyError):
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": method})
        return 0
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def cmd_events_settings_get(args, ctx) -> int:
    _ = args
    method_id = "events-settings.get"
    try:
        headers, auth_mode = _resolve_auth(ctx=ctx)
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/events/v1/settings",
            headers=headers,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {"ok": True, "method": method_id, "auth_mode": auth_mode, "request": {"method": "GET", "path": "/events/v1/settings"}, "response": payload}
        ctx["audit"].write(method_id, out)
        ctx["out"].emit(out)
        return 0
    except Exception as exc:
        return _emit_error(ctx, method=method_id, exc=exc)


def cmd_events_settings_update(args, ctx) -> int:
    method_id = "events-settings.update"
    try:
        settings_id = _coerce_required_text(getattr(args, "events_settings_id", None), field="events-settings-id")
        body = _read_json_arg(getattr(args, "settings_json", None), field="settings-json")
        headers, auth_mode = _resolve_auth(ctx=ctx)
        before_state = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/events/v1/settings",
            headers=headers,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        before_id = _settings_id_from_payload(before_state)
        if before_id and before_id != settings_id:
            raise SafetyError(f"Refused: current events settings id is {before_id}, not {settings_id}")
        path = f"/events/v1/settings/{settings_id}"
        request = {"method": "PATCH", "path": path, "body": body}
        selector = _build_selector(settings_id=settings_id)
        plan = _build_plan(request=request, selector=selector, ctx=ctx, before_state=before_state)
        if not reviewed_plan_apply_requested(ctx, requires_ack=False, command_label=method_id):
            plan_out = ctx.get("plan_out")
            out = {"ok": True, "dry_run": True, "method": method_id, "auth_mode": auth_mode, "plan": plan, "plan_out": write_json_file(plan_out, plan) if plan_out else None}
            ctx["audit"].write("events-settings.update.plan", out)
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(plan_in=ctx.get("plan_in"), expected_selector=selector, ctx=ctx)
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=path,
            headers=headers,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_state = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/events/v1/settings",
            headers=headers,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": method_id,
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": {"ok": True, "type": "read-after-write", "after": after_state},
            "diff_applied": loaded_plan.get("proposed_changes") or [],
            "recovery": {"automatic": False, "notes": "Recovery is manual only."},
        }
        receipt_out = ctx.get("receipt_out")
        out = {
            "ok": True,
            "dry_run": False,
            "method": method_id,
            "auth_mode": auth_mode,
            "request": request,
            "response": response,
            "receipt": receipt,
            "receipt_out": write_json_file(receipt_out, receipt) if receipt_out else None,
        }
        ctx["audit"].write("events-settings.update.apply", out)
        ctx["out"].emit(out)
        return 0
    except Exception as exc:
        return _emit_error(ctx, method=method_id, exc=exc)
