from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from ..plausible import PlausibleClient


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
    q: dict[str, Any] = {
        "site_id": site_id,
        "date_range": date_range,
        "metrics": metrics,
        "dimensions": [dimension],
        "order_by": [[order_by_metric, "desc"]],
        "pagination": {"limit": int(limit), "offset": 0},
    }
    if filters:
        q["filters"] = filters
    return q


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
            row_dims = row.get("dimensions") if isinstance(row.get("dimensions"), list) else []
            row_mets = row.get("metrics") if isinstance(row.get("metrics"), list) else []
            w.writerow([*row_dims, *row_mets])


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


def _membership_funnels(client: PlausibleClient, *, site_id: str, date_range: str) -> dict[str, Any]:
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
            drops.append(
                {
                    "from": steps[i - 1]["goal"],
                    "to": steps[i]["goal"],
                    "drop_events": max(prev - cur, 0),
                    "step_ratio": (cur / prev) if prev > 0 else None,
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
    funnels = _membership_funnels(client, site_id=cfg.site_id, date_range=dr)

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
            "top_pages": {"query": pages_q, "response": pages},
            "sources_channel": {"query": sources_q, "response": sources},
            "goals": {"query": goals_q, "response": goals},
            "membership_funnels": funnels,
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

    funnels = _membership_funnels(client, site_id=cfg.site_id, date_range=dr)
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
    placement = client.stats_query(placement_q)

    project_cfg = ctx.get("project_cfg") or {}
    out_dir_str = args.out_dir or project_cfg.get("reports_out_dir")
    csv_files: list[str] = []
    if out_dir_str:
        out_dir = Path(str(out_dir_str)).expanduser().resolve()
        _write_breakdown_csv(out_dir / f"membership_goals_{days}d.csv", query=goals_q, response=goals)
        _write_breakdown_csv(out_dir / f"members_modal_shown_manual_by_placement_{days}d.csv", query=placement_q, response=placement)
        csv_files = [
            str(out_dir / f"membership_goals_{days}d.csv"),
            str(out_dir / f"members_modal_shown_manual_by_placement_{days}d.csv"),
        ]

    out = {
        "ok": True,
        "date_range": dr,
        "reports": {
            "membership_funnels": funnels,
            "goals": {"query": goals_q, "response": goals},
            "members_modal_shown_manual_by_placement": {"query": placement_q, "response": placement},
        },
        "csv_files": csv_files,
    }
    ctx["audit"].write("report.membership", {"date_range": dr, "out_dir": str(out_dir_str) if out_dir_str else None})
    ctx["out"].emit(out)
    return 0
