from __future__ import annotations

import re
from collections.abc import Mapping
from urllib.parse import quote, quote_plus

REDACTED = "<redacted>"

SENSITIVE_TOKENS = {
    "apikey",
    "savapikey",
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


def redact(value: object, *, secrets: tuple[str, ...] = ()) -> object:
    # SAV can repeat a submitted value in free-form text or in a URL.
    sensitive_strings = sorted(
        {form for secret in secrets if secret for form in (secret, quote(secret, safe=""), quote_plus(secret))},
        key=len,
        reverse=True,
    )
    pattern = (
        re.compile("|".join(map(re.escape, sensitive_strings))) if sensitive_strings else None
    )

    def scrub_text(text: str) -> str:
        return pattern.sub(REDACTED, text) if pattern else text

    def scrub(item: object) -> object:
        if isinstance(item, Mapping):
            return {
                scrub_text(str(key)): (
                    scrub(nested) if isinstance(key, str) and not _contains_sensitive_field(key) else REDACTED
                )
                for key, nested in item.items()
            }
        if isinstance(item, (list, tuple)):
            return [scrub(nested) for nested in item]
        if isinstance(item, str):
            return scrub_text(item)
        return item

    return scrub(value)
