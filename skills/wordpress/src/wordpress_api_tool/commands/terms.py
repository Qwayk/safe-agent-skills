from __future__ import annotations

from typing import Any

from ..http import HttpClient
from ..wp_api import WordPressApi


def _rest_base(taxonomy: str) -> str:
    if taxonomy == "categories":
        return "categories"
    if taxonomy == "tags":
        return "tags"
    raise RuntimeError(f"Unsupported taxonomy: {taxonomy!r}")


def _term_summary(t: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": t.get("id"),
        "name": t.get("name"),
        "slug": t.get("slug"),
        "taxonomy": t.get("taxonomy"),
        "count": t.get("count"),
        "parent": t.get("parent"),
        "link": t.get("link"),
    }


def cmd_terms_list(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )

    params: dict[str, Any] = {}
    if args.query:
        params["search"] = str(args.query)
    if args.slug:
        params["slug"] = str(args.slug)
    if bool(args.hide_empty):
        params["hide_empty"] = "true"

    page = api.list_collection(
        f"/{_rest_base(str(args.taxonomy))}",
        params=params,
        context=str(args.context),
        limit=int(args.limit),
        per_page=None if args.per_page is None else int(args.per_page),
        max_pages=int(args.max_pages),
    )

    results = []
    for t in page["items"]:
        if not isinstance(t, dict):
            continue
        results.append(_term_summary(t))

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


def cmd_terms_get(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )
    taxonomy = str(args.taxonomy)
    term = api.get(
        f"/{_rest_base(taxonomy)}/{int(args.id)}",
        params={"context": str(args.context)},
        retries=1,
    )
    if not isinstance(term, dict):
        raise RuntimeError("Unexpected WordPress response for term get (expected an object).")
    out = _term_summary(term)
    out["raw"] = term
    ctx["out"].emit(out)
    return 0

