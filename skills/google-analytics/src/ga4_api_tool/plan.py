from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any

from .config import Config
from .errors import SafetyError, ValidationError
from .redaction import sanitize


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _stable_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_no_recovery_contract() -> dict[str, Any]:
    return {
        "automatic_rollback": False,
        "backups": [],
        "snapshots": [],
        "rollback_plan": None,
        "restore_note": "No automatic rollback, snapshots, or backups are created. "
        "If a restore action is available, run a separate explicit restore command as its own command.",
    }


def build_before_state_contract(*, required: bool = True, provider: str = "GA4") -> dict[str, Any]:
    if not required:
        return {
            "required": False,
            "supported": False,
            "status": "not-required",
            "notes": "This operation is read-like, so no before-state capture is required.",
        }
    return {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "approval_required": "--ack-no-snapshot",
        "notes": (
            f"No useful before-state snapshot is captured for this {provider} write. "
            "The write may still run after the reviewed plan and explicit no-snapshot approval."
        ),
    }


def build_before_state_refusal_plan(*, provider: str = "GA4") -> dict[str, Any]:
    return {
        "type": "best_effort_after_apply",
        "requires_no_snapshot_approval": True,
        "notes": f"Apply can run after explicit no-snapshot approval, then records the {provider} response.",
    }


def env_fingerprint(cfg: Config) -> str:
    # Intentionally omit secrets. This fingerprint is used for plan drift checks.
    payload = {
        "auth_mode": cfg.auth_mode,
        "scopes": list(cfg.scopes),
        "admin_base_url": cfg.admin_base_url,
        "data_base_url": cfg.data_base_url,
        "timeout_s": cfg.timeout_s,
        "service_account_json": cfg.service_account_json if cfg.auth_mode == "service_account_json" else None,
        "has_refresh_token": bool(cfg.oauth_refresh_token) if cfg.auth_mode == "oauth_refresh_token" else None,
    }
    return _sha256_hex(_stable_json(payload))


@dataclass(frozen=True)
class PreparedRequest:
    method: str
    url: str
    query: dict[str, Any]
    body: dict[str, Any] | None


def request_fingerprint(req: PreparedRequest) -> str:
    payload = {
        "method": req.method,
        "url": req.url,
        "query": req.query,
        "body": req.body,
    }
    return _sha256_hex(_stable_json(sanitize(payload)))


def build_plan(
    *,
    ctx: dict[str, Any],
    operation: dict[str, Any],
    risk: dict[str, Any],
    req: PreparedRequest,
    env_fp: str,
    req_fp: str,
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "ga4-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "command": ctx.get("command_str") or None,
        "env_fingerprint": env_fp,
        "request_fingerprint": req_fp,
        "operation": operation,
        "risk": risk,
        "request": sanitize(
            {
                "method": req.method,
                "url": req.url,
                "query": req.query,
                "body": req.body,
            }
        ),
        "preconditions": [
            "env_fingerprint must match",
            "request_fingerprint must match",
        ],
        "before_state": build_before_state_contract(provider="GA4"),
        "verification_plan": build_before_state_refusal_plan(provider="GA4"),
    }


def validate_plan_for_apply(
    plan: dict[str, Any],
    *,
    expected_env_fingerprint: str,
    expected_request_fingerprint: str,
    expected_operation: dict[str, Any],
) -> None:
    if not isinstance(plan, dict):
        raise ValidationError("Plan must be a JSON object")
    if str(plan.get("env_fingerprint") or "") != expected_env_fingerprint:
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if str(plan.get("request_fingerprint") or "") != expected_request_fingerprint:
        raise SafetyError("Refused: plan request_fingerprint does not match current request")
    op = plan.get("operation")
    if not isinstance(op, dict):
        raise ValidationError("Plan missing operation dict")
    for k in ("service", "version", "method_id"):
        if str(op.get(k) or "") != str(expected_operation.get(k) or ""):
            raise SafetyError("Refused: plan operation does not match current command")
