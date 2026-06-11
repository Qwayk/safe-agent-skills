from __future__ import annotations

from typing import Any

from ..commands.common import build_optional_params, build_read_params
from ..errors import ValidationError
from ..threads_client import ThreadsAPIClient


def _client(ctx: dict[str, Any]) -> ThreadsAPIClient:
    return ThreadsAPIClient(
        cfg=ctx["cfg"],
        env_file=ctx["env_file"],
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
    )


def _resolve_threads_id(args: object, *, field: str) -> str:
    value = str(getattr(args, field, "") or "").strip()
    if not value:
        raise ValidationError(f"Missing --{field.replace('_', '-')}")
    return value

def _resolve_threads_user_id(args: object, ctx: dict[str, Any]) -> str:
    provided = str(getattr(args, "threads_user_id", "") or "").strip()
    if provided:
        return provided
    fallback = str(getattr(ctx["cfg"], "default_user_id", "") or "").strip()
    if fallback:
        return fallback
    raise ValidationError("Missing --threads-user-id and THREADS_DEFAULT_USER_ID is not set")


def cmd_insights_media(args, ctx: dict[str, Any]) -> int:
    media_id = _resolve_threads_id(args, field="threads_media_id")
    params = build_read_params(args=args)
    params.update(build_optional_params(args=args, include_metric=True))
    period = str(getattr(args, "period", "") or "").strip()
    if period:
        params["period"] = period
    result = _client(ctx).media_insights(threads_media_id=media_id, params=params)
    out = {"ok": True, "command": "insights.media", "result": result}
    ctx["audit"].write("insights.media", out)
    ctx["out"].emit(out)
    return 0


def cmd_insights_user(args, ctx: dict[str, Any]) -> int:
    user_id = _resolve_threads_user_id(args, ctx)
    params = build_read_params(args=args)
    params.update(build_optional_params(args=args, include_metric=True))
    period = str(getattr(args, "period", "") or "").strip()
    if period:
        params["period"] = period
    result = _client(ctx).user_insights(threads_user_id=user_id, params=params)
    out = {"ok": True, "command": "insights.user", "result": result}
    ctx["audit"].write("insights.user", out)
    ctx["out"].emit(out)
    return 0
