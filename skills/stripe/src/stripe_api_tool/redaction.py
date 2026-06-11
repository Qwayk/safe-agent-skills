from __future__ import annotations

import re
from typing import Any


_SECRET_KEY_RE = re.compile(r"(secret|api[_-]?key|password|token|client_secret)", re.IGNORECASE)


def redact_str(value: str) -> str:
    if not value:
        return value
    return "<REDACTED>"


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in (headers or {}).items():
        lk = str(k).lower()
        if lk in {"authorization", "proxy-authorization"}:
            out[lk] = "<REDACTED>"
        else:
            out[lk] = str(v)
    return out


def redact_obj(obj: Any) -> Any:
    """
    Best-effort redaction for Stripe responses/plans.

    Stripe responses can include secrets (notably `client_secret` on PaymentIntent/SetupIntent).
    We redact any keys that look secret-bearing.
    """
    if obj is None:
        return None
    if isinstance(obj, (bool, int, float)):
        return obj
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        return [redact_obj(v) for v in obj]
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            ks = str(k)
            if _SECRET_KEY_RE.search(ks):
                out[ks] = "<REDACTED>"
            else:
                out[ks] = redact_obj(v)
        return out
    return str(obj)

