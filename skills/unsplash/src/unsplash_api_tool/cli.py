from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import auth as auth_cmd
from .commands import collections as collections_cmd
from .commands import demo as demo_cmd
from .commands import export as export_cmd
from .commands import jobs as jobs_cmd
from .commands import onboarding as onboarding_cmd
from .commands import photos as photos_cmd
from .commands import search as search_cmd
from .commands import stats as stats_cmd
from .commands import topics as topics_cmd
from .commands import users as users_cmd
from .config import load_config
from .errors import SafetyError, ToolError, ValidationError
from .http import HttpClient
from .output import Output
from .project_config import load_project_config
from .runs import (
    RunContext,
    build_deterministic_summary,
    init_run_context,
    list_runs,
    find_run,
    write_summary_md,
    append_index_row,
    runs_index_path_for_env_file,
 )
from .unsplash_client import UnsplashClient


class _ToolArgumentParser(argparse.ArgumentParser):
    """
    Ensure user-input errors can be surfaced as JSON.

    Argparse defaults to printing usage/help to stderr and raising SystemExit, which makes it
    hard to keep the `--output json` contract (exactly one JSON object to stdout on errors).
    """

    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def _cmd_runs_list(args: argparse.Namespace, ctx: dict) -> int:
    _ = args
    runs_index = ctx.get("runs_index_path")
    if not runs_index:
        ctx["out"].emit({"ok": True, "runs": [], "count": 0})
        return 0
    limit = int(getattr(args, "limit", 20) or 20)
    rows = list_runs(runs_index, limit=limit)
    ctx["out"].emit({"ok": True, "runs": rows, "count": len(rows)})
    return 0


def _cmd_runs_show(args: argparse.Namespace, ctx: dict) -> int:
    rid = str(getattr(args, "run_id", "") or "").strip()
    if not rid:
        ctx["out"].emit({"ok": False, "error": "Missing --run-id", "error_type": "ValidationError"})
        return 1
    runs_index = ctx.get("runs_index_path")
    if not runs_index or not runs_index.exists():
        ctx["out"].emit({"ok": False, "error": "No runs index found", "error_type": "NotFound"})
        return 1
    row = find_run(runs_index, run_id=rid)
    if not row:
        ctx["out"].emit({"ok": False, "error": f"Run not found: {rid}", "error_type": "NotFound"})
        return 1
    summary = None
    try:
        ad = row.get("artifacts_dir")
        if isinstance(ad, str) and ad:
            p = (Path(ad) / "summary.md")
            if p.exists():
                summary = p.read_text(encoding="utf-8")
    except Exception:
        summary = None
    ctx["out"].emit({"ok": True, "run": row, "summary_md": summary})
    return 0


def _finalize_run_artifacts(
    *,
    run_ctx: RunContext,
    tool: str,
    version: str,
    command: str | None,
    env_fingerprint: str | None,
    output_obj: dict | None,
    audit_log_path: str | None,
    audit_log_global_path: str | None,
    apply: bool | None,
    yes: bool | None,
) -> None:
    if not run_ctx.enabled or not run_ctx.artifacts_dir or not run_ctx.runs_index_path or not run_ctx.run_id:
        return

    plan_file = run_ctx.artifacts_dir / "plan.json"
    receipt_file = run_ctx.artifacts_dir / "receipt.json"
    plan_path = str(plan_file) if plan_file.exists() else None
    receipt_path = str(receipt_file) if receipt_file.exists() else None

    summary_lines = build_deterministic_summary(
        tool=tool,
        version=version,
        run_id=run_ctx.run_id,
        env_fingerprint=env_fingerprint,
        command=command,
        output_obj=output_obj,
        plan_path=plan_path,
        receipt_path=receipt_path,
        audit_log_path=audit_log_path,
        audit_log_global_path=audit_log_global_path,
        runs_index_path=str(run_ctx.runs_index_path),
    )
    write_summary_md(path=run_ctx.artifacts_dir / "summary.md", lines=summary_lines)

    append_index_row(
        run_ctx.runs_index_path,
        {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "run_id": run_ctx.run_id,
            "artifacts_dir": str(run_ctx.artifacts_dir),
            "tool": tool,
            "version": version,
            "command": command,
            "env_fingerprint": env_fingerprint,
            "dry_run": bool(output_obj.get("dry_run")) if isinstance(output_obj, dict) else None,
            "apply": apply,
            "yes": yes,
            "ok": bool(output_obj.get("ok")) if isinstance(output_obj, dict) else None,
            "refused": bool(output_obj.get("refused")) if isinstance(output_obj, dict) else False,
            "plan_path": plan_path,
            "receipt_path": receipt_path,
            "audit_log": audit_log_path,
            "audit_log_global": audit_log_global_path,
        },
    )


