from __future__ import annotations

from typing import Any


BEFORE_STATE_REFUSAL_REASON = (
    "Refused: this X write has no reliable before-state snapshot. "
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
            "Record the X provider or token response in the receipt.",
            "Record any local token, PKCE, demo/job receipt, or write output created by the flow.",
            "Record explicit no-snapshot approval for write operations.",
        ],
        "approval_required": "--ack-no-snapshot",
    }


def rollback_contract(*, requires_ack_irreversible: bool = False) -> dict[str, Any]:
    return {
        "supported": False,
        "mode": "irreversible_and_clearly_labeled",
        "requires_ack_irreversible": bool(requires_ack_irreversible),
        "automatic_rollback": False,
        "notes": (
            "No built-in rollback, backups, snapshots, or provider restore are available in this runtime. "
            "Treat current X write families as irreversible_and_clearly_labeled and use the saved plan "
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
        changes = list(proposed_changes or [])
        provider = {"service": "X API", "action": str(action)}
        if changes:
            provider["proposed_changes"] = changes
    return before_state_contract(
        reason=(
            "This source tool can build and review X write plans, but no reliable "
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
    requires_ack_irreversible: bool = False,
) -> dict[str, Any]:
    out = dict(plan)
    if not isinstance(out.get("before_state"), dict):
        out["before_state"] = blocked_before_state(
            action=action,
            proposed_changes=proposed_changes,
            provider_write=provider_write,
            local_state=local_state,
        )
    if not isinstance(out.get("verification_plan"), dict):
        out["verification_plan"] = before_state_refusal_verification_plan()
    rollback = out.get("rollback")
    if not isinstance(rollback, dict):
        out["rollback"] = rollback_contract(requires_ack_irreversible=requires_ack_irreversible)
    elif "automatic_rollback" not in rollback:
        updated = dict(rollback)
        updated["automatic_rollback"] = False
        out["rollback"] = updated
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
    if isinstance(plan.get("rollback"), dict):
        out["rollback"] = plan["rollback"]
    return out
