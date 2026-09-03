from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any, cast

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
    selector: dict[str, Any] = (
        plan["selector"] if isinstance(plan.get("selector"), dict) else {}
    )
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
        "request_binding": request_binding(operation=op, selector=selector, request=request),
        "reviewed": False,
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "recovery": recovery,
    }
    return ensure_write_safety_contract(plan=plan, op=op)


def request_binding(*, operation: Operation, selector: dict[str, Any], request: dict[str, Any]) -> str:
    """Return a stable digest for the exact reviewed request contract."""
    material = {
        "operation": operation.name,
        "endpoint": f"{operation.method.upper()} {operation.path}",
        "selector": selector,
        "request": request,
    }
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def validate_request_contract(*, op: Operation, request: dict[str, Any]) -> None:
    params = cast(dict[str, Any], request.get("params")) if isinstance(request.get("params"), dict) else {}
    files = request.get("files") if isinstance(request.get("files"), dict) else {}
    files_obj = cast(dict[str, Any], files)
    missing_query = [name for name in op.required_query_params if not params.get(name)]
    if missing_query:
        raise ValidationError(f"Missing required query parameter(s): {', '.join(missing_query)}")
    unknown_query = sorted(set(params) - set(op.query_params or op.required_query_params))
    if unknown_query:
        raise ValidationError(f"Unknown query parameter(s): {', '.join(unknown_query)}")
    if op.request_body_required and not (isinstance(request.get("json"), dict) or request.get("body_file") or request.get("files")):
        raise ValidationError("Missing required request body")
    if op.request_body_fields and isinstance(request.get("json"), dict):
        known = set(op.request_body_fields)
        actual: set[str] = set()
        def walk(value: Any, prefix: str = "") -> None:
            if isinstance(value, dict):
                for key, child in value.items():
                    path = f"{prefix}.{key}" if prefix else key
                    actual.add(path)
                    walk(child, path)
            elif isinstance(value, list):
                # Array item objects use the same dotted contract prefix.
                # Walk every item so nested fields are checked without
                # inventing numeric indices in the public request schema.
                for child in value:
                    walk(child, prefix)
        walk(request["json"])
        open_prefixes = tuple(op.request_body_open_prefixes)
        unknown = sorted(path for path in actual if path not in known and not any(item.startswith(path + ".") for item in known) and not any(path == p or path.startswith(p + ".") for p in open_prefixes))
        if unknown:
            raise ValidationError(f"Unknown request body field(s): {', '.join(unknown)}")
        body_obj = cast(dict[str, Any], request["json"])
        def required_path_missing(value: Any, parts: list[str]) -> bool:
            """Check a required path only beneath parents that are present.

            OpenAPI marks children required within an object schema, but that
            does not make an optional parent object globally required. Lists
            are traversed item-by-item; an empty list has no items to fail.
            """
            if not parts:
                return False
            if isinstance(value, list):
                return any(required_path_missing(item, parts) for item in value)
            if not isinstance(value, dict):
                return True
            name = parts[0]
            if name not in value:
                # A missing intermediate object means its branch was not
                # supplied.  Only the final property is required once its
                # immediate parent object/item is present.
                return len(parts) == 1
            if len(parts) == 1:
                return False
            return required_path_missing(value[name], parts[1:])

        missing: list[str] = []
        for field in op.request_body_required_fields:
            if field in files_obj:
                continue
            parts = field.split(".")
            # A dotted field is conditional on its top-level parent being
            # supplied. Top-level required fields remain unconditional.
            if len(parts) > 1 and parts[0] not in body_obj:
                continue
            if required_path_missing(body_obj, parts):
                missing.append(field)
        missing.sort()
        if missing:
            raise ValidationError(f"Missing required request body field(s): {', '.join(missing)}")
    content_types = set(op.request_body_content_types)
    if files_obj and content_types and "multipart/form-data" not in content_types:
        raise ValidationError("Upload fields require a multipart/form-data request contract")
    # Multipart operations may legitimately encode URL/text-only requests as
    # form fields even when no binary part is present.
    unknown_files = sorted(set(files_obj) - set(op.request_file_fields)) if op.request_file_fields else (sorted(files_obj) if files_obj else [])
    if unknown_files:
        raise ValidationError(f"Unknown upload field(s): {', '.join(unknown_files)}")
    missing_files = sorted(set(op.request_file_required_fields) - set(files_obj))
    if missing_files:
        raise ValidationError(f"Missing required upload field(s): {', '.join(missing_files)}")


