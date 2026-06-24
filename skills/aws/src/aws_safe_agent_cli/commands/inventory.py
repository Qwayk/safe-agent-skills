from __future__ import annotations

from typing import Any

from ..generated_registry import load_generated_registry


def cmd_inventory_summary(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    registry = ctx.get("registry") or load_generated_registry()
    payload = {"ok": True, "inventory": registry.summary_payload()}
    ctx["audit"].write("inventory.summary", payload)
    ctx["out"].emit(payload)
    return 0

