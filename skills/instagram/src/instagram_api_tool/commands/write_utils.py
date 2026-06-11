from __future__ import annotations

import time
from typing import Any, Callable

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file
from .write_safety import before_state_contract, before_state_refusal_output, before_state_refusal_verification_plan


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def split_csv_arg(raw: str | None) -> list[str]:
    if raw is None:
        return []
    text = str(raw).strip()
    if not text:
        return []
    return [part.strip() for part in text.split(",") if part.strip()]


def parse_bool_arg(value: Any, *, name: str = "value") -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        raise ValidationError(f"Missing --{name}")
    v = str(value).strip().lower()
    if v in {"true", "1", "yes", "on", "y"}:
        return True
    if v in {"false", "0", "no", "off", "n"}:
        return False
    raise ValidationError(f"--{name} must be true/false")


def build_write_plan(
    *,
    ctx: dict[str, Any],
    command: str,
    selector: dict[str, Any],
    risk_level: str = "medium",
    risk_reasons: list[str] | None = None,
    proposed_changes: list[dict[str, Any]] | None = None,
    preconditions: list[str] | None = None,
    verification: dict[str, Any] | None = None,
    rollback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if proposed_changes is None:
        proposed_changes = []
    if preconditions is None:
        preconditions = ["dry-run approved by user before apply"]
    if verification is None:
        verification = before_state_refusal_verification_plan()
    if rollback is None:
        rollback = {
            "mode": "irreversible_and_clearly_labeled",
            "supported": False,
            "automatic_rollback": False,
            "notes": (
                "No built-in rollback, backups, snapshots, or provider restore are available in this runtime. "
                "Treat current Instagram write families as irreversible_and_clearly_labeled and use the saved plan "
                "and receipt output for manual follow-up only."
            ),
        }

    plan = {
        "tool": ctx.get("tool") or "instagram-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": getattr(ctx["cfg"], "base_url", None),
        "command_id": command,
        "command": str(ctx.get("command_str") or command),
        "selector": selector,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons or ["write-operation"],
        "preconditions": preconditions,
        "baseline": {"env_fingerprint": getattr(ctx["cfg"], "base_url", None)},
        "proposed_changes": proposed_changes,
        "verification_plan": verification,
        "rollback": rollback,
    }
    plan["before_state"] = _before_state_contract_for_command(command=command, selector=selector, ctx=ctx)
    return plan


def _before_state_contract_for_command(
    *,
    command: str,
    selector: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    command_text = str(command)
    provider_write: dict[str, Any] | None = {
        "service": "Instagram Graph API",
        "command": command_text,
        "selector": selector,
        "base_url": getattr(ctx["cfg"], "base_url", None),
    }
    local_state: dict[str, Any] | None = None

    if command_text.startswith("auth"):
        local_state = {
            "kind": "token_file",
            "env_file": str(ctx.get("env_file") or ""),
            "path_hint": ".state/token.json next to the selected env file",
        }
        if command_text == "auth token set":
            provider_write = None

    return before_state_contract(
        reason=(
            "This source tool can build and review Instagram write plans, but it does not yet save "
            "operation-specific before-state or provider backup data before applying them."
        ),
        provider_write=provider_write,
        local_state=local_state,
    )


def _load_plan_for_apply(
    ctx: dict[str, Any],
    *,
    expected_command: str,
    expected_selector: dict[str, Any],
) -> dict[str, Any]:
    plan_path = str(ctx.get("plan_in") or "").strip()
    if not plan_path:
        return {}
    plan = read_json_file(plan_path)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")

    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    if str(baseline.get("env_fingerprint") or "") and str(baseline.get("env_fingerprint")) != str(
        getattr(ctx["cfg"], "base_url", "")
    ):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if str(plan.get("command_id") or "") != str(expected_command):
        raise SafetyError("Refused: plan command does not match the current write action")
    if plan.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match the current target")
    return plan


def run_write_command(
    *,
    ctx: dict[str, Any],
    selector: dict[str, Any],
    command: str,
    proposed_changes: list[dict[str, Any]] | None = None,
    execute: Callable[[], Any],
    requires_yes: bool = False,
    requires_ack: bool = False,
    risk_level: str = "medium",
) -> dict[str, Any]:
    if bool(ctx.get("plan_in")):
        _load_plan_for_apply(
            ctx,
            expected_command=command,
            expected_selector=selector,
        )

    if bool(ctx.get("apply")) is False:
        plan = build_write_plan(
            ctx=ctx,
            command=command,
            selector=selector,
            risk_level=risk_level,
            risk_reasons=["safe-dry-run"],
            proposed_changes=proposed_changes or [],
        )
        plan_out = str(ctx.get("plan_out")) if ctx.get("plan_out") else None
        if plan_out:
            plan_out = write_json_file(plan_out, plan)
        return {
            "ok": True,
            "dry_run": True,
            "plan": plan,
            "plan_out": plan_out,
        }

    if requires_yes and not bool(ctx.get("yes")):
        raise SafetyError(f"{command} requires --yes")
    if requires_ack and not bool(ctx.get("ack_irreversible")):
        raise SafetyError(f"{command} requires --ack-irreversible")

    plan = build_write_plan(
        ctx=ctx,
        command=command,
        selector=selector,
        risk_level=risk_level,
        risk_reasons=["write-operation"],
        proposed_changes=proposed_changes or [],
    )
    if not bool(ctx.get("ack_no_snapshot")):
        return before_state_refusal_output(plan)

    result = execute()
    reason = str(plan.get("before_state", {}).get("reason") or "No saved before-state snapshot is available for this write.")
    receipt = {
        "ok": True,
        "dry_run": False,
        "tool": ctx.get("tool") or "instagram-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": getattr(ctx["cfg"], "base_url", None),
        "command_id": command,
        "command": str(ctx.get("command_str") or command),
        "selector": selector,
        "changed": True,
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": reason,
        },
        "write_result": result,
        "verification_plan": plan.get("verification_plan"),
        "rollback": plan.get("rollback"),
    }
    receipt_out = str(ctx.get("receipt_out") or "").strip()
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    return {
        "ok": True,
        "dry_run": False,
        "receipt": receipt,
        "receipt_out": receipt_path,
        "result": result,
    }
