from __future__ import annotations

from ..http import HttpClient
from ..instantly_client import InstantlyClient


def cmd_whoami(args: object, ctx: dict) -> int:
    _ = args
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="instantly-api-tool")
    client = InstantlyClient(cfg=cfg, http=http)
    res = client.get("/workspaces/current")
    out = {"ok": True, "workspace": res.data}
    ctx["audit"].write("whoami", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_health(args: object, ctx: dict) -> int:
    # Health is currently implemented as the same endpoint as whoami.
    return cmd_whoami(args, ctx)

