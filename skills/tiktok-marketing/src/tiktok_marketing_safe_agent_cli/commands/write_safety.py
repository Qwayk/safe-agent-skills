from __future__ import annotations

from typing import Any


BEFORE_STATE_REFUSAL_REASON = (
    "Refused: this TikTok Marketing write has no reliable before-state snapshot. "
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
            "Record the TikTok Marketing provider response in the receipt.",
            "Record explicit no-snapshot approval for write operations.",
            "Run a follow-up read when the operation has a clear read-back endpoint.",
        ],
        "approval_required": "--ack-no-snapshot",
    }


def before_state_refusal_output(plan: dict[str, Any], *, reason: str = BEFORE_STATE_REFUSAL_REASON) -> dict[str, Any]:
    out: dict[str, Any] = {
        "ok": True,
        "dry_run": False,
        "refused": True,
        "reasons": [reason],
        "refusal_type": "SafetyError",
        "plan": plan,
        "verification_plan": before_state_refusal_verification_plan(),
    }
    if isinstance(plan.get("rollback"), dict):
        out["rollback"] = plan["rollback"]
    return out
