from __future__ import annotations

import time
from typing import Any

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file
from .write_safety import (
    before_state_contract,
    before_state_refusal_output,
    before_state_refusal_verification_plan,
    no_inverse_recovery_contract,
)


DEMO_WRITE_REFUSAL_REASON = (
    "Refused: Unsplash demo write is template-only and has no live provider write executor."
)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def cmd_demo_read(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    out = {"ok": True, "message": "demo read (safe)", "env": ctx["cfg"].base_url}
    ctx["audit"].write("demo.read", out)
    ctx["out"].emit(out)
    return 0


def _build_demo_plan(*, selector: str, ctx: dict[str, Any]) -> dict[str, Any]:
    restore_note = "Demo write is a stubbed workflow in this tool. This CLI has no automatic rollback."
    return {
        "tool": ctx.get("tool") or "unsplash-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": {"kind": "demo", "value": selector},
        "risk_level": "medium",
        "risk_reasons": ["write-demo"],
        "preconditions": ["env_fingerprint must match", "selector must match"],
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
        },
        "before_state": before_state_contract(
            reason=(
                "Demo write is a stubbed write surface and does not save real before-state. "
                "Successful stub receipts would overstate source safety."
            ),
            local_state={"selector": selector},
        ),
        "proposed_changes": [{"field": "demo_field", "from": "<unknown>", "to": "new_value"}],
        "verification_plan": before_state_refusal_verification_plan(),
        "recovery": no_inverse_recovery_contract(restore_note=restore_note),
    }


def _ensure_demo_safety_contract(plan: dict[str, Any], *, selector: str) -> dict[str, Any]:
    restore_note = "Demo write is a stubbed workflow in this tool. This CLI has no automatic rollback."
    plan["before_state"] = before_state_contract(
        reason=(
            "Demo write is a stubbed write surface and does not save real before-state. "
            "Successful stub receipts would overstate source safety."
        ),
        local_state={"selector": selector},
    )
    plan["verification_plan"] = before_state_refusal_verification_plan()
    plan["recovery"] = no_inverse_recovery_contract(restore_note=restore_note)
    return plan


def _validate_plan_for_apply(plan: dict[str, Any], *, selector: str, ctx: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if str(baseline.get("selector") or "") != str(selector):
        raise SafetyError("Refused: plan selector does not match current selector")


def cmd_demo_write(args: Any, ctx: dict[str, Any]) -> int:
    selector = str(getattr(args, "selector", "") or "").strip()
    if not selector:
        raise ValidationError("Missing --selector")

    plan_in = ctx.get("plan_in")
    if plan_in:
        plan_obj = read_json_file(plan_in)
        if not isinstance(plan_obj, dict):
            raise ValidationError("Plan file must be a JSON object")
        plan = plan_obj
    else:
        plan = _build_demo_plan(selector=selector, ctx=ctx)
    plan = _ensure_demo_safety_contract(plan, selector=selector)

    plan_out = ctx.get("plan_out")
    if plan_out and not bool(ctx.get("apply")):
        plan_path = write_json_file(plan_out, plan)
    else:
        plan_path = None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("demo.write.plan", {"plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    try:
        _validate_plan_for_apply(plan, selector=selector, ctx=ctx)
    except SafetyError as e:
        out = {"ok": True, "dry_run": False, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError"}
        ctx["audit"].write("demo.write.refused", out)
        ctx["out"].emit(out)
        return 0

    out = before_state_refusal_output(plan, reason=DEMO_WRITE_REFUSAL_REASON)
    ctx["audit"].write("demo.write.refused", out)
    ctx["out"].emit(out)
    return 0
