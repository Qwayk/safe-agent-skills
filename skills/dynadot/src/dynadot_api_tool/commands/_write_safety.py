from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file

BEFORE_STATE_REFUSAL_REASON = (
    "Refused: missing explicit no-snapshot approval for a Dynadot write with no reliable before-state snapshot. "
    "Review the dry-run plan, then rerun with --ack-no-snapshot if you approve applying without a snapshot."
)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def build_no_recovery_contract(*, notes: str) -> dict[str, Any]:
    return {
        "end_state": "irreversible_and_clearly_labeled",
        "strategy": "no_inverse",
        "rollback_ready": False,
        "backups": [],
        "snapshots": [],
        "rollback_plan": None,
        "restore_note": notes,
    }


def build_before_state_contract(
    *,
    selector_kind: str,
    selector_value: str | None,
    notes: str | None = None,
) -> dict[str, Any]:
    return {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "approval_required": "--ack-no-snapshot",
        "selector": {"kind": selector_kind, "value": selector_value},
        "storage": None,
        "saved_at_utc": None,
        "reason": BEFORE_STATE_REFUSAL_REASON,
        "notes": notes
        or "No reliable before-state snapshot is available. Apply requires explicit no-snapshot approval.",
    }


def build_before_state_refusal_verification_plan(*, notes: str | None = None) -> dict[str, Any]:
    return {
        "type": "best_effort_after_apply",
        "notes": notes or "Record the Dynadot response, any read-back verification, and explicit no-snapshot approval.",
    }


def ensure_before_state_refusal_plan(
    plan: dict[str, Any],
    *,
    selector_kind: str,
    selector_value: str | None,
    notes: str | None = None,
) -> dict[str, Any]:
    plan["before_state"] = build_before_state_contract(
        selector_kind=selector_kind,
        selector_value=selector_value,
        notes=notes,
    )
    plan["verification_plan"] = build_before_state_refusal_verification_plan()
    return plan


def emit_before_state_refusal(
    *,
    ctx: dict[str, Any],
    plan: dict[str, Any],
    audit_event: str,
    extra: dict[str, Any] | None = None,
) -> int:
    out = {
        "ok": True,
        "dry_run": False,
        "refused": True,
        "reasons": [BEFORE_STATE_REFUSAL_REASON],
        "refusal_type": "SafetyError",
        "before_state": plan.get("before_state"),
        "plan": plan,
    }
    if extra:
        out.update(extra)
    if "audit" in ctx:
        ctx["audit"].write(audit_event, {"reason": "missing-no-snapshot-approval"})
    ctx["out"].emit(out)
    return 0


def _validate_plan_for_apply(
    plan: dict[str, Any],
    *,
    baseline: dict[str, Any],
    env_fingerprint: str,
) -> None:
    if str(plan.get("env_fingerprint") or "") != str(env_fingerprint):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    b = plan.get("baseline")
    if not isinstance(b, dict):
        raise ValidationError("Plan missing baseline object")
    for k, v in baseline.items():
        if str(b.get(k) or "") != str(v or ""):
            raise SafetyError(f"Refused: plan baseline mismatch for {k}")


@dataclass(frozen=True)
class WriteSpec:
    api_command: str
    selector_kind: str
    selector_value: str | None
    risk_level: str
    risk_reasons: list[str]
    irreversible: bool
    baseline: dict[str, Any]
    preview: dict[str, Any] | None
    proposed_changes: list[dict[str, Any]] | None
    verification_plan: dict[str, Any]
    rollback: dict[str, Any]


ApplyCall = Callable[[], dict[str, Any]]
VerifyCall = Callable[[], dict[str, Any]]


