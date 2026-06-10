from __future__ import annotations

import time
from typing import Any, Callable

from .. import __version__
from ..commands.plan_helpers import build_plan, write_plan
from ..errors import ValidationError, ToolError
from ..http import HttpClient
from ..json_files import write_json_file
from ..locale_data import LocaleInfo, locale_info
from ..oauth_tokens import authorization_header


RESOURCE_NAMES = [
    "BrowseNodeInfo",
    "BrowseNodes",
    "Images",
    "ItemInfo",
    "OffersV2",
    "ParentAsin",
    "SearchRefinements",
    "VariationSummary",
]

RESOURCE_EXPANSIONS: dict[str, dict[str, list[str]]] = {
    "GetBrowseNodes": {
        "BrowseNodes": [
            "browseNodes.ancestor",
            "browseNodes.children",
        ],
    },
    "GetItems": {
        "BrowseNodeInfo": [
            "browseNodeInfo.browseNodes",
            "browseNodeInfo.browseNodes.ancestor",
            "browseNodeInfo.browseNodes.salesRank",
            "browseNodeInfo.websiteSalesRank",
        ],
        "Images": [
            "images.primary.small",
            "images.primary.medium",
            "images.primary.large",
            "images.variants.small",
            "images.variants.medium",
            "images.variants.large",
        ],
        "ItemInfo": [
            "itemInfo.byLineInfo",
            "itemInfo.classifications",
            "itemInfo.contentInfo",
            "itemInfo.contentRating",
            "itemInfo.externalIds",
            "itemInfo.features",
            "itemInfo.manufactureInfo",
            "itemInfo.productInfo",
            "itemInfo.technicalInfo",
            "itemInfo.title",
            "itemInfo.tradeInInfo",
        ],
        "OffersV2": [
            "offersV2.listings.availability",
            "offersV2.listings.condition",
            "offersV2.listings.dealDetails",
            "offersV2.listings.isBuyBoxWinner",
            "offersV2.listings.loyaltyPoints",
            "offersV2.listings.merchantInfo",
            "offersV2.listings.price",
            "offersV2.listings.type",
        ],
        "ParentAsin": ["parentASIN"],
    },
    "GetVariations": {
        "BrowseNodeInfo": [
            "browseNodeInfo.browseNodes",
            "browseNodeInfo.browseNodes.ancestor",
            "browseNodeInfo.browseNodes.salesRank",
            "browseNodeInfo.websiteSalesRank",
        ],
        "Images": [
            "images.primary.small",
            "images.primary.medium",
            "images.primary.large",
            "images.variants.small",
            "images.variants.medium",
            "images.variants.large",
        ],
        "ItemInfo": [
            "itemInfo.byLineInfo",
            "itemInfo.classifications",
            "itemInfo.contentInfo",
            "itemInfo.contentRating",
            "itemInfo.externalIds",
            "itemInfo.features",
            "itemInfo.manufactureInfo",
            "itemInfo.productInfo",
            "itemInfo.technicalInfo",
            "itemInfo.title",
            "itemInfo.tradeInInfo",
        ],
        "OffersV2": [
            "offersV2.listings.availability",
            "offersV2.listings.condition",
            "offersV2.listings.dealDetails",
            "offersV2.listings.isBuyBoxWinner",
            "offersV2.listings.loyaltyPoints",
            "offersV2.listings.merchantInfo",
            "offersV2.listings.price",
            "offersV2.listings.type",
        ],
        "ParentAsin": ["parentASIN"],
        "VariationSummary": [
            "variationSummary.price.highestPrice",
            "variationSummary.price.lowestPrice",
            "variationSummary.variationDimension",
        ],
    },
    "SearchItems": {
        "BrowseNodeInfo": [
            "browseNodeInfo.browseNodes",
            "browseNodeInfo.browseNodes.ancestor",
            "browseNodeInfo.browseNodes.salesRank",
            "browseNodeInfo.websiteSalesRank",
        ],
        "Images": [
            "images.primary.small",
            "images.primary.medium",
            "images.primary.large",
            "images.variants.small",
            "images.variants.medium",
            "images.variants.large",
        ],
        "ItemInfo": [
            "itemInfo.byLineInfo",
            "itemInfo.classifications",
            "itemInfo.contentInfo",
            "itemInfo.contentRating",
            "itemInfo.externalIds",
            "itemInfo.features",
            "itemInfo.manufactureInfo",
            "itemInfo.productInfo",
            "itemInfo.technicalInfo",
            "itemInfo.title",
            "itemInfo.tradeInInfo",
        ],
        "OffersV2": [
            "offersV2.listings.availability",
            "offersV2.listings.condition",
            "offersV2.listings.dealDetails",
            "offersV2.listings.isBuyBoxWinner",
            "offersV2.listings.loyaltyPoints",
            "offersV2.listings.merchantInfo",
            "offersV2.listings.price",
            "offersV2.listings.type",
        ],
        "ParentAsin": ["parentASIN"],
        "SearchRefinements": ["searchRefinements"],
    },
}

