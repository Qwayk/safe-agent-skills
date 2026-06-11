from __future__ import annotations

import json
from pathlib import Path


def _tool_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_live_inventory_payload() -> dict[str, object]:
    path = _tool_root() / "docs" / "_generated" / "live_official_api_inventory.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_live_inventory_rows() -> list[dict[str, object]]:
    payload = load_live_inventory_payload()
    rows = payload.get("operations")
    if not isinstance(rows, list):
        raise AssertionError("live_official_api_inventory.json is missing an operations list")
    return [row for row in rows if isinstance(row, dict)]
