from __future__ import annotations

import argparse
import csv
import hashlib
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from typing import Type

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file
from ._write_safety import (
    build_before_state_refusal_verification_plan,
    build_no_recovery_contract,
    emit_before_state_refusal,
    ensure_before_state_refusal_plan,
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
    # Demo write action: does nothing but shows the apply/verify pattern.
    apply = bool(ctx.get("apply"))
    if not apply:
        return {"ok": True, "dry_run": True, "plan": {"would_write": True, "row": row}}
    # Apply would do: POST/PUT then GET verify. Here we only return a stub.
    return {"ok": True, "applied": True, "verified": True}


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
    recovery = build_no_recovery_contract(
        notes="Jobs runner uses verification and receipts, but it has no generic rollback or restore path across mixed write rows."
    )
    verification_plan = {
        "type": "per-row",
        "notes": "In a real tool: verify writes via read-back or idempotence checks per row.",
    }
    plan = {
        "tool": ctx.get("tool") or "dynadot-api-tool",
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
        "proposed_changes": [
            {"row": idx, "action": str(r.get("action") or "").strip(), "input": r}
            for idx, r in enumerate(rows, start=1)
        ],
        "verification_plan": verification_plan,
        "rollback": {"supported": False, "notes": "Jobs runner has no generic rollback in this template."},
        "recovery": recovery,
    }
    if risk_level == "high":
        plan["post_apply_verification_plan"] = verification_plan
        ensure_before_state_refusal_plan(
            plan,
            selector_kind="jobs",
            selector_value=job_file or "<plan-in>",
            notes="Jobs with write actions are template-only here; use a real provider command for live Dynadot writes.",
        )
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

    has_writes = _has_write_actions(rows)

    # High-risk safety rule: if a jobs run includes write actions, applying requires a reviewed plan file.
    if bool(ctx.get("apply")) and has_writes and not plan_in:
        plan = _build_jobs_plan(
            job_file=str(job_file_path) if job_file_path else None,
            rows=rows,
            ctx=ctx,
        )
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
            "reasons": ["Refused: applying jobs with write actions requires a reviewed plan file (--plan-in). Run the dry-run first."],
            "refusal_type": "SafetyError",
            "plan": plan,
            "plan_out": auto_plan_path,
            "count": 0,
            "errors": 0,
            "results": [],
        }
        if "audit" in ctx:
            ctx["audit"].write("jobs.refused", {"reason": "missing-plan-in", "plan_out": auto_plan_path})
        ctx["out"].emit(out)
        return 0

    # Safety gate: only required when actually applying.
    if bool(ctx.get("apply")) and has_writes and not bool(ctx.get("yes")):
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

    if has_writes:
        return emit_before_state_refusal(
            ctx=ctx,
            plan=plan,
            audit_event="jobs.refused",
            extra={"count": 0, "errors": 0, "results": []},
        )

    recovery = build_no_recovery_contract(
        notes="Jobs runner uses verification and receipts, but it has no generic rollback or restore path across mixed write rows."
    )
    receipt = {
        "tool": ctx.get("tool") or "dynadot-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": plan.get("selector"),
        "changed": any((r.get("result") or {}).get("applied") for r in results if isinstance(r, dict)),
        "verification": {"ok": errors == 0, "details": {"type": "demo", "notes": "stub jobs verify"}},
        "diff_applied": [r for r in results if isinstance(r, dict)],
        "backups": recovery["backups"],
        "rollback_plan": recovery["rollback_plan"],
        "recovery": recovery,
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


def register_jobs(
    subparsers: argparse._SubParsersAction,  # type: ignore[name-defined]
    *,
    parser_class: Type[argparse.ArgumentParser],
) -> None:
    jobs = subparsers.add_parser("jobs", help="Batch operations from job files")
    jobs_sub = jobs.add_subparsers(dest="jobs_cmd", required=True, parser_class=parser_class)
    jobs_run = jobs_sub.add_parser("run", help="Run a CSV job file (demo actions)")
    jobs_run.add_argument("--file", required=False, help="Job CSV file (must include action column)")
    jobs_run.add_argument("--limit", type=int, default=None, help="Max number of rows to process")
    jobs_run.set_defaults(func=cmd_jobs_run, write_capable=True)
