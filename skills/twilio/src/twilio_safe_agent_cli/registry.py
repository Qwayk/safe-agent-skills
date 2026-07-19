from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path
from typing import Any

from .errors import ValidationError


@dataclass(frozen=True)
class CatalogRegistry:
    data: dict[str, Any]
    inventory_hash: str
    commands: dict[str, dict[str, Any]] = field(init=False)
    by_spec: dict[str, list[dict[str, Any]]] = field(init=False)

    def __post_init__(self) -> None:
        commands = {
            row["command"]: row
            for row in self.data.get("operations", [])
            if row.get("disposition") == "command" and row.get("command")
        }
        object.__setattr__(self, "commands", commands)
        by_spec: dict[str, list[dict[str, Any]]] = {}
        for row in commands.values():
            by_spec.setdefault(row["spec_id"], []).append(row)
        for rows in by_spec.values():
            rows.sort(key=lambda item: item["command"])
        object.__setattr__(self, "by_spec", by_spec)

    def get(self, command: str) -> dict[str, Any] | None:
        return self.commands.get(command)

    def summary(self) -> dict[str, Any]:
        counts = self.data["counts"]
        return {
            "raw_operations": counts["raw_operations"],
            "commands": counts["command"],
            "legacy_eol": counts["legacy_eol"],
            "canonical_duplicates": counts["canonical_duplicate"],
            "developer_preview": counts["developer_preview"],
            "private_or_unavailable": counts["private_or_unavailable"],
            "specs": self.data["source"]["spec_count"],
            "pinned_commit": self.data["source"]["commit"],
            "inventory_hash": self.inventory_hash,
        }

    def paired_read(self, operation: dict[str, Any]) -> dict[str, Any] | None:
        for candidate in self.commands.values():
            if (
                candidate["method"] == "GET"
                and candidate["server"] == operation["server"]
                and candidate["path"] == operation["path"]
            ):
                return candidate
        return None

    def describe(self, command: str) -> dict[str, Any]:
        operation = self.get(command)
        if operation is None:
            raise ValidationError(f"Unknown fixed Twilio command: {command}")
        input_contract: dict[str, Any] = {}
        for location, section in (("path", "path"), ("query", "query"), ("header", "headers")):
            parameters = []
            for parameter in operation.get("parameters", []):
                if parameter.get("in") != location:
                    continue
                schema = parameter.get("schema") or {}
                parameters.append(
                    {
                        "name": parameter["name"],
                        "required": bool(parameter.get("required")),
                        "type": schema.get("type") or "object",
                        "array": schema.get("type") == "array",
                        "explode": parameter.get("explode", True),
                    }
                )
            input_contract[section] = parameters

        request = operation.get("request")
        if request:
            fields: dict[str, str] = {}
            required_fields: set[str] = set()
            required_any_of: list[list[str]] = []

            def collect(schema: Any, *, include_required: bool = True) -> None:
                if not isinstance(schema, dict):
                    return
                for member in schema.get("allOf") or []:
                    collect(member, include_required=include_required)
                for group in ("oneOf", "anyOf"):
                    alternatives = []
                    for member in schema.get(group) or []:
                        if isinstance(member, dict):
                            names = [str(name) for name in member.get("required") or []]
                            if names:
                                alternatives.append(names)
                        collect(member, include_required=False)
                    if alternatives:
                        required_any_of.extend(alternatives)
                if include_required:
                    required_fields.update(str(name) for name in schema.get("required") or [])
                for name, field_schema in (schema.get("properties") or {}).items():
                    field_type = field_schema.get("type") if isinstance(field_schema, dict) else None
                    fields[str(name)] = str(field_type or "object")

            for media_type in request.get("media_types", []):
                collect(request["schemas"][media_type].get("resolved_schema"))
            input_contract["body"] = {
                "media_types": request.get("media_types", []),
                "required": bool(request.get("required")),
                "required_fields": sorted(required_fields),
                "required_any_of": required_any_of,
                "fields": {name: fields[name] for name in sorted(fields)},
            }
        else:
            input_contract["body"] = None

        requirements = operation.get("security", {}).get("requirements", [])
        return {
            "ok": True,
            "command": operation["command"],
            "method": operation["method"],
            "path": operation["path"],
            "input": input_contract,
            "auth_schemes": sorted({name for alternative in requirements for name in alternative}),
            "risks": operation.get("risk_flags", []),
            "preview": bool(operation.get("classification", {}).get("preview")),
            "access_gated": bool(operation.get("classification", {}).get("access_gated")),
            "scheduled_eol": operation.get("classification", {}).get("scheduled_eol"),
            "sensitive_output": bool(operation.get("pii_fields")),
            "snapshot_required": bool(operation.get("snapshot_required")),
            "snapshot_strategy": operation.get("snapshot_strategy"),
            "verification_strategy": operation.get("verification_strategy"),
        }


def load_registry(path: str | Path | None = None) -> CatalogRegistry:
    catalog_path = (
        Path(path)
        if path is not None
        else Path(str(files("twilio_safe_agent_cli").joinpath("generated/operations.json")))
    )
    try:
        raw = catalog_path.read_bytes()
        data = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        raise ValidationError(f"Twilio operation catalog is unavailable or invalid: {type(exc).__name__}") from None
    if data.get("counts") != {
        "canonical_duplicate": 9,
        "command": 1_325,
        "developer_preview": 5,
        "legacy_eol": 205,
        "private_or_unavailable": 6,
        "raw_operations": 1_550,
    }:
        raise ValidationError("Twilio operation catalog failed its pinned count check")
    return CatalogRegistry(data=data, inventory_hash=hashlib.sha256(raw).hexdigest())
