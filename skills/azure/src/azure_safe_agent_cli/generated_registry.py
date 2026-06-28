from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _inventory_path(root: Path | None = None) -> Path:
    base = root or _repo_root()
    return base / "docs" / "official_inventory.json"


def slugify(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")


@dataclass(frozen=True)
class AzureRegistry:
    data: dict[str, Any]

    def __post_init__(self) -> None:
        service_index: dict[str, dict[str, Any]] = {}
        operation_index: dict[tuple[str, str], dict[str, Any]] = {}
        for service in self.data.get("services", []):
            service_id = str(service.get("service_id") or "").strip()
            if service_id:
                service_index.setdefault(service_id, service)
                service_index.setdefault(slugify(service_id), service)
            for operation in service.get("operations", []):
                op_name = str(operation.get("operation_name") or "").strip()
                if service_id and op_name:
                    operation_index[(service_id, op_name)] = operation
                    operation_index[(slugify(service_id), slugify(op_name))] = operation
        object.__setattr__(self, "_service_index", service_index)
        object.__setattr__(self, "_operation_index", operation_index)

    def get_service(self, service_name: str) -> dict[str, Any] | None:
        key = service_name.strip()
        return self._service_index.get(key) or self._service_index.get(slugify(key))

    def get_operation(self, service_name: str, operation_name: str) -> dict[str, Any] | None:
        return self._operation_index.get((service_name.strip(), operation_name.strip())) or self._operation_index.get(
            (slugify(service_name), slugify(operation_name))
        )


def load_inventory(root: Path | None = None) -> dict[str, Any]:
    return json.loads(_inventory_path(root).read_text(encoding="utf-8"))


def load_registry(root: Path | None = None) -> AzureRegistry:
    return AzureRegistry(load_inventory(root))
