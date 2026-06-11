from __future__ import annotations

import math
from typing import Any

from ..http import HttpClient
from ..paapi import PaApiClient


DEFAULT_RESOURCES = [
    "ItemInfo.Title",
    "Images.Primary.Small",
    "Images.Primary.Medium",
    "Images.Primary.Large",
]

RESOURCE_PRESET_CHOICES = ("basic", "none")

PAAPI_MAX_ITEM_IDS_PER_REQUEST = 10
PAAPI_MAX_BROWSE_NODE_IDS_PER_REQUEST = 10
PAAPI_MAX_VARIATION_COUNT_PER_REQUEST = 10


def build_paapi_client(ctx: dict[str, Any]) -> PaApiClient:
    cfg = ctx["cfg"]
    http = HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx["verbose"]),
        user_agent=str(ctx.get("user_agent") or "amazon-pa-api-tool/0.1"),
    )
    return PaApiClient(cfg=cfg, http=http)


def resolve_resources(
    *,
    preset: str | None,
    resources: list[str] | None,
    default_resources: list[str],
) -> list[str]:
    if preset is None and resources is None:
        return list(default_resources)

    base: list[str]
    if preset is None:
        base = list(default_resources)
    elif preset == "basic":
        base = list(default_resources)
    elif preset == "none":
        base = []
    else:
        raise RuntimeError(
            f"Unknown --resources-preset {preset!r} (supported: {', '.join(RESOURCE_PRESET_CHOICES)})"
        )

    explicit = []
    for r in resources or []:
        s = str(r or "").strip()
        if s:
            explicit.append(s)

    seen = set()
    out: list[str] = []
    for r in base + explicit:
        if r in seen:
            continue
        out.append(r)
        seen.add(r)
    return out


def batch_values(
    values: list[str],
    *,
    batch_size: int,
    api_max_per_request: int,
    max_requests: int | None,
    yes: bool,
    what: str,
) -> list[list[str]]:
    if batch_size <= 0:
        raise RuntimeError("--batch-size must be >= 1")
    if batch_size > api_max_per_request:
        raise RuntimeError(f"--batch-size must be <= {api_max_per_request} for {what}")
    if max_requests is not None and int(max_requests) < 1:
        raise RuntimeError("--max-requests must be >= 1")

    if not values:
        return []
    reqs = int(math.ceil(len(values) / float(batch_size)))
    if max_requests is not None and reqs > int(max_requests):
        raise RuntimeError(
            f"{what} would require {reqs} requests, which exceeds --max-requests={int(max_requests)}"
        )
    if reqs > 1 and not yes:
        raise RuntimeError(
            f"{what} would require {reqs} requests (batch size {batch_size}). Re-run with --yes to allow batching."
        )

    out: list[list[str]] = []
    for i in range(0, len(values), batch_size):
        out.append(values[i : i + batch_size])
    return out


def image_blob(img: Any) -> dict[str, Any] | None:
    if not isinstance(img, dict):
        return None
    url = img.get("URL")
    height = img.get("Height")
    width = img.get("Width")
    if not isinstance(url, str) or not url.strip():
        return None
    out: dict[str, Any] = {"url": url.strip()}
    if isinstance(height, int):
        out["height"] = height
    if isinstance(width, int):
        out["width"] = width
    return out


def simplify_item(item: dict[str, Any]) -> dict[str, Any]:
    asin = (item.get("ASIN") or "").strip()
    title = None
    item_info = item.get("ItemInfo")
    if isinstance(item_info, dict):
        title_obj = item_info.get("Title")
        if isinstance(title_obj, dict):
            dv = title_obj.get("DisplayValue")
            if isinstance(dv, str) and dv.strip():
                title = dv.strip()

    images_out: dict[str, Any] = {}
    images = item.get("Images")
    if isinstance(images, dict):
        primary = images.get("Primary")
        if isinstance(primary, dict):
            for size in ("Small", "Medium", "Large"):
                blob = image_blob(primary.get(size))
                if blob:
                    images_out[size.lower()] = blob

    out: dict[str, Any] = {"asin": asin}
    if title is not None:
        out["title"] = title
    if images_out:
        out["images"] = images_out

    url = item.get("DetailPageURL")
    if isinstance(url, str) and url.strip():
        out["affiliate_url"] = url.strip()
    return out


def items_from_paapi_response(data: dict[str, Any]) -> list[dict[str, Any]]:
    for container_key in ("ItemsResult", "SearchResult", "VariationsResult"):
        container = data.get(container_key)
        if isinstance(container, dict):
            items = container.get("Items")
            if isinstance(items, list):
                out: list[dict[str, Any]] = []
                for it in items:
                    if isinstance(it, dict):
                        out.append(it)
                return out
    return []


def browse_nodes_from_paapi_response(data: dict[str, Any]) -> list[dict[str, Any]]:
    container = data.get("BrowseNodesResult")
    if isinstance(container, dict):
        nodes = container.get("BrowseNodes")
        if isinstance(nodes, list):
            out: list[dict[str, Any]] = []
            for n in nodes:
                if isinstance(n, dict):
                    out.append(n)
            return out
    return []


def simplify_browse_node(node: dict[str, Any]) -> dict[str, Any]:
    node_id = None
    for k in ("Id", "BrowseNodeId"):
        v = node.get(k)
        if isinstance(v, str) and v.strip():
            node_id = v.strip()
            break

    display_name = None
    v = node.get("DisplayName")
    if isinstance(v, str) and v.strip():
        display_name = v.strip()

    out: dict[str, Any] = {}
    if node_id is not None:
        out["id"] = node_id
    if display_name is not None:
        out["display_name"] = display_name

    ancestors = node.get("Ancestor")
    if isinstance(ancestors, list):
        out_anc: list[dict[str, Any]] = []
        for a in ancestors:
            if not isinstance(a, dict):
                continue
            blob: dict[str, Any] = {}
            aid = a.get("Id")
            if isinstance(aid, str) and aid.strip():
                blob["id"] = aid.strip()
            aname = a.get("DisplayName")
            if isinstance(aname, str) and aname.strip():
                blob["display_name"] = aname.strip()
            if blob:
                out_anc.append(blob)
        if out_anc:
            out["ancestors"] = out_anc

    return out


def api_errors(data: dict[str, Any]) -> list[dict[str, Any]]:
    errs = data.get("Errors")
    if isinstance(errs, list):
        return [e for e in errs if isinstance(e, dict)]
    return []
