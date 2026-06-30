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


COMMAND_FAMILY = "receipts-settings"
BASE_PATH = "/receipts/v1/receipts-settings"


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    value = str(raw).strip()
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
    if not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _settings_body(raw: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = _read_json_arg(raw, field="settings-json")
    body = dict(payload) if "receiptsSettings" in payload else {"receiptsSettings": payload}
    settings = body.get("receiptsSettings")
    if not isinstance(settings, dict) or not settings:
        raise ValidationError("--settings-json must include a non-empty receiptsSettings object")
    _coerce_text(settings.get("revision"), field="settings-json receiptsSettings.revision")
    return body, settings


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
    json_body: dict[str, Any] | None,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
        request_headers["Content-Type"] = "application/json"
    client = HttpClient(
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
        user_agent="wix-safe-agent-cli",
    )
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


def _build_plan(
    *,
    method_name: str,
    request: dict[str, Any],
    settings: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    selector = {"scope": "site-receipts-settings", "revision": settings.get("revision")}
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "risk_level": "medium",
        "risk_reasons": ["wix-receipts-settings-update", "receipt-numbering-settings-change", "requires-current-revision"],
        "preconditions": ["env_fingerprint must match", "selector must match", "apply requires --plan-in, --apply, and --yes"],
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {
            "before_state_available": False,
            "notes": "Receipts Settings plans do not capture a full before-state snapshot in this slice.",
        },
        "proposed_changes": [{"operation": "update-receipts-settings", "receiptsSettings": settings}],
        "verification_plan": {
            "type": "provider-response-plus-readback",
            "notes": "After apply, call receipts-settings get and compare the returned numbering settings to the reviewed update body.",
        },
        "rollback": {"supported": False, "notes": "No automatic rollback. Reapply prior numbering settings manually if needed."},
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


def cmd_receipts_settings_get(args, ctx) -> int:
    method = "receiptsSettings.getReceiptsSettings"
    try:
        _ = args
        auth = _resolve_auth(ctx)
        response = _request_json(method="GET", path=BASE_PATH, headers=auth["headers"], json_body=None, ctx=ctx)
        out = {
            "ok": True,
            "method": method,
            "auth_mode": auth["mode"],
            "request": {"method": "GET", "path": BASE_PATH},
            "response": response,
        }
        ctx["audit"].write(method, out)
        ctx["out"].emit(out)
        return 0
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_receipts_settings_update(args, ctx) -> int:
    method = "receiptsSettings.updateReceiptsSettings"
    try:
        body, settings = _settings_body(args.settings_json)
        request = {"method": "PATCH", "path": BASE_PATH, "body": body}
        auth = _resolve_auth(ctx)
        selector = {"scope": "site-receipts-settings", "revision": settings.get("revision")}
        plan = _build_plan(method_name=method, request=request, settings=settings, ctx=ctx)
        if not reviewed_plan_apply_requested(ctx, requires_ack=False, command_label=method):
            out = {"ok": True, "dry_run": True, "method": method, "auth_mode": auth["mode"], "plan": plan}
            if not ctx.get("apply") and ctx.get("plan_out"):
                out["plan_out"] = write_json_file(ctx["plan_out"], plan)
            ctx["audit"].write(f"{method}.plan", out)
            ctx["out"].emit(out)
            return 0
        loaded_plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method=method, expected_selector=selector, ctx=ctx)
        response = _request_json(method="PATCH", path=BASE_PATH, headers=auth["headers"], json_body=body, ctx=ctx)
        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": method,
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": {
                "ok": True,
                "type": "provider-response-plus-readback",
                "notes": "Provider accepted the update. Run receipts-settings get to verify the site numbering settings.",
            },
            "diff_applied": loaded_plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
            "recovery": {"automatic": False, "notes": "Recovery is manual only."},
        }
        out = {"ok": True, "dry_run": False, "method": method, "auth_mode": auth["mode"], "receipt": receipt}
        if ctx.get("receipt_out"):
            out["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
        ctx["audit"].write(f"{method}.receipt", out)
        ctx["out"].emit(out)
        return 0
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
