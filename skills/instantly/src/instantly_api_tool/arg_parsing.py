from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import quote

from .errors import ValidationError


def parse_yyyy_mm_dd(value: str, *, field: str) -> str:
    s = str(value or "").strip()
    if not s:
        raise ValidationError(f"Missing --{field}")
    try:
        # Enforce exact YYYY-MM-DD (no ambiguous formats).
        dt = datetime.strptime(s, "%Y-%m-%d")
    except ValueError as e:
        raise ValidationError(f"Invalid --{field} (expected YYYY-MM-DD): {s}") from e
    # Ensure round-trip preserves the exact formatting.
    if dt.strftime("%Y-%m-%d") != s:
        raise ValidationError(f"Invalid --{field} (expected YYYY-MM-DD): {s}")
    return s


def parse_comma_separated_strings(value: str, *, field: str, min_items: int = 1) -> list[str]:
    raw = str(value or "").strip()
    if not raw:
        if min_items <= 0:
            return []
        raise ValidationError(f"Missing --{field}")
    items = [p.strip() for p in raw.split(",")]
    items = [p for p in items if p]
    if len(items) < min_items:
        raise ValidationError(f"--{field} must include at least {min_items} value(s)")
    return items


def parse_comma_separated_ints(value: str, *, field: str) -> list[int]:
    items = parse_comma_separated_strings(value, field=field, min_items=1)
    out: list[int] = []
    for item in items:
        try:
            out.append(int(item))
        except ValueError as e:
            raise ValidationError(f"Invalid --{field} item (expected int): {item}") from e
    return out


def clamp_limit(value: Any, *, default: int | None, max_value: int, field: str = "limit") -> int | None:
    if value is None:
        return default
    try:
        n = int(value)
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"Invalid --{field} (expected int): {value}") from e
    if n <= 0:
        raise ValidationError(f"--{field} must be > 0")
    if n > max_value:
        raise ValidationError(f"--{field} must be <= {max_value}")
    return n


def quote_path_segment(value: str, *, field: str) -> str:
    s = str(value or "").strip()
    if not s:
        raise ValidationError(f"Missing --{field}")
    return quote(s, safe="")

