from __future__ import annotations

import argparse
from typing import Any

from ..errors import ValidationError
from ..sovrn_api import (
    DEVICE_TYPE_CHOICES,
    MARKET_CHOICES,
    PROGRAM_TYPE_CHOICES,
    SOVRN_PRODUCT_CHOICES,
    bool_to_query,
    clean_mapping,
    commerce_secret_headers,
    emit_api_result,
    join_csv_values,
    quote_path,
    read_text_file,
    require_commerce_secret_key,
    require_commerce_site_api_key,
    require_one_of,
)

COMMERCE_REPORT_ENDPOINTS = {
    "pages": "https://viglink.io/v1/reports/pages",
    "links": "https://viglink.io/v1/reports/links",
    "merchants": "https://viglink.io/v1/reports/merchants",
    "merchants-by-date": "https://viglink.io/v1/reports/merchantsbydate",
    "merchandise": "https://viglink.io/v1/reports/merchandise",
    "networks": "https://viglink.io/v1/reports/networks",
    "cuids": "https://viglink.io/v1/reports/cuids",
}

APPROVED_MERCHANT_FILTERS = (
    ("name", "NAME"),
    ("group_id", "GROUP_ID"),
    ("domain", "DOMAIN"),
    ("geo", "GEO"),
    ("program_type_filter", "PROGRAM_TYPE"),
    ("category", "CATEGORY"),
)


def _add_common_report_filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--campaign-ids", default=None, help="Comma-separated campaign IDs")
    parser.add_argument("--sub-ids", default=None, help="Comma-separated sub IDs")
    parser.add_argument("--merchant-group-ids", default=None, help="Comma-separated merchant group IDs")
    parser.add_argument("--cuids", default=None, help="Comma-separated custom tracking IDs")
    parser.add_argument("--page-utm-source", default=None)
    parser.add_argument("--page-utm-medium", default=None)
    parser.add_argument("--page-utm-campaign", default=None)
    parser.add_argument("--page-utm-term", default=None)
    parser.add_argument("--page-utm-content", default=None)
    parser.add_argument("--link-utm-source", default=None)
    parser.add_argument("--link-utm-medium", default=None)
    parser.add_argument("--link-utm-campaign", default=None)
    parser.add_argument("--link-utm-term", default=None)
    parser.add_argument("--link-utm-content", default=None)
    parser.add_argument("--program-type", choices=PROGRAM_TYPE_CHOICES, default=None)
    parser.add_argument("--sovrn-product", choices=SOVRN_PRODUCT_CHOICES, default=None)
    parser.add_argument("--device-type", choices=DEVICE_TYPE_CHOICES, default=None)
    parser.add_argument("--country", default=None, help="Two-letter ISO country code")


def _common_report_params(args: argparse.Namespace) -> dict[str, Any]:
    return clean_mapping(
        {
            "clickDateStart": args.click_date_start,
            "clickDateEnd": args.click_date_end,
            "campaignIds": args.campaign_ids,
            "subIds": args.sub_ids,
            "merchantGroupIds": args.merchant_group_ids,
            "cuids": args.cuids,
            "pageUtmSource": args.page_utm_source,
            "pageUtmMedium": args.page_utm_medium,
            "pageUtmCampaign": args.page_utm_campaign,
            "pageUtmTerm": args.page_utm_term,
            "pageUtmContent": args.page_utm_content,
            "linkUtmSource": args.link_utm_source,
            "linkUtmMedium": args.link_utm_medium,
            "linkUtmCampaign": args.link_utm_campaign,
            "linkUtmTerm": args.link_utm_term,
            "linkUtmContent": args.link_utm_content,
            "programType": args.program_type,
            "sovrnProduct": args.sovrn_product,
            "deviceType": args.device_type,
            "country": args.country,
        }
    )


