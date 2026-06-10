from __future__ import annotations

import re
from typing import Any


REDACTED = "***REDACTED***"


def _normalize_key(key: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(key).lower())


_REDACT_KEYS_NORMALIZED = {
    _normalize_key("authorization"),
    _normalize_key("password"),
    _normalize_key("secret"),
    _normalize_key("token"),
    _normalize_key("api_key"),
    _normalize_key("apiKey"),
    _normalize_key("access_token"),
    _normalize_key("accessToken"),
    _normalize_key("refresh_token"),
    _normalize_key("refreshToken"),
    _normalize_key("client_secret"),
    _normalize_key("clientSecret"),
}

_REDACT_SUFFIXES_NORMALIZED = (
    "token",
    "secret",
    "apikey",
    "password",
)


def _redact_bearer_tokens(text: str) -> str:
    # Include common base64-ish and JWT-ish characters, plus "=" padding.
    return re.sub(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+", f"Bearer {REDACTED}", text)


def _redact_inline_key_value(text: str) -> str:
    # JSON-style: "apiKey": "...."
    text = re.sub(
        r'(?is)("?(?:api[_-]?key|access[_-]?token|refresh[_-]?token|token|password|secret|authorization)"?\s*:\s*)"[^"]*"',
        rf"\1\"{REDACTED}\"",
        text,
    )
    # INI/query-style: apiKey=.... or accessToken: ....
    text = re.sub(
        r"(?is)(\b(?:api[_-]?key|access[_-]?token|refresh[_-]?token|token|password|secret|authorization)\b\s*[:=]\s*)([^\s,;]+)",
        rf"\1{REDACTED}",
        text,
    )
    return text


def sanitize(obj: Any) -> Any:
    """
    Recursively sanitize objects for safe stdout + receipts.

    This tool must never print or persist secrets (passwords/tokens/Authorization headers).
    """
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            nk = _normalize_key(k)
            if nk in _REDACT_KEYS_NORMALIZED or nk.endswith(_REDACT_SUFFIXES_NORMALIZED):
                out[k] = REDACTED
            else:
                out[k] = sanitize(v)
        return out
    if isinstance(obj, list):
        return [sanitize(x) for x in obj]
    if isinstance(obj, str):
        text = _redact_bearer_tokens(obj)
        return _redact_inline_key_value(text)
    return obj
