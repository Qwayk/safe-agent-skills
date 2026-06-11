from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .openapi_ops import load_operation_specs, operation_command_line
from .openapi_snapshot import tool_root_dir
from .project_config import OPENAPI_COMMANDS_FILENAME, OPENAPI_OPERATIONS_FILENAME


def canonical_operation_ids() -> list[str]:
    specs = load_operation_specs()
    return [s.operation_id for s in specs]


def pinned_operations_path() -> Path:
    return tool_root_dir() / OPENAPI_OPERATIONS_FILENAME


def pinned_commands_path() -> Path:
    return tool_root_dir() / OPENAPI_COMMANDS_FILENAME


def operations_text(ops: list[str]) -> str:
    return "\n".join(ops) + ("\n" if ops else "")


def commands_text(cmds: list[str]) -> str:
    return "\n".join(cmds) + ("\n" if cmds else "")


def write_operations_file(*, ops: list[str], path: Path | None = None) -> Path:
    out_path = path or pinned_operations_path()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(operations_text(ops), encoding="utf-8")
    return out_path


def write_commands_file(*, commands: list[str], path: Path | None = None) -> Path:
    out_path = path or pinned_commands_path()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(commands_text(commands), encoding="utf-8")
    return out_path


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class InventoryValidation:
    ok: bool
    operation_count: int
    command_count: int
    pinned_path: str
    pinned_sha256: str | None
    regenerated_sha256: str
    mismatch: bool
    pinned_commands_path: str
    pinned_commands_sha256: str | None
    regenerated_commands_sha256: str
    commands_mismatch: bool
    errors: tuple[str, ...]


def canonical_commands() -> list[str]:
    specs = load_operation_specs()
    return [operation_command_line(s) for s in specs]


def validate_inventories() -> InventoryValidation:
    errors: list[str] = []
    try:
        specs = load_operation_specs()
        ops = [s.operation_id for s in specs]
        cmds = [operation_command_line(s) for s in specs]
    except Exception as e:  # pragma: no cover
        return InventoryValidation(
            ok=False,
            operation_count=0,
            command_count=0,
            pinned_path=str(pinned_operations_path()),
            pinned_sha256=None,
            regenerated_sha256="",
            mismatch=True,
            pinned_commands_path=str(pinned_commands_path()),
            pinned_commands_sha256=None,
            regenerated_commands_sha256="",
            commands_mismatch=True,
            errors=(f"Failed to load snapshot / derive operations: {e}",),
        )

    regen_text = operations_text(ops)
    regen_sha = sha256_text(regen_text)

    pinned = pinned_operations_path()
    if not pinned.exists():
        errors.append(f"Pinned operations file missing: {pinned}")
        pinned_text = ""
        pinned_sha = None
        mismatch = True
    else:
        pinned_text = pinned.read_text(encoding="utf-8")
        pinned_sha = sha256_text(pinned_text)
        mismatch = pinned_text != regen_text
        if mismatch:
            errors.append("Pinned operations file does not match regenerated operations list")

    regen_cmd_text = commands_text(cmds)
    regen_cmd_sha = sha256_text(regen_cmd_text)
    pinned_cmds = pinned_commands_path()
    if not pinned_cmds.exists():
        errors.append(f"Pinned commands file missing: {pinned_cmds}")
        pinned_cmd_text = ""
        pinned_cmd_sha = None
        cmds_mismatch = True
    else:
        pinned_cmd_text = pinned_cmds.read_text(encoding="utf-8")
        pinned_cmd_sha = sha256_text(pinned_cmd_text)
        cmds_mismatch = pinned_cmd_text != regen_cmd_text
        if cmds_mismatch:
            errors.append("Pinned commands file does not match regenerated commands list")

    if len(cmds) == 0:
        errors.append("Regenerated commands list is empty (expected one command per operation)")
    if len(set(cmds)) != len(cmds):
        errors.append("Regenerated commands list contains duplicates (command naming collision)")
    if len(set(ops)) != len(ops):
        # Should be impossible due to load_operation_specs() collision check, but keep a belt-and-suspenders error.
        errors.append("Regenerated operations list contains duplicates (operationId collision)")

    return InventoryValidation(
        ok=len(errors) == 0,
        operation_count=len(ops),
        command_count=len(cmds),
        pinned_path=str(pinned),
        pinned_sha256=pinned_sha,
        regenerated_sha256=regen_sha,
        mismatch=mismatch,
        pinned_commands_path=str(pinned_cmds),
        pinned_commands_sha256=pinned_cmd_sha,
        regenerated_commands_sha256=regen_cmd_sha,
        commands_mismatch=cmds_mismatch,
        errors=tuple(errors),
    )


# Backwards-compatible name used by earlier scaffolding/tests.
def validate_operations_inventory() -> InventoryValidation:
    return validate_inventories()
