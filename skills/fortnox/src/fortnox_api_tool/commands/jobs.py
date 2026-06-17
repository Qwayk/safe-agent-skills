from __future__ import annotations

from typing import Any


_UNSUPPORTED_MESSAGE = (
    "Fortnox jobs are not public yet in this CLI. The old demo ping rows were removed, and no registry-backed "
    "Fortnox batch rows are shipped yet."
)


def cmd_jobs_run(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    out = {
        "ok": False,
        "error": _UNSUPPORTED_MESSAGE,
        "error_type": "NotSupportedError",
        "supported": False,
    }
    if "audit" in ctx:
        ctx["audit"].write("jobs.unsupported", {"error": _UNSUPPORTED_MESSAGE})
    ctx["out"].emit(out)
    return 1