RESOURCE_PRESETS: dict[str, dict[str, list[str]]] = {
    "GetBrowseNodes": {
        "browse-basic": ["BrowseNodes"],
        "full": ["BrowseNodes"],
    },
    "GetItems": {
        "book-media": ["ItemInfo", "Images", "OffersV2", "ParentAsin"],
        "inventory-view": ["ItemInfo", "OffersV2", "Images"],
        "full": ["BrowseNodeInfo", "Images", "ItemInfo", "OffersV2", "ParentAsin"],
    },
    "GetVariations": {
        "book-media": ["ItemInfo", "Images", "OffersV2", "ParentAsin", "VariationSummary"],
        "inventory-view": ["ItemInfo", "OffersV2", "Images"],
        "full": ["BrowseNodeInfo", "Images", "ItemInfo", "OffersV2", "ParentAsin", "VariationSummary"],
    },
    "SearchItems": {
        "book-media": ["ItemInfo", "Images", "OffersV2", "ParentAsin"],
        "inventory-view": ["ItemInfo", "OffersV2", "Images"],
        "search-lens": ["ItemInfo", "SearchRefinements", "Images"],
        "full": ["BrowseNodeInfo", "Images", "ItemInfo", "OffersV2", "ParentAsin", "SearchRefinements"],
    },
}

_OPERATION_PATHS: dict[str, str] = {
    # Docs use lower-camel paths (ex: /catalog/v1/getItems) even when the operation name
    # is capitalized (ex: GetItems).
    "GetBrowseNodes": "getBrowseNodes",
    "GetItems": "getItems",
    "GetVariations": "getVariations",
    "SearchItems": "searchItems",
}


def _normalize_resource_flags(flags: list[str] | None) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    if not flags:
        return normalized
    for raw in flags:
        if not raw:
            continue
        parts = [part.strip() for part in raw.strip().split(",")]
        for part in parts:
            if not part:
                continue
            if part not in RESOURCE_NAMES:
                raise ValidationError(f"Unknown resource: {part}")
            if part in seen:
                continue
            seen.add(part)
            normalized.append(part)
    return normalized


def _resolve_resources(
    operation: str,
    explicit: list[str] | None,
    presets: list[str] | None,
    default_preset: str,
) -> list[str]:
    operation_presets = RESOURCE_PRESETS.get(operation, {})
    operation_resources = RESOURCE_EXPANSIONS.get(operation, {})

    selected_aliases: list[str] = []
    seen_aliases: set[str] = set()

    def add_alias(alias: str) -> None:
        if alias in seen_aliases:
            return
        if alias not in operation_resources:
            raise ValidationError(f"Resource {alias} is not supported for {operation}")
        seen_aliases.add(alias)
        selected_aliases.append(alias)

    if presets:
        for alias in presets:
            if not alias:
                continue
            key = alias.strip().lower()
            preset_aliases = operation_presets.get(key)
            if preset_aliases is None:
                raise ValidationError(f"Unknown resource preset for {operation}: {alias}")
            for preset_alias in preset_aliases:
                add_alias(preset_alias)

    for alias in _normalize_resource_flags(explicit):
        add_alias(alias)

    if not selected_aliases:
        default_aliases = operation_presets.get(default_preset.lower(), [])
        for preset_alias in default_aliases:
            add_alias(preset_alias)
        if not selected_aliases:
            raise ValidationError("No resources selected")

    resolved: list[str] = []
    seen_resources: set[str] = set()
    for alias in selected_aliases:
        for resource in operation_resources[alias]:
            if resource in seen_resources:
                continue
            seen_resources.add(resource)
            resolved.append(resource)
    return resolved


def _flatten_values(values: list[str] | None) -> list[str]:
    if not values:
        return []
    return [value.strip() for value in values if value and value.strip()]


