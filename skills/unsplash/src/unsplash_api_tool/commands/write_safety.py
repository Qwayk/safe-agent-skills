from __future__ import annotations

from typing import Any


BEFORE_STATE_REFUSAL_REASON = (
    "Refused: this Unsplash write has no reliable before-state snapshot. "
    "Review the dry-run plan, then rerun with --ack-no-snapshot if you approve applying without a snapshot."
)


def no_inverse_recovery_contract(*, restore_note: str) -> dict[str, Any]:
    return {
        "end_state": "irreversible_and_clearly_labeled",
        "strategy": "no_inverse",
        "rollback_ready": False,
        "automatic_rollback": False,
        "backups": [],
        "snapshots": [],
        "rollback_plan": None,
        "restore_note": restore_note,
    }


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
            "Record the Unsplash provider response in the receipt.",
            "Record any local destination file written by the flow.",
            "Record explicit no-snapshot approval for write operations.",
        ],
        "approval_required": "--ack-no-snapshot",
    }


def before_state_refusal_output(plan: dict[str, Any], *, reason: str = BEFORE_STATE_REFUSAL_REASON) -> dict[str, Any]:
    out = {
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
