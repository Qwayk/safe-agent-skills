from __future__ import annotations

from typing import Any

from ..commands.common import build_read_params, run_write_command, split_csv_arg
from ..errors import ValidationError
from ..threads_client import ThreadsAPIClient

_REPLY_CONTROL_VALUES = {
    "everyone",
    "accounts_you_follow",
    "mentioned_only",
    "parent_post_author_only",
    "followers_only",
}


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


def _resolve_username(args: object) -> str:
    username = str(getattr(args, "username", "") or "").strip()
    if not username:
        raise ValidationError("Missing --username")
    return username


def _resolve_threads_media_id(args: object, *, field: str) -> str:
    value = str(getattr(args, field, "") or "").strip()
    if not value:
        raise ValidationError(f"Missing --{field.replace('_', '-')}")
    return value


def cmd_posts_list_owned(args, ctx: dict[str, Any]) -> int:
    threads_user_id = _resolve_threads_user_id(args, ctx)
    params = build_read_params(args=args)
    result = _client(ctx).list_owned_posts(threads_user_id=threads_user_id, params=params)
    out = {"ok": True, "command": "posts.list-owned", "result": result}
    ctx["audit"].write("posts.list_owned", out)
    ctx["out"].emit(out)
    return 0


def cmd_posts_list_public(args, ctx: dict[str, Any]) -> int:
    username = _resolve_username(args)
    params = build_read_params(args=args)
    result = _client(ctx).list_public_posts(username=username, params=params)
    out = {"ok": True, "command": "posts.list-public", "result": result}
    ctx["audit"].write("posts.list_public", out)
    ctx["out"].emit(out)
    return 0


def cmd_posts_get(args, ctx: dict[str, Any]) -> int:
    threads_media_id = _resolve_threads_media_id(args, field="threads_media_id")
    params = build_read_params(args=args, include_pagination=False, include_reverse=False)
    result = _client(ctx).get_post(threads_media_id=threads_media_id, params=params)
    out = {"ok": True, "command": "posts.get", "result": result}
    ctx["audit"].write("posts.get", out)
    ctx["out"].emit(out)
    return 0


def cmd_posts_limits(args, ctx: dict[str, Any]) -> int:
    threads_user_id = _resolve_threads_user_id(args, ctx)
    result = _client(ctx).posting_limits(threads_user_id=threads_user_id)
    out = {"ok": True, "command": "posts.limits", "result": result}
    ctx["audit"].write("posts.limits", out)
    ctx["out"].emit(out)
    return 0


def _parse_text_spoiler_ranges(args: object) -> list[dict[str, Any]]:
    raw_ranges = getattr(args, "text_spoiler_ranges", None)
    if not raw_ranges:
        return []
    if not isinstance(raw_ranges, list):
        raise ValidationError("--text-spoiler-range must be repeated as offset:length")
    entities: list[dict[str, Any]] = []
    for raw in raw_ranges:
        value = str(raw or "").strip()
        if not value or ":" not in value:
            raise ValidationError("--text-spoiler-range must use offset:length")
        offset_raw, length_raw = value.split(":", 1)
        try:
            offset = int(offset_raw)
            length = int(length_raw)
        except Exception:
            raise ValidationError("--text-spoiler-range must use integer offset:length") from None
        if offset < 0:
            raise ValidationError("--text-spoiler-range offset must be 0 or greater")
        if length <= 0:
            raise ValidationError("--text-spoiler-range length must be greater than 0")
        entities.append({"entity_type": "SPOILER", "offset": offset, "length": length})
    if len(entities) > 10:
        raise ValidationError("Threads supports at most 10 text spoiler entities per post")
    return entities


def _parse_poll_attachment(args: object) -> dict[str, Any] | None:
    repeated = getattr(args, "poll_options", None)
    options: list[str] = []
    if isinstance(repeated, list):
        options.extend(str(item or "").strip() for item in repeated if str(item or "").strip())
    csv_options = split_csv_arg(str(getattr(args, "poll_options_csv", "") or ""))
    if csv_options:
        options.extend(csv_options)
    if not options:
        return None
    if len(options) < 2 or len(options) > 4:
        raise ValidationError("Polls require 2 to 4 options")
    payload: dict[str, Any] = {}
    for idx, option in enumerate(options):
        if len(option) > 25:
            raise ValidationError("Each poll option must be 25 characters or fewer")
        payload[f"option_{chr(ord('a') + idx)}"] = option
    return payload


