from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from ..instagram_client import InstagramAPIClient
from .write_utils import run_write_command


def _client(ctx: dict[str, Any]) -> InstagramAPIClient:
    return InstagramAPIClient(
        cfg=ctx["cfg"],
        env_file=ctx["env_file"],
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
    )


def _mentioned_media_fields(media_id: str) -> str:
    return f"mentioned_media.media_id({media_id})"


def _mentioned_comment_fields(comment_id: str) -> str:
    return f"mentioned_comment.comment_id({comment_id})"


def cmd_mentions_media_get(args: Any, ctx: dict[str, Any]) -> int:
    ig_user_id = str(getattr(args, "ig_user_id", "") or "").strip()
    media_id = str(getattr(args, "media_id", "") or "").strip()
    if not ig_user_id:
        raise ValidationError("Missing --ig-user-id")
    if not media_id:
        raise ValidationError("Missing --media-id")

    params = {"fields": _mentioned_media_fields(media_id)}
    client = _client(ctx)
    result = client.get(f"/{ig_user_id}", params=params)
    out = {"ok": True, "command": "mentions.media.get", "result": result}
    ctx["audit"].write("mentions.media.get", out)
    ctx["out"].emit(out)
    return 0


def cmd_mentions_comment_get(args: Any, ctx: dict[str, Any]) -> int:
    ig_user_id = str(getattr(args, "ig_user_id", "") or "").strip()
    comment_id = str(getattr(args, "comment_id", "") or "").strip()
    if not ig_user_id:
        raise ValidationError("Missing --ig-user-id")
    if not comment_id:
        raise ValidationError("Missing --comment-id")

    params = {"fields": _mentioned_comment_fields(comment_id)}
    client = _client(ctx)
    result = client.get(f"/{ig_user_id}", params=params)
    out = {"ok": True, "command": "mentions.comment.get", "result": result}
    ctx["audit"].write("mentions.comment.get", out)
    ctx["out"].emit(out)
    return 0


def cmd_mentions_reply_media(args: Any, ctx: dict[str, Any]) -> int:
    ig_user_id = str(getattr(args, "ig_user_id", "") or "").strip()
    media_id = str(getattr(args, "media_id", "") or "").strip()
    message = str(getattr(args, "message", "") or "").strip()
    if not ig_user_id:
        raise ValidationError("Missing --ig-user-id")
    if not media_id:
        raise ValidationError("Missing --media-id")
    if not message:
        raise ValidationError("Missing --message")

    client = _client(ctx)

    def execute() -> Any:
        return client.post(f"/{ig_user_id}/mentions", data={"media_id": media_id, "message": message})

    out = run_write_command(
        ctx=ctx,
        command="mentions.reply-media",
        selector={"kind": "mentions.reply_media", "ig_user_id": ig_user_id, "media_id": media_id},
        proposed_changes=[
            {"action": "reply_media_mention", "ig_user_id": ig_user_id, "media_id": media_id},
        ],
        execute=execute,
    )
    out["command"] = "mentions.reply_media"
    ctx["audit"].write("mentions.reply_media", out)
    ctx["out"].emit(out)
    return 0


def cmd_mentions_reply_comment(args: Any, ctx: dict[str, Any]) -> int:
    ig_user_id = str(getattr(args, "ig_user_id", "") or "").strip()
    media_id = str(getattr(args, "media_id", "") or "").strip()
    comment_id = str(getattr(args, "comment_id", "") or "").strip()
    message = str(getattr(args, "message", "") or "").strip()
    if not ig_user_id:
        raise ValidationError("Missing --ig-user-id")
    if not media_id:
        raise ValidationError("Missing --media-id")
    if not comment_id:
        raise ValidationError("Missing --comment-id")
    if not message:
        raise ValidationError("Missing --message")

    client = _client(ctx)

    def execute() -> Any:
        return client.post(
            f"/{ig_user_id}/mentions",
            data={"media_id": media_id, "comment_id": comment_id, "message": message},
        )

    out = run_write_command(
        ctx=ctx,
        command="mentions.reply-comment",
        selector={
            "kind": "mentions.reply_comment",
            "ig_user_id": ig_user_id,
            "media_id": media_id,
            "comment_id": comment_id,
        },
        proposed_changes=[
            {"action": "reply_comment_mention", "ig_user_id": ig_user_id, "media_id": media_id, "comment_id": comment_id},
        ],
        execute=execute,
    )
    out["command"] = "mentions.reply_comment"
    ctx["audit"].write("mentions.reply_comment", out)
    ctx["out"].emit(out)
    return 0
