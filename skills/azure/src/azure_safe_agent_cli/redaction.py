from __future__ import annotations

from typing import Any, Iterable

REDACTED = "***REDACTED***"

_SENSITIVE_KEYS = (
    "access_token",
    "authorization",
    "client_secret",
    "connectionstring",
    "key",
    "password",
    "privatekey",
    "sas",
    "secret",
    "token",
)


def iter_scalar_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_scalar_strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from iter_scalar_strings(item)


def redact_text(text: str, values: Iterable[str] = ()) -> str:
    out = str(text)
    for value in values:
        if isinstance(value, str) and value and len(value) >= 4:
            out = out.replace(value, REDACTED)
    return out


def redact_jsonish(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            lowered = str(key).replace("_", "").replace("-", "").lower()
            if any(token in lowered for token in _SENSITIVE_KEYS):
                out[key] = REDACTED
            else:
                out[key] = redact_jsonish(item)
        return out
    if isinstance(value, list):
        return [redact_jsonish(item) for item in value]
    return value


def redact_jsonish_with_values(value: Any, values: Iterable[str]) -> Any:
    if isinstance(value, str):
        return redact_text(value, values)
    if isinstance(value, dict):
        return {key: redact_jsonish_with_values(item, values) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_jsonish_with_values(item, values) for item in value]
    return value


def sanitize_error_message(exc: BaseException, values: Iterable[str]) -> str:
    return redact_text(f"{type(exc).__name__}: {exc}", values)
