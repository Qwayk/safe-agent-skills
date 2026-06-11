from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

from .errors import ValidationError
from .http import HttpClient, HttpResponse

MARKET_CHOICES = (
    "usd_en",
    "gbp_en",
    "aud_en",
    "cad_en",
    "eur_de",
    "eur_it",
    "eur_fr",
    "eur_es",
    "eur_nl",
    "chf_de",
)

PROGRAM_TYPE_CHOICES = ("CPA", "CPC")
SOVRN_PRODUCT_CHOICES = ("WRA", "ORG", "RAC", "RAL", "CUP", "TPA", "PCR", "TXT", "SHG", "PRF", "INS", "UNK")
DEVICE_TYPE_CHOICES = ("DSK", "MBL", "TBL", "UKN")
GRANULARITY_CHOICES = ("hour", "day", "month")
PROPERTY_TYPE_CHOICES = ("web", "app")
SENSITIVE_QUERY_KEYS = {"key", "apikey", "api_key", "site-api-key"}
SENSITIVE_EMIT_KEYS = {
    *SENSITIVE_QUERY_KEYS,
    "publisher_id",
    "advertising_publisher_id",
    "ip",
    "useragent",
    "referrerurl",
    "subid",
    "gdprconsent",
    "ccpaconsent",
    "gppconsent",
    "cuid",
}
SELECTED_RESPONSE_HEADERS = (
    "content-type",
    "content-encoding",
    "etag",
    "last-modified",
    "retry-after",
    "x-ratelimit-limit",
    "x-ratelimit-remaining",
    "x-ratelimit-reset",
)


def build_http_client(ctx: dict[str, Any]) -> HttpClient:
    return HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx.get("verbose")),
        user_agent=f'{ctx.get("tool", "sovrn-safe-cli")}/{ctx.get("tool_version", "0.0.0")}',
    )


def require_commerce_secret_key(cfg: Any) -> str:
    key = str(getattr(cfg, "commerce_secret_key", "") or "").strip()
    if not key:
        raise ValidationError("Missing SOVRN_COMMERCE_SECRET_KEY for this Commerce command")
    return key


def require_commerce_site_api_key(cfg: Any) -> str:
    key = str(getattr(cfg, "commerce_site_api_key", "") or "").strip()
    if not key:
        raise ValidationError("Missing SOVRN_COMMERCE_SITE_API_KEY for this Commerce command")
    return key


def require_advertising_api_key(cfg: Any) -> str:
    key = str(getattr(cfg, "advertising_api_key", "") or "").strip()
    if not key:
        raise ValidationError("Missing SOVRN_ADVERTISING_API_KEY for this Advertising command")
    return key


def resolve_advertising_publisher_id(args: argparse.Namespace, cfg: Any) -> str:
    override = str(getattr(args, "publisher_id", "") or "").strip()
    if override:
        return override
    configured = str(getattr(cfg, "advertising_publisher_id", "") or "").strip()
    if not configured:
        raise ValidationError(
            "Missing SOVRN_ADVERTISING_PUBLISHER_ID for this Advertising command. "
            "Set it in .env or pass --publisher-id."
        )
    return configured


def commerce_secret_headers(secret_key: str) -> dict[str, str]:
    return {"Authorization": f"secret {secret_key}"}


def advertising_headers(api_key: str) -> dict[str, str]:
    return {"x-api-key": api_key}


def quote_path(value: str) -> str:
    return quote(str(value), safe="")


def clean_mapping(obj: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in obj.items():
        if value is None:
            continue
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                continue
            out[key] = stripped
            continue
        out[key] = value
    return out


def bool_to_query(value: bool | None) -> str | None:
    if value is None:
        return None
    return "true" if value else "false"


def split_csv_values(values: list[str] | None) -> list[str]:
    out: list[str] = []
    for raw in values or []:
        for piece in str(raw).split(","):
            value = piece.strip()
            if value:
                out.append(value)
    return out


def join_csv_values(values: list[str] | None) -> str | None:
    items = split_csv_values(values)
    return ",".join(items) if items else None


def read_text_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise ValidationError(f"Text file not found: {p}")
    return p.read_text(encoding="utf-8")


def require_one_of(*, names: tuple[str, ...], values: tuple[str | None, ...], message: str) -> None:
    if any(bool(str(value or "").strip()) for value in values):
        return
    raise ValidationError(message)


def redact_url(url: str) -> str:
    if not url:
        return url
    parts = urlsplit(url)
    path_parts = parts.path.split("/")
    for idx, part in enumerate(path_parts):
        if part == "sites" and idx + 1 < len(path_parts) and path_parts[idx + 1]:
            path_parts[idx + 1] = "***REDACTED***"
    safe_path = "/".join(path_parts)
    if not parts.query:
        return urlunsplit((parts.scheme, parts.netloc, safe_path, parts.query, parts.fragment))
    query_pairs = parse_qsl(parts.query, keep_blank_values=True)
    redacted_pairs: list[tuple[str, str]] = []
    for key, value in query_pairs:
        if key.lower() in SENSITIVE_QUERY_KEYS:
            redacted_pairs.append((key, "***REDACTED***"))
        else:
            redacted_pairs.append((key, value))
    return urlunsplit((parts.scheme, parts.netloc, safe_path, urlencode(redacted_pairs), parts.fragment))


def redact_query_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    if not params:
        return None
    out: dict[str, Any] = {}
    for key, value in params.items():
        if key.lower() in SENSITIVE_EMIT_KEYS:
            out[key] = "***REDACTED***"
        else:
            out[key] = value
    return out


def extract_response_data(resp: HttpResponse) -> Any:
    if not resp.body:
        return None
    try:
        return resp.json()
    except Exception:
        return resp.text()


def selected_response_headers(headers: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for name in SELECTED_RESPONSE_HEADERS:
        if name in headers:
            out[name] = headers[name]
    return out


def emit_api_result(
    *,
    ctx: dict[str, Any],
    event: str,
    method: str,
    url: str,
    auth_shape: str,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
    notes: list[str] | None = None,
) -> int:
    client = build_http_client(ctx)
    response = client.request(method, url, headers=headers, params=params, json_body=json_body)
    payload: dict[str, Any] = {
        "ok": True,
        "command": ctx.get("command_str"),
        "auth_shape": auth_shape,
        "request": {
            "method": method,
            "url": response.url,
        },
        "response": {
            "status": response.status,
            "headers": selected_response_headers(response.headers),
            "data": extract_response_data(response),
        },
    }
    safe_params = redact_query_params(params)
    if safe_params:
        payload["request"]["params"] = safe_params
    if json_body is not None:
        payload["request"]["json"] = json_body
    if notes:
        payload["notes"] = notes
    ctx["audit"].write(
        event,
        {
            "auth_shape": auth_shape,
            "method": method,
            "url": redact_url(url),
            "params": safe_params,
            "status": response.status,
        },
    )
    ctx["out"].emit(payload)
    return 0
