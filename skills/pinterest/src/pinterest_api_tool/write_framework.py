from __future__ import annotations

import time
from typing import Any, Iterable

from .commands.write_safety import (
    before_state_refusal_verification_plan,
    blocked_plan,
    rollback_contract,
)


_REDACT_KEYS = {
    "authorization",
    "access_token",
    "refresh_token",
    "token",
    "client_secret",
    "app_secret",
    "password",
    "api_key",
}


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            lk = str(k).lower()
            if lk in _REDACT_KEYS or lk.endswith("_token") or lk.endswith("_secret") or lk.endswith("_api_key"):
                out[k] = "***REDACTED***"
            else:
                out[k] = redact(v)
        return out
    if isinstance(obj, list):
        return [redact(x) for x in obj]
    return obj


def _missing_flags_message(*, missing: list[str]) -> str:
    bits = ", ".join(missing)
    return f"Refusing to apply remote write: missing required flag(s): {bits}"


def require_write_allowed(ctx: dict[str, Any], *, acks_required: Iterable[str] = ()) -> None:
    missing: list[str] = []
    if not bool(ctx.get("apply")):
        missing.append("--apply")
    if not bool(ctx.get("yes")):
        missing.append("--yes")

    required = set(acks_required)
    if "ack-irreversible" in required and not bool(ctx.get("ack_irreversible")):
        missing.append("--ack-irreversible")
    if "ack-spend" in required and not bool(ctx.get("ack_spend")):
        missing.append("--ack-spend")
    if "ack-volume" in required and not bool(ctx.get("ack_volume")):
        missing.append("--ack-volume")
    if not bool(ctx.get("ack_no_snapshot")):
        missing.append("--ack-no-snapshot")

    if missing:
        raise RuntimeError(_missing_flags_message(missing=missing))


def write_operation(
    *,
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    json_body: Any | None = None,
) -> dict[str, Any]:
    op: dict[str, Any] = {"method": str(method).upper(), "path": str(path)}
    if params:
        op["params"] = redact(params)
    if json_body is not None:
        op["json_body"] = redact(json_body)
    return op


def build_plan(
    *,
    action: str,
    operations: list[dict[str, Any]],
    acks_required: list[str] | None = None,
    request: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    out = {
        "ok": True,
        "dry_run": True,
        "action": str(action),
        "generated_at_utc": now_utc(),
        "apply_requires": ["--apply", "--yes"],
        "acks_required": sorted(set(acks_required or [])),
        "request": redact(request or {}),
        "operations": operations,
        "warnings": list(warnings or []),
    }
    blocked = blocked_plan(
        action=str(action),
        operations=operations,
        acks_required=acks_required,
        request=redact(request or {}),
        warnings=list(warnings or []),
    )
    out["before_state"] = blocked["before_state"]
    out["verification_plan"] = before_state_refusal_verification_plan()
    out["rollback"] = rollback_contract(acks_required=acks_required)
    return out


def build_receipt(
    *,
    action: str,
    changed: bool,
    operations: list[dict[str, Any]],
    acks_required: list[str] | None = None,
    request: dict[str, Any] | None = None,
    before: Any | None = None,
    write_result: Any | None = None,
    after: Any | None = None,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "ok": True,
        "dry_run": False,
        "action": str(action),
        "generated_at_utc": now_utc(),
        "changed": bool(changed),
        "apply_requires": ["--apply", "--yes"],
        "acks_required": sorted(set(acks_required or [])),
        "request": redact(request or {}),
        "before": redact(before),
        "before_state": {
            "required": True,
            "supported": False,
            "status": "no_snapshot_available",
            "approval_required": "--ack-no-snapshot",
            "reason": "No reliable before-state snapshot is available for this Pinterest write.",
        },
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": "No reliable before-state snapshot is available for this Pinterest write.",
        },
        "write": redact(write_result),
        "after": redact(after),
        "operations": operations,
        "warnings": list(warnings or []),
    }
