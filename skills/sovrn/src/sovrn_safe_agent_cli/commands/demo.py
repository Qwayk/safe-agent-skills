from __future__ import annotations

import time
from typing import Any

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def cmd_demo_read(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    out = {"ok": True, "message": "demo read (safe)", "env_fingerprint": ctx["cfg"].env_fingerprint}
    ctx["audit"].write("demo.read", out)
    ctx["out"].emit(out)
    return 0


def _build_demo_plan(*, selector: str, ctx: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "sovrn-safe-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].env_fingerprint,
        "command": ctx.get("command_str") or None,
        "selector": {"kind": "demo", "value": selector},
        "risk_level": "medium",
        "risk_reasons": ["write-demo"],
        "preconditions": ["env_fingerprint must match", "selector must match"],
        "baseline": {
            "env_fingerprint": ctx["cfg"].env_fingerprint,
            "selector": selector,
        },
        "proposed_changes": [{"field": "demo_field", "from": "<unknown>", "to": "new_value"}],
        "verification_plan": {"type": "demo", "notes": "In a real tool: GET after PUT and assert fields."},
        "rollback": {"supported": False, "notes": "Demo command has no rollback."},
    }


def _validate_plan_for_apply(plan: dict[str, Any], *, selector: str, ctx: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].env_fingerprint):
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

    receipt = {
        "tool": ctx.get("tool") or "sovrn-safe-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].env_fingerprint,
        "selector": {"kind": "demo", "value": selector},
        "changed": True,
        "verification": {"ok": True, "details": {"type": "demo", "notes": "stub verify passed"}},
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }

    receipt_out = ctx.get("receipt_out")
    if receipt_out:
        receipt_path = write_json_file(receipt_out, receipt)
    else:
        receipt_path = None

    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("demo.write.apply", {"receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0
