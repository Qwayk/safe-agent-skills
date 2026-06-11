from __future__ import annotations

from ..errors import ValidationError
from ..graph import _parse_kv_pairs
from ._ad_account_edge_helpers import _edge_list_common, _required_ad_account_id


def cmd_videos_list(args, ctx) -> int:
    out = ctx["out"]
    audit = ctx["audit"]
    graph = ctx["graph"]

    ad_account_id = _required_ad_account_id(args, ctx)
    _, params = _edge_list_common(args)
    params.setdefault("limit", str(getattr(args, "limit", 100) or 100))

    res = graph.list_edge(
        object_id=ad_account_id,
        edge="advideos",
        params=params,
        max_pages=getattr(args, "max_pages", None),
        max_items=getattr(args, "max_items", None),
    )
    out_obj = {
        "ok": True,
        "videos_list": {"ad_account_id": ad_account_id, "params": params},
        "data": res.data,
        "count": len(res.data),
        "paging": res.paging,
        "pages_fetched": res.raw_pages,
    }
    audit.write("videos.list", {"ad_account_id": ad_account_id, "count": len(res.data), "params": list(params.keys())})
    out.emit(out_obj)
    return 0


def cmd_videos_get(args, ctx) -> int:
    out = ctx["out"]
    audit = ctx["audit"]
    graph = ctx["graph"]

    vid = str(getattr(args, "video_id", "") or "").strip()
    if not vid:
        raise ValidationError("Missing --video-id")
    fields = str(getattr(args, "fields", "") or "").strip()
    params = _parse_kv_pairs(getattr(args, "param", None))
    if fields:
        params.setdefault("fields", fields)

    payload = graph.get(vid, params=params or None)
    out_obj = {"ok": True, "videos_get": {"video_id": vid, "params": params}, "data": payload}
    audit.write("videos.get", {"video_id": vid, "params": list(params.keys())})
    out.emit(out_obj)
    return 0

