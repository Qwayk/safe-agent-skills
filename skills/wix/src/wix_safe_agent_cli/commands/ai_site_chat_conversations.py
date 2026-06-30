from __future__ import annotations

from . import community_groups as _groups


COMMAND_FAMILY = "ai-site-chat-conversations"
BASE_PATH = "/wix-assistant-widget/v1/conversation"


def cmd_ai_site_chat_conversations_get(args, ctx) -> int:
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
