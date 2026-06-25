from __future__ import annotations

import re
from typing import Any, Iterable

_REDACT_KEYS = {
    "authorization",
    "access_token",
    "api_key",
    "client_secret",
    "id_token",
    "password",
    "refresh_token",
    "secret",
    "token",
}


def redact_jsonish(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for key, value in obj.items():
            lk = str(key).lower()
            if lk in _REDACT_KEYS or lk.endswith("_token") or lk.endswith("_secret") or lk.endswith("_api_key"):
                out[key] = "***REDACTED***"
            else:
                out[key] = redact_jsonish(value)
        return out
    if isinstance(obj, list):
        return [redact_jsonish(item) for item in obj]
    if isinstance(obj, tuple):
        return [redact_jsonish(item) for item in obj]
    return obj


def iter_scalar_strings(obj: Any) -> Iterable[str]:
    if obj is None:
        return
    if isinstance(obj, str):
        if obj.strip():
            yield obj
        return
    if isinstance(obj, dict):
        for value in obj.values():
            yield from iter_scalar_strings(value)
        return
    if isinstance(obj, (list, tuple, set)):
        for value in obj:
            yield from iter_scalar_strings(value)


def redact_text(text: str, values: Iterable[str]) -> str:
    out = text
    for value in sorted({str(v).strip() for v in values if str(v).strip()}, key=len, reverse=True):
        if len(value) < 4:
            continue
        out = out.replace(value, "***REDACTED***")
    return out


def sanitize_error_message(exc: Exception, values: Iterable[str]) -> str:
    return redact_text(str(exc), values)


def redact_jsonish_with_values(obj: Any, values: Iterable[str]) -> Any:
    redaction_values = [str(v) for v in values if str(v).strip()]
    if isinstance(obj, dict):
        return {key: redact_jsonish_with_values(value, redaction_values) for key, value in obj.items()}
    if isinstance(obj, list):
        return [redact_jsonish_with_values(item, redaction_values) for item in obj]
    if isinstance(obj, tuple):
        return [redact_jsonish_with_values(item, redaction_values) for item in obj]
    if isinstance(obj, str):
        return redact_text(obj, redaction_values)
    return obj
