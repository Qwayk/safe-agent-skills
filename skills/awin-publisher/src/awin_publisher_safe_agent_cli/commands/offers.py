from __future__ import annotations

from .api_helpers import build_access_token_query, build_bearer_headers
from .common import (
    csv_int_query_value,
    normalize_country_codes,
    normalize_iso_date,
    normalize_optional_str,
    normalize_positive_int,
    require_token,
    request_json,
    safe_query_sent,
)
from ..errors import ValidationError


_OFFERS_PATH = "/publisher/{publisher_id}/promotions"
_MEMBERSHIP_VALUES = {"joined", "notJoined", "all"}
_STATUS_VALUES = {"active", "expiringSoon", "upcoming"}
_TYPE_VALUES = {"promotion", "voucher", "all"}


def cmd_offers_list(args, ctx) -> int:
    cfg = ctx["cfg"]
    http = ctx["http_client"]

    token = require_token(cfg)
    publisher_id = str(args.publisher_id).strip()
    if not publisher_id:
        raise ValidationError("Missing --publisher-id")

    membership = normalize_optional_str(getattr(args, "membership", None))
    if membership and membership not in _MEMBERSHIP_VALUES:
        raise ValidationError("Invalid --membership. Use joined, notJoined, or all")

    status = normalize_optional_str(getattr(args, "status", None))
    if status and status not in _STATUS_VALUES:
        raise ValidationError("Invalid --status. Use active, expiringSoon, or upcoming")

    offer_type = normalize_optional_str(getattr(args, "offer_type", None))
    if offer_type and offer_type not in _TYPE_VALUES:
        raise ValidationError("Invalid --type. Use promotion, voucher, or all")

    updated_since = normalize_optional_str(getattr(args, "updated_since", None))
    if updated_since:
        updated_since = normalize_iso_date(updated_since, flag="--updated-since")

    advertiser_ids = csv_int_query_value(getattr(args, "advertiser_ids", None), flag="--advertiser-ids")
    region_codes = normalize_country_codes(getattr(args, "region_codes", None), flag="--region-codes")

    filters: dict[str, object] = {}
    if advertiser_ids:
        filters["advertiserIds"] = [int(value) for value in advertiser_ids.split(",")]
    if bool(getattr(args, "exclusive_only", False)):
        filters["exclusiveOnly"] = True
    if membership:
        filters["membership"] = membership
    if region_codes:
        filters["regionCodes"] = region_codes
    if status:
        filters["status"] = status
    if offer_type:
        filters["type"] = offer_type
    if updated_since:
        filters["updatedSince"] = updated_since

    pagination: dict[str, int] = {}
    if getattr(args, "page", None) is not None:
        pagination["page"] = normalize_positive_int(args.page, flag="--page", minimum=1)
    if getattr(args, "page_size", None) is not None:
        pagination["pageSize"] = normalize_positive_int(args.page_size, flag="--page-size", minimum=10, maximum=200)

    body: dict[str, object] = {}
    if filters:
        body["filters"] = filters
    if pagination:
        body["pagination"] = pagination

    params = build_access_token_query(token)
    headers = build_bearer_headers(token)
    payload, status_code = request_json(
        http,
        method="POST",
        url=f"{cfg.api_host}{_OFFERS_PATH.format(publisher_id=publisher_id)}",
        headers=headers,
        params=params,
        json_body=body,
        label="offers list",
    )

    out = {
        "ok": True,
        "operation": "offers.list",
        "publisher_id": publisher_id,
        "offers": payload,
        "request": {
            "method": "POST",
            "endpoint": f"{cfg.api_host}/publisher/{publisher_id}/promotions",
            "query": {
                "required": ["accessToken"],
                "sent": safe_query_sent({}),
            },
            "body": {
                "filters": sorted(filters.keys()),
                "pagination": sorted(pagination.keys()),
            },
            "response_status": status_code,
        },
        "metadata": {
            "auth_mode": "bearer",
            "advertiser_ids": advertiser_ids.split(",") if advertiser_ids else [],
            "exclusive_only": bool(getattr(args, "exclusive_only", False)),
            "membership": membership,
            "region_codes": region_codes,
            "status": status,
            "type": offer_type,
            "updated_since": updated_since,
            "page": pagination.get("page"),
            "page_size": pagination.get("pageSize"),
        },
    }
    ctx["audit"].write("offers.list", out)
    ctx["out"].emit(out)
    return 0
