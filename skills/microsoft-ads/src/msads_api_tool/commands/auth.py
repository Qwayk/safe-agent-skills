from __future__ import annotations

import json
from pathlib import Path

import requests

from ..errors import SafetyError, ValidationError
from ..oauth_tokens import get_token_status, read_token_json, token_path_for_env_file, write_token_dict, write_token_from_file
from ..oauth_tokens import redact_token_dict
from ..soap_client import MsAdsSoapClient


def cmd_auth_check(args, ctx) -> int:
    # Keep this command read-only and safe: it should only validate credentials.
    cfg = ctx["cfg"]
    tok_path = token_path_for_env_file(ctx["env_file"])
    status = get_token_status(tok_path)
    tok = read_token_json(tok_path) or {}
    access_present = bool(str(tok.get("access_token") or "").strip())
    refresh_present = bool(str(tok.get("refresh_token") or "").strip())

    live = bool(getattr(args, "live", False)) or bool(ctx.get("live"))

    out = {
        "ok": True,
        "environment": cfg.environment,
        "endpoints": cfg.endpoints,
        "developer_token_present": bool(cfg.developer_token),
        "customer_id_present": bool(cfg.customer_id),
        "customer_account_id_present": bool(cfg.customer_account_id),
        "oauth_token": {
            "exists": status.exists,
            "path": status.path,
            "access_token_present": access_present,
            "refresh_token_present": refresh_present,
        },
        "live_checked": False,
    }

    if live:
        client = MsAdsSoapClient(
            env_file=str(ctx["env_file"]),
            timeout_s=float(ctx["timeout_s"]),
            verbose=bool(ctx.get("verbose")),
            user_agent=f"msads-api-tool/{ctx['tool_version']}",
            endpoints=cfg.endpoints,
            developer_token=cfg.developer_token,
            customer_id=cfg.customer_id,
            customer_account_id=cfg.customer_account_id,
        )
        # Minimal read-like call: Customer Management GetUser
        result = client.call(service="customer-management", operation="GetUser", request_obj={})
        out["live_checked"] = True
        out["live_call"] = {
            "service": "customer-management",
            "operation": "GetUser",
            "ok": bool(result.ok),
            "status": result.status,
            "error": result.error,
        }
        if not result.ok:
            out["ok"] = False

    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_show(args, ctx) -> int:
    _ = args
    tok_path = token_path_for_env_file(ctx["env_file"])
    st = get_token_status(tok_path)
    tok = read_token_json(tok_path) or {}
    out = {"ok": True, "token_status": st.__dict__, "token": redact_token_dict(tok)}
    ctx["audit"].write("auth.token_show", {"token_status": st.__dict__})
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_refresh(args, ctx) -> int:
    _ = args
    if not bool(ctx.get("live")):
        raise SafetyError("Refusing to refresh tokens without --live")

    cfg = ctx["cfg"]
    if not cfg.oauth_client_id:
        raise ValidationError("Missing MSADS_OAUTH_CLIENT_ID (required for token refresh)")

    tok_path = token_path_for_env_file(ctx["env_file"])
    tok = read_token_json(tok_path) or {}
    refresh_token = str(tok.get("refresh_token") or "").strip()
    if not refresh_token:
        raise ValidationError("Missing refresh_token in token file (set token JSON via: msads-api-tool auth token set)")

    tenant = str(cfg.oauth_tenant or "").strip() or "common"
    token_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"

    form = {
        "client_id": cfg.oauth_client_id,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "scope": cfg.oauth_scope,
    }
    if cfg.oauth_client_secret:
        form["client_secret"] = cfg.oauth_client_secret

    resp = requests.post(token_url, data=form, timeout=float(ctx["timeout_s"]))
    text = resp.text or ""
    try:
        obj = json.loads(text) if text.strip() else {}
    except Exception:
        obj = {"raw_response": text[:4000]}

    if resp.status_code >= 400:
        out = {
            "ok": False,
            "token_refreshed": False,
            "http_status": resp.status_code,
            "error": obj.get("error") if isinstance(obj, dict) else None,
            "error_description": obj.get("error_description") if isinstance(obj, dict) else None,
        }
        ctx["audit"].write("auth.token_refresh.failed", {"http_status": resp.status_code})
        ctx["out"].emit(out)
        return 0

    if not isinstance(obj, dict):
        raise RuntimeError("Token endpoint response must be a JSON object")

    new_tok = dict(tok)
    for k in ("access_token", "refresh_token", "expires_in", "token_type", "scope", "id_token"):
        if k in obj:
            new_tok[k] = obj[k]

    if isinstance(obj.get("expires_in"), (int, float)):
        import time as _time

        new_tok["expires_at"] = int(_time.time() + float(obj["expires_in"]))

    st = write_token_dict(data=new_tok, dest_file=tok_path)
    out = {
        "ok": True,
        "token_refreshed": True,
        "token_status": st.__dict__,
        "token": redact_token_dict(new_tok),
        "token_url": token_url,
    }
    ctx["audit"].write("auth.token_refresh", {"token_status": st.__dict__})
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_set(args, ctx) -> int:
    dest = token_path_for_env_file(ctx["env_file"])
    st = write_token_from_file(src_file=Path(args.file), dest_file=dest)
    out = {"ok": True, "stored_to": st.path, "token_status": st.__dict__}
    ctx["audit"].write("auth.token_set", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_status(args, ctx) -> int:
    _ = args
    st = get_token_status(token_path_for_env_file(ctx["env_file"]))
    out = {"ok": True, "token_status": st.__dict__}
    ctx["audit"].write("auth.token_status", out)
    ctx["out"].emit(out)
    return 0
