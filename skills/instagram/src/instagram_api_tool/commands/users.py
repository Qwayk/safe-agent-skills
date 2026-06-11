from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from ..instagram_client import InstagramAPIClient
from .write_utils import split_csv_arg


def _client(ctx: dict[str, Any]) -> InstagramAPIClient:
    return InstagramAPIClient(
        cfg=ctx["cfg"],
        env_file=ctx["env_file"],
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
    )


def cmd_users_me(args: Any, ctx: dict[str, Any]) -> int:
    fields = split_csv_arg(getattr(args, "fields", None))
    client = _client(ctx)
    result = client.get_me(",".join(fields) if fields else None)
    out = {"ok": True, "command": "users.me", "result": result}
    ctx["audit"].write("users.me", out)
    ctx["out"].emit(out)
    return 0


def cmd_users_get(args: Any, ctx: dict[str, Any]) -> int:
    ig_user_id = str(getattr(args, "ig_user_id", "") or "").strip()
    if not ig_user_id:
        raise ValidationError("Missing --ig-user-id")
    fields = split_csv_arg(getattr(args, "fields", None))
    params: dict[str, Any] = {}
    if fields:
        params["fields"] = ",".join(fields)

    client = _client(ctx)
    result = client.get(f"/{ig_user_id}", params=params)
    out = {"ok": True, "command": "users.get", "result": result}
    ctx["audit"].write("users.get", out)
    ctx["out"].emit(out)
    return 0
