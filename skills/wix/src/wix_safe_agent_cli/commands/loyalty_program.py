from __future__ import annotations

from . import community_groups as _groups


COMMAND_FAMILY = "loyalty-program"
BASE_PATH = "/loyalty-programs/v1/program"


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _program_body(raw) -> dict:
    body = _object_body(raw, field="program-json")
    if not isinstance(body.get("loyaltyProgram"), dict):
        raise _groups.ValidationError("--program-json must include loyaltyProgram")
    return body


def _run_status_write(args, ctx, *, command: str, path_suffix: str, risk: str, note: str) -> int:
    method = f"{COMMAND_FAMILY}.{command}"
    try:
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{path_suffix}",
            body={},
            selector={"operation": command},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=[risk],
            verification_notes=note,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_program_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=BASE_PATH,
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_program_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        body = _program_body(args.program_json)
        return _groups._run_write(
            method_name=method,
            http_method="PATCH",
            path=BASE_PATH,
            body=body,
            selector={"operation": "update-loyalty-program", "loyaltyProgram": body.get("loyaltyProgram", body)},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["update-loyalty-program"],
            verification_notes="Provider response only. Official docs say Update Loyalty Program updates the program settings.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_program_activate(args, ctx) -> int:
    return _run_status_write(
        args,
        ctx,
        command="activate",
        path_suffix="activate",
        risk="activate-loyalty-program",
        note="Provider response only. Official docs say Activate Loyalty Program activates the loyalty program.",
    )


def cmd_loyalty_program_pause(args, ctx) -> int:
    return _run_status_write(
        args,
        ctx,
        command="pause",
        path_suffix="pause",
        risk="pause-loyalty-program",
        note="Provider response only. Official docs say Pause Loyalty Program pauses the loyalty program.",
    )


def cmd_loyalty_program_premium_features(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.premium-features"
    try:
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/premium-features",
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_program_enable_points_expiration(args, ctx) -> int:
    return _run_status_write(
        args,
        ctx,
        command="enable-points-expiration",
        path_suffix="points-expiration/enable",
        risk="enable-loyalty-points-expiration",
        note="Provider response only. Official docs say Enable Points Expiration enables points expiration for the loyalty program.",
    )


def cmd_loyalty_program_disable_points_expiration(args, ctx) -> int:
    return _run_status_write(
        args,
        ctx,
        command="disable-points-expiration",
        path_suffix="points-expiration/disable",
        risk="disable-loyalty-points-expiration",
        note="Provider response only. Official docs say Disable Points Expiration disables points expiration for the loyalty program.",
    )