def _build_create_payload(
    args: object,
    *,
    media_type: str,
    force_carousel_item: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"media_type": media_type}

    text = str(getattr(args, "text", "") or "").strip()
    if text:
        payload["text"] = text

    image_url = str(getattr(args, "image_url", "") or "").strip()
    if image_url:
        payload["image_url"] = image_url

    video_url = str(getattr(args, "video_url", "") or "").strip()
    if video_url:
        payload["video_url"] = video_url

    topic_tag = str(getattr(args, "topic_tag", "") or "").strip()
    if topic_tag:
        payload["topic_tag"] = topic_tag

    reply_to_id = str(getattr(args, "reply_to_id", "") or "").strip()
    if reply_to_id:
        payload["reply_to_id"] = reply_to_id

    reply_control = str(getattr(args, "reply_control", "") or "").strip()
    if reply_control:
        if reply_control not in _REPLY_CONTROL_VALUES:
            allowed = ", ".join(sorted(_REPLY_CONTROL_VALUES))
            raise ValidationError(f"--reply-control must be one of: {allowed}")
        payload["reply_control"] = reply_control
    if bool(getattr(args, "enable_reply_approvals", False)):
        payload["enable_reply_approvals"] = True

    quote_post_id = str(getattr(args, "quote_post_id", "") or "").strip()
    if quote_post_id:
        payload["quote_post_id"] = quote_post_id

    link_attachment = str(getattr(args, "link_attachment", "") or "").strip()
    if link_attachment:
        payload["link_attachment"] = link_attachment

    gif_id = str(getattr(args, "gif_id", "") or "").strip()
    gif_provider = str(getattr(args, "gif_provider", "") or "").strip()
    if gif_id or gif_provider:
        if not gif_id or not gif_provider:
            raise ValidationError("--gif-id and --gif-provider must be provided together")
        payload["gif_attachment"] = {"gif_id": gif_id, "provider": gif_provider}

    if bool(getattr(args, "spoiler_media", False)):
        payload["is_spoiler_media"] = True

    text_entities = _parse_text_spoiler_ranges(args)
    if text_entities:
        payload["text_entities"] = text_entities

    poll_attachment = _parse_poll_attachment(args)
    if poll_attachment:
        payload["poll_attachment"] = poll_attachment

    location_id = str(getattr(args, "location_id", "") or "").strip()
    if location_id:
        payload["location_id"] = location_id

    if force_carousel_item or bool(getattr(args, "is_carousel_item", False)):
        payload["is_carousel_item"] = True

    children = split_csv_arg(str(getattr(args, "children", "") or ""))
    if children:
        payload["children"] = children

    if media_type == "TEXT":
        if image_url or video_url:
            raise ValidationError("Text posts do not accept --image-url or --video-url")
        if payload.get("is_carousel_item"):
            raise ValidationError("Text posts cannot be carousel items")
        if "children" in payload:
            raise ValidationError("Text posts do not accept --children")
    elif media_type == "IMAGE":
        if not image_url:
            raise ValidationError("Missing --image-url")
        if video_url:
            raise ValidationError("Image posts do not accept --video-url")
        if "children" in payload:
            raise ValidationError("Image posts do not accept --children")
    elif media_type == "VIDEO":
        if not video_url:
            raise ValidationError("Missing --video-url")
        if image_url:
            raise ValidationError("Video posts do not accept --image-url")
        if "children" in payload:
            raise ValidationError("Video posts do not accept --children")
    elif media_type == "CAROUSEL":
        if image_url or video_url:
            raise ValidationError("Carousel posts do not accept --image-url or --video-url")
        if payload.get("is_carousel_item"):
            raise ValidationError("Carousel containers cannot use --is-carousel-item")
        carousel_children = payload.get("children")
        if not isinstance(carousel_children, list) or len(carousel_children) < 2:
            raise ValidationError("Carousel posts require at least 2 --children entries")
        if len(carousel_children) > 20:
            raise ValidationError("Carousel posts support at most 20 children")
    else:
        raise ValidationError(f"Unsupported media type: {media_type}")

    if "text_entities" in payload and "text" not in payload:
        raise ValidationError("Text spoiler ranges require --text")
    if media_type != "TEXT" and ("gif_attachment" in payload or "poll_attachment" in payload or "link_attachment" in payload):
        raise ValidationError("GIF, poll, and link attachments are supported only for text posts")

    return payload


