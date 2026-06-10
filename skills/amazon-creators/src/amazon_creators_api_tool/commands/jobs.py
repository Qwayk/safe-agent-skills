from __future__ import annotations

import csv
import hashlib
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file
from .write_safety import (
    before_state_refusal_verification_plan,
    blocked_before_state,
    ensure_blocked_apply_contract,
    recovery_contract,
    refusal_output,
)


@dataclass(frozen=True)
class ActionSpec:
    name: str
    is_write: bool
    handler: Callable[[dict[str, str], dict[str, Any]], dict[str, Any]]


def _demo_read(row: dict[str, str], ctx: dict[str, Any]) -> dict[str, Any]:
    _ = ctx
    return {"ok": True, "message": "read action (demo)", "row": row}


def _demo_write(row: dict[str, str], ctx: dict[str, Any]) -> dict[str, Any]:
    apply = bool(ctx.get("apply"))
    if not apply:
        return {"ok": True, "dry_run": True, "plan": {"would_write": True, "row": row}}
    return {
        "ok": True,
        "dry_run": False,
        "refused": True,
        "reasons": ["Refused: jobs write.ping is template-only and has no live Amazon Creators write executor."],
    }


_ACTIONS = {
    "read.ping": ActionSpec(name="read.ping", is_write=False, handler=_demo_read),
    "write.ping": ActionSpec(name="write.ping", is_write=True, handler=_demo_write),
}


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _has_write_actions(rows: list[dict[str, Any]]) -> bool:
    for row in rows:
        action = str(row.get("action") or "").strip()
        spec = _ACTIONS.get(action)
        if spec and spec.is_write:
            return True
    return False


def _build_jobs_plan(*, job_file: str | None, rows: list[dict[str, Any]], ctx: dict[str, Any]) -> dict[str, Any]:
    risk_level = "high" if _has_write_actions(rows) else "low"
    risk_reasons = ["jobs-batch"] + (["contains-write-actions"] if risk_level == "high" else [])
    selector: dict[str, Any] = {"kind": "jobs", "value": job_file or "<plan-in>"}
    proposed_changes = [
        {"row": idx, "action": str(r.get("action") or "").strip(), "input": r}
        for idx, r in enumerate(rows, start=1)
    ]
    plan = {
        "tool": ctx.get("tool") or "amazon-creators-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "preconditions": ["env_fingerprint must match", "plan rows must match intended job file/actions"],
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "job_file_sha256": _sha256_file(Path(job_file)) if job_file else None,
        },
        "proposed_changes": proposed_changes,
        "verification_plan": {
            "type": "per-row",
            "notes": "Read-only rows can run; write rows are template-only and have no live Amazon Creators write executor.",
        },
        "recovery": recovery_contract(),
    }
    if _has_write_actions(rows):
        plan["before_state"] = blocked_before_state(
            action="jobs.run",
            local_state={"kind": "jobs_run", "writes_receipt": True},
        )
        plan["verification_plan"] = before_state_refusal_verification_plan()
    return plan


