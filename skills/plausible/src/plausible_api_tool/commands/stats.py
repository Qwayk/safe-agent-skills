from __future__ import annotations

from typing import Any

from ..plausible import PlausibleClient
from ..stats_utils import (
    DateRangePair,
    apply_date_range,
    date_range_pair_for_days,
    ensure_site_id,
    load_query_from_sources,
    merge_paginated_responses,
    set_include_total_rows,
    set_pagination,
    validate_query,
)


def _date_range_from_args(*, days: int | None, date_range: str | None, default_days: int) -> str:
    if days is not None and date_range is not None:
        raise RuntimeError("Provide only one of: --days or --date-range")
    if date_range is not None:
        return date_range
    return f"{int(days if days is not None else default_days)}d"


def _paginate_if_needed(
    client: PlausibleClient,
    query: dict[str, Any],
    *,
    limit: int,
    offset: int,
    all_rows: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if limit <= 0:
        raise RuntimeError("--limit must be > 0")
    if offset < 0:
        raise RuntimeError("--offset must be >= 0")

    if not all_rows:
        q = set_pagination(query, limit=limit, offset=offset)
        resp = client.stats_query(q)
        return resp, {"all": False, "limit": limit, "offset": offset}

    # Auto-loop pagination until we reach total_rows (when available), otherwise until a short page.
    q = set_include_total_rows(query, True)
    page_limit = min(int(limit), 10000)
    q = set_pagination(q, limit=page_limit, offset=int(offset))

    first = client.stats_query(q)
    parts: list[dict[str, Any]] = []

    total_rows = None
    meta = first.get("meta")
    if isinstance(meta, dict) and isinstance(meta.get("total_rows"), int):
        total_rows = int(meta["total_rows"])

    got = len(first.get("results") or []) if isinstance(first.get("results"), list) else 0
    next_offset = int(offset) + page_limit

    while True:
        if total_rows is not None and next_offset >= total_rows:
            break
        if total_rows is None and got % page_limit != 0:
            break

        qn = set_pagination(q, limit=page_limit, offset=next_offset)
        part = client.stats_query(qn)
        parts.append(part)

        part_results_len = len(part.get("results") or []) if isinstance(part.get("results"), list) else 0
        got += part_results_len
        next_offset += page_limit
        if part_results_len < page_limit:
            break

    merged = merge_paginated_responses(first, parts)
    info = {
        "all": True,
        "limit": page_limit,
        "offset_start": int(offset),
        "pages": 1 + len(parts),
        "rows": len(merged.get("results") or []) if isinstance(merged.get("results"), list) else None,
        "total_rows": total_rows,
    }
    return merged, info


def _breakdown_query(
    *,
    site_id: str,
    date_range: str,
    dimension: str,
    metrics: list[str],
    order_by_metric: str,
    filters: list[Any] | None = None,
) -> dict[str, Any]:
    q: dict[str, Any] = {
        "site_id": site_id,
        "date_range": date_range,
        "metrics": metrics,
        "dimensions": [dimension],
        "order_by": [[order_by_metric, "desc"]],
    }
    if filters:
        q["filters"] = filters
    return q


def cmd_stats_query(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])

    query = load_query_from_sources(file=args.file, query=args.query, stdin=bool(args.stdin))
    query = ensure_site_id(query, cfg.site_id)

    resp = client.stats_query(query)
    out = {"ok": True, "query": query, "response": resp}
    ctx["audit"].write("stats.query", {"query": query})
    ctx["out"].emit(out)
    return 0


def cmd_stats_validate(args, ctx) -> int:
    query = load_query_from_sources(file=args.file, query=None, stdin=False)
    errors, warnings = validate_query(query)
    if errors:
        ctx["out"].emit(
            {"ok": False, "error": "Invalid query", "error_type": "ValidationError", "errors": errors, "warnings": warnings}
        )
        return 1
    ctx["out"].emit({"ok": True, "valid": True, "warnings": warnings, "query": query})
    return 0


def cmd_stats_pages_top(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])

    dr = _date_range_from_args(days=args.days, date_range=args.date_range, default_days=30)
    metric = str(args.metric)
    metrics = [metric, "visitors"] if bool(args.include_visitors) else [metric]
    query = _breakdown_query(
        site_id=cfg.site_id,
        date_range=dr,
        dimension="event:page",
        metrics=metrics,
        order_by_metric=metric,
    )

    resp, page_info = _paginate_if_needed(client, query, limit=int(args.limit), offset=int(args.offset), all_rows=bool(args.all))
    out = {"ok": True, "query": query, "pagination": page_info, "response": resp}
    ctx["audit"].write("stats.pages_top", {"query": query, "pagination": page_info})
    ctx["out"].emit(out)
    return 0


