from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from ..graph import _parse_kv_pairs
from ..http import HttpClient


def _redact_recursive(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _redact_recursive(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_redact_recursive(v) for v in obj]
    if isinstance(obj, str):
        return HttpClient.redact_url(obj)
    return obj


def cmd_previews_get(args, ctx) -> int:
    out = ctx["out"]
    audit = ctx["audit"]
    graph = ctx["graph"]

    cid = str(getattr(args, "creative_id", "") or "").strip()
    if not cid:
        raise ValidationError("Missing --creative-id")

    params = _parse_kv_pairs(getattr(args, "param", None))
    ad_format = str(getattr(args, "ad_format", "") or "").strip()
    if ad_format:
        params.setdefault("ad_format", ad_format)

    res = graph.list_edge(object_id=cid, edge="previews", params=params or None, max_pages=1, max_items=0)
    safe_data = _redact_recursive(res.data)
    out_obj = {
        "ok": True,
        "previews_get": {"creative_id": cid, "params": params},
        "data": safe_data,
        "count": len(safe_data) if isinstance(safe_data, list) else 0,
        "paging": res.paging,
        "pages_fetched": res.raw_pages,
    }
    audit.write("previews.get", {"creative_id": cid, "count": out_obj["count"], "params": list(params.keys())})
    out.emit(out_obj)
    return 0

