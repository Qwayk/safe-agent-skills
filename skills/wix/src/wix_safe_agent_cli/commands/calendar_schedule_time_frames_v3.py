from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient


COMMAND_FAMILY = "calendar-schedule-time-frames-v3"
BASE_PATH = "/calendar/v3/schedules/timeframe"


def _read_json_arg(raw: Any, *, field: str) -> Any:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a JSON string or @file path")
    text = raw.strip()
    if not text:
        raise ValidationError(f"--{field} cannot be empty")
    if text.startswith("@"):
        path = Path(text[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        text = path.read_text(encoding="utf-8").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc


def _coerce_non_empty_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_optional_text(raw: Any, *, field: str) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    return value or None


def _coerce_ids(raw: Any) -> list[str]:
    payload = _read_json_arg(raw, field="ids-json")
    if not isinstance(payload, list):
        raise ValidationError("--ids-json must be a JSON array of schedule IDs")
    ids: list[str] = []
    for value in payload:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("--ids-json must contain only non-empty schedule ID strings")
        ids.append(value.strip())
    if not ids:
        raise ValidationError("--ids-json must contain at least one schedule ID")
    if len(ids) > 100:
        raise ValidationError("--ids-json cannot contain more than 100 schedule IDs")
    return ids


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
    base_url: str,
    path: str,
    headers: dict[str, str],
    params: dict[str, Any] | None,
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=headers,
        params=params,
        json_body=None,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _emit_success(*, method: str, auth_mode: str, request: dict[str, Any], response: dict[str, Any], ctx: dict[str, Any]) -> None:
    out = {"ok": True, "method": method, "auth_mode": auth_mode, "request": request, "response": response}
    ctx["audit"].write(method, out)
    ctx["out"].emit(out)


def _write_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _run_get(*, method_name: str, path: str, params: dict[str, Any] | None, ctx: dict[str, Any]) -> int:
    auth = _resolve_auth(ctx)
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=path,
        headers=auth["headers"],
        params=params,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    request: dict[str, Any] = {"method": "GET", "path": path}
    if params:
        request["params"] = params
    _emit_success(method=method_name, auth_mode=auth["mode"], request=request, response=payload, ctx=ctx)
    return 0


def cmd_calendar_schedule_time_frames_v3_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        schedule_id = _coerce_non_empty_text(getattr(args, "schedule_id", None), field="schedule-id")
        params: dict[str, Any] = {}
        time_zone = _coerce_optional_text(getattr(args, "time_zone", None), field="time-zone")
        if time_zone:
            params["timeZone"] = time_zone
        return _run_get(method_name=method, path=f"{BASE_PATH}/{schedule_id}", params=params or None, ctx=ctx)
    except (ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_calendar_schedule_time_frames_v3_list(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list"
    try:
        params: dict[str, Any] = {"ids": _coerce_ids(getattr(args, "ids_json", None))}
        time_zone = _coerce_optional_text(getattr(args, "time_zone", None), field="time-zone")
        if time_zone:
            params["timeZone"] = time_zone
        return _run_get(method_name=method, path=BASE_PATH, params=params, ctx=ctx)
    except (ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)
