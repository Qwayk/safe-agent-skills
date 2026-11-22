from __future__ import annotations

import hashlib
import json
from typing import Any

from .authz import ResolvedAuth

from .errors import SafetyError


def reviewed_plan_apply_requested(
    ctx: dict[str, Any],
    *,
    requires_ack: bool = False,
    command_label: str | None = None,
) -> bool:
    if not bool(ctx.get("apply")):
        return False
    if not bool(ctx.get("yes")):
        return False
    if requires_ack and not bool(ctx.get("ack_irreversible")):
        return False
    if not bool(ctx.get("enforce_reviewed_plan")):
        return True
    if not ctx.get("plan_in"):
        label = command_label or "this command"
        ack_suffix = " --ack-irreversible" if requires_ack else ""
        raise SafetyError(
            f"Refused: {label} live apply requires a reviewed saved plan. "
            f"First run with --plan-out, review the plan, then rerun with --plan-in --apply --yes{ack_suffix}."
        )
    return True

def review_connection(cfg: Any, auth: ResolvedAuth) -> dict[str, str]:
    connection = {"mode": auth.mode}
    if auth.from_app_credentials:
        connection.update(app_id=str(cfg.app_id), instance_id=str(cfg.instance_id))
        credential = str(cfg.app_secret)
    else:
        credential = auth.headers["Authorization"]
        if account_id := auth.headers.get("wix-account-id"):
            connection["account_id"] = account_id
    encoded = json.dumps([connection, credential], sort_keys=True).encode()
    connection["credential_sha256"] = hashlib.sha256(encoded).hexdigest()
    return connection


def check_reviewed_change(plan: dict[str, Any], request: dict[str, Any], connection: dict[str, str]) -> None:
    if plan.get("connection") != connection:
        raise SafetyError("The Wix connection changed or was not saved. Make and review a new plan.")
    if plan.get("request") != request:
        raise SafetyError("The Wix request changed. Make and review a new plan.")