def validate_plan_for_apply(
    *, plan: dict[str, Any], op: Operation, ctx: dict[str, Any], selector: dict[str, Any] | None = None,
    request: dict[str, Any] | None = None,
) -> None:
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
    binding = plan.get("request_binding")
    if not isinstance(binding, str) or not re.fullmatch(r"[0-9a-f]{64}", binding):
        raise SafetyError("Refused: reviewed plan has no request binding")
    if plan.get("reviewed") is not True:
        raise SafetyError("Refused: plan must be explicitly marked reviewed before apply")
    if selector is not None and request is not None:
        expected = request_binding(operation=op, selector=selector, request=request)
        if plan.get("request_binding") != expected:
            raise SafetyError("Refused: reviewed plan does not match the exact apply inputs")


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
        "status": "final",
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "applied_at_utc": _utc_now(),
        "env_fingerprint": cfg.base_url,
        "command": ctx.get("command_str"),
        "operation": op.name,
        "request_binding": plan.get("request_binding"),
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
        bound_files: dict[str, Any] = {}
        for key, value in files.items():
            values = value if isinstance(value, list) else [value]
            items: list[dict[str, Any]] = []
            for one in values:
                path = str(one)
                item: dict[str, Any] = {"path": path}
                candidate = Path(path)
                if candidate.exists() and candidate.is_file():
                    item["sha256"] = hashlib.sha256(candidate.read_bytes()).hexdigest()
                items.append(item)
            bound_files[key] = items if len(items) > 1 else items[0]
        summary["files"] = bound_files
    return summary


def default_proposed_changes(*, op: Operation, selector: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "description": f"{op.description}",
            "selector": selector,
        }
    ]


def default_verification(*, op: Operation) -> dict[str, Any]:
    # Keep the reviewed plan honest about the evidence apply will attempt.
    # Import lazily to avoid the operations -> plans module cycle.
    if {"binary_output", "sensitive_output"} & set(op.safety):
        local = {"type": "local_output", "status": "planned", "notes": "Apply will verify output-file existence, size, and SHA-256."}
        if op.method.upper() in {"PUT", "PATCH"}:
            from .operations import OPERATIONS
            paired = next((c for c in OPERATIONS if c.method.upper() == "GET" and c.path == op.path), None)
            if paired is not None:
                return {"type": "composite", "status": "planned", "local_output": local, "paired_readback": {"method": "GET", "endpoint": paired.path, "status_only": True, "response_body_stored": False}}
        return local
    if "write" in op.safety and op.method.upper() in {"PUT", "PATCH"}:
        from .operations import OPERATIONS

        paired = next(
            (
                candidate
                for candidate in OPERATIONS
                if candidate.method.upper() == "GET" and candidate.path == op.path
            ),
            None,
        )
        if paired is not None:
            return {
                "type": "paired_readback",
                "status": "planned",
                "method": "GET",
                "endpoint": paired.path,
                "status_only": True,
                "response_body_stored": False,
                "notes": "Apply will perform a status-only GET readback using only query fields allowed by the GET contract.",
            }
    if "write" in op.safety:
        return {
            "type": "unsupported",
            "status": "unsupported",
            "notes": (
                "No paired readback operation is declared for this generic write; "
                "provider state verification remains unsupported."
            ),
        }
    return {"type": "read", "status": "planned", "notes": "Inspect the response to confirm the expected data."}


def default_recovery(*, op: Operation) -> dict[str, Any]:
    return build_no_recovery_contract(
        notes=(
            f"{op.name}: no automated rollback is available for this command; "
            "it is treated as irreversible and needs manual cleanup if removal is required."
        )
    )
