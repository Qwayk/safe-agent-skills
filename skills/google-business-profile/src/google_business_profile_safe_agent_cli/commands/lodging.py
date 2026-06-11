from __future__ import annotations

from typing import Any

from ..api_client import LODGING_HOST
from ..errors import SafetyError, ValidationError
from .business_info import (
    _build_plan,
    _build_receipt,
    _client_for_ctx,
    _emit,
    _emit_write_output,
    _normalize_mask,
    _optional_text,
    _require_matching_plan_in,
    _require_resource,
    _validate_json_object,
    _write_plan_if_needed,
    _write_receipt_if_needed,
)


def _build_verification(
    *,
    name: str,
    verify_response: dict[str, Any],
    verify_request: dict[str, Any],
) -> tuple[dict[str, Any], bool]:
    response_name = str(verify_response.get("name") or "").strip()
    if not response_name:
        return {
            "ok": False,
            "operation": "lodging.locations.get-lodging",
            "request": verify_request,
            "response": verify_response,
            "note": "Write verification could not confirm change; get-lodging returned no name.",
        }, False

    if response_name != name:
        return {
            "ok": False,
            "operation": "lodging.locations.get-lodging",
            "request": verify_request,
            "response": verify_response,
            "note": (
                f"Write verification returned a different lodging name. Expected {name}, got {response_name}."
            ),
        }, False

    return {
        "ok": True,
        "operation": "lodging.locations.get-lodging",
        "request": verify_request,
        "response": verify_response,
        "note": "Write verification read-back succeeded with matching lodging name.",
    }, True


def cmd_locations_get_lodging(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")
    read_mask = _require_resource(args.read_mask, arg_name="--read-mask")
    client = _client_for_ctx(ctx)
    response, request = client.get_lodging(name=name, read_mask=read_mask)
    return _emit(ctx, "lodging.locations.get-lodging", request, response)


def cmd_locations_update_lodging(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")
    update_mask = _normalize_mask(_require_resource(args.update_mask, arg_name="--update-mask"))
    if not update_mask:
        raise ValidationError("--update-mask must contain at least one field.")

    lodging_file = _require_resource(args.lodging_file, arg_name="--lodging-file")
    lodging_body = _validate_json_object(lodging_file, label="Lodging")
    if not lodging_body:
        raise ValidationError("Lodging file must not be empty.")

    operation = "lodging.locations.update-lodging"
    client = _client_for_ctx(ctx)
    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=LODGING_HOST,
        body=lodging_body,
        mask=update_mask,
        risk_level="medium",
        risk_reasons=["Lodging metadata update"],
        preconditions=["OAuth access"],
        verification_plan=[
            "Read back the lodging resource with get-lodging and readMask from the update mask."
        ],
    )

    if bool(ctx.get("apply")):
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for lodging update-lodging.")
        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=name,
            body=lodging_body,
            mask=update_mask,
        )

        _, request = client.update_lodging(
            name=name,
            update_mask=update_mask,
            body=lodging_body,
        )
        verify_response, verify_request = client.get_lodging(name=name, read_mask=update_mask)
        verification, changed = _build_verification(
            name=name,
            verify_response=verify_response,
            verify_request=verify_request,
        )
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=LODGING_HOST,
            changed=changed,
            verification=verification,
            diff_applied=[field.strip() for field in update_mask.split(",") if field.strip()],
        )
        receipt_path = _write_receipt_if_needed(ctx.get("receipt_out"), receipt)
        return _emit_write_output(
            ctx,
            operation=operation,
            dry_run=False,
            payload_obj=receipt,
            artifact_path=receipt_path,
        )

    plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
    return _emit_write_output(
        ctx,
        operation=operation,
        dry_run=True,
        payload_obj=plan,
        artifact_path=plan_path,
    )


def cmd_locations_lodging_get_google_updated(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")
    read_mask = _require_resource(args.read_mask, arg_name="--read-mask")
    client = _client_for_ctx(ctx)
    response, request = client.get_lodging_google_updated(name=name, read_mask=read_mask)
    return _emit(ctx, "lodging.locations.lodging.get-google-updated", request, response)
