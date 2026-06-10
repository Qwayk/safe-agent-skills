from __future__ import annotations

import argparse
import time
from typing import Any
from typing import Type

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file
from ._write_safety import (
    build_before_state_refusal_verification_plan,
    build_no_recovery_contract,
    emit_before_state_refusal,
    ensure_before_state_refusal_plan,
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
    recovery = build_no_recovery_contract(notes="Demo write keeps the same proof-only no-recovery contract as the real Dynadot write paths.")
    plan = {
        "tool": ctx.get("tool") or "dynadot-api-tool",
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
        "proposed_changes": [{"field": "demo_field", "from": "<unknown>", "to": "new_value"}],
        "post_apply_verification_plan": {"type": "demo", "notes": "In a real tool: GET after PUT and assert fields."},
        "verification_plan": build_before_state_refusal_verification_plan(),
        "rollback": {"supported": False, "notes": "Demo command has no rollback."},
        "recovery": recovery,
    }
    ensure_before_state_refusal_plan(
        plan,
        selector_kind="demo",
        selector_value=selector,
        notes="Demo write has no real Dynadot provider write executor.",
    )
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
        ensure_before_state_refusal_plan(
            plan,
            selector_kind="demo",
            selector_value=selector,
            notes="Demo write has no real Dynadot provider write executor.",
        )
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

    if not plan_in:
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": ["Refused: demo write apply requires a reviewed plan file (--plan-in). Run the dry-run first."],
            "refusal_type": "SafetyError",
            "plan": plan,
            "plan_out": plan_path,
        }
        ctx["audit"].write("demo.write.refused", {"reason": "missing-plan-in", "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: demo write requires --apply --yes")

    try:
        _validate_plan_for_apply(plan, selector=selector, ctx=ctx)
    except SafetyError as e:
        out = {"ok": True, "dry_run": False, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError"}
        ctx["audit"].write("demo.write.refused", out)
        ctx["out"].emit(out)
        return 0
    return emit_before_state_refusal(ctx=ctx, plan=plan, audit_event="demo.write.refused")


def register_demo(
    subparsers: argparse._SubParsersAction,  # type: ignore[name-defined]
    *,
    parser_class: Type[argparse.ArgumentParser],
) -> None:
    demo = subparsers.add_parser("demo", help="Demo commands that show the v2 plan/receipt workflow")
    demo_sub = demo.add_subparsers(dest="demo_cmd", required=True, parser_class=parser_class)
    demo_read = demo_sub.add_parser("read", help="Safe read (demo)")
    demo_read.set_defaults(func=cmd_demo_read, write_capable=False)
    demo_write = demo_sub.add_parser("write", help="Write with plan/receipt (demo)")
    demo_write.add_argument("--selector", default="demo-resource", help="Target selector (demo)")
    demo_write.set_defaults(func=cmd_demo_write, write_capable=True)
