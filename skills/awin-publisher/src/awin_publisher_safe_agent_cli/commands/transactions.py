from __future__ import annotations

from .api_helpers import build_access_token_query, build_bearer_headers
from .common import (
    bool_str,
    csv_int_query_value,
    normalize_iso_datetime,
    normalize_optional_str,
    normalize_timezone,
    require_token,
    request_json,
    safe_query_sent,
    validate_max_date_range_days,
)
from ..errors import ValidationError


_TRANSACTIONS_LIST_PATH = "/publishers/{publisher_id}/transactions/"
_TRANSACTIONS_BY_IDS_PATH = "/publishers/{publisher_id}/transactions"
_LIST_DATE_TYPES = {"transaction", "validation", "amendment"}
_STATUS_VALUES = {"pending", "approved", "declined", "deleted"}


def _base_params(args) -> tuple[dict[str, str], dict[str, object]]:
    start_date = normalize_iso_datetime(getattr(args, "start_date", None), flag="--start-date")
    end_date = normalize_iso_datetime(getattr(args, "end_date", None), flag="--end-date")
    validate_max_date_range_days(
        start=start_date,
        end=end_date,
        max_days=31,
        label="transaction date range",
        date_only=False,
    )

    date_type = normalize_optional_str(getattr(args, "date_type", None)) or "transaction"
    if date_type not in _LIST_DATE_TYPES:
        raise ValidationError("Invalid --date-type. Use transaction, validation, or amendment")

    timezone = normalize_timezone(getattr(args, "timezone", None), default="UTC")
    params: dict[str, str] = {
        "startDate": start_date,
        "endDate": end_date,
        "dateType": date_type,
        "timezone": timezone,
    }
    metadata: dict[str, object] = {
        "start_date": start_date,
        "end_date": end_date,
        "date_type": date_type,
        "timezone": timezone,
    }
    return params, metadata


def cmd_transactions_list(args, ctx) -> int:
    cfg = ctx["cfg"]
    http = ctx["http_client"]
    token = require_token(cfg)

    publisher_id = str(args.publisher_id).strip()
    if not publisher_id:
        raise ValidationError("Missing --publisher-id")

    params, metadata = _base_params(args)

    advertiser_ids = csv_int_query_value(getattr(args, "advertiser_ids", None), flag="--advertiser-ids")
    if advertiser_ids:
        params["advertiserId"] = advertiser_ids
        metadata["advertiser_ids"] = advertiser_ids.split(",")
    else:
        metadata["advertiser_ids"] = []

    status = normalize_optional_str(getattr(args, "status", None))
    if status:
        if status not in _STATUS_VALUES:
            raise ValidationError("Invalid --status. Use pending, approved, declined, or deleted")
        params["status"] = status
    metadata["status"] = status

    show_basket_products = bool(getattr(args, "show_basket_products", False))
    if show_basket_products:
        params["showBasketProducts"] = bool_str(True)
    metadata["show_basket_products"] = show_basket_products

    headers = build_bearer_headers(token)
    query = build_access_token_query(token)
    query.update(params)

    payload, status_code = request_json(
        http,
        method="GET",
        url=f"{cfg.api_host}{_TRANSACTIONS_LIST_PATH.format(publisher_id=publisher_id)}",
        headers=headers,
        params=query,
        label="transactions list",
    )

    out = {
        "ok": True,
        "operation": "transactions.list",
        "publisher_id": publisher_id,
        "transactions": payload,
        "request": {
            "method": "GET",
            "endpoint": f"{cfg.api_host}/publishers/{publisher_id}/transactions/",
            "query": {
                "required": ["accessToken", "startDate", "endDate", "timezone"],
                "sent": safe_query_sent(params),
            },
            "response_status": status_code,
        },
        "metadata": metadata,
    }
    ctx["audit"].write("transactions.list", out)
    ctx["out"].emit(out)
    return 0


def cmd_transactions_by_ids(args, ctx) -> int:
    cfg = ctx["cfg"]
    http = ctx["http_client"]
    token = require_token(cfg)

    publisher_id = str(args.publisher_id).strip()
    if not publisher_id:
        raise ValidationError("Missing --publisher-id")

    ids = csv_int_query_value(getattr(args, "ids", None), flag="--ids")
    if not ids:
        raise ValidationError("Missing --ids")

    params: dict[str, str] = {
        "ids": ids,
        "timezone": normalize_timezone(getattr(args, "timezone", None), default="UTC"),
    }
    show_basket_products = bool(getattr(args, "show_basket_products", False))
    if show_basket_products:
        params["showBasketProducts"] = bool_str(True)

    headers = build_bearer_headers(token)
    query = build_access_token_query(token)
    query.update(params)

    payload, status_code = request_json(
        http,
        method="GET",
        url=f"{cfg.api_host}{_TRANSACTIONS_BY_IDS_PATH.format(publisher_id=publisher_id)}",
        headers=headers,
        params=query,
        label="transactions by ids",
    )

    out = {
        "ok": True,
        "operation": "transactions.by-ids",
        "publisher_id": publisher_id,
        "transactions": payload,
        "request": {
            "method": "GET",
            "endpoint": f"{cfg.api_host}/publishers/{publisher_id}/transactions",
            "query": {
                "required": ["accessToken", "ids"],
                "sent": safe_query_sent(params),
            },
            "response_status": status_code,
        },
        "metadata": {
            "ids": ids.split(","),
            "timezone": params["timezone"],
            "show_basket_products": show_basket_products,
        },
    }
    ctx["audit"].write("transactions.by-ids", out)
    ctx["out"].emit(out)
    return 0
