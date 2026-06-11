from __future__ import annotations

from urllib.parse import quote

from .errors import ValidationError
from .http import HttpClient


def normalize_ol_id(raw: str, *, expected_prefix: str) -> str:
    value = (raw or "").strip()
    if not value:
        raise ValidationError(f"{expected_prefix} id is required")

    low = value.lower()
    if low.startswith("http://") or low.startswith("https://"):
        marker = "openlibrary.org/"
        idx = low.find(marker)
        if idx >= 0:
            value = value[idx + len(marker) :]
        else:
            value = value.split("/")[-1]

    value = value.strip().strip("/")
    if value.endswith(".json"):
        value = value[: -len(".json")]

    parts = [p for p in value.split("/") if p]
    if not parts:
        raise ValidationError(f"{expected_prefix} id is required")
    if parts[0] == expected_prefix:
        if len(parts) < 2:
            raise ValidationError(f"Invalid {expected_prefix} id")
        return parts[1]
    return parts[-1]


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
