from __future__ import annotations

from ..errors import ValidationError
from ..graph import _parse_kv_pairs
from ._ad_account_edge_helpers import _edge_list_common, _required_ad_account_id


def cmd_images_list(args, ctx) -> int:
    out = ctx["out"]
    audit = ctx["audit"]
    graph = ctx["graph"]

    ad_account_id = _required_ad_account_id(args, ctx)
    _, params = _edge_list_common(args)
    params.setdefault("limit", str(getattr(args, "limit", 100) or 100))

    res = graph.list_edge(
        object_id=ad_account_id,
        edge="adimages",
        params=params,
        max_pages=getattr(args, "max_pages", None),
        max_items=getattr(args, "max_items", None),
    )
    out_obj = {
        "ok": True,
        "images_list": {"ad_account_id": ad_account_id, "params": params},
        "data": res.data,
        "count": len(res.data),
        "paging": res.paging,
        "pages_fetched": res.raw_pages,
    }
    audit.write("images.list", {"ad_account_id": ad_account_id, "count": len(res.data), "params": list(params.keys())})
    out.emit(out_obj)
    return 0


def cmd_images_get(args, ctx) -> int:
    out = ctx["out"]
    audit = ctx["audit"]
    graph = ctx["graph"]

    iid = str(getattr(args, "image_id", "") or "").strip()
    if not iid:
        raise ValidationError("Missing --image-id")
    fields = str(getattr(args, "fields", "") or "").strip()
    params = _parse_kv_pairs(getattr(args, "param", None))
    if fields:
        params.setdefault("fields", fields)

    payload = graph.get(iid, params=params or None)
    out_obj = {"ok": True, "images_get": {"image_id": iid, "params": params}, "data": payload}
    audit.write("images.get", {"image_id": iid, "params": list(params.keys())})
    out.emit(out_obj)
    return 0

