from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import parse_qsl, quote, unquote, urlencode, urlsplit, urlunsplit


SECRET_KEYS = (
    "token",
    "secret",
    "password",
    "authorization",
    "cookie",
    "webhook",
    "blueprint",
    "api_key",
    "apikey",
    "access_key",
    "private_key",
    "refresh_token",
    "client_secret",
)


def is_secret_like(key: str, value: str) -> bool:
    key_l = str(key).lower()
    if any(part in key_l for part in SECRET_KEYS):
        return True
    return len(str(value)) > 12 and bool(re.search(r"(token|secret|key|hook)", str(value), re.I))


def redact_value(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            key_s = str(key)
            if any(part in key_s.lower() for part in SECRET_KEYS):
                redacted[key_s] = "<REDACTED>"
            else:
                redacted[key_s] = redact_value(item)
        return redacted
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, str) and is_secret_like("", value):
        return "<REDACTED>"
    return value


def redact_pair(raw: str, *, marker: str = "<redacted>") -> str:
    if "=" not in raw:
        return raw
    key, value = raw.split("=", 1)
    return f"{key}={marker}" if is_secret_like(key, value) else raw


def redact_url(
    url: str,
    *,
    path_params: dict[str, str] | None = None,
    query: dict[str, str] | None = None,
) -> str:
    redacted = str(url)
    for key, value in (path_params or {}).items():
        if is_secret_like(key, value):
            redacted = redacted.replace(str(value), "<REDACTED>")
            redacted = redacted.replace(quote(str(value), safe=""), "%3CREDACTED%3E")

    try:
        parts = urlsplit(redacted)
    except Exception:
        return redacted

    path_parts: list[str] = []
    for segment in parts.path.split("/"):
        decoded = unquote(segment)
        path_parts.append("%3CREDACTED%3E" if is_secret_like("", decoded) else segment)

    pairs = parse_qsl(parts.query, keep_blank_values=True)
    safe_pairs: list[tuple[str, str]] = []
    for key, value in pairs:
        original_value = (query or {}).get(key, value)
        safe_pairs.append((key, "<REDACTED>" if is_secret_like(key, original_value) else value))

    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            "/".join(path_parts),
            urlencode(safe_pairs, doseq=True),
            parts.fragment,
        )
    )


def redact_text(text: str, *, url_sanitizer: Any | None = None) -> str:
    safe = str(text)

    def _replace_url(match: re.Match[str]) -> str:
        raw = match.group(0)
        return str(url_sanitizer(raw) if url_sanitizer else redact_url(raw))

    safe = re.sub(r"https?://[^\s\"'<>]+", _replace_url, safe)
    secret_names = "|".join(re.escape(key) for key in SECRET_KEYS)
    safe = re.sub(
        rf"(?i)([\"']?(?:{secret_names})[\"']?\s*[:=]\s*)(\"[^\"]*\"|'[^']*'|[^\s,}}]+)",
        lambda m: m.group(1) + '"<REDACTED>"',
        safe,
    )
    return safe


def redact_body_text(text: str, *, url_sanitizer: Any | None = None) -> str:
    try:
        parsed = json.loads(text)
    except Exception:
        return redact_text(text, url_sanitizer=url_sanitizer)
    return json.dumps(redact_value(parsed), sort_keys=True, ensure_ascii=True)
