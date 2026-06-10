from __future__ import annotations

import time
from typing import Any

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file
from .write_safety import (
    before_state_refusal_verification_plan,
    blocked_before_state,
    refusal_output,
    rollback_contract,
)

IRREVERSIBLE_WRITE_MODE = "irreversible_and_clearly_labeled"


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _current_env_fingerprint(ctx: dict[str, Any]) -> str:
    return str(ctx.get("env_fingerprint") or str(ctx["cfg"].base_url))


def _rollback_contract(*, requires_ack_irreversible: bool = False) -> dict[str, Any]:
    return rollback_contract(requires_ack_irreversible=requires_ack_irreversible)


def cmd_demo_read(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    out = {"ok": True, "message": "demo read (safe)", "env": ctx["cfg"].base_url}
    ctx["audit"].write("demo.read", out)
    ctx["out"].emit(out)
    return 0


def _build_demo_plan(*, selector: str, ctx: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "threads-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": _current_env_fingerprint(ctx),
        "command": ctx.get("command_str") or None,
        "selector": {"kind": "demo", "value": selector},
        "risk_level": "medium",
        "risk_reasons": ["write-demo"],
        "preconditions": ["env_fingerprint must match", "selector must match"],
        "baseline": {
            "env_fingerprint": _current_env_fingerprint(ctx),
            "selector": selector,
        },
        "proposed_changes": [{"field": "demo_field", "from": "<unknown>", "to": "new_value"}],
        "before_state": blocked_before_state(
            action="demo.write",
            proposed_changes=[{"field": "demo_field", "from": "<unknown>", "to": "new_value"}],
            local_state={"kind": "demo_write", "writes_stub_receipt": True},
        ),
        "verification_plan": before_state_refusal_verification_plan(),
        "rollback": _rollback_contract(),
    }


def _validate_plan_for_apply(plan: dict[str, Any], *, selector: str, ctx: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    if str(baseline.get("env_fingerprint") or "") != _current_env_fingerprint(ctx):
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

    plan_out = ctx.get("plan_out")
    if plan_out:
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

    out = refusal_output(plan=plan)
    ctx["audit"].write("demo.write.refused", out)
    ctx["out"].emit(out)
    return 0
