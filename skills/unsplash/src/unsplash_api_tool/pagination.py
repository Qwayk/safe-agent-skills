from __future__ import annotations

from .errors import ValidationError
from .unsplash_client import validate_positive_int


PER_PAGE_MAX_DEFAULT = 30
PAGE_DEFAULT = 1
PER_PAGE_DEFAULT = 10


def validate_page(value: int | None, *, field: str = "--page") -> int:
    if value is None:
        return PAGE_DEFAULT
    n = validate_positive_int(value, field=field)
    return n


def validate_per_page(
    value: int | None,
    *,
    field: str = "--per-page",
    max_value: int = PER_PAGE_MAX_DEFAULT,
) -> int:
    if value is None:
        return PER_PAGE_DEFAULT
    n = validate_positive_int(value, field=field)
    if n > max_value:
        raise ValidationError(f"{field} must be <= {max_value}")
    return n

