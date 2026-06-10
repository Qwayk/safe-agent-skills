from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ._shared import (
    DEFAULT_RESOURCES,
    PAAPI_MAX_BROWSE_NODE_IDS_PER_REQUEST,
    PAAPI_MAX_ITEM_IDS_PER_REQUEST,
    PAAPI_MAX_VARIATION_COUNT_PER_REQUEST,
    batch_values,
    browse_nodes_from_paapi_response,
    build_paapi_client,
    items_from_paapi_response,
    simplify_browse_node,
    simplify_item,
)

_ASIN_RE = re.compile(r"^[A-Z0-9]{10}$")
_BROWSE_NODE_RE = re.compile(r"^[0-9]+$")


@dataclass(frozen=True)
class ActionSpec:
    name: str
    handler: Callable[[dict[str, str], dict[str, Any]], dict[str, Any]]

def _split_pipe_list(value: str) -> list[str]:
    return [p.strip() for p in str(value or "").split("|") if p.strip()]


def _product_get(row: dict[str, str], ctx: dict[str, Any]) -> dict[str, Any]:
    raw_asins: list[str] = []
    if (row.get("asins") or "").strip():
        raw_asins = _split_pipe_list(row.get("asins") or "")
    else:
        raw_asins = [(row.get("asin") or "").strip()]

    asins = [a.strip().upper() for a in raw_asins if str(a).strip()]
    if not asins:
        raise RuntimeError("Missing asin/asins")
    bad = [a for a in asins if not _ASIN_RE.fullmatch(a)]
    if bad:
        raise RuntimeError(f"Invalid ASIN(s): {', '.join(bad)}")

    batches = batch_values(
        asins,
        batch_size=PAAPI_MAX_ITEM_IDS_PER_REQUEST,
        api_max_per_request=PAAPI_MAX_ITEM_IDS_PER_REQUEST,
        max_requests=10,
        yes=bool(ctx.get("yes")),
        what="product.get",
    )

    client = build_paapi_client(ctx)
    items_out: list[dict[str, Any]] = []
    request_ids: list[str | None] = []
    raw_responses: list[dict[str, Any]] = []

    for batch in batches:
        resp = client.get_items(item_ids=batch, resources=DEFAULT_RESOURCES)
        request_ids.append(resp.request_id)
        raw_responses.append(resp.data)
        items_out.extend([simplify_item(i) for i in items_from_paapi_response(resp.data)])

    out: dict[str, Any] = {"requested": asins, "count": len(items_out), "items": items_out}
    if len(batches) == 1:
        out["request_id"] = request_ids[0]
    else:
        out["requests"] = len(batches)
        out["request_ids"] = request_ids

    if bool(ctx.get("include_raw")):
        out["raw"] = raw_responses[0] if len(batches) == 1 else raw_responses
    return out


def _product_search(row: dict[str, str], ctx: dict[str, Any]) -> dict[str, Any]:
    query = (row.get("query") or "").strip()
    if not query:
        raise RuntimeError("Missing query")
    search_index = (row.get("search_index") or "All").strip() or "All"
    limit = int((row.get("limit") or "10").strip() or "10")
    page = int((row.get("item_page") or "1").strip() or "1")
    resp = build_paapi_client(ctx).search_items(
        keywords=query,
        search_index=search_index,
        item_count=limit,
        item_page=page,
        resources=DEFAULT_RESOURCES,
    )
    items = [simplify_item(i) for i in items_from_paapi_response(resp.data)]
    out: dict[str, Any] = {"request_id": resp.request_id, "count": len(items), "items": items}
    if bool(ctx.get("include_raw")):
        out["raw"] = resp.data
    return out


