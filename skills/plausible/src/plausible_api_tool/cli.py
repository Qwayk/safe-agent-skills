from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger
from .commands import auth as auth_cmd
from .commands import event as event_cmd
from .commands import report as report_cmd
from .commands import sites as sites_cmd
from .commands import stats as stats_cmd
from .config import load_config
from .http import HttpClient
from .output import Output
from .project_config import load_project_config


class ValidationError(Exception):
    pass


def _argv_output_mode(argv: list[str]) -> str:
    # Default is json.
    for i, tok in enumerate(argv):
        if tok == "--output" and i + 1 < len(argv):
            return str(argv[i + 1])
        if tok.startswith("--output="):
            return tok.split("=", 1)[1]
    return "json"


def _argv_wants_json(argv: list[str]) -> bool:
    return _argv_output_mode(argv) != "text"


def build_parser() -> argparse.ArgumentParser:
    class _JsonAwareParser(argparse.ArgumentParser):
        def parse_args(self, args=None, namespace=None):  # type: ignore[override]
            self._raw_args = list(args) if args is not None else sys.argv[1:]
            return super().parse_args(args=args, namespace=namespace)

        def error(self, message: str) -> None:  # type: ignore[override]
            raw = getattr(self, "_raw_args", sys.argv[1:])
            if _argv_wants_json(list(raw)):
                raise ValidationError(message)
            super().error(message)

    p = _JsonAwareParser(prog="plausible-api-tool")
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
        help="Optional project root dir for outputs. If omitted and --config is provided, defaults to the config file's directory; otherwise defaults to the current working directory.",
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
    p.add_argument("--plan-out", default=None, help="Write computed plan JSON to a file (v2)")
    p.add_argument("--receipt-out", default=None, help="Write receipt JSON to a file after apply (v2)")
    p.add_argument("--ack-irreversible", action="store_true", help="Additional acknowledgement for irreversible actions (v2)")

    sub = p.add_subparsers(dest="cmd", required=True)

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True)
    auth_check = auth_sub.add_parser("check", help="Smoke test credentials")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check)

    stats = sub.add_parser("stats", help="Plausible Stats API (read-only)")
    stats_sub = stats.add_subparsers(dest="stats_cmd", required=True)

    stats_query = stats_sub.add_parser("query", help="POST /api/v2/query with a JSON payload")
    stats_query.add_argument("--file", default=None, help="Query JSON file path")
    stats_query.add_argument("--query", default=None, help="Query JSON string")
    stats_query.add_argument("--stdin", action="store_true", default=False, help="Read query JSON from stdin")
    stats_query.set_defaults(func=stats_cmd.cmd_stats_query)

    stats_validate = stats_sub.add_parser("validate", help="Validate a Stats API v2 query JSON file")
    stats_validate.add_argument("--file", required=True, help="Query JSON file path")
    stats_validate.set_defaults(func=stats_cmd.cmd_stats_validate)

    pages = stats_sub.add_parser("pages", help="Page breakdown helpers")
    pages_sub = pages.add_subparsers(dest="pages_cmd", required=True)
    pages_top = pages_sub.add_parser("top", help="Top pages by a metric")
    pages_top.add_argument("--metric", default="pageviews", help="Metric name (default: pageviews)")
    pages_top.add_argument("--days", type=int, default=30, help="Lookback days (default: 30)")
    pages_top.add_argument("--date-range", default=None, help="Override Plausible date_range (e.g. 30d)")
    pages_top.add_argument("--limit", type=int, default=50, help="Rows per page (default: 50)")
    pages_top.add_argument("--offset", type=int, default=0, help="Pagination offset (default: 0)")
    pages_top.add_argument("--all", action="store_true", default=False, help="Fetch all pages (auto pagination)")
    pages_top.add_argument("--no-visitors", action="store_false", dest="include_visitors", help="Do not include visitors")
    pages_top.set_defaults(func=stats_cmd.cmd_stats_pages_top)

    sources = stats_sub.add_parser("sources", help="Acquisition/source breakdown helpers")
    sources.add_argument(
        "--dimension",
        required=True,
        choices=(
            "visit:source",
            "visit:channel",
            "visit:referrer",
            "visit:utm_source",
            "visit:utm_medium",
            "visit:utm_campaign",
            "visit:utm_content",
            "visit:utm_term",
        ),
        help="Dimension to break down by",
    )
    sources.add_argument("--metric", default="visitors", help="Metric to sort by (default: visitors)")
    sources.add_argument("--days", type=int, default=30, help="Lookback days (default: 30)")
    sources.add_argument("--date-range", default=None, help="Override Plausible date_range (e.g. 30d)")
    sources.add_argument("--limit", type=int, default=50, help="Rows per page (default: 50)")
    sources.add_argument("--offset", type=int, default=0, help="Pagination offset (default: 0)")
    sources.add_argument("--all", action="store_true", default=False, help="Fetch all pages (auto pagination)")
    sources.set_defaults(func=stats_cmd.cmd_stats_sources)

    referrers = stats_sub.add_parser("referrers", help="Top referrers")
    referrers.add_argument("--metric", default="visitors", help="Metric to sort by (default: visitors)")
    referrers.add_argument("--days", type=int, default=30, help="Lookback days (default: 30)")
    referrers.add_argument("--date-range", default=None, help="Override Plausible date_range (e.g. 30d)")
    referrers.add_argument("--limit", type=int, default=50, help="Rows per page (default: 50)")
    referrers.add_argument("--offset", type=int, default=0, help="Pagination offset (default: 0)")
    referrers.add_argument("--all", action="store_true", default=False, help="Fetch all pages (auto pagination)")
    referrers.set_defaults(func=stats_cmd.cmd_stats_referrers)

    entry_exit = stats_sub.add_parser("entry-exit", help="Entry/exit page breakdown")
    entry_exit.add_argument("--type", choices=("entry", "exit", "both"), default="both", help="Which breakdown to fetch")
    entry_exit.add_argument("--days", type=int, default=30, help="Lookback days (default: 30)")
    entry_exit.add_argument("--date-range", default=None, help="Override Plausible date_range (e.g. 30d)")
    entry_exit.add_argument("--limit", type=int, default=50, help="Rows per page (default: 50)")
    entry_exit.add_argument("--offset", type=int, default=0, help="Pagination offset (default: 0)")
    entry_exit.add_argument("--all", action="store_true", default=False, help="Fetch all pages (auto pagination)")
    entry_exit.set_defaults(func=stats_cmd.cmd_stats_entry_exit)

    devices = stats_sub.add_parser("devices", help="Device/browser/OS breakdown")
    devices.add_argument("--dimension", choices=("visit:device", "visit:browser", "visit:os"), default="visit:device")
    devices.add_argument("--days", type=int, default=30, help="Lookback days (default: 30)")
    devices.add_argument("--date-range", default=None, help="Override Plausible date_range (e.g. 30d)")
    devices.add_argument("--limit", type=int, default=50, help="Rows per page (default: 50)")
    devices.add_argument("--offset", type=int, default=0, help="Pagination offset (default: 0)")
    devices.add_argument("--all", action="store_true", default=False, help="Fetch all pages (auto pagination)")
    devices.set_defaults(func=stats_cmd.cmd_stats_devices)

    goals = stats_sub.add_parser("goals", help="Goal-centric helpers")
    goals_sub = goals.add_subparsers(dest="goals_cmd", required=True)

    goals_list = goals_sub.add_parser("list", help="List goals by conversions")
    goals_list.add_argument("--date-range", default="30d", help="Date range (default: 30d)")
    goals_list.add_argument("--limit", default=50, type=int, help="Limit rows (default: 50)")
    goals_list.add_argument("--offset", default=0, type=int, help="Pagination offset (default: 0)")
    goals_list.add_argument("--all", action="store_true", default=False, help="Fetch all pages (auto pagination)")
    goals_list.set_defaults(func=stats_cmd.cmd_stats_goals_list)

    goals_ts = goals_sub.add_parser("timeseries", help="Goal conversions per day")
    goals_ts.add_argument("--goal", required=True, help="Goal display name (exact)")
    goals_ts.add_argument("--date-range", default="30d", help="Date range (default: 30d)")
    goals_ts.set_defaults(func=stats_cmd.cmd_stats_goals_timeseries)

    goals_breakdown = goals_sub.add_parser("breakdown", help="Break down a goal by a custom property")
    goals_breakdown.add_argument("--goal", required=True, help="Goal display name (exact)")
    goals_breakdown.add_argument("--prop", required=True, help="Custom prop name (without event:props:)")
    goals_breakdown.add_argument("--date-range", default="30d", help="Date range (default: 30d)")
    goals_breakdown.add_argument("--limit", default=50, type=int, help="Limit rows (default: 50)")
    goals_breakdown.add_argument("--offset", default=0, type=int, help="Pagination offset (default: 0)")
    goals_breakdown.add_argument("--all", action="store_true", default=False, help="Fetch all pages (auto pagination)")
    goals_breakdown.set_defaults(func=stats_cmd.cmd_stats_goals_breakdown)

    goal = stats_sub.add_parser("goal", help="Goal + custom event power tools")
    goal_sub = goal.add_subparsers(dest="goal_cmd", required=True)
    goal_breakdown = goal_sub.add_parser("breakdown", help="Break down a goal by a custom property")
    goal_breakdown.add_argument("--goal", required=True, help="Goal display name (exact)")
    goal_breakdown.add_argument("--prop", required=True, help="Custom prop name (without event:props:)")
    goal_breakdown.add_argument("--days", type=int, default=30, help="Lookback days (default: 30)")
    goal_breakdown.add_argument("--date-range", default=None, help="Override Plausible date_range (e.g. 30d)")
    goal_breakdown.add_argument("--limit", type=int, default=50, help="Rows per page (default: 50)")
    goal_breakdown.add_argument("--offset", type=int, default=0, help="Pagination offset (default: 0)")
    goal_breakdown.add_argument("--all", action="store_true", default=False, help="Fetch all pages (auto pagination)")
    goal_breakdown.set_defaults(func=stats_cmd.cmd_stats_goal_breakdown)

    goal_pages = goal_sub.add_parser("pages", help="Which pages generate a goal")
    goal_pages.add_argument("--goal", required=True, help="Goal display name (exact)")
    goal_pages.add_argument("--days", type=int, default=30, help="Lookback days (default: 30)")
    goal_pages.add_argument("--date-range", default=None, help="Override Plausible date_range (e.g. 30d)")
    goal_pages.add_argument("--limit", type=int, default=50, help="Rows per page (default: 50)")
    goal_pages.add_argument("--offset", type=int, default=0, help="Pagination offset (default: 0)")
    goal_pages.add_argument("--all", action="store_true", default=False, help="Fetch all pages (auto pagination)")
    goal_pages.set_defaults(func=stats_cmd.cmd_stats_goal_pages)

    funnel = stats_sub.add_parser("funnel", help="Funnel helpers")
    funnel_sub = funnel.add_subparsers(dest="funnel_cmd", required=True)
    funnel_members = funnel_sub.add_parser("members", help="Membership funnel summary (common membership goals)")
    funnel_members.add_argument("--days", type=int, default=30, help="Lookback days (default: 30)")
    funnel_members.add_argument("--date-range", default=None, help="Override Plausible date_range (e.g. 30d)")
    funnel_members.set_defaults(func=stats_cmd.cmd_stats_funnel_members)

    compare = stats_sub.add_parser("compare", help="Compare a query over two time ranges")
    compare.add_argument("--file", required=True, help="Base query JSON file path")
    compare.add_argument("--range", required=True, help="Range string like 7d, 30d")
    compare.add_argument("--compare", choices=("previous",), default="previous", help="Comparison mode (default: previous)")
    compare.set_defaults(func=stats_cmd.cmd_stats_compare)

    event = sub.add_parser("event", help="Plausible Events API (write; disabled by default)")
    event_sub = event.add_subparsers(dest="event_cmd", required=True)
    event_send = event_sub.add_parser("send", help="POST /api/event (requires --apply --yes)")
    event_send.add_argument("--name", required=True, help="Event name")
    event_send.add_argument("--url", required=True, help="Page URL to associate with the event")
    event_send.add_argument("--domain", default=None, help="Domain (defaults to PLAUSIBLE_SITE_ID)")
    event_send.add_argument("--referrer", default=None, help="Optional referrer URL")
    event_send.add_argument("--revenue-currency", default=None, help="Optional revenue currency (ISO 4217)")
    event_send.add_argument("--revenue-amount", default=None, help="Optional revenue amount (string; keep exact)")
    event_send.add_argument(
        "--allow-non-default-domain",
        action="store_true",
        default=False,
        help="Allow --domain to differ from PLAUSIBLE_SITE_ID (extra safety gate).",
    )
    event_send.add_argument(
        "--allow-url-host-mismatch",
        action="store_true",
        default=False,
        help="Allow URL host to not match the event domain (extra safety gate).",
    )
    event_send.add_argument(
        "--prop",
        action="append",
        nargs=2,
        metavar=("KEY", "VALUE"),
        default=[],
        help="Custom property key/value (repeatable)",
    )
    event_send.add_argument(
        "--interactive",
        action="store_true",
        default=False,
        help="Mark event as interactive (affects bounce rate). Default: false.",
    )
    event_send.add_argument(
        "--verify",
        action="store_true",
        default=False,
        help="Best-effort verification by querying Stats API for the URL path right after sending.",
    )
    event_send.add_argument(
        "--verify-wait-s",
        type=float,
        default=8.0,
        help="Max seconds to wait while verifying (default: 8).",
    )
    event_send.set_defaults(func=event_cmd.cmd_event_send)

    site = sub.add_parser("site", help="Plausible Sites API v1 (safe reads + gated writes)")
    site_sub = site.add_subparsers(dest="site_cmd", required=True)

    site_list = site_sub.add_parser("list", help="List sites")
    site_list.add_argument("--after", default=None, help="Pagination cursor (after)")
    site_list.add_argument("--before", default=None, help="Pagination cursor (before)")
    site_list.add_argument("--limit", type=int, default=100, help="Pagination limit (default: 100)")
    site_list.add_argument("--team-id", default=None, help="Optional team ID to scope results")
    site_list.set_defaults(func=sites_cmd.cmd_site_list)

    site_get = site_sub.add_parser("get", help="Get site details")
    site_get.add_argument("--site-id", default=None, help="Site ID (domain). Defaults to PLAUSIBLE_SITE_ID.")
    site_get.set_defaults(func=sites_cmd.cmd_site_get)

    site_create = site_sub.add_parser("create", help="Create a site (requires --apply --yes)")
    site_create.add_argument("--domain", required=True, help="Site domain to create (unique)")
    site_create.add_argument("--timezone", default=None, help="IANA timezone name (default: Etc/UTC)")
    site_create.add_argument("--team-id", default=None, help="Optional team ID (defaults to 'My Personal Sites')")
    site_create.add_argument("--tracker-config", default=None, help="Tracker script config JSON object string (optional)")
    site_create.add_argument("--tracker-config-file", default=None, help="Tracker script config JSON file path (optional)")
    site_create.set_defaults(func=sites_cmd.cmd_site_create)

    site_update = site_sub.add_parser("update", help="Update a site (requires --apply --yes)")
    site_update.add_argument("--site-id", default=None, help="Site ID (domain). Defaults to PLAUSIBLE_SITE_ID.")
    site_update.add_argument("--domain", default=None, help="New domain (optional)")
    site_update.add_argument("--tracker-config", default=None, help="Tracker script config JSON object string (optional)")
    site_update.add_argument("--tracker-config-file", default=None, help="Tracker script config JSON file path (optional)")
    site_update.set_defaults(func=sites_cmd.cmd_site_update)

    site_delete = site_sub.add_parser("delete", help="Delete a site (requires --apply --yes --ack-irreversible)")
    site_delete.add_argument("--site-id", default=None, help="Site ID (domain). Defaults to PLAUSIBLE_SITE_ID.")
    site_delete.set_defaults(func=sites_cmd.cmd_site_delete)

    teams = site_sub.add_parser("teams", help="Teams")
    teams_sub = teams.add_subparsers(dest="teams_cmd", required=True)
    teams_list = teams_sub.add_parser("list", help="List teams")
    teams_list.set_defaults(func=sites_cmd.cmd_site_teams_list)

    shared_links = site_sub.add_parser("shared-links", help="Shared links (Sites API)")
    shared_links_sub = shared_links.add_subparsers(dest="shared_links_cmd", required=True)
    shared_links_ensure = shared_links_sub.add_parser("ensure", help="Ensure a shared link exists (idempotent)")
    shared_links_ensure.add_argument("--site-id", default=None, help="Site ID (domain). Defaults to PLAUSIBLE_SITE_ID.")
    shared_links_ensure.add_argument("--name", required=True, help="Shared link name")
    shared_links_ensure.set_defaults(func=sites_cmd.cmd_site_shared_links_ensure)

    goals = site_sub.add_parser("goals", help="Goals (Sites API)")
    goals_sub = goals.add_subparsers(dest="goals_cmd", required=True)
    goals_list = goals_sub.add_parser("list", help="List goals")
    goals_list.add_argument("--site-id", default=None, help="Site ID (domain). Defaults to PLAUSIBLE_SITE_ID.")
    goals_list.add_argument("--after", default=None, help="Pagination cursor (after)")
    goals_list.add_argument("--before", default=None, help="Pagination cursor (before)")
    goals_list.add_argument("--limit", type=int, default=100, help="Pagination limit (default: 100)")
    goals_list.set_defaults(func=sites_cmd.cmd_site_goals_list)

    goals_ensure = goals_sub.add_parser("ensure", help="Find or create a goal (idempotent; requires --apply --yes)")
    goals_ensure.add_argument("--site-id", default=None, help="Site ID (domain). Defaults to PLAUSIBLE_SITE_ID.")
    goals_ensure.add_argument("--goal-type", required=True, choices=("event", "page"), help="Goal type")
    goals_ensure.add_argument("--event-name", default=None, help="Event name (required for event goals)")
    goals_ensure.add_argument("--page-path", default=None, help="Page path (required for page goals; wildcards allowed)")
    goals_ensure.add_argument("--display-name", default=None, help="Optional display name shown in the dashboard")
    goals_ensure.set_defaults(func=sites_cmd.cmd_site_goals_ensure)

    goals_delete = goals_sub.add_parser("delete", help="Delete a goal (requires --apply --yes --ack-irreversible)")
    goals_delete.add_argument("--site-id", default=None, help="Site ID (domain). Defaults to PLAUSIBLE_SITE_ID.")
    goals_delete.add_argument("--goal-id", required=True, help="Goal ID")
    goals_delete.set_defaults(func=sites_cmd.cmd_site_goals_delete)

    custom_props = site_sub.add_parser("custom-props", help="Custom properties (Sites API)")
    custom_props_sub = custom_props.add_subparsers(dest="custom_props_cmd", required=True)
    custom_props_list = custom_props_sub.add_parser("list", help="List custom properties")
    custom_props_list.add_argument("--site-id", default=None, help="Site ID (domain). Defaults to PLAUSIBLE_SITE_ID.")
    custom_props_list.set_defaults(func=sites_cmd.cmd_site_custom_props_list)

    custom_props_ensure = custom_props_sub.add_parser("ensure", help="Create a custom property (idempotent; requires --apply --yes)")
    custom_props_ensure.add_argument("--site-id", default=None, help="Site ID (domain). Defaults to PLAUSIBLE_SITE_ID.")
    custom_props_ensure.add_argument("--property", required=True, help="Property name")
    custom_props_ensure.set_defaults(func=sites_cmd.cmd_site_custom_props_ensure)

    custom_props_delete = custom_props_sub.add_parser("delete", help="Delete a custom property (requires --apply --yes --ack-irreversible)")
    custom_props_delete.add_argument("--site-id", default=None, help="Site ID (domain). Defaults to PLAUSIBLE_SITE_ID.")
    custom_props_delete.add_argument("--property", required=True, help="Property name")
    custom_props_delete.set_defaults(func=sites_cmd.cmd_site_custom_props_delete)

    guests = site_sub.add_parser("guests", help="Guests (Sites API)")
    guests_sub = guests.add_subparsers(dest="guests_cmd", required=True)
    guests_list = guests_sub.add_parser("list", help="List guests")
    guests_list.add_argument("--site-id", default=None, help="Site ID (domain). Defaults to PLAUSIBLE_SITE_ID.")
    guests_list.add_argument("--after", default=None, help="Pagination cursor (after)")
    guests_list.add_argument("--before", default=None, help="Pagination cursor (before)")
    guests_list.add_argument("--limit", type=int, default=100, help="Pagination limit (default: 100)")
    guests_list.set_defaults(func=sites_cmd.cmd_site_guests_list)

    guests_ensure = guests_sub.add_parser("ensure", help="Invite or add a guest (idempotent; requires --apply --yes)")
    guests_ensure.add_argument("--site-id", default=None, help="Site ID (domain). Defaults to PLAUSIBLE_SITE_ID.")
    guests_ensure.add_argument("--email", required=True, help="Guest email")
    guests_ensure.add_argument("--role", required=True, choices=("viewer", "editor"), help="Guest role")
    guests_ensure.set_defaults(func=sites_cmd.cmd_site_guests_ensure)

    guests_delete = guests_sub.add_parser("delete", help="Delete a guest membership/invite (requires --apply --yes --ack-irreversible)")
    guests_delete.add_argument("--site-id", default=None, help="Site ID (domain). Defaults to PLAUSIBLE_SITE_ID.")
    guests_delete.add_argument("--email", required=True, help="Guest email")
    guests_delete.set_defaults(func=sites_cmd.cmd_site_guests_delete)

    report = sub.add_parser("report", help="Opinionated read-only reports (Stats API)")
    report_sub = report.add_subparsers(dest="report_cmd", required=True)
    weekly = report_sub.add_parser("weekly", help="Weekly snapshot (top pages/sources/goals + membership funnel)")
    weekly.add_argument("--days", type=int, default=7, help="Lookback days (default: 7)")
    weekly.add_argument("--limit", type=int, default=50, help="Rows per breakdown (default: 50)")
    weekly.add_argument("--out-dir", default=None, help="Optional output directory for CSV exports")
    weekly.set_defaults(func=report_cmd.cmd_report_weekly)

    membership = report_sub.add_parser("membership", help="Membership-focused snapshot")
    membership.add_argument("--days", type=int, default=30, help="Lookback days (default: 30)")
    membership.add_argument("--limit", type=int, default=50, help="Rows per breakdown (default: 50)")
    membership.add_argument("--out-dir", default=None, help="Optional output directory for CSV exports")
    membership.set_defaults(func=report_cmd.cmd_report_membership)

    return p


