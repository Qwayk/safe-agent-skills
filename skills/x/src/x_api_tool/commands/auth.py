from __future__ import annotations

import base64
import hashlib
import json
import secrets
import time
import urllib.parse
from pathlib import Path
from typing import Any

from ..api_dispatch import openapi_snapshot_path
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import write_json_file
from ..oauth_tokens import (
    get_token_status,
    read_token_json,
    redact_token_dict,
    token_path_for_env_file,
    write_token_from_file,
)
from .write_safety import (
    before_state_refusal_verification_plan,
    blocked_before_state,
    ensure_blocked_apply_contract,
    refusal_output,
    rollback_contract,
)


def cmd_auth_check(args, ctx) -> int:
    cfg = ctx["cfg"]
    tok_path = token_path_for_env_file(ctx["env_file"])
    status = get_token_status(tok_path)
    include_local_paths = not bool(getattr(args, "no_provenance", False))
    out = {
        "ok": True,
        "base_url": cfg.base_url,
        "env_token_present": bool(cfg.token),
        "oauth_token": {"exists": status.exists, "path": (status.path if include_local_paths else None)},
        "live_allowed": bool(ctx.get("live")),
    }

    if bool(ctx.get("live")):
        tok = read_token_json(tok_path) if status.exists else None
        access_token = str((tok or {}).get("access_token") or "").strip()
        if not access_token:
            raise ValidationError(
                "Missing OAuth access token for live check. Current auth write helpers plan/require explicit no-snapshot approval before storing tokens."
            )
        url = cfg.base_url.rstrip("/") + "/users/me"
        client = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="x-api-tool")
        resp = client.request("GET", url, headers={"Authorization": f"Bearer {access_token}"})
        resp_keys: list[str] | None = None
        try:
            obj = resp.json()
            if isinstance(obj, dict):
                resp_keys = sorted([k for k in obj.keys() if isinstance(k, str)])
        except Exception:
            resp_keys = None
        out["live_check"] = {"attempted": True, "status": resp.status, "response_keys": resp_keys}
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0


def _build_auth_write_plan(
    *,
    ctx: dict[str, Any],
    command: str,
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    provider_write: dict[str, Any] | None = None,
    local_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "x-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command_id": command,
        "command": command,
        "selector": selector,
        "risk_level": "high",
        "risk_reasons": ["local-auth-state-write"],
        "preconditions": ["before-state for the local auth state exists before any write"],
        "baseline": {"env_fingerprint": str(ctx["cfg"].base_url)},
        "proposed_changes": proposed_changes,
        "before_state": blocked_before_state(
            action=command,
            proposed_changes=proposed_changes,
            provider_write=provider_write,
            local_state=local_state,
        ),
        "verification_plan": before_state_refusal_verification_plan(),
        "rollback": rollback_contract(),
        "dry_run": True,
    }


