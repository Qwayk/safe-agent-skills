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
    page_summary,
    set_include_total_rows,
    set_pagination,
    total_result_rows,
    validate_query,
)
from .report import membership_funnels


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

    page_limit = min(limit, 10000)
    query = set_include_total_rows(query, True)
    first = client.stats_query(set_pagination(query, limit=page_limit, offset=offset))
    total_rows = total_result_rows(first)
    row_count = len(first["results"])
    last_page_rows = row_count
    parts: list[dict[str, Any]] = []

    while all_rows and last_page_rows > 0:
        if total_rows is not None:
            if offset + row_count >= total_rows:
                break
        elif last_page_rows < page_limit:
            break

        part = client.stats_query(set_pagination(query, limit=page_limit, offset=offset + row_count))
        parts.append(part)
        last_page_rows = len(part["results"])
        row_count += last_page_rows
        if total_rows is None:
            total_rows = total_result_rows(part)

    info = page_summary(
        rows=row_count, offset=offset, limit=page_limit, total_rows=total_rows, last_page_rows=last_page_rows,
    )
    info.update({"all": all_rows, "pages": 1 + len(parts)})
    info["offset_start" if all_rows else "offset"] = offset
    if all_rows and info["complete"] is not True:
        info["reason"] = "Plausible stopped returning rows before the total it reported."
    return (merge_paginated_responses(first, parts) if all_rows else first), info


def _page_ok(info: dict[str, Any]) -> bool:
    return not info["all"] or info["complete"] is True


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
    pagination = query.get("pagination") or {}
    total_rows = total_result_rows(resp)
    if pagination or total_rows is not None:
        rows = len(resp["results"])
        out["pagination"] = page_summary(
            rows=rows,
            offset=int(pagination.get("offset", 0)),
            limit=int(pagination.get("limit", 10000)),
            total_rows=total_rows,
            last_page_rows=rows,
        )
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
    out = {"ok": _page_ok(page_info), "query": query, "pagination": page_info, "response": resp}
    ctx["audit"].write("stats.pages_top", {"query": query, "pagination": page_info})
    ctx["out"].emit(out)
    return 0 if out["ok"] else 1


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
    out = {"ok": _page_ok(page_info), "query": query, "pagination": page_info, "response": resp}
    ctx["audit"].write("stats.sources", {"query": query, "pagination": page_info})
    ctx["out"].emit(out)
    return 0 if out["ok"] else 1


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
    out = {"ok": _page_ok(page_info), "query": query, "pagination": page_info, "response": resp}
    ctx["audit"].write("stats.referrers", {"query": query, "pagination": page_info})
    ctx["out"].emit(out)
    return 0 if out["ok"] else 1


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

    out["ok"] = all(_page_ok(out[key]["pagination"]) for key in ("entry", "exit") if key in out)
    ctx["audit"].write("stats.entry_exit", {"type": which, "date_range": dr})
    ctx["out"].emit(out)
    return 0 if out["ok"] else 1


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
    out = {"ok": _page_ok(page_info), "query": query, "pagination": page_info, "response": resp}
    ctx["audit"].write("stats.devices", {"query": query, "pagination": page_info})
    ctx["out"].emit(out)
    return 0 if out["ok"] else 1


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
    out = {"ok": _page_ok(page_info), "query": query, "pagination": page_info, "response": resp}
    ctx["audit"].write("stats.goals_list", {"query": query, "pagination": page_info})
    ctx["out"].emit(out)
    return 0 if out["ok"] else 1


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
    out = {"ok": _page_ok(page_info), "query": query, "pagination": page_info, "response": resp}
    ctx["audit"].write("stats.goals_breakdown", {"query": query, "pagination": page_info})
    ctx["out"].emit(out)
    return 0 if out["ok"] else 1


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
    out = {"ok": _page_ok(page_info), "query": query, "pagination": page_info, "response": resp}
    ctx["audit"].write("stats.goal_breakdown", {"query": query, "pagination": page_info})
    ctx["out"].emit(out)
    return 0 if out["ok"] else 1


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
    out = {"ok": _page_ok(page_info), "query": query, "pagination": page_info, "response": resp}
    ctx["audit"].write("stats.goal_pages", {"query": query, "pagination": page_info})
    ctx["out"].emit(out)
    return 0 if out["ok"] else 1


def cmd_stats_funnel_members(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])
    dr = _date_range_from_args(days=args.days, date_range=args.date_range, default_days=30)
    funnels = membership_funnels(client, site_id=cfg.site_id, date_range=dr)
    missing_goals = funnels.pop("missing_goals")
    out = {"ok": True, "date_range": dr, "funnels": funnels, "missing_goals": missing_goals}
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
