from __future__ import annotations

from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient


COMMAND_FAMILY = "bookings-policy-snapshots"
BASE_PATH = "/_api/booking-policy-snapshots/v1/policy-snapshots"


def _parse_booking_ids(raw: Any) -> list[str]:
    if raw is None:
        raise ValidationError("Missing --booking-ids")
    if not isinstance(raw, str):
        raise ValidationError("--booking-ids must be a comma-separated string")
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if not values:
        raise ValidationError("--booking-ids cannot be empty")
    return values


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


def cmd_bookings_policy_snapshots_list(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list"
    try:
        booking_ids = _parse_booking_ids(getattr(args, "booking_ids", None))
        params = {"bookingIds": booking_ids}
        auth = _resolve_auth(ctx)
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=BASE_PATH,
            headers=auth["headers"],
            params=params,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method=method,
            auth_mode=auth["mode"],
            request={"method": "GET", "path": BASE_PATH, "params": params},
            response=payload,
            ctx=ctx,
        )
        return 0
    except (ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)
