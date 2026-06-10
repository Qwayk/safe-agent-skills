from __future__ import annotations

import re
from typing import Any


_DEFAULT_REDACT_KEY_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(^|_)(access[_-]?token|token)($|_)", re.I),
    re.compile(r"(^|_)(password|secret|api[_-]?key)($|_)", re.I),
    re.compile(r"(^|_)(email)($|_)", re.I),
    re.compile(r"(^|_)(phone)($|_)", re.I),
    re.compile(r"(^|_)(first[_-]?name|last[_-]?name|name)($|_)", re.I),
    re.compile(r"(^|_)(address|city|zip|postal|country|province|state)($|_)", re.I),
)


def _should_redact_key(key: str) -> bool:
    k = str(key or "").strip()
    if not k:
        return False
    return any(p.search(k) for p in _DEFAULT_REDACT_KEY_PATTERNS)


def redact_for_artifacts(value: Any) -> Any:
    """
    Best-effort redaction for plan/receipt artifacts.

    - Never redact structural keys.
    - Redact values for likely secret/PII keys recursively.
    """
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            if _should_redact_key(str(k)):
                out[str(k)] = "***REDACTED***"
            else:
                out[str(k)] = redact_for_artifacts(v)
        return out
    if isinstance(value, list):
        return [redact_for_artifacts(v) for v in value]
    return value

