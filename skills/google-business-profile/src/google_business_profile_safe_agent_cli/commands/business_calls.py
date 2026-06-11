from __future__ import annotations

from typing import Any

from ..api_client import BUSINESS_CALLS_HOST
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
            "operation": "business-calls.locations.get-business-calls-settings",
            "request": verify_request,
            "response": verify_response,
            "note": "Write verification could not confirm change; get-business-calls-settings returned no name.",
        }, False

    if response_name != name:
        return {
            "ok": False,
            "operation": "business-calls.locations.get-business-calls-settings",
            "request": verify_request,
            "response": verify_response,
            "note": (
                f"Write verification returned a different business calls settings name. Expected {name}, got {response_name}."
            ),
        }, False

    return {
        "ok": True,
        "operation": "business-calls.locations.get-business-calls-settings",
        "request": verify_request,
        "response": verify_response,
        "note": "Write verification read-back succeeded with matching business calls settings name.",
    }, True


def cmd_locations_get_business_calls_settings(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")
    client = _client_for_ctx(ctx)
    response, request = client.get_business_calls_settings(name=name)
    return _emit(ctx, "business-calls.locations.get-business-calls-settings", request, response)


def cmd_locations_update_business_calls_settings(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")
    update_mask = _normalize_mask(_require_resource(args.update_mask, arg_name="--update-mask"))
    if not update_mask:
        raise ValidationError("--update-mask must contain at least one field.")

    settings_file = _require_resource(args.business_calls_settings_file, arg_name="--business-calls-settings-file")
    settings_body = _validate_json_object(settings_file, label="BusinessCallsSettings")
    if not settings_body:
        raise ValidationError("BusinessCallsSettings file must not be empty.")

    operation = "business-calls.locations.update-business-calls-settings"
    client = _client_for_ctx(ctx)
    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=BUSINESS_CALLS_HOST,
        body=settings_body,
        mask=update_mask,
        risk_level="medium",
        risk_reasons=["Business calls settings update"],
        preconditions=["OAuth access"],
        verification_plan=[
            "Read back the settings with get-business-calls-settings and verify the returned resource name."
        ],
    )

    if bool(ctx.get("apply")):
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for business-calls update-business-calls-settings.")

        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=name,
            body=settings_body,
            mask=update_mask,
        )

        _, _ = client.update_business_calls_settings(
            name=name,
            update_mask=update_mask,
            body=settings_body,
        )
        verify_response, verify_request = client.get_business_calls_settings(
            name=name,
        )
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
            env_fingerprint=BUSINESS_CALLS_HOST,
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


def cmd_locations_business_calls_insights_list(args: Any, ctx: dict[str, Any]) -> int:
    parent = _require_resource(args.parent, arg_name="--parent")
    client = _client_for_ctx(ctx)
    response, request = client.list_business_calls_insights(
        parent=parent,
        page_size=args.page_size,
        page_token=args.page_token,
        filter=args.filter,
    )
    return _emit(ctx, "business-calls.locations.business-calls-insights.list", request, response)
