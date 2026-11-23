from __future__ import annotations

import json

from cloudflare_api_tool.openapi_index import LIVE_INVENTORY_PATH


def load_live_inventory_payload() -> dict[str, object]:
    return json.loads(LIVE_INVENTORY_PATH.read_text(encoding="utf-8"))


def load_live_inventory_rows() -> list[dict[str, object]]:
    payload = load_live_inventory_payload()
    rows = payload.get("operations")
    if not isinstance(rows, list):
        raise AssertionError("live_official_api_inventory.json is missing an operations list")
    return [row for row in rows if isinstance(row, dict)]
