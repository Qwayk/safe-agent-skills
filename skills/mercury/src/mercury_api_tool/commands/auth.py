from __future__ import annotations

from ..context import build_mercury_client


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    client = build_mercury_client(ctx)
    org = client.get_json("/organization")
    out = {"ok": True, "base_url": cfg.base_url, "auth_scheme": cfg.auth_scheme, "organization": org}
    ctx["audit"].write("auth.check", {"base_url": cfg.base_url, "auth_scheme": cfg.auth_scheme})
    ctx["out"].emit(out)
    return 0
