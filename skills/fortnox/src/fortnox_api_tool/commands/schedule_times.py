from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

from .. import api_runtime
from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file

request_json = api_runtime.request_json


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_payload_file(path_str: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    path = Path(path_str)
    if not path.exists():
        raise ValidationError(f"JSON file not found: {path}")
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError("JSON file must contain a top-level object")
    schedule_time = obj.get("ScheduleTime")
    if not isinstance(schedule_time, dict):
        raise ValidationError("JSON file must contain a top-level ScheduleTime object")
    return path, obj, schedule_time


def _extract_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _build_plan(
    *,
    action: str,
    selector: dict[str, Any],
    payload_file: Path | None,
    payload_obj: dict[str, Any] | None,
    risk_level: str,
    risk_reasons: list[str],
    verification_plan: dict[str, Any],
    rollback_notes: str,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    baseline: dict[str, Any] = {
        "env_fingerprint": ctx["cfg"].base_url,
        "action": action,
        "selector": selector,
    }
    if payload_file is not None:
        payload_sha256 = _sha256_file(payload_file)
        baseline["payload_sha256"] = payload_sha256
        baseline["json_file_sha256"] = payload_sha256
        baseline["payload_file"] = str(payload_file)
    return {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
        ] + (["payload_sha256 must match"] if payload_file is not None else []),
        "baseline": baseline,
        "proposed_changes": [
            {
                "action": action,
                "selector": selector,
                "payload": payload_obj,
            }
        ],
        "verification_plan": verification_plan,
        "rollback": {"supported": False, "notes": rollback_notes},
    }


def _validate_plan_for_apply(
    plan: dict[str, Any],
    *,
    action: str,
    selector: dict[str, Any],
    payload_file: Path | None,
    ctx: dict[str, Any],
) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("action") != action:
        raise SafetyError("Refused: plan action does not match the current command")
    if baseline.get("selector") != selector:
        raise SafetyError("Refused: plan selector does not match the current command")
    expected = str(baseline.get("payload_sha256") or "").strip()
    if payload_file is None:
        if expected:
            raise SafetyError("Refused: plan expects the original JSON payload file, but no --json-file was provided")
    else:
        actual = _sha256_file(payload_file)
        if not expected or expected != actual:
            raise SafetyError("Refused: payload file hash changed since plan creation (sha256 mismatch)")


def _load_plan_from_ctx(ctx: dict[str, Any]) -> dict[str, Any]:
    plan_in = str(ctx.get("plan_in") or "").strip()
    if not plan_in:
        raise SafetyError("Refused: this write command must be applied from a reviewed plan via --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    return plan


def _write_plan_if_requested(ctx: dict[str, Any], plan: dict[str, Any]) -> str | None:
    plan_out = str(ctx.get("plan_out") or "").strip()
    if not plan_out:
        return None
    return write_json_file(plan_out, plan)


def _write_receipt_if_requested(ctx: dict[str, Any], receipt: dict[str, Any]) -> str | None:
    receipt_out = str(ctx.get("receipt_out") or "").strip()
    if not receipt_out:
        return None
    return write_json_file(receipt_out, receipt)


def _verify_present(*, ctx: dict[str, Any], employee_id: str, date: str) -> dict[str, Any]:
    path = f"/scheduletimes/{employee_id}/{date}"
    try:
        payload = request_json(ctx=ctx, method="GET", path=path, expect_json=True)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "path": path, "error": str(e)}
    return {
        "ok": True,
        "path": path,
        "http_status": payload["status"],
        "data": payload["body"],
    }


def _build_selector(*, action: str, employee_id: str, date: str) -> dict[str, Any]:
    path = f"/scheduletimes/{employee_id}/{date}"
    return {
        "kind": "schedule_time",
        "action": action,
        "path": path,
        "employee_id": employee_id,
        "date": date,
    }


def _validate_payload_selector(schedule_time: dict[str, Any], *, employee_id: str, date: str) -> None:
    payload_employee_id = _extract_string(schedule_time.get("EmployeeId"))
    if payload_employee_id and payload_employee_id != employee_id:
        raise ValidationError("ScheduleTime.EmployeeId in the JSON file must match --employee-id")
    payload_date = _extract_string(schedule_time.get("Date"))
    if payload_date and payload_date != date:
        raise ValidationError("ScheduleTime.Date in the JSON file must match --date")


def _apply_write(
    *,
    action: str,
    audit_prefix: str,
    path: str,
    payload_file: Path,
    payload_obj: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
) -> int:
    plan = _build_plan(
        action=action,
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", f"schedule-time-{action}"],
        verification_plan={"type": "read-after-write", "path": selector["path"]},
        rollback_notes="No generic rollback. Re-run the schedule-time update with the prior values if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write(f"{audit_prefix}.plan", {"plan_out": plan_path, "employee_id": selector["employee_id"], "date": selector["date"]})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action=action, selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(ctx=ctx, method="PUT", path=path, json_body=payload_obj, expect_json=True)
    verification = _verify_present(ctx=ctx, employee_id=selector["employee_id"], date=selector["date"])
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_employee_id": selector["employee_id"],
        "target_date": selector["date"],
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(f"{audit_prefix}.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_schedule_times_update(args: Any, ctx: dict[str, Any]) -> int:
    employee_id = str(getattr(args, "employee_id", "") or "").strip()
    date = str(getattr(args, "date", "") or "").strip()
    payload_file, payload_obj, schedule_time = _load_payload_file(str(getattr(args, "json_file", "") or "").strip())
    _validate_payload_selector(schedule_time, employee_id=employee_id, date=date)
    selector = _build_selector(action="update", employee_id=employee_id, date=date)
    return _apply_write(
        action="update",
        audit_prefix="schedule_times.update",
        path=f"/scheduletimes/{employee_id}/{date}",
        payload_file=payload_file,
        payload_obj=payload_obj,
        selector=selector,
        ctx=ctx,
    )


def cmd_schedule_times_reset_day(args: Any, ctx: dict[str, Any]) -> int:
    employee_id = str(getattr(args, "employee_id", "") or "").strip()
    date = str(getattr(args, "date", "") or "").strip()
    payload_file, payload_obj, schedule_time = _load_payload_file(str(getattr(args, "json_file", "") or "").strip())
    _validate_payload_selector(schedule_time, employee_id=employee_id, date=date)
    selector = _build_selector(action="reset-day", employee_id=employee_id, date=date)
    return _apply_write(
        action="reset-day",
        audit_prefix="schedule_times.reset_day",
        path=f"/scheduletimes/{employee_id}/{date}/resetday",
        payload_file=payload_file,
        payload_obj=payload_obj,
        selector=selector,
        ctx=ctx,
    )
