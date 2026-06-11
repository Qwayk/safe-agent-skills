from __future__ import annotations

from typing import Any

from ..http import HttpClient
from ..wp_api import WordPressApi


def cmd_search_query(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )

    params: dict[str, Any] = {"search": str(args.query)}
    if args.type:
        params["type"] = str(args.type)
    if args.subtype:
        params["subtype"] = str(args.subtype)

    page = api.list_collection(
        "/search",
        params=params,
        context=None,
        limit=int(args.limit),
        per_page=None if args.per_page is None else int(args.per_page),
        max_pages=int(args.max_pages),
    )

    results = []
    for r in page["items"]:
        if not isinstance(r, dict):
            continue
        results.append(
            {
                "id": r.get("id"),
                "title": r.get("title"),
                "url": r.get("url"),
                "type": r.get("type"),
                "subtype": r.get("subtype"),
            }
        )

    payload: dict[str, Any] = {
        "ok": True,
        "count": len(results),
        "limit": page["limit"],
        "truncated": page["truncated"],
        "results": results,
    }
    if page.get("truncated_reason"):
        payload["truncated_reason"] = page["truncated_reason"]
    if page.get("total") is not None:
        payload["total"] = page["total"]
    if page.get("total_pages") is not None:
        payload["total_pages"] = page["total_pages"]
    payload["pages_fetched"] = page["pages_fetched"]

    ctx["out"].emit(payload)
    return 0

