from __future__ import annotations

from urllib.parse import quote

from . import community_groups as _groups


COMMAND_FAMILY = "loyalty-tiers"
BASE_PATH = "/loyalty-tiers/v1/tiers"
BULK_BASE_PATH = "/loyalty-tiers/v1/bulk/tiers"
PROGRAM_PATH = f"{BASE_PATH}/program"
PROGRAM_SETTINGS_PATH = f"{BASE_PATH}/program-settings"


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _tier_id(raw) -> str:
    return _groups._coerce_text(raw, field="tier-id")


def _revision(raw) -> str:
    return _groups._coerce_text(raw, field="revision")


def _tier_body(raw) -> dict:
    body = _object_body(raw, field="tier-json")
    if not isinstance(body.get("tier"), dict):
        raise _groups.ValidationError("--tier-json must include tier")
    return body


def _tiers_body(raw) -> dict:
    body = _object_body(raw, field="tiers-json")
    tiers = body.get("tiers")
    if not isinstance(tiers, list) or not tiers:
        raise _groups.ValidationError("--tiers-json must include a non-empty tiers array")
    return body


def _program_settings_body(raw) -> dict:
    body = _object_body(raw, field="program-settings-json")
    settings = body.get("programSettings")
    if not isinstance(settings, dict):
        raise _groups.ValidationError("--program-settings-json must include programSettings")
    return body


def _program_settings_update_body(raw) -> dict:
    body = _program_settings_body(raw)
    settings = body["programSettings"]
    for key in ("status", "revision", "rollingWindow"):
        if key not in settings:
            raise _groups.ValidationError(f"--program-settings-json must include programSettings.{key}")
    return body


def cmd_loyalty_tiers_list(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list"
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


def cmd_loyalty_tiers_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        tier_id = _tier_id(args.tier_id)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/{tier_id}",
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_tiers_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _tier_body(args.tier_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"operation": "create-tier", "tier": body.get("tier")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["create-loyalty-tier"],
            verification_notes="Provider response only. Official docs say Create Tier creates a loyalty tier and requires a Plus or Business plan.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_tiers_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        tier_id = _tier_id(args.tier_id)
        body = _tier_body(args.tier_json)
        return _groups._run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{tier_id}",
            body=body,
            selector={"tierId": tier_id, "tier": body.get("tier")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["update-loyalty-tier"],
            verification_notes="Provider response only. Official docs say Update Tier updates tier-specific settings such as name and required points.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_tiers_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        tier_id = _tier_id(args.tier_id)
        revision = _revision(args.revision)
        return _groups._run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{BASE_PATH}/{tier_id}?revision={quote(revision, safe='')}",
            body=None,
            selector={"tierId": tier_id, "revision": revision},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["delete-loyalty-tier"],
            verification_notes="Provider response only. Official docs say Delete Tier deletes a loyalty tier.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_tiers_bulk_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-create"
    try:
        body = _tiers_body(args.tiers_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BULK_BASE_PATH}/create",
            body=body,
            selector={"operation": "bulk-create-tiers", "tiers": body.get("tiers")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["bulk-create-loyalty-tiers"],
            verification_notes="Provider response only. Official docs say Bulk Create Tiers creates up to 20 tiers.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_tiers_get_program(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-program"
    try:
        return _groups._run_write(
            method_name=method,
            http_method="GET",
            path=PROGRAM_PATH,
            body=None,
            selector={"operation": "get-tiers-program"},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["get-tiers-program-default-settings-side-effect"],
            verification_notes="Provider response only. Official docs say Get Tiers Program creates default program settings if none exist.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_tiers_create_program_settings(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create-program-settings"
    try:
        body = _program_settings_body(args.program_settings_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=PROGRAM_SETTINGS_PATH,
            body=body,
            selector={"operation": "create-tiers-program-settings", "programSettings": body.get("programSettings")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["create-loyalty-tiers-program-settings"],
            verification_notes="Provider response only. Official docs say Create Tiers Program Settings creates global settings for all tiers.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_tiers_get_program_settings(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-program-settings"
    try:
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=PROGRAM_SETTINGS_PATH,
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_tiers_update_program_settings(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update-program-settings"
    try:
        body = _program_settings_update_body(args.program_settings_json)
        return _groups._run_write(
            method_name=method,
            http_method="PATCH",
            path=PROGRAM_SETTINGS_PATH,
            body=body,
            selector={"operation": "update-tiers-program-settings", "programSettings": body.get("programSettings")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["update-loyalty-tiers-program-settings"],
            verification_notes="Provider response only. Official docs say Update Tiers Program Settings updates global settings for all loyalty tiers.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
