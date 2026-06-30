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


def _read_json_arg(raw: Any, field: str) -> Any:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a JSON string, JSON file path, or omitted")
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


def _coerce_bool(raw: Any, *, field: str) -> bool:
    value = str(raw or "").strip().lower()
    if value not in {"true", "false"}:
        raise ValidationError(f"--{field} must be true or false")
    return value == "true"


def _coerce_locale_settings(raw: Any) -> dict[str, Any]:
    value = _read_json_arg(raw, "locale-settings-json")
    if not isinstance(value, dict):
        raise ValidationError("--locale-settings-json must be a JSON object")
    revision = str(value.get("revision") or "").strip()
    if not revision:
        raise ValidationError("--locale-settings-json must include revision")
    if "multilingualModeEnabled" in value:
        raise ValidationError("Use set-mode to enable or disable multilingual mode")
    return value


def _resolve_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="multilingual-locale-settings",
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


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    requires_ack: bool,
    risk_reasons: list[str],
) -> dict[str, Any]:
    preconditions = ["env_fingerprint must match", "selector must match", "apply requires --apply and --yes"]
    if requires_ack:
        preconditions.append("apply requires --ack-irreversible")
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "critical" if requires_ack else "high",
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector},
        "proposed_changes": [{"operation": selector.get("operation"), **{k: v for k, v in selector.items() if k not in {"kind", "operation"}}}],
        "verification_plan": {
            "type": "provider-response",
            "notes": "Verify localeSettings in the provider response, then run multilingual-locale-settings get when live confirmation is needed.",
        },
        "rollback": {"supported": False, "notes": "No automatic rollback is available for locale settings changes."},
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
        raise SafetyError("Refused: plan missing baseline")
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


def _build_receipt(*, method: str, request: dict[str, Any], response: dict[str, Any], selector: dict[str, Any], plan: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    verification = {
        "ok": isinstance(response.get("localeSettings"), dict),
        "type": "provider-response",
        "notes": "Provider response must include localeSettings.",
        "response": response,
    }
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "selector": selector,
        "request": request,
        "response": response,
        "changed": bool(verification["ok"]),
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }


def _write_command(*, method: str, request: dict[str, Any], selector: dict[str, Any], ctx: dict[str, Any], requires_ack: bool, risk_reasons: list[str]) -> int:
    auth_headers, auth_mode = _resolve_auth(ctx=ctx)
    plan_in = ctx.get("plan_in")
    if plan_in:
        plan = _load_plan(plan_in=str(plan_in), expected_method=method, expected_selector=selector, ctx=ctx)
    else:
        plan = _build_plan(method=method, request=request, selector=selector, ctx=ctx, requires_ack=requires_ack, risk_reasons=risk_reasons)
    if not reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="multilingual-locale-settings"):
        ctx["out"].emit({"ok": True, "dry_run": True, "method": method, "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)})
        return 0
    loaded_plan = _load_plan(plan_in=str(plan_in), expected_method=method, expected_selector=selector, ctx=ctx) if plan_in else plan
    response = _request_json(
        method=request["method"],
        base_url=ctx["cfg"].base_url,
        path=request["path"],
        headers=auth_headers,
        json_body=request.get("body"),
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    receipt = _build_receipt(method=method, request=request, response=response, selector=selector, plan=loaded_plan, ctx=ctx)
    out = {"ok": bool(receipt["verification"]["ok"]), "dry_run": False, "method": method, "auth_mode": auth_mode, "receipt": receipt, "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt)}
    ctx["out"].emit(out)
    return 0 if out["ok"] else 1


def cmd_multilingual_locale_settings_get(args, ctx) -> int:
    try:
        _ = args
        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        path = "/locale-settings/v2/settings"
        response = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=path,
            headers=auth_headers,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {"ok": True, "method": "multilingual-locale-settings.get", "auth_mode": auth_mode, "request": {"method": "GET", "path": path}, "response": response}
        ctx["audit"].write("multilingual-locale-settings.get", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "multilingual-locale-settings.get"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-locale-settings.get"})
        return 1


def cmd_multilingual_locale_settings_set_mode(args, ctx) -> int:
    try:
        enabled = _coerce_bool(getattr(args, "enabled", None), field="enabled")
        request = {"method": "POST", "path": "/locale-settings/v2/settings/mode", "body": {"multilingualModeEnabled": enabled}}
        selector = {"kind": "wix-multilingual-locale-settings", "operation": "set-mode", "multilingualModeEnabled": enabled}
        return _write_command(
            method="multilingual-locale-settings.set-mode",
            request=request,
            selector=selector,
            ctx=ctx,
            requires_ack=not enabled,
            risk_reasons=["multilingual-mode-change", "translated-content-removal" if not enabled else "multilingual-mode-enable"],
        )
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-locale-settings.set-mode"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "multilingual-locale-settings.set-mode"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-locale-settings.set-mode"})
        return 1


def cmd_multilingual_locale_settings_update(args, ctx) -> int:
    try:
        locale_settings = _coerce_locale_settings(getattr(args, "locale_settings_json", None))
        request = {"method": "PATCH", "path": "/locale-settings/v2/settings", "body": {"localeSettings": locale_settings}}
        selector = {
            "kind": "wix-multilingual-locale-settings",
            "operation": "update",
            "revision": str(locale_settings.get("revision") or ""),
        }
        return _write_command(
            method="multilingual-locale-settings.update",
            request=request,
            selector=selector,
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["locale-settings-update", "seo-impact"],
        )
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-locale-settings.update"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "multilingual-locale-settings.update"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-locale-settings.update"})
        return 1
