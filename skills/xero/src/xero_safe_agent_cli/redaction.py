from __future__ import annotations

import re
from typing import Any

REDACTED = "***REDACTED***"

SECRET_KEYS = {
    "access_token",
    "authorization",
    "client_secret",
    "code",
    "code_verifier",
    "cookie",
    "id_token",
    "password",
    "refresh_token",
    "secret",
    "token",
}

SENSITIVE_PARTS = {
    "accountnumber",
    "address",
    "amount",
    "asset",
    "balance",
    "bank",
    "bsb",
    "businessnumber",
    "cash",
    "contact",
    "dateofbirth",
    "description",
    "duration",
    "email",
    "employee",
    "estimate",
    "firstname",
    "invoice",
    "lastname",
    "mobile",
    "price",
    "project",
    "payment",
    "payroll",
    "phone",
    "rate",
    "receipt",
    "registrationnumber",
    "salary",
    "serial",
    "statement",
    "tax",
    "tfn",
    "timeentry",
    "total",
    "user",
    "value",
}

BEARER_RE = re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/-]+=*")
BASIC_RE = re.compile(r"(?i)basic\s+[A-Za-z0-9+/]+=*")
EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")


def _normalized_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


NORMALIZED_SECRET_KEYS = frozenset(_normalized_key(name) for name in SECRET_KEYS)


def redact(value: Any, *, sensitive: bool = True) -> Any:
    if isinstance(value, dict):
        output: dict[str, Any] = {}
        for key, item in value.items():
            normalized = _normalized_key(key)
            if normalized in NORMALIZED_SECRET_KEYS:
                output[str(key)] = REDACTED
            elif sensitive and (
                any(part in normalized for part in SENSITIVE_PARTS)
                or normalized == "id"
                or normalized.endswith("id")
                or normalized.endswith("name")
            ):
                output[str(key)] = REDACTED
            else:
                output[str(key)] = redact(item, sensitive=sensitive)
        return output
    if isinstance(value, list):
        return [redact(item, sensitive=sensitive) for item in value]
    if isinstance(value, str):
        result = BEARER_RE.sub("Bearer ***REDACTED***", value)
        result = BASIC_RE.sub("Basic ***REDACTED***", result)
        if sensitive:
            result = EMAIL_RE.sub(REDACTED, result)
        return result
    return value


def redact_all_leaves(value: Any) -> Any:
    """Keep response shape while hiding every provider-supplied scalar value."""
    if isinstance(value, dict):
        return {str(key): redact_all_leaves(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_all_leaves(item) for item in value]
    return REDACTED


def safe_error(message: str) -> str:
    return str(redact(message, sensitive=True))
