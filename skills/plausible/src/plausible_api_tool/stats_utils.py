from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any


_ALLOWED_QUERY_KEYS = {"site_id", "date_range", "metrics", "dimensions", "filters", "order_by", "include", "pagination"}
_ALLOWED_INCLUDE_KEYS = {"imports", "time_labels", "total_rows"}
_ALLOWED_PAGINATION_KEYS = {"limit", "offset"}


@dataclass(frozen=True)
class DateRangePair:
    current: list[str]
    previous: list[str]


def load_query_from_sources(*, file: str | None, query: str | None, stdin: bool) -> dict[str, Any]:
    if int(bool(file)) + int(bool(query)) + int(bool(stdin)) != 1:
        raise RuntimeError("Provide exactly one of: --file, --query, --stdin")
    if file:
        data = json.loads(Path(file).read_text(encoding="utf-8"))
    elif query:
        data = json.loads(query)
    else:
        data = json.loads(sys.stdin.read())
    if not isinstance(data, dict):
        raise RuntimeError("Query JSON must be an object")
    return data


def validate_query(query: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    unknown = sorted(k for k in query.keys() if k not in _ALLOWED_QUERY_KEYS)
    if unknown:
        errors.append(f"Unknown top-level query keys: {unknown} (Stats API v2 is strict).")

    for required in ("site_id", "date_range", "metrics"):
        if required not in query:
            errors.append(f"Missing required key: {required}")

    if "limit" in query:
        errors.append("Top-level 'limit' is not supported; use pagination: {\"limit\": N, \"offset\": 0}.")

    metrics = query.get("metrics")
    if metrics is not None and not (isinstance(metrics, list) and all(isinstance(x, str) for x in metrics)):
        errors.append("'metrics' must be a list of strings.")

    dimensions = query.get("dimensions")
    if dimensions is not None and not (isinstance(dimensions, list) and all(isinstance(x, str) for x in dimensions)):
        errors.append("'dimensions' must be a list of strings.")

    date_range = query.get("date_range")
    if date_range is not None:
        if isinstance(date_range, str):
            pass
        elif isinstance(date_range, list) and len(date_range) == 2 and all(isinstance(x, str) for x in date_range):
            pass
        else:
            errors.append("'date_range' must be a string (e.g. '30d') or a [start,end] list of ISO8601 strings.")

    filters = query.get("filters")
    if filters is not None and not isinstance(filters, list):
        errors.append("'filters' must be a list.")

    order_by = query.get("order_by")
    if order_by is not None and not isinstance(order_by, list):
        errors.append("'order_by' must be a list.")

    include = query.get("include")
    if include is not None:
        if not isinstance(include, dict):
            errors.append("'include' must be an object.")
        else:
            unknown_include = sorted(k for k in include.keys() if k not in _ALLOWED_INCLUDE_KEYS)
            if unknown_include:
                warnings.append(f"Unknown include keys: {unknown_include} (may fail on strict servers).")

    pagination = query.get("pagination")
    if pagination is not None:
        if not isinstance(pagination, dict):
            errors.append("'pagination' must be an object.")
        else:
            unknown_pag = sorted(k for k in pagination.keys() if k not in _ALLOWED_PAGINATION_KEYS)
            if unknown_pag:
                warnings.append(f"Unknown pagination keys: {unknown_pag}")
            lim = pagination.get("limit")
            off = pagination.get("offset")
            if lim is not None and not (isinstance(lim, int) and lim > 0):
                errors.append("'pagination.limit' must be a positive integer.")
            if off is not None and not (isinstance(off, int) and off >= 0):
                errors.append("'pagination.offset' must be a non-negative integer.")

    return errors, warnings


def ensure_site_id(query: dict[str, Any], site_id: str) -> dict[str, Any]:
    out = dict(query)
    out.setdefault("site_id", site_id)
    return out


def set_pagination(query: dict[str, Any], *, limit: int, offset: int) -> dict[str, Any]:
    out = dict(query)
    out["pagination"] = {"limit": int(limit), "offset": int(offset)}
    return out


def set_include_total_rows(query: dict[str, Any], enabled: bool) -> dict[str, Any]:
    out = dict(query)
    include = dict(out.get("include") or {})
    if enabled:
        include["total_rows"] = True
    else:
        include.pop("total_rows", None)
    out["include"] = include
    return out


def merge_paginated_responses(first: dict[str, Any], parts: list[dict[str, Any]]) -> dict[str, Any]:
    merged = dict(first)
    merged_results: list[Any] = []
    for resp in [first, *parts]:
        r = resp.get("results")
        if isinstance(r, list):
            merged_results.extend(r)
    merged["results"] = merged_results
    return merged


def date_range_pair_for_days(days: int) -> DateRangePair:
    if days <= 0:
        raise RuntimeError("--days must be > 0")
    today = date.today()
    current_end = today
    current_start = today - timedelta(days=days - 1)
    prev_end = current_start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days - 1)
    return DateRangePair(
        current=[current_start.isoformat(), current_end.isoformat()],
        previous=[prev_start.isoformat(), prev_end.isoformat()],
    )


def apply_date_range(query: dict[str, Any], dr: list[str] | str) -> dict[str, Any]:
    out = dict(query)
    out["date_range"] = dr
    return out

