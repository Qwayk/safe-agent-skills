from __future__ import annotations

from pathlib import Path

from ..auth_store import (
    auth_path_for_env_file,
    get_access_key_from_store,
    get_auth_status,
    write_auth_from_file,
)
from ..errors import ValidationError


def _effective_access_key(ctx: dict) -> tuple[str | None, dict]:
    cfg = ctx["cfg"]
    auth_path = auth_path_for_env_file(ctx["env_file"])
    stored = get_access_key_from_store(auth_path)
    access_key = cfg.access_key or stored
    return access_key, {"exists": get_auth_status(auth_path).exists, "path": str(auth_path)}


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    access_key, auth_status = _effective_access_key(ctx)
    if not access_key:
        raise ValidationError("Missing UNSPLASH_ACCESS_KEY (set it in your env file or via `unsplash-api-tool auth key set`)")

    # Safe read-only smoke test using Client-ID auth.
    payload = ctx["client"].get("/photos", params={"page": 1, "per_page": 1})
    out = {
        "ok": True,
        "base_url": cfg.base_url,
        "env_access_key_present": bool(cfg.access_key),
        "stored_access_key": auth_status,
        "smoke_test": {"endpoint": "GET /photos", "ok": True, "sample_count": len(payload) if isinstance(payload, list) else None},
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_key_set(args, ctx) -> int:
    dest = auth_path_for_env_file(ctx["env_file"])
    st = write_auth_from_file(src_file=Path(args.file), dest_file=dest)
    out = {"ok": True, "stored_to": st.path, "auth_status": st.__dict__}
    ctx["audit"].write("auth.key_set", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_key_status(args, ctx) -> int:
    _ = args
    st = get_auth_status(auth_path_for_env_file(ctx["env_file"]))
    out = {"ok": True, "auth_status": st.__dict__}
    ctx["audit"].write("auth.key_status", out)
    ctx["out"].emit(out)
    return 0
