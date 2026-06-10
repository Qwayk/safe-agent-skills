from __future__ import annotations

from typing import Any

_LEGACY_NOTICE = "The `jobs` command is a legacy placeholder and is not part of the shipped Merchant CLI surface."


def cmd_jobs_run(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    out = {
        "ok": False,
        "legacy": True,
        "command": "jobs run",
        "error": _LEGACY_NOTICE,
        "error_type": "LegacyCommandError",
    }
    if "out" in ctx:
        ctx["out"].emit(out)
    if "audit" in ctx:
        ctx["audit"].write("jobs.legacy_guard", out)
    return 1
