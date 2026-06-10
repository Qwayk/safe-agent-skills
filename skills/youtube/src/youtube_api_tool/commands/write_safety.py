from __future__ import annotations

from typing import Any


BEFORE_STATE_REFUSAL_REASON = (
    "Refused: this YouTube write has no reliable before-state snapshot. "
    "Review the dry-run plan, then rerun with --ack-no-snapshot if you approve applying without a snapshot."
)


def before_state_contract(
    *,
    reason: str,
    provider_write: dict[str, Any] | None = None,
    local_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "approval_required": "--ack-no-snapshot",
        "saved_path": None,
        "provider_backup_id": None,
        "reason": reason,
    }
    if provider_write is not None:
        out["provider_write"] = provider_write
    if local_state is not None:
        out["local_state"] = local_state
    return out


def before_state_refusal_verification_plan() -> dict[str, Any]:
    return {
        "status": "best_effort_after_apply",
        "steps": [
            "Record the YouTube provider or upload response in the receipt.",
            "Record any OAuth/token/demo/job output created by the flow.",
            "Record explicit no-snapshot approval for write operations.",
        ],
        "approval_required": "--ack-no-snapshot",
    }


def recovery_contract() -> dict[str, Any]:
    return {
        "end_state": "irreversible_and_clearly_labeled",
        "automatic_rollback": False,
        "backups": [],
        "snapshots": [],
        "rollback_plan": None,
        "restore_note": (
            "No built-in rollback, backups, snapshots, or provider restore are available in this runtime. "
            "Treat current YouTube write families as irreversible_and_clearly_labeled and use the saved plan "
            "and refusal output for manual follow-up only."
        ),
    }


def blocked_before_state(
    *,
    action: str,
    proposed_changes: list[dict[str, Any]] | None = None,
    provider_write: dict[str, Any] | None = None,
    local_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    provider = provider_write
    if provider is None:
        provider = {"service": "YouTube Data API v3", "action": str(action)}
        changes = list(proposed_changes or [])
        if changes:
            provider["proposed_changes"] = changes
    return before_state_contract(
        reason=(
            "This source tool can build and review YouTube write plans, but no reliable "
            "operation-specific before-state snapshot is available for this write."
        ),
        provider_write=provider,
        local_state=local_state,
    )


def ensure_blocked_apply_contract(
    plan: dict[str, Any],
    *,
    action: str,
    proposed_changes: list[dict[str, Any]] | None = None,
    provider_write: dict[str, Any] | None = None,
    local_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out = dict(plan)
    if not isinstance(out.get("before_state"), dict):
        out["before_state"] = blocked_before_state(
            action=action,
            proposed_changes=proposed_changes,
            provider_write=provider_write,
            local_state=local_state,
        )
    if not isinstance(out.get("verification_plan"), dict) or str(out.get("verification_plan", {}).get("status") or "") != "blocked_before_apply":
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
