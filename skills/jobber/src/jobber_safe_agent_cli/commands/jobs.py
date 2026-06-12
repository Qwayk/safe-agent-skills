from __future__ import annotations

import csv
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ..errors import SafetyError, ValidationError
from ..http import GraphQLClient
from ..json_files import read_json_file, write_json_file
from ..schema_registry import OperationField, mutation_fields, query_fields
from .common import (
    build_graphql_selection,
    build_operation_document,
    filter_allowed_args,
    mutation_requires_ack_irreversible,
    mutation_requires_no_snapshot,
    mutation_snapshot_plan_fields,
)


@dataclass(frozen=True)
class ActionSpec:
    name: str
    is_write: bool
    handler: Callable[[dict[str, str], dict[str, Any]], dict[str, Any]]


def _query_map() -> dict[str, OperationField]:
    return {field.name: field for field in query_fields()}


def _mutation_map() -> dict[str, OperationField]:
    return {field.name: field for field in mutation_fields()}


def _parse_row_args(row: dict[str, str]) -> dict[str, Any]:
    raw = str(row.get("args_json") or "").strip()
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except Exception:
        raise ValidationError("Invalid JSON in args_json column") from None
    if not isinstance(parsed, dict):
        raise ValidationError("args_json column must contain a JSON object")
    return parsed


def _parse_row_selection(row: dict[str, str]) -> str | None:
    selection = str(row.get("selection") or "").strip()
    return selection or None


def _parse_row_limit(row: dict[str, str]) -> int | None:
    raw = str(row.get("limit") or "").strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except Exception:
        raise ValidationError("limit column must be an integer") from None
    if value < 1:
        raise ValidationError("limit column must be greater than zero")
    return value


def _add_limit_if_supported(*, spec: OperationField, args_in: dict[str, Any], limit: int | None) -> dict[str, Any]:
    if limit is None:
        return args_in
    allowed = {arg.name for arg in spec.args}
    if "limit" in allowed and "limit" not in args_in:
        args_in["limit"] = limit
    elif "first" in allowed and "first" not in args_in:
        args_in["first"] = limit
    return args_in


def _operation_payload(*, spec: OperationField, row: dict[str, str], operation_type: str) -> dict[str, Any]:
    args_in = filter_allowed_args(spec=spec, raw_args=_parse_row_args(row))
    if operation_type == "query":
        args_in = _add_limit_if_supported(spec=spec, args_in=args_in, limit=_parse_row_limit(row))
    selection = _parse_row_selection(row)
    if spec.type.kind not in {"SCALAR", "ENUM"}:
        selection = build_graphql_selection(spec.type.kind, selection)
    document = build_operation_document(
        operation=spec.name,
        args=args_in,
        selection=selection,
        operation_type=operation_type,
    )
    return {
        "operation": spec.name,
        "operation_type": operation_type,
        "arguments": args_in,
        "selection": selection,
        "graphql": {"document": document},
    }


