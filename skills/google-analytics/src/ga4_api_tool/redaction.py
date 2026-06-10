from __future__ import annotations

import re
from typing import Any


_REDACTED = "<REDACTED>"

# Keys that are known to carry secret values (case/format-insensitive).
_EXACT_SENSITIVE_KEYS = {
    "authorization",
    "cookie",
    "password",
    "passwd",
    "api_key",
    "apikey",
    "client_secret",
    "clientsecret",
    "refresh_token",
    "refreshtoken",
    "access_token",
    "accesstoken",
    "id_token",
    "idtoken",
    "token",
    "secret",
    # GA4 Measurement Protocol
    "secretvalue",
}

_TOKENISH_SUFFIXES = (
    "token",
    "secret",
    "password",
    "apikey",
)

_URL_QUERY_REDACT = re.compile(
    r"(?i)(access_token|refresh_token|id_token|client_secret|api_key|apikey|secretvalue|api_secret)=([^&]+)"
)


def _normalize_key(key: str) -> str:
    # Lowercase and drop non-alphanumerics so we catch camelCase/snake/kebab variants.
    return "".join(ch for ch in key.lower() if ch.isalnum() or ch == "_")


def is_sensitive_key(key: str) -> bool:
    nk = _normalize_key(key)
    if nk in _EXACT_SENSITIVE_KEYS:
        return True
    if nk.endswith(_TOKENISH_SUFFIXES):
        # Avoid redacting common non-secret fields like token_uri.
        if nk in {"token_uri", "tokenurl", "tokenendpoint"}:
            return False
        return True
    if "secret" in nk:
        return True
    if "password" in nk:
        return True
    if "authorization" in nk:
        return True
    return False


def _is_hard_sensitive_key(key: str) -> bool:
    """
    Keys that should always be replaced with <REDACTED>, even if the value is a
    nested structure.

    For "token-ish" container keys (e.g. oauth_token), we prefer to keep the
    structure and rely on recursive sanitization of nested secret fields.
    """
    nk = _normalize_key(key)
    if nk in _EXACT_SENSITIVE_KEYS:
        return True
    if "authorization" in nk:
        return True
    if "password" in nk:
        return True
    # Any "secret*" key is treated as hard sensitive; this includes GA4 Measurement Protocol `secretValue`.
    if "secret" in nk:
        return True
    return False


def _sanitize_str(value: str) -> str:
    # Best-effort: redact secret-y query params embedded in URLs/strings.
    return _URL_QUERY_REDACT.sub(lambda m: f"{m.group(1)}={_REDACTED}", value)


def sanitize(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            ks = str(k)
            if _is_hard_sensitive_key(ks):
                out[k] = _REDACTED
                continue

            if is_sensitive_key(ks):
                # Prefer preserving non-secret structure for token-ish container keys, while still
                # redacting secret scalar values.
                if isinstance(v, (dict, list, tuple)):
                    out[k] = sanitize(v)
                elif isinstance(v, str):
                    out[k] = _REDACTED
                else:
                    out[k] = v
                continue

            out[k] = sanitize(v)
        return out
    if isinstance(obj, list):
        return [sanitize(x) for x in obj]
    if isinstance(obj, tuple):
        return tuple(sanitize(x) for x in obj)
    if isinstance(obj, str):
        return _sanitize_str(obj)
    return obj
