from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from ..plausible import PlausibleClient
from ..stats_utils import page_summary, total_result_rows


def _date_range_from_days(days: int) -> str:
    if days <= 0:
        raise RuntimeError("--days must be > 0")
    return f"{int(days)}d"


def _breakdown_query(
    *,
    site_id: str,
    date_range: str,
    dimension: str,
    metrics: list[str],
    order_by_metric: str,
    filters: list[Any] | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    if limit <= 0:
        raise RuntimeError("--limit must be > 0")
    q: dict[str, Any] = {
        "site_id": site_id,
        "date_range": date_range,
        "metrics": metrics,
        "dimensions": [dimension],
        "order_by": [[order_by_metric, "desc"]],
        "include": {"total_rows": True},
        "pagination": {"limit": int(limit), "offset": 0},
    }
    if filters:
        q["filters"] = filters
    return q


def _breakdown_result(query: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    rows = len(response["results"])
    return {
        "query": query,
        "response": response,
        "pagination": page_summary(
            rows=rows, offset=0, limit=query["pagination"]["limit"],
            total_rows=total_result_rows(response), last_page_rows=rows,
        ),
    }


def _write_breakdown_csv(out_path: Path, *, query: dict[str, Any], response: dict[str, Any]) -> None:
    dims = query.get("dimensions") or []
    mets = query.get("metrics") or []
    if not isinstance(dims, list) or not isinstance(mets, list):
        raise RuntimeError("Unexpected query shape for CSV export")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([*dims, *mets])
        results = response.get("results")
        if not isinstance(results, list):
            return
        for row in results:
            if not isinstance(row, dict):
                continue
            row_dims = row.get("dimensions")
            row_mets = row.get("metrics")
            w.writerow([
                *(row_dims if isinstance(row_dims, list) else []),
                *(row_mets if isinstance(row_mets, list) else []),
            ])


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
                "response": None,
                "missing_goal": True,
                "warning": f"Goal not configured in Plausible: {goal}",
            }
        raise


def membership_funnels(client: PlausibleClient, *, site_id: str, date_range: str) -> dict[str, Any]:
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
            cache[cache_key] = _goal_aggregate(client, site_id=site_id, date_range=date_range, goal=goal, extra_filters=extra_filters)
        return cache[cache_key]

    missing_goals: list[str] = []
    out: dict[str, Any] = {"missing_goals": []}
    for name, chain in funnels.items():
        steps: list[dict[str, Any]] = []
        for step in chain:
            row = get_step_row(step)
            if bool(row.get("missing_goal")):
                missing_goals.append(str(step.get("goal")))

            results = row["response"]["results"] if row["response"] is not None else None
            events = 0 if results == [] else None
            if isinstance(results, list) and results and isinstance(results[0], dict):
                metrics = results[0].get("metrics")
                if isinstance(metrics, list) and metrics and isinstance(metrics[0], (int, float)):
                    events = int(metrics[0])

            steps.append({"goal": str(step.get("id") or step.get("goal")), "events": events, "raw": row})

        drops = []
        for i in range(1, len(steps)):
            prev = steps[i - 1]["events"]
            cur = steps[i]["events"]
            drops.append(
                {
                    "from": steps[i - 1]["goal"],
                    "to": steps[i]["goal"],
                    "drop_events": max(prev - cur, 0) if prev is not None and cur is not None else None,
                    "step_ratio": (cur / prev) if prev and cur is not None else None,
                }
            )
        out[name] = {"steps": steps, "drop_off": drops}
    out["missing_goals"] = sorted(set(missing_goals))
    return out


def cmd_report_weekly(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])

    days = int(args.days)
    dr = _date_range_from_days(days)
    limit = int(args.limit)

    pages_q = _breakdown_query(
        site_id=cfg.site_id,
        date_range=dr,
        dimension="event:page",
        metrics=["pageviews", "visitors"],
        order_by_metric="pageviews",
        limit=limit,
    )
    sources_q = _breakdown_query(
        site_id=cfg.site_id,
        date_range=dr,
        dimension="visit:channel",
        metrics=["visitors", "visits"],
        order_by_metric="visitors",
        limit=limit,
    )
    goals_q = _breakdown_query(
        site_id=cfg.site_id,
        date_range=dr,
        dimension="event:goal",
        metrics=["events", "visitors"],
        order_by_metric="events",
        limit=limit,
    )

    pages = client.stats_query(pages_q)
    sources = client.stats_query(sources_q)
    goals = client.stats_query(goals_q)

    project_cfg = ctx.get("project_cfg") or {}
    out_dir_str = args.out_dir or project_cfg.get("reports_out_dir")
    csv_files: list[str] = []
    if out_dir_str:
        out_dir = Path(str(out_dir_str)).expanduser().resolve()
        _write_breakdown_csv(out_dir / f"top_pages_{days}d.csv", query=pages_q, response=pages)
        _write_breakdown_csv(out_dir / f"sources_channel_{days}d.csv", query=sources_q, response=sources)
        _write_breakdown_csv(out_dir / f"goals_{days}d.csv", query=goals_q, response=goals)
        csv_files = [
            str(out_dir / f"top_pages_{days}d.csv"),
            str(out_dir / f"sources_channel_{days}d.csv"),
            str(out_dir / f"goals_{days}d.csv"),
        ]

    out = {
        "ok": True,
        "date_range": dr,
        "reports": {
            "top_pages": _breakdown_result(pages_q, pages),
            "sources_channel": _breakdown_result(sources_q, sources),
            "goals": _breakdown_result(goals_q, goals),
        },
        "csv_files": csv_files,
    }
    ctx["audit"].write("report.weekly", {"date_range": dr, "out_dir": str(out_dir_str) if out_dir_str else None})
    ctx["out"].emit(out)
    return 0


