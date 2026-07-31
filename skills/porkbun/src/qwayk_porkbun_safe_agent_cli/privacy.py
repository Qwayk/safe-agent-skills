from __future__ import annotations

from collections.abc import Iterable
from typing import Any

REDACTED = "***REDACTED***"
_SENSITIVE_MARKERS = (
    "password",
    "token",
    "secret",
    "apikey",
    "privatekey",
    "authcode",
    "codeverifier",
    "requesttoken",
)


def _normalized_key(key: Any) -> str:
    return "".join(char for char in str(key).lower() if char.isalnum())


def is_sensitive_key(key: Any) -> bool:
    normalized = _normalized_key(key)
    return any(marker in normalized for marker in _SENSITIVE_MARKERS)


def _all_scalar_values(value: Any) -> set[str]:
    if isinstance(value, dict):
        result: set[str] = set()
        for nested in value.values():
            result.update(_all_scalar_values(nested))
        return result
    if isinstance(value, list):
        result = set()
        for nested in value:
            result.update(_all_scalar_values(nested))
        return result
    if isinstance(value, (str, int, float)) and str(value):
        return {str(value)}
    return set()


def collect_sensitive_values(value: Any) -> set[str]:
    result: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            if is_sensitive_key(key):
                result.update(_all_scalar_values(nested))
            else:
                result.update(collect_sensitive_values(nested))
    elif isinstance(value, list):
        for nested in value:
            result.update(collect_sensitive_values(nested))
    return result


def scrub_text(text: Any, sensitive_values: Iterable[str]) -> str:
    result = str(text)
    values = sorted({str(value) for value in sensitive_values if str(value)}, key=len, reverse=True)
    for value in values:
        result = result.replace(value, REDACTED)
    return result


def sanitize(value: Any, sensitive_values: Iterable[str] = ()) -> Any:
    values = tuple(str(item) for item in sensitive_values if str(item))
    if isinstance(value, dict):
        result: dict[Any, Any] = {}
        for key, nested in value.items():
            if is_sensitive_key(key):
                result[key] = REDACTED
            else:
                result[key] = sanitize(nested, values)
        return result
    if isinstance(value, list):
        return [sanitize(nested, values) for nested in value]
    if isinstance(value, str):
        return scrub_text(value, values)
    return value
