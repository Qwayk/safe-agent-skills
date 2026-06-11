from __future__ import annotations

import argparse

from ..inventory import (
    canonical_commands,
    canonical_operation_ids,
    pinned_commands_path,
    pinned_operations_path,
    validate_inventories,
    write_commands_file,
    write_operations_file,
)


def cmd_inventory_operations_list(args: argparse.Namespace, ctx: dict) -> int:
    _ = args
    ops = canonical_operation_ids()
    ctx["out"].emit(
        {
            "ok": True,
            "operations": ops,
            "count": len(ops),
            "pinned_operations_path": str(pinned_operations_path()),
        }
    )
    return 0


def cmd_inventory_commands_list(args: argparse.Namespace, ctx: dict) -> int:
    _ = args
    cmds = canonical_commands()
    ctx["out"].emit(
        {
            "ok": True,
            "commands": cmds,
            "count": len(cmds),
            "pinned_commands_path": str(pinned_commands_path()),
        }
    )
    return 0


def cmd_inventory_commands_write(args: argparse.Namespace, ctx: dict) -> int:
    _ = args
    cmds = canonical_commands()
    out_path = write_commands_file(commands=cmds)
    ctx["out"].emit(
        {
            "ok": True,
            "wrote": True,
            "count": len(cmds),
            "pinned_commands_path": str(out_path),
        }
    )
    return 0


def cmd_inventory_operations_write(args: argparse.Namespace, ctx: dict) -> int:
    _ = args
    ops = canonical_operation_ids()
    out_path = write_operations_file(ops=ops)
    ctx["out"].emit(
        {
            "ok": True,
            "wrote": True,
            "count": len(ops),
            "pinned_operations_path": str(out_path),
        }
    )
    return 0


def cmd_inventory_validate(args: argparse.Namespace, ctx: dict) -> int:
    _ = args
    v = validate_inventories()
    ctx["out"].emit(
        {
            "ok": v.ok,
            "operation_count": v.operation_count,
            "command_count": v.command_count,
            "pinned_operations_path": v.pinned_path,
            "pinned_sha256": v.pinned_sha256,
            "regenerated_sha256": v.regenerated_sha256,
            "mismatch": v.mismatch,
            "pinned_commands_path": v.pinned_commands_path,
            "pinned_commands_sha256": v.pinned_commands_sha256,
            "regenerated_commands_sha256": v.regenerated_commands_sha256,
            "commands_mismatch": v.commands_mismatch,
            "errors": list(v.errors),
        }
    )
    return 0 if v.ok else 1
