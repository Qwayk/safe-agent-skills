from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any


@dataclasses.dataclass(frozen=True)
class OperationSpec:
    lexicon_id: str
    operation_command: str
    namespace: str
    group: str
    kind: str
    http_method: str
    path: str
    doc_url: str
    docs_source: str
    stability: str
    route_hint: str
    primary_cli: str
    input_encoding: str | None = None
    description: str = ""
    query_params: tuple[str, ...] = ()
    required_query_params: tuple[str, ...] = ()
    required_body_fields: tuple[str, ...] = ()


def tool_root_path() -> Path:
    return Path(__file__).resolve().parents[2]


def pinned_official_inventory_path() -> Path:
    docs = tool_root_path() / "docs"
    candidates = sorted(docs.glob("official_xrpc_inventory_v1_*.json"))
    if not candidates:
        raise RuntimeError(f"Missing pinned Bluesky inventory under {docs}")
    return candidates[-1]


def _row_to_operation(row: dict[str, Any]) -> OperationSpec:
    return OperationSpec(
        lexicon_id=str(row.get("lexicon_id") or ""),
        operation_command=str(row.get("operation_command") or ""),
        namespace=str(row.get("namespace") or ""),
        group=str(row.get("group") or ""),
        kind=str(row.get("kind") or ""),
        http_method=str(row.get("http_method") or ""),
        path=str(row.get("path") or ""),
        doc_url=str(row.get("doc_url") or ""),
        docs_source=str(row.get("docs_source") or ""),
        stability=str(row.get("stability") or ""),
        route_hint=str(row.get("route_hint") or ""),
        primary_cli=str(row.get("primary_cli") or ""),
        input_encoding=str(row.get("input_encoding") or "") or None,
        description=str(row.get("description") or ""),
        query_params=tuple(str(item) for item in (row.get("query_params") or [])),
        required_query_params=tuple(str(item) for item in (row.get("required_query_params") or [])),
        required_body_fields=tuple(str(item) for item in (row.get("required_body_fields") or [])),
    )


def parse_official_inventory_json(text: str) -> list[OperationSpec]:
    raw = json.loads(text)
    if not isinstance(raw, list):
        raise RuntimeError("Pinned Bluesky inventory must be a JSON array")
    out: list[OperationSpec] = []
    for item in raw:
        if not isinstance(item, dict):
            raise RuntimeError("Pinned Bluesky inventory rows must be JSON objects")
        op = _row_to_operation(item)
        if not op.lexicon_id or not op.operation_command or not op.path:
            raise RuntimeError(f"Invalid inventory row: {item}")
        out.append(op)
    return out


def load_official_inventory_file(path: Path) -> list[OperationSpec]:
    return parse_official_inventory_json(path.read_text(encoding="utf-8"))


def load_pinned_inventory() -> list[OperationSpec]:
    return load_official_inventory_file(pinned_official_inventory_path())
