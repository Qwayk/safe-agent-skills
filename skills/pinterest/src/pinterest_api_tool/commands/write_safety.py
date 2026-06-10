from __future__ import annotations

from typing import Any


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
            "Record the Pinterest provider response or job receipt.",
            "Record any local token, report, or download output written by the flow.",
            "Record explicit no-snapshot approval for write operations.",
        ],
        "approval_required": "--ack-no-snapshot",
    }


def rollback_contract(*, acks_required: list[str] | None = None) -> dict[str, Any]:
    return {
        "supported": False,
        "mode": "irreversible_and_clearly_labeled",
        "automatic_rollback": False,
        "acks_required": sorted(set(acks_required or [])),
        "notes": (
            "No built-in rollback, backups, snapshots, or provider restore are available in this runtime. "
            "Treat current Pinterest write families as irreversible_and_clearly_labeled and use the saved plan "
            "and receipt output for manual follow-up only."
        ),
    }


def blocked_plan(
    *,
    action: str,
    operations: list[dict[str, Any]] | None = None,
    acks_required: list[str] | None = None,
    request: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
    local_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ops = list(operations or [])
    plan: dict[str, Any] = {
        "ok": True,
        "dry_run": True,
        "action": str(action),
        "apply_requires": ["--apply", "--yes"],
        "acks_required": sorted(set(acks_required or [])),
        "request": dict(request or {}),
        "operations": ops,
        "warnings": list(warnings or []),
        "before_state": before_state_contract(
            reason=(
                "This source tool can build and review Pinterest write plans, but no reliable "
                "operation-specific before-state snapshot is available for this write."
            ),
            provider_write={"service": "Pinterest API", "action": str(action), "operations": ops} if ops else None,
            local_state=local_state,
        ),
        "verification_plan": before_state_refusal_verification_plan(),
        "rollback": rollback_contract(acks_required=acks_required),
    }
    return plan