def _resolve_locale_info(cfg: Any, override: str | None) -> LocaleInfo:
    code = (override or getattr(cfg, "locale", "") or "").strip()
    info = locale_info(code)
    if not info:
        raise ValidationError(f"Locale not tracked: {code or 'empty'}")
    return info


def _decorate_body_with_marketplace(
    body: dict[str, Any], cfg: Any, locale: LocaleInfo
) -> None:
    body["marketplace"] = locale.marketplace
    body["partnerTag"] = cfg.partner_tag


def _build_http_client(ctx: dict[str, Any]) -> HttpClient:
    timeout = float(ctx.get("timeout_s") or 30)
    verbose = bool(ctx.get("verbose"))
    user_agent = f"amazon-creators-api-tool/{ctx.get('tool_version') or __version__}"
    return HttpClient(timeout_s=timeout, verbose=verbose, user_agent=user_agent)


def _catalog_url(cfg: Any, operation: str) -> str:
    base = str(getattr(cfg, "base_url", "")).rstrip("/")
    op = _OPERATION_PATHS.get(operation, operation)
    return f"{base}/{op}"


def _call_operation(
    cfg: Any,
    ctx: dict[str, Any],
    operation: str,
    body: dict[str, Any],
    locale: LocaleInfo,
) -> dict[str, Any]:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": authorization_header(cfg, ctx["env_file"]),
        "x-marketplace": locale.marketplace,
    }
    client = _build_http_client(ctx)
    url = _catalog_url(cfg, operation)
    try:
        resp = client.request("POST", url, headers=headers, json_body=body, retries=2)
    except RuntimeError as exc:
        raise ToolError(f"{operation} failed: {exc}") from exc
    return resp.json()


def _extract_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if not payload:
        return []
    value = payload.get("items")
    if isinstance(value, list):
        return value
    # Common response container shapes across the 4 operations.
    for container in ("itemsResult", "itemResults", "variationsResult", "searchResult"):
        obj = payload.get(container)
        if isinstance(obj, dict):
            items = obj.get("items")
            if isinstance(items, list):
                return items
    return []


def _display_value(field: Any) -> Any:
    if isinstance(field, dict):
        return field.get("displayValue") or field.get("value")
    return field


def _simplified_item(item: dict[str, Any]) -> dict[str, Any]:
    item_info = item.get("itemInfo", {}) or {}
    classifications = item_info.get("classifications", {}) or {}
    return {
        "asin": item.get("asin"),
        "title": _display_value(item_info.get("title")),
        "binding": _display_value(classifications.get("binding")),
        "product_group": _display_value(classifications.get("productGroup")),
        "content_info": item_info.get("contentInfo"),
        "technical_info": item_info.get("technicalInfo"),
        "classifications": classifications,
        "parent_asin": item.get("parentASIN"),
        "variation_summary": item.get("variationSummary"),
    }


def _simplified_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = _extract_items(payload)
    return [_simplified_item(item) for item in rows if isinstance(item, dict)]