def main(argv: list[str]) -> int:
    pre_out = Output(mode=_argv_output_mode(argv))

    if "--version" in argv or any(a.startswith("--version=") for a in argv):
        if _argv_wants_json(argv):
            pre_out.emit({"ok": True, "tool": "plausible-api-tool", "version": __version__})
        else:
            pre_out.emit(f"plausible-api-tool {__version__}")
        return 0

    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except ValidationError as e:
        pre_out.emit({"ok": False, "error": str(e), "error_type": "ValidationError"})
        return 2

    out = Output(mode=args.output)
    audit = AuditLogger(path=args.log_file, enabled=bool(args.log_file))

    try:
        if bool(getattr(args, "version", False)):
            if _argv_wants_json(argv):
                out.emit({"ok": True, "tool": "plausible-api-tool", "version": __version__})
            else:
                out.emit(f"plausible-api-tool {__version__}")
            return 0

        cfg = load_config(args.env_file)
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        http = HttpClient(timeout_s=timeout_s, verbose=bool(args.verbose), user_agent=f"plausible-api-tool/{__version__}")
        project_cfg, cfg_base_dir = load_project_config(getattr(args, "config", None))
        project_dir = Path(str(getattr(args, "project_dir", "") or "")).expanduser()
        if not str(getattr(args, "project_dir", "") or "").strip():
            project_dir = cfg_base_dir or Path.cwd()
        project_dir = project_dir.resolve()
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "env_file": str(args.env_file),
            "timeout_s": timeout_s,
            "verbose": bool(args.verbose),
            "apply": bool(args.apply),
            "yes": bool(args.yes),
            "ack_no_snapshot": bool(args.ack_no_snapshot),
            "plan_out": str(args.plan_out) if getattr(args, "plan_out", None) else None,
            "receipt_out": str(args.receipt_out) if getattr(args, "receipt_out", None) else None,
            "ack_irreversible": bool(getattr(args, "ack_irreversible", False)),
            "http": http,
            "project_cfg": project_cfg,
            "project_dir": str(project_dir),
        }
        return int(args.func(args, ctx))
    except KeyboardInterrupt:
        if _argv_wants_json(argv):
            out.emit({"ok": False, "error": "Interrupted", "error_type": "KeyboardInterrupt"})
        else:
            print("Interrupted.", file=sys.stderr)
        return 130
    except Exception as e:  # noqa: BLE001
        if bool(args.debug):
            raise
        audit.write("error", {"error": str(e), "error_type": type(e).__name__})
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        return 1
    finally:
        audit.close()
