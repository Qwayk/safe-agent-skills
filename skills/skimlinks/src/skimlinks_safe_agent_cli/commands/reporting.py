from __future__ import annotations

from typing import Any

from ..skimlinks import SkimlinksClient, clean_params, make_http_client, require_publisher_id


def _client(ctx: dict[str, Any]) -> SkimlinksClient:
    return SkimlinksClient(cfg=ctx["cfg"], http=make_http_client(ctx))


def _emit(ctx: dict[str, Any], event: str, out: dict[str, Any]) -> int:
    ctx["audit"].write(event, {"ok": out.get("ok"), "path": out.get("path"), "params": out.get("params")})
    ctx["out"].emit(out)
    return 0


def _params(args: Any, names: list[str]) -> dict[str, Any]:
    return clean_params({name: getattr(args, name, None) for name in names})


def _publisher(args: Any, ctx: dict[str, Any]) -> str:
    return require_publisher_id(ctx["cfg"], getattr(args, "publisher_id", None))


def cmd_commissions_search(args: Any, ctx: dict[str, Any]) -> int:
    params = _params(
        args,
        [
            "limit",
            "offset",
            "start_date",
            "end_date",
            "updated_since",
            "custom_id",
            "merchant_id",
            "a_id",
            "domain_id",
            "sort_dir",
            "sort_by",
            "commission_id",
            "status",
            "commission_type",
        ],
    )
    out = _client(ctx).get_json(
        base_url=ctx["cfg"].reporting_base_url,
        path=f"/publisher/{_publisher(args, ctx)}/commission-report",
        params=params,
    )
    out.update({"family": "reporting", "operation": "commissions.search"})
    return _emit(ctx, "reporting.commissions.search", out)


def cmd_aggregated_get(args: Any, ctx: dict[str, Any]) -> int:
    params = _params(
        args,
        [
            "report_by",
            "start_date",
            "end_date",
            "limit",
            "offset",
            "sort_by",
            "sort_dir",
            "time_period",
            "currency",
            "user_country",
            "user_ip_countries",
            "device_type",
            "a_id",
            "domain_id",
            "page_search",
            "link_search",
            "merchant_search",
        ],
    )
    out = _client(ctx).get_json(
        base_url=ctx["cfg"].reporting_base_url,
        path=f"/publisher/{_publisher(args, ctx)}/reports",
        params=params,
    )
    out.update({"family": "reporting", "operation": "aggregated.get"})
    return _emit(ctx, "reporting.aggregated.get", out)


def cmd_link_report_query(args: Any, ctx: dict[str, Any]) -> int:
    params = _params(args, ["start_date", "end_date", "limit", "offset", "dim", "met", "currency"])
    out = _client(ctx).get_ndjson(
        base_url=ctx["cfg"].reporting_base_url,
        path=f"/publisher/{_publisher(args, ctx)}/aggregation/v1/link-report",
        params=params,
    )
    out.update({"family": "reporting", "operation": "link_report.query"})
    return _emit(ctx, "reporting.link_report.query", out)


def cmd_link_report_dimensions(args: Any, ctx: dict[str, Any]) -> int:
    out = _client(ctx).get_json(
        base_url=ctx["cfg"].reporting_base_url,
        path=f"/publisher/{_publisher(args, ctx)}/aggregation/v1/link-report/dimensions",
        params={},
    )
    out.update({"family": "reporting", "operation": "link_report.dimensions"})
    return _emit(ctx, "reporting.link_report.dimensions", out)


def cmd_link_report_metrics(args: Any, ctx: dict[str, Any]) -> int:
    out = _client(ctx).get_json(
        base_url=ctx["cfg"].reporting_base_url,
        path=f"/publisher/{_publisher(args, ctx)}/aggregation/v1/link-report/metrics",
        params={},
    )
    out.update({"family": "reporting", "operation": "link_report.metrics"})
    return _emit(ctx, "reporting.link_report.metrics", out)


