from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _inventory_path(root: Path | None = None) -> Path:
    base = root or _repo_root()
    return base / "docs" / "_generated" / "gcp_discovery_inventory.json"


def _slugify(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")


@dataclass(frozen=True)
class DiscoveryRegistry:
    data: dict[str, Any]

    def __post_init__(self) -> None:
        service_index: dict[str, dict[str, Any]] = {}
        operation_index: dict[tuple[str, str], dict[str, Any]] = {}
        for service in self.data.get("services", []):
            api_id = str(service.get("api_id") or "").strip()
            version = str(service.get("version") or "").strip()
            key = api_id
            if api_id:
                service_index.setdefault(_slugify(api_id), service)
                if version:
                    service_index.setdefault(_slugify(f"{api_id}:{version}"), service)
                    service_index.setdefault(f"{api_id}:{version}", service)
            for operation in service.get("operations", []):
                op_name = str(operation.get("operation_name") or "").strip()
                if api_id and op_name:
                    operation_index[(_slugify(api_id), _slugify(op_name))] = operation
                    operation_index[(api_id, op_name)] = operation
        object.__setattr__(self, "_service_index", service_index)
        object.__setattr__(self, "_operation_index", operation_index)

    def get_service(self, service_name: str) -> dict[str, Any] | None:
        key = service_name.strip()
        return self._service_index.get(key) or self._service_index.get(_slugify(key))

    def has_service(self, service_name: str) -> bool:
        return self.get_service(service_name) is not None

    def get_operation(self, service_name: str, operation_name: str) -> dict[str, Any] | None:
        key = (service_name.strip(), operation_name.strip())
        return self._operation_index.get(key) or self._operation_index.get((_slugify(key[0]), _slugify(key[1])))

    def has_operation(self, service_name: str, operation_name: str) -> bool:
        return self.get_operation(service_name, operation_name) is not None


def load_inventory(root: Path | None = None) -> dict[str, Any]:
    path = _inventory_path(root)
    return json.loads(path.read_text(encoding="utf-8"))


def load_registry(root: Path | None = None) -> DiscoveryRegistry:
    return DiscoveryRegistry(load_inventory(root))
