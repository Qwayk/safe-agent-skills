from __future__ import annotations

from ..errors import ValidationError
from ..graph import _parse_kv_pairs


def cmd_graph_get(args, ctx) -> int:
    out = ctx["out"]
    audit = ctx["audit"]
    graph = ctx["graph"]

    object_id = str(getattr(args, "object_id", "") or "").strip()
    if not object_id:
        raise ValidationError("Missing --object-id")

    edge = str(getattr(args, "edge", "") or "").strip()
    fields = str(getattr(args, "fields", "") or "").strip()
    params = _parse_kv_pairs(getattr(args, "param", None))
    if fields:
        params.setdefault("fields", fields)

    max_pages = getattr(args, "max_pages", None)
    max_items = getattr(args, "max_items", None)

    if edge:
        res = graph.list_edge(
            object_id=object_id,
            edge=edge,
            params=params,
            max_pages=max_pages,
            max_items=max_items,
        )
        out_obj = {
            "ok": True,
            "graph_get": {"object_id": object_id, "edge": edge, "params": params},
            "data": res.data,
            "count": len(res.data),
            "paging": res.paging,
            "pages_fetched": res.raw_pages,
        }
        audit.write(
            "graph.get_edge",
            {"object_id": object_id, "edge": edge, "params": list(params.keys()), "count": len(res.data)},
        )
        out.emit(out_obj)
        return 0

    payload = graph.get(object_id, params=params or None)
    out_obj = {"ok": True, "graph_get": {"object_id": object_id, "params": params}, "data": payload}
    audit.write("graph.get_object", {"object_id": object_id, "params": list(params.keys())})
    out.emit(out_obj)
    return 0

