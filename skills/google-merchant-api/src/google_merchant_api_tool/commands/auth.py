from __future__ import annotations

from pathlib import Path

from ..errors import ToolError, ValidationError
from ..google_auth import load_credentials_from_config
from ..oauth_tokens import get_token_status, token_path_for_env_file, write_token_from_file


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    try:
        credentials, info = load_credentials_from_config(cfg=cfg, env_file=ctx["env_file"])
        has_token = bool(getattr(credentials, "token", None))
        token_path = token_path_for_env_file(ctx["env_file"])
        token_status = get_token_status(token_path)
        out = {
            "ok": True,
            "auth": {
                "mode": cfg.auth_mode,
                "kind": info.kind,
                "source": info.source,
                "valid": info.valid,
                "expiry_utc": info.expiry_utc,
                "scopes": list(info.scopes),
                "has_token": has_token,
            },
            "token_file": {
                "exists": token_status.exists,
                "path": token_status.path,
                "fields": token_status.fields,
            },
        }
        ctx["audit"].write("auth.check", out)
        ctx["out"].emit(out)
        return 0
    except (ValidationError, ToolError) as e:
        out = {
            "ok": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "auth": {"mode": cfg.auth_mode},
        }
        ctx["audit"].write("auth.check", out)
        ctx["out"].emit(out)
        return 1


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
