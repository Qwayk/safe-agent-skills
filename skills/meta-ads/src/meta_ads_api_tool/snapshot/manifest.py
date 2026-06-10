from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from ..errors import ValidationError
from .schema import SCHEMA_VERSION, join_keys_by_table


@dataclass(frozen=True)
class TableInventoryItem:
    table: str
    relpath: str
    rows: int

    def to_public_dict(self) -> dict[str, Any]:
        return {"table": self.table, "relpath": self.relpath, "rows": self.rows}


def utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def build_manifest(
    *,
    tool: str,
    version: str,
    run_id: str,
    started_at_utc: str,
    finished_at_utc: str,
    base_url: str,
    api_version: str,
    ad_account_id: str,
    preset_id: str,
    preset_schema_version: str,
    tables: list[TableInventoryItem],
    request_summaries: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    assets: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = str(run_id or "").strip()
    if not rid:
        raise ValidationError("Missing run_id for manifest")
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": tool, "version": version},
        "run": {
            "run_id": rid,
            "started_at_utc": started_at_utc,
            "finished_at_utc": finished_at_utc,
        },
        "env": {
            "base_url": str(base_url or ""),
            "api_version": str(api_version or ""),
            "ad_account_id": str(ad_account_id or ""),
        },
        "preset": {
            "preset_id": str(preset_id or ""),
            "preset_schema_version": str(preset_schema_version or ""),
        },
        "join_keys": join_keys_by_table([t.table for t in tables]),
        "tables": [t.to_public_dict() for t in tables],
        "assets": assets if isinstance(assets, dict) else {"enabled": False},
        "requests": _sanitize_request_summaries(request_summaries),
        "errors": list(errors or []),
    }


def _sanitize_request_summaries(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for it in items or []:
        if not isinstance(it, dict):
            continue
        cleaned: dict[str, Any] = {}
        for k in ("surface", "path", "edge", "object_id", "level", "fields_count", "chunk_index", "chunks_total"):
            if k in it:
                cleaned[k] = it.get(k)
        params_keys = it.get("params_keys")
        if isinstance(params_keys, list):
            cleaned["params_keys"] = [str(x) for x in params_keys if str(x)]
            if "access_token" in cleaned["params_keys"]:
                cleaned["params_keys"] = [k for k in cleaned["params_keys"] if k != "access_token"]
        out.append(cleaned)
    return out
