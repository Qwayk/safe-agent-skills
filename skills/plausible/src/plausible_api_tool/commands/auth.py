from __future__ import annotations

from ..plausible import PlausibleClient


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])

    health_ok = False
    health_status: int | str | None = None
    try:
        health_resp = client.health()
        health_status = health_resp.status
        health_ok = health_resp.status < 400
    except Exception as e:  # noqa: BLE001
        health_status = f"error: {type(e).__name__}"

    query = {"site_id": cfg.site_id, "metrics": ["visitors"], "date_range": "7d"}
    stats = client.stats_query(query)

    out = {
        "ok": True,
        "base_url": cfg.base_url,
        "site_id": cfg.site_id,
        "health": {"ok": health_ok, "status": health_status},
        "stats_api": {"ok": True, "sample_query": query, "response_keys": sorted(stats.keys())},
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0
