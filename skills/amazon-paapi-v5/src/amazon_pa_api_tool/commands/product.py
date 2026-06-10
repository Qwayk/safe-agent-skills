from __future__ import annotations

import re
from typing import Any

from ..amazon_urls import extract_asin_from_url
from ..paapi import PaApiError
from ._shared import (
    DEFAULT_RESOURCES,
    PAAPI_MAX_ITEM_IDS_PER_REQUEST,
    PAAPI_MAX_VARIATION_COUNT_PER_REQUEST,
    api_errors,
    batch_values,
    build_paapi_client,
    items_from_paapi_response,
    resolve_resources,
    simplify_item,
)

_ASIN_RE = re.compile(r"^[A-Z0-9]{10}$")


def _parse_asins(values: list[str]) -> list[str]:
    asins = [a.strip().upper() for a in values if str(a).strip()]
    if not asins:
        raise RuntimeError("At least one --asin is required")
    bad = [a for a in asins if not _ASIN_RE.fullmatch(a)]
    if bad:
        raise RuntimeError(f"Invalid ASIN(s): {', '.join(bad)}")
    return asins


def cmd_product_get(args: Any, ctx: dict[str, Any]) -> int:
    asins = _parse_asins(list(args.asin or []))

    resources = resolve_resources(
        preset=getattr(args, "resources_preset", None),
        resources=getattr(args, "resource", None),
        default_resources=DEFAULT_RESOURCES,
    )

    batch_size = int(getattr(args, "batch_size", PAAPI_MAX_ITEM_IDS_PER_REQUEST))
    max_requests = getattr(args, "max_requests", None)
    max_requests_i = int(max_requests) if max_requests is not None else None
    batches = batch_values(
        asins,
        batch_size=batch_size,
        api_max_per_request=PAAPI_MAX_ITEM_IDS_PER_REQUEST,
        max_requests=max_requests_i,
        yes=bool(ctx.get("yes")),
        what="product.get",
    )

    client = build_paapi_client(ctx)
    items_out: list[dict[str, Any]] = []
    request_ids: list[str | None] = []
    raw_responses: list[dict[str, Any]] = []
    errors_by_request: list[dict[str, Any]] = []

    for batch in batches:
        try:
            resp = client.get_items(item_ids=batch, resources=resources or None)
        except PaApiError as e:
            raise RuntimeError(str(e)) from None
        request_ids.append(resp.request_id)
        raw_responses.append(resp.data)
        items_out.extend([simplify_item(i) for i in items_from_paapi_response(resp.data)])

        errs = api_errors(resp.data)
        if errs:
            errors_by_request.append({"request_id": resp.request_id, "errors": errs})

    out: dict[str, Any] = {
        "ok": True,
        "requested": asins,
        "count": len(items_out),
        "items": items_out,
    }
    if len(batches) == 1:
        out["request_id"] = request_ids[0]
    else:
        out["requests"] = len(batches)
        out["request_ids"] = request_ids
        out["batch_size"] = batch_size
        if max_requests_i is not None:
            out["max_requests"] = max_requests_i

    if bool(ctx.get("include_raw")):
        out["raw"] = raw_responses[0] if len(batches) == 1 else raw_responses
    if errors_by_request:
        out["api_errors"] = errors_by_request[0]["errors"] if len(batches) == 1 else errors_by_request

    ctx["audit"].write("product.get", out)
    ctx["out"].emit(out)
    return 0


def cmd_product_search(args: Any, ctx: dict[str, Any]) -> int:
    q = (args.query or "").strip()
    if not q:
        raise RuntimeError("Missing --query")

    limit = int(args.limit)
    if limit < 1 or limit > 10:
        raise RuntimeError("--limit must be between 1 and 10")
    item_page = int(args.item_page)
    if item_page < 1:
        raise RuntimeError("--item-page must be >= 1")

    resources = resolve_resources(
        preset=getattr(args, "resources_preset", None),
        resources=getattr(args, "resource", None),
        default_resources=DEFAULT_RESOURCES,
    )

    client = build_paapi_client(ctx)
    try:
        resp = client.search_items(
            keywords=q,
            search_index=str(args.search_index or "All"),
            item_count=limit,
            item_page=item_page,
            resources=resources or None,
        )
    except PaApiError as e:
        raise RuntimeError(str(e)) from None

    items = [simplify_item(i) for i in items_from_paapi_response(resp.data)]
    out = {
        "ok": True,
        "request_id": resp.request_id,
        "query": q,
        "search_index": str(args.search_index or "All"),
        "limit": limit,
        "item_page": item_page,
        "count": len(items),
        "items": items,
    }
    if bool(ctx.get("include_raw")):
        out["raw"] = resp.data
    errors = api_errors(resp.data)
    if errors:
        out["api_errors"] = errors
    ctx["audit"].write("product.search", out)
    ctx["out"].emit(out)
    return 0


def cmd_product_variations(args: Any, ctx: dict[str, Any]) -> int:
    asin = _parse_asins([str(getattr(args, "asin", "") or "").strip()])[0]

    variation_page = int(getattr(args, "variation_page", 1))
    if variation_page < 1:
        raise RuntimeError("--variation-page must be >= 1")
    variation_count = int(getattr(args, "variation_count", 10))
    if variation_count < 1 or variation_count > PAAPI_MAX_VARIATION_COUNT_PER_REQUEST:
        raise RuntimeError(f"--variation-count must be between 1 and {PAAPI_MAX_VARIATION_COUNT_PER_REQUEST}")

    resources = resolve_resources(
        preset=getattr(args, "resources_preset", None),
        resources=getattr(args, "resource", None),
        default_resources=DEFAULT_RESOURCES,
    )

    client = build_paapi_client(ctx)
    try:
        resp = client.get_variations(
            asin=asin,
            variation_page=variation_page,
            variation_count=variation_count,
            resources=resources or None,
        )
    except PaApiError as e:
        raise RuntimeError(str(e)) from None

    items = [simplify_item(i) for i in items_from_paapi_response(resp.data)]
    out: dict[str, Any] = {
        "ok": True,
        "request_id": resp.request_id,
        "asin": asin,
        "variation_page": variation_page,
        "variation_count": variation_count,
        "count": len(items),
        "items": items,
    }
    if bool(ctx.get("include_raw")):
        out["raw"] = resp.data
    errors = api_errors(resp.data)
    if errors:
        out["api_errors"] = errors
    ctx["audit"].write("product.variations", out)
    ctx["out"].emit(out)
    return 0


def cmd_product_resolve(args: Any, ctx: dict[str, Any]) -> int:
    url = (args.url or "").strip()
    asin = extract_asin_from_url(url)
    out: dict[str, Any] = {"ok": True, "url": url, "asin": asin}
    if asin is None:
        out["refused"] = True
        out["reasons"] = [
            "Could not extract ASIN from URL.",
            "Short links like amzn.to require a redirect lookup; this tool does not follow redirects in resolve mode.",
        ]
    ctx["audit"].write("product.resolve", out)
    ctx["out"].emit(out)
    return 0
