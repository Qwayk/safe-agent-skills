from __future__ import annotations

from pathlib import Path
from typing import Any

from ..http import HttpClient
from ..oauth_tokens import get_token_status, token_path_for_env_file, write_token_from_file
from ..session_store import (
    access_token_from_session,
    clear_session_json,
    pds_url_from_session,
    read_session_json,
    refresh_token_from_session,
    write_session_json,
)


def _client(ctx: dict[str, Any]) -> HttpClient:
    return HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"linux:{ctx.get('tool') or 'bluesky-safe-cli'}:v{ctx.get('tool_version') or '0.1.0'}",
    )


def _create_session(cfg: Any, ctx: dict[str, Any], *, persist: bool) -> dict[str, Any]:
    if not cfg.identifier:
        raise RuntimeError("Missing BLUESKY_IDENTIFIER")
    if not cfg.app_password:
        raise RuntimeError("Missing BLUESKY_APP_PASSWORD")

    client = _client(ctx)
    response = client.request(
        "POST",
        cfg.entryway_url.rstrip("/") + "/xrpc/com.atproto.server.createSession",
        headers={"Accept": "application/json"},
        json_body={"identifier": cfg.identifier, "password": cfg.app_password},
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("Session response must be a JSON object")
    if persist:
        write_session_json(ctx["env_file"], payload)
    return payload


def _refresh_session(cfg: Any, ctx: dict[str, Any], *, persist: bool) -> dict[str, Any]:
    saved = read_session_json(ctx["env_file"])
    refresh_token = cfg.refresh_jwt or refresh_token_from_session(saved)
    if not refresh_token:
        raise RuntimeError("Missing refresh JWT. Run `bluesky-safe-cli auth login` first.")
    base_url = pds_url_from_session(saved) or cfg.default_pds_url or cfg.entryway_url
    client = _client(ctx)
    response = client.request(
        "POST",
        base_url.rstrip("/") + "/xrpc/com.atproto.server.refreshSession",
        headers={"Authorization": f"Bearer {refresh_token}", "Accept": "application/json"},
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("Refresh response must be a JSON object")
    if persist:
        write_session_json(ctx["env_file"], payload)
    return payload


def _current_session(cfg: Any, ctx: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    saved = read_session_json(ctx["env_file"])
    access_token = cfg.access_jwt or access_token_from_session(saved)
    if access_token:
        base_url = pds_url_from_session(saved) or cfg.default_pds_url or cfg.entryway_url
        client = _client(ctx)
        response = client.request(
            "GET",
            base_url.rstrip("/") + "/xrpc/com.atproto.server.getSession",
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
        )
        payload = response.json()
        if not isinstance(payload, dict):
            raise RuntimeError("Session check response must be a JSON object")
        return payload, base_url.rstrip("/")
    if cfg.identifier and cfg.app_password:
        payload = _create_session(cfg, ctx, persist=False)
        return payload, pds_url_from_session(payload) or cfg.default_pds_url or cfg.entryway_url
    if cfg.refresh_jwt or refresh_token_from_session(saved):
        payload = _refresh_session(cfg, ctx, persist=False)
        return payload, pds_url_from_session(payload) or cfg.default_pds_url or cfg.entryway_url
    return None, None


def cmd_auth_check(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    cfg = ctx["cfg"]
    tok_path = token_path_for_env_file(ctx["env_file"])
    status = get_token_status(tok_path)
    session, session_base_url = _current_session(cfg, ctx)
    out: dict[str, Any] = {
        "ok": True,
        "entryway_url": cfg.entryway_url,
        "default_pds_url": cfg.default_pds_url,
        "identifier_present": bool(cfg.identifier),
        "app_password_present": bool(cfg.app_password),
        "access_jwt_present": bool(cfg.access_jwt),
        "refresh_jwt_present": bool(cfg.refresh_jwt),
        "admin_token_present": bool(cfg.admin_token),
        "oauth_token": {"exists": status.exists, "path": status.path},
        "live_checked": bool(session),
        "session_base_url": session_base_url,
    }
    if isinstance(session, dict):
        out["did"] = session.get("did")
        out["handle"] = session.get("handle")
        out["active"] = session.get("active")
        out["status"] = session.get("status")
        out["resolved_pds_url"] = pds_url_from_session(session)
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_login(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    payload = _create_session(ctx["cfg"], ctx, persist=True)
    status = get_token_status(token_path_for_env_file(ctx["env_file"]))
    out = {
        "ok": True,
        "stored_to": status.path,
        "token_status": status.__dict__,
        "did": payload.get("did"),
        "handle": payload.get("handle"),
        "resolved_pds_url": pds_url_from_session(payload),
    }
    ctx["audit"].write("auth.login", {"stored_to": status.path, "did": payload.get("did"), "handle": payload.get("handle")})
    ctx["out"].emit(out)
    return 0


def cmd_auth_refresh(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    payload = _refresh_session(ctx["cfg"], ctx, persist=True)
    status = get_token_status(token_path_for_env_file(ctx["env_file"]))
    out = {
        "ok": True,
        "stored_to": status.path,
        "token_status": status.__dict__,
        "did": payload.get("did"),
        "handle": payload.get("handle"),
        "resolved_pds_url": pds_url_from_session(payload),
    }
    ctx["audit"].write("auth.refresh", {"stored_to": status.path, "did": payload.get("did"), "handle": payload.get("handle")})
    ctx["out"].emit(out)
    return 0


def cmd_auth_logout(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    result = clear_session_json(ctx["env_file"])
    out = {"ok": True, "logout": result}
    ctx["audit"].write("auth.logout", result)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_set(args: Any, ctx: dict[str, Any]) -> int:
    dest = token_path_for_env_file(ctx["env_file"])
    st = write_token_from_file(src_file=Path(args.file), dest_file=dest)
    out = {"ok": True, "stored_to": st.path, "token_status": st.__dict__}
    ctx["audit"].write("auth.token_set", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_status(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    st = get_token_status(token_path_for_env_file(ctx["env_file"]))
    out = {"ok": True, "token_status": st.__dict__}
    ctx["audit"].write("auth.token_status", out)
    ctx["out"].emit(out)
    return 0