def run_write_command(
    *,
    ctx: dict[str, Any],
    spec: WriteSpec,
    apply_call: ApplyCall,
    verify_call: VerifyCall | None = None,
) -> int:
    """
    Standard v2-style write contract, centralized:
    - dry-run emits a plan (and writes it via ctx["plan_out"] when configured)
    - apply requires --apply --yes AND reviewed --plan-in
    - irreversible actions require --ack-irreversible
    - receipts are always written via ctx["receipt_out"] when configured
    """
    plan_in = str(ctx.get("plan_in") or "").strip() or None
    env_fp = str(ctx["cfg"].base_url)

    if plan_in:
        plan_obj = read_json_file(plan_in)
        if not isinstance(plan_obj, dict):
            raise ValidationError("Plan file must be a JSON object")
        plan = dict(plan_obj)
        plan.setdefault("rollback", spec.rollback)
        plan.setdefault("recovery", build_no_recovery_contract(notes=str(spec.rollback.get("notes") or "")))
        ensure_before_state_refusal_plan(
            plan,
            selector_kind=spec.selector_kind,
            selector_value=spec.selector_value,
        )
    else:
        recovery = build_no_recovery_contract(notes=str(spec.rollback.get("notes") or ""))
        plan = {
            "tool": ctx.get("tool") or "dynadot-api-tool",
            "version": ctx.get("tool_version") or None,
            "generated_at_utc": _utc_now(),
            "env_fingerprint": env_fp,
            "command": ctx.get("command_str") or None,
            "api_command": spec.api_command,
            "selector": {"kind": spec.selector_kind, "value": spec.selector_value},
            "risk_level": spec.risk_level,
            "risk_reasons": list(spec.risk_reasons),
            "preconditions": ["env_fingerprint must match", "plan baseline must match current inputs"],
            "baseline": dict(spec.baseline),
            "preview": spec.preview,
            "proposed_changes": spec.proposed_changes,
            "post_apply_verification_plan": spec.verification_plan,
            "rollback": spec.rollback,
            "recovery": recovery,
        }
        ensure_before_state_refusal_plan(
            plan,
            selector_kind=spec.selector_kind,
            selector_value=spec.selector_value,
        )

    plan_out = str(ctx.get("plan_out") or "").strip() or None
    if plan_out and not bool(ctx.get("apply")):
        write_json_file(plan_out, plan)

    if not bool(ctx.get("apply")):
        out = {
            "ok": True,
            "dry_run": True,
            "api_command": spec.api_command,
            "plan": plan,
            "plan_out": plan_out,
        }
        ctx["audit"].write(f"{spec.selector_kind}.plan", {"api_command": spec.api_command, "plan_out": plan_out})
        ctx["out"].emit(out)
        return 0

    if not plan_in:
        auto_plan_path = None
        try:
            ad = ctx.get("artifacts_dir")
            if ad:
                auto_plan_path = write_json_file(str(ad / "plan.json"), plan)  # type: ignore[operator]
        except Exception:
            auto_plan_path = None
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": [
                "Refused: apply requires a reviewed plan file (--plan-in). Run the dry-run first, review the plan, then re-run with --apply --yes --plan-in."
            ],
            "refusal_type": "SafetyError",
            "api_command": spec.api_command,
            "plan": plan,
            "plan_out": auto_plan_path,
        }
        ctx["audit"].write(f"{spec.selector_kind}.refused", {"api_command": spec.api_command, "plan_out": auto_plan_path})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: applying this command requires --apply --yes")

    if spec.irreversible and not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refused: irreversible/monetary actions require --ack-irreversible")

    _validate_plan_for_apply(plan, baseline=spec.baseline, env_fingerprint=env_fp)
    if not bool(ctx.get("ack_no_snapshot")):
        return emit_before_state_refusal(
            ctx=ctx,
            plan=plan,
            audit_event=f"{spec.selector_kind}.refused",
            extra={"api_command": spec.api_command},
        )

    apply_result = apply_call()
    verification = verify_call() if verify_call else {"ok": True, "details": {"type": "provider-response-only"}}
    receipt = {
        "tool": ctx.get("tool") or "dynadot-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": env_fp,
        "command": ctx.get("command_str") or None,
        "api_command": spec.api_command,
        "selector": {"kind": spec.selector_kind, "value": spec.selector_value},
        "risk_level": spec.risk_level,
        "risk_reasons": list(spec.risk_reasons),
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": "No reliable before-state snapshot is available for this Dynadot write.",
        },
        "changed": bool(apply_result.get("ok", True)) if isinstance(apply_result, dict) else True,
        "provider_response": apply_result,
        "verification": verification,
        "diff_applied": spec.proposed_changes or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": plan.get("recovery"),
    }
    receipt_out = str(ctx.get("receipt_out") or "").strip() or None
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {
        "ok": bool(verification.get("ok", True)) if isinstance(verification, dict) else True,
        "dry_run": False,
        "api_command": spec.api_command,
        "receipt": receipt,
        "receipt_out": receipt_path,
    }
    ctx["audit"].write(f"{spec.selector_kind}.apply", {"api_command": spec.api_command, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0
