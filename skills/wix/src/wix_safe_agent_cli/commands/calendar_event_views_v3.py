from __future__ import annotations

from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient


COMMAND_FAMILY = "calendar-event-views-v3"
BASE_PATH = "/calendar/v3/events/view"


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
    )


def _request_json(*, headers: dict[str, str], ctx: dict[str, Any]) -> dict[str, Any]:
    client = HttpClient(timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")), user_agent="wix-safe-agent-cli")
    response = client.request(
        method="GET",
        url=ctx["cfg"].base_url.rstrip("/") + "/" + BASE_PATH.lstrip("/"),
        headers=headers,
        params=None,
        json_body=None,
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


def cmd_calendar_event_views_v3_get(args, ctx) -> int:
    _ = args
    method = f"{COMMAND_FAMILY}.get"
    try:
        auth = _resolve_auth(ctx)
        payload = _request_json(headers=auth["headers"], ctx=ctx)
        out = {
            "ok": True,
            "method": method,
            "auth_mode": auth["mode"],
            "request": {"method": "GET", "path": BASE_PATH},
            "response": payload,
        }
        ctx["audit"].write(method, out)
        ctx["out"].emit(out)
        return 0
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