def _product_variations(row: dict[str, str], ctx: dict[str, Any]) -> dict[str, Any]:
    asin = (row.get("asin") or "").strip().upper()
    if not asin:
        raise RuntimeError("Missing asin")
    if not _ASIN_RE.fullmatch(asin):
        raise RuntimeError(f"Invalid ASIN: {asin}")

    variation_page = int((row.get("variation_page") or "1").strip() or "1")
    if variation_page < 1:
        raise RuntimeError("variation_page must be >= 1")
    variation_count = int((row.get("variation_count") or "10").strip() or "10")
    if variation_count < 1 or variation_count > PAAPI_MAX_VARIATION_COUNT_PER_REQUEST:
        raise RuntimeError(f"variation_count must be between 1 and {PAAPI_MAX_VARIATION_COUNT_PER_REQUEST}")

    resp = build_paapi_client(ctx).get_variations(
        asin=asin,
        variation_page=variation_page,
        variation_count=variation_count,
        resources=DEFAULT_RESOURCES,
    )
    items = [simplify_item(i) for i in items_from_paapi_response(resp.data)]
    out: dict[str, Any] = {"request_id": resp.request_id, "count": len(items), "items": items}
    if bool(ctx.get("include_raw")):
        out["raw"] = resp.data
    return out


def _browse_get(row: dict[str, str], ctx: dict[str, Any]) -> dict[str, Any]:
    raw_ids: list[str] = []
    if (row.get("browse_node_ids") or "").strip():
        raw_ids = _split_pipe_list(row.get("browse_node_ids") or "")
    else:
        raw_ids = [(row.get("browse_node_id") or "").strip()]

    ids = [str(i).strip() for i in raw_ids if str(i).strip()]
    if not ids:
        raise RuntimeError("Missing browse_node_id/browse_node_ids")
    bad = [i for i in ids if not _BROWSE_NODE_RE.fullmatch(i)]
    if bad:
        raise RuntimeError(f"Invalid browse node id(s): {', '.join(bad)}")

    batches = batch_values(
        ids,
        batch_size=PAAPI_MAX_BROWSE_NODE_IDS_PER_REQUEST,
        api_max_per_request=PAAPI_MAX_BROWSE_NODE_IDS_PER_REQUEST,
        max_requests=10,
        yes=bool(ctx.get("yes")),
        what="browse.get",
    )

    client = build_paapi_client(ctx)
    nodes_out: list[dict[str, Any]] = []
    request_ids: list[str | None] = []
    raw_responses: list[dict[str, Any]] = []

    for batch in batches:
        resp = client.get_browse_nodes(browse_node_ids=batch, resources=None)
        request_ids.append(resp.request_id)
        raw_responses.append(resp.data)
        nodes_out.extend([simplify_browse_node(n) for n in browse_nodes_from_paapi_response(resp.data)])

    out: dict[str, Any] = {"requested": ids, "count": len(nodes_out), "browse_nodes": nodes_out}
    if len(batches) == 1:
        out["request_id"] = request_ids[0]
    else:
        out["requests"] = len(batches)
        out["request_ids"] = request_ids

    if bool(ctx.get("include_raw")):
        out["raw"] = raw_responses[0] if len(batches) == 1 else raw_responses
    return out


_ACTIONS = {
    "product.get": ActionSpec(name="product.get", handler=_product_get),
    "product.search": ActionSpec(name="product.search", handler=_product_search),
    "product.variations": ActionSpec(name="product.variations", handler=_product_variations),
    "browse.get": ActionSpec(name="browse.get", handler=_browse_get),
}


def cmd_jobs_run(args: Any, ctx: dict[str, Any]) -> int:
    job_file = Path(args.file)
    if not job_file.exists():
        raise RuntimeError(f"Job file not found: {job_file}")

    processed = 0
    errors = 0
    results: list[dict[str, Any]] = []

    with job_file.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=1):
            if not row:
                continue
            if args.limit is not None and processed >= int(args.limit):
                break
            processed += 1

            action_name = (row.get("action") or "").strip()
            try:
                if not action_name:
                    raise RuntimeError("Missing action column")
                spec = _ACTIONS.get(action_name)
                if spec is None:
                    raise RuntimeError(f"Unknown action: {action_name} (supported: {', '.join(sorted(_ACTIONS))})")

                res = spec.handler(row, ctx)
                results.append({"row": row_num, "action": action_name, "input": row, "result": res})
            except Exception as e:  # noqa: BLE001
                errors += 1
                results.append({"row": row_num, "action": action_name or "<empty>", "input": row, "error": str(e)})
                break

    out = {
        "ok": errors == 0,
        "apply": bool(ctx.get("apply")),
        "count": processed,
        "errors": errors,
        "results": results,
    }
    if "audit" in ctx:
        ctx["audit"].write("jobs.run", out)
    ctx["out"].emit(out)
    return 1 if errors else 0
