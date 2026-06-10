from __future__ import annotations

from typing import Any

from .api_helpers import build_access_token_query, build_bearer_headers
from .common import load_json_file, normalize_optional_str, require_token, request_json, safe_query_sent
from ..errors import ValidationError


_GENERATE_PATH = "/publishers/{publisher_id}/linkbuilder/generate"
_GENERATE_BATCH_PATH = "/publishers/{publisher_id}/linkbuilder/generate-batch"
_QUOTA_PATH = "/publishers/{publisher_id}/linkbuilder/quota"
_CLICK_PARAMETER_FLAGS = ("campaign", "clickref", "clickref2", "clickref3", "clickref4", "clickref5", "clickref6")


def _validate_publisher_and_advertiser_ids(args) -> tuple[str, int]:
    publisher_id = str(args.publisher_id).strip()
    if not publisher_id:
        raise ValidationError("Missing --publisher-id")
    advertiser_raw = str(args.advertiser_id).strip()
    if not advertiser_raw:
        raise ValidationError("Missing --advertiser-id")
    if not advertiser_raw.isdigit():
        raise ValidationError("Invalid --advertiser-id. Use a numeric advertiser id")
    return publisher_id, int(advertiser_raw)


def _tracking_parameters(args) -> dict[str, str]:
    out: dict[str, str] = {}
    for flag in _CLICK_PARAMETER_FLAGS:
        value = normalize_optional_str(getattr(args, flag, None))
        if value:
            out[flag] = value
    return out


def cmd_linkbuilder_generate(args, ctx) -> int:
    cfg = ctx["cfg"]
    http = ctx["http_client"]
    token = require_token(cfg)

    publisher_id, advertiser_id = _validate_publisher_and_advertiser_ids(args)
    body: dict[str, Any] = {"advertiserId": advertiser_id}

    destination_url = normalize_optional_str(getattr(args, "destination_url", None))
    if destination_url:
        body["destinationUrl"] = destination_url

    parameters = _tracking_parameters(args)
    if parameters:
        body["parameters"] = parameters

    shorten = bool(getattr(args, "shorten", False))
    if shorten:
        body["shorten"] = True

    headers = build_bearer_headers(token)
    query = build_access_token_query(token)
    payload, status_code = request_json(
        http,
        method="POST",
        url=f"{cfg.api_host}{_GENERATE_PATH.format(publisher_id=publisher_id)}",
        headers=headers,
        params=query,
        json_body=body,
        label="linkbuilder generate",
    )

    out = {
        "ok": True,
        "operation": "linkbuilder.generate",
        "publisher_id": publisher_id,
        "advertiser_id": advertiser_id,
        "link": payload,
        "request": {
            "method": "POST",
            "endpoint": f"{cfg.api_host}/publishers/{publisher_id}/linkbuilder/generate",
            "query": {
                "required": ["accessToken"],
                "sent": safe_query_sent({}),
            },
            "body": {
                "keys": sorted(body.keys()),
                "parameter_keys": sorted(parameters.keys()),
            },
            "response_status": status_code,
        },
        "metadata": {
            "destination_url": destination_url,
            "shorten": shorten,
            "parameter_keys": sorted(parameters.keys()),
        },
    }
    ctx["audit"].write("linkbuilder.generate", out)
    ctx["out"].emit(out)
    return 0


def cmd_linkbuilder_generate_batch(args, ctx) -> int:
    cfg = ctx["cfg"]
    http = ctx["http_client"]
    token = require_token(cfg)

    publisher_id = str(args.publisher_id).strip()
    if not publisher_id:
        raise ValidationError("Missing --publisher-id")

    payload_in, source_path = load_json_file(getattr(args, "requests_file", None), label="--requests-file")
    if isinstance(payload_in, dict):
        requests_value = payload_in.get("requests")
    else:
        requests_value = payload_in
    if not isinstance(requests_value, list):
        raise ValidationError("--requests-file must be a JSON array or an object with a requests array")
    if not requests_value:
        raise ValidationError("--requests-file must contain at least one batch request")
    if len(requests_value) > 100:
        raise ValidationError("The batch linkbuilder endpoint supports at most 100 requests per call")

    normalized_requests: list[dict[str, Any]] = []
    for idx, item in enumerate(requests_value, start=1):
        if not isinstance(item, dict):
            raise ValidationError(f"Batch request #{idx} must be a JSON object")
        advertiser_id = item.get("advertiserId")
        if advertiser_id is None or str(advertiser_id).strip() == "":
            raise ValidationError(f"Batch request #{idx} is missing advertiserId")
        if "shorten" in item:
            raise ValidationError("Batch linkbuilder requests do not support shorten")
        normalized_requests.append(item)

    body = {"requests": normalized_requests}
    headers = build_bearer_headers(token)
    query = build_access_token_query(token)
    payload, status_code = request_json(
        http,
        method="POST",
        url=f"{cfg.api_host}{_GENERATE_BATCH_PATH.format(publisher_id=publisher_id)}",
        headers=headers,
        params=query,
        json_body=body,
        label="linkbuilder generate batch",
    )
    responses_payload = payload.get("responses") if isinstance(payload, dict) and "responses" in payload else payload

    out = {
        "ok": True,
        "operation": "linkbuilder.generate-batch",
        "publisher_id": publisher_id,
        "responses": responses_payload,
        "request": {
            "method": "POST",
            "endpoint": f"{cfg.api_host}/publishers/{publisher_id}/linkbuilder/generate-batch",
            "query": {
                "required": ["accessToken"],
                "sent": safe_query_sent({}),
            },
            "body": {
                "requests_count": len(normalized_requests),
                "source_file": str(source_path),
            },
            "response_status": status_code,
        },
        "metadata": {
            "requests_count": len(normalized_requests),
            "source_file": str(source_path),
        },
    }
    ctx["audit"].write("linkbuilder.generate-batch", out)
    ctx["out"].emit(out)
    return 0


def cmd_linkbuilder_quota(args, ctx) -> int:
    cfg = ctx["cfg"]
    http = ctx["http_client"]
    token = require_token(cfg)

    publisher_id = str(args.publisher_id).strip()
    if not publisher_id:
        raise ValidationError("Missing --publisher-id")

    headers = build_bearer_headers(token)
    query = build_access_token_query(token)
    payload, status_code = request_json(
        http,
        method="GET",
        url=f"{cfg.api_host}{_QUOTA_PATH.format(publisher_id=publisher_id)}",
        headers=headers,
        params=query,
        label="linkbuilder quota",
    )

    out = {
        "ok": True,
        "operation": "linkbuilder.quota",
        "publisher_id": publisher_id,
        "quota": payload,
        "request": {
            "method": "GET",
            "endpoint": f"{cfg.api_host}/publishers/{publisher_id}/linkbuilder/quota",
            "query": {
                "required": ["accessToken"],
                "sent": safe_query_sent({}),
            },
            "response_status": status_code,
        },
        "metadata": {
            "auth_mode": "bearer",
        },
    }
    ctx["audit"].write("linkbuilder.quota", out)
    ctx["out"].emit(out)
    return 0
