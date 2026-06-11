from __future__ import annotations

from typing import Any, TypedDict

from ..sovrn_api import (
    GRANULARITY_CHOICES,
    PROPERTY_TYPE_CHOICES,
    advertising_headers,
    clean_mapping,
    emit_api_result,
    quote_path,
    require_advertising_api_key,
    resolve_advertising_publisher_id,
)


class AdvertisingEndpointSpec(TypedDict, total=False):
    path: str
    event: str
    requires_dimensions: bool
    requires_domain_name: bool


ADVERTISING_ENDPOINTS: dict[str, AdvertisingEndpointSpec] = {
    "account": {
        "path": "/reporting/advertising/publishers/{publisherId}/account",
        "event": "advertising.reports.account.get",
        "requires_dimensions": True,
    },
    "bid": {
        "path": "/reporting/advertising/publishers/{publisherId}/bid",
        "event": "advertising.reports.bid.get",
        "requires_dimensions": True,
    },
    "breakout": {
        "path": "/reporting/advertising/publishers/{publisherId}/breakout",
        "event": "advertising.reports.breakout.get",
        "requires_dimensions": False,
    },
    "domain-account": {
        "path": "/reporting/advertising/publishers/{publisherId}/domains/{domainName}/account",
        "event": "advertising.reports.domain_account.get",
        "requires_dimensions": True,
        "requires_domain_name": True,
    },
    "domain-bid": {
        "path": "/reporting/advertising/publishers/{publisherId}/domains/{domainName}/bid",
        "event": "advertising.reports.domain_bid.get",
        "requires_dimensions": True,
        "requires_domain_name": True,
    },
}


def _common_report_params(args: Any, *, include_dimensions: bool) -> dict[str, Any]:
    params = {
        "start": args.start,
        "end": args.end,
        "metrics": args.metrics,
    }
    if include_dimensions:
        params["dimensions"] = args.dimensions
    elif args.dimensions:
        params["dimensions"] = args.dimensions
    return clean_mapping(params)


def _build_report_handler(slug: str) -> Any:
    spec = ADVERTISING_ENDPOINTS[slug]

    def _handler(args: Any, ctx: dict[str, Any]) -> int:
        api_key = require_advertising_api_key(ctx["cfg"])
        publisher_id = resolve_advertising_publisher_id(args, ctx["cfg"])
        url = "https://api.sovrn.com" + spec["path"].format(
            publisherId=quote_path(publisher_id),
            domainName=quote_path(getattr(args, "domain_name", "") or ""),
        )
        return emit_api_result(
            ctx=ctx,
            event=spec["event"],
            method="GET",
            url=url,
            auth_shape="advertising-x-api-key+publisher-id",
            headers=advertising_headers(api_key),
            params=_common_report_params(args, include_dimensions=True),
        )

    return _handler


def _cmd_custom_get(args: Any, ctx: dict[str, Any]) -> int:
    api_key = require_advertising_api_key(ctx["cfg"])
    publisher_id = resolve_advertising_publisher_id(args, ctx["cfg"])
    params = clean_mapping(
        {
            "start": args.start,
            "end": args.end,
            "metrics": args.metrics,
            "dimensions": args.dimensions,
            "granularity": args.granularity,
            "domain": args.domain,
            "bundleId": args.bundle_id,
            "auction": args.auction,
            "propertyType": args.property_type,
        }
    )
    return emit_api_result(
        ctx=ctx,
        event="advertising.reports.custom.get",
        method="GET",
        url=(
            "https://api.sovrn.com/reporting/advertising/publishers/"
            f"{quote_path(publisher_id)}/"
        ),
        auth_shape="advertising-x-api-key+publisher-id",
        headers=advertising_headers(api_key),
        params=params,
    )


def register_advertising_parser(subparsers: Any) -> None:
    advertising = subparsers.add_parser("advertising", help="Official Sovrn Advertising Reporting APIs")
    advertising_sub = advertising.add_subparsers(dest="advertising_cmd", required=True, parser_class=type(advertising))

    reports = advertising_sub.add_parser("reports", help="Advertising reporting endpoints")
    reports_sub = reports.add_subparsers(dest="advertising_reports_cmd", required=True, parser_class=type(reports))

    for slug, spec in ADVERTISING_ENDPOINTS.items():
        parser = reports_sub.add_parser(slug, help=f"{slug.replace('-', ' ').title()} reporting")
        parser_sub = parser.add_subparsers(dest=f"advertising_reports_{slug.replace('-', '_')}_cmd", required=True, parser_class=type(parser))
        get = parser_sub.add_parser("get", help=f"Query the {slug.replace('-', ' ')} report")
        get.add_argument("--publisher-id", default=None, help="Override the configured publisher ID")
        if spec.get("requires_domain_name"):
            get.add_argument("--domain-name", required=True, help="Domain name path value")
        get.add_argument("--start", required=True, help="Inclusive start time in ISO-8601 UTC")
        get.add_argument("--end", required=True, help="Exclusive end time in ISO-8601 UTC")
        get.add_argument("--metrics", required=True, help="Comma-separated metrics list")
        if spec.get("requires_dimensions", True):
            get.add_argument("--dimensions", required=True, help="Comma-separated dimensions list")
        else:
            get.add_argument("--dimensions", default=None, help="Optional comma-separated dimensions list")
        get.set_defaults(func=_build_report_handler(slug), write_capable=False)

    custom = reports_sub.add_parser("custom", help="Custom advertising reporting")
    custom_sub = custom.add_subparsers(dest="advertising_reports_custom_cmd", required=True, parser_class=type(custom))
    custom_get = custom_sub.add_parser("get", help="Query the custom reporting endpoint")
    custom_get.add_argument("--publisher-id", default=None, help="Override the configured publisher ID")
    custom_get.add_argument("--start", required=True, help="Inclusive start time in ISO-8601 UTC")
    custom_get.add_argument("--end", required=True, help="Exclusive end time in ISO-8601 UTC")
    custom_get.add_argument("--metrics", required=True, help="Comma-separated metrics list")
    custom_get.add_argument("--dimensions", required=True, help="Comma-separated dimensions list")
    custom_get.add_argument("--granularity", required=True, choices=GRANULARITY_CHOICES)
    custom_get.add_argument("--domain", default=None, help="Comma-separated domains filter")
    custom_get.add_argument("--bundle-id", default=None, help="Comma-separated bundle IDs filter")
    custom_get.add_argument("--auction", default=None, help="Comma-separated auction types filter")
    custom_get.add_argument("--property-type", default=None, choices=PROPERTY_TYPE_CHOICES)
    custom_get.set_defaults(func=_cmd_custom_get, write_capable=False)
