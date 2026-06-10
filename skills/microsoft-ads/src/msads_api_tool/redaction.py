from __future__ import annotations

from typing import Any


def _looks_secret_key(key: str) -> bool:
    lk = key.lower()
    if lk in {
        "authorization",
        "developer_token",
        "developertoken",
        "authenticationtoken",
        "authentication_token",
        "access_token",
        "refresh_token",
        "id_token",
        "client_secret",
        "password",
        "token",
    }:
        return True
    if lk.endswith("_token") or lk.endswith("token"):
        return True
    if "secret" in lk:
        return True
    return False


def redact_any(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            ks = str(k)
            if _looks_secret_key(ks):
                out[ks] = "***REDACTED***"
            else:
                out[ks] = redact_any(v)
        return out
    if isinstance(obj, list):
        return [redact_any(v) for v in obj]
    return obj