def build_parser() -> argparse.ArgumentParser:
    p = _ToolArgumentParser(prog="unsplash-api-tool")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument(
        "--config",
        default=None,
        help="Optional non-secret project config JSON (paths/defaults). Use for customer projects; do not store API keys here.",
    )
    p.add_argument(
        "--project-dir",
        default=None,
        help="Optional project root dir for outputs. If not provided and --config is provided, defaults to the config file's directory; otherwise defaults to the current working directory.",
    )
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    p.add_argument("--debug", action="store_true", help="Show stack traces on errors")
    p.add_argument("--output", choices=("json", "text"), default="json", help="Output format (default: json)")
    p.add_argument("--log-file", default=None, help="Optional audit log path (JSONL)")
    p.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    p.add_argument("--yes", action="store_true", help="Additional confirmation for destructive/batch actions")
    p.add_argument(
        "--ack-no-snapshot",
        action="store_true",
        help="Acknowledge that this approved write may run without a saved before-state snapshot",
    )
    p.add_argument("--plan-out", default=None, help="Write a dry-run plan JSON to a file")
    p.add_argument("--plan-in", default=None, help="Apply from an existing plan JSON file (high-risk writes)")
    p.add_argument("--receipt-out", default=None, help="Write an apply receipt JSON to a file")
    p.add_argument(
        "--ack-irreversible",
        action="store_true",
        help="Extra acknowledgement for irreversible actions",
    )
    p.add_argument("--run-id", default=None, help="Optional run id (for run history/audit)")
    p.add_argument("--artifacts-dir", default=None, help="Optional artifacts directory for this run")
    p.add_argument("--no-artifacts", action="store_true", help="Disable writing local run artifacts")

    sub = p.add_subparsers(dest="cmd", required=False, parser_class=_ToolArgumentParser)

    runs = sub.add_parser("runs", help="Run history (local)")
    runs_sub = runs.add_subparsers(dest="runs_cmd", required=True, parser_class=_ToolArgumentParser)
    runs_list = runs_sub.add_parser("list", help="List recent runs")
    runs_list.add_argument("--limit", type=int, default=20, help="Max runs to return (default: 20)")
    runs_list.set_defaults(func=_cmd_runs_list, write_capable=False)
    runs_show = runs_sub.add_parser("show", help="Show one run from the index")
    runs_show.add_argument("--run-id", required=True, help="Run id to show")
    runs_show.set_defaults(func=_cmd_runs_show, write_capable=False)

    onboarding = sub.add_parser("onboarding", help="First-time setup help (no secrets)")
    onboarding.add_argument(
        "--no-write-env",
        action="store_true",
        help="Do not write/update the env file; print instructions only",
    )
    onboarding.set_defaults(func=onboarding_cmd.cmd_onboarding, write_capable=False)

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Smoke test credentials")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=False)

    key = auth_sub.add_parser("key", help="Access key helpers (manual copy/paste)")
    key_sub = key.add_subparsers(dest="key_cmd", required=True, parser_class=_ToolArgumentParser)
    key_set = key_sub.add_parser("set", help="Store auth JSON under .state/auth.json (never prints secrets)")
    key_set.add_argument("--file", required=True, help="Auth JSON file path (input)")
    key_set.set_defaults(func=auth_cmd.cmd_auth_key_set, write_capable=True)
    key_status = key_sub.add_parser("status", help="Show auth status (never prints secret values)")
    key_status.set_defaults(func=auth_cmd.cmd_auth_key_status, write_capable=False)

    jobs = sub.add_parser("jobs", help="Batch operations from job files")
    jobs_sub = jobs.add_subparsers(dest="jobs_cmd", required=True, parser_class=_ToolArgumentParser)
    jobs_run = jobs_sub.add_parser("run", help="Run a CSV job file (demo actions)")
    jobs_run.add_argument("--file", required=False, help="Job CSV file (must include action column)")
    jobs_run.add_argument("--limit", type=int, default=None, help="Max number of rows to process")
    jobs_run.set_defaults(func=jobs_cmd.cmd_jobs_run, write_capable=True)

    demo = sub.add_parser("demo", help="Demo commands that show the v2 plan/receipt workflow")
    demo_sub = demo.add_subparsers(dest="demo_cmd", required=True, parser_class=_ToolArgumentParser)
    demo_read = demo_sub.add_parser("read", help="Safe read (demo)")
    demo_read.set_defaults(func=demo_cmd.cmd_demo_read, write_capable=False)
    demo_write = demo_sub.add_parser("write", help="Write with plan/receipt (demo)")
    demo_write.add_argument("--selector", default="demo-resource", help="Target selector (demo)")
    demo_write.set_defaults(func=demo_cmd.cmd_demo_write, write_capable=True)

    photos = sub.add_parser("photos", help="Photos endpoints")
    photos_sub = photos.add_subparsers(dest="photos_cmd", required=True, parser_class=_ToolArgumentParser)
    photos_list = photos_sub.add_parser("list", help="List photos")
    photos_list.add_argument("--page", type=int, default=1)
    photos_list.add_argument("--per-page", type=int, default=10)
    photos_list.add_argument("--order-by", default=None, help="latest|oldest|popular")
    photos_list.set_defaults(func=photos_cmd.cmd_photos_list, write_capable=False)
    photos_get = photos_sub.add_parser("get", help="Get a photo")
    photos_get.add_argument("--id", required=True)
    photos_get.set_defaults(func=photos_cmd.cmd_photos_get, write_capable=False)
    photos_random = photos_sub.add_parser("random", help="Get random photo(s)")
    photos_random.add_argument("--count", type=int, default=None, help="1..30")
    photos_random.add_argument("--query", default=None)
    photos_random.add_argument("--username", default=None)
    photos_random.add_argument("--orientation", default=None, help="landscape|portrait|squarish")
    photos_random.add_argument("--content-filter", default=None, help="low|high")
    photos_random.set_defaults(func=photos_cmd.cmd_photos_random, write_capable=False)
    photos_search = photos_sub.add_parser("search", help="Search photos")
    photos_search.add_argument("--query", required=True)
    photos_search.add_argument("--page", type=int, default=1)
    photos_search.add_argument("--per-page", type=int, default=10)
    photos_search.add_argument("--order-by", default=None, help="relevant|latest")
    photos_search.set_defaults(func=photos_cmd.cmd_photos_search, write_capable=False)
    photos_stats = photos_sub.add_parser("stats", help="Photo statistics")
    photos_stats.add_argument("--id", required=True)
    photos_stats.add_argument("--resolution", default=None)
    photos_stats.add_argument("--quantity", default=None)
    photos_stats.set_defaults(func=photos_cmd.cmd_photos_stats, write_capable=False)
    photos_download = photos_sub.add_parser("download", help="Download tracking + optional file download (write-capable)")
    photos_download.add_argument("--id", required=True)
    photos_download.add_argument("--dest", default=None, help="Optional file path to write")
    photos_download.add_argument("--overwrite", action="store_true", help="Allow overwriting dest file (requires --apply --yes)")
    photos_download.set_defaults(func=photos_cmd.cmd_photos_download, write_capable=True)

    collections = sub.add_parser("collections", help="Collections endpoints")
    collections_sub = collections.add_subparsers(dest="collections_cmd", required=True, parser_class=_ToolArgumentParser)
    collections_list = collections_sub.add_parser("list", help="List collections")
    collections_list.add_argument("--page", type=int, default=1)
    collections_list.add_argument("--per-page", type=int, default=10)
    collections_list.set_defaults(func=collections_cmd.cmd_collections_list, write_capable=False)
    collections_get = collections_sub.add_parser("get", help="Get a collection")
    collections_get.add_argument("--id", type=int, required=True)
    collections_get.set_defaults(func=collections_cmd.cmd_collections_get, write_capable=False)
    collections_photos = collections_sub.add_parser("photos", help="List photos in a collection")
    collections_photos.add_argument("--id", type=int, required=True)
    collections_photos.add_argument("--page", type=int, default=1)
    collections_photos.add_argument("--per-page", type=int, default=10)
    collections_photos.add_argument("--orientation", default=None, help="landscape|portrait|squarish")
    collections_photos.set_defaults(func=collections_cmd.cmd_collections_photos, write_capable=False)
    collections_related = collections_sub.add_parser("related", help="Get related collections")
    collections_related.add_argument("--id", type=int, required=True)
    collections_related.set_defaults(func=collections_cmd.cmd_collections_related, write_capable=False)

    topics = sub.add_parser("topics", help="Topics endpoints")
    topics_sub = topics.add_subparsers(dest="topics_cmd", required=True, parser_class=_ToolArgumentParser)
    topics_list = topics_sub.add_parser("list", help="List topics")
    topics_list.add_argument("--page", type=int, default=1)
    topics_list.add_argument("--per-page", type=int, default=10)
    topics_list.add_argument("--order-by", default=None, help="featured|latest|oldest|position")
    topics_list.set_defaults(func=topics_cmd.cmd_topics_list, write_capable=False)
    topics_get = topics_sub.add_parser("get", help="Get a topic")
    topics_get.add_argument("--id", required=True, help="Topic slug or id")
    topics_get.set_defaults(func=topics_cmd.cmd_topics_get, write_capable=False)
    topics_photos = topics_sub.add_parser("photos", help="List photos for a topic")
    topics_photos.add_argument("--id", required=True, help="Topic slug or id")
    topics_photos.add_argument("--page", type=int, default=1)
    topics_photos.add_argument("--per-page", type=int, default=10)
    topics_photos.add_argument("--orientation", default=None, help="landscape|portrait|squarish")
    topics_photos.set_defaults(func=topics_cmd.cmd_topics_photos, write_capable=False)

    users = sub.add_parser("users", help="Users endpoints")
    users_sub = users.add_subparsers(dest="users_cmd", required=True, parser_class=_ToolArgumentParser)
    users_get = users_sub.add_parser("get", help="Get a user profile")
    users_get.add_argument("--username", required=True)
    users_get.set_defaults(func=users_cmd.cmd_users_get, write_capable=False)
    users_photos = users_sub.add_parser("photos", help="List photos for a user")
    users_photos.add_argument("--username", required=True)
    users_photos.add_argument("--page", type=int, default=1)
    users_photos.add_argument("--per-page", type=int, default=10)
    users_photos.add_argument("--order-by", default=None)
    users_photos.add_argument("--orientation", default=None)
    users_photos.set_defaults(func=users_cmd.cmd_users_photos, write_capable=False)
    users_likes = users_sub.add_parser("likes", help="List liked photos for a user")
    users_likes.add_argument("--username", required=True)
    users_likes.add_argument("--page", type=int, default=1)
    users_likes.add_argument("--per-page", type=int, default=10)
    users_likes.add_argument("--order-by", default=None)
    users_likes.add_argument("--orientation", default=None)
    users_likes.set_defaults(func=users_cmd.cmd_users_likes, write_capable=False)

    users_collections = users_sub.add_parser("collections", help="List collections for a user")
    users_collections.add_argument("--username", required=True)
    users_collections.add_argument("--page", type=int, default=1)
    users_collections.add_argument("--per-page", type=int, default=10)
    users_collections.set_defaults(func=users_cmd.cmd_users_collections, write_capable=False)

    users_statistics = users_sub.add_parser("statistics", help="User statistics")
    users_statistics.add_argument("--username", required=True)
    users_statistics.add_argument("--resolution", default=None)
    users_statistics.add_argument("--quantity", default=None)
    users_statistics.set_defaults(func=users_cmd.cmd_users_statistics, write_capable=False)

    search = sub.add_parser("search", help="Search endpoints")
    search_sub = search.add_subparsers(dest="search_cmd", required=True, parser_class=_ToolArgumentParser)
    search_photos = search_sub.add_parser("photos", help="Search photos")
    search_photos.add_argument("--query", required=True)
    search_photos.add_argument("--page", type=int, default=1)
    search_photos.add_argument("--per-page", type=int, default=10)
    search_photos.set_defaults(func=search_cmd.cmd_search_photos, write_capable=False)
    search_collections = search_sub.add_parser("collections", help="Search collections")
    search_collections.add_argument("--query", required=True)
    search_collections.add_argument("--page", type=int, default=1)
    search_collections.add_argument("--per-page", type=int, default=10)
    search_collections.set_defaults(func=search_cmd.cmd_search_collections, write_capable=False)
    search_users = search_sub.add_parser("users", help="Search users")
    search_users.add_argument("--query", required=True)
    search_users.add_argument("--page", type=int, default=1)
    search_users.add_argument("--per-page", type=int, default=10)
    search_users.set_defaults(func=search_cmd.cmd_search_users, write_capable=False)

    export = sub.add_parser("export", help="Deterministic pagination exports (writes local JSON)")
    export_sub = export.add_subparsers(dest="export_cmd", required=True, parser_class=_ToolArgumentParser)

    def _add_export_paging_flags(sp):  # noqa: ANN001
        sp.add_argument("--out", required=True, help="Output JSON file path")
        sp.add_argument("--start-page", type=int, default=1)
        sp.add_argument("--max-pages", type=int, default=1)
        sp.add_argument("--per-page", type=int, default=10)
        sp.add_argument("--sleep-ms", type=int, default=0)

    export_photos_search = export_sub.add_parser("photos-search", help="Export /search/photos results")
    export_photos_search.add_argument("--query", required=True)
    export_photos_search.add_argument("--order-by", default=None, help="relevant|latest")
    _add_export_paging_flags(export_photos_search)
    export_photos_search.set_defaults(func=export_cmd.cmd_export_photos_search, write_capable=True)

    export_photos_list = export_sub.add_parser("photos-list", help="Export /photos list")
    export_photos_list.add_argument("--order-by", default=None, help="latest|oldest|popular")
    _add_export_paging_flags(export_photos_list)
    export_photos_list.set_defaults(func=export_cmd.cmd_export_photos_list, write_capable=True)

    export_collections_photos = export_sub.add_parser("collections-photos", help="Export /collections/:id/photos")
    export_collections_photos.add_argument("--id", type=int, required=True)
    export_collections_photos.add_argument("--orientation", default=None, help="landscape|portrait|squarish")
    _add_export_paging_flags(export_collections_photos)
    export_collections_photos.set_defaults(func=export_cmd.cmd_export_collections_photos, write_capable=True)

    export_topics_photos = export_sub.add_parser("topics-photos", help="Export /topics/:id/photos")
    export_topics_photos.add_argument("--id", required=True, help="Topic slug or id")
    export_topics_photos.add_argument("--orientation", default=None, help="landscape|portrait|squarish")
    _add_export_paging_flags(export_topics_photos)
    export_topics_photos.set_defaults(func=export_cmd.cmd_export_topics_photos, write_capable=True)

    export_users_photos = export_sub.add_parser("users-photos", help="Export /users/:username/photos")
    export_users_photos.add_argument("--username", required=True)
    export_users_photos.add_argument("--order-by", default=None)
    export_users_photos.add_argument("--orientation", default=None)
    _add_export_paging_flags(export_users_photos)
    export_users_photos.set_defaults(func=export_cmd.cmd_export_users_photos, write_capable=True)

    stats = sub.add_parser("stats", help="Global stats endpoints")
    stats_sub = stats.add_subparsers(dest="stats_cmd", required=True, parser_class=_ToolArgumentParser)
    stats_total = stats_sub.add_parser("total", help="Get total stats")
    stats_total.set_defaults(func=stats_cmd.cmd_stats_total, write_capable=False)
    stats_month = stats_sub.add_parser("month", help="Get monthly stats")
    stats_month.set_defaults(func=stats_cmd.cmd_stats_month, write_capable=False)

    return p


