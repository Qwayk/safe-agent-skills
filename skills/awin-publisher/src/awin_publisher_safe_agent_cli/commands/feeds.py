from __future__ import annotations

from .api_helpers import build_bearer_headers
from .common import (
    normalize_optional_str,
    parse_csv_text,
    require_feed_api_key,
    require_token,
    request_bytes,
    resolve_out_path,
    validate_feed_download_url,
    write_download_file,
)
from ..errors import ValidationError


_ENHANCED_DOWNLOAD_PATH = "/publishers/{publisher_id}/awinfeeds/download/{advertiser_id}-{vertical}-{locale}.jsonl"
_LEGACY_LIST_PATH = "/datafeed/list/apikey/{api_key}"


def _decode_text(data: bytes) -> str:
    return data.decode("utf-8-sig", errors="replace")


def _find_row_value(row: dict[str, str], *candidates: str) -> str | None:
    lowered = {key.lower(): value for key, value in row.items()}
    for candidate in candidates:
        value = lowered.get(candidate.lower())
        if value:
            return value
    return None


def cmd_feeds_enhanced_download(args, ctx) -> int:
    cfg = ctx["cfg"]
    http = ctx["http_client"]
    token = require_token(cfg)

    publisher_id = str(args.publisher_id).strip()
    advertiser_id = str(args.advertiser_id).strip()
    if not publisher_id:
        raise ValidationError("Missing --publisher-id")
    if not advertiser_id:
        raise ValidationError("Missing --advertiser-id")

    locale = str(args.locale).strip()
    if not locale:
        raise ValidationError("Missing --locale")
    vertical = normalize_optional_str(getattr(args, "vertical", None)) or "retail"
    if vertical != "retail":
        raise ValidationError("Invalid --vertical. The official enhanced feed endpoint currently supports only retail")

    out_path = resolve_out_path(getattr(args, "out", None), overwrite=bool(getattr(args, "overwrite", False)))
    headers = build_bearer_headers(token)
    data, status_code, response_headers = request_bytes(
        http,
        method="GET",
        url=f"{cfg.api_host}{_ENHANCED_DOWNLOAD_PATH.format(publisher_id=publisher_id, advertiser_id=advertiser_id, vertical=vertical, locale=locale)}",
        headers=headers,
        label="feeds enhanced download",
    )
    file_info = write_download_file(out_path=out_path, data=data, content_type=response_headers.get("content-type"))

    out = {
        "ok": True,
        "operation": "feeds.enhanced-download",
        "publisher_id": publisher_id,
        "advertiser_id": advertiser_id,
        "download": file_info,
        "request": {
            "method": "GET",
            "endpoint": f"{cfg.api_host}/publishers/{publisher_id}/awinfeeds/download/{advertiser_id}-{vertical}-{locale}.jsonl",
            "response_status": status_code,
        },
        "metadata": {
            "auth_mode": "bearer",
            "locale": locale,
            "vertical": vertical,
        },
    }
    ctx["audit"].write("feeds.enhanced-download", out)
    ctx["out"].emit(out)
    return 0


def cmd_feeds_legacy_list(args, ctx) -> int:
    cfg = ctx["cfg"]
    http = ctx["http_client"]
    api_key = require_feed_api_key(cfg)

    out_path = resolve_out_path(getattr(args, "out", None), overwrite=bool(getattr(args, "overwrite", False)))
    data, status_code, response_headers = request_bytes(
        http,
        method="GET",
        url=f"{cfg.legacy_feed_host}{_LEGACY_LIST_PATH.format(api_key=api_key)}",
        label="feeds legacy list",
    )
    file_info = write_download_file(out_path=out_path, data=data, content_type=response_headers.get("content-type"))

    out = {
        "ok": True,
        "operation": "feeds.legacy-list",
        "download": file_info,
        "request": {
            "method": "GET",
            "endpoint": f"{cfg.legacy_feed_host}/datafeed/list/apikey/<redacted>",
            "response_status": status_code,
        },
        "metadata": {
            "auth_mode": "feed-api-key-in-url",
        },
    }
    ctx["audit"].write("feeds.legacy-list", out)
    ctx["out"].emit(out)
    return 0


def cmd_feeds_legacy_download(args, ctx) -> int:
    cfg = ctx["cfg"]
    http = ctx["http_client"]

    download_url = normalize_optional_str(getattr(args, "download_url", None))
    feed_id = normalize_optional_str(getattr(args, "feed_id", None))
    if bool(download_url) == bool(feed_id):
        raise ValidationError("Provide exactly one of --download-url or --feed-id")

    out_path = resolve_out_path(getattr(args, "out", None), overwrite=bool(getattr(args, "overwrite", False)))
    selector: dict[str, object]

    if feed_id:
        api_key = require_feed_api_key(cfg)
        list_data, _, _ = request_bytes(
            http,
            method="GET",
            url=f"{cfg.legacy_feed_host}{_LEGACY_LIST_PATH.format(api_key=api_key)}",
            label="feeds legacy list lookup",
        )
        rows = parse_csv_text(_decode_text(list_data))
        matched_url = None
        for row in rows:
            row_feed_id = _find_row_value(row, "Feed ID", "feed_id")
            if row_feed_id and row_feed_id.strip() == feed_id:
                matched_url = _find_row_value(row, "URL", "url")
                break
        if not matched_url:
            raise ValidationError(f"Feed id not found in legacy feed list: {feed_id}")
        download_url = validate_feed_download_url(matched_url)
        selector = {"source": "feed-id", "feed_id": feed_id}
    else:
        download_url = validate_feed_download_url(download_url or "")
        selector = {"source": "download-url"}

    data, status_code, response_headers = request_bytes(
        http,
        method="GET",
        url=download_url,
        label="feeds legacy download",
    )
    file_info = write_download_file(out_path=out_path, data=data, content_type=response_headers.get("content-type"))

    out = {
        "ok": True,
        "operation": "feeds.legacy-download",
        "download": file_info,
        "request": {
            "method": "GET",
            "endpoint": "<legacy-download-url-redacted>",
            "response_status": status_code,
        },
        "metadata": selector,
    }
    ctx["audit"].write("feeds.legacy-download", out)
    ctx["out"].emit(out)
    return 0
