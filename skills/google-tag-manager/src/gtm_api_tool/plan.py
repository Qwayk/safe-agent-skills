from __future__ import annotations

import hashlib
import json
import time
from typing import Any

from .config import Config
from .errors import SafetyError, ValidationError


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _canon_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def env_fingerprint(cfg: Config) -> str:
    safe = {
        "base_url": cfg.base_url,
        "auth_mode": cfg.auth_mode,
        "scopes": list(cfg.scopes),
    }
    return hashlib.sha256(_canon_json(safe).encode("utf-8")).hexdigest()


def request_fingerprint(
    *,
    method_id: str,
    http_method: str,
    path_template: str,
    path_params: dict[str, Any],
    query: dict[str, Any] | None,
    body: dict[str, Any] | None,
) -> str:
    safe = {
        "method_id": method_id,
        "http_method": http_method,
        "path_template": path_template,
        "path_params": path_params,
        "query": query or {},
        "body": body or None,
    }
    return hashlib.sha256(_canon_json(safe).encode("utf-8")).hexdigest()


def build_plan(
    *,
    tool: str,
    version: str,
    command: str | None,
    cfg: Config,
    method_id: str,
    http_method: str,
    path_template: str,
    path_params: dict[str, Any],
    query: dict[str, Any] | None,
    body: dict[str, Any] | None,
    risk_level: str,
    risk_reasons: list[str],
) -> dict[str, Any]:
    efp = env_fingerprint(cfg)
    rfp = request_fingerprint(
        method_id=method_id,
        http_method=http_method,
        path_template=path_template,
        path_params=path_params,
        query=query,
        body=body,
    )
    return {
        "tool": tool,
        "version": version,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": efp,
        "command": command,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "request": {
            "method_id": method_id,
            "http_method": http_method,
            "path_template": path_template,
            "path_params": path_params,
            "query": query or {},
            "body": body,
            "request_fingerprint": rfp,
        },
    }


def _as_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return obj
    raise ValidationError("Plan file must be a JSON object")


def validate_plan_for_apply(
    plan_obj: Any,
    *,
    cfg: Config,
    expected_env_fingerprint: str,
    expected_request_fingerprint: str,
) -> dict[str, Any]:
    plan = _as_dict(plan_obj)
    if str(plan.get("env_fingerprint") or "") != expected_env_fingerprint:
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    req = plan.get("request")
    if not isinstance(req, dict):
        raise ValidationError("Plan missing request dict")
    if str(req.get("request_fingerprint") or "") != expected_request_fingerprint:
        raise SafetyError("Refused: plan request_fingerprint does not match current request")
    return plan