def cmd_report_membership(args, ctx) -> int:
    cfg = ctx["cfg"]
    client = PlausibleClient(cfg=cfg, http=ctx["http"])

    days = int(args.days)
    dr = _date_range_from_days(days)
    limit = int(args.limit)

    funnels = membership_funnels(client, site_id=cfg.site_id, date_range=dr)
    goals_q = _breakdown_query(
        site_id=cfg.site_id,
        date_range=dr,
        dimension="event:goal",
        metrics=["events", "visitors"],
        order_by_metric="events",
        limit=limit,
    )
    goals = client.stats_query(goals_q)

    placement_q = _breakdown_query(
        site_id=cfg.site_id,
        date_range=dr,
        dimension="event:props:placement",
        metrics=["events", "visitors"],
        order_by_metric="events",
        filters=[["is", "event:goal", ["members_modal_shown_manual"]]],
        limit=limit,
    )
    placement_result: dict[str, Any]
    if "members_modal_shown_manual" in funnels["missing_goals"]:
        placement_result = {
            "query": placement_q,
            "response": None,
            "warning": "The members_modal_shown_manual goal is not configured in Plausible.",
        }
    else:
        placement_result = _breakdown_result(placement_q, client.stats_query(placement_q))

    project_cfg = ctx.get("project_cfg") or {}
    out_dir_str = args.out_dir or project_cfg.get("reports_out_dir")
    csv_files: list[str] = []
    if out_dir_str:
        out_dir = Path(str(out_dir_str)).expanduser().resolve()
        _write_breakdown_csv(out_dir / f"membership_goals_{days}d.csv", query=goals_q, response=goals)
        csv_files = [str(out_dir / f"membership_goals_{days}d.csv")]
        if placement_result["response"] is not None:
            placement_path = out_dir / f"members_modal_shown_manual_by_placement_{days}d.csv"
            _write_breakdown_csv(placement_path, query=placement_q, response=placement_result["response"])
            csv_files.append(str(placement_path))

    out = {
        "ok": True,
        "date_range": dr,
        "reports": {
            "membership_funnels": funnels,
            "goals": _breakdown_result(goals_q, goals),
            "members_modal_shown_manual_by_placement": placement_result,
        },
        "csv_files": csv_files,
    }
    ctx["audit"].write("report.membership", {"date_range": dr, "out_dir": str(out_dir_str) if out_dir_str else None})
    ctx["out"].emit(out)
    return 0
