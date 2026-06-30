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


COMMAND_FAMILY = "headless-oauth-apps"
BASE_PATH = "/oauth-app/v1/oauth-apps"


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


def _oauth_app_body(raw: Any, *, require_id: bool = False, require_mask: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = _read_json_arg(raw, field="o-auth-app-json")
    body = dict(payload) if "oAuthApp" in payload else {"oAuthApp": payload}
    oauth_app = body.get("oAuthApp")
    if not isinstance(oauth_app, dict) or not oauth_app:
        raise ValidationError("--o-auth-app-json must include a non-empty oAuthApp object")
    if require_id:
        _coerce_text(oauth_app.get("id"), field="o-auth-app-json oAuthApp.id")
    if require_mask:
        mask = body.get("mask")
        if not isinstance(mask, dict) or not isinstance(mask.get("paths"), list) or not mask.get("paths"):
            raise ValidationError("--o-auth-app-json must include mask.paths for update")
    return body, oauth_app


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
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": method})
        return 0
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _run_read(*, method_name: str, http_method: str, path: str, body: dict[str, Any] | None, ctx: dict[str, Any]) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], json_body=body, ctx=ctx)
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
    risk_reasons: list[str],
    verification_notes: str,
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "risk_level": "medium",
        "risk_reasons": risk_reasons,
        "preconditions": ["env_fingerprint must match", "selector must match", "apply requires --plan-in, --apply, and --yes"],
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {"before_state_available": False, "notes": "Headless OAuth Apps plans do not capture a full before-state snapshot in this slice."},
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response-plus-readback", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Update the OAuth app again or adjust it in the Wix dashboard if needed."},
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
    risk_reasons: list[str],
    verification_notes: str,
) -> int:
    auth = _resolve_auth(ctx)
    request = {"method": http_method, "path": path, "body": body}
    plan = _build_plan(
        method_name=method_name,
        request=request,
        selector=selector,
        proposed_changes=proposed_changes,
        ctx=ctx,
        risk_reasons=risk_reasons,
        verification_notes=verification_notes,
    )
    if not reviewed_plan_apply_requested(ctx, requires_ack=False, command_label=method_name):
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
        "verification": {"ok": True, "type": "provider-response-plus-readback", "notes": verification_notes},
        "diff_applied": loaded_plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {"automatic": False, "notes": "Recovery is manual only."},
    }
    out = {"ok": True, "dry_run": False, "method": method_name, "auth_mode": auth["mode"], "receipt": receipt}
    if ctx.get("receipt_out"):
        out["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
    ctx["audit"].write(f"{method_name}.receipt", out)
    ctx["out"].emit(out)
    return 0


def cmd_headless_oauth_apps_create(args, ctx) -> int:
    method = "headlessOauthApps.createOAuthApp"
    try:
        body, oauth_app = _oauth_app_body(args.o_auth_app_json)
        return _run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"operation": "create-headless-oauth-app", "name": oauth_app.get("name")},
            proposed_changes=[{"operation": "create-headless-oauth-app", "oAuthApp": oauth_app}],
            ctx=ctx,
            risk_reasons=["wix-headless-oauth-app-create", "external-client-auth-access"],
            verification_notes="Inspect the provider response, then use headless-oauth-apps get or query to verify the OAuth app.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_headless_oauth_apps_get(args, ctx) -> int:
    method = "headlessOauthApps.getOAuthApp"
    try:
        oauth_app_id = _coerce_text(args.o_auth_app_id, field="o-auth-app-id")
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/{oauth_app_id}", body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_headless_oauth_apps_update(args, ctx) -> int:
    method = "headlessOauthApps.updateOAuthApp"
    try:
        body, oauth_app = _oauth_app_body(args.o_auth_app_json, require_id=True, require_mask=True)
        oauth_app_id = _coerce_text(oauth_app.get("id"), field="o-auth-app-json oAuthApp.id")
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{oauth_app_id}",
            body=body,
            selector={"oAuthAppId": oauth_app_id, "mask": body.get("mask")},
            proposed_changes=[{"operation": "update-headless-oauth-app", "oAuthApp": oauth_app, "mask": body.get("mask")}],
            ctx=ctx,
            risk_reasons=["wix-headless-oauth-app-update", "external-client-auth-settings-change"],
            verification_notes="Inspect the provider response, then use headless-oauth-apps get to verify the OAuth app.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_headless_oauth_apps_query(args, ctx) -> int:
    method = "headlessOauthApps.queryOAuthApps"
    try:
        body = _read_json_arg(args.query_json or "{}", field="query-json", allow_empty=True)
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/query", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
