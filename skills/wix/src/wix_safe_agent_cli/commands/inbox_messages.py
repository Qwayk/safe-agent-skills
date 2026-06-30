from __future__ import annotations

from . import community_groups as _groups


COMMAND_FAMILY = "inbox-messages"
BASE_PATH = "/inbox/v2/messages"


def _request_body(raw, *, allow_empty: bool = True) -> dict:
    return _groups._read_object(raw, field="request-json", allow_empty=allow_empty)


def _params(raw) -> dict:
    return _groups._read_object(raw, field="params-json", allow_empty=True)


def cmd_inbox_messages_list(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list"
    try:
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=BASE_PATH,
            params=_params(args.params_json),
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_inbox_messages_send(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.send"
    try:
        body = _request_body(args.request_json, allow_empty=False)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"operation": "send-inbox-message", "conversationId": body.get("conversationId")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["send-inbox-message"],
            verification_notes="Provider response only. Official docs say Send Message sends a message to the business or participant and may send notifications.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
