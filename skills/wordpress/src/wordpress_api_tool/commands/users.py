from __future__ import annotations

from typing import Any

from ..http import HttpClient
from ..wp_api import WordPressApi


def _user_summary(u: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": u.get("id"),
        "name": u.get("name"),
        "slug": u.get("slug"),
        "url": u.get("url"),
        "link": u.get("link"),
    }


def cmd_users_list(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )

    params: dict[str, Any] = {}
    if args.query:
        params["search"] = str(args.query)
    if args.slug:
        params["slug"] = str(args.slug)

    page = api.list_collection(
        "/users",
        params=params,
        context=str(args.context),
        limit=int(args.limit),
        per_page=None if args.per_page is None else int(args.per_page),
        max_pages=int(args.max_pages),
    )

    results = []
    for u in page["items"]:
        if not isinstance(u, dict):
            continue
        results.append(_user_summary(u))

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


def cmd_users_get(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )
    user = api.get(f"/users/{int(args.id)}", params={"context": str(args.context)}, retries=1)
    if not isinstance(user, dict):
        raise RuntimeError("Unexpected WordPress response for /users/{id} (expected an object).")
    out = _user_summary(user)
    out["raw"] = user
    ctx["out"].emit(out)
    return 0

