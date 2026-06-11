from __future__ import annotations

import time
from typing import Any, Sequence

from ..json_files import write_json_file


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def build_plan(
    ctx: dict[str, Any],
    *,
    selector: dict[str, Any],
    payload: dict[str, Any],
    risk_level: str = "low",
    risk_reasons: Sequence[str] | None = None,
    preconditions: Sequence[str] | None = None,
    verification_plan: dict[str, Any] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    plan: dict[str, Any] = {
        "tool": ctx.get("tool") or "amazon-creators-api-tool",
        "version": ctx.get("tool_version"),
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str"),
        "selector": selector,
        "risk_level": risk_level,
        "risk_reasons": list(risk_reasons or []),
        "payload": payload,
        "preconditions": list(preconditions or ["Run with --apply to contact Amazon Creators API"]),
    }
    if verification_plan:
        plan["verification_plan"] = verification_plan
    if extra:
        plan.update(extra)
    return plan


def write_plan(ctx: dict[str, Any], plan: dict[str, Any]) -> str | None:
    plan_out = ctx.get("plan_out")
    if not plan_out:
        return None
    return write_json_file(plan_out, plan)