def _execute_graphql(payload: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    if not ctx["cfg"].token:
        raise ValidationError("Missing access token for job execution")
    client = GraphQLClient(
        endpoint=ctx["cfg"].graphql_url,
        token=ctx["cfg"].token,
        graphql_version=ctx["cfg"].graphql_version,
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
    )
    return client.execute(str(payload["graphql"]["document"]), variables=None)


def _registry_read_handler(spec: OperationField) -> Callable[[dict[str, str], dict[str, Any]], dict[str, Any]]:
    def _handler(row: dict[str, str], ctx: dict[str, Any]) -> dict[str, Any]:
        payload = _operation_payload(spec=spec, row=row, operation_type="query")
        if not bool(ctx.get("apply")):
            return {"ok": True, "dry_run": True, "plan": payload}
        response = _execute_graphql(payload, ctx)
        return {"ok": True, "dry_run": False, "operation": spec.name, "result": response}

    return _handler


def _registry_write_handler(spec: OperationField) -> Callable[[dict[str, str], dict[str, Any]], dict[str, Any]]:
    def _handler(row: dict[str, str], ctx: dict[str, Any]) -> dict[str, Any]:
        payload = _operation_payload(spec=spec, row=row, operation_type="mutation")
        plan = {
            "command": f"write.{spec.name}",
            "mutation": spec.name,
            "arguments": payload["arguments"],
            "graphql": payload["graphql"],
            "risk": "high" if mutation_requires_no_snapshot(spec.name) else "medium",
            **mutation_snapshot_plan_fields(),
            "verification_plan": {
                "type": "read_back",
                "required_for_apply": True,
            },
        }
        if not bool(ctx.get("apply")):
            return {"ok": True, "dry_run": True, "plan": plan}
        response = _execute_graphql(payload, ctx)
        return {"ok": True, "dry_run": False, "operation": spec.name, "plan": plan, "result": response}

    return _handler


def _resolve_action(action: str) -> ActionSpec | None:
    if action.startswith("read."):
        field_name = action[len("read.") :]
        spec = _query_map().get(field_name)
        if spec:
            return ActionSpec(name=action, is_write=False, handler=_registry_read_handler(spec))
    if action.startswith("write."):
        field_name = action[len("write.") :]
        spec = _mutation_map().get(field_name)
        if spec:
            return ActionSpec(name=action, is_write=True, handler=_registry_write_handler(spec))
    return None


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
        spec = _resolve_action(action)
        if spec and spec.is_write:
            return True
    return False


def _build_jobs_plan(*, job_file: str | None, rows: list[dict[str, Any]], ctx: dict[str, Any]) -> dict[str, Any]:
    risk_level = "high" if _has_write_actions(rows) else "low"
    risk_reasons = ["jobs-batch"] + (["contains-write-actions"] if risk_level == "high" else [])
    selector: dict[str, Any] = {"kind": "jobs", "value": job_file or "<plan-in>"}
    return {
        "tool": ctx.get("tool") or "qwayk-jobber-safe-agent-cli",
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
        **mutation_snapshot_plan_fields(),
        "verification_plan": {
            "type": "per-row",
            "notes": "Verify writes via read-back or idempotence checks per row.",
        },
        "rollback": {
            "supported": False,
            "notes": "Jobs runner has no generic rollback; use per-operation restore steps when available.",
        },
    }


def _validate_plan_for_apply(plan: dict[str, Any], *, ctx: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")


def _is_no_snapshot_write_action(*, action: str) -> bool:
    action = str(action or "").strip()
    if not action.startswith("write."):
        return False
    field_name = action[len("write.") :]
    spec = _mutation_map().get(field_name)
    if not spec:
        return False
    return mutation_requires_no_snapshot(spec.name)


def _is_irreversible_write_action(*, action: str) -> bool:
    action = str(action or "").strip()
    if not action.startswith("write."):
        return False
    field_name = action[len("write.") :]
    spec = _mutation_map().get(field_name)
    if not spec:
        return False
    return mutation_requires_ack_irreversible(spec.name)


def _has_no_snapshot_write_actions(rows: list[dict[str, Any]]) -> bool:
    for row in rows:
        if _is_no_snapshot_write_action(action=str(row.get("action") or "")):
            return True
    return False


def _has_irreversible_write_actions(rows: list[dict[str, Any]]) -> bool:
    for row in rows:
        if _is_irreversible_write_action(action=str(row.get("action") or "")):
            return True
    return False


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
    if bool(ctx.get("apply")) and _has_write_actions(rows) and not ctx.get("plan_in"):
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": ["Refused: jobs that include write actions require --plan-in from a reviewed plan"],
            "refusal_type": "SafetyError",
            "count": 0,
            "errors": 0,
            "results": [],
        }
        if "audit" in ctx:
            ctx["audit"].write("jobs.refused", out)
        ctx["out"].emit(out)
        return 0
    if bool(ctx.get("apply")) and _has_no_snapshot_write_actions(rows) and not bool(ctx.get("ack_no_snapshot")):
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": ["Refused: jobs that include high-risk write actions require --ack-no-snapshot"],
            "refusal_type": "SafetyError",
            "count": 0,
            "errors": 0,
            "results": [],
        }
        if "audit" in ctx:
            ctx["audit"].write("jobs.refused", out)
        ctx["out"].emit(out)
        return 0

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
    if bool(ctx.get("apply")) and _has_irreversible_write_actions(rows) and not bool(ctx.get("ack_irreversible")):
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": ["Refused: jobs that include irreversible write actions require --ack-irreversible"],
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
            spec = _resolve_action(action_name)
            if spec is None:
                raise ValidationError(
                    "Unknown action: "
                    f"{action_name} (use read.<JobberQuery> or write.<JobberMutation>)"
                )

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
        "tool": ctx.get("tool") or "qwayk-jobber-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": plan.get("selector"),
        "changed": any((r.get("result") or {}).get("applied") for r in results if isinstance(r, dict)),
        "verification": {"ok": errors == 0, "details": {"type": "per-row", "notes": "Each row result is included"}},
        "diff_applied": [r for r in results if isinstance(r, dict)],
        "backups": [],
        "rollback_plan": None,
        **mutation_snapshot_plan_fields(),
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