def _cmd_campaigns_get(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    secret_key = require_commerce_secret_key(ctx["cfg"])
    search = str(getattr(args, "search", "PRIMARY") or "PRIMARY").strip() or "PRIMARY"
    params = clean_mapping(
        {
            "format": args.format,
            "callback": args.callback,
            "rowsPerPage": args.rows_per_page,
            "page": args.page,
        }
    )
    return emit_api_result(
        ctx=ctx,
        event="commerce.campaigns.get",
        method="GET",
        url=f"https://rest.viglink.com/api/account/campaigns/{quote_path(search)}",
        auth_shape="commerce-secret-header",
        headers=commerce_secret_headers(secret_key),
        params=params,
    )


def _cmd_links_check(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    site_key = require_commerce_site_api_key(ctx["cfg"])
    params = clean_mapping(
        {
            "out": args.url,
            "key": site_key,
            "optimize": bool_to_query(args.optimize),
            "format": args.format,
            "geo": args.geo,
            "fbu": args.fbu,
            "bf": args.bf,
        }
    )
    return emit_api_result(
        ctx=ctx,
        event="commerce.links.check",
        method="GET",
        url="https://api.viglink.com/api/link/",
        auth_shape="commerce-site-api-key-query",
        params=params,
        notes=["This endpoint uses the site API key query parameter, not the Commerce secret header."],
    )


def _cmd_links_bid_check(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    site_key = require_commerce_site_api_key(ctx["cfg"])
    params = clean_mapping(
        {
            "key": site_key,
            "out": args.url,
            "ip": args.user_ip,
            "userAgent": args.user_agent,
            "referrerUrl": args.referrer_url,
            "subId": args.sub_id,
            "bidFloor": args.bid_floor,
            "includeCpa": bool_to_query(args.include_cpa),
            "gdprApplies": bool_to_query(args.gdpr_applies),
            "gdprConsent": args.gdpr_consent,
            "ccpaConsent": args.ccpa_consent,
            "gppConsent": args.gpp_consent,
            "cuid": args.cuid,
            "utm_source": args.utm_source,
            "utm_medium": args.utm_medium,
            "utm_campaign": args.utm_campaign,
            "utm_term": args.utm_term,
            "utm_content": args.utm_content,
        }
    )
    return emit_api_result(
        ctx=ctx,
        event="commerce.links.bid_check",
        method="GET",
        url="https://api.viglink.com/api/bid",
        auth_shape="commerce-site-api-key-query",
        params=params,
        notes=[
            "Bid Check requires the real end-user IP and user agent.",
            "Do not follow the returned redirect URL server-side.",
        ],
    )


def _cmd_transactions_get(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    secret_key = require_commerce_secret_key(ctx["cfg"])
    params = clean_mapping(
        {
            "clickDate": args.click_date,
            "commissionDate": args.commission_date,
            "updateDate": args.update_date,
            "campaignIds": args.campaign_ids,
            "merchantGroupIds": args.merchant_group_ids,
            "programType": args.program_type,
        }
    )
    return emit_api_result(
        ctx=ctx,
        event="commerce.reports.transactions.get",
        method="GET",
        url="https://viglink.io/v1/reports/transactions",
        auth_shape="commerce-secret-header",
        headers=commerce_secret_headers(secret_key),
        params=params,
    )


def _build_common_report_handler(report_slug: str) -> Any:
    def _handler(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
        secret_key = require_commerce_secret_key(ctx["cfg"])
        return emit_api_result(
            ctx=ctx,
            event=f"commerce.reports.{report_slug.replace('-', '_')}.get",
            method="GET",
            url=COMMERCE_REPORT_ENDPOINTS[report_slug],
            auth_shape="commerce-secret-header",
            headers=commerce_secret_headers(secret_key),
            params=_common_report_params(args),
        )

    return _handler


def _merchant_group_filters(args: argparse.Namespace) -> list[dict[str, Any]]:
    filters: list[dict[str, Any]] = []
    for attr_name, filter_type in APPROVED_MERCHANT_FILTERS:
        values = join_csv_values(getattr(args, attr_name))
        if values is None:
            continue
        filter_values = [item.strip() for item in values.split(",") if item.strip()]
        filters.append({"type": filter_type, "values": filter_values})
    return filters


def _cmd_merchant_groups_approved(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    secret_key = require_commerce_secret_key(ctx["cfg"])
    body = {
        "filters": _merchant_group_filters(args),
        "page": args.page,
        "pageSize": args.page_size,
    }
    return emit_api_result(
        ctx=ctx,
        event="commerce.merchant_groups.approved",
        method="POST",
        url="https://viglink.io/merchants/rates/summaries",
        auth_shape="commerce-secret-header",
        headers=commerce_secret_headers(secret_key),
        params={"campaignId": args.campaign_id},
        json_body=body,
    )


def _cmd_merchant_groups_delta(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    secret_key = require_commerce_secret_key(ctx["cfg"])
    if not args.since and not args.if_none_match:
        raise ValidationError("Pass --since or --if-none-match for the merchant delta command")
    headers = commerce_secret_headers(secret_key)
    if args.if_none_match:
        headers["If-None-Match"] = args.if_none_match
    params = clean_mapping(
        {
            "campaignId": args.campaign_id,
            "page": args.page,
            "pageSize": args.page_size,
            "since": args.since,
        }
    )
    return emit_api_result(
        ctx=ctx,
        event="commerce.merchant_groups.delta",
        method="GET",
        url="https://viglink.io/merchants/rates/summaries/delta",
        auth_shape="commerce-secret-header",
        headers=headers,
        params=params,
    )


def _cmd_coupons_product_get(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    secret_key = require_commerce_secret_key(ctx["cfg"])
    site_key = require_commerce_site_api_key(ctx["cfg"])
    params = clean_mapping(
        {
            "api_key": site_key,
            "product_url": args.product_url,
            "include_unverified": None if args.verified_only else None,
            "cuid": args.cuid,
            "utm_source": args.utm_source,
            "utm_medium": args.utm_medium,
            "utm_campaign": args.utm_campaign,
            "utm_term": args.utm_term,
            "utm_content": args.utm_content,
        }
    )
    if args.verified_only:
        params["include_unverified"] = "false"
    return emit_api_result(
        ctx=ctx,
        event="commerce.coupons.product.get",
        method="GET",
        url="https://viglink.io/coupons/product",
        auth_shape="commerce-secret-header+commerce-site-api-key-query",
        headers=commerce_secret_headers(secret_key),
        params=params,
        notes=["This official endpoint is access-gated. Sovrn registration is required before it will work."],
    )


def _cmd_products_recommend(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    site_key = require_commerce_site_api_key(ctx["cfg"])
    if bool(args.content) == bool(args.content_file):
        raise ValidationError("Pass exactly one of --content or --content-file")
    if args.include_merchants and args.exclude_merchants:
        raise ValidationError("Use only one of --include-merchants or --exclude-merchants")
    content = args.content if args.content else read_text_file(args.content_file)
    params = clean_mapping(
        {
            "apiKey": site_key,
            "market": args.market,
            "cuid": args.cuid,
            "priceRange": args.price_range,
            "includeMerchants": args.include_merchants,
            "excludeMerchants": args.exclude_merchants,
            "numProducts": args.num_products,
            "pageUrl": args.page_url,
        }
    )
    body = clean_mapping({"title": args.title, "content": content})
    return emit_api_result(
        ctx=ctx,
        event="commerce.products.recommend",
        method="POST",
        url="https://shopping-gallery.prd-commerce.sovrnservices.com/ai-orchestration/products",
        auth_shape="commerce-site-api-key-query",
        params=params,
        json_body=body,
    )


def _cmd_comparisons_prices_search(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    secret_key = require_commerce_secret_key(ctx["cfg"])
    site_key = require_commerce_site_api_key(ctx["cfg"])
    require_one_of(
        names=("barcode", "plainlink", "search_keywords"),
        values=(args.barcode, args.plainlink, args.search_keywords),
        message="Pass at least one of --barcode, --plainlink, or --search-keywords",
    )
    params = clean_mapping(
        {
            "barcode": args.barcode,
            "plainlink": args.plainlink,
            "search-keywords": args.search_keywords,
            "exclude-keywords": args.exclude_keywords,
            "price-range": args.price_range,
            "limit": args.limit,
            "sid": args.sid,
            "epc-sort": bool_to_query(args.epc_sort),
        }
    )
    return emit_api_result(
        ctx=ctx,
        event="commerce.comparisons.prices.search",
        method="GET",
        url=(
            "https://comparisons.sovrn.com/api/affiliate/v3.5/"
            f"sites/{quote_path(site_key)}/compare/prices/{quote_path(args.market)}/by/accuracy"
        ),
        auth_shape="commerce-secret-header+commerce-site-api-key-path",
        headers=commerce_secret_headers(secret_key),
        params=params,
    )


def register_commerce_parser(subparsers: Any) -> None:
    commerce = subparsers.add_parser("commerce", help="Official Sovrn Commerce HTTP APIs")
    commerce_sub = commerce.add_subparsers(dest="commerce_cmd", required=True, parser_class=type(commerce))

    campaigns = commerce_sub.add_parser("campaigns", help="Campaign discovery")
    campaigns_sub = campaigns.add_subparsers(dest="commerce_campaigns_cmd", required=True, parser_class=type(campaigns))
    campaigns_get = campaigns_sub.add_parser("get", help="List campaigns or search by campaign name or ID")
    campaigns_get.add_argument("--search", default="PRIMARY", help="Campaign name or campaign ID (default: PRIMARY)")
    campaigns_get.add_argument("--format", choices=("json", "xml"), default=None)
    campaigns_get.add_argument("--callback", default=None)
    campaigns_get.add_argument("--rows-per-page", type=int, default=None)
    campaigns_get.add_argument("--page", type=int, default=None)
    campaigns_get.set_defaults(func=_cmd_campaigns_get, write_capable=False)

    links = commerce_sub.add_parser("links", help="Link and bid tools")
    links_sub = links.add_subparsers(dest="commerce_links_cmd", required=True, parser_class=type(links))
    links_check = links_sub.add_parser("check", help="Check whether a URL can be monetized")
    links_check.add_argument("--url", required=True, help="Destination URL to check")
    links_check.add_argument("--optimize", action=argparse.BooleanOptionalAction, default=None)
    links_check.add_argument("--format", default=None)
    links_check.add_argument("--geo", default=None)
    links_check.add_argument("--fbu", default=None)
    links_check.add_argument("--bf", default=None)
    links_check.set_defaults(func=_cmd_links_check, write_capable=False)

    links_bid = links_sub.add_parser("bid-check", help="Get a real-time bid for a click")
    links_bid.add_argument("--url", required=True, help="Destination URL for the click")
    links_bid.add_argument("--user-ip", required=True, help="Real end-user IP address")
    links_bid.add_argument("--user-agent", required=True, help="Real end-user browser User-Agent")
    links_bid.add_argument("--referrer-url", default=None)
    links_bid.add_argument("--sub-id", default=None, help="Fully qualified SubID URL")
    links_bid.add_argument("--bid-floor", type=float, default=None)
    links_bid.add_argument("--include-cpa", action=argparse.BooleanOptionalAction, default=None)
    links_bid.add_argument("--gdpr-applies", action=argparse.BooleanOptionalAction, default=None)
    links_bid.add_argument("--gdpr-consent", default=None)
    links_bid.add_argument("--ccpa-consent", default=None)
    links_bid.add_argument("--gpp-consent", default=None)
    links_bid.add_argument("--cuid", default=None)
    links_bid.add_argument("--utm-source", default=None)
    links_bid.add_argument("--utm-medium", default=None)
    links_bid.add_argument("--utm-campaign", default=None)
    links_bid.add_argument("--utm-term", default=None)
    links_bid.add_argument("--utm-content", default=None)
    links_bid.set_defaults(func=_cmd_links_bid_check, write_capable=False)

    reports = commerce_sub.add_parser("reports", help="Commerce reporting endpoints")
    reports_sub = reports.add_subparsers(dest="commerce_reports_cmd", required=True, parser_class=type(reports))
    transactions = reports_sub.add_parser("transactions", help="Transaction-level commission events")
    transactions_sub = transactions.add_subparsers(dest="commerce_reports_transactions_cmd", required=True, parser_class=type(transactions))
    transactions_get = transactions_sub.add_parser("get", help="Query transaction report rows")
    transactions_get.add_argument("--click-date", default=None, help="Exact click date in YYYY-MM-DD")
    transactions_get.add_argument("--commission-date", default=None, help="Exact commission date in YYYY-MM-DD")
    transactions_get.add_argument("--update-date", default=None, help="Exact update date in YYYY-MM-DD")
    transactions_get.add_argument("--campaign-ids", default=None)
    transactions_get.add_argument("--merchant-group-ids", default=None)
    transactions_get.add_argument("--program-type", choices=PROGRAM_TYPE_CHOICES, default=None)
    transactions_get.set_defaults(func=_cmd_transactions_get, write_capable=False)

    for slug, handler in ((slug, _build_common_report_handler(slug)) for slug in COMMERCE_REPORT_ENDPOINTS):
        report = reports_sub.add_parser(slug, help=f"{slug.replace('-', ' ').title()} report")
        report_sub = report.add_subparsers(dest=f"commerce_reports_{slug.replace('-', '_')}_cmd", required=True, parser_class=type(report))
        report_get = report_sub.add_parser("get", help=f"Query the {slug.replace('-', ' ')} report")
        report_get.add_argument("--click-date-start", required=True, help="Start date in YYYY-MM-DD")
        report_get.add_argument("--click-date-end", required=True, help="Exclusive end date in YYYY-MM-DD")
        _add_common_report_filters(report_get)
        report_get.set_defaults(func=handler, write_capable=False)

    merchant_groups = commerce_sub.add_parser("merchant-groups", help="Approved merchant and delta endpoints")
    merchant_groups_sub = merchant_groups.add_subparsers(dest="commerce_merchant_groups_cmd", required=True, parser_class=type(merchant_groups))
    approved = merchant_groups_sub.add_parser("approved", help="Retrieve approved merchants")
    approved.add_argument("--campaign-id", required=True, type=int)
    approved.add_argument("--name", action="append", default=None, help="Merchant name filter; repeat or use commas")
    approved.add_argument("--group-id", action="append", default=None, dest="group_id", help="Merchant group ID filter; repeat or use commas")
    approved.add_argument("--domain", action="append", default=None, help="Merchant domain filter; repeat or use commas")
    approved.add_argument("--geo", action="append", default=None, help="Lower-case ISO country code filter; repeat or use commas")
    approved.add_argument("--program-type-filter", action="append", default=None, choices=PROGRAM_TYPE_CHOICES, help="Approved merchant program type filter")
    approved.add_argument("--category", action="append", default=None, help="Sovrn category code filter; repeat or use commas")
    approved.add_argument("--page", type=int, default=1)
    approved.add_argument("--page-size", type=int, default=1000)
    approved.set_defaults(func=_cmd_merchant_groups_approved, write_capable=False)

    delta = merchant_groups_sub.add_parser("delta", help="Retrieve merchant changes since a timestamp or ETag")
    delta.add_argument("--campaign-id", required=True, type=int)
    delta.add_argument("--page", type=int, default=None)
    delta.add_argument("--page-size", type=int, default=None)
    delta.add_argument("--since", default=None, help="ISO timestamp")
    delta.add_argument("--if-none-match", default=None, help="ETag value from a previous response")
    delta.set_defaults(func=_cmd_merchant_groups_delta, write_capable=False)

    coupons = commerce_sub.add_parser("coupons", help="Product promo code endpoint")
    coupons_sub = coupons.add_subparsers(dest="commerce_coupons_cmd", required=True, parser_class=type(coupons))
    product = coupons_sub.add_parser("product", help="Product-specific promo codes")
    product_sub = product.add_subparsers(dest="commerce_coupons_product_cmd", required=True, parser_class=type(product))
    product_get = product_sub.add_parser("get", help="Get product-specific promo codes")
    product_get.add_argument("--product-url", required=True, help="Canonical retailer product URL")
    product_get.add_argument("--verified-only", action="store_true", help="Exclude unverified codes")
    product_get.add_argument("--cuid", default=None)
    product_get.add_argument("--utm-source", default=None)
    product_get.add_argument("--utm-medium", default=None)
    product_get.add_argument("--utm-campaign", default=None)
    product_get.add_argument("--utm-term", default=None)
    product_get.add_argument("--utm-content", default=None)
    product_get.set_defaults(func=_cmd_coupons_product_get, write_capable=False)

    products = commerce_sub.add_parser("products", help="Product recommendation APIs")
    products_sub = products.add_subparsers(dest="commerce_products_cmd", required=True, parser_class=type(products))
    recommend = products_sub.add_parser("recommend", help="Generate product recommendations from content")
    recommend.add_argument("--page-url", required=True, help="Stable page URL or cache key")
    recommend.add_argument("--content", default=None, help="Inline content string")
    recommend.add_argument("--content-file", default=None, help="Text or HTML file to send as content")
    recommend.add_argument("--title", default=None)
    recommend.add_argument("--market", choices=MARKET_CHOICES, default=None)
    recommend.add_argument("--cuid", default=None)
    recommend.add_argument("--price-range", default=None)
    recommend.add_argument("--include-merchants", default=None, help="Comma-separated merchant IDs")
    recommend.add_argument("--exclude-merchants", default=None, help="Comma-separated merchant IDs")
    recommend.add_argument("--num-products", type=int, default=None)
    recommend.set_defaults(func=_cmd_products_recommend, write_capable=False)

    comparisons = commerce_sub.add_parser("comparisons", help="Price comparison search")
    comparisons_sub = comparisons.add_subparsers(dest="commerce_comparisons_cmd", required=True, parser_class=type(comparisons))
    prices = comparisons_sub.add_parser("prices", help="Compare prices across merchants")
    prices_sub = prices.add_subparsers(dest="commerce_comparisons_prices_cmd", required=True, parser_class=type(prices))
    search = prices_sub.add_parser("search", help="Find alternative merchants and prices")
    search.add_argument("--market", required=True, choices=MARKET_CHOICES)
    search.add_argument("--barcode", default=None)
    search.add_argument("--plainlink", default=None)
    search.add_argument("--search-keywords", default=None)
    search.add_argument("--exclude-keywords", default=None)
    search.add_argument("--price-range", default=None)
    search.add_argument("--limit", type=int, default=None)
    search.add_argument("--sid", default=None, help="Sovrn CUID / source ID")
    search.add_argument("--epc-sort", action=argparse.BooleanOptionalAction, default=None)
    search.set_defaults(func=_cmd_comparisons_prices_search, write_capable=False)
