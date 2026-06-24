from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from .errors import ValidationError


def _kebab_from_operation_name(name: str) -> str:
    step1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    step2 = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", step1)
    return step2.replace("_", "-").lower()


@dataclass(frozen=True)
class InventorySummary:
    date: str
    boto3_version: str
    botocore_version: str
    service_count: int
    operation_count: int
    paginator_service_count: int
    paginator_count: int
    waiter_service_count: int
    waiter_count: int
    endpoints_model_version: int
    partitions_count: int
    services_with_multiple_versions: tuple[Any, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "date": self.date,
            "boto3_version": self.boto3_version,
            "botocore_version": self.botocore_version,
            "service_count": self.service_count,
            "operation_count": self.operation_count,
            "paginator_service_count": self.paginator_service_count,
            "paginator_count": self.paginator_count,
            "waiter_service_count": self.waiter_service_count,
            "waiter_count": self.waiter_count,
            "endpoints_model_version": self.endpoints_model_version,
            "partitions_count": self.partitions_count,
            "services_with_multiple_versions": list(self.services_with_multiple_versions),
        }


@dataclass(frozen=True)
class ServiceIndex:
    service: str
    api_version: str | None
    operation_names: tuple[str, ...]
    operation_kebabs: tuple[str, ...]

    @property
    def operations(self) -> tuple[tuple[str, str], ...]:
        return tuple(zip(self.operation_kebabs, self.operation_names, strict=True))


@dataclass(frozen=True)
class OperationIndex:
    service: str
    operation_name: str
    operation_kebab: str


@dataclass(frozen=True)
class GeneratedRegistry:
    inventory_path: Path
    summary: InventorySummary
    services: dict[str, ServiceIndex]

    def service_names(self) -> tuple[str, ...]:
        return tuple(self.services.keys())

    def get_service(self, service_name: str) -> ServiceIndex:
        service = self.services.get(service_name)
        if service is None:
            raise ValidationError(f"Unknown AWS service: {service_name}")
        return service

    def get_operation(self, service_name: str, operation_kebab: str) -> OperationIndex:
        service = self.get_service(service_name)
        lookup = dict(service.operations)
        operation_name = lookup.get(operation_kebab)
        if operation_name is None:
            raise ValidationError(
                f"Unknown operation for {service_name}: {operation_kebab} "
                f"(supported: {', '.join(service.operation_kebabs)})"
            )
        return OperationIndex(service=service_name, operation_name=operation_name, operation_kebab=operation_kebab)

    def summary_payload(self) -> dict[str, Any]:
        return self.summary.to_payload()


def _load_inventory_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValidationError("Inventory file must be a JSON object")
    return payload


@lru_cache(maxsize=1)
def load_generated_registry(inventory_path: str | None = None) -> GeneratedRegistry:
    path = Path(
        inventory_path
        or Path(__file__).resolve().parents[2] / "docs" / "_generated" / "aws_botocore_inventory.json"
    )
    payload = _load_inventory_payload(path)
    raw_services = payload.get("services", [])
    if not isinstance(raw_services, list):
        raise ValidationError("Inventory services must be a list")

    services: dict[str, ServiceIndex] = {}
    for row in raw_services:
        if not isinstance(row, dict):
            raise ValidationError("Inventory services must contain objects")
        service_name = str(row.get("service") or "").strip()
        if not service_name:
            raise ValidationError("Inventory service entry missing service name")
        raw_ops = row.get("operation_names", [])
        if not isinstance(raw_ops, list):
            raise ValidationError(f"Inventory service {service_name} has invalid operation_names")
        operation_names = tuple(str(name) for name in raw_ops if str(name).strip())
        operation_kebabs = tuple(_kebab_from_operation_name(name) for name in operation_names)
        services[service_name] = ServiceIndex(
            service=service_name,
            api_version=(str(row.get("api_version")) if row.get("api_version") else None),
            operation_names=operation_names,
            operation_kebabs=operation_kebabs,
        )

    summary = InventorySummary(
        date=str(payload.get("date") or ""),
        boto3_version=str(payload.get("boto3_version") or ""),
        botocore_version=str(payload.get("botocore_version") or ""),
        service_count=int(payload.get("service_count") or len(services)),
        operation_count=int(payload.get("operation_count") or 0),
        paginator_service_count=int(payload.get("paginator_service_count") or 0),
        paginator_count=int(payload.get("paginator_count") or 0),
        waiter_service_count=int(payload.get("waiter_service_count") or 0),
        waiter_count=int(payload.get("waiter_count") or 0),
        endpoints_model_version=int(payload.get("endpoints_model_version") or 0),
        partitions_count=int(payload.get("partitions_count") or 0),
        services_with_multiple_versions=tuple(
            item for item in payload.get("services_with_multiple_versions", []) if item is not None
        ),
    )
    return GeneratedRegistry(inventory_path=path, summary=summary, services=services)
