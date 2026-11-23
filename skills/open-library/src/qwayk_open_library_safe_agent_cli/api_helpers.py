from __future__ import annotations

import re
from urllib.parse import quote, urlsplit

from .errors import ValidationError
from .http import HttpClient


_RECORD_IDS = {
    "works": ("work", "W"),
    "books": ("edition", "M"),
    "authors": ("author", "A"),
}


def _matches_record_id(record_id: str, suffix: str) -> bool:
    return re.fullmatch(rf"OL[0-9]+{suffix}", record_id) is not None


def is_record_key(key: object, *, collection: str) -> bool:
    prefix = f"/{collection}/"
    return (
        isinstance(key, str)
        and key.startswith(prefix)
        and _matches_record_id(key[len(prefix) :], _RECORD_IDS[collection][1])
    )


def normalize_ol_id(raw: str, *, expected_prefix: str) -> str:
    kind, suffix = _RECORD_IDS[expected_prefix]
    message = f"Use an Open Library {kind} ID ending in {suffix}, or a link to that record."
    try:
        path = urlsplit(raw.strip()).path
    except ValueError:
        raise ValidationError(message) from None
    parts = path.strip("/").split("/")
    if len(parts) == 1:
        record_id = parts[0]
    elif parts[0] == expected_prefix:
        record_id = parts[1]
    else:
        raise ValidationError(message)
    record_id = record_id.removesuffix(".json").upper()
    if not _matches_record_id(record_id, suffix):
        raise ValidationError(message)
    return record_id


def normalize_isbn(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        raise ValidationError("isbn is required")
    digits = "".join(ch for ch in raw if ch.isdigit() or ch.upper() == "X")
    if not digits:
        raise ValidationError("isbn must contain digits")
    digits = digits.upper()
    if len(digits) not in {10, 13}:
        raise ValidationError("isbn must be ISBN-10 or ISBN-13")
    if "X" in digits[:-1]:
        raise ValidationError("isbn X checksum marker is only valid at the end")
    return digits


def normalize_subject(raw: str) -> str:
    value = (raw or "").strip()
    if not value:
        raise ValidationError("subject is required")
    return quote(value.strip("/"))


def build_path(base_url: str, endpoint: str) -> str:
    return base_url.rstrip("/") + "/" + endpoint.lstrip("/")


def get_json(*, client: HttpClient, base_url: str, endpoint: str, params: dict[str, object] | None) -> object:
    if not endpoint:
        raise ValidationError("Missing endpoint")
    # Shared GET-only request layer for all commands.
    return client.request("GET", build_path(base_url, endpoint), params=params).json()
