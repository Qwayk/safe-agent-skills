from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Type

from ..runs import find_run, list_runs


def cmd_runs_list(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    _ = args
    runs_index = ctx.get("runs_index_path")
    if not runs_index:
        ctx["out"].emit({"ok": True, "runs": [], "count": 0})
        return 0
    limit = int(getattr(args, "limit", 20) or 20)
    rows = list_runs(runs_index, limit=limit, tool="dynadot-api-tool")
    ctx["out"].emit({"ok": True, "runs": rows, "count": len(rows)})
    return 0


def cmd_runs_show(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    rid = str(getattr(args, "run_id", "") or "").strip()
    if not rid:
        ctx["out"].emit({"ok": False, "error": "Missing --run-id", "error_type": "ValidationError"})
        return 1
    runs_index = ctx.get("runs_index_path")
    if not runs_index or not runs_index.exists():
        ctx["out"].emit({"ok": False, "error": "No runs index found", "error_type": "NotFound"})
        return 1
    row = find_run(runs_index, run_id=rid, tool="dynadot-api-tool")
    if not row:
        ctx["out"].emit({"ok": False, "error": f"Run not found: {rid}", "error_type": "NotFound"})
        return 1
    summary_md = None
    try:
        ad = row.get("artifacts_dir")
        if isinstance(ad, str) and ad:
            p = (Path(ad) / "summary.md")
            if p.exists():
                summary_md = p.read_text(encoding="utf-8")
    except Exception:
        summary_md = None
    ctx["out"].emit({"ok": True, "run": row, "summary_md": summary_md})
    return 0


def register_runs(subparsers: argparse._SubParsersAction, *, parser_class: Type[argparse.ArgumentParser]) -> None:  # type: ignore[name-defined]
    runs = subparsers.add_parser("runs", help="Run history (local)")
    runs_sub = runs.add_subparsers(dest="runs_cmd", required=True, parser_class=parser_class)
    runs_list = runs_sub.add_parser("list", help="List recent runs")
    runs_list.add_argument("--limit", type=int, default=20, help="Max runs to return (default: 20)")
    runs_list.set_defaults(func=cmd_runs_list, write_capable=False)
    runs_show = runs_sub.add_parser("show", help="Show one run from the index")
    runs_show.add_argument("--run-id", required=True, help="Run id to show")
    runs_show.set_defaults(func=cmd_runs_show, write_capable=False)
