from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path
from typing import Any

from .errors import ValidationError

EXPECTED_COUNTS = {
    "command": 474,
    "manual_operations": 2,
    "raw_openapi_operations": 477,
    "superseded_compatibility": 5,
}

EXPECTED_CATALOG_SHA256 = "d62c9c6acf60ec5c556c4cf66fd779fe1704cc7ef87d34a4dd51af95ae8fc004"
ALLOWED_METHODS = {"DELETE", "GET", "PATCH", "POST", "PUT"}
ALLOWED_SERVERS = {
    "https://api.xero.com",
    "https://api.xero.com/api.xro/2.0",
    "https://api.xero.com/appstore/2.0",
    "https://api.xero.com/assets.xro/1.0",
    "https://api.xero.com/bankfeeds.xro/1.0",
    "https://api.xero.com/einvoicing.xro/1.0",
    "https://api.xero.com/files.xro/1.0",
    "https://api.xero.com/finance.xro/1.0",
    "https://api.xero.com/payroll.xro/1.0",
    "https://api.xero.com/payroll.xro/2.0",
    "https://api.xero.com/projects.xro/2.0",
}
COMMAND_PATTERN = re.compile(
    r"^[a-z0-9]+(?:-[a-z0-9]+)*\.[a-z0-9]+(?:-[a-z0-9]+)*$"
)


def _validate_fixed_surface(data: dict[str, Any]) -> None:
    operations = data.get("operations")
    if not isinstance(operations, list):
        raise ValidationError("Xero operation catalog has no fixed operation list")
    for row in operations:
        if not isinstance(row, dict):
            raise ValidationError("Xero operation catalog contains a non-object row")
        if row.get("disposition") != "command":
            continue
        command = str(row.get("command") or "")
        spec_id = str(row.get("spec_id") or "")
        server = str(row.get("server") or "")
        method = str(row.get("method") or "")
        path = str(row.get("path") or "")
        if not COMMAND_PATTERN.fullmatch(command) or not command.startswith(spec_id + "."):
            raise ValidationError("Xero operation catalog contains an unsafe command name")
        if server not in ALLOWED_SERVERS:
            raise ValidationError("Xero operation catalog contains an unapproved server")
        if method not in ALLOWED_METHODS:
            raise ValidationError("Xero operation catalog contains an unapproved HTTP method")
        if (
            not path.startswith("/")
            or "://" in path
            or "?" in path
            or "#" in path
            or "\\" in path
        ):
            raise ValidationError("Xero operation catalog contains an unsafe provider path")
        placeholders = set(re.findall(r"\{([^{}]+)\}", path))
        path_parameters = {
            str(item.get("name") or "")
            for item in row.get("parameters") or []
            if isinstance(item, dict) and item.get("in") == "path" and item.get("required")
        }
        if placeholders != path_parameters:
            raise ValidationError("Xero operation catalog path parameters do not match its path")


