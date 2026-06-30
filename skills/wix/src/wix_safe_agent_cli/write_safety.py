from __future__ import annotations

from typing import Any

from .errors import SafetyError


def reviewed_plan_apply_requested(
    ctx: dict[str, Any],
    *,
    requires_ack: bool = False,
    command_label: str | None = None,
) -> bool:
    if not bool(ctx.get("apply")):
        return False
    if not bool(ctx.get("yes")):
        return False
    if requires_ack and not bool(ctx.get("ack_irreversible")):
        return False
    if not bool(ctx.get("enforce_reviewed_plan")):
        return True
    if not ctx.get("plan_in"):
        label = command_label or "this command"
        ack_suffix = " --ack-irreversible" if requires_ack else ""
        raise SafetyError(
            f"Refused: {label} live apply requires a reviewed saved plan. "
            f"First run with --plan-out, review the plan, then rerun with --plan-in --apply --yes{ack_suffix}."
        )
    return True
