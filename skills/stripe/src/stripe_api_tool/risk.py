from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class RiskRequirements:
    apply: bool
    yes: bool
    plan_in: bool
    ack_spend_money: bool
    ack_irreversible: bool


@dataclasses.dataclass(frozen=True)
class RiskClassification:
    level: str  # low|medium|high|irreversible
    reasons: tuple[str, ...]
    requirements: RiskRequirements


_READ_METHODS = {"get", "head", "options"}


def _is_money_moving(*, operation_id: str, path_template: str) -> bool:
    op = operation_id.lower()
    path = path_template.lower()
    # Safe default: over-gate anything plausibly money-moving.
    tokens = (
        "/v1/charges",
        "/v1/payment_intents",
        "/v1/refunds",
        "/v1/payouts",
        "/v1/transfers",
        "/v1/topups",
        "/v1/treasury/",
        "/v1/balance_transactions",
    )
    if any(t in path for t in tokens):
        return True
    # Invoice payment is money-moving.
    if "/v1/invoices" in path and "/pay" in path:
        return True
    if any(t in op for t in ("charge", "paymentintent", "refund", "payout", "transfer", "topup", "treasury")):
        return True
    if "invoice" in op and "pay" in op:
        return True
    return False


def classify_operation(*, operation_id: str, method: str, path_template: str) -> RiskClassification:
    m = (method or "").lower().strip()
    if m in _READ_METHODS:
        return RiskClassification(
            level="low",
            reasons=("read-only method",),
            requirements=RiskRequirements(
                apply=False,
                yes=False,
                plan_in=False,
                ack_spend_money=False,
                ack_irreversible=False,
            ),
        )

    money_moving = _is_money_moving(operation_id=operation_id, path_template=path_template)
    is_delete = m == "delete"

    if is_delete:
        level = "irreversible"
        reasons = ("http.delete",)
    elif money_moving:
        level = "high"
        reasons = ("money-moving",)
    else:
        level = "medium"
        reasons = ("write-like method",)

    return RiskClassification(
        level=level,
        reasons=tuple(reasons),
        requirements=RiskRequirements(
            apply=True,
            yes=level in {"high", "irreversible"},
            plan_in=level in {"high", "irreversible"},
            ack_spend_money=bool(money_moving),
            ack_irreversible=level == "irreversible",
        ),
    )
