from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from ..google_ads_client import build_google_ads_client, protobuf_to_dict


def cmd_gaql(args: Any, ctx: dict[str, Any]) -> int:
    cfg = ctx["cfg"]
    customer_id = str(getattr(args, "customer_id", "") or "").strip()
    query = str(getattr(args, "query", "") or "").strip()
    limit = getattr(args, "limit", None)
    page_size = getattr(args, "page_size", 1000)

    if not customer_id:
        raise ValidationError("Missing --customer-id")
    if not query:
        raise ValidationError("Missing --query")
    if limit is not None:
        try:
            limit = int(limit)
        except Exception:
            raise ValidationError("--limit must be an integer") from None
        if limit <= 0:
            raise ValidationError("--limit must be > 0")
    try:
        page_size = int(page_size)
    except Exception:
        raise ValidationError("--page-size must be an integer") from None
    if page_size <= 0:
        raise ValidationError("--page-size must be > 0")

    client = build_google_ads_client(cfg)
    ga_service = client.get_service("GoogleAdsService")
    req = client.get_type("SearchGoogleAdsRequest")
    req.customer_id = customer_id
    req.query = query
    it = ga_service.search(request=req)

    rows: list[dict[str, Any]] = []
    limited = False
    for row in it:
        rows.append(protobuf_to_dict(row))
        if limit is not None and len(rows) >= limit:
            limited = True
            break

    out = {
        "ok": True,
        "meta": {
            "customer_id": customer_id,
            "row_count": len(rows),
            "limited": limited,
            "page_size": page_size,
        },
        "rows": rows,
    }
    ctx["audit"].write("gaql", {"ok": True, "row_count": len(rows), "limited": limited})
    ctx["out"].emit(out)
    return 0
