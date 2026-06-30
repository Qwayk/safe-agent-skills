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


COMMAND_FAMILY = "portfolio-settings"
SETTINGS_PATH = "/portfolio/v1/settings"


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


def _resolve_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
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


def _build_selector() -> dict[str, Any]:
    return {"kind": COMMAND_FAMILY, "scope": "site-portfolio-settings"}


def _settings_object(payload: dict[str, Any]) -> dict[str, Any]:
    for key in ("portfolioSettings", "settings"):
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return payload


def _revision_from_payload(payload: dict[str, Any]) -> str | None:
    raw_revision = _settings_object(payload).get("revision")
    if raw_revision is None:
        return None
    revision = str(raw_revision).strip()
    return revision or None


def _body_with_current_revision(*, body: dict[str, Any], current_revision: str) -> dict[str, Any]:
    updated = dict(body)
    for key in ("portfolioSettings", "settings"):
        nested = updated.get(key)
        if isinstance(nested, dict):
            provided_revision = nested.get("revision")
            if provided_revision is not None and str(provided_revision).strip() != current_revision:
                raise SafetyError("Refused: provided portfolio settings revision does not match current revision")
            revised_nested = dict(nested)
            revised_nested["revision"] = current_revision
            updated[key] = revised_nested
            return updated

    provided_revision = updated.get("revision")
    if provided_revision is not None and str(provided_revision).strip() != current_revision:
        raise SafetyError("Refused: provided portfolio settings revision does not match current revision")
    updated["revision"] = current_revision
    return updated


def _build_plan(*, request: dict[str, Any], selector: dict[str, Any], ctx: dict[str, Any], before_state: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "portfolio-settings.update",
        "risk_level": "medium",
        "risk_reasons": ["portfolio-settings-write"],
        "preconditions": ["env_fingerprint must match", "selector must match", "apply requires --plan-in, --apply, and --yes"],
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": before_state},
        "proposed_changes": [{"operation": "update-portfolio-settings", "scope": selector["scope"]}],
        "verification_plan": {"type": "read-after-write", "notes": "Verify by rereading Portfolio Settings."},
        "rollback": {"supported": False, "notes": "No automatic rollback. Use before-state as a manual reference."},
    }


def _load_plan(*, plan_in: str | None, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan.get("method") or "") != "portfolio-settings.update":
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


def cmd_portfolio_settings_get(args, ctx) -> int:
    _ = args
    method_id = "portfolio-settings.get"
    try:
        headers, auth_mode = _resolve_auth(ctx=ctx)
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=SETTINGS_PATH,
            headers=headers,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {"ok": True, "method": method_id, "auth_mode": auth_mode, "request": {"method": "GET", "path": SETTINGS_PATH}, "response": payload}
        ctx["audit"].write(method_id, out)
        ctx["out"].emit(out)
        return 0
    except Exception as exc:
        return _emit_error(ctx, method=method_id, exc=exc)


def cmd_portfolio_settings_update(args, ctx) -> int:
    method_id = "portfolio-settings.update"
    try:
        body = _read_json_arg(getattr(args, "settings_json", None), field="settings-json")
        headers, auth_mode = _resolve_auth(ctx=ctx)
        before_state = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=SETTINGS_PATH,
            headers=headers,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        current_revision = _revision_from_payload(before_state)
        if not current_revision:
            raise SafetyError("Refused: current portfolio settings revision was not found")
        body = _body_with_current_revision(body=body, current_revision=current_revision)
        request = {"method": "PATCH", "path": SETTINGS_PATH, "body": body}
        selector = _build_selector()
        plan = _build_plan(request=request, selector=selector, ctx=ctx, before_state=before_state)
        if not reviewed_plan_apply_requested(ctx, requires_ack=False, command_label=method_id):
            plan_out = ctx.get("plan_out")
            out = {"ok": True, "dry_run": True, "method": method_id, "auth_mode": auth_mode, "plan": plan, "plan_out": write_json_file(plan_out, plan) if plan_out else None}
            ctx["audit"].write("portfolio-settings.update.plan", out)
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(plan_in=ctx.get("plan_in"), expected_selector=selector, ctx=ctx)
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=SETTINGS_PATH,
            headers=headers,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_state = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=SETTINGS_PATH,
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
        ctx["audit"].write("portfolio-settings.update.apply", out)
        ctx["out"].emit(out)
        return 0
    except Exception as exc:
        return _emit_error(ctx, method=method_id, exc=exc)
