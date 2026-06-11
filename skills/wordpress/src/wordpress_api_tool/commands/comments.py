from __future__ import annotations

from typing import Any

from ..http import HttpClient
from ..wp_api import WordPressApi


def _comment_summary(c: dict[str, Any]) -> dict[str, Any]:
    content = c.get("content") or {}
    return {
        "id": c.get("id"),
        "post": c.get("post"),
        "parent": c.get("parent"),
        "status": c.get("status"),
        "type": c.get("type"),
        "author": c.get("author"),
        "author_name": c.get("author_name"),
        "date_gmt": c.get("date_gmt"),
        "link": c.get("link"),
        "content_rendered": content.get("rendered"),
    }


def cmd_comments_list(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )

    params: dict[str, Any] = {}
    if args.post_id is not None:
        params["post"] = str(int(args.post_id))
    if args.query:
        params["search"] = str(args.query)
    if args.status:
        params["status"] = str(args.status)
    if args.author is not None:
        params["author"] = str(int(args.author))
    if args.parent is not None:
        params["parent"] = str(int(args.parent))
    if args.type:
        params["type"] = str(args.type)
    if args.after:
        params["after"] = str(args.after)
    if args.before:
        params["before"] = str(args.before)
    if args.order:
        params["order"] = str(args.order)
    if args.orderby:
        params["orderby"] = str(args.orderby)

    page = api.list_collection(
        "/comments",
        params=params,
        context=str(args.context),
        limit=int(args.limit),
        per_page=None if args.per_page is None else int(args.per_page),
        max_pages=int(args.max_pages),
    )

    results = [_comment_summary(c) for c in page["items"]]
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


def cmd_comments_get(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )
    comment = api.get(f"/comments/{int(args.id)}", params={"context": str(args.context)}, retries=1)
    if not isinstance(comment, dict):
        raise RuntimeError("Unexpected WordPress response for /comments/{id} (expected an object).")
    out = _comment_summary(comment)
    out["raw"] = comment
    ctx["out"].emit(out)
    return 0