def cmd_stats_sources(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])

    dr = _date_range_from_args(days=args.days, date_range=args.date_range, default_days=30)
    dim = str(args.dimension)
    metric = str(args.metric)
    query = _breakdown_query(
        site_id=cfg.site_id,
        date_range=dr,
        dimension=dim,
        metrics=[metric, "visits"] if metric != "visits" else [metric],
        order_by_metric=metric,
    )
    resp, page_info = _paginate_if_needed(client, query, limit=int(args.limit), offset=int(args.offset), all_rows=bool(args.all))
    out = {"ok": True, "query": query, "pagination": page_info, "response": resp}
    ctx["audit"].write("stats.sources", {"query": query, "pagination": page_info})
    ctx["out"].emit(out)
    return 0


def cmd_stats_referrers(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    dr = _date_range_from_args(days=args.days, date_range=args.date_range, default_days=30)
    metric = str(args.metric)
    query = _breakdown_query(
        site_id=cfg.site_id,
        date_range=dr,
        dimension="visit:referrer",
        metrics=[metric, "visits"] if metric != "visits" else [metric],
        order_by_metric=metric,
    )
    resp, page_info = _paginate_if_needed(client, query, limit=int(args.limit), offset=int(args.offset), all_rows=bool(args.all))
    out = {"ok": True, "query": query, "pagination": page_info, "response": resp}
    ctx["audit"].write("stats.referrers", {"query": query, "pagination": page_info})
    ctx["out"].emit(out)
    return 0


def cmd_stats_entry_exit(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    dr = _date_range_from_args(days=args.days, date_range=args.date_range, default_days=30)

    def run(dim: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        q = _breakdown_query(
            site_id=cfg.site_id,
            date_range=dr,
            dimension=dim,
            metrics=["visits", "visitors"],
            order_by_metric="visits",
        )
        resp, page_info = _paginate_if_needed(
            client, q, limit=int(args.limit), offset=int(args.offset), all_rows=bool(args.all)
        )
        return q, page_info, resp

    out: dict[str, Any] = {"ok": True, "date_range": dr}
    which = str(args.type)
    if which in ("entry", "both"):
        q, page, resp = run("visit:entry_page")
        out["entry"] = {"query": q, "pagination": page, "response": resp}
    if which in ("exit", "both"):
        q, page, resp = run("visit:exit_page")
        out["exit"] = {"query": q, "pagination": page, "response": resp}

    ctx["audit"].write("stats.entry_exit", {"type": which, "date_range": dr})
    ctx["out"].emit(out)
    return 0


def cmd_stats_devices(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    dr = _date_range_from_args(days=args.days, date_range=args.date_range, default_days=30)
    dim = str(args.dimension)
    query = _breakdown_query(
        site_id=cfg.site_id,
        date_range=dr,
        dimension=dim,
        metrics=["visits", "visitors"],
        order_by_metric="visits",
    )
    resp, page_info = _paginate_if_needed(client, query, limit=int(args.limit), offset=int(args.offset), all_rows=bool(args.all))
    out = {"ok": True, "query": query, "pagination": page_info, "response": resp}
    ctx["audit"].write("stats.devices", {"query": query, "pagination": page_info})
    ctx["out"].emit(out)
    return 0


def cmd_stats_goals_list(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    dr = _date_range_from_args(days=None, date_range=args.date_range, default_days=30)
    query = _breakdown_query(
        site_id=cfg.site_id,
        date_range=dr,
        dimension="event:goal",
        metrics=["events", "visitors"],
        order_by_metric="events",
    )
    resp, page_info = _paginate_if_needed(client, query, limit=int(args.limit), offset=int(args.offset), all_rows=bool(args.all))
    out = {"ok": True, "query": query, "pagination": page_info, "response": resp}
    ctx["audit"].write("stats.goals_list", {"query": query, "pagination": page_info})
    ctx["out"].emit(out)
    return 0


def cmd_stats_goals_timeseries(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    dr = _date_range_from_args(days=None, date_range=args.date_range, default_days=30)
    query: dict[str, Any] = {
        "site_id": cfg.site_id,
        "date_range": dr,
        "metrics": ["events", "visitors"],
        "dimensions": ["time:day"],
        "filters": [["is", "event:goal", [args.goal]]],
        "order_by": [["time:day", "asc"]],
    }
    resp = client.stats_query(query)
    out = {"ok": True, "query": query, "response": resp}
    ctx["audit"].write("stats.goals_timeseries", {"query": query})
    ctx["out"].emit(out)
    return 0


def cmd_stats_goals_breakdown(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    dr = _date_range_from_args(days=None, date_range=args.date_range, default_days=30)
    dim = f"event:props:{args.prop}"
    query = _breakdown_query(
        site_id=cfg.site_id,
        date_range=dr,
        dimension=dim,
        metrics=["events", "visitors"],
        order_by_metric="events",
        filters=[["is", "event:goal", [args.goal]]],
    )
    resp, page_info = _paginate_if_needed(client, query, limit=int(args.limit), offset=int(args.offset), all_rows=bool(args.all))
    out = {"ok": True, "query": query, "pagination": page_info, "response": resp}
    ctx["audit"].write("stats.goals_breakdown", {"query": query, "pagination": page_info})
    ctx["out"].emit(out)
    return 0


def cmd_stats_goal_breakdown(args, ctx) -> int:
    # Alias with nicer flags (days + offset + all).
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    dr = _date_range_from_args(days=args.days, date_range=args.date_range, default_days=30)
    dim = f"event:props:{args.prop}"
    query = _breakdown_query(
        site_id=cfg.site_id,
        date_range=dr,
        dimension=dim,
        metrics=["events", "visitors"],
        order_by_metric="events",
        filters=[["is", "event:goal", [args.goal]]],
    )
    resp, page_info = _paginate_if_needed(client, query, limit=int(args.limit), offset=int(args.offset), all_rows=bool(args.all))
    out = {"ok": True, "query": query, "pagination": page_info, "response": resp}
    ctx["audit"].write("stats.goal_breakdown", {"query": query, "pagination": page_info})
    ctx["out"].emit(out)
    return 0


def cmd_stats_goal_pages(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    dr = _date_range_from_args(days=args.days, date_range=args.date_range, default_days=30)
    query = _breakdown_query(
        site_id=cfg.site_id,
        date_range=dr,
        dimension="event:page",
        metrics=["events", "visitors"],
        order_by_metric="events",
        filters=[["is", "event:goal", [args.goal]]],
    )
    resp, page_info = _paginate_if_needed(client, query, limit=int(args.limit), offset=int(args.offset), all_rows=bool(args.all))
    out = {"ok": True, "query": query, "pagination": page_info, "response": resp}
    ctx["audit"].write("stats.goal_pages", {"query": query, "pagination": page_info})
    ctx["out"].emit(out)
    return 0


def _goal_aggregate(
    client: PlausibleClient,
    *,
    site_id: str,
    date_range: str,
    goal: str,
    extra_filters: list[Any] | None = None,
) -> dict[str, Any]:
    q: dict[str, Any] = {
        "site_id": site_id,
        "date_range": date_range,
        "metrics": ["events", "visitors", "conversion_rate"],
        "filters": [["is", "event:goal", [goal]]] + (list(extra_filters or [])),
    }
    try:
        return {"goal": goal, "query": q, "response": client.stats_query(q), "missing_goal": False}
    except RuntimeError as e:
        msg = str(e)
        if f"The goal `{goal}` is not configured" in msg:
            return {
                "goal": goal,
                "query": q,
                "response": {"meta": {}, "query": q, "results": [{"dimensions": [], "metrics": [0, 0, None]}]},
                "missing_goal": True,
                "warning": f"Goal not configured in Plausible: {goal}",
            }
        raise


def cmd_stats_funnel_members(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    dr = _date_range_from_args(days=args.days, date_range=args.date_range, default_days=30)

    # Ordered chains (best-effort; these are not strict subsets, but they are still useful signals).
    #
    # Important: submit/email/confirmed are tracked as a single goal with a `trigger` prop, not separate goals.
    # We split by `event:props:trigger` here so the funnel is reportable without extra goal setup.
    funnels: dict[str, list[dict[str, Any]]] = {
        "popup_auto": [
            {"id": "members_modal_shown_auto", "goal": "members_modal_shown_auto"},
            {"id": "members_modal_submit (auto)", "goal": "members_modal_submit", "filters": [["is", "event:props:trigger", ["auto"]]]},
            {"id": "members_magic_link_sent (auto)", "goal": "members_magic_link_sent", "filters": [["is", "event:props:trigger", ["auto"]]]},
            {"id": "members_confirmed (auto)", "goal": "members_confirmed", "filters": [["is", "event:props:trigger", ["auto"]]]},
        ],
        "popup_manual": [
            {"id": "members_modal_shown_manual", "goal": "members_modal_shown_manual"},
            {"id": "members_modal_submit (manual)", "goal": "members_modal_submit", "filters": [["is", "event:props:trigger", ["manual"]]]},
            {"id": "members_magic_link_sent (manual)", "goal": "members_magic_link_sent", "filters": [["is", "event:props:trigger", ["manual"]]]},
            {"id": "members_confirmed (manual)", "goal": "members_confirmed", "filters": [["is", "event:props:trigger", ["manual"]]]},
        ],
        "member_gate": [
            {"id": "member_gate_shown", "goal": "member_gate_shown"},
            {"id": "member_gate_cta_click", "goal": "member_gate_cta_click"},
        ],
        "footer_newsletter": [
            {"id": "footer_signup_submit", "goal": "footer_signup_submit"},
            {"id": "footer_signup_success", "goal": "footer_signup_success"},
        ],
    }

    cache: dict[str, dict[str, Any]] = {}

    def get_step_row(step: dict[str, Any]) -> dict[str, Any]:
        goal = str(step["goal"])
        extra_filters = step.get("filters") if isinstance(step.get("filters"), list) else None
        cache_key = f"{goal}:{extra_filters!r}"
        if cache_key not in cache:
            cache[cache_key] = _goal_aggregate(client, site_id=cfg.site_id, date_range=dr, goal=goal, extra_filters=extra_filters)
        return cache[cache_key]

    missing_goals: list[str] = []
    summaries: dict[str, Any] = {}
    for name, chain in funnels.items():
        steps = []
        for step in chain:
            row = get_step_row(step)
            if bool(row.get("missing_goal")):
                missing_goals.append(str(step.get("goal")))

            events = 0
            results = row.get("response", {}).get("results") if isinstance(row.get("response"), dict) else None
            if isinstance(results, list) and results and isinstance(results[0], dict):
                metrics = results[0].get("metrics")
                if isinstance(metrics, list) and metrics and isinstance(metrics[0], (int, float)):
                    events = int(metrics[0])

            steps.append({"goal": str(step.get("id") or step.get("goal")), "events": events, "raw": row})

        drops = []
        for i in range(1, len(steps)):
            prev = steps[i - 1]["events"]
            cur = steps[i]["events"]
            drop = max(prev - cur, 0)
            ratio = (cur / prev) if prev > 0 else None
            drops.append(
                {
                    "from": steps[i - 1]["goal"],
                    "to": steps[i]["goal"],
                    "drop_events": drop,
                    "step_ratio": ratio,
                }
            )
        summaries[name] = {"steps": steps, "drop_off": drops}

    out = {"ok": True, "date_range": dr, "funnels": summaries, "missing_goals": sorted(set(missing_goals))}
    ctx["audit"].write("stats.funnel_members", {"date_range": dr})
    ctx["out"].emit(out)
    return 0


def _index_rows(resp: dict[str, Any]) -> dict[tuple[Any, ...], list[Any]]:
    out: dict[tuple[Any, ...], list[Any]] = {}
    results = resp.get("results")
    if not isinstance(results, list):
        return out
    for row in results:
        if not isinstance(row, dict):
            continue
        dims = row.get("dimensions")
        mets = row.get("metrics")
        key = tuple(dims) if isinstance(dims, list) else tuple()
        if isinstance(mets, list):
            out[key] = mets
    return out


def _metric_delta(cur: Any, prev: Any) -> dict[str, Any]:
    if isinstance(cur, (int, float)) and isinstance(prev, (int, float)):
        delta = cur - prev
        pct = (delta / prev) if prev not in (0, 0.0) else None
        return {"current": cur, "previous": prev, "delta": delta, "delta_pct": pct}
    return {"current": cur, "previous": prev, "delta": None, "delta_pct": None}


def cmd_stats_compare(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])

    base_query = load_query_from_sources(file=args.file, query=None, stdin=False)
    base_query = ensure_site_id(base_query, cfg.site_id)

    # Determine comparison date ranges (days only for now).
    range_str = str(args.range)
    if not range_str.endswith("d") or not range_str[:-1].isdigit():
        raise RuntimeError("--range must look like '7d', '30d', etc.")
    days = int(range_str[:-1])
    pair: DateRangePair = date_range_pair_for_days(days)

    cur_q = apply_date_range(base_query, pair.current)
    prev_q = apply_date_range(base_query, pair.previous)

    cur_resp = client.stats_query(cur_q)
    prev_resp = client.stats_query(prev_q)

    cur_rows = _index_rows(cur_resp)
    prev_rows = _index_rows(prev_resp)
    all_keys = sorted(set(cur_rows.keys()) | set(prev_rows.keys()))

    rows = []
    for key in all_keys:
        cur_m = cur_rows.get(key, [])
        prev_m = prev_rows.get(key, [])
        max_len = max(len(cur_m), len(prev_m))
        comps = []
        for i in range(max_len):
            comps.append(_metric_delta(cur_m[i] if i < len(cur_m) else None, prev_m[i] if i < len(prev_m) else None))
        rows.append({"dimensions": list(key), "metrics": comps})

    out = {
        "ok": True,
        "range": range_str,
        "current_query": cur_q,
        "previous_query": prev_q,
        "current_response_meta": cur_resp.get("meta"),
        "previous_response_meta": prev_resp.get("meta"),
        "rows": rows,
    }
    ctx["audit"].write("stats.compare", {"range": range_str})
    ctx["out"].emit(out)
    return 0
