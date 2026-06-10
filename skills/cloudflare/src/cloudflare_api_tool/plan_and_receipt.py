from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import SafetyError, ValidationError
from .json_files import read_json_file, write_json_file


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def sha256_of_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 128), b""):
            h.update(chunk)
    return h.hexdigest()


def write_plan_if_requested(ctx: dict, plan: dict) -> str | None:
    out_path = str(ctx.get("plan_out") or "").strip()
    if not out_path:
        return None
    return write_json_file(out_path, plan)


def write_receipt_if_requested(ctx: dict, receipt: dict) -> str | None:
    out_path = str(ctx.get("receipt_out") or "").strip()
    if not out_path:
        return None
    return write_json_file(out_path, receipt)


def load_plan_in(ctx: dict) -> dict | None:
    plan_in = str(ctx.get("plan_in") or "").strip()
    if not plan_in:
        return None
    obj = read_json_file(plan_in)
    if not isinstance(obj, dict):
        raise ValidationError("Plan file must contain a JSON object")
    return obj


def require_plan_matches(*, expected_plan: dict, provided_plan: dict) -> None:
    """
    Safety: When applying with `--plan-in`, refuse if the newly generated plan differs.

    This protects against drift (target changed) and against accidentally applying a different change
    than the reviewed plan.
    """
    expected_selector = expected_plan.get("selector")
    provided_selector = provided_plan.get("selector")
    if expected_selector != provided_selector:
        raise SafetyError("Refusing to apply: plan selector does not match current request (drift or wrong plan file).")

    expected_changes = expected_plan.get("proposed_changes")
    provided_changes = provided_plan.get("proposed_changes")
    if expected_changes != provided_changes:
        raise SafetyError("Refusing to apply: plan proposed_changes do not match current state (drift or wrong plan file).")


@dataclass(frozen=True)
class SafeOutPath:
    abs_path: Path
    rel_to_project: str


def resolve_safe_out_path(*, project_dir: Path, out_path: str, allow_overwrite: bool) -> SafeOutPath:
    """
    Resolve an output path for sensitive reads.

    Rules:
    - Relative paths are resolved under `project_dir`.
    - Absolute paths must still live under `project_dir` (so the tool can't write arbitrarily).
    """
    if not out_path or not str(out_path).strip():
        raise ValidationError("Missing --out")
    base = project_dir.resolve()
    base.mkdir(parents=True, exist_ok=True)

    p = Path(out_path)
    resolved = (base / p).resolve() if not p.is_absolute() else p.resolve()
    try:
        common = os.path.commonpath([str(base), str(resolved)])
    except Exception:
        common = ""
    if common != str(base):
        raise SafetyError("Refusing to write outside --project-dir. Choose an --out path under the project directory.")

    if resolved.exists() and not allow_overwrite:
        raise SafetyError(f"Refusing to overwrite existing file: {resolved} (pass --overwrite to allow).")

    rel = os.path.relpath(str(resolved), str(base))
    return SafeOutPath(abs_path=resolved, rel_to_project=rel)
