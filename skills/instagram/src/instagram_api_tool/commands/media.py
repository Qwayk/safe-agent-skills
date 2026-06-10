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


def cmd_media_list(args: Any, ctx: dict[str, Any]) -> int:
    ig_user_id = str(getattr(args, "ig_user_id", "") or "").strip()
    if not ig_user_id:
        raise ValidationError("Missing --ig-user-id")
    fields = split_csv_arg(getattr(args, "fields", None))
    params: dict[str, Any] = {}
    if fields:
        params["fields"] = ",".join(fields)
    if getattr(args, "limit", None):
        params["limit"] = int(args.limit)
    if getattr(args, "after", None):
        params["after"] = str(args.after)
    if getattr(args, "before", None):
        params["before"] = str(args.before)

    client = _client(ctx)
    result = client.get(f"/{ig_user_id}/media", params=params)
    out = {"ok": True, "command": "media.list", "result": result}
    ctx["audit"].write("media.list", out)
    ctx["out"].emit(out)
    return 0


def cmd_media_container_get(args: Any, ctx: dict[str, Any]) -> int:
    container_id = str(getattr(args, "container_id", "") or "").strip()
    if not container_id:
        raise ValidationError("Missing --container-id")
    fields = split_csv_arg(getattr(args, "fields", None))
    params = {"fields": ",".join(fields)} if fields else {}

    client = _client(ctx)
    result = client.get(f"/{container_id}", params=params)
    out = {"ok": True, "command": "media.container.get", "result": result}
    ctx["audit"].write("media.container.get", out)
    ctx["out"].emit(out)
    return 0


def cmd_media_publish_limit(args: Any, ctx: dict[str, Any]) -> int:
    ig_user_id = str(getattr(args, "ig_user_id", "") or "").strip()
    if not ig_user_id:
        raise ValidationError("Missing --ig-user-id")
    fields = split_csv_arg(getattr(args, "fields", None))
    params = {"fields": ",".join(fields)} if fields else None

    client = _client(ctx)
    result = client.get(f"/{ig_user_id}/content_publishing_limit", params=params)
    out = {"ok": True, "command": "media.publish_limit", "result": result}
    ctx["audit"].write("media.publish_limit", out)
    ctx["out"].emit(out)
    return 0


def cmd_media_get(args: Any, ctx: dict[str, Any]) -> int:
    media_id = str(getattr(args, "media_id", "") or "").strip()
    if not media_id:
        raise ValidationError("Missing --media-id")
    fields = split_csv_arg(getattr(args, "fields", None))
    params = {"fields": ",".join(fields)} if fields else None

    client = _client(ctx)
    result = client.get(f"/{media_id}", params=params)
    out = {"ok": True, "command": "media.get", "result": result}
    ctx["audit"].write("media.get", out)
    ctx["out"].emit(out)
    return 0


def cmd_media_children(args: Any, ctx: dict[str, Any]) -> int:
    media_id = str(getattr(args, "media_id", "") or "").strip()
    if not media_id:
        raise ValidationError("Missing --media-id")
    fields = split_csv_arg(getattr(args, "fields", None))
    params = {"fields": ",".join(fields)} if fields else None

    client = _client(ctx)
    result = client.get(f"/{media_id}/children", params=params)
    out = {"ok": True, "command": "media.children", "result": result}
    ctx["audit"].write("media.children", out)
    ctx["out"].emit(out)
    return 0


def cmd_media_create_container(args: Any, ctx: dict[str, Any]) -> int:
    ig_user_id = str(getattr(args, "ig_user_id", "") or "").strip()
    if not ig_user_id:
        raise ValidationError("Missing --ig-user-id")

    payload: dict[str, Any] = {}
    media_type = str(getattr(args, "media_type", "") or "").strip()
    if media_type:
        payload["media_type"] = media_type

    image_url = str(getattr(args, "image_url", "") or "").strip()
    video_url = str(getattr(args, "video_url", "") or "").strip()
    children = split_csv_arg(getattr(args, "children", None))
    if not image_url and not video_url and not children:
        raise ValidationError("Missing payload for media.create-container")

    if image_url:
        payload["image_url"] = image_url
    if video_url:
        payload["video_url"] = video_url
    if children:
        payload["children"] = ",".join(children)
    caption = str(getattr(args, "caption", "") or "").strip()
    if caption:
        payload["caption"] = caption
    fields = split_csv_arg(getattr(args, "fields", None))
    if fields:
        payload["fields"] = ",".join(fields)

    client = _client(ctx)
    payload_key = payload.copy()

    def execute() -> Any:
        return client.post(f"/{ig_user_id}/media", data=payload_key)

    out = run_write_command(
        ctx=ctx,
        command="media.create-container",
        selector={"kind": "media.create_container", "ig_user_id": ig_user_id},
        proposed_changes=[{"action": "create_container", "ig_user_id": ig_user_id, "payload": payload_key}],
        execute=execute,
    )
    out["command"] = "media.create_container"
    ctx["audit"].write("media.create_container", out)
    ctx["out"].emit(out)
    return 0


def cmd_media_publish(args: Any, ctx: dict[str, Any]) -> int:
    ig_user_id = str(getattr(args, "ig_user_id", "") or "").strip()
    creation_id = str(getattr(args, "creation_id", "") or "").strip()
    if not ig_user_id:
        raise ValidationError("Missing --ig-user-id")
    if not creation_id:
        raise ValidationError("Missing --creation-id")

    client = _client(ctx)
    payload = {"creation_id": creation_id}
    payload_for_send = payload.copy()

    def execute() -> Any:
        return client.post(f"/{ig_user_id}/media_publish", data=payload_for_send)

    out = run_write_command(
        ctx=ctx,
        command="media.publish",
        selector={"kind": "media.publish", "ig_user_id": ig_user_id, "creation_id": creation_id},
        proposed_changes=[
            {"action": "publish_container", "ig_user_id": ig_user_id, "creation_id": creation_id},
        ],
        requires_yes=True,
        execute=execute,
        risk_level="high",
    )
    out["command"] = "media.publish"
    ctx["audit"].write("media.publish", out)
    ctx["out"].emit(out)
    return 0


def cmd_media_comments_set(args: Any, ctx: dict[str, Any]) -> int:
    media_id = str(getattr(args, "media_id", "") or "").strip()
    if not media_id:
        raise ValidationError("Missing --media-id")
    enabled = parse_bool_arg(getattr(args, "enabled", None), name="enabled")

    client = _client(ctx)
    payload = {"comment_enabled": str(enabled).lower()}

    def execute() -> Any:
        return client.post(f"/{media_id}", data=payload)

    out = run_write_command(
        ctx=ctx,
        command="media.comments.set",
        selector={"kind": "media.comments.set", "media_id": media_id},
        proposed_changes=[{"action": "set_comment_enabled", "media_id": media_id, "enabled": enabled}],
        execute=execute,
    )
    out["command"] = "media.comments.set"
    ctx["audit"].write("media.comments.set", out)
    ctx["out"].emit(out)
    return 0
