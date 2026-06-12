from __future__ import annotations

import urllib.parse
from pathlib import Path

from ..errors import ValidationError
from ..http import GraphQLClient, HttpClient
from ..oauth_tokens import (
    get_token_status,
    read_token_json,
    write_token_payload,
    token_path_for_env_file,
    write_token_from_file,
)
from ..json_files import write_json_file


def _token_endpoint(base_url: str) -> str:
    base = str(base_url or "").rstrip("/")
    if not base:
        base = "https://api.getjobber.com"
    if base.endswith("/api/graphql"):
        return base[: -len("/api/graphql")] + "/api/oauth/token"
    if base.endswith("/api"):
        return base + "/oauth/token"
    return base + "/api/oauth/token"


def _authorize_endpoint(base_url: str) -> str:
    base = str(base_url or "").rstrip("/")
    if not base:
        base = "https://api.getjobber.com"
    if base.endswith("/api/graphql"):
        return base[: -len("/api/graphql")] + "/api/oauth/authorize"
    if base.endswith("/api"):
        return base + "/oauth/authorize"
    return base + "/api/oauth/authorize"


def _require_arg(value: str, *, label: str) -> str:
    out = str(value or "").strip()
    if not out:
        raise ValidationError(f"Missing required setting: {label}")
    return out


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    if not cfg.token:
        out = {
            "ok": True,
            "command": "auth.check",
            "token_available": False,
            "missing_token": True,
            "message": "Set JOBBER_API_TOKEN or store a token in .state/token.json",
        }
        ctx["audit"].write("auth.check", out)
        ctx["out"].emit(out)
        return 0

    token_status = get_token_status(token_path_for_env_file(ctx["env_file"]))
    client = GraphQLClient(
        endpoint=cfg.graphql_url,
        token=cfg.token,
        graphql_version=cfg.graphql_version,
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
    )
    result = client.execute("query { account { __typename } }", variables=None)
    out = {
        "ok": True,
        "command": "auth.check",
        "token_available": True,
        "base_url": cfg.base_url,
        "graphql_url": cfg.graphql_url,
        "token_store": {
            "exists": token_status.exists,
            "path": token_status.path,
            "updated_at_utc": token_status.updated_at_utc,
            "fields": token_status.fields,
        },
        "account_probe": result.get("data", {}),
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_authorize_url(args, ctx) -> int:
    cfg = ctx["cfg"]
    client_id = _require_arg(cfg.client_id, label="JOBBER_CLIENT_ID")
    redirect_uri = str(getattr(cfg, "redirect_uri", "") or "").strip()
    scope = str(getattr(args, "scope", "") or "").strip()
    state = str(getattr(args, "state", "") or "").strip()

    params = {
        "client_id": client_id,
        "response_type": "code",
    }
    if scope:
        params["scope"] = scope
    if redirect_uri:
        params["redirect_uri"] = redirect_uri
    if state:
        params["state"] = state

    out = {
        "ok": True,
        "command": "auth.authorize_url",
        "authorize_url": _authorize_endpoint(cfg.base_url) + "?" + urllib.parse.urlencode(params, doseq=True),
    }
    ctx["audit"].write("auth.authorize_url", out)
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


def cmd_auth_token_refresh(args, ctx) -> int:
    cfg = ctx["cfg"]
    _require_arg(cfg.client_id, label="JOBBER_CLIENT_ID")
    secret = _require_arg(cfg.client_secret, label="JOBBER_CLIENT_SECRET")

    if not bool(ctx.get("apply")):
        out = {
            "ok": True,
            "dry_run": True,
            "command": "auth.token_refresh",
            "plan": {
                "command": "auth.token_refresh",
                "mutation": "oauth/token",
                "risk": "high",
                "arguments_summary": {"has_refresh_token": bool(getattr(args, "refresh_token", None))},
                "verification_plan": {"type": "auth.check"},
            },
        }
        if ctx.get("plan_out"):
            out["plan_out"] = write_json_file(ctx["plan_out"], out["plan"])
        ctx["audit"].write("auth.token_refresh.plan", out)
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "command": "auth.token_refresh",
            "reasons": ["Refused: auth token refresh requires --apply --yes"],
            "refusal_type": "SafetyError",
        }
        ctx["audit"].write("auth.token_refresh.refused", out)
        ctx["out"].emit(out)
        return 0

    refresh_token = str(getattr(args, "refresh_token", "") or "").strip()
    if not refresh_token:
        token_file = token_path_for_env_file(ctx["env_file"])
        data = read_token_json(token_file) or {}
        if isinstance(data, dict):
            refresh_token = str(data.get("refresh_token") or "").strip()
        if not refresh_token:
            raise ValidationError("Missing refresh token (pass --refresh-token or store token JSON with refresh_token)")

    http = HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"], user_agent="qwayk-jobber-safe-agent-cli")
    payload = {
        "client_id": cfg.client_id,
        "client_secret": secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    response = http.request(
        method="POST",
        url=_token_endpoint(cfg.base_url),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=payload,
    )

    try:
        body = response.json()
    except Exception as e:
        raise ValidationError(f"Token endpoint response parse error: {type(e).__name__}") from None
    if not isinstance(body, dict):
        raise ValidationError("Token endpoint response must be a JSON object")

    write_token_payload(payload=body, dest_file=token_path_for_env_file(ctx["env_file"]))
    # Never emit raw token data.
    redacted = {"ok": True, "dry_run": False, "command": "auth.token_refresh"}
    redacted["received"] = {
        "has_access_token": bool(body.get("access_token")),
        "has_refresh_token": bool(body.get("refresh_token")),
        "expires_in": body.get("expires_in"),
    }
    if ctx.get("receipt_out"):
        redacted["receipt_out"] = str(ctx["receipt_out"])
        write_json_file(ctx["receipt_out"], redacted)
    ctx["audit"].write("auth.token_refresh", redacted)
    ctx["out"].emit(redacted)
    return 0
