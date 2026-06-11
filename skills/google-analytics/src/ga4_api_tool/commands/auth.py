from __future__ import annotations

from pathlib import Path

from ..auth import authorization_header, auth_summary
from ..oauth_tokens import get_token_status, token_path_for_env_file, write_token_from_file


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    tok_path = token_path_for_env_file(ctx["env_file"])
    status = get_token_status(tok_path)
    refreshed = False
    if bool(ctx.get("apply")):
        # This performs an OAuth token refresh (network) for ADC/service account/refresh-token modes.
        # It must not print token values.
        _ = authorization_header(cfg, refresh=True)
        refreshed = True
    out = {
        "ok": True,
        "auth": auth_summary(cfg),
        "admin_base_url": cfg.admin_base_url,
        "data_base_url": cfg.data_base_url,
        "token_refreshed": refreshed,
        "oauth_token": {"exists": status.exists, "path": status.path},
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
