from __future__ import annotations

from typing import Any

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
from ..api_client import NOTIFICATIONS_HOST
from ..errors import ValidationError


def cmd_accounts_get_notification_setting(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")
    client = _client_for_ctx(ctx)
    response, request = client.get_notification_setting(name=name)
    return _emit(ctx, "notifications.accounts.get-notification-setting", request, response)


def cmd_accounts_update_notification_setting(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")
    update_mask = _normalize_mask(_require_resource(args.update_mask, arg_name="--update-mask"))
    if not update_mask:
        raise ValidationError("--update-mask must contain at least one field.")

    notification_setting_file = _require_resource(
        args.notification_setting_file,
        arg_name="--notification-setting-file",
    )
    notification_setting_body = _validate_json_object(notification_setting_file, label="NotificationSetting")

    operation = "notifications.accounts.update-notification-setting"
    client = _client_for_ctx(ctx)
    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=NOTIFICATIONS_HOST,
        body=notification_setting_body,
        mask=update_mask,
        risk_level="medium",
        risk_reasons=["Notification setting update"],
        preconditions=["OAuth access"],
        verification_plan=["Read the notification setting with get-notification-setting."],
    )

    if bool(ctx.get("apply")):
        plan_in = _optional_text(ctx.get("plan_in"))
        if plan_in:
            _require_matching_plan_in(
                plan_in=plan_in,
                operation=operation,
                selector=name,
                body=notification_setting_body,
                mask=update_mask,
            )

        _, _ = client.update_notification_setting(
            name=name,
            update_mask=update_mask,
            body=notification_setting_body,
        )
        verify_response, verify_request = client.get_notification_setting(name=name)
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
            env_fingerprint=NOTIFICATIONS_HOST,
            changed=True,
            verification={
                "ok": True,
                "operation": "notifications.accounts.get-notification-setting",
                "request": verify_request,
                "response": verify_response,
            },
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
