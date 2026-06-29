from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from typing import Any

from .errors import ValidationError


@lru_cache(maxsize=4)
def load_inventory(path: str | None = None) -> dict[str, Any]:
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    data_path = files("n8n_safe_agent_cli").joinpath("data/official_inventory.json")
    return json.loads(data_path.read_text(encoding="utf-8"))


def operations_by_family(inventory: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    families: dict[str, list[dict[str, Any]]] = {}
    for op in inventory.get("operations") or []:
        if isinstance(op, dict):
            families.setdefault(str(op.get("family_slug") or "api"), []).append(op)
    for ops in families.values():
        ops.sort(key=lambda op: str(op.get("command") or ""))
    return dict(sorted(families.items()))


def find_operation(family: str, command: str) -> dict[str, Any]:
    inventory = load_inventory()
    for op in inventory.get("operations") or []:
        if not isinstance(op, dict):
            continue
        if str(op.get("family_slug")) == family and str(op.get("command")) == command:
            return op
    raise ValidationError(f"Unknown n8n operation: {family} {command}")


def find_operation_by_id(operation_id: str | None) -> dict[str, Any] | None:
    if not operation_id:
        return None
    inventory = load_inventory()
    for op in inventory.get("operations") or []:
        if isinstance(op, dict) and str(op.get("operation_id")) == str(operation_id):
            return op
    return None


def operation_is_write(op: dict[str, Any]) -> bool:
    return bool(op.get("write")) or str(op.get("method") or "").upper() != "GET"
