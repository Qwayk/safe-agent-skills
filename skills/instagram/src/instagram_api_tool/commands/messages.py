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


def cmd_messages_send(args: Any, ctx: dict[str, Any]) -> int:
    ig_user_id = str(getattr(args, "ig_user_id", "") or "").strip()
    recipient_id = str(getattr(args, "recipient_id", "") or "").strip()
    message = str(getattr(args, "message", "") or "").strip()
    if not ig_user_id:
        raise ValidationError("Missing --ig-user-id")
    if not recipient_id:
        raise ValidationError("Missing --recipient-id")
    if not message:
        raise ValidationError("Missing --message")

    client = _client(ctx)

    def execute() -> Any:
        return client.post(f"/{ig_user_id}/messages", data={"recipient_id": recipient_id, "message": message})

    out = run_write_command(
        ctx=ctx,
        command="messages.send",
        selector={"kind": "messages.send", "ig_user_id": ig_user_id, "recipient_id": recipient_id},
        proposed_changes=[{"action": "send_message", "recipient_id": recipient_id}],
        requires_yes=True,
        execute=execute,
    )
    out["command"] = "messages.send"
    ctx["audit"].write("messages.send", out)
    ctx["out"].emit(out)
    return 0


def cmd_messages_private_reply(args: Any, ctx: dict[str, Any]) -> int:
    ig_user_id = str(getattr(args, "ig_user_id", "") or "").strip()
    recipient_id = str(getattr(args, "recipient_id", "") or "").strip()
    message = str(getattr(args, "message", "") or "").strip()
    if not ig_user_id:
        raise ValidationError("Missing --ig-user-id")
    if not recipient_id:
        raise ValidationError("Missing --recipient-id")
    if not message:
        raise ValidationError("Missing --message")

    client = _client(ctx)

    def execute() -> Any:
        # Instagram private replies are sent via the same edge family in IG Login examples.
        return client.post(f"/{ig_user_id}/messages", data={"recipient_id": recipient_id, "message": message})

    out = run_write_command(
        ctx=ctx,
        command="messages.private-reply",
        selector={"kind": "messages.private_reply", "ig_user_id": ig_user_id, "recipient_id": recipient_id},
        proposed_changes=[{"action": "private_reply", "recipient_id": recipient_id}],
        requires_yes=True,
        execute=execute,
    )
    out["command"] = "messages.private_reply"
    ctx["audit"].write("messages.private_reply", out)
    ctx["out"].emit(out)
    return 0
