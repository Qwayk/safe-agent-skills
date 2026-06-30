from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient


COMMAND_FAMILY = "restaurants-reservation-time-slots"
BASE_PATH = "/table-reservations/reservations/v1"


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_json_arg(raw: Any, *, field: str, allow_empty: bool = False) -> dict[str, Any]:
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
    if not allow_empty and not payload:
        raise ValidationError(f"--{field} cannot be empty")
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
    json_body: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    request_headers = dict(headers)
    request_headers["Content-Type"] = "application/json"
    client = HttpClient(timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")), user_agent="wix-safe-agent-cli")
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


def _run_post_read(*, method_name: str, path: str, body: dict[str, Any], ctx: dict[str, Any]) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method="POST", path=path, headers=auth["headers"], json_body=body, ctx=ctx)
    request = {"method": "POST", "path": path, "body": body}
    out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": request, "response": response}
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def cmd_restaurants_reservation_time_slots_check(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.check"
    try:
        body = _read_json_arg(getattr(args, "time_slot_json", None), field="time-slot-json")
        return _run_post_read(method_name=method, path=f"{BASE_PATH}/check-time-slot", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_reservation_time_slots_get_scheduled(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-scheduled"
    try:
        body = _read_json_arg(getattr(args, "time_slots_json", None), field="time-slots-json")
        return _run_post_read(method_name=method, path=f"{BASE_PATH}/scheduled-time-slots", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_restaurants_reservation_time_slots_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        body = _read_json_arg(getattr(args, "time_slots_json", None), field="time-slots-json")
        return _run_post_read(method_name=method, path=f"{BASE_PATH}/time-slots", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
