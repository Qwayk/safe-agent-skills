from __future__ import annotations

import re
from collections.abc import Mapping

REDACTED = "<redacted>"

SENSITIVE_TOKENS = {
    "authcode",
    "auth",
    "whois",
    "contact",
    "person",
    "organization",
    "email",
    "street",
    "address",
    "city",
    "state",
    "country",
    "postal",
    "zip",
    "phone",
}

SENSITIVE_EXACT_TOKENS = {
    "name",
    "fullname",
    "firstname",
    "lastname",
    "middlename",
    "personname",
    "organizationname",
    "postalcode",
}

COMPACT_SENSITIVE_PREFIXES = {
    "auth",
    "whois",
    "contact",
    "person",
    "organization",
    "email",
    "street",
    "address",
    "city",
    "state",
    "country",
    "postal",
    "zip",
    "phone",
}

WHITELIST_KEYS = {
    "status",
    "statusmeta",
    "statuscode",
    "domain",
    "domains",
    "domainname",
    "nameserver",
    "nameservers",
    "ns1",
    "ns2",
}

_CAMEL_PART_RE = re.compile(r"[A-Z]?[a-z]+|[0-9]+")


def _normalize_key(value: str) -> str:
    return "".join(ch.lower() for ch in value if ch.isalnum())


def _tokenize_key(value: str) -> set[str]:
    normalized = re.sub(r"[^0-9A-Za-z]+", " ", value)
    parts: set[str] = set()
    for segment in normalized.split():
        for token in _CAMEL_PART_RE.findall(segment):
            parts.add(token.lower())
    return parts


def _contains_sensitive_field(raw_key: str) -> bool:
    normalized = _normalize_key(raw_key)
    if normalized in WHITELIST_KEYS:
        return False
    if normalized in SENSITIVE_EXACT_TOKENS:
        return True
    if normalized in SENSITIVE_TOKENS:
        return True
    if any(normalized.startswith(prefix) for prefix in COMPACT_SENSITIVE_PREFIXES):
        return True
    if normalized.startswith("ns") and normalized[2:].isdigit() and normalized in {"ns1", "ns2"}:
        return False

    tokens = _tokenize_key(raw_key)
    if "auth" in tokens and "code" in tokens and len(tokens) > 1:
        return True
    if {"authcode", "auth", "code"}.intersection(tokens):
        return normalized.startswith("auth")

    return bool(tokens.intersection(SENSITIVE_TOKENS))


def redact(value: object) -> object:
    if isinstance(value, Mapping):
        redacted: dict[str, object] = {}
        for raw_key, raw_value in value.items():
            if not isinstance(raw_key, str):
                redacted[str(raw_key)] = REDACTED
                continue
            if _contains_sensitive_field(raw_key):
                redacted[raw_key] = REDACTED
            else:
                redacted[raw_key] = redact(raw_value)
        return redacted

    if isinstance(value, list):
        return [redact(item) for item in value]

    if isinstance(value, tuple):
        return [redact(item) for item in value]

    if isinstance(value, str):
        return value

    return value
