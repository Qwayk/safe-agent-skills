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


def cmd_stories_list(args: Any, ctx: dict[str, Any]) -> int:
    ig_user_id = str(getattr(args, "ig_user_id", "") or "").strip()
    if not ig_user_id:
        raise ValidationError("Missing --ig-user-id")
    fields = split_csv_arg(getattr(args, "fields", None))
    params = {"fields": ",".join(fields)} if fields else None

    client = _client(ctx)
    result = client.get(f"/{ig_user_id}/stories", params=params)
    out = {"ok": True, "command": "stories.list", "result": result}
    ctx["audit"].write("stories.list", out)
    ctx["out"].emit(out)
    return 0
