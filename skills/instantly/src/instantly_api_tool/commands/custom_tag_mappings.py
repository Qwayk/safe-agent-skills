from __future__ import annotations

from typing import Any

from ..http import HttpClient
from ..instantly_client import InstantlyClient


def _client(ctx: dict) -> InstantlyClient:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="instantly-api-tool")
    return InstantlyClient(cfg=cfg, http=http)


def _pagination_params(args: Any) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if getattr(args, "limit", None) is not None:
        params["limit"] = int(args.limit)
    if getattr(args, "starting_after", None):
        params["starting_after"] = str(args.starting_after).strip()
    return params


def cmd_custom_tag_mappings_list(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.get("/custom-tag-mappings", params=_pagination_params(args))
    out = {"ok": True, "custom_tag_mappings": res.data, "next_starting_after": res.next_starting_after}
    ctx["audit"].write("custom_tag_mappings.list", {"ok": True})
    ctx["out"].emit(out)
    return 0

