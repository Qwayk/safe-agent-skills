from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import SafetyError, ValidationError


_MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
_HIGH_RISK_MARKERS = (
    " delete ",
    " remove ",
    " cancel ",
    " credit ",
    " bookkeep ",
    " externalprint ",
    " approvalpayment ",
    " send-given-",
    " send-as-email ",
    " jobs run ",
)
_IRREVERSIBLE_MARKERS = (
    " delete ",
    " remove ",
)


def _as_dict(obj: Any) -> dict[str, Any] | None:
    return obj if isinstance(obj, dict) else None


def is_plan_object(obj: Any) -> bool:
    data = _as_dict(obj)
    if data is None:
        return False
    return "risk_level" in data and "selector" in data and (
        "proposed_changes" in data or "verification_plan" in data or "baseline" in data
    )


def is_receipt_object(obj: Any) -> bool:
    data = _as_dict(obj)
    if data is None:
        return False
    return "changed" in data and ("verification" in data or "diff_applied" in data or "selector" in data)


def _detect_snapshot_status(plan_or_receipt: dict[str, Any]) -> str:
    status = str(plan_or_receipt.get("snapshot_status") or "").strip()
    if status:
        return status

    before_state = _as_dict(plan_or_receipt.get("before_state")) or {}
    if before_state.get("saved_path"):
        return "snapshot_saved"
    if before_state.get("provider_backup_id"):
        return "provider_backup_recorded"
    return "no_snapshot_available"


def _default_before_state(plan_or_receipt: dict[str, Any], *, snapshot_status: str) -> dict[str, Any]:
    before_state = _as_dict(plan_or_receipt.get("before_state"))
    if before_state is not None:
        out = dict(before_state)
    else:
        out = {}
    out.setdefault("required", str(plan_or_receipt.get("risk_level") or "") in {"high", "irreversible"})
    out.setdefault("supported", snapshot_status != "no_snapshot_available")
    out.setdefault("status", snapshot_status)
    out.setdefault("saved_path", None)
    out.setdefault("provider_backup_id", None)
    out.setdefault(
        "reason",
        "This Fortnox runtime does not record a useful before-state snapshot for this change family yet.",
    )
    return out


def _default_recovery_notes(plan_or_receipt: dict[str, Any], *, snapshot_status: str) -> str:
    recovery = _as_dict(plan_or_receipt.get("recovery")) or {}
    if recovery.get("restore_note"):
        return str(recovery["restore_note"])
    rollback = _as_dict(plan_or_receipt.get("rollback")) or {}
    if rollback.get("notes"):
        return str(rollback["notes"])
    rollback_plan = plan_or_receipt.get("rollback_plan")
    if rollback_plan:
        return "Rollback details are recorded in rollback_plan. Review provider limits before manual recovery."
    if snapshot_status == "snapshot_saved":
        return "A saved before-state snapshot is recorded for manual recovery."
    if snapshot_status == "provider_backup_recorded":
        return "A provider backup or restore handle is recorded for manual recovery."
    return "No useful before-state snapshot is recorded. Recovery is manual or may be unavailable for this change."


def _default_recovery(
    plan_or_receipt: dict[str, Any],
    *,
    snapshot_status: str,
    before_state: dict[str, Any],
    recovery_notes: str,
) -> dict[str, Any]:
    recovery = _as_dict(plan_or_receipt.get("recovery"))
    if recovery is not None:
        out = dict(recovery)
    else:
        rollback = _as_dict(plan_or_receipt.get("rollback")) or {}
        out = {
            "automatic_rollback": False,
            "backups": [],
            "snapshots": [],
            "rollback_plan": plan_or_receipt.get("rollback_plan"),
            "restore_note": rollback.get("notes"),
        }
    out.setdefault("automatic_rollback", False)
    out.setdefault("backups", [])
    out.setdefault("snapshots", [])
    out.setdefault("rollback_plan", plan_or_receipt.get("rollback_plan"))
    if before_state.get("saved_path") and before_state["saved_path"] not in out["snapshots"]:
        out["snapshots"] = [*list(out["snapshots"]), before_state["saved_path"]]
    if before_state.get("provider_backup_id") and before_state["provider_backup_id"] not in out["backups"]:
        out["backups"] = [*list(out["backups"]), before_state["provider_backup_id"]]
    out.setdefault("end_state", "manual_recovery_only" if snapshot_status == "no_snapshot_available" else "review_saved_state")
    out["restore_note"] = str(out.get("restore_note") or recovery_notes)
    return out


def normalize_plan(plan: dict[str, Any]) -> dict[str, Any]:
    out = dict(plan)
    snapshot_status = _detect_snapshot_status(out)
    before_state = _default_before_state(out, snapshot_status=snapshot_status)
    recovery_notes = _default_recovery_notes(out, snapshot_status=snapshot_status)
    out["snapshot_status"] = snapshot_status
    out["before_state"] = before_state
    out["recovery_notes"] = recovery_notes
    out["recovery"] = _default_recovery(
        out,
        snapshot_status=snapshot_status,
        before_state=before_state,
        recovery_notes=recovery_notes,
    )
    return out


