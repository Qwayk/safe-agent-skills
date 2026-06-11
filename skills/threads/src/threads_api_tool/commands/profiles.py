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


def cmd_profiles_me(args: object, ctx: dict[str, Any]) -> int:
    params = build_read_params(args=args, include_pagination=False, include_reverse=False)
    fields = params.get("fields")
    client = _client(ctx)
    result = client.get_me(fields=fields)
    out = {"ok": True, "command": "profiles.me", "result": result}
    ctx["audit"].write("profiles.me", out)
    ctx["out"].emit(out)
    return 0


def cmd_profiles_get(args, ctx: dict[str, Any]) -> int:
    threads_user_id = _resolve_threads_user_id(args, ctx)
    params = build_read_params(args=args, include_pagination=False, include_reverse=False)
    fields = params.pop("fields", None)
    client = _client(ctx)
    result = client.get_profile(threads_user_id=threads_user_id, fields=fields)
    out = {"ok": True, "command": "profiles.get", "result": result}
    ctx["audit"].write("profiles.get", out)
    ctx["out"].emit(out)
    return 0


def cmd_profiles_lookup(args, ctx: dict[str, Any]) -> int:
    username = str(getattr(args, "username", "") or "").strip()
    if not username:
        raise ValidationError("Missing --username")
    params = build_read_params(args=args, include_pagination=False, include_reverse=False)
    fields = params.pop("fields", None)
    client = _client(ctx)
    result = client.lookup_profile(username=username, fields=fields)
    out = {"ok": True, "command": "profiles.lookup", "result": result}
    ctx["audit"].write("profiles.lookup", out)
    ctx["out"].emit(out)
    return 0
