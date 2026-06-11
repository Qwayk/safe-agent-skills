from __future__ import annotations

import time
from typing import Any


BEFORE_STATE_REFUSAL_REASON = (
    "Refused: this Amazon Creators local write helper has no live apply executor in this command. "
    "Use the dry-run plan for review only."
)


def before_state_contract(
    *,
    reason: str,
    local_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "required": True,
        "supported": False,
        "status": "true_blocker",
        "saved_path": None,
        "provider_backup_id": None,
        "reason": reason,
    }
    if local_state is not None:
        out["local_state"] = local_state
    return out


def before_state_refusal_verification_plan() -> dict[str, Any]:
    return {
        "status": "true_blocker",
        "steps": [
            "Confirm this local helper did not write an env file, token cache, demo/job output, or success receipt.",
            "Confirm token-fetch did not call the OAuth token endpoint.",
            "Confirm catalog read-only apply flows remain separate from local write helpers.",
        ],
        "blocker": "This command has no implemented live local-write executor.",
    }


def recovery_contract() -> dict[str, Any]:
    return {
        "end_state": "irreversible_and_clearly_labeled",
        "automatic_rollback": False,
        "backups": [],
        "snapshots": [],
        "rollback_plan": None,
        "restore_note": (
            "No built-in rollback, backups, snapshots, or provider restore are available for these local write "
            "helpers in this runtime. Treat current local write helpers as irreversible_and_clearly_labeled "
            "and use the saved plan and refusal output for manual follow-up only."
        ),
    }


def blocked_before_state(
    *,
    action: str,
    local_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    state = local_state or {"kind": "local_write_helper", "action": str(action)}
    return before_state_contract(
        reason=(
            "This source tool can build and review Amazon Creators local write-helper plans, "
            "but this command has no implemented live local-write executor."
        ),
        local_state=state,
    )


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def build_local_write_plan(
    *,
    ctx: dict[str, Any],
    command_id: str,
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    risk_reasons: list[str],
    local_state: dict[str, Any],
) -> dict[str, Any]:
    cfg = ctx.get("cfg")
    env_fingerprint = getattr(cfg, "base_url", None) if cfg is not None else None
    return {
        "tool": ctx.get("tool") or "amazon-creators-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": utc_now(),
        "env_fingerprint": env_fingerprint,
        "command_id": command_id,
        "command": str(ctx.get("command_str") or command_id),
        "selector": selector,
        "risk_level": "high",
        "risk_reasons": list(risk_reasons),
        "preconditions": ["local helper apply is not implemented in this command"],
        "baseline": {"env_fingerprint": env_fingerprint},
        "proposed_changes": proposed_changes,
        "before_state": blocked_before_state(action=command_id, local_state=local_state),
        "verification_plan": before_state_refusal_verification_plan(),
        "recovery": recovery_contract(),
        "dry_run": True,
    }


def ensure_blocked_apply_contract(
    plan: dict[str, Any],
    *,
    action: str,
    local_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out = dict(plan)
    if not isinstance(out.get("before_state"), dict):
        out["before_state"] = blocked_before_state(action=action, local_state=local_state)
    if (
        not isinstance(out.get("verification_plan"), dict)
        or str(out.get("verification_plan", {}).get("status") or "") != "true_blocker"
    ):
        out["verification_plan"] = before_state_refusal_verification_plan()
    recovery = out.get("recovery")
    if not isinstance(recovery, dict):
        out["recovery"] = recovery_contract()
    elif "automatic_rollback" not in recovery:
        updated = dict(recovery)
        updated["automatic_rollback"] = False
        out["recovery"] = updated
    return out


def refusal_output(
    *,
    plan: dict[str, Any],
    reason: str = BEFORE_STATE_REFUSAL_REASON,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "ok": True,
        "dry_run": False,
        "refused": True,
        "reasons": [reason],
        "refusal_type": "SafetyError",
        "plan": plan,
        "verification_plan": before_state_refusal_verification_plan(),
    }
    if isinstance(plan.get("recovery"), dict):
        out["recovery"] = plan["recovery"]
    return out
