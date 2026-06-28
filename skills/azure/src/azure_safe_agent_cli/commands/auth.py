from __future__ import annotations

from pathlib import Path

from ..oauth_tokens import get_token_status, token_path_for_env_file, write_token_from_file


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    tok_path = token_path_for_env_file(ctx["env_file"])
    status = get_token_status(tok_path)
    out = {
        "ok": True,
        "management_endpoint": cfg.management_endpoint,
        "data_plane_endpoint": cfg.data_plane_endpoint,
        "tenant_id_configured": bool(cfg.tenant_id),
        "env_token_present": bool(cfg.token),
        "oauth_token": {"exists": status.exists, "path": status.path},
        "live_verified": False,
        "note": "This local check confirms configuration shape only; live Azure identity is unverified until a safe token and target are available.",
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
