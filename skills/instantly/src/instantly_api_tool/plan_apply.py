from __future__ import annotations

from typing import Any

from .errors import SafetyError, ValidationError
from .json_files import read_json_file
from .plans import validate_plan_env, validate_plan_kind


def require_plan_in_on_apply(*, apply: bool, plan_in: str | None, reason: str) -> None:
    if apply and not str(plan_in or "").strip():
        raise SafetyError(f"Refused: {reason} requires --plan-in")


def load_apply_plan(*, plan_in: str, env_fingerprint: str, kind: str) -> dict[str, Any]:
    plan_obj_any = read_json_file(plan_in)
    if not isinstance(plan_obj_any, dict):
        raise ValidationError("Plan file must be a JSON object")
    plan_obj: dict[str, Any] = dict(plan_obj_any)
    validate_plan_env(plan_obj, env_fingerprint=env_fingerprint)
    validate_plan_kind(plan_obj, kind=kind)
    return plan_obj


def request_from_plan(
    plan: dict[str, Any],
    *,
    expected_method: str | None = None,
) -> tuple[str, str, dict[str, Any]]:
    request_any = plan.get("request")
    if not isinstance(request_any, dict):
        raise ValidationError("Plan missing request object")
    method = str(request_any.get("method") or "").strip().upper()
    path = str(request_any.get("path") or "").strip()
    body_any = request_any.get("body")
    if not isinstance(body_any, dict):
        raise ValidationError("Plan request body must be a JSON object")
    body = dict(body_any)

    if expected_method and method != expected_method.upper():
        raise SafetyError(f"Refused: plan method mismatch (expected {expected_method.upper()})")
    if not method:
        raise ValidationError("Plan request missing method")
    if not path.startswith("/"):
        raise ValidationError("Plan request missing path")

    return method, path, body

