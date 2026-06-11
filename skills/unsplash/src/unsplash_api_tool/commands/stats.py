from __future__ import annotations

from typing import Any

from ..unsplash_client import UnsplashClient


def cmd_stats_total(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    client: UnsplashClient = ctx["client"]
    data = client.get("/stats/total")
    out = {"ok": True, "endpoint": "GET /stats/total", "data": data}
    ctx["audit"].write("stats.total", {})
    ctx["out"].emit(out)
    return 0


def cmd_stats_month(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    client: UnsplashClient = ctx["client"]
    data = client.get("/stats/month")
    out = {"ok": True, "endpoint": "GET /stats/month", "data": data}
    ctx["audit"].write("stats.month", {})
    ctx["out"].emit(out)
    return 0

