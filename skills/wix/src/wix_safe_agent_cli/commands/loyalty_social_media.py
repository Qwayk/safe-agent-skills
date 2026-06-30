from __future__ import annotations

from . import community_groups as _groups


COMMAND_FAMILY = "loyalty-social-media"
BASE_PATH = "/loyalty-social-media/v1/followed-channels"


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _followed_channel_body(raw) -> dict:
    body = _object_body(raw, field="followed-channel-json")
    followed_channel = body.get("followedChannel")
    if not isinstance(followed_channel, dict):
        raise _groups.ValidationError("--followed-channel-json must include followedChannel")
    channel = followed_channel.get("channel")
    if not isinstance(channel, str) or not channel.strip():
        raise _groups.ValidationError("--followed-channel-json must include followedChannel.channel")
    followed_channel["channel"] = channel.strip()
    return body


def cmd_loyalty_social_media_list(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list"
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


def cmd_loyalty_social_media_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _followed_channel_body(args.followed_channel_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"operation": "create-followed-channel", "followedChannel": body.get("followedChannel")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["create-followed-social-media-channel", "can-award-loyalty-points"],
            verification_notes=(
                "Verify with loyalty-social-media list using the same visitor/member identity. "
                "Official docs say members can only follow channels enabled in the dashboard."
            ),
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
