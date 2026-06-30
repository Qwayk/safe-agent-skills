from __future__ import annotations

from . import community_groups as _groups


COMMAND_FAMILY = "ai-site-chat-widget-settings-v2"
BASE_PATH = "/wix-assistant-widget/v2/settings"


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def cmd_ai_site_chat_widget_settings_v2_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        _ = args
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


def cmd_ai_site_chat_widget_settings_v2_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        body = _object_body(args.settings_json, field="settings-json")
        return _groups._run_write(
            method_name=method,
            http_method="PATCH",
            path=BASE_PATH,
            body=body,
            selector={"fieldMask": body.get("fieldMask"), "settings": body.get("settings", body)},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-ai-site-chat-widget-settings-update", "field-mask-update", "developer-preview"],
            verification_notes="Inspect provider response, then use ai-site-chat-widget-settings-v2 get to verify the settings.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
