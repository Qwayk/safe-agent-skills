from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskRequirements:
    apply: bool = False
    yes: bool = False
    plan_in: bool = False
    ack_irreversible: bool = False


@dataclass(frozen=True)
class RiskClassification:
    level: str
    reasons: tuple[str, ...]
    requirements: RiskRequirements


_READ_METHODS = {"get", "head", "options"}


def classify_operation(*, operation_id: str, method: str, path_template: str) -> RiskClassification:
    m = method.lower().strip()
    if m in _READ_METHODS:
        return RiskClassification(
            level="low",
            reasons=(f"read-like HTTP method: {m.upper()}",),
            requirements=RiskRequirements(),
        )
    if m == "delete":
        return RiskClassification(
            level="irreversible",
            reasons=(
                "HTTP DELETE can permanently remove data",
                f"operation: {operation_id}",
                f"path: {path_template}",
            ),
            requirements=RiskRequirements(apply=True, yes=True, plan_in=True, ack_irreversible=True),
        )
    # Safe default: treat any non-read as high-risk and require plan-in + explicit confirmation.
    return RiskClassification(
        level="high",
        reasons=(
            f"write-like HTTP method: {m.upper()}",
            f"operation: {operation_id}",
            f"path: {path_template}",
        ),
        requirements=RiskRequirements(apply=True, yes=True, plan_in=True),
    )

