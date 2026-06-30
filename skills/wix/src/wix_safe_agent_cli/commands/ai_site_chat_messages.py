from __future__ import annotations

from . import community_groups as _groups


COMMAND_FAMILY = "ai-site-chat-messages"
BASE_PATH = "/wix-assistant-widget/v1/messages"


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _params(raw, *, field: str) -> dict | None:
    body = _object_body(raw, field=field, allow_empty=True)
    return body or None


def cmd_ai_site_chat_messages_list(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list"
    try:
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/list",
            params=_params(args.params_json, field="params-json"),
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_ai_site_chat_messages_bulk_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-create"
    try:
        body = _object_body(args.messages_json, field="messages-json")
        messages = body.get("messages")
        if not isinstance(messages, list) or not messages:
            raise _groups.ValidationError("--messages-json must include non-empty messages")
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path="/wix-assistant-widget/v1/bulk/messages/create",
            body=body,
            selector={"messageCount": len(messages)},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-ai-site-chat-bulk-create-messages", "sends-chat-messages"],
            verification_notes="Inspect provider response, then use ai-site-chat-messages list to verify messages for the same visitor/member identity.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_ai_site_chat_messages_bulk_get_by_inbox(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-get-by-inbox"
    try:
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/get-by-inbox",
            params=_params(args.params_json, field="params-json"),
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_ai_site_chat_messages_media_upload_url(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.media-upload-url"
    try:
        _ = args
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/files/generate-upload-url",
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
