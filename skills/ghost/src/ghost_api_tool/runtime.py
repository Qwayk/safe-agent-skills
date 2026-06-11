from __future__ import annotations

from typing import Any

from .ghost_api import GhostAdminApi
from .ghost_content_api import GhostContentApi
from .http import HttpClient


def get_api(ctx: dict[str, Any]) -> GhostAdminApi:
    api = ctx.get("_api")
    if api is not None:
        return api
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"], user_agent="ghost-api-tool/0.1")
    api = GhostAdminApi(cfg=cfg, http=http)
    ctx["_api"] = api
    return api


def get_content_api(ctx: dict[str, Any]) -> GhostContentApi:
    api = ctx.get("_content_api")
    if api is not None:
        return api
    cfg = ctx["content_cfg"]
    http = HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"], user_agent="ghost-api-tool/0.1")
    api = GhostContentApi(cfg=cfg, http=http)
    ctx["_content_api"] = api
    return api
