from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient


COMMAND_FAMILY = "referral-tracker"
BASE_PATH = "/_api/referral-tracker/v1"


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    value = str(raw).strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_json_arg(raw: Any, *, field: str) -> dict[str, Any]:
    value = _coerce_text(raw, field=field)
    if value.startswith("@"):
        path = Path(value[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        value = path.read_text(encoding="utf-8").strip()
    try:
        payload = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _query_body(raw: Any) -> dict[str, Any]:
    payload = _read_json_arg(raw, field="query-json")
    query = payload.get("query")
    if not isinstance(query, dict):
        raise ValidationError("--query-json.query must be a JSON object")
    return payload


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
    )


def _request_json(
    *,
    method: str,
    path: str,
    headers: dict[str, str],
    json_body: dict[str, Any] | None,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
        request_headers["Content-Type"] = "application/json"
    client = HttpClient(
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
        user_agent="wix-safe-agent-cli",
    )
    response = client.request(
        method=method,
        url=ctx["cfg"].base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=None,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _emit_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _read(*, method_name: str, http_method: str, path: str, body: dict[str, Any] | None, ctx: dict[str, Any]) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], json_body=body, ctx=ctx)
    out = {
        "ok": True,
        "method": method_name,
        "auth_mode": auth["mode"],
        "request": {"method": http_method, "path": path, **({"body": body} if body is not None else {})},
        "response": response,
    }
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def cmd_referral_tracker_get(args, ctx) -> int:
    method = "referralTracker.getReferralEvent"
    try:
        referral_event_id = _coerce_text(getattr(args, "referral_event_id", None), field="referral-event-id")
        return _read(method_name=method, http_method="GET", path=f"{BASE_PATH}/referral-events/{referral_event_id}", body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_referral_tracker_query(args, ctx) -> int:
    method = "referralTracker.queryReferralEvent"
    try:
        body = _query_body(getattr(args, "query_json", None))
        return _read(method_name=method, http_method="POST", path=f"{BASE_PATH}/referral-events/query", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_referral_tracker_get_statistics(args, ctx) -> int:
    _ = args
    method = "referralTracker.getReferralStatistics"
    try:
        return _read(method_name=method, http_method="GET", path=f"{BASE_PATH}/referral-statistics", body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