def _extract_browse_nodes(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if not payload:
        return []
    for key in ("browseNodes", "BrowseNodes"):
        value = payload.get(key)
        if isinstance(value, list):
            return [node for node in value if isinstance(node, dict)]
    result = payload.get("browseNodesResult")
    if isinstance(result, dict):
        value = result.get("browseNodes")
        if isinstance(value, list):
            return [node for node in value if isinstance(node, dict)]
    info = payload.get("browseNodeInfo") or payload.get("BrowseNodeInfo")
    if isinstance(info, dict):
        for key in ("browseNodes", "BrowseNodes"):
            value = info.get(key)
            if isinstance(value, list):
                return [node for node in value if isinstance(node, dict)]
    return []


def _simplified_browse_node(node: dict[str, Any]) -> dict[str, Any]:
    return {
        "node_id": node.get("id") or node.get("nodeId"),
        "name": node.get("displayName") or node.get("name"),
        "parent_node": node.get("parentNode"),
        "ancestors": node.get("ancestors"),
        "path": node.get("browseNodePath"),
        "children": node.get("children") or node.get("browseNodeChildren"),
    }


def _simplified_browse_nodes(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = _extract_browse_nodes(payload)
    return [_simplified_browse_node(node) for node in rows]


def _build_request_summary(body: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "keywords",
        "browseNodeIds",
        "itemIds",
        "itemIdType",
        "asin",
        "variationCount",
        "variationPage",
        "itemCount",
        "itemPage",
    )
    return {k: body[k] for k in keys if k in body}


def _build_response(
    args: Any,
    ctx: dict[str, Any],
    operation: str,
    body: dict[str, Any],
    locale: LocaleInfo,
    payload: dict[str, Any] | None = None,
    simplified: list[dict[str, Any]] | None = None,
    simplified_key: str | None = "items",
) -> dict[str, Any]:
    response: dict[str, Any] = {
        "operation": operation,
        "locale": locale.locale_tag,
        "marketplace": locale.marketplace,
        "partner_tag": ctx["cfg"].partner_tag,
        "resources": body.get("resources"),
        "request": _build_request_summary(body),
    }
    if simplified is not None and simplified_key:
        response[simplified_key] = simplified
    if payload and args.include_raw:
        response["raw"] = payload
    return response


def _catalog_selector(
    operation: str,
    locale: LocaleInfo,
    body: dict[str, Any],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    selector: dict[str, Any] = {
        "operation": operation,
        "locale": locale.locale_tag,
        "marketplace": locale.marketplace,
        "resources": body.get("resources"),
    }
    if extra:
        filtered = {k: v for k, v in extra.items() if v or (v == 0)}
        selector.update(filtered)
    return selector


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _emit_catalog_plan(ctx: dict[str, Any], response: dict[str, Any], plan: dict[str, Any], plan_path: str | None) -> int:
    out = {**response, "ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
    if "audit" in ctx:
        ctx["audit"].write("catalog.plan", {"plan_out": plan_path, "operation": plan["selector"].get("operation")})
    ctx["out"].emit(out)
    return 0


def _emit_catalog_apply(
    ctx: dict[str, Any],
    response: dict[str, Any],
    selector: dict[str, Any],
    payload: dict[str, Any],
    plan: dict[str, Any],
    simplified: list[dict[str, Any]] | None,
    simplified_key: str | None,
) -> int:
    receipt = {
        "tool": ctx.get("tool") or "amazon-creators-api-tool",
        "version": ctx.get("tool_version"),
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str"),
        "operation": selector.get("operation"),
        "locale": selector.get("locale"),
        "marketplace": selector.get("marketplace"),
        "resources": selector.get("resources"),
        "selector": selector,
        "request": response.get("request"),
        "payload": plan.get("payload"),
        "simplified_key": simplified_key,
        "simplified_count": len(simplified or []),
        "verification": {"ok": True, "details": "Applied catalog request"},
    }
    receipt_path = None
    if ctx.get("receipt_out"):
        receipt_path = write_json_file(ctx["receipt_out"], receipt)

    out = {
        **response,
        "ok": True,
        "dry_run": False,
        "receipt": receipt,
        "receipt_out": receipt_path,
    }
    if "audit" in ctx:
        ctx["audit"].write("catalog.apply", {"receipt_out": receipt_path, "operation": selector.get("operation")})
    ctx["out"].emit(out)
    return 0


def _execute_catalog_operation(
    args: Any,
    ctx: dict[str, Any],
    operation: str,
    body: dict[str, Any],
    locale: LocaleInfo,
    simplified_builder: Callable[[dict[str, Any]], list[dict[str, Any]]],
    simplified_key: str | None,
    selector_extra: dict[str, Any] | None = None,
) -> int:
    cfg = ctx["cfg"]
    selector = _catalog_selector(operation, locale, body, selector_extra)
    plan = build_plan(ctx, selector=selector, payload=body)
    if not bool(ctx.get("apply")):
        plan_path = write_plan(ctx, plan)
        response = _build_response(args, ctx, operation, body, locale, payload=None, simplified=None, simplified_key=None)
        return _emit_catalog_plan(ctx, response, plan, plan_path)

    payload = _call_operation(cfg, ctx, operation, body, locale)
    simplified = simplified_builder(payload) if simplified_builder else None
    response = _build_response(args, ctx, operation, body, locale, payload=payload, simplified=simplified, simplified_key=simplified_key)
    return _emit_catalog_apply(ctx, response, selector, payload, plan, simplified, simplified_key)


def _simplified_search(payload: dict[str, Any]) -> list[dict[str, Any]]:
    simplified = _simplified_items(payload)
    search_result = payload.get("searchResult")
    if isinstance(search_result, dict):
        simplified = _simplified_items(search_result or {})
    return simplified


def cmd_browse_nodes(args: Any, ctx: dict[str, Any]) -> int:
    cfg = ctx["cfg"]
    locale = _resolve_locale_info(cfg, args.locale)
    resources = _resolve_resources(
        "GetBrowseNodes",
        args.resources,
        args.resource_preset,
        default_preset="browse-basic",
    )
    node_ids = _flatten_values(args.browse_node_id)
    if not node_ids:
        raise ValidationError("At least one --browse-node-id is required")
    body = {
        "resources": resources,
        "browseNodeIds": node_ids,
    }
    _decorate_body_with_marketplace(body, cfg, locale)
    return _execute_catalog_operation(
        args,
        ctx,
        "GetBrowseNodes",
        body,
        locale,
        simplified_builder=_simplified_browse_nodes,
        simplified_key="browse_nodes",
        selector_extra={"browseNodeIds": node_ids},
    )


def cmd_items(args: Any, ctx: dict[str, Any]) -> int:
    cfg = ctx["cfg"]
    locale = _resolve_locale_info(cfg, args.locale)
    resources = _resolve_resources(
        "GetItems",
        args.resources,
        args.resource_preset,
        default_preset="book-media",
    )
    item_ids = _flatten_values(args.item_id)
    if not item_ids:
        raise ValidationError("At least one --item-id is required")
    body = {
        "resources": resources,
        "itemIds": item_ids,
        "itemIdType": args.item_id_type or "ASIN",
    }
    _decorate_body_with_marketplace(body, cfg, locale)
    return _execute_catalog_operation(
        args,
        ctx,
        "GetItems",
        body,
        locale,
        simplified_builder=_simplified_items,
        simplified_key="items",
        selector_extra={
            "itemIds": item_ids,
            "itemIdType": body["itemIdType"],
        },
    )


def cmd_variations(args: Any, ctx: dict[str, Any]) -> int:
    cfg = ctx["cfg"]
    locale = _resolve_locale_info(cfg, args.locale)
    resources = _resolve_resources(
        "GetVariations",
        args.resources,
        args.resource_preset,
        default_preset="book-media",
    )
    asins = _flatten_values(args.asin)
    if not asins:
        raise ValidationError("At least one --asin is required")
    variation_count = int(getattr(args, "variation_count", 10) or 10)
    variation_page = int(getattr(args, "variation_page", 1) or 1)
    if variation_count < 1 or variation_count > 10:
        raise ValidationError("--variation-count must be between 1 and 10")
    if variation_page < 1:
        raise ValidationError("--variation-page must be >= 1")
    body = {
        "resources": resources,
        "asin": asins[0],
        "variationCount": variation_count,
        "variationPage": variation_page,
    }
    _decorate_body_with_marketplace(body, cfg, locale)
    return _execute_catalog_operation(
        args,
        ctx,
        "GetVariations",
        body,
        locale,
        simplified_builder=_simplified_items,
        simplified_key="items",
        selector_extra={
            "asin": body["asin"],
            "variationCount": body["variationCount"],
            "variationPage": body["variationPage"],
        },
    )


def cmd_search(args: Any, ctx: dict[str, Any]) -> int:
    cfg = ctx["cfg"]
    locale = _resolve_locale_info(cfg, args.locale)
    resources = _resolve_resources(
        "SearchItems",
        args.resources,
        args.resource_preset,
        default_preset="search-lens",
    )
    if not args.keywords:
        raise ValidationError("--keywords is required")
    item_count = int(getattr(args, "item_count", 10) or 10)
    item_page = int(getattr(args, "item_page", 1) or 1)
    if item_count < 1 or item_count > 10:
        raise ValidationError("--item-count must be between 1 and 10")
    if item_page < 1 or item_page > 10:
        raise ValidationError("--item-page must be between 1 and 10")
    body = {
        "resources": resources,
        "keywords": args.keywords,
        "itemCount": item_count,
        "itemPage": item_page,
    }
    _decorate_body_with_marketplace(body, cfg, locale)
    return _execute_catalog_operation(
        args,
        ctx,
        "SearchItems",
        body,
        locale,
        simplified_builder=_simplified_search,
        simplified_key="items",
        selector_extra={
            "keywords": body["keywords"],
            "itemCount": body["itemCount"],
            "itemPage": body["itemPage"],
        },
    )
