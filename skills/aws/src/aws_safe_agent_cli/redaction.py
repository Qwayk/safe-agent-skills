from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

REDACTED = "***REDACTED***"

_SENSITIVE_KEY_RE = re.compile(
    r"(?i)(authorization|api[_-]?key|access[_-]?key|secret|session[_-]?token|"
    r"token|password|private[_-]?key|client[_-]?secret|credential|credentials)"
)

_KEY_VALUE_TEXT_RE = re.compile(
    r"(?i)\b(secret(?:access)?key|sessiontoken|token|password|api[_-]?key|client[_-]?secret|"
    r"private[_-]?key|accesskeyid|secretbinary|secretstring)\b\s*[:=]\s*['\"]?[^,'\"\s}]+['\"]?"
)
_AUTH_TEXT_RE = re.compile(r"(?i)\bauthorization:\s*[^\n,]+")
_AWS_ACCESS_KEY_RE = re.compile(r"\b(AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|AROA[0-9A-Z]{16})\b")


def _is_sensitive_key(key: Any) -> bool:
    text = str(key or "").strip().lower()
    return bool(text) and bool(_SENSITIVE_KEY_RE.search(text))


def redact_text(text: str) -> str:
    out = _KEY_VALUE_TEXT_RE.sub(lambda m: f"{m.group(1)}={REDACTED}", text)
    out = _AUTH_TEXT_RE.sub(f"authorization: {REDACTED}", out)
    out = _AWS_ACCESS_KEY_RE.sub(REDACTED, out)
    return out


def redact_obj(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, bytes):
        return REDACTED
    if isinstance(value, Mapping):
        out: dict[Any, Any] = {}
        for key, item in value.items():
            if _is_sensitive_key(key):
                out[key] = REDACTED
            else:
                out[key] = redact_obj(item)
        return out
    if isinstance(value, list):
        return [redact_obj(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_obj(item) for item in value)
    return value
