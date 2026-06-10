from __future__ import annotations

from typing import Any

_LEGACY_NOTICE = "The `demo` command family is a legacy placeholder and is not part of the shipped Merchant CLI surface."


def _emit_legacy_message(*, action: str, ctx: dict[str, Any], args: Any) -> int:
    _ = args
    out = {
        "ok": False,
        "legacy": True,
        "command": f"demo {action}",
        "error": _LEGACY_NOTICE,
        "error_type": "LegacyCommandError",
    }
    if "out" in ctx:
        ctx["out"].emit(out)
    if "audit" in ctx:
        ctx["audit"].write("demo.legacy_guard", out)
    return 1


def cmd_demo_read(args: Any, ctx: dict[str, Any]) -> int:
    return _emit_legacy_message(action="read", args=args, ctx=ctx)


def cmd_demo_write(args: Any, ctx: dict[str, Any]) -> int:
    return _emit_legacy_message(action="write", args=args, ctx=ctx)
