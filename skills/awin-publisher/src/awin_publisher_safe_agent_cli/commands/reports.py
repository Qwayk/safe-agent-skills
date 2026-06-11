from __future__ import annotations

from .api_helpers import build_access_token_query, build_bearer_headers
from .common import (
    bool_str,
    csv_int_query_value,
    normalize_iso_date,
    normalize_optional_str,
    normalize_timezone,
    require_token,
    request_json,
    safe_query_sent,
    validate_max_date_range_days,
)
from ..errors import ValidationError


_ADVERTISER_PATH = "/publishers/{publisher_id}/reports/advertiser"
_CAMPAIGN_PATH = "/publishers/{publisher_id}/reports/campaign"
_CREATIVE_PATH = "/publishers/{publisher_id}/reports/creative"
_DATE_TYPES = {"transaction", "validation"}
_CAMPAIGN_INTERVALS = {"day", "month", "year"}


def _base_report_params(args, *, command_name: str) -> tuple[str, dict[str, str], dict[str, object]]:
    publisher_id = str(args.publisher_id).strip()
    if not publisher_id:
        raise ValidationError("Missing --publisher-id")

    start_date = normalize_iso_date(getattr(args, "start_date", None), flag="--start-date")
    end_date = normalize_iso_date(getattr(args, "end_date", None), flag="--end-date")
    date_type = normalize_optional_str(getattr(args, "date_type", None)) or "transaction"
    if date_type not in _DATE_TYPES:
        raise ValidationError(f"Invalid --date-type for {command_name}. Use transaction or validation")

    region = str(getattr(args, "region", "") or "").strip().upper()
    if not region:
        raise ValidationError("Missing --region")
    timezone = normalize_timezone(getattr(args, "timezone", None), default="UTC")

    params = {
        "startDate": start_date,
        "endDate": end_date,
        "region": region,
        "dateType": date_type,
        "timezone": timezone,
    }
    metadata = {
        "start_date": start_date,
        "end_date": end_date,
        "region": region,
        "date_type": date_type,
        "timezone": timezone,
    }
    return publisher_id, params, metadata


def _emit_report(ctx, *, operation: str, publisher_id: str, endpoint: str, params: dict[str, str], payload: object, status_code: int, metadata: dict[str, object]) -> int:
    out = {
        "ok": True,
        "operation": operation,
        "publisher_id": publisher_id,
        "report": payload,
        "request": {
            "method": "GET",
            "endpoint": endpoint,
            "query": {
                "required": ["accessToken", "startDate", "endDate", "region", "timezone"],
                "sent": safe_query_sent(params),
            },
            "response_status": status_code,
        },
        "metadata": metadata,
    }
    ctx["audit"].write(operation, out)
    ctx["out"].emit(out)
    return 0


def cmd_reports_advertiser(args, ctx) -> int:
    cfg = ctx["cfg"]
    http = ctx["http_client"]
    token = require_token(cfg)

    publisher_id, params, metadata = _base_report_params(args, command_name="reports advertiser")
    headers = build_bearer_headers(token)
    query = build_access_token_query(token)
    query.update(params)
    payload, status_code = request_json(
        http,
        method="GET",
        url=f"{cfg.api_host}{_ADVERTISER_PATH.format(publisher_id=publisher_id)}",
        headers=headers,
        params=query,
        label="reports advertiser",
    )
    return _emit_report(
        ctx,
        operation="reports.advertiser",
        publisher_id=publisher_id,
        endpoint=f"{cfg.api_host}/publishers/{publisher_id}/reports/advertiser",
        params=params,
        payload=payload,
        status_code=status_code,
        metadata=metadata,
    )


def cmd_reports_creative(args, ctx) -> int:
    cfg = ctx["cfg"]
    http = ctx["http_client"]
    token = require_token(cfg)

    publisher_id, params, metadata = _base_report_params(args, command_name="reports creative")
    headers = build_bearer_headers(token)
    query = build_access_token_query(token)
    query.update(params)
    payload, status_code = request_json(
        http,
        method="GET",
        url=f"{cfg.api_host}{_CREATIVE_PATH.format(publisher_id=publisher_id)}",
        headers=headers,
        params=query,
        label="reports creative",
    )
    return _emit_report(
        ctx,
        operation="reports.creative",
        publisher_id=publisher_id,
        endpoint=f"{cfg.api_host}/publishers/{publisher_id}/reports/creative",
        params=params,
        payload=payload,
        status_code=status_code,
        metadata=metadata,
    )


def cmd_reports_campaign(args, ctx) -> int:
    cfg = ctx["cfg"]
    http = ctx["http_client"]
    token = require_token(cfg)

    publisher_id, params, metadata = _base_report_params(args, command_name="reports campaign")
    validate_max_date_range_days(
        start=params["startDate"],
        end=params["endDate"],
        max_days=400,
        label="campaign report date range",
        date_only=True,
    )

    advertiser_ids = csv_int_query_value(getattr(args, "advertiser_ids", None), flag="--advertiser-ids")
    if advertiser_ids:
        params["advertiserIds"] = advertiser_ids
        metadata["advertiser_ids"] = advertiser_ids.split(",")
    else:
        metadata["advertiser_ids"] = []

    campaign = normalize_optional_str(getattr(args, "campaign", None))
    if campaign:
        if len(campaign) < 3 or len(campaign) > 128:
            raise ValidationError("Invalid --campaign. Use 3 to 128 characters")
        params["campaign"] = campaign
    metadata["campaign"] = campaign

    interval = normalize_optional_str(getattr(args, "interval", None))
    if interval:
        if interval not in _CAMPAIGN_INTERVALS:
            raise ValidationError("Invalid --interval. Use day, month, or year")
        params["interval"] = interval
    metadata["interval"] = interval

    include_without_campaign = bool(getattr(args, "include_numbers_without_campaign", False))
    if include_without_campaign:
        params["includeNumbersWithoutCampaign"] = bool_str(True)
    metadata["include_numbers_without_campaign"] = include_without_campaign

    headers = build_bearer_headers(token)
    query = build_access_token_query(token)
    query.update(params)
    payload, status_code = request_json(
        http,
        method="GET",
        url=f"{cfg.api_host}{_CAMPAIGN_PATH.format(publisher_id=publisher_id)}",
        headers=headers,
        params=query,
        label="reports campaign",
    )
    return _emit_report(
        ctx,
        operation="reports.campaign",
        publisher_id=publisher_id,
        endpoint=f"{cfg.api_host}/publishers/{publisher_id}/reports/campaign",
        params=params,
        payload=payload,
        status_code=status_code,
        metadata=metadata,
    )
