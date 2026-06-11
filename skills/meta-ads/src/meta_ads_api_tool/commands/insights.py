from __future__ import annotations

import json

from ..errors import ValidationError
from ..graph import _parse_kv_pairs
from ._ad_account_edge_helpers import _required_ad_account_id


def _require_level(args) -> str:
    level = str(getattr(args, "level", "") or "").strip().lower()
    if level not in {"account", "campaign", "adset", "ad"}:
        raise ValidationError("--level must be one of: account, campaign, adset, ad")
    return level


def _common_params_from_args(args) -> dict[str, str]:
    fields = str(getattr(args, "fields", "") or "").strip()
    params = _parse_kv_pairs(getattr(args, "param", None))

    time_increment = str(getattr(args, "time_increment", "") or "").strip()
    if time_increment:
        params.setdefault("time_increment", time_increment)

    breakdowns = getattr(args, "breakdown", None) or []
    if breakdowns:
        params.setdefault("breakdowns", ",".join(str(b).strip() for b in breakdowns if str(b).strip()))

    action_breakdowns = getattr(args, "action_breakdown", None) or []
    if action_breakdowns:
        params.setdefault("action_breakdowns", ",".join(str(b).strip() for b in action_breakdowns if str(b).strip()))

    action_windows = getattr(args, "action_attribution_window", None) or []
    if action_windows:
        params.setdefault(
            "action_attribution_windows",
            ",".join(str(w).strip() for w in action_windows if str(w).strip()),
        )

    if fields:
        params.setdefault("fields", fields)
    return params


def _time_range_param(*, since: str, until: str) -> str:
    s = str(since or "").strip()
    u = str(until or "").strip()
    if not s or not u:
        raise ValidationError("Use both since and until (YYYY-MM-DD)")
    return json.dumps({"since": s, "until": u}, separators=(",", ":"))


def cmd_insights_get(args, ctx) -> int:
    out = ctx["out"]
    audit = ctx["audit"]
    graph = ctx["graph"]

    ad_account_id = _required_ad_account_id(args, ctx)
    level = _require_level(args)

    params = _common_params_from_args(args)
    params.setdefault("level", level)

    since = str(getattr(args, "since", "") or "").strip()
    until = str(getattr(args, "until", "") or "").strip()
    if (since and not until) or (until and not since):
        raise ValidationError("Use --since and --until together (or omit both)")
    if since and until:
        params.setdefault("time_range", _time_range_param(since=since, until=until))

    res = graph.list_edge(
        object_id=ad_account_id,
        edge="insights",
        params=params,
        max_pages=getattr(args, "max_pages", None),
        max_items=getattr(args, "max_items", None),
    )

    out_obj = {
        "ok": True,
        "insights_get": {
            "ad_account_id": ad_account_id,
            "level": level,
            "params": params,
        },
        "data": res.data,
        "count": len(res.data),
        "paging": res.paging,
        "pages_fetched": res.raw_pages,
    }
    audit.write(
        "insights.get",
        {
            "ad_account_id": ad_account_id,
            "level": level,
            "count": len(res.data),
            "params": list(params.keys()),
        },
    )
    out.emit(out_obj)
    return 0


def cmd_insights_compare(args, ctx) -> int:
    out = ctx["out"]
    audit = ctx["audit"]
    graph = ctx["graph"]

    ad_account_id = _required_ad_account_id(args, ctx)
    level = _require_level(args)
    params_common = _common_params_from_args(args)
    params_common.setdefault("level", level)

    since_a = str(getattr(args, "since_a", "") or "").strip()
    until_a = str(getattr(args, "until_a", "") or "").strip()
    since_b = str(getattr(args, "since_b", "") or "").strip()
    until_b = str(getattr(args, "until_b", "") or "").strip()

    params_a = dict(params_common)
    params_a.setdefault("time_range", _time_range_param(since=since_a, until=until_a))
    params_b = dict(params_common)
    params_b.setdefault("time_range", _time_range_param(since=since_b, until=until_b))

    res_a = graph.list_edge(
        object_id=ad_account_id,
        edge="insights",
        params=params_a,
        max_pages=getattr(args, "max_pages", None),
        max_items=getattr(args, "max_items", None),
    )
    res_b = graph.list_edge(
        object_id=ad_account_id,
        edge="insights",
        params=params_b,
        max_pages=getattr(args, "max_pages", None),
        max_items=getattr(args, "max_items", None),
    )

    out_obj = {
        "ok": True,
        "insights_compare": {
            "ad_account_id": ad_account_id,
            "level": level,
            "params_common": {k: v for k, v in params_common.items() if k != "access_token"},
            "range_a": {"since": since_a, "until": until_a},
            "range_b": {"since": since_b, "until": until_b},
        },
        "data": {"a": res_a.data, "b": res_b.data},
        "count": {"a": len(res_a.data), "b": len(res_b.data)},
        "paging": {"a": res_a.paging, "b": res_b.paging},
        "pages_fetched": {"a": res_a.raw_pages, "b": res_b.raw_pages},
    }
    audit.write(
        "insights.compare",
        {
            "ad_account_id": ad_account_id,
            "level": level,
            "count_a": len(res_a.data),
            "count_b": len(res_b.data),
            "params": list(params_common.keys()),
        },
    )
    out.emit(out_obj)
    return 0
