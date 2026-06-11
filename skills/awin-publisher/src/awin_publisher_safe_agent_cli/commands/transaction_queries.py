from __future__ import annotations

from .api_helpers import build_access_token_query, build_bearer_headers
from .common import (
    csv_int_query_value,
    csv_query_value,
    normalize_iso_datetime,
    normalize_optional_str,
    normalize_positive_int,
    normalize_timezone,
    require_token,
    request_json,
    safe_query_sent,
    validate_max_date_range_days,
)
from ..errors import ValidationError


_TRANSACTION_QUERIES_PATH = "/publisher/{publisher_id}/transactionqueries"
_DATE_TYPES = {"enquiryDate", "transactionDate", "validationDate"}
_STATUS_VALUES = {"pending", "approved", "declined"}


def cmd_transaction_queries_list(args, ctx) -> int:
    cfg = ctx["cfg"]
    http = ctx["http_client"]
    token = require_token(cfg)

    publisher_id = str(args.publisher_id).strip()
    if not publisher_id:
        raise ValidationError("Missing --publisher-id")

    start_date = normalize_iso_datetime(getattr(args, "start_date", None), flag="--start-date")
    end_date = normalize_iso_datetime(getattr(args, "end_date", None), flag="--end-date")
    validate_max_date_range_days(
        start=start_date,
        end=end_date,
        max_days=31,
        label="transaction query date range",
        date_only=False,
    )

    date_type = normalize_optional_str(getattr(args, "date_type", None)) or "transactionDate"
    if date_type not in _DATE_TYPES:
        raise ValidationError("Invalid --date-type. Use enquiryDate, transactionDate, or validationDate")

    timezone = normalize_timezone(getattr(args, "timezone", None), default="UTC")
    page_number = normalize_positive_int(getattr(args, "page_number", 1), flag="--page-number", minimum=1)
    page_size = normalize_positive_int(getattr(args, "page_size", 100), flag="--page-size", minimum=1, maximum=500)

    advertiser_ids = csv_int_query_value(getattr(args, "advertiser_ids", None), flag="--advertiser-ids")
    click_refs = csv_query_value(getattr(args, "click_refs", None), flag="--click-refs")
    statuses_list = []
    for value in str(getattr(args, "statuses", "") or "").split(","):
        item = value.strip()
        if not item:
            continue
        if item not in _STATUS_VALUES:
            raise ValidationError("Invalid --statuses. Use pending, approved, declined")
        statuses_list.append(item)

    params: dict[str, str] = {
        "startDate": start_date,
        "endDate": end_date,
        "dateType": date_type,
        "timezone": timezone,
        "pageNumber": str(page_number),
        "pageSize": str(page_size),
    }
    if advertiser_ids:
        params["advertiserIds"] = advertiser_ids
    if click_refs:
        params["clickRefs"] = click_refs
    if statuses_list:
        params["statuses"] = ",".join(statuses_list)

    headers = build_bearer_headers(token)
    query = build_access_token_query(token)
    query.update(params)

    payload, status_code = request_json(
        http,
        method="GET",
        url=f"{cfg.api_host}{_TRANSACTION_QUERIES_PATH.format(publisher_id=publisher_id)}",
        headers=headers,
        params=query,
        label="transaction queries list",
    )

    out = {
        "ok": True,
        "operation": "transaction-queries.list",
        "publisher_id": publisher_id,
        "transaction_queries": payload,
        "request": {
            "method": "GET",
            "endpoint": f"{cfg.api_host}/publisher/{publisher_id}/transactionqueries",
            "query": {
                "required": ["accessToken", "startDate", "endDate", "timezone"],
                "sent": safe_query_sent(params),
            },
            "response_status": status_code,
        },
        "metadata": {
            "start_date": start_date,
            "end_date": end_date,
            "date_type": date_type,
            "timezone": timezone,
            "page_number": page_number,
            "page_size": page_size,
            "advertiser_ids": advertiser_ids.split(",") if advertiser_ids else [],
            "click_refs": click_refs.split(",") if click_refs else [],
            "statuses": statuses_list,
        },
    }
    ctx["audit"].write("transaction-queries.list", out)
    ctx["out"].emit(out)
    return 0
