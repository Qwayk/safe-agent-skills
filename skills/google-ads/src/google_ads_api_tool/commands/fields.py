from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from ..google_ads_client import build_google_ads_client, protobuf_to_dict


def _escape_single_quotes(s: str) -> str:
    return (s or "").replace("'", "\\'")


def _query_for_contains(contains: str) -> str:
    c = _escape_single_quotes((contains or "").strip())
    return (
        "SELECT name, category, selectable, filterable, sortable, data_type, enum_values, is_repeated "
        f"WHERE name LIKE '%{c}%'"
    )


def cmd_fields_search(args: Any, ctx: dict[str, Any]) -> int:
    cfg = ctx["cfg"]
    query = str(getattr(args, "query", "") or "").strip()
    contains = str(getattr(args, "contains", "") or "").strip()
    limit = getattr(args, "limit", 50)

    if not query and not contains:
        raise ValidationError("Provide either --query or --contains")
    if query and contains:
        raise ValidationError("Provide only one of --query or --contains")
    try:
        limit = int(limit)
    except Exception:
        raise ValidationError("--limit must be an integer") from None
    if limit <= 0:
        raise ValidationError("--limit must be > 0")

    effective_query = query or _query_for_contains(contains)

    client = build_google_ads_client(cfg)
    fields_service = client.get_service("GoogleAdsFieldService")
    it = fields_service.search_google_ads_fields(query=effective_query)

    fields: list[dict[str, Any]] = []
    limited = False
    for f in it:
        fields.append(protobuf_to_dict(f))
        if len(fields) >= limit:
            limited = True
            break

    out = {
        "ok": True,
        "meta": {
            "query": effective_query,
            "result_count": len(fields),
            "limited": limited,
        },
        "fields": fields,
    }
    ctx["audit"].write("fields.search", {"ok": True, "result_count": len(fields), "limited": limited})
    ctx["out"].emit(out)
    return 0

