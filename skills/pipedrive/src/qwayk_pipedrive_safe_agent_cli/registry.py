from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _catalog_path() -> Path:
    filename = "pipedrive_endpoint_catalog.json"
    seen: set[Path] = set()
    for base in Path(__file__).resolve().parents:
        for candidate in [
            base / ".openapi" / filename,
            base / "src" / ".openapi" / filename,
        ]:
            if candidate in seen:
                continue
            seen.add(candidate)
            if candidate.exists():
                return candidate
    raise RuntimeError("Missing endpoint catalog: no readable pipedrive_endpoint_catalog.json in .openapi")


def load_endpoint_catalog() -> list[dict[str, Any]]:
    path = _catalog_path()
    if not path.exists():
        raise RuntimeError(f"Missing endpoint catalog: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
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
