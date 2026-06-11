from __future__ import annotations

import time
from typing import Any

from .errors import SafetyError, ValidationError
from .json_files import read_json_file, write_json_file
from .operations import Operation


_NO_RECOVERY_NOTE = (
    "No automated rollback is available for this operation; "
    "it is treated as irreversible and needs manual cleanup if removal is required."
)

BEFORE_STATE_REFUSAL_REASON = (
    "Refused: this ElevenLabs write has no saved before-state snapshot. "
    "Review the plan, confirm the recovery limit, then re-run with --ack-no-snapshot."
)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def build_no_recovery_contract(*, notes: str | None = None) -> dict[str, Any]:
    return {
        "automatic_rollback": False,
        "end_state": "irreversible_and_clearly_labeled",
        "strategy": "no_inverse",
        "rollback_ready": False,
        "backups": [],
        "snapshots": [],
        "rollback_plan": None,
        "restore_note": notes or _NO_RECOVERY_NOTE,
    }


def build_before_state_contract(*, op: Operation, selector: dict[str, Any]) -> dict[str, Any]:
    return {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "approval_required": "--ack-no-snapshot",
        "operation": op.name,
        "target": {
            "selector": selector,
            "endpoint": f"{op.method.upper()} {op.path}",
        },
        "saved_path": None,
        "provider_backup_id": None,
        "reason": (
            "No useful before-state snapshot or provider recovery point is captured for this ElevenLabs write. "
            "The write may still run after the reviewed plan and explicit no-snapshot approval."
        ),
    }


def build_before_state_refusal_verification_plan() -> dict[str, Any]:
    return {
        "type": "best_effort_after_apply",
        "status": "requires-no-snapshot-approval",
        "requires_no_snapshot_approval": True,
        "notes": (
            "Apply can run after explicit no-snapshot approval, then records provider response "
            "and the operation verification plan."
        ),
    }


def ensure_write_safety_contract(*, plan: dict[str, Any], op: Operation) -> dict[str, Any]:
    if "write" not in op.safety:
        return plan
    selector = plan.get("selector") if isinstance(plan.get("selector"), dict) else {}
    previous_verification = plan.get("verification_plan")
    plan["before_state"] = build_before_state_contract(op=op, selector=selector)
    plan["verification_plan"] = build_before_state_refusal_verification_plan()
    plan["post_apply_verification_plan"] = previous_verification or default_verification(op=op)
    plan["recovery"] = plan.get("recovery") or default_recovery(op=op)
    return plan


def build_plan(
    *,
    ctx: dict[str, Any],
    op: Operation,
    selector: dict[str, Any],
    request: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    verification_plan: dict[str, Any],
    recovery: dict[str, Any],
) -> dict[str, Any]:
    cfg = ctx["cfg"]
    risk_reasons = list(op.safety)
    risk_level = "high" if "write" in op.safety else "low"
    baseline = {
        "env_fingerprint": cfg.base_url,
        "operation": op.name,
        "selector": selector,
    }
    plan = {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "generated_at_utc": _utc_now(),
        "env_fingerprint": cfg.base_url,
        "command": ctx.get("command_str"),
        "operation": op.name,
        "section": op.section,
        "endpoint": f"{op.method.upper()} {op.path}",
        "doc_url": op.doc_url,
        "selector": selector,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "preconditions": [
            "API key configured via ELEVENLABS_API_KEY",
            "Base URL matches the intended environment",
        ],
        "baseline": baseline,
        "request": request,
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "recovery": recovery,
    }
    return ensure_write_safety_contract(plan=plan, op=op)


def validate_plan_for_apply(*, plan: dict[str, Any], op: Operation, ctx: dict[str, Any]) -> None:
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must contain an object")
    if plan.get("operation") != op.name:
        raise SafetyError("Refused: plan operation does not match the current command")
    endpoint = plan.get("endpoint")
    expected = f"{op.method.upper()} {op.path}"
    if endpoint != expected:
        raise SafetyError("Refused: plan endpoint does not match the current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan baseline missing or invalid")
    env_fp = baseline.get("env_fingerprint")
    if str(env_fp or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan environment fingerprint does not match current base URL")


def load_plan_from_file(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    raw = read_json_file(path)
    if not isinstance(raw, dict):
        raise ValidationError("Plan file must contain an object")
    return raw


def write_plan_to_file(*, plan: dict[str, Any], path: str | None) -> str | None:
    if not path:
        return None
    return write_json_file(path, plan)


def write_receipt_to_file(*, receipt: dict[str, Any], path: str | None) -> str | None:
    if not path:
        return None
    return write_json_file(path, receipt)


def build_receipt(
    *,
    ctx: dict[str, Any],
    op: Operation,
    plan: dict[str, Any],
    result: dict[str, Any],
    verification: dict[str, Any],
    outputs: dict[str, Any],
    changed: bool,
    recovery: dict[str, Any] | None = None,
) -> dict[str, Any]:
    cfg = ctx["cfg"]
    recovery_contract = recovery or default_recovery(op=op)
    receipt = {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "applied_at_utc": _utc_now(),
        "env_fingerprint": cfg.base_url,
        "command": ctx.get("command_str"),
        "operation": op.name,
        "selector": plan.get("selector"),
        "changed": changed,
        "result": result,
        "outputs": outputs,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes", []),
        **(
            {
                "before_state": plan.get("before_state"),
                "no_snapshot_approval": {"approved": True, "flag": "--ack-no-snapshot"},
            }
            if changed and isinstance(plan.get("before_state"), dict)
            else {}
        ),
        "recovery": recovery_contract,
    }
    return receipt


def summarize_request(
    *,
    op: Operation,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
    files: dict[str, Any] | None = None,
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "method": op.method.upper(),
        "path": op.path,
    }
    if params:
        summary["params"] = {k: v for k, v in params.items() if v is not None}
    if body:
        if set(body.keys()) == {"__body_file"}:
            summary["body_file"] = body["__body_file"]
        else:
            summary["json"] = {k: v for k, v in body.items() if v is not None}
    if files:
        summary["files"] = {k: str(v) for k, v in files.items()}
    return summary


def default_proposed_changes(*, op: Operation, selector: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "description": f"{op.description}",
            "selector": selector,
        }
    ]


def default_verification(*, op: Operation) -> dict[str, Any]:
    if "write" in op.safety:
        return {"type": "write", "notes": "Verify the output file or service state after apply."}
    return {"type": "read", "notes": "Inspect the response to confirm the expected data."}


def default_recovery(*, op: Operation) -> dict[str, Any]:
    return build_no_recovery_contract(
        notes=(
            f"{op.name}: no automated rollback is available for this command; "
            "it is treated as irreversible and needs manual cleanup if removal is required."
        )
    )