@dataclass(frozen=True)
class CatalogRegistry:
    data: dict[str, Any]
    inventory_hash: str
    commands: dict[str, dict[str, Any]] = field(init=False)

    def __post_init__(self) -> None:
        commands = {
            str(row["command"]): row
            for row in self.data.get("operations", [])
            if row.get("disposition") == "command" and row.get("command")
        }
        if len(commands) != EXPECTED_COUNTS["command"]:
            raise ValidationError("Xero operation catalog failed its fixed-command count check")
        object.__setattr__(self, "commands", commands)

    def get(self, command: str) -> dict[str, Any] | None:
        return self.commands.get(command)

    def summary(self) -> dict[str, Any]:
        source = self.data["source"]
        counts = self.data["counts"]
        return {
            "pinned_release": source["release"],
            "pinned_commit": source["commit"],
            "openapi_operations": counts["raw_openapi_operations"],
            "manual_operations": counts["manual_operations"],
            "commands": counts["command"],
            "superseded_compatibility": counts["superseded_compatibility"],
            "callback_only_specs": source["callback_spec_count"],
            "inventory_hash": self.inventory_hash,
        }

    def minimum_scopes(self, command_names: list[str], *, offline: bool) -> list[str]:
        scopes: set[str] = set()
        for name in command_names:
            operation = self.get(name)
            if operation is None:
                raise ValidationError(f"Unknown fixed Xero command: {name}")
            if operation["auth_flow"] == "client_credentials":
                raise ValidationError(
                    f"{name} uses the separate App Store client-credentials flow, not PKCE"
                )
            scopes.update(operation.get("minimum_scopes") or [])
        scopes = {
            scope
            for scope in scopes
            if not (scope.endswith(".read") and scope[: -len(".read")] in scopes)
        }
        if offline:
            scopes.add("offline_access")
        return sorted(scopes)

    def client_credentials_scopes(self, profile: str) -> set[str]:
        if profile == "app-store":
            return {"app.connections", "marketplace.billing"}
        if profile != "custom":
            raise ValidationError("Unknown client-credentials profile")
        return {
            str(scope)
            for operation in self.commands.values()
            if operation.get("tenant_required")
            for scope in operation.get("minimum_scopes") or []
            if scope not in {"openid", "offline_access"}
            and scope not in {"app.connections", "marketplace.billing"}
        }

    def describe(self, command: str) -> dict[str, Any]:
        operation = self.get(command)
        if operation is None:
            raise ValidationError(f"Unknown fixed Xero command: {command}")
        parameters: dict[str, list[dict[str, Any]]] = {
            "path": [],
            "query": [],
            "header": [],
        }
        for parameter in operation.get("parameters") or []:
            location = parameter.get("in")
            is_auto_tenant_header = (
                str(parameter.get("name", "")).lower() == "xero-tenant-id"
                and operation.get("spec_id") != "identity"
            )
            if location in parameters and not is_auto_tenant_header:
                parameters[location].append(parameter)
        request = operation.get("request")
        body = None
        if request:
            body = {
                "required": bool(request.get("required")),
                "media_types": sorted((request.get("content") or {}).keys()),
                "schemas": request.get("content") or {},
            }
        return {
            "ok": True,
            "command": command,
            "summary": operation.get("summary"),
            "method": operation["method"],
            "server": operation["server"],
            "path": operation["path"],
            "input": {**parameters, "body": body},
            "minimum_scopes": operation.get("minimum_scopes") or [],
            "scope_status": operation.get("scope_status"),
            "auth_flow": operation.get("auth_flow"),
            "tenant_required": bool(operation.get("tenant_required")),
            "tenant_bound_path_parameters": operation.get("tenant_bound_path_parameters") or [],
            "required_one_of_headers": operation.get("required_one_of_headers") or [],
            "region": operation.get("region"),
            "excluded_regions": operation.get("excluded_regions") or [],
            "access_gated": bool(operation.get("access_gated")),
            "access_reason": operation.get("access_reason"),
            "risk_flags": operation.get("risk_flags") or [],
            "extra_approval": bool(operation.get("extra_approval")),
            "sensitive_output": bool(operation.get("sensitive_output")),
            "response_media_types": operation.get("response_media_types") or [],
            "preferred_accept": operation.get("preferred_accept") or "application/json",
            "idempotency_supported": bool(operation.get("idempotency_supported")),
            "snapshot_strategy": operation.get("snapshot_strategy"),
            "verification_strategy": operation.get("verification_strategy"),
            "verification_command": operation.get("verification_command"),
            "scheduled_retirement": operation.get("scheduled_retirement"),
        }


def load_registry(path: str | Path | None = None) -> CatalogRegistry:
    catalog_path = (
        Path(path)
        if path is not None
        else Path(str(files("xero_safe_agent_cli").joinpath("generated/operations.json")))
    )
    try:
        raw = catalog_path.read_bytes()
        data = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        raise ValidationError(
            f"Xero operation catalog is unavailable or invalid: {type(exc).__name__}"
        ) from None
    inventory_hash = hashlib.sha256(raw).hexdigest()
    if inventory_hash != EXPECTED_CATALOG_SHA256:
        raise ValidationError("Xero operation catalog failed its pinned SHA-256 check")
    if data.get("counts") != EXPECTED_COUNTS:
        raise ValidationError("Xero operation catalog failed its pinned count check")
    if data.get("source", {}).get("commit") != "e952d0bda3628facbf7afc5990ad6a0e7e77bd1e":
        raise ValidationError("Xero operation catalog failed its pinned commit check")
    _validate_fixed_surface(data)
    return CatalogRegistry(data=data, inventory_hash=inventory_hash)
