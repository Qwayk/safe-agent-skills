from __future__ import annotations

from typing import Any

from ..amazon_urls import build_affiliate_dp_link


def cmd_link_build(args: Any, ctx: dict[str, Any]) -> int:
    cfg = ctx["cfg"]
    url = build_affiliate_dp_link(marketplace=cfg.marketplace, asin=str(args.asin), partner_tag=cfg.partner_tag)
    out = {"ok": True, "asin": str(args.asin).strip().upper(), "affiliate_url": url}
    ctx["audit"].write("link.build", out)
    ctx["out"].emit(out)
    return 0

