from __future__ import annotations

import hashlib
import time
from typing import Any

from .errors import SafetyError, ValidationError


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_text(text: str) -> str:
    h = hashlib.sha256()
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def build_plan(
    *,
    tool: str,
    version: str,
    env_fingerprint: str,
    command: str,
    selector: dict[str, Any],
    risk_level: str,
    risk_reasons: list[str],
    request: dict[str, Any],
    verification_plan: dict[str, Any],
    baseline: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool": tool,
        "version": version,
        "generated_at_utc": utc_now(),
        "env_fingerprint": env_fingerprint,
        "command": command,
        "selector": selector,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "preconditions": ["plan env_fingerprint must match current environment"],
        "baseline": baseline,
        "request": request,
        "verification_plan": verification_plan,
        "rollback": {
            "supported": False,
            "notes": "Writes in this tool are treated as irreversible. No machine rollback path is available.",
        },
    }


def validate_plan_env(plan: dict[str, Any], *, env_fingerprint: str) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    if str(baseline.get("env_fingerprint") or "") != str(env_fingerprint):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")


def validate_plan_kind(plan: dict[str, Any], *, kind: str) -> None:
    selector = plan.get("selector")
    if not isinstance(selector, dict):
        raise ValidationError("Plan missing selector dict")
    if str(selector.get("kind") or "") != kind:
        raise SafetyError(f"Refused: plan kind mismatch (expected {kind})")

