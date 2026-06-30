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


COMMAND_FAMILY = "headless-verification"
VERIFY_DURING_AUTHENTICATION_PATH = "/_api/iam/verification/v1/auth/verify"
REDACTED = "[REDACTED]"

_SENSITIVE_KEYS = {
    "access_token",
    "accesstoken",
    "authorization",
    "code",
    "refresh_token",
    "refreshtoken",
    "sessiontoken",
    "set-cookie",
    "statetoken",
    "token",
}


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


def _redact_sensitive(value: Any, *, parent_key: str | None = None) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            normalized = str(key).replace("_", "").replace("-", "").lower()
            if normalized in _SENSITIVE_KEYS:
                redacted[key] = REDACTED
            else:
                redacted[key] = _redact_sensitive(item, parent_key=str(key))
        return redacted
    if isinstance(value, list):
        return [_redact_sensitive(item, parent_key=parent_key) for item in value]
    if parent_key and str(parent_key).replace("_", "").replace("-", "").lower() in _SENSITIVE_KEYS:
        return REDACTED
    return value


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
    )


def _request_json(*, path: str, headers: dict[str, str], json_body: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    request_headers = dict(headers)
    request_headers["Content-Type"] = "application/json"
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


def _build_body(args: Any) -> dict[str, Any]:
    if getattr(args, "verification_json", None):
        body = _read_json_arg(getattr(args, "verification_json", None), field="verification-json")
    else:
        body = {
            "code": _coerce_text(getattr(args, "code", None), field="code"),
            "stateToken": _coerce_text(getattr(args, "state_token", None), field="state-token"),
        }
    if not body.get("code"):
        raise ValidationError("--verification-json must include code")
    if not body.get("stateToken"):
        raise ValidationError("--verification-json must include stateToken")
    return body


def _build_plan(*, method_name: str, request: dict[str, Any], selector: dict[str, Any], body: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "risk_level": "high",
        "risk_reasons": ["headless-email-verification", "may-complete-member-registration"],
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "apply requires --plan-in, --apply, and --yes",
            "code and stateToken must come from the current REQUIRE_EMAIL_VERIFICATION flow",
        ],
        "selector": selector,
        "request": _redact_sensitive(request),
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {
            "before_state_available": False,
            "notes": "Headless verification does not expose a stable before-state snapshot in this slice.",
        },
        "proposed_changes": [{"operation": "verify-during-authentication", "body": _redact_sensitive(body)}],
        "verification_plan": {
            "type": "provider-response",
            "notes": "Provider response confirms Wix accepted the verification request. If the returned state is SUCCESS, follow the Headless Authentication token flow to retrieve member tokens.",
        },
        "rollback": {"supported": False, "notes": "No automatic rollback. The verification step cannot be unsent or unverified by this CLI."},
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


def cmd_headless_verification_verify_during_authentication(args, ctx) -> int:
    method = "headlessVerification.verifyDuringAuthentication"
    try:
        body = _build_body(args)
        selector = {"kind": COMMAND_FAMILY, "operation": "verify-during-authentication"}
        request = {"method": "POST", "path": VERIFY_DURING_AUTHENTICATION_PATH, "body": body}
        auth = _resolve_auth(ctx)
        plan = _build_plan(method_name=method, request=request, selector=selector, body=body, ctx=ctx)
        if not reviewed_plan_apply_requested(ctx, requires_ack=False, command_label=method):
            out = {"ok": True, "dry_run": True, "method": method, "auth_mode": auth["mode"], "plan": plan, "redacted": True}
            if not ctx.get("apply") and ctx.get("plan_out"):
                out["plan_out"] = write_json_file(ctx["plan_out"], plan)
            ctx["audit"].write(f"{method}.plan", out)
            ctx["out"].emit(out)
            return 0
        loaded_plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method=method, expected_selector=selector, ctx=ctx)
        response = _request_json(path=VERIFY_DURING_AUTHENTICATION_PATH, headers=auth["headers"], json_body=body, ctx=ctx)
        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": method,
            "selector": selector,
            "request": _redact_sensitive(request),
            "response": _redact_sensitive(response),
            "changed": True,
            "verification": {
                "ok": True,
                "type": "provider-response",
                "notes": "Wix accepted the verification request. Member token retrieval is a separate Headless Authentication step.",
            },
            "diff_applied": loaded_plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
            "recovery": {"automatic": False, "notes": "Recovery is manual only."},
        }
        out = {"ok": True, "dry_run": False, "method": method, "auth_mode": auth["mode"], "receipt": receipt, "redacted": True}
        if ctx.get("receipt_out"):
            out["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
        ctx["audit"].write(f"{method}.apply", out)
        ctx["out"].emit(out)
        return 0
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
