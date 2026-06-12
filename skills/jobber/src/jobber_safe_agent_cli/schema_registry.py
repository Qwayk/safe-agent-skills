from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GraphQLTypeRef:
    kind: str
    name: str | None


@dataclass(frozen=True)
class FieldArgSpec:
    name: str
    description: str | None
    default: Any
    type: GraphQLTypeRef


@dataclass(frozen=True)
class OperationField:
    name: str
    description: str | None
    args: list[FieldArgSpec]
    type: GraphQLTypeRef


_SCHEMA_CACHE: dict[str, Any] | None = None


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _registry_path() -> Path:
    return _repo_root() / "docs" / "jobber_schema_inventory.json"


def _parse_type(raw: Any) -> GraphQLTypeRef:
    kind = str((raw or {}).get("kind") or "").strip() or "SCALAR"
    name = raw.get("name") if isinstance(raw, dict) else None
    if kind in {"NON_NULL", "LIST"} and isinstance(raw, dict) and isinstance(raw.get("ofType"), dict):
        of_type = raw.get("ofType") or {}
        return _parse_type(of_type)
    return GraphQLTypeRef(kind=kind, name=str(name) if name else None)


def _load_schema() -> dict[str, Any]:
    path = _registry_path()
    if not path.exists():
        raise RuntimeError(f"Missing schema registry: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _to_operation_fields(raw_fields: list[dict[str, Any]] | None) -> list[OperationField]:
    out: list[OperationField] = []
    if not isinstance(raw_fields, list):
        return out

    for field in raw_fields:
        if not isinstance(field, dict):
            continue
        name = str(field.get("name") or "").strip()
        if not name:
            continue
        args_raw = field.get("args") if isinstance(field.get("args"), list) else []
        args: list[FieldArgSpec] = []
        for item in args_raw:
            if not isinstance(item, dict):
                continue
            args.append(
                FieldArgSpec(
                    name=str(item.get("name") or "").strip(),
                    description=str(item.get("description") or "").strip() or None,
                    default=item.get("defaultValue"),
                    type=_parse_type(item.get("type") or {}),
                )
            )
        out.append(
            OperationField(
                name=name,
                description=str(field.get("description") or "").strip() or None,
                args=args,
                type=_parse_type(field.get("type") or {}),
            )
        )
    return out


def load_schema_registry() -> dict[str, Any]:
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE is not None:
        return _SCHEMA_CACHE

    raw = _load_schema()
    query_fields = _to_operation_fields(raw.get("query_fields") if isinstance(raw, dict) else None)
    mutation_fields = _to_operation_fields(raw.get("mutation_fields") if isinstance(raw, dict) else None)
    webhook_topics = raw.get("webhook_topics") if isinstance(raw.get("webhook_topics"), list) else []
    _SCHEMA_CACHE = {
        "query_count": len(query_fields),
        "mutation_count": len(mutation_fields),
        "query_fields": query_fields,
        "mutation_fields": mutation_fields,
        "webhook_topics": [str(x) for x in webhook_topics],
        "api_version_header": str(raw.get("api_version_header") or "2025-04-16").strip(),
        "fetched_utc": str(raw.get("fetched_utc") or "").strip() or None,
        "webhook_topic_count": len(webhook_topics),
    }
    return _SCHEMA_CACHE


def query_fields() -> list[OperationField]:
    return load_schema_registry()["query_fields"]


def mutation_fields() -> list[OperationField]:
    return load_schema_registry()["mutation_fields"]


def webhook_topics() -> list[str]:
    return load_schema_registry()["webhook_topics"]
