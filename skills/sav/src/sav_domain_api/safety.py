from __future__ import annotations

import hmac
import json
import re
from decimal import Decimal, InvalidOperation
from math import isfinite

from .errors import ValidationError

PLAN_SCHEMA_VERSION = 2
PLAN_REQUIRED_ACKS = ("--apply", "--yes", "--ack-no-snapshot", "--ack-high-risk")


def validate_domain(name: str) -> str:
    return _normalize_fqdn((name or "").strip().lower(), "domain name")


def parse_flag(value: str, *, name: str) -> str:
    normalized = (value or "").strip()
    if normalized not in {"0", "1"}:
        raise ValidationError(f"{name} must be 0 or 1")
    return normalized


def parse_sale_price(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        raise ValidationError("sale-price must be a positive number")
    if "_" in raw or re.search(r"[eE]", raw):
        raise ValidationError("sale-price must be a positive number")
    if not re.fullmatch(r"(0|[1-9][0-9]*)(?:\.[0-9]+)?", raw):
        raise ValidationError("sale-price must be a positive number")

    try:
        decimal_value = Decimal(raw)
    except InvalidOperation as exc:
        raise ValidationError("sale-price must be a positive number") from exc

    if not decimal_value.is_finite() or decimal_value <= 0:
        raise ValidationError("sale-price must be a positive number")

    normalized = f"{decimal_value.normalize():f}"
    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")
    return normalized


def parse_nameserver(value: str, *, label: str) -> str:
    return _normalize_fqdn((value or "").strip().lower(), label)


def parse_country_code(value: str) -> str:
    code = (value or "").strip().upper()
    if not re.fullmatch(r"[A-Z]{2}", code):
        raise ValidationError("country must be a 2-letter country code")
    return code


def parse_timeout_s(raw: str, *, field_name: str) -> float:
    try:
        timeout_s = float(raw)
    except ValueError as exc:
        raise ValidationError(f"{field_name} must be a finite, positive number") from exc

    if not isfinite(timeout_s) or timeout_s <= 0:
        raise ValidationError(f"{field_name} must be a finite, positive number")

    return timeout_s


def _normalize_fqdn(value: str, field_name: str) -> str:
    if not value or "." not in value:
        raise ValidationError(f"Invalid {field_name}")
    if len(value) > 253:
        raise ValidationError(f"Invalid {field_name}")

    labels = value.split(".")
    if any(len(label) == 0 for label in labels):
        raise ValidationError(f"Invalid {field_name}")
    for label in labels:
        if len(label) > 63:
            raise ValidationError(f"Invalid {field_name}")
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label):
            raise ValidationError(f"Invalid {field_name}")
    return value


def assert_any_whois_update(*, update_registrant: str, update_admin: str, update_tech: str) -> None:
    if update_registrant == "0" and update_admin == "0" and update_tech == "0":
        raise ValidationError("At least one WHOIS update flag must be 1")


def parse_auth_code(value: str) -> str:
    candidate = (value or "").strip()
    if not candidate:
        raise ValidationError("auth-code cannot be empty")
    return candidate


def build_plan_hmac(plan_body: dict[str, object], key: bytes) -> str:
    payload = json.dumps(
        plan_body,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hmac.new(key, payload, "sha256").hexdigest()
