from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from ..instagram_client import InstagramAPIClient
from .write_utils import parse_bool_arg, run_write_command, split_csv_arg


def _client(ctx: dict[str, Any]) -> InstagramAPIClient:
    return InstagramAPIClient(
        cfg=ctx["cfg"],
        env_file=ctx["env_file"],
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
    )


def cmd_comments_list(args: Any, ctx: dict[str, Any]) -> int:
    media_id = str(getattr(args, "media_id", "") or "").strip()
    if not media_id:
        raise ValidationError("Missing --media-id")
    fields = split_csv_arg(getattr(args, "fields", None))
    params = {"fields": ",".join(fields)} if fields else None

    client = _client(ctx)
    result = client.get(f"/{media_id}/comments", params=params)
    out = {"ok": True, "command": "comments.list", "result": result}
    ctx["audit"].write("comments.list", out)
    ctx["out"].emit(out)
    return 0


def cmd_comments_create(args: Any, ctx: dict[str, Any]) -> int:
    media_id = str(getattr(args, "media_id", "") or "").strip()
    message = str(getattr(args, "message", "") or "").strip()
    if not media_id:
        raise ValidationError("Missing --media-id")
    if not message:
        raise ValidationError("Missing --message")
    client = _client(ctx)

    def execute() -> Any:
        return client.post(f"/{media_id}/comments", data={"message": message})

    out = run_write_command(
        ctx=ctx,
        command="comments.create",
        selector={"kind": "comments.create", "media_id": media_id},
        proposed_changes=[{"action": "create_comment", "media_id": media_id}],
        execute=execute,
    )
    out["command"] = "comments.create"
    ctx["audit"].write("comments.create", out)
    ctx["out"].emit(out)
    return 0


def cmd_comments_get(args: Any, ctx: dict[str, Any]) -> int:
    comment_id = str(getattr(args, "comment_id", "") or "").strip()
    if not comment_id:
        raise ValidationError("Missing --comment-id")
    fields = split_csv_arg(getattr(args, "fields", None))
    params = {"fields": ",".join(fields)} if fields else None

    client = _client(ctx)
    result = client.get(f"/{comment_id}", params=params)
    out = {"ok": True, "command": "comments.get", "result": result}
    ctx["audit"].write("comments.get", out)
    ctx["out"].emit(out)
    return 0


def cmd_comments_replies_list(args: Any, ctx: dict[str, Any]) -> int:
    comment_id = str(getattr(args, "comment_id", "") or "").strip()
    if not comment_id:
        raise ValidationError("Missing --comment-id")

    client = _client(ctx)
    result = client.get(f"/{comment_id}/replies")
    out = {"ok": True, "command": "comments.replies.list", "result": result}
    ctx["audit"].write("comments.replies.list", out)
    ctx["out"].emit(out)
    return 0


def cmd_comments_replies_create(args: Any, ctx: dict[str, Any]) -> int:
    comment_id = str(getattr(args, "comment_id", "") or "").strip()
    message = str(getattr(args, "message", "") or "").strip()
    if not comment_id:
        raise ValidationError("Missing --comment-id")
    if not message:
        raise ValidationError("Missing --message")
    client = _client(ctx)

    def execute() -> Any:
        return client.post(f"/{comment_id}/replies", data={"message": message})

    out = run_write_command(
        ctx=ctx,
        command="comments.replies.create",
        selector={"kind": "comments.replies.create", "comment_id": comment_id},
        proposed_changes=[{"action": "reply_comment", "comment_id": comment_id}],
        execute=execute,
    )
    out["command"] = "comments.replies.create"
    ctx["audit"].write("comments.replies.create", out)
    ctx["out"].emit(out)
    return 0


def cmd_comments_hide(args: Any, ctx: dict[str, Any]) -> int:
    comment_id = str(getattr(args, "comment_id", "") or "").strip()
    if not comment_id:
        raise ValidationError("Missing --comment-id")
    hidden = parse_bool_arg(getattr(args, "hidden", None), name="hidden")
    client = _client(ctx)

    def execute() -> Any:
        return client.post(f"/{comment_id}", data={"hide": str(hidden).lower()})

    out = run_write_command(
        ctx=ctx,
        command="comments.hide",
        selector={"kind": "comments.hide", "comment_id": comment_id},
        proposed_changes=[{"action": "hide_comment", "comment_id": comment_id, "hidden": hidden}],
        execute=execute,
    )
    out["command"] = "comments.hide"
    ctx["audit"].write("comments.hide", out)
    ctx["out"].emit(out)
    return 0


def cmd_comments_delete(args: Any, ctx: dict[str, Any]) -> int:
    comment_id = str(getattr(args, "comment_id", "") or "").strip()
    if not comment_id:
        raise ValidationError("Missing --comment-id")
    client = _client(ctx)

    def execute() -> Any:
        return client.delete(f"/{comment_id}")

    out = run_write_command(
        ctx=ctx,
        command="comments.delete",
        selector={"kind": "comments.delete", "comment_id": comment_id},
        proposed_changes=[{"action": "delete_comment", "comment_id": comment_id}],
        requires_yes=True,
        requires_ack=True,
        risk_level="high",
        execute=execute,
    )
    out["command"] = "comments.delete"
    ctx["audit"].write("comments.delete", out)
    ctx["out"].emit(out)
    return 0