def _run_create(
    cmd: str,
    args,
    ctx: dict[str, Any],
    *,
    media_type: str,
    required_text: bool = False,
    force_carousel_item: bool = False,
) -> int:
    threads_user_id = _resolve_threads_user_id(args, ctx)
    payload = _build_create_payload(args, media_type=media_type, force_carousel_item=force_carousel_item)

    if required_text and "text" not in payload:
        raise ValidationError("Missing required --text")

    client = _client(ctx)

    selector = {"kind": cmd, "threads_user_id": threads_user_id, "threads_media_id": payload.get("threads_media_id", "<auto>")}

    def execute() -> dict[str, Any]:
        return client.create_post(threads_user_id=threads_user_id, payload=payload)

    out = run_write_command(
        ctx=ctx,
        command=cmd,
        selector=selector,
        proposed_changes=[{"action": "create_post", "user": threads_user_id, "payload": payload}],
        execute=execute,
    )
    out["command"] = cmd
    ctx["audit"].write(f"posts.{cmd.replace('-', '_')}.write", out)
    ctx["out"].emit(out)
    return 0


def cmd_posts_create_text(args, ctx: dict[str, Any]) -> int:
    return _run_create("posts.create-text", args, ctx, media_type="TEXT", required_text=True)


def cmd_posts_create_image(args, ctx: dict[str, Any]) -> int:
    return _run_create("posts.create-image", args, ctx, media_type="IMAGE")


def cmd_posts_create_video(args, ctx: dict[str, Any]) -> int:
    return _run_create("posts.create-video", args, ctx, media_type="VIDEO")


def cmd_posts_create_carousel_item(args, ctx: dict[str, Any]) -> int:
    image_url = str(getattr(args, "image_url", "") or "").strip()
    video_url = str(getattr(args, "video_url", "") or "").strip()
    if image_url and video_url:
        raise ValidationError("Carousel items accept either --image-url or --video-url, not both")
    if not image_url and not video_url:
        raise ValidationError("Carousel items require --image-url or --video-url")
    media_type = "IMAGE" if image_url else "VIDEO"
    return _run_create(
        "posts.create-carousel-item",
        args,
        ctx,
        media_type=media_type,
        force_carousel_item=True,
    )


def cmd_posts_create_carousel(args, ctx: dict[str, Any]) -> int:
    return _run_create("posts.create-carousel", args, ctx, media_type="CAROUSEL")


def cmd_posts_publish(args, ctx: dict[str, Any]) -> int:
    creation_id = _resolve_threads_media_id(args, field="threads_container_id")
    client = _client(ctx)

    selector = {"kind": "posts.publish", "threads_container_id": creation_id}

    def execute() -> dict[str, Any]:
        user_id = _resolve_threads_user_id(args, ctx)
        return client.publish_post(threads_user_id=user_id, creation_id=creation_id)

    out = run_write_command(
        ctx=ctx,
        command="posts.publish",
        selector=selector,
        proposed_changes=[{"action": "publish_post", "threads_container_id": creation_id}],
        execute=execute,
    )
    out["command"] = "posts.publish"
    ctx["audit"].write("posts.publish", out)
    ctx["out"].emit(out)
    return 0


def cmd_posts_status(args, ctx: dict[str, Any]) -> int:
    container_id = _resolve_threads_media_id(args, field="threads_container_id")
    params = build_read_params(args=args, include_pagination=False, include_reverse=False)
    result = _client(ctx).post_status(threads_container_id=container_id, fields=params.get("fields"))
    out = {"ok": True, "command": "posts.status", "result": result}
    ctx["audit"].write("posts.status", out)
    ctx["out"].emit(out)
    return 0


def cmd_posts_repost(args, ctx: dict[str, Any]) -> int:
    media_id = _resolve_threads_media_id(args, field="threads_media_id")
    client = _client(ctx)

    selector = {"kind": "posts.repost", "threads_media_id": media_id}

    def execute() -> dict[str, Any]:
        return client.repost_media(threads_media_id=media_id)

    out = run_write_command(
        ctx=ctx,
        command="posts.repost",
        selector=selector,
        proposed_changes=[{"action": "repost", "threads_media_id": media_id}],
        execute=execute,
    )
    out["command"] = "posts.repost"
    ctx["audit"].write("posts.repost", out)
    ctx["out"].emit(out)
    return 0


def cmd_posts_delete(args, ctx: dict[str, Any]) -> int:
    media_id = _resolve_threads_media_id(args, field="threads_media_id")
    client = _client(ctx)

    selector = {"kind": "posts.delete", "threads_media_id": media_id}

    def execute() -> dict[str, Any]:
        return client.delete_media(threads_media_id=media_id)

    out = run_write_command(
        ctx=ctx,
        command="posts.delete",
        selector=selector,
        requires_yes=True,
        requires_ack=True,
        risk_level="high",
        proposed_changes=[{"action": "delete", "threads_media_id": media_id}],
        execute=execute,
    )
    out["command"] = "posts.delete"
    ctx["audit"].write("posts.delete", out)
    ctx["out"].emit(out)
    return 0
