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


COMMAND_FAMILY = "headless-authentication"
AUTH_BASE_PATH = "/_api/iam/authentication"
TOKEN_PATH = "/oauth2/token"
REDACTED = "[REDACTED]"


_SENSITIVE_KEYS = {
    "access_token",
    "accesstoken",
    "authorization",
    "code",
    "codeverifier",
    "newpassword",
    "oldpassword",
    "password",
    "refresh_token",
    "refreshtoken",
    "sessiontoken",
    "set-cookie",
}


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    value = str(raw).strip()
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
    if not payload and not allow_empty:
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


def _request_json(
    *,
    method: str,
    path: str,
    headers: dict[str, str] | None,
    json_body: dict[str, Any] | None,
    params: dict[str, Any] | None,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    request_headers = dict(headers or {})
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


def _build_plan(
    *,
    method_name: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    ctx: dict[str, Any],
    risk_reasons: list[str],
    verification_notes: str,
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
        "risk_level": "high",
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "selector": selector,
        "request": _redact_sensitive(request),
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {"before_state_available": False, "notes": "Headless Authentication actions do not expose a stable before-state snapshot in this slice."},
        "proposed_changes": _redact_sensitive(proposed_changes),
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Recovery depends on the affected member/session flow."},
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


def _run_sensitive_helper(
    *,
    method_name: str,
    http_method: str,
    path: str,
    body: dict[str, Any] | None,
    params: dict[str, Any] | None,
    auth_required: bool,
    ctx: dict[str, Any],
) -> int:
    auth = _resolve_auth(ctx) if auth_required else {"headers": {}, "mode": "oauth_client_request"}
    response = _request_json(method=http_method, path=path, headers=auth["headers"], json_body=body, params=params, ctx=ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    if params is not None:
        request["params"] = params
    out = {
        "ok": True,
        "method": method_name,
        "auth_mode": auth["mode"],
        "request": _redact_sensitive(request),
        "response": _redact_sensitive(response),
        "redacted": True,
    }
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _run_write(
    *,
    method_name: str,
    http_method: str,
    path: str,
    body: dict[str, Any] | None,
    params: dict[str, Any] | None,
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    ctx: dict[str, Any],
    risk_reasons: list[str],
    verification_notes: str,
    requires_ack: bool,
) -> int:
    auth = _resolve_auth(ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    if params is not None:
        request["params"] = params
    plan = _build_plan(
        method_name=method_name,
        request=request,
        selector=selector,
        proposed_changes=proposed_changes,
        ctx=ctx,
        risk_reasons=risk_reasons,
        verification_notes=verification_notes,
        requires_ack=requires_ack,
    )
    if not reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=method_name):
        out = {"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth["mode"], "plan": plan, "redacted": True}
        if not ctx.get("apply") and ctx.get("plan_out"):
            out["plan_out"] = write_json_file(ctx["plan_out"], plan)
        ctx["audit"].write(f"{method_name}.plan", out)
        ctx["out"].emit(out)
        return 0
    loaded_plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], json_body=body, params=params, ctx=ctx)
    receipt = {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "selector": selector,
        "request": _redact_sensitive(request),
        "response": _redact_sensitive(response),
        "changed": True,
        "verification": {"ok": True, "type": "provider-response", "notes": verification_notes},
        "diff_applied": loaded_plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {"automatic": False, "notes": "Recovery is manual only."},
    }
    out = {"ok": True, "dry_run": False, "method": method_name, "auth_mode": auth["mode"], "receipt": receipt, "redacted": True}
    if ctx.get("receipt_out"):
        out["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
    ctx["audit"].write(f"{method_name}.receipt", out)
    ctx["out"].emit(out)
    return 0


def cmd_headless_authentication_login_v2(args, ctx) -> int:
    method = "headlessAuthentication.loginV2"
    try:
        body = _read_json_arg(getattr(args, "login_json", None), field="login-json")
        return _run_sensitive_helper(
            method_name=method,
            http_method="POST",
            path=f"{AUTH_BASE_PATH}/v2/login",
            body=body,
            params=None,
            auth_required=True,
            ctx=ctx,
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_headless_authentication_retrieve_tokens(args, ctx) -> int:
    method = "headlessAuthentication.retrieveTokens"
    try:
        body = _read_json_arg(getattr(args, "token_json", None), field="token-json")
        if not body.get("clientId"):
            raise ValidationError("--token-json must include clientId")
        if not body.get("grantType"):
            raise ValidationError("--token-json must include grantType")
        return _run_sensitive_helper(
            method_name=method,
            http_method="POST",
            path=TOKEN_PATH,
            body=body,
            params=None,
            auth_required=False,
            ctx=ctx,
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_headless_authentication_register_v2(args, ctx) -> int:
    method = "headlessAuthentication.registerV2"
    try:
        body = _read_json_arg(getattr(args, "register_json", None), field="register-json")
        selector = {"kind": COMMAND_FAMILY, "operation": "register-v2"}
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{AUTH_BASE_PATH}/v2/register",
            body=body,
            params=None,
            selector=selector,
            proposed_changes=[{"operation": "register-member", "body": body}],
            ctx=ctx,
            risk_reasons=["wix-headless-member-registration", "may-create-member-or-require-email-verification"],
            verification_notes="Provider response confirms Wix accepted the registration request and may include a redacted session token.",
            requires_ack=False,
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_headless_authentication_change_password(args, ctx) -> int:
    method = "headlessAuthentication.changePassword"
    try:
        body = _read_json_arg(getattr(args, "password_json", None), field="password-json")
        selector = {"kind": COMMAND_FAMILY, "operation": "change-password"}
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{AUTH_BASE_PATH}/v2/change-password",
            body=body,
            params=None,
            selector=selector,
            proposed_changes=[{"operation": "change-member-password", "body": body}],
            ctx=ctx,
            risk_reasons=["wix-headless-password-change", "credential-change"],
            verification_notes="Provider response confirms Wix accepted the password change request.",
            requires_ack=True,
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_headless_authentication_logout(args, ctx) -> int:
    method = "headlessAuthentication.logout"
    try:
        params = _read_json_arg(getattr(args, "params_json", "{}") or "{}", field="params-json", allow_empty=True)
        selector = {"kind": COMMAND_FAMILY, "operation": "logout"}
        return _run_write(
            method_name=method,
            http_method="GET",
            path=f"{AUTH_BASE_PATH}/v1/logout",
            body=None,
            params=params,
            selector=selector,
            proposed_changes=[{"operation": "terminate-member-session", "params": params}],
            ctx=ctx,
            risk_reasons=["wix-headless-session-logout", "clears-member-authentication-cookies"],
            verification_notes="Provider response confirms Wix accepted the logout request and may return redacted cookie headers.",
            requires_ack=False,
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_headless_authentication_sign_on(args, ctx) -> int:
    method = "headlessAuthentication.signOn"
    try:
        body = _read_json_arg(getattr(args, "sign_on_json", None), field="sign-on-json")
        selector = {"kind": COMMAND_FAMILY, "operation": "sign-on"}
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{AUTH_BASE_PATH}/v2/sign-on",
            body=body,
            params=None,
            selector=selector,
            proposed_changes=[{"operation": "trusted-sign-on", "body": body}],
            ctx=ctx,
            risk_reasons=["wix-headless-trusted-sign-on", "may-create-or-update-member-account"],
            verification_notes="Provider response confirms Wix accepted the sign-on request and may include a redacted session token.",
            requires_ack=True,
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
