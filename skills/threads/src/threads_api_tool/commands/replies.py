from __future__ import annotations

from typing import Any

from ..commands.common import build_read_params, parse_bool_arg, run_write_command
from ..errors import ValidationError
from ..threads_client import ThreadsAPIClient


def _client(ctx: dict[str, Any]) -> ThreadsAPIClient:
    return ThreadsAPIClient(
        cfg=ctx["cfg"],
        env_file=ctx["env_file"],
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
    )


def _resolve_threads_user_id(args: object, ctx: dict[str, Any]) -> str:
    provided = str(getattr(args, "threads_user_id", "") or "").strip()
    if provided:
        return provided
    fallback = str(getattr(ctx["cfg"], "default_user_id", "") or "").strip()
    if fallback:
        return fallback
    raise ValidationError("Missing --threads-user-id and THREADS_DEFAULT_USER_ID is not set")


def _resolve_threads_media_id(args: object, *, field: str = "threads_media_id") -> str:
    value = str(getattr(args, field, "") or "").strip()
    if not value:
        raise ValidationError(f"Missing --{field.replace('_', '-')}" )
    return value


def cmd_replies_list(args, ctx: dict[str, Any]) -> int:
    media_id = _resolve_threads_media_id(args)
    params = build_read_params(args=args)
    result = _client(ctx).list_replies(threads_media_id=media_id, params=params)
    out = {"ok": True, "command": "replies.list", "result": result}
    ctx["audit"].write("replies.list", out)
    ctx["out"].emit(out)
    return 0


def cmd_replies_conversation(args, ctx: dict[str, Any]) -> int:
    media_id = _resolve_threads_media_id(args)
    params = build_read_params(args=args, include_reverse=False)
    result = _client(ctx).reply_conversation(threads_media_id=media_id, params=params)
    out = {"ok": True, "command": "replies.conversation", "result": result}
    ctx["audit"].write("replies.conversation", out)
    ctx["out"].emit(out)
    return 0


def cmd_replies_hide(args, ctx: dict[str, Any]) -> int:
    reply_id = _resolve_threads_media_id(args, field="threads_reply_id")
    hide = parse_bool_arg(getattr(args, "hide", None), name="hide")
    client = _client(ctx)

    selector = {"kind": "replies.hide", "threads_reply_id": reply_id}

    def execute() -> dict[str, Any]:
        return client.manage_reply(threads_reply_id=reply_id, hide=hide)

    out = run_write_command(
        ctx=ctx,
        command="replies.hide",
        selector=selector,
        proposed_changes=[
            {"action": "manage_reply", "threads_reply_id": reply_id, "hide": hide},
        ],
        execute=execute,
    )
    out["command"] = "replies.hide"
    ctx["audit"].write("replies.hide", out)
    ctx["out"].emit(out)
    return 0


def cmd_replies_pending_list(args, ctx: dict[str, Any]) -> int:
    media_id = _resolve_threads_media_id(args)
    params = build_read_params(args=args)
    result = _client(ctx).list_pending_replies(threads_media_id=media_id, params=params)
    out = {"ok": True, "command": "replies.pending_list", "result": result}
    ctx["audit"].write("replies.pending_list", out)
    ctx["out"].emit(out)
    return 0


def cmd_replies_pending_decide(args, ctx: dict[str, Any]) -> int:
    reply_id = _resolve_threads_media_id(args, field="threads_reply_id")
    approve = parse_bool_arg(getattr(args, "approve", None), name="approve")

    client = _client(ctx)

    selector = {"kind": "replies.pending_decide", "threads_reply_id": reply_id, "approve": approve}

    def execute() -> dict[str, Any]:
        return client.manage_pending_reply(threads_reply_id=reply_id, approve=approve)

    out = run_write_command(
        ctx=ctx,
        command="replies.pending-decide",
        selector=selector,
        proposed_changes=[{"action": "manage_pending_reply", "threads_reply_id": reply_id, "approve": approve}],
        execute=execute,
    )
    out["command"] = "replies.pending-decide"
    ctx["audit"].write("replies.pending_decide", out)
    ctx["out"].emit(out)
    return 0
