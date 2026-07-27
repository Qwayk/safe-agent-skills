from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from typing import Any

from .errors import ValidationError


@lru_cache(maxsize=1)
def load_inventory() -> dict[str, Any]:
    path = files("asana_safe_agent_cli").joinpath("inventory/operations.json")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("operations"), list):
        raise RuntimeError("Packaged Asana operation inventory is invalid")
    return value


def manifest() -> dict[str, Any]:
    value = load_inventory().get("manifest")
    if not isinstance(value, dict):
        raise RuntimeError("Packaged Asana inventory manifest is invalid")
    return value


def operations() -> list[dict[str, Any]]:
    return list(load_inventory()["operations"])


@lru_cache(maxsize=1)
def _by_command() -> dict[str, dict[str, Any]]:
    return {
        str(operation["command"]): operation
        for operation in operations()
        if operation.get("command")
    }


@lru_cache(maxsize=1)
def _by_operation_id() -> dict[str, dict[str, Any]]:
    return {str(operation["operation_id"]): operation for operation in operations()}


def command_names() -> tuple[str, ...]:
    return tuple(sorted(_by_command()))


def operation_for_command(command: str) -> dict[str, Any]:
    try:
        return _by_command()[command]
    except KeyError:
        raise ValidationError(f"Unknown fixed Asana command: {command}") from None


def operation_for_id(operation_id: str) -> dict[str, Any]:
    try:
        return _by_operation_id()[operation_id]
    except KeyError:
        raise ValidationError(f"Unknown Asana operation ID: {operation_id}") from None