def cmd_page_report_query(args: Any, ctx: dict[str, Any]) -> int:
    params = _params(args, ["start_date", "end_date", "limit", "offset", "dim", "met", "currency"])
    out = _client(ctx).get_ndjson(
        base_url=ctx["cfg"].reporting_base_url,
        path=f"/publisher/{_publisher(args, ctx)}/aggregation/v1/page-report",
        params=params,
    )
    out.update({"family": "reporting", "operation": "page_report.query"})
    return _emit(ctx, "reporting.page_report.query", out)


def cmd_page_report_dimensions(args: Any, ctx: dict[str, Any]) -> int:
    out = _client(ctx).get_json(
        base_url=ctx["cfg"].reporting_base_url,
        path=f"/publisher/{_publisher(args, ctx)}/aggregation/v1/page-report/dimensions",
        params={},
    )
    out.update({"family": "reporting", "operation": "page_report.dimensions"})
    return _emit(ctx, "reporting.page_report.dimensions", out)


def cmd_page_report_metrics(args: Any, ctx: dict[str, Any]) -> int:
    out = _client(ctx).get_json(
        base_url=ctx["cfg"].reporting_base_url,
        path=f"/publisher/{_publisher(args, ctx)}/aggregation/v1/page-report/metrics",
        params={},
    )
    out.update({"family": "reporting", "operation": "page_report.metrics"})
    return _emit(ctx, "reporting.page_report.metrics", out)


def cmd_trending_products_get(args: Any, ctx: dict[str, Any]) -> int:
    params = _params(
        args,
        [
            "period",
            "sort_by",
            "sort_dir",
            "a_id",
            "country_code",
            "audience_country_code",
            "vertical_id",
            "product_search",
            "limit",
            "offset",
        ],
    )
    out = _client(ctx).get_json(
        base_url=ctx["cfg"].reporting_base_url,
        path=f"/publisher/{_publisher(args, ctx)}/trending-products",
        params=params,
    )
    out.update({"family": "reporting", "operation": "trending_products.get"})
    return _emit(ctx, "reporting.trending_products.get", out)


def cmd_product_report_get(args: Any, ctx: dict[str, Any]) -> int:
    params = _params(
        args,
        [
            "start_date",
            "end_date",
            "limit",
            "offset",
            "sort_by",
            "sort_dir",
            "currency",
            "product_search",
            "domain_id",
        ],
    )
    out = _client(ctx).get_json(
        base_url=ctx["cfg"].reporting_base_url,
        path=f"/publisher/{_publisher(args, ctx)}/product-report",
        params=params,
    )
    out.update({"family": "reporting", "operation": "product_report.get"})
    return _emit(ctx, "reporting.product_report.get", out)


def cmd_payment_status_get(args: Any, ctx: dict[str, Any]) -> int:
    params = _params(
        args,
        [
            "start_date",
            "end_date",
            "limit",
            "offset",
            "sort_by",
            "sort_dir",
            "invoice_id",
            "payment_status",
            "payment_type",
            "saas_fee",
        ],
    )
    out = _client(ctx).get_json(
        base_url=ctx["cfg"].reporting_base_url,
        path=f"/publisher/{_publisher(args, ctx)}/payment-status",
        params=params,
    )
    out.update({"family": "reporting", "operation": "payment_status.get"})
    return _emit(ctx, "reporting.payment_status.get", out)


def cmd_deactivated_merchants_get(args: Any, ctx: dict[str, Any]) -> int:
    params = _params(
        args,
        [
            "sort_by",
            "sort_dir",
            "limit",
            "offset",
            "min_publisher_combined_commission_amount",
            "domain_id",
            "currency",
            "timezone",
        ],
    )
    out = _client(ctx).get_json(
        base_url=ctx["cfg"].reporting_base_url,
        path=f"/publisher/{_publisher(args, ctx)}/deactivated-merchants",
        params=params,
    )
    out.update({"family": "reporting", "operation": "deactivated_merchants.get"})
    return _emit(ctx, "reporting.deactivated_merchants.get", out)
