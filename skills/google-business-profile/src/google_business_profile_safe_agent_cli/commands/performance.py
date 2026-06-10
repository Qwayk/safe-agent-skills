from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from .business_info import _client_for_ctx, _emit, _require_resource


def _normalize_int(value: object, *, arg_name: str) -> int:
    text = str(value or "").strip()
    if not text:
        raise ValidationError(f"{arg_name} is required and must not be blank.")
    try:
        return int(text)
    except ValueError as exc:
        raise ValidationError(f"{arg_name} must be an integer: {text}") from exc


def _normalize_daily_metrics(values: list[str] | None, *, arg_name: str) -> list[str]:
    metrics = [str(v).strip() for v in values or [] if str(v).strip()]
    if not metrics:
        raise ValidationError(f"{arg_name} is required and must include at least one value.")
    return metrics


def cmd_locations_fetch_multi_daily_metrics_time_series(args: Any, ctx: dict[str, Any]) -> int:
    location = _require_resource(args.location, arg_name="--location")
    daily_metrics = _normalize_daily_metrics(args.daily_metrics, arg_name="--daily-metrics")
    client = _client_for_ctx(ctx)

    response, request = client.fetch_multi_daily_metrics_time_series(
        location=location,
        daily_metrics=daily_metrics,
        daily_range_start_year=_normalize_int(args.daily_range_start_year, arg_name="--daily-range-start-year"),
        daily_range_start_month=_normalize_int(args.daily_range_start_month, arg_name="--daily-range-start-month"),
        daily_range_start_day=_normalize_int(args.daily_range_start_day, arg_name="--daily-range-start-day"),
        daily_range_end_year=_normalize_int(args.daily_range_end_year, arg_name="--daily-range-end-year"),
        daily_range_end_month=_normalize_int(args.daily_range_end_month, arg_name="--daily-range-end-month"),
        daily_range_end_day=_normalize_int(args.daily_range_end_day, arg_name="--daily-range-end-day"),
    )
    return _emit(ctx, "performance.locations.fetch-multi-daily-metrics-time-series", request, response)


def cmd_locations_get_daily_metrics_time_series(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")
    daily_metric = _require_resource(args.daily_metric, arg_name="--daily-metric")
    client = _client_for_ctx(ctx)

    response, request = client.get_daily_metrics_time_series(
        name=name,
        daily_metric=daily_metric,
        daily_range_start_year=_normalize_int(args.daily_range_start_year, arg_name="--daily-range-start-year"),
        daily_range_start_month=_normalize_int(args.daily_range_start_month, arg_name="--daily-range-start-month"),
        daily_range_start_day=_normalize_int(args.daily_range_start_day, arg_name="--daily-range-start-day"),
        daily_range_end_year=_normalize_int(args.daily_range_end_year, arg_name="--daily-range-end-year"),
        daily_range_end_month=_normalize_int(args.daily_range_end_month, arg_name="--daily-range-end-month"),
        daily_range_end_day=_normalize_int(args.daily_range_end_day, arg_name="--daily-range-end-day"),
    )
    return _emit(ctx, "performance.locations.get-daily-metrics-time-series", request, response)


def cmd_locations_search_keywords_impressions_monthly_list(args: Any, ctx: dict[str, Any]) -> int:
    parent = _require_resource(args.parent, arg_name="--parent")
    client = _client_for_ctx(ctx)

    response, request = client.list_search_keywords_impressions_monthly(
        parent=parent,
        monthly_range_start_year=_normalize_int(args.monthly_range_start_year, arg_name="--monthly-range-start-year"),
        monthly_range_start_month=_normalize_int(args.monthly_range_start_month, arg_name="--monthly-range-start-month"),
        monthly_range_end_year=_normalize_int(args.monthly_range_end_year, arg_name="--monthly-range-end-year"),
        monthly_range_end_month=_normalize_int(args.monthly_range_end_month, arg_name="--monthly-range-end-month"),
        page_size=args.page_size,
        page_token=str(args.page_token).strip() or None,
    )
    return _emit(ctx, "performance.locations.search-keywords.impressions.monthly.list", request, response)
