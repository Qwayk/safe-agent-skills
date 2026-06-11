from __future__ import annotations

from pathlib import Path

from ..http import HttpClient
from ..oauth_tokens import get_token_status, token_path_for_env_file, write_token_from_file


def _auth_headers(cfg, token: str | None) -> dict[str, str]:
    if cfg.auth_mode in {"personal", "plan"}:
        return {"X-Figma-Token": token or ""}
    return {"Authorization": f"Bearer {token or ''}"}


def cmd_auth_check(args, ctx) -> int:
    cfg = ctx["cfg"]
    skip_live = bool(getattr(args, "skip_live", False))
    tok_path = token_path_for_env_file(ctx["env_file"])
    status = get_token_status(tok_path)

    probe = {
        "mode": cfg.auth_mode,
        "attempted": False,
        "status": None,
        "ok": None,
        "reason": None,
    }
    overall_ok = True
    token_present = bool(cfg.token)
    if cfg.auth_mode == "plan":
        probe["attempted"] = False
        probe["reason"] = "plan mode: /v1/me is not the plan-token smoke endpoint"
        overall_ok = token_present
        if not token_present:
            probe["reason"] = "plan mode: no token available in env or token file"
            probe["status"] = "blocked"
            probe["ok"] = False
    elif skip_live:
        probe["attempted"] = False
        if token_present:
            probe["reason"] = "skipped by --skip-live"
        else:
            probe["ok"] = False
            overall_ok = False
            probe["status"] = "blocked"
            probe["reason"] = "skipped live probe because no token is configured"
    elif not token_present:
        probe["attempted"] = False
        probe["ok"] = False
        overall_ok = False
        probe["status"] = "blocked"
        probe["reason"] = "no token available in env or token file"
    else:
        headers = _auth_headers(cfg, cfg.token)
        client = HttpClient(timeout_s=ctx["timeout_s"] or cfg.timeout_s, verbose=bool(ctx.get("verbose", False)), user_agent=f"{ctx['tool']}/{ctx['tool_version']}")
        probe["attempted"] = True
        try:
            resp = client.request("GET", f"{cfg.base_url}/v1/me", headers=headers)
            probe["status"] = resp.status
            probe["ok"] = 200 <= resp.status < 300
            if not probe["ok"]:
                overall_ok = False
                probe["reason"] = f"probe failed with status {resp.status}: {resp.text()}"
        except Exception as e:  # noqa: BLE001
            overall_ok = False
            probe["status"] = "blocked"
            probe["ok"] = False
            probe["reason"] = str(e)

    if overall_ok and probe["status"] is None:
        probe["status"] = "ok"
    out = {
        "ok": overall_ok,
        "base_url": cfg.base_url,
        "auth_mode": cfg.auth_mode,
        "token_source": cfg.token_source,
        "token_present": token_present,
        "token_status": {
            "oauth_token_json": {
                "exists": status.exists,
                "path": status.path,
                "fields": status.fields,
                "has_refresh_token": status.has_refresh_token,
                "expires_at_utc": status.expires_at_utc,
            }
        },
        "live_probe": probe,
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0 if overall_ok else 1


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
