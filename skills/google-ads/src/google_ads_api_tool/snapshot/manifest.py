from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass(frozen=True)
class GroupResult:
    group_id: str
    required: bool
    status: str  # ok|failed|skipped
    error_count: int
    row_count: int
    truncated: bool


@dataclass(frozen=True)
class TableResult:
    name: str
    path: str
    row_count: int
    truncated: bool
    join_keys: list[str]
    source_group_id: str


def build_manifest(
    *,
    tool: str,
    tool_version: str,
    preset: dict[str, Any],
    customer_id: str,
    since: str,
    until: str,
    segmentation: str,
    join_map: dict[str, Any],
    groups: list[GroupResult],
    tables: list[TableResult],
    warnings: list[str],
    errors_path: str,
    queries_path: str,
    schema_version: int = 1,
) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "tool": tool,
        "tool_version": tool_version,
        "generated_at_utc": _utc_now(),
        "preset": preset.get("name"),
        "customer_id": customer_id,
        "since": since,
        "until": until,
        "segmentation": segmentation,
        "join_map": join_map,
        "tables": [
            {
                "name": t.name,
                "path": t.path,
                "row_count": t.row_count,
                "truncated": t.truncated,
                "join_keys": list(t.join_keys),
                "source_group_id": t.source_group_id,
            }
            for t in tables
        ],
        "groups": [
            {
                "group_id": g.group_id,
                "required": g.required,
                "status": g.status,
                "error_count": g.error_count,
                "row_count": g.row_count,
                "truncated": g.truncated,
            }
            for g in groups
        ],
        "warnings": list(warnings),
        "errors_path": errors_path,
        "queries_path": queries_path,
    }

