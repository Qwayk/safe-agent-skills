from __future__ import annotations

import argparse

from ..inventory import (
    canonical_commands,
    canonical_operation_ids,
    pinned_commands_path,
    pinned_operations_path,
    validate_inventories,
    write_commands_inventory,
    write_operations_inventory,
)


def cmd_inventory_operations_list(args: argparse.Namespace, ctx: dict) -> int:
    _ = args
    ops = canonical_operation_ids()
    payload = {"ok": True, "operations": ops, "count": len(ops), "pinned_path": str(pinned_operations_path())}
    ctx["audit"].write("inventory.operations.list", payload)
    ctx["out"].emit(payload)
    return 0


def cmd_inventory_commands_list(args: argparse.Namespace, ctx: dict) -> int:
    _ = args
    cmds = canonical_commands()
    payload = {"ok": True, "commands": cmds, "count": len(cmds), "pinned_path": str(pinned_commands_path())}
    ctx["audit"].write("inventory.commands.list", payload)
    ctx["out"].emit(payload)
    return 0


def cmd_inventory_operations_write(args: argparse.Namespace, ctx: dict) -> int:
    _ = args
    p = write_operations_inventory()
    payload = {"ok": True, "wrote_to": str(p), "count": len(canonical_operation_ids())}
    ctx["audit"].write("inventory.operations.write", payload)
    ctx["out"].emit(payload)
    return 0


def cmd_inventory_commands_write(args: argparse.Namespace, ctx: dict) -> int:
    _ = args
    p = write_commands_inventory()
    payload = {"ok": True, "wrote_to": str(p), "count": len(canonical_commands())}
    ctx["audit"].write("inventory.commands.write", payload)
    ctx["out"].emit(payload)
    return 0


def cmd_inventory_validate(args: argparse.Namespace, ctx: dict) -> int:
    _ = args
    v = validate_inventories()
    payload = {"ok": v.ok, **v.__dict__}
    ctx["audit"].write("inventory.validate", payload)
    ctx["out"].emit(payload)
    return 0

