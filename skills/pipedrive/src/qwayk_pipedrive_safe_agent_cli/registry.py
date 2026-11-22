from __future__ import annotations

import json
from importlib.resources import files
from typing import Any


def load_endpoint_catalog() -> list[dict[str, Any]]:
    catalog = files(__package__).joinpath("data", "pipedrive_endpoint_catalog.json")
    raw = json.loads(catalog.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise RuntimeError("Endpoint catalog must be a JSON list")
    out: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, dict):
            out.append(item)
    return out


def command_name(entry: dict[str, Any]) -> str:
    return " ".join(str(x) for x in entry.get("command_tokens", []) if str(x).strip())


def arg_dest(name: str) -> str:
    return str(name).replace("-", "_").replace(".", "_").replace("{", "").replace("}", "")