def _output_mode_from_argv(argv: list[str]) -> str:
    # Default is json; treat unknown/missing value as json.
    try:
        idx = argv.index("--output")
    except ValueError:
        return "json"
    if idx + 1 >= len(argv):
        return "json"
    v = str(argv[idx + 1] or "").strip()
    return v if v in {"json", "text"} else "json"


def main(argv: list[str]) -> int:
    parser = build_parser()
    out = Output(mode=_output_mode_from_argv(argv))
    try:
        args = parser.parse_args(argv)
    except ValidationError as e:
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        return 1
    except SystemExit as e:
        # `--help` and similar argparse exits. For parse errors, we raise ValidationError instead.
        try:
            return int(e.code or 0)
        except Exception:
            return 0
    write_capable = bool(getattr(args, "write_capable", False))
    run_ctx: RunContext = init_run_context(
        env_file=str(args.env_file),
        enabled=write_capable,
        run_id=str(args.run_id) if args.run_id else None,
        artifacts_dir=str(args.artifacts_dir) if args.artifacts_dir else None,
        no_artifacts=bool(args.no_artifacts),
    )
    run_audit_log_path = str(run_ctx.audit_log_path) if (run_ctx.enabled and run_ctx.audit_log_path) else None
    global_audit_log_path = str(args.log_file) if args.log_file else None

    loggers: list[AuditLogger] = []
    if run_audit_log_path:
        loggers.append(AuditLogger(path=run_audit_log_path, enabled=True))
    if global_audit_log_path:
        loggers.append(AuditLogger(path=global_audit_log_path, enabled=True))
    audit = CompositeAuditLogger(loggers) if len(loggers) > 1 else (loggers[0] if loggers else AuditLogger(path=None, enabled=False))

    runs_index_path = runs_index_path_for_env_file(str(args.env_file))
    if str(getattr(args, "cmd", "") or "") == "runs":
        # `runs` is a local-only command; it still needs to know where the index lives.
        run_ctx = RunContext(
            enabled=False,
            run_id=None,
            artifacts_dir=None,
            runs_index_path=runs_index_path,
            audit_log_path=None,
        )

    out.set_provenance(
        {
            "run_id": run_ctx.run_id,
            "artifacts_dir": str(run_ctx.artifacts_dir) if run_ctx.artifacts_dir else None,
            "runs_index": str(run_ctx.runs_index_path) if run_ctx.runs_index_path else str(runs_index_path),
            "audit_log": run_audit_log_path or global_audit_log_path,
            "audit_log_global": global_audit_log_path,
        }
    )

    try:
        if bool(args.version):
            payload = {"ok": True, "tool": "unsplash-api-tool", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"unsplash-api-tool {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        command_str = "unsplash-api-tool " + " ".join(argv)
        audit.bind_context(
            {
                "tool": "unsplash-api-tool",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "env_fingerprint": None,
                "run_id": run_ctx.run_id,
            }
        )

        # Some commands are local-only and don't need API config.
        project_cfg, cfg_base_dir = load_project_config(getattr(args, "config", None))
        project_dir = Path(str(getattr(args, "project_dir", "") or "")).expanduser()
        if not str(getattr(args, "project_dir", "") or "").strip():
            project_dir = cfg_base_dir or Path.cwd()
        project_dir = project_dir.resolve()

        if str(getattr(args, "cmd", "") or "") in {"runs", "onboarding"}:
            ctx = {
                "cfg": None,
                "out": out,
                "audit": audit,
                "tool": "unsplash-api-tool",
                "tool_version": __version__,
                "command_str": command_str,
                "env_file": str(args.env_file),
                "timeout_s": None,
                "verbose": bool(args.verbose),
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "plan_out": args.plan_out,
                "plan_in": args.plan_in,
                "receipt_out": args.receipt_out,
                "ack_irreversible": bool(args.ack_irreversible),
                "run_id": run_ctx.run_id,
                "artifacts_dir": run_ctx.artifacts_dir,
                "runs_index_path": runs_index_path,
                "project_cfg": project_cfg,
                "project_dir": str(project_dir),
            }
            rc = int(args.func(args, ctx))
            return rc

        cfg = load_config(args.env_file)
        env_fingerprint = cfg.base_url
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        http = HttpClient(timeout_s=timeout_s, verbose=bool(args.verbose), user_agent=f"unsplash-api-tool/{__version__}")
        ctx = {
            "cfg": cfg,
            "http": http,
            "client": UnsplashClient(cfg=cfg, http=http, env_file=str(args.env_file)),
            "out": out,
            "audit": audit,
            "tool": "unsplash-api-tool",
            "tool_version": __version__,
            "command_str": command_str,
            "env_file": str(args.env_file),
            "timeout_s": timeout_s,
            "verbose": bool(args.verbose),
            "apply": bool(args.apply),
            "yes": bool(args.yes),
            "ack_no_snapshot": bool(args.ack_no_snapshot),
            "plan_out": args.plan_out,
            "plan_in": args.plan_in,
            "receipt_out": args.receipt_out,
            "ack_irreversible": bool(args.ack_irreversible),
            "run_id": run_ctx.run_id,
            "artifacts_dir": run_ctx.artifacts_dir,
            "runs_index_path": run_ctx.runs_index_path,
            "audit_log_path": run_audit_log_path or global_audit_log_path,
            "audit_log_run_path": run_audit_log_path,
            "audit_log_global_path": global_audit_log_path,
            "project_cfg": project_cfg,
            "project_dir": str(project_dir),
        }

        if run_ctx.enabled and run_ctx.artifacts_dir:
            if not bool(args.apply) and not ctx.get("plan_out"):
                ctx["plan_out"] = str(run_ctx.artifacts_dir / "plan.json")
            if bool(args.apply) and not ctx.get("receipt_out"):
                ctx["receipt_out"] = str(run_ctx.artifacts_dir / "receipt.json")

        audit.bind_context(
            {
                "tool": "unsplash-api-tool",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "env_fingerprint": cfg.base_url,
                "run_id": run_ctx.run_id,
            }
        )
        rc = int(args.func(args, ctx))

        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="unsplash-api-tool",
            version=__version__,
            command=command_str,
            env_fingerprint=env_fingerprint,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )

        return rc
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    except SafetyError as e:
        # Safety refusals are "safe no-ops" (not errors).
        audit.write("refused", {"reason": str(e)})
        out.emit({"ok": True, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError"})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="unsplash-api-tool",
            version=__version__,
            command="unsplash-api-tool " + " ".join(argv),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 0
    except ToolError as e:
        audit.write("error", {"error": str(e), "error_type": type(e).__name__})
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="unsplash-api-tool",
            version=__version__,
            command="unsplash-api-tool " + " ".join(argv),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 1
    except Exception as e:  # noqa: BLE001
        if bool(args.debug):
            raise
        audit.write("error", {"error": str(e), "error_type": type(e).__name__})
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="unsplash-api-tool",
            version=__version__,
            command="unsplash-api-tool " + " ".join(argv),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 1
    finally:
        audit.close()
