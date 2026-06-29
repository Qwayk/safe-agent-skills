from __future__ import annotations

import json
import re
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any


def slugify(value: str, *, fallback: str = "item") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or fallback


def load_inventory(path: str | None = None) -> dict[str, Any]:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    return _load_packaged_inventory()


@lru_cache(maxsize=1)
def _load_packaged_inventory() -> dict[str, Any]:
    try:
        data = resources.files(__package__).joinpath("data/official_inventory.json").read_text(
            encoding="utf-8"
        )
    except FileNotFoundError:
        return {"operations": [], "families": []}
    return json.loads(data)


def operations_by_family(inventory: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    families: dict[str, list[dict[str, Any]]] = {}
    for op in inventory.get("operations") or []:
        if not isinstance(op, dict):
            continue
        family = str(op.get("family_slug") or "general")
        families.setdefault(family, []).append(op)
    for ops in families.values():
        ops.sort(key=lambda item: str(item.get("command") or item.get("operation_key") or ""))
    return dict(sorted(families.items()))


def find_operation(inventory: dict[str, Any], family: str, command: str) -> dict[str, Any] | None:
    for op in inventory.get("operations") or []:
        if not isinstance(op, dict):
            continue
        if str(op.get("family_slug")) == family and str(op.get("command")) == command:
            return op
    return None


def operation_is_write(op: dict[str, Any]) -> bool:
    return str(op.get("method") or "").upper() not in {"GET", "HEAD", "OPTIONS"}
