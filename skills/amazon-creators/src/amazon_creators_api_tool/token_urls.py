from __future__ import annotations

from typing import Final

from .locale_data import LocaleInfo, locale_info

V2_TOKEN_ENDPOINTS: Final[dict[str, str]] = {
    "2.1": "https://creatorsapi.auth.us-east-1.amazoncognito.com/oauth2/token",
    "2.2": "https://creatorsapi.auth.eu-south-2.amazoncognito.com/oauth2/token",
    "2.3": "https://creatorsapi.auth.us-west-2.amazoncognito.com/oauth2/token",
}
V3_TOKEN_ENDPOINTS: Final[dict[str, str]] = {
    "3.1": "https://api.amazon.com/auth/o2/token",
    "3.2": "https://api.amazon.co.uk/auth/o2/token",
    "3.3": "https://api.amazon.co.jp/auth/o2/token",
}
DEFAULT_V2_VERSION: Final[str] = "2.1"
DEFAULT_V3_VERSION: Final[str] = "3.1"


def _normalize_version(value: str) -> str:
    clean = (value or "").strip().lower()
    if clean.startswith("v"):
        clean = clean[1:]
    return clean


def default_token_url(credential_version: str, locale_code: str | None) -> str:
    normalized = _normalize_version(credential_version)
    info = locale_info(locale_code or "")
    if normalized.startswith("3"):
        version = normalized if normalized in V3_TOKEN_ENDPOINTS else _default_locale_v3_version(info)
        return V3_TOKEN_ENDPOINTS.get(version, V3_TOKEN_ENDPOINTS[DEFAULT_V3_VERSION])
    if normalized.startswith("2"):
        version = normalized if normalized in V2_TOKEN_ENDPOINTS else _default_locale_v2_version(info)
        return V2_TOKEN_ENDPOINTS.get(version, V2_TOKEN_ENDPOINTS[DEFAULT_V2_VERSION])
    fallback = _default_locale_v2_version(info)
    return V2_TOKEN_ENDPOINTS.get(fallback, V2_TOKEN_ENDPOINTS[DEFAULT_V2_VERSION])


def _default_locale_v2_version(info: LocaleInfo | None) -> str:
    if info:
        region = (info.region or "").lower()
        if region == "us-west-2":
            return "2.3"
        if region == "us-east-1":
            return "2.1"
    return "2.2"


def _default_locale_v3_version(info: LocaleInfo | None) -> str:
    if info:
        marketplace = (info.marketplace or "").lower()
        if marketplace.endswith(".co.uk"):
            return "3.2"
        if marketplace.endswith(".co.jp"):
            return "3.3"
    return "3.1"


def token_endpoints_for_locale(locale_code: str) -> dict[str, str]:
    info = locale_info(locale_code)
    out: dict[str, str] = {}
    out["v2"] = V2_TOKEN_ENDPOINTS[_default_locale_v2_version(info)]
    out["v3"] = V3_TOKEN_ENDPOINTS[_default_locale_v3_version(info)]
    for version, url in sorted(V2_TOKEN_ENDPOINTS.items()):
        out[f"v{version}"] = url
    for version, url in sorted(V3_TOKEN_ENDPOINTS.items()):
        out[f"v{version}"] = url
    return out
