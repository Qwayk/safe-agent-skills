from __future__ import annotations

from pathlib import Path

from ..oauth_tokens import get_token_status, token_path_for_env_file, write_token_from_file
from .api import _headers
from ..http import HttpClient


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    tok_path = token_path_for_env_file(ctx["env_file"])
    status = get_token_status(tok_path)
    api_status = None
    if cfg.token:
        client = HttpClient(
            timeout_s=float(ctx["timeout_s"]),
            verbose=bool(ctx.get("verbose")),
            user_agent=f"make-com-safe/{ctx.get('tool_version')}",
        )
        try:
            resp = client.request("GET", cfg.base_url.rstrip("/") + "/users/me", headers=_headers(ctx))
            api_status = {"ok": True, "status": resp.status}
        except Exception as e:  # noqa: BLE001
            api_status = {"ok": False, "error": str(e).splitlines()[0]}
    out = {
        "ok": True,
        "base_url": cfg.base_url,
        "env_token_present": bool(cfg.token),
        "oauth_token": {"exists": status.exists, "path": status.path},
        "live_check": api_status,
    }
    ctx["audit"].write("auth.check", out)
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