def normalize_receipt(receipt: dict[str, Any], *, plan: dict[str, Any] | None = None) -> dict[str, Any]:
    out = dict(receipt)
    normalized_plan = normalize_plan(plan) if isinstance(plan, dict) else None
    if normalized_plan is not None:
        out.setdefault("selector", normalized_plan.get("selector"))
    snapshot_status = str(out.get("snapshot_status") or "") or (
        str(normalized_plan.get("snapshot_status")) if normalized_plan else ""
    )
    if not snapshot_status:
        snapshot_status = _detect_snapshot_status(out)
    before_state = _default_before_state(normalized_plan or out, snapshot_status=snapshot_status)
    recovery_notes = str(out.get("recovery_notes") or "") or (
        str(normalized_plan.get("recovery_notes")) if normalized_plan else ""
    )
    if not recovery_notes:
        recovery_notes = _default_recovery_notes(normalized_plan or out, snapshot_status=snapshot_status)
    out["snapshot_status"] = snapshot_status
    out["before_state"] = before_state
    out["recovery_notes"] = recovery_notes
    out["recovery"] = _default_recovery(
        out if isinstance(out.get("recovery"), dict) else (normalized_plan or out),
        snapshot_status=snapshot_status,
        before_state=before_state,
        recovery_notes=recovery_notes,
    )
    return out


def normalize_output_contract(obj: Any) -> Any:
    if not isinstance(obj, dict):
        return obj

    out = dict(obj)
    if is_plan_object(out):
        out = normalize_plan(out)
    if isinstance(out.get("plan"), dict):
        out["plan"] = normalize_plan(out["plan"])
    if is_receipt_object(out):
        out = normalize_receipt(out, plan=_as_dict(out.get("plan")))
    if isinstance(out.get("receipt"), dict):
        out["receipt"] = normalize_receipt(out["receipt"], plan=_as_dict(out.get("plan")))
    return out


def load_apply_plan(ctx: dict[str, Any]) -> dict[str, Any] | None:
    cached = ctx.get("_normalized_plan")
    if isinstance(cached, dict):
        return cached
    plan = ctx.get("plan_obj")
    if isinstance(plan, dict):
        normalized = normalize_plan(plan)
        ctx["_normalized_plan"] = normalized
        return normalized
    plan_in = str(ctx.get("plan_in") or "").strip()
    if not plan_in:
        return None
    plan_path = Path(plan_in)
    if not plan_path.exists():
        raise ValidationError(f"JSON file not found: {plan_path}")
    try:
        plan_obj = json.loads(plan_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise ValidationError(f"Invalid JSON file: {plan_path}: {type(exc).__name__}: {exc}") from None
    if not isinstance(plan_obj, dict):
        raise ValidationError(f"Plan file must be a JSON object: {plan_path}")
    normalized = normalize_plan(plan_obj)
    ctx["_normalized_plan"] = normalized
    return normalized


def command_requires_saved_plan(*, command_str: str, method: str) -> bool:
    if method.upper() not in _MUTATING_METHODS:
        return False
    lowered = f" {str(command_str or '').lower()} "
    return any(marker in lowered for marker in _HIGH_RISK_MARKERS)


def command_requires_ack_irreversible(*, command_str: str, plan: dict[str, Any] | None) -> bool:
    if isinstance(plan, dict) and str(plan.get("risk_level") or "") == "irreversible":
        return True
    lowered = f" {str(command_str or '').lower()} "
    return any(marker in lowered for marker in _IRREVERSIBLE_MARKERS)


def plan_requires_no_snapshot_ack(plan: dict[str, Any] | None) -> bool:
    if not isinstance(plan, dict):
        return False
    risk_level = str(plan.get("risk_level") or "")
    snapshot_status = str(plan.get("snapshot_status") or "")
    return risk_level in {"high", "irreversible"} and snapshot_status == "no_snapshot_available"


def enforce_write_apply_contract(*, ctx: dict[str, Any], method: str, path: str) -> None:
    del path
    if not bool(ctx.get("apply")):
        return
    if method.upper() not in _MUTATING_METHODS:
        return

    command_str = str(ctx.get("command_str") or "")
    plan = load_apply_plan(ctx)

    if plan is None and command_requires_saved_plan(command_str=command_str, method=method):
        raise SafetyError(
            "Refused before HTTP: this high-risk Fortnox apply requires --apply --yes --plan-in <reviewed-plan.json>."
        )

    if isinstance(plan, dict) and str(plan.get("risk_level") or "") in {"high", "irreversible"} and not bool(ctx.get("yes")):
        raise SafetyError("Refused before HTTP: applying a high-risk Fortnox plan requires --apply --yes --plan-in.")

    if plan_requires_no_snapshot_ack(plan) and not bool(ctx.get("ack_no_snapshot")):
        raise SafetyError(
            "Refused before HTTP: this high-risk Fortnox apply has no before-state snapshot. Review the plan and add "
            "--ack-no-snapshot to continue."
        )

    if command_requires_ack_irreversible(command_str=command_str, plan=plan) and not bool(ctx.get("ack_irreversible")):
        raise SafetyError(
            "Refused before HTTP: this Fortnox apply is clearly irreversible. Add --ack-irreversible after review."
        )
