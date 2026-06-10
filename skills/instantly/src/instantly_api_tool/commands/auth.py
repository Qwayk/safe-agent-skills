from __future__ import annotations

from ..http import HttpClient
from ..instantly_client import InstantlyClient


def cmd_auth_check(args: object, ctx: dict) -> int:
    # Keep this command read-only and safe: it should only validate credentials.
    _ = args
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="instantly-api-tool")
    client = InstantlyClient(cfg=cfg, http=http)
    res = client.get("/workspaces/current")

    out = {"ok": True, "base_url": cfg.base_url, "workspace": res.data}
    ctx["audit"].write("auth.check", {"ok": True, "base_url": cfg.base_url})
    ctx["out"].emit(out)
    return 0
