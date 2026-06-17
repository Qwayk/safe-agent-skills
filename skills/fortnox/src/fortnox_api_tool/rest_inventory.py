from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RestGroupSummary:
    group_name: str
    family_count: int
    operation_count: int


@dataclass(frozen=True)
class RestFamilySummary:
    family_slug: str
    official_labels: tuple[str, ...]
    group_names: tuple[str, ...]
    operation_count: int
    planned_cli_prefix: str
    ship_status: str
    notes: str


@dataclass(frozen=True)
class RestOperation:
    group_name: str
    family_name: str
    family_slug: str
    operation_id: str
    title: str
    http_method: str
    path: str
    path_params: tuple[str, ...]
    action_slug: str
    cli_command: str
    ship_status: str
    proof_status: str
    notes: str


@dataclass(frozen=True)
class RestInventory:
    source_url: str
    audited_utc: str
    rendered_family_count: int
    unique_family_slug_count: int
    operation_count: int
    notes: tuple[str, ...]
    group_summaries: tuple[RestGroupSummary, ...]
    family_summaries: tuple[RestFamilySummary, ...]
    operations: tuple[RestOperation, ...]


def _vendor_dir() -> Path:
    return Path(__file__).resolve().parent / "_vendor"


def _load_raw_inventory() -> dict:
    path = _vendor_dir() / "rest_inventory.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise RuntimeError(f"Unexpected REST inventory payload in {path}")
    return raw


def load_rest_inventory() -> RestInventory:
    raw = _load_raw_inventory()
    group_summaries = tuple(
        RestGroupSummary(
            group_name=str(item["group_name"]),
            family_count=int(item["family_count"]),
            operation_count=int(item["operation_count"]),
        )
        for item in raw["group_summaries"]
    )
    family_summaries = tuple(
        RestFamilySummary(
            family_slug=str(item["family_slug"]),
            official_labels=tuple(str(label) for label in item["official_labels"]),
            group_names=tuple(str(group_name) for group_name in item["group_names"]),
            operation_count=int(item["operation_count"]),
            planned_cli_prefix=str(item["planned_cli_prefix"]),
            ship_status=str(item["ship_status"]),
            notes=str(item.get("notes") or ""),
        )
        for item in raw["family_summaries"]
    )
    operations = tuple(
        RestOperation(
            group_name=str(item["group_name"]),
            family_name=str(item["family_name"]),
            family_slug=str(item["family_slug"]),
            operation_id=str(item["operation_id"]),
            title=str(item["title"]),
            http_method=str(item["http_method"]),
            path=str(item["path"]),
            path_params=tuple(str(param) for param in item["path_params"]),
            action_slug=str(item["action_slug"]),
            cli_command=str(item["cli_command"]),
            ship_status=str(item["ship_status"]),
            proof_status=str(item["proof_status"]),
            notes=str(item.get("notes") or ""),
        )
        for item in raw["operations"]
    )
    return RestInventory(
        source_url=str(raw["source_url"]),
        audited_utc=str(raw["audited_utc"]),
        rendered_family_count=int(raw["rendered_family_count"]),
        unique_family_slug_count=int(raw["unique_family_slug_count"]),
        operation_count=int(raw["operation_count"]),
        notes=tuple(str(note) for note in raw["notes"]),
        group_summaries=group_summaries,
        family_summaries=family_summaries,
        operations=operations,
    )


def load_rest_operations() -> tuple[RestOperation, ...]:
    return load_rest_inventory().operations


def planned_cli_commands() -> tuple[str, ...]:
    return tuple(operation.cli_command for operation in load_rest_operations())


def operation_ids() -> tuple[str, ...]:
    return tuple(operation.operation_id for operation in load_rest_operations())


def find_operation(operation_id: str) -> RestOperation | None:
    target = str(operation_id or "").strip()
    if not target:
        return None
    for operation in load_rest_operations():
        if operation.operation_id == target:
            return operation
    return None
