from __future__ import annotations

import re
from typing import Any


_SENSITIVE_KEY_RE = re.compile(
    r"(^|_)(api[_-]?key|apikey|authorization|bearer|token|secret|password|refresh[_-]?token)($|_)",
    re.IGNORECASE,
)


def _looks_like_apikey_value(value: str) -> bool:
    v = value.strip().lower()
    # Only redact obvious Authorization-style token strings. Avoid redacting non-secret hashes
    # (for example request_sha256 used for plan drift checks).
    return v.startswith("apikey ") or v.startswith("bearer ")


def redact_any(obj: Any) -> Any:
    """
    Redact secrets in nested dict/list structures.

    - Redacts values for sensitive-looking keys.
    - Redacts string values that look like an Authorization-style apikey token.
    """
    if obj is None:
        return None
    if isinstance(obj, (bool, int, float)):
        return obj
    if isinstance(obj, str):
        return "<REDACTED>" if _looks_like_apikey_value(obj) else obj
    if isinstance(obj, list):
        return [redact_any(v) for v in obj]
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            ks = str(k)
            if _SENSITIVE_KEY_RE.search(ks):
                out[ks] = "<REDACTED>"
            else:
                out[ks] = redact_any(v)
        return out
    # Fallback for unknown types (bytes, dataclasses, etc.)
    try:
        s = str(obj)
    except Exception:
        return "<REDACTED>"
    return "<REDACTED>" if _looks_like_apikey_value(s) else s
