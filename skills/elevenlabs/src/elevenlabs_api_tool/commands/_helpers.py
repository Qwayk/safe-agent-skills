from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..operations import Operation, OPERATIONS
from ..plans import (
    build_plan,
    default_proposed_changes,
    default_recovery,
    default_verification,
    ensure_write_safety_contract,
    load_plan_from_file,
    validate_plan_for_apply,
    write_plan_to_file,
)


def find_operation(name: str) -> Operation:
    for op in OPERATIONS:
        if op.name == name:
            return op
    raise RuntimeError(f"Operation not found: {name}")


def plan_for_operation(
    *,
    ctx: dict[str, Any],
    op: Operation,
    selector: dict[str, Any],
    request: dict[str, Any],
    proposed_changes: list[dict[str, Any]] | None = None,
    verification_plan: dict[str, Any] | None = None,
    recovery: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], str | None]:
    plan = build_plan(
        ctx=ctx,
        op=op,
        selector=selector,
        request=request,
        proposed_changes=proposed_changes or default_proposed_changes(op=op, selector=selector),
        verification_plan=verification_plan or default_verification(op=op),
        recovery=recovery or default_recovery(op=op),
    )
    plan_path = write_plan_to_file(plan=plan, path=ctx.get("plan_out"))
    return plan, plan_path


def plan_from_file_for_apply(*, ctx: dict[str, Any], op: Operation) -> dict[str, Any] | None:
    plan_path = ctx.get("plan_in")
    if not plan_path:
        return None
    plan = load_plan_from_file(plan_path)
    validate_plan_for_apply(plan=plan, op=op, ctx=ctx)
    return ensure_write_safety_contract(plan=plan, op=op)


def ensure_output_file(*, path: str | None, overwrite: bool) -> Path:
    if not path:
        raise ValidationError("Missing --out <path>")
    out_path = Path(path)
    if out_path.exists() and not overwrite:
        raise SafetyError("Refused: output file already exists; add --overwrite")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    return out_path


def write_binary_file(path: Path, data: bytes) -> dict[str, Any]:
    path.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    return {
        "file_path": str(path),
        "size_bytes": len(data),
        "sha256": digest,
    }


def ensure_json_output_file(*, path: str | None, overwrite: bool) -> Path:
    out_path = ensure_output_file(path=path, overwrite=overwrite)
    if out_path.suffix.lower() != ".json":
        raise ValidationError("JSON output must use a .json extension")
    return out_path


def write_json_file(path: Path, data: Any) -> dict[str, Any]:
    text = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    encoded = text.encode("utf-8")
    path.write_bytes(encoded)
    digest = hashlib.sha256(encoded).hexdigest()
    return {
        "file_path": str(path),
        "size_bytes": len(encoded),
        "sha256": digest,
    }
