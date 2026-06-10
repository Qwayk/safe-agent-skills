from __future__ import annotations

from typing import Any

from ..commands.common import build_read_params
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


def cmd_mentions_list(args, ctx: dict[str, Any]) -> int:
    threads_user_id = _resolve_threads_user_id(args, ctx)
    params = build_read_params(args=args)
    result = _client(ctx).list_mentions(threads_user_id=threads_user_id, params=params)
    out = {"ok": True, "command": "mentions.list", "result": result}
    ctx["audit"].write("mentions.list", out)
    ctx["out"].emit(out)
    return 0
