from __future__ import annotations

from ..freepik_api import FreepikApi
from ..http import HttpClient


def cmd_auth_check(args: object, ctx: dict) -> int:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"], user_agent="freepik-api-tool/0.1")
    api = FreepikApi(cfg=cfg, http=http)

    payload = api.get_resources(query="test", page=1, limit=1, extra_params={})
    sample = None
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, list) and data and isinstance(data[0], dict):
            item = data[0]
            image = item.get("image") if isinstance(item.get("image"), dict) else {}
            source = image.get("source") if isinstance(image.get("source"), dict) else {}
            sample = {
                "id": item.get("id"),
                "title": item.get("title"),
                "url": item.get("url"),
                "type": image.get("type") or item.get("type"),
                "preview_url": source.get("url"),
            }
    out = {"ok": True, "sample": sample}
    if "audit" in ctx:
        ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0
