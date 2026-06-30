from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient


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


def _coerce_json_object(raw: Any, *, field: str) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
    json_body: dict[str, Any],
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    request_headers = dict(headers)
    request_headers["Content-Type"] = "application/json"

    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=None,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _emit_success(*, method: str, auth_mode: str, request: dict[str, Any], response: dict[str, Any], ctx: dict[str, Any]) -> None:
    out = {
        "ok": True,
        "method": method,
        "auth_mode": auth_mode,
        "request": request,
        "response": response,
    }
    ctx["audit"].write(method, out)
    ctx["out"].emit(out)


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="bookings-time-slots-v2",
    )


def _cmd_post_json(args, ctx, *, arg_name: str, field: str, command: str, path: str) -> int:
    try:
        body = _coerce_json_object(getattr(args, arg_name, None), field=field)
        auth = _resolve_auth(ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=path,
            headers=auth["headers"],
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method=f"bookings-time-slots-v2.{command}",
            auth_mode=auth["mode"],
            request={"method": "POST", "path": path, "body": body},
            response=payload,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1


def _cmd_get_event(args, ctx) -> int:
    try:
        event_id = str(getattr(args, "event_id", "") or "").strip()
        if not event_id:
            raise ValidationError("Missing --event-id")
        auth = _resolve_auth(ctx)
        request_path = f"/_api/service-availability/v2/time-slots/event/{event_id}"
        client = HttpClient(timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")), user_agent="wix-safe-agent-cli")
        response = client.request(
            method="GET",
            url=ctx["cfg"].base_url.rstrip("/") + "/" + request_path.lstrip("/"),
            headers=auth["headers"],
            params=None,
            json_body=None,
        )
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValidationError("Wix API returned a non-object JSON response")
        _emit_success(
            method="bookings-time-slots-v2.get-event",
            auth_mode=auth["mode"],
            request={"method": "GET", "path": request_path, "event_id": event_id},
            response=payload,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1


def cmd_bookings_time_slots_v2_list_availability(args, ctx) -> int:
    return _cmd_post_json(
        args,
        ctx,
        arg_name="list_availability_json",
        field="list-availability-json",
        command="list-availability",
        path="/_api/service-availability/v2/time-slots",
    )


def cmd_bookings_time_slots_v2_get_availability(args, ctx) -> int:
    return _cmd_post_json(
        args,
        ctx,
        arg_name="get_availability_json",
        field="get-availability-json",
        command="get-availability",
        path="/_api/service-availability/v2/time-slots/get",
    )


def cmd_bookings_time_slots_v2_list_event(args, ctx) -> int:
    return _cmd_post_json(
        args,
        ctx,
        arg_name="list_event_json",
        field="list-event-json",
        command="list-event",
        path="/_api/service-availability/v2/time-slots/event",
    )


def cmd_bookings_time_slots_v2_get_event(args, ctx) -> int:
    return _cmd_get_event(args, ctx)


def cmd_bookings_time_slots_v2_list_multi_service(args, ctx) -> int:
    return _cmd_post_json(
        args,
        ctx,
        arg_name="list_multi_service_json",
        field="list-multi-service-json",
        command="list-multi-service",
        path="/_api/service-availability/v2/multi-service-time-slots",
    )


def cmd_bookings_time_slots_v2_get_multi_service(args, ctx) -> int:
    return _cmd_post_json(
        args,
        ctx,
        arg_name="get_multi_service_json",
        field="get-multi-service-json",
        command="get-multi-service",
        path="/_api/service-availability/v2/multi-service-time-slots/get",
    )
