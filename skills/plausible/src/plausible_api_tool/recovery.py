from __future__ import annotations

from typing import Any


def build_recovery_contract(
    *,
    end_state: str,
    strategy: str,
    rollback_ready: bool,
    rollback_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "end_state": end_state,
        "strategy": strategy,
        "rollback_ready": rollback_ready,
        "rollback_plan": rollback_plan,
    }


def build_irreversible_recovery(*, strategy: str = "no_inverse") -> dict[str, Any]:
    return build_recovery_contract(
        end_state="irreversible_and_clearly_labeled",
        strategy=strategy,
        rollback_ready=False,
        rollback_plan=None,
    )


def build_inverse_recovery(
    *,
    strategy: str,
    rollback_plan: dict[str, Any] | None,
    rollback_ready: bool,
) -> dict[str, Any]:
    return build_recovery_contract(
        end_state="rollback_by_inverse_action",
        strategy=strategy,
        rollback_ready=rollback_ready,
        rollback_plan=rollback_plan,
    )
