from __future__ import annotations

from pathlib import Path

from ..auth_runtime import (
    build_authorize_url,
    exchange_authorization_code,
    get_me,
    refresh_access_token,
    request_service_account_access_token,
    resolve_access_token,
)
from ..oauth_tokens import get_token_status, token_path_for_env_file, write_token_from_file


def _scopes_from_args(args, cfg) -> tuple[str, ...]:
    raw = getattr(args, "scope", None)
    if not raw:
        return tuple(cfg.oauth_scopes)
    if isinstance(raw, str):
        items = [raw]
    else:
        items = list(raw)
    scopes: list[str] = []
    for item in items:
        for part in str(item).replace(",", " ").split():
            cleaned = part.strip()
            if cleaned:
                scopes.append(cleaned)
    return tuple(scopes) or tuple(cfg.oauth_scopes)


def cmd_auth_check(args, ctx) -> int:
    cfg = ctx["cfg"]
    skip_live = bool(getattr(args, "skip_live", False))
    resolved = resolve_access_token(cfg=cfg, env_file=ctx["env_file"])
    status = get_token_status(token_path_for_env_file(ctx["env_file"], cfg.token_file))

    probe: dict[str, object] = {
        "attempted": False,
        "ok": None,
        "status": None,
        "reason": None,
        "path": "/me",
    }
    overall_ok = True

    if skip_live:
        probe["reason"] = "skipped by --skip-live"
        overall_ok = bool(resolved.token)
        if not resolved.token:
            probe["ok"] = False
            probe["status"] = "blocked"
            probe["reason"] = "no access token available in env or token file"
    elif not resolved.token:
        probe["ok"] = False
        probe["status"] = "blocked"
        probe["reason"] = "no access token available in env or token file"
        overall_ok = False
    elif resolved.expired is True and resolved.source == "token_file":
        probe["ok"] = False
        probe["status"] = "blocked"
        probe["reason"] = "token file access token looks expired; run `auth refresh` or `auth service-account-token` first"
        overall_ok = False
    else:
        probe["attempted"] = True
        try:
            body = get_me(
                cfg=cfg,
                access_token=resolved.token,
                timeout_s=float(ctx["timeout_s"]),
                verbose=bool(ctx.get("verbose")),
                user_agent=f"{ctx['tool']}/{ctx['tool_version']}",
            )
            probe["ok"] = True
            probe["status"] = 200
            probe["response_keys"] = sorted(str(key) for key in body.keys())
        except Exception as e:  # noqa: BLE001
            probe["ok"] = False
            probe["status"] = "blocked"
            probe["reason"] = str(e)
            overall_ok = False

    out = {
        "ok": overall_ok,
        "base_url": cfg.base_url,
        "ws_url": cfg.ws_url,
        "client_id_present": bool(cfg.client_id),
        "client_secret_present": bool(cfg.client_secret),
        "redirect_uri_present": bool(cfg.redirect_uri),
        "service_tenant_id_present": bool(cfg.service_tenant_id),
        "oauth_scopes": list(cfg.oauth_scopes),
        "token_source": resolved.source,
        "token_present": bool(resolved.token),
        "token_expired": resolved.expired,
        "token_status": status.__dict__,
        "live_probe": probe,
    }
    ctx["audit"].write(
        "auth.check",
        {
            "ok": overall_ok,
            "token_source": resolved.source,
            "token_present": bool(resolved.token),
            "token_expired": resolved.expired,
            "live_probe": probe,
        },
    )
    ctx["out"].emit(out)
    return 0 if overall_ok else 1


def cmd_auth_login(args, ctx) -> int:
    cfg = ctx["cfg"]
    scopes = _scopes_from_args(args, cfg)
    payload = build_authorize_url(
        cfg=cfg,
        env_file=ctx["env_file"],
        scopes=scopes,
        service_account=bool(getattr(args, "service_account", False)),
        state=str(getattr(args, "state", "") or "").strip() or None,
    )
    out = {
        "ok": True,
        "authorize_url": payload["authorize_url"],
        "state": payload["state"],
        "state_file": payload["state_file"],
        "redirect_uri": payload["redirect_uri"],
        "scope": payload["scope"],
        "service_account": payload["service_account"],
        "next_step": "After approval, run `fortnox-api-tool auth exchange-code --code <code> --state <state>`.",
    }
    ctx["audit"].write(
        "auth.login",
        {
            "ok": True,
            "state_file": payload["state_file"],
            "scope": payload["scope"],
            "service_account": payload["service_account"],
        },
    )
    ctx["out"].emit(out)
    return 0


def cmd_auth_exchange_code(args, ctx) -> int:
    cfg = ctx["cfg"]
    payload = exchange_authorization_code(
        cfg=cfg,
        env_file=ctx["env_file"],
        code=str(getattr(args, "code", "") or ""),
        state=str(getattr(args, "state", "") or "").strip() or None,
        timeout_s=float(ctx["timeout_s"]),
    )
    out = {
        "ok": True,
        "token_exchanged": True,
        "stored_to": payload["stored_to"],
        "token_status": payload["token_status"],
        "token": payload["token"],
    }
    ctx["audit"].write(
        "auth.exchange_code",
        {"ok": True, "stored_to": payload["stored_to"], "token_status": payload["token_status"]},
    )
    ctx["out"].emit(out)
    return 0


def cmd_auth_refresh(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    payload = refresh_access_token(cfg=cfg, env_file=ctx["env_file"], timeout_s=float(ctx["timeout_s"]))
    out = {
        "ok": True,
        "token_refreshed": True,
        "stored_to": payload["stored_to"],
        "token_status": payload["token_status"],
        "token": payload["token"],
    }
    ctx["audit"].write(
        "auth.refresh",
        {"ok": True, "stored_to": payload["stored_to"], "token_status": payload["token_status"]},
    )
    ctx["out"].emit(out)
    return 0


def cmd_auth_service_account_token(args, ctx) -> int:
    cfg = ctx["cfg"]
    scopes = _scopes_from_args(args, cfg)
    payload = request_service_account_access_token(
        cfg=cfg,
        env_file=ctx["env_file"],
        scopes=scopes,
        timeout_s=float(ctx["timeout_s"]),
    )
    out = {
        "ok": True,
        "service_account_token_fetched": True,
        "stored_to": payload["stored_to"],
        "tenant_id": payload["tenant_id"],
        "scope": payload["scope"],
        "token_status": payload["token_status"],
        "token": payload["token"],
    }
    ctx["audit"].write(
        "auth.service_account_token",
        {
            "ok": True,
            "stored_to": payload["stored_to"],
            "tenant_id": payload["tenant_id"],
            "scope": payload["scope"],
            "token_status": payload["token_status"],
        },
    )
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_set(args, ctx) -> int:
    cfg = ctx["cfg"]
    dest = token_path_for_env_file(ctx["env_file"], cfg.token_file)
    st = write_token_from_file(src_file=Path(args.file), dest_file=dest)
    out = {"ok": True, "stored_to": st.path, "token_status": st.__dict__}
    ctx["audit"].write("auth.token_set", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_status(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    st = get_token_status(token_path_for_env_file(ctx["env_file"], cfg.token_file))
    out = {"ok": True, "token_status": st.__dict__}
    ctx["audit"].write("auth.token_status", out)
    ctx["out"].emit(out)
    return 0
