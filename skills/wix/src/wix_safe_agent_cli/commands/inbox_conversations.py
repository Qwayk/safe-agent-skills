from __future__ import annotations

from . import community_groups as _groups


COMMAND_FAMILY = "inbox-conversations"
BASE_PATH = "/inbox/v2/conversations"


def _conversation_id(raw) -> str:
    return _groups._coerce_text(raw, field="conversation-id")


def _request_body(raw) -> dict:
    return _groups._read_object(raw, field="request-json", allow_empty=True)


def cmd_inbox_conversations_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        conversation_id = _conversation_id(args.conversation_id)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/{conversation_id}",
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_inbox_conversations_get_or_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-or-create"
    try:
        body = _request_body(args.request_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"operation": "get-or-create-conversation", "participantId": body.get("participantId")},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["get-or-create-inbox-conversation"],
            verification_notes="Provider response only. Official docs say Get Or Create Conversation returns an existing conversation or creates one for the participant.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
