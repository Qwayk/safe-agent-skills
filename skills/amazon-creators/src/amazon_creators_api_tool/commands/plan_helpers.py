from __future__ import annotations

import time
from typing import Any, Sequence

from ..errors import ValidationError
from ..json_files import read_json_file, write_json_file


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
        "env_fingerprint": ctx["cfg"].account_fingerprint,
        "api_base_url": ctx["cfg"].base_url,
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


def check_saved_plan(path: str, current: dict[str, Any]) -> None:
    saved = read_json_file(path)
    if not isinstance(saved, dict):
        raise ValidationError("The saved preview must be a JSON plan. Create a new preview.")
    for field in ("tool", "env_fingerprint", "api_base_url", "selector", "payload"):
        if saved.get(field) != current[field]:
            raise ValidationError(
                "The account or request differs from the saved preview. Create and review a new preview."
            )
