from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .errors import ValidationError


def parse_fields_csv(fields_csv: str | None) -> list[str]:
    """
    Parse a comma-separated `fields` string into a stable list.

    - Trims whitespace
    - Drops empty entries
    - De-duplicates while preserving order
    """
    raw = str(fields_csv or "").strip()
    if not raw:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for part in raw.split(","):
        f = part.strip()
        if not f:
            continue
        if f in seen:
            continue
        seen.add(f)
        out.append(f)
    return out


def chunk_list(items: list[str], *, max_chunk_size: int) -> list[list[str]]:
    if max_chunk_size <= 0:
        raise ValidationError("--fields-chunk-size must be > 0")
    if not items:
        return []
    return [items[i : i + max_chunk_size] for i in range(0, len(items), max_chunk_size)]


def ensure_field(fields: list[str], required_field: str) -> list[str]:
    required_field = str(required_field or "").strip()
    if not required_field:
        return list(fields)
    if required_field in fields:
        return list(fields)
    return [required_field, *fields]


@dataclass(frozen=True)
class ChunkFailure:
    surface: str
    chunk_index: int
    fields: tuple[str, ...]
    error_type: str
    error: str

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "surface": self.surface,
            "chunk_index": self.chunk_index,
            "fields": list(self.fields),
            "error_type": self.error_type,
            "error": self.error,
        }


def merge_rows_by_id(passes: list[list[dict[str, Any]]], *, id_key: str = "id") -> list[dict[str, Any]]:
    """
    Merge multiple passes of list results, joining rows by `id_key`.

    Merge rule: shallow dict merge; later passes overwrite earlier keys.
    Output order: stable by first-seen id across passes.
    """
    out: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    order: list[str] = []

    for rows in passes:
        for row in rows:
            if not isinstance(row, dict):
                continue
            rid = row.get(id_key, None)
            if not isinstance(rid, str) or not rid.strip():
                continue
            rid = rid.strip()
            if rid not in by_id:
                by_id[rid] = {"id": rid}
                order.append(rid)
            by_id[rid].update(row)

    for rid in order:
        out.append(by_id[rid])
    return out

