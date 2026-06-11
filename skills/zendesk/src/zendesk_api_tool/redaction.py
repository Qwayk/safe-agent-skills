from __future__ import annotations

from typing import Any


_SENSITIVE_HEADER_KEYS = {
    "authorization",
    "proxy-authorization",
    "x-api-key",
    "api-key",
}


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in (headers or {}).items():
        lk = str(k).lower().strip()
        if lk in _SENSITIVE_HEADER_KEYS or "token" in lk or "secret" in lk:
            out[k] = "***REDACTED***"
        else:
            out[k] = v
    return out


def redact_obj(obj: Any) -> Any:
    """
    Best-effort redaction for obvious secret fields in JSON-like structures.

    Note: this intentionally does NOT attempt to redact user PII (names/emails/ticket contents),
    because those fields are not reliably detectable and redacting them blindly would be misleading.
    """
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            lk = str(k).lower()
            if lk in {"api_token", "access_token", "refresh_token", "id_token", "client_secret"} or lk.endswith("_token"):
                out[k] = "***REDACTED***"
            else:
                out[k] = redact_obj(v)
        return out
    if isinstance(obj, list):
        return [redact_obj(v) for v in obj]
    return obj

