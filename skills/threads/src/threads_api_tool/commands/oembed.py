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


def cmd_oembed_get(args, ctx: dict[str, Any]) -> int:
    url = str(getattr(args, "url", "") or "").strip()
    if not url:
        raise ValidationError("Missing --url")
    params = build_read_params(args=args)
    params.update(build_optional_params(args=args, include_maxwidth=True))
    result = _client(ctx).oembed(url=url, params=params)
    out = {"ok": True, "command": "oembed.get", "result": result}
    ctx["audit"].write("oembed.get", out)
    ctx["out"].emit(out)
    return 0