def _emit_auth_write_plan_or_refusal(*, ctx: dict[str, Any], plan: dict[str, Any], command: str) -> int:
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if plan_out and not bool(ctx.get("apply")) else None
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path, "command": command}
        ctx["audit"].write(f"{command}.plan", {"plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError(f"Refused: {command} requires --apply --yes")
    plan = ensure_blocked_apply_contract(
        plan,
        action=command,
        proposed_changes=plan.get("proposed_changes") if isinstance(plan.get("proposed_changes"), list) else [],
        local_state=plan.get("before_state", {}).get("local_state") if isinstance(plan.get("before_state"), dict) else None,
    )
    if not bool(ctx.get("ack_no_snapshot")):
        out = refusal_output(plan=plan)
        out["command"] = command
        ctx["audit"].write(f"{command}.refused", {"reasons": out["reasons"]})
        ctx["out"].emit(out)
        return 0

    return _apply_auth_write(ctx=ctx, plan=plan, command=command)


def _auth_receipt(ctx: dict[str, Any], *, command: str, plan: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "x-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command_id": command,
        "selector": plan.get("selector"),
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": "No reliable before-state snapshot is available for this X auth local-state write.",
        },
        "changed": True,
        "result": result,
        "verification": {"ok": True, "mode": "local-state-status"},
        "rollback": plan.get("rollback"),
    }


def _emit_auth_receipt(ctx: dict[str, Any], *, command: str, plan: dict[str, Any], result: dict[str, Any]) -> int:
    receipt = _auth_receipt(ctx, command=command, plan=plan, result=result)
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "command": command, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(f"{command}.apply", {"receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def _apply_auth_write(*, ctx: dict[str, Any], plan: dict[str, Any], command: str) -> int:
    if command == "auth.token_set":
        proposed = plan.get("proposed_changes") if isinstance(plan.get("proposed_changes"), list) else []
        source_file = ""
        if proposed and isinstance(proposed[0], dict):
            source_file = str(proposed[0].get("source_file") or "")
        status = write_token_from_file(src_file=Path(source_file), dest_file=token_path_for_env_file(ctx["env_file"]))
        result = {"token_status": status.__dict__}
        return _emit_auth_receipt(ctx, command=command, plan=plan, result=result)

    if command == "auth.pkce_start":
        result = _write_pkce_state(ctx=ctx)
        return _emit_auth_receipt(ctx, command=command, plan=plan, result=result)

    if command == "auth.pkce_finish":
        result = _exchange_pkce_token(ctx=ctx, plan=plan)
        return _emit_auth_receipt(ctx, command=command, plan=plan, result=result)

    out = refusal_output(plan=plan, reason=f"Refused: {command} has no implemented live executor.")
    out["command"] = command
    ctx["audit"].write(f"{command}.refused", {"reasons": out["reasons"]})
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_set(args, ctx) -> int:
    dest = token_path_for_env_file(ctx["env_file"])
    plan = _build_auth_write_plan(
        ctx=ctx,
        command="auth.token_set",
        selector={"kind": "auth.token", "target": ".state/token.json"},
        proposed_changes=[{"action": "store_token_file", "source_file": str(Path(args.file)), "dest_file": str(dest)}],
        local_state={"kind": "oauth_token_store", "path": str(dest), "writes_token_file": True},
    )
    return _emit_auth_write_plan_or_refusal(ctx=ctx, plan=plan, command="auth.token_set")


def cmd_auth_token_status(args, ctx) -> int:
    _ = args
    st = get_token_status(token_path_for_env_file(ctx["env_file"]))
    out = {"ok": True, "token_status": st.__dict__}
    ctx["audit"].write("auth.token_status", out)
    ctx["out"].emit(out)
    return 0


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _pkce_state_path(env_file: str) -> Path:
    root = Path(env_file).resolve().parent
    return root / ".state" / "pkce.json"


def _load_oauth2_endpoints_from_snapshot() -> tuple[str, str] | None:
    snap = openapi_snapshot_path()
    if not snap.exists():
        return None
    obj = json.loads(snap.read_text(encoding="utf-8"))
    schemes = (obj.get("components") or {}).get("securitySchemes") or {}
    for v in schemes.values():
        if not isinstance(v, dict) or v.get("type") != "oauth2":
            continue
        flows = v.get("flows") or {}
        ac = flows.get("authorizationCode") if isinstance(flows, dict) else None
        if not isinstance(ac, dict):
            continue
        auth_url = str(ac.get("authorizationUrl") or "").strip()
        token_url = str(ac.get("tokenUrl") or "").strip()
        if auth_url and token_url:
            return auth_url, token_url
    return None


def cmd_auth_pkce_start(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    cfg = ctx["cfg"]
    if not cfg.oauth2_client_id or not cfg.oauth2_redirect_uri:
        raise ValidationError("Missing OAuth2 config: set X_API_OAUTH2_CLIENT_ID and X_API_OAUTH2_REDIRECT_URI")
    scopes = (cfg.oauth2_scopes or "").strip()
    if not scopes:
        raise ValidationError("Missing OAuth2 scopes: set X_API_OAUTH2_SCOPES (space-separated)")

    endpoints = _load_oauth2_endpoints_from_snapshot()
    auth_url_default, token_url_default = endpoints if endpoints else ("", "")
    auth_url = (cfg.oauth2_authorization_url or auth_url_default).strip()
    token_url = (cfg.oauth2_token_url or token_url_default).strip()
    if not auth_url or not token_url:
        raise ValidationError("Missing OAuth2 endpoints (auth/token URL). Set X_API_OAUTH2_AUTH_URL and X_API_OAUTH2_TOKEN_URL.")

    st_path = _pkce_state_path(ctx["env_file"])
    plan = _build_auth_write_plan(
        ctx=ctx,
        command="auth.pkce_start",
        selector={"kind": "auth.pkce", "target": ".state/pkce.json"},
        proposed_changes=[
            {
                "action": "create_pkce_state",
                "authorization_url": auth_url,
                "token_url": token_url,
                "redirect_uri": cfg.oauth2_redirect_uri,
                "scopes": scopes,
            }
        ],
        local_state={"kind": "pkce_state_store", "path": str(st_path), "writes_pkce_file": True},
    )
    return _emit_auth_write_plan_or_refusal(ctx=ctx, plan=plan, command="auth.pkce_start")


def _write_pkce_state(*, ctx: dict[str, Any]) -> dict[str, Any]:
    cfg = ctx["cfg"]
    endpoints = _load_oauth2_endpoints_from_snapshot()
    auth_url_default, token_url_default = endpoints if endpoints else ("", "")
    auth_url = (cfg.oauth2_authorization_url or auth_url_default).strip()
    token_url = (cfg.oauth2_token_url or token_url_default).strip()
    if not cfg.oauth2_client_id or not cfg.oauth2_redirect_uri:
        raise ValidationError("Missing OAuth2 config: set X_API_OAUTH2_CLIENT_ID and X_API_OAUTH2_REDIRECT_URI")
    if not auth_url or not token_url:
        raise ValidationError("Missing OAuth2 endpoints (auth/token URL). Set X_API_OAUTH2_AUTH_URL and X_API_OAUTH2_TOKEN_URL.")

    verifier = _b64url(secrets.token_bytes(32))
    challenge = _b64url(hashlib.sha256(verifier.encode("ascii")).digest())
    state = _b64url(secrets.token_bytes(18))
    scope = (cfg.oauth2_scopes or "").strip()
    params = {
        "response_type": "code",
        "client_id": cfg.oauth2_client_id,
        "redirect_uri": cfg.oauth2_redirect_uri,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    if scope:
        params["scope"] = scope
    authorize_url = auth_url + ("&" if "?" in auth_url else "?") + urllib.parse.urlencode(params)
    st_path = _pkce_state_path(ctx["env_file"])
    st_path.parent.mkdir(parents=True, exist_ok=True)
    st_path.write_text(
        json.dumps(
            {
                "created_at_utc": _utc_now(),
                "state": state,
                "code_verifier": verifier,
                "authorization_url": auth_url,
                "token_url": token_url,
                "client_id": cfg.oauth2_client_id,
                "redirect_uri": cfg.oauth2_redirect_uri,
                "scope": scope,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"pkce_state_path": str(st_path), "authorization_url": authorize_url, "state": state}


def _parse_redirect_url(redirect_url: str) -> tuple[str | None, str | None, str | None]:
    try:
        parsed = urllib.parse.urlsplit(redirect_url)
        qs = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
        return qs.get("code"), qs.get("state"), qs.get("error")
    except Exception:
        return None, None, None


def cmd_auth_pkce_finish(args: Any, ctx: dict[str, Any]) -> int:
    redirect_url = str(getattr(args, "redirect_url", "") or "").strip()
    code = str(getattr(args, "code", "") or "").strip()
    state = str(getattr(args, "state", "") or "").strip()

    if redirect_url:
        code2, state2, err = _parse_redirect_url(redirect_url)
        if err:
            raise ValidationError(f"OAuth2 redirect returned error: {err}")
        code = code or (code2 or "")
        state = state or (state2 or "")

    if not code:
        raise ValidationError("Missing authorization code. Provide --redirect-url or --code.")
    ctx["_pkce_finish_code"] = code
    ctx["_pkce_finish_state"] = state

    st_path = _pkce_state_path(ctx["env_file"])
    dest = token_path_for_env_file(ctx["env_file"])
    plan = _build_auth_write_plan(
        ctx=ctx,
        command="auth.pkce_finish",
        selector={"kind": "auth.pkce", "source": ".state/pkce.json", "target": ".state/token.json"},
        proposed_changes=[{"action": "exchange_authorization_code", "code": "***REDACTED***", "state_present": bool(state)}],
        provider_write={"service": "X OAuth2", "action": "token_exchange", "method": "POST"},
        local_state={
            "kind": "oauth_token_store",
            "pkce_state_path": str(st_path),
            "token_path": str(dest),
            "writes_token_file": True,
        },
    )
    return _emit_auth_write_plan_or_refusal(ctx=ctx, plan=plan, command="auth.pkce_finish")


def _exchange_pkce_token(*, ctx: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    st_path = _pkce_state_path(ctx["env_file"])
    if not st_path.exists():
        raise SafetyError("Refused: missing PKCE state file. Run auth pkce start first.")
    st = json.loads(st_path.read_text(encoding="utf-8"))
    if not isinstance(st, dict):
        raise ValidationError("PKCE state file must be a JSON object")

    expected_state = str(st.get("state") or "")
    token_url = str(st.get("token_url") or "")
    client_id = str(st.get("client_id") or "")
    redirect_uri = str(st.get("redirect_uri") or "")
    code_verifier = str(st.get("code_verifier") or "")
    if not token_url or not client_id or not redirect_uri or not code_verifier:
        raise ValidationError("PKCE state file is missing token exchange fields")

    code = str(ctx.get("_pkce_finish_code") or "")
    supplied_state = str(ctx.get("_pkce_finish_state") or "")
    if not code:
        raise ValidationError("Missing authorization code. Use --code for approved apply.")
    if supplied_state and expected_state and supplied_state != expected_state:
        raise SafetyError("Refused: supplied OAuth state does not match the saved PKCE state")

    client = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="x-api-tool")
    resp = client.request(
        "POST",
        token_url,
        headers={"Accept": "application/json"},
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "code": code,
            "code_verifier": code_verifier,
        },
    )
    data = resp.json()
    if not isinstance(data, dict):
        raise RuntimeError("Token response must be a JSON object")
    dest = token_path_for_env_file(ctx["env_file"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    status = get_token_status(dest)
    return {"token_status": status.__dict__, "token": redact_token_dict(data), "status": resp.status}
