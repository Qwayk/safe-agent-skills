from __future__ import annotations

from typing import Any

from ._shared import build_paapi_client


def _mask_key(key_id: str) -> str:
    s = (key_id or "").strip()
    if len(s) <= 6:
        return "***"
    return f"{s[:2]}***{s[-4:]}"


def cmd_auth_check(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    cfg = ctx["cfg"]
    client = build_paapi_client(ctx)

    # Minimal, read-only call to validate signing/credentials.
    resp = client.search_items(
        keywords="test",
        search_index="All",
        item_count=1,
        item_page=1,
        resources=["ItemInfo.Title"],
    )

    out = {
        "ok": True,
        "request_id": resp.request_id,
        "credentials": {
            "access_key_id_masked": _mask_key(cfg.access_key_id),
            "partner_tag": cfg.partner_tag,
            "partner_type": cfg.partner_type,
            "host": cfg.host,
            "region": cfg.region,
            "marketplace": cfg.marketplace,
        },
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0