def _validate_plan_for_apply(plan: dict[str, Any], *, ctx: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")


def cmd_jobs_run(args: Any, ctx: dict[str, Any]) -> int:
    try:
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan_obj = read_json_file(plan_in)
            if not isinstance(plan_obj, dict):
                raise ValidationError("Plan file must be a JSON object")
            _validate_plan_for_apply(plan_obj, ctx=ctx)

            # Strong drift detection for plan apply: require the original job file and verify its hash.
            # This prevents applying a plan against a changed job file by accident.
            if bool(ctx.get("apply")):
                if not getattr(args, "file", None):
                    raise SafetyError("Refused: applying a jobs plan requires --file (to verify job_file_sha256)")
                job_file_path = Path(args.file)
                if not job_file_path.exists():
                    raise ValidationError(f"Job file not found: {job_file_path}")
                expected = (plan_obj.get("baseline") or {}).get("job_file_sha256")
                actual = _sha256_file(job_file_path)
                if expected and str(expected) != str(actual):
                    raise SafetyError("Refused: job file changed since plan creation (sha256 mismatch)")

            rows_any = plan_obj.get("proposed_changes")
            if not isinstance(rows_any, list):
                raise ValidationError("Plan file missing proposed_changes list")
            rows: list[dict[str, Any]] = []
            for item in rows_any:
                if not isinstance(item, dict):
                    raise ValidationError("Plan proposed_changes must be a list of objects")
                row_input = item.get("input")
                if not isinstance(row_input, dict):
                    raise ValidationError("Plan proposed_changes items must include an input object")
                rows.append({k: ("" if v is None else str(v)) for k, v in row_input.items()})
            job_file_path = None
        else:
            if not getattr(args, "file", None):
                raise ValidationError("Missing --file (or provide --plan-in)")
            job_file_path = Path(args.file)
            if not job_file_path.exists():
                raise ValidationError(f"Job file not found: {job_file_path}")

            rows = []
            with job_file_path.open(newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row:
                        rows.append(row)
    except SafetyError as e:
        out = {
            "ok": True,
            "dry_run": not bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(e)],
            "refusal_type": "SafetyError",
            "count": 0,
            "errors": 0,
            "results": [],
        }
        if "audit" in ctx:
            ctx["audit"].write("jobs.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as e:
        out = {
            "ok": False,
            "dry_run": not bool(ctx.get("apply")),
            "error": str(e),
            "error_type": "ValidationError",
            "count": 0,
            "errors": 1,
            "results": [],
        }
        if "audit" in ctx:
            ctx["audit"].write("jobs.error", out)
        ctx["out"].emit(out)
        return 1

    processed = 0
    errors = 0
    results: list[dict[str, Any]] = []

    if args.limit is not None:
        rows = rows[: int(args.limit)]

    # Safety gate: only required when actually applying.
    if bool(ctx.get("apply")) and _has_write_actions(rows) and not bool(ctx.get("yes")):
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": ["Refused: jobs that include write actions require --apply --yes"],
            "refusal_type": "SafetyError",
            "count": 0,
            "errors": 0,
            "results": [],
        }
        if "audit" in ctx:
            ctx["audit"].write("jobs.refused", out)
        ctx["out"].emit(out)
        return 0

    plan = _build_jobs_plan(
        job_file=str(job_file_path) if job_file_path else None,
        rows=rows,
        ctx=ctx,
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if plan_out and not bool(ctx.get("apply")) else None

    if bool(ctx.get("apply")) and _has_write_actions(rows):
        plan = ensure_blocked_apply_contract(
            plan,
            action="jobs.run",
            local_state={"kind": "jobs_run", "writes_receipt": True},
        )
        out = refusal_output(plan=plan)
        out.update({"count": 0, "errors": 0, "results": []})
        if "audit" in ctx:
            ctx["audit"].write("jobs.refused", {"reasons": out["reasons"]})
        ctx["out"].emit(out)
        return 0

    for row_num, row in enumerate(rows, start=1):
        if not row:
            continue
        processed += 1

        action_name = (row.get("action") or "").strip()
        try:
            if not action_name:
                raise ValidationError("Missing action column")
            spec = _ACTIONS.get(action_name)
            if spec is None:
                raise ValidationError(f"Unknown action: {action_name} (supported: {', '.join(sorted(_ACTIONS))})")

            res = spec.handler({k: ("" if v is None else str(v)) for k, v in row.items()}, ctx)
            results.append({"row": row_num, "action": action_name, "input": row, "result": res})
        except Exception as e:  # noqa: BLE001
            errors += 1
            results.append({"row": row_num, "action": action_name or "<empty>", "input": row, "error": str(e)})
            break

    if not bool(ctx.get("apply")):
        out = {
            "ok": errors == 0,
            "dry_run": True,
            "plan": plan,
            "plan_out": plan_path,
            "count": processed,
            "errors": errors,
            "results": results,
        }
        if "audit" in ctx:
            ctx["audit"].write("jobs.plan", {"plan_out": plan_path, "count": processed, "errors": errors})
        ctx["out"].emit(out)
        return 1 if errors else 0

    receipt = {
        "tool": ctx.get("tool") or "amazon-creators-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": plan.get("selector"),
        "changed": any((r.get("result") or {}).get("applied") for r in results if isinstance(r, dict)),
        "verification": {"ok": errors == 0, "details": {"type": "demo", "notes": "stub jobs verify"}},
        "diff_applied": [r for r in results if isinstance(r, dict)],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None

    out = {
        "ok": errors == 0,
        "dry_run": False,
        "receipt": receipt,
        "receipt_out": receipt_path,
        "count": processed,
        "errors": errors,
        "results": results,
    }
    if "audit" in ctx:
        ctx["audit"].write("jobs.apply", {"receipt_out": receipt_path, "count": processed, "errors": errors})
    ctx["out"].emit(out)
    return 1 if errors else 0
