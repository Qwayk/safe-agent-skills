from __future__ import annotations

import argparse
import time
import sys
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import auth as auth_cmd
from .commands import accounts as accounts_cmd
from .commands import feeds as feeds_cmd
from .commands import linkbuilder as linkbuilder_cmd
from .commands import onboarding as onboarding_cmd
from .commands import offers as offers_cmd
from .commands import proof_of_purchase as proof_of_purchase_cmd
from .commands import programs as programs_cmd
from .commands import reports as reports_cmd
from .commands import transaction_queries as transaction_queries_cmd
from .commands import transactions as transactions_cmd
from .config import load_config
from .errors import SafetyError, ToolError, ValidationError
from .http import HttpClient
from .output import Output
from .runs import RunContext, build_deterministic_summary, init_run_context, find_run, list_runs, runs_index_path_for_env_file, write_summary_md, append_index_row

_TOOL = "awin-publisher-safe-cli"


class _ToolArgumentParser(argparse.ArgumentParser):
    """
    Keep parser errors as clean JSON while still preserving the local CLI contract.
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
        artifacts_dir = row.get("artifacts_dir")
        if isinstance(artifacts_dir, str) and artifacts_dir:
            summary_path = Path(artifacts_dir) / "summary.md"
            if summary_path.exists():
                summary = summary_path.read_text(encoding="utf-8")
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

    summary_lines = build_deterministic_summary(
        tool=tool,
        version=version,
        run_id=run_ctx.run_id,
        env_fingerprint=env_fingerprint,
        command=command,
        output_obj=output_obj,
        plan_path=None,
        receipt_path=None,
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
            "plan_path": None,
            "receipt_path": None,
            "audit_log": audit_log_path,
            "audit_log_global": audit_log_global_path,
        },
    )


def _user_agent(version: str) -> str:
    return f"{_TOOL}/{version}"


def _output_mode_from_argv(argv: list[str]) -> str:
    try:
        idx = argv.index("--output")
    except ValueError:
        return "json"
    if idx + 1 >= len(argv):
        return "json"
    v = str(argv[idx + 1] or "").strip()
    return v if v in {"json", "text"} else "json"


def build_parser() -> argparse.ArgumentParser:
    p = _ToolArgumentParser(prog=_TOOL)
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    p.add_argument("--debug", action="store_true", help="Show stack traces on errors")
    p.add_argument("--output", choices=("json", "text"), default="json", help="Output format (default: json)")
    p.add_argument("--log-file", default=None, help="Optional audit log path (JSONL)")
    p.add_argument("--apply", action="store_true", help="Apply remote changes (default is dry-run for write commands)")
    p.add_argument("--yes", action="store_true", help="Additional confirmation for risky or batch write commands")
    p.add_argument("--plan-out", default=None, help="Optional path to write a dry-run plan JSON")
    p.add_argument("--plan-in", default=None, help="Optional plan JSON to validate before apply")
    p.add_argument("--receipt-out", default=None, help="Optional path to write an apply receipt JSON")
    p.add_argument("--run-id", default=None, help="Optional run id (for run history/audit)")
    p.add_argument("--artifacts-dir", default=None, help="Optional artifacts directory for this run")
    p.add_argument("--no-artifacts", action="store_true", help="Disable writing run artifacts")

    sub = p.add_subparsers(dest="cmd", required=False, parser_class=_ToolArgumentParser)

    runs = sub.add_parser("runs", help="Run history (local only)")
    runs_sub = runs.add_subparsers(dest="runs_cmd", required=True, parser_class=_ToolArgumentParser)
    runs_list = runs_sub.add_parser("list", help="List recent runs")
    runs_list.add_argument("--limit", type=int, default=20, help="Max runs to return (default: 20)")
    runs_list.set_defaults(func=_cmd_runs_list, write_capable=False)

    runs_show = runs_sub.add_parser("show", help="Show one run from the index")
    runs_show.add_argument("--run-id", required=True, help="Run id to show")
    runs_show.set_defaults(func=_cmd_runs_show, write_capable=False)

    onboarding = sub.add_parser("onboarding", help="First-time setup help (no secrets)")
    onboarding.add_argument("--no-write-env", action="store_true", help="Do not write/update the env file; print instructions only")
    onboarding.set_defaults(func=onboarding_cmd.cmd_onboarding, write_capable=False)

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Validate AWIN_API_TOKEN against GET /accounts")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=False)

    accounts = sub.add_parser("accounts", help="Read-only account lists")
    accounts_sub = accounts.add_subparsers(dest="accounts_cmd", required=True, parser_class=_ToolArgumentParser)
    accounts_list = accounts_sub.add_parser("list", help="List publisher accounts only")
    accounts_list.set_defaults(func=accounts_cmd.cmd_accounts_list, write_capable=False)

    programs = sub.add_parser("programs", help="Read-only publisher program lookup")
    programs_sub = programs.add_subparsers(dest="programs_cmd", required=True, parser_class=_ToolArgumentParser)
    programs_list = programs_sub.add_parser("list", help="List programs for a publisher")
    programs_list.add_argument("--publisher-id", required=True, help="Publisher ID for the programs lookup")
    programs_list.add_argument(
        "--relationship",
        default=None,
        help="Optional relationship filter: joined, pending, suspended, rejected, notjoined",
    )
    programs_list.add_argument("--country-code", default=None, help="Optional two-letter ISO Alpha-2 country code")
    programs_list.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden programs when --relationship is not set",
    )
    programs_list.set_defaults(func=programs_cmd.cmd_programs_list, write_capable=False)

    programs_details = programs_sub.add_parser("details", help="Get program details by advertiser")
    programs_details.add_argument("--publisher-id", required=True, help="Publisher ID for the program lookup")
    programs_details.add_argument("--advertiser-id", required=True, help="Advertiser ID for details")
    programs_details.add_argument(
        "--relationship",
        default=None,
        help="Optional relationship filter: joined, pending, suspended, rejected, notjoined, any",
    )
    programs_details.set_defaults(func=programs_cmd.cmd_programs_details, write_capable=False)

    offers = sub.add_parser("offers", help="Read-only publisher offers")
    offers_sub = offers.add_subparsers(dest="offers_cmd", required=True, parser_class=_ToolArgumentParser)
    offers_list = offers_sub.add_parser("list", help="Retrieve publisher offers")
    offers_list.add_argument("--publisher-id", required=True, help="Publisher ID for the offers lookup")
    offers_list.add_argument("--advertiser-ids", default=None, help="Optional comma-separated advertiser ids")
    offers_list.add_argument("--exclusive-only", action="store_true", help="Limit to exclusive offers only")
    offers_list.add_argument("--membership", default=None, help="Optional membership filter: joined, notJoined, all")
    offers_list.add_argument("--region-codes", default=None, help="Optional comma-separated ISO Alpha-2 region codes")
    offers_list.add_argument("--status", default=None, help="Optional status filter: active, expiringSoon, upcoming")
    offers_list.add_argument("--type", dest="offer_type", default=None, help="Optional type filter: promotion, voucher, all")
    offers_list.add_argument("--updated-since", default=None, help="Optional YYYY-MM-DD filter for changed offers")
    offers_list.add_argument("--page", type=int, default=None, help="Optional offers page number")
    offers_list.add_argument("--page-size", type=int, default=None, help="Optional offers page size (10-200)")
    offers_list.set_defaults(func=offers_cmd.cmd_offers_list, write_capable=False)

    transactions = sub.add_parser("transactions", help="Read-only publisher transactions")
    transactions_sub = transactions.add_subparsers(dest="transactions_cmd", required=True, parser_class=_ToolArgumentParser)
    transactions_list = transactions_sub.add_parser("list", help="List transactions for a publisher and time range")
    transactions_list.add_argument("--publisher-id", required=True, help="Publisher ID for the transactions lookup")
    transactions_list.add_argument("--start-date", required=True, help="Start date-time in ISO 8601 format")
    transactions_list.add_argument("--end-date", required=True, help="End date-time in ISO 8601 format")
    transactions_list.add_argument("--timezone", default="UTC", help="Timezone for the report (default: UTC)")
    transactions_list.add_argument("--date-type", default="transaction", help="transaction, validation, or amendment")
    transactions_list.add_argument("--advertiser-ids", default=None, help="Optional comma-separated advertiser ids")
    transactions_list.add_argument("--status", default=None, help="Optional status filter: pending, approved, declined, deleted")
    transactions_list.add_argument("--show-basket-products", action="store_true", help="Include basketProducts when shared by the advertiser")
    transactions_list.set_defaults(func=transactions_cmd.cmd_transactions_list, write_capable=False)

    transactions_by_ids = transactions_sub.add_parser("by-ids", help="Get transactions by transaction ids")
    transactions_by_ids.add_argument("--publisher-id", required=True, help="Publisher ID for the transactions lookup")
    transactions_by_ids.add_argument("--ids", required=True, help="Comma-separated transaction ids")
    transactions_by_ids.add_argument("--timezone", default="UTC", help="Timezone for the response (default: UTC)")
    transactions_by_ids.add_argument("--show-basket-products", action="store_true", help="Include basketProducts when shared by the advertiser")
    transactions_by_ids.set_defaults(func=transactions_cmd.cmd_transactions_by_ids, write_capable=False)

    transaction_queries = sub.add_parser("transaction-queries", help="Read-only publisher transaction queries")
    transaction_queries_sub = transaction_queries.add_subparsers(dest="transaction_queries_cmd", required=True, parser_class=_ToolArgumentParser)
    transaction_queries_list = transaction_queries_sub.add_parser("list", help="List transaction queries for a time range")
    transaction_queries_list.add_argument("--publisher-id", required=True, help="Publisher ID for the query lookup")
    transaction_queries_list.add_argument("--start-date", required=True, help="Start date-time in ISO 8601 format")
    transaction_queries_list.add_argument("--end-date", required=True, help="End date-time in ISO 8601 format")
    transaction_queries_list.add_argument("--timezone", default="UTC", help="Timezone for the report (default: UTC)")
    transaction_queries_list.add_argument("--date-type", default="transactionDate", help="enquiryDate, transactionDate, or validationDate")
    transaction_queries_list.add_argument("--advertiser-ids", default=None, help="Optional comma-separated advertiser ids")
    transaction_queries_list.add_argument("--click-refs", default=None, help="Optional comma-separated click refs")
    transaction_queries_list.add_argument("--statuses", default=None, help="Optional comma-separated statuses: pending, approved, declined")
    transaction_queries_list.add_argument("--page-number", type=int, default=1, help="Page number (default: 1)")
    transaction_queries_list.add_argument("--page-size", type=int, default=100, help="Page size (default: 100, max: 500)")
    transaction_queries_list.set_defaults(func=transaction_queries_cmd.cmd_transaction_queries_list, write_capable=False)

    reports = sub.add_parser("reports", help="Publisher performance reports")
    reports_sub = reports.add_subparsers(dest="reports_cmd", required=True, parser_class=_ToolArgumentParser)

    reports_advertiser = reports_sub.add_parser("advertiser", help="Advertiser performance report")
    reports_advertiser.add_argument("--publisher-id", required=True, help="Publisher ID for the report")
    reports_advertiser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format")
    reports_advertiser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format")
    reports_advertiser.add_argument("--region", required=True, help="Advertiser region code like GB or US")
    reports_advertiser.add_argument("--timezone", default="UTC", help="Timezone for the report (default: UTC)")
    reports_advertiser.add_argument("--date-type", default="transaction", help="transaction or validation")
    reports_advertiser.set_defaults(func=reports_cmd.cmd_reports_advertiser, write_capable=False)

    reports_campaign = reports_sub.add_parser("campaign", help="Campaign performance report")
    reports_campaign.add_argument("--publisher-id", required=True, help="Publisher ID for the report")
    reports_campaign.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format")
    reports_campaign.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format")
    reports_campaign.add_argument("--region", required=True, help="Advertiser region code like GB or US")
    reports_campaign.add_argument("--timezone", default="UTC", help="Timezone for the report (default: UTC)")
    reports_campaign.add_argument("--date-type", default="transaction", help="transaction or validation")
    reports_campaign.add_argument("--advertiser-ids", default=None, help="Optional comma-separated advertiser ids")
    reports_campaign.add_argument("--campaign", default=None, help="Optional campaign prefix filter (3-128 chars)")
    reports_campaign.add_argument("--include-numbers-without-campaign", action="store_true", help="Include data with no campaign value")
    reports_campaign.add_argument("--interval", default=None, help="Optional interval: day, month, or year")
    reports_campaign.set_defaults(func=reports_cmd.cmd_reports_campaign, write_capable=False)

    reports_creative = reports_sub.add_parser("creative", help="Creative performance report")
    reports_creative.add_argument("--publisher-id", required=True, help="Publisher ID for the report")
    reports_creative.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format")
    reports_creative.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format")
    reports_creative.add_argument("--region", required=True, help="Advertiser region code like GB or US")
    reports_creative.add_argument("--timezone", default="UTC", help="Timezone for the report (default: UTC)")
    reports_creative.add_argument("--date-type", default="transaction", help="transaction or validation")
    reports_creative.set_defaults(func=reports_cmd.cmd_reports_creative, write_capable=False)

    linkbuilder = sub.add_parser("linkbuilder", help="Publisher tracking link tools")
    linkbuilder_sub = linkbuilder.add_subparsers(dest="linkbuilder_cmd", required=True, parser_class=_ToolArgumentParser)

    linkbuilder_generate = linkbuilder_sub.add_parser("generate", help="Generate one tracking link")
    linkbuilder_generate.add_argument("--publisher-id", required=True, help="Publisher ID for the link generation")
    linkbuilder_generate.add_argument("--advertiser-id", required=True, help="Advertiser ID for the link generation")
    linkbuilder_generate.add_argument("--destination-url", default=None, help="Optional destination URL")
    linkbuilder_generate.add_argument("--campaign", default=None, help="Optional campaign tracking value")
    linkbuilder_generate.add_argument("--clickref", default=None, help="Optional clickref value")
    linkbuilder_generate.add_argument("--clickref2", default=None, help="Optional clickref2 value")
    linkbuilder_generate.add_argument("--clickref3", default=None, help="Optional clickref3 value")
    linkbuilder_generate.add_argument("--clickref4", default=None, help="Optional clickref4 value")
    linkbuilder_generate.add_argument("--clickref5", default=None, help="Optional clickref5 value")
    linkbuilder_generate.add_argument("--clickref6", default=None, help="Optional clickref6 value")
    linkbuilder_generate.add_argument("--shorten", action="store_true", help="Request a short link when the advertiser allows it")
    linkbuilder_generate.set_defaults(func=linkbuilder_cmd.cmd_linkbuilder_generate, write_capable=False)

    linkbuilder_generate_batch = linkbuilder_sub.add_parser("generate-batch", help="Generate a batch of tracking links from JSON")
    linkbuilder_generate_batch.add_argument("--publisher-id", required=True, help="Publisher ID for the link generation")
    linkbuilder_generate_batch.add_argument("--requests-file", required=True, help="JSON file with a requests array (max 100 requests)")
    linkbuilder_generate_batch.set_defaults(func=linkbuilder_cmd.cmd_linkbuilder_generate_batch, write_capable=False)

    linkbuilder_quota = linkbuilder_sub.add_parser("quota", help="Show the current short-link quota")
    linkbuilder_quota.add_argument("--publisher-id", required=True, help="Publisher ID for the quota lookup")
    linkbuilder_quota.set_defaults(func=linkbuilder_cmd.cmd_linkbuilder_quota, write_capable=False)

    feeds = sub.add_parser("feeds", help="Publisher product feed downloads")
    feeds_sub = feeds.add_subparsers(dest="feeds_cmd", required=True, parser_class=_ToolArgumentParser)

    feeds_enhanced = feeds_sub.add_parser("enhanced-download", help="Download one enhanced Google-format feed to a file")
    feeds_enhanced.add_argument("--publisher-id", required=True, help="Publisher ID for the feed download")
    feeds_enhanced.add_argument("--advertiser-id", required=True, help="Advertiser ID for the feed download")
    feeds_enhanced.add_argument("--locale", required=True, help="Locale like en_GB or en_US")
    feeds_enhanced.add_argument("--vertical", default="retail", help="Enhanced feed vertical (currently only retail)")
    feeds_enhanced.add_argument("--out", required=True, help="Output file path")
    feeds_enhanced.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing file")
    feeds_enhanced.set_defaults(func=feeds_cmd.cmd_feeds_enhanced_download, write_capable=False)

    feeds_legacy_list = feeds_sub.add_parser("legacy-list", help="Download the legacy feed list CSV to a file")
    feeds_legacy_list.add_argument("--out", required=True, help="Output file path")
    feeds_legacy_list.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing file")
    feeds_legacy_list.set_defaults(func=feeds_cmd.cmd_feeds_legacy_list, write_capable=False)

    feeds_legacy_download = feeds_sub.add_parser("legacy-download", help="Download a legacy feed to a file")
    feeds_legacy_download.add_argument("--feed-id", default=None, help="Feed ID from the legacy feed list")
    feeds_legacy_download.add_argument("--download-url", default=None, help="Exact legacy download URL from Create-a-Feed")
    feeds_legacy_download.add_argument("--out", required=True, help="Output file path")
    feeds_legacy_download.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing file")
    feeds_legacy_download.set_defaults(func=feeds_cmd.cmd_feeds_legacy_download, write_capable=False)

    proof = sub.add_parser("proof-of-purchase", help="Proof-of-purchase publisher write workflow")
    proof_sub = proof.add_subparsers(dest="proof_cmd", required=True, parser_class=_ToolArgumentParser)
    proof_orders = proof_sub.add_parser("orders", help="Proof-of-purchase order ingestion")
    proof_orders_sub = proof_orders.add_subparsers(dest="proof_orders_cmd", required=True, parser_class=_ToolArgumentParser)
    proof_orders_create = proof_orders_sub.add_parser("create", help="Create proof-of-purchase orders from a JSON file")
    proof_orders_create.add_argument("--publisher-id", required=True, help="Publisher ID for the transaction ingestion")
    proof_orders_create.add_argument("--advertiser-id", required=True, help="Advertiser ID receiving the orders")
    proof_orders_create.add_argument("--orders-file", required=True, help="JSON file containing an orders array")
    proof_orders_create.set_defaults(func=proof_of_purchase_cmd.cmd_proof_of_purchase_orders_create, write_capable=True)

    return p


def main(argv: list[str]) -> int:
    parser = build_parser()
    out = Output(mode=_output_mode_from_argv(argv))
    try:
        args = parser.parse_args(argv)
    except ValidationError as e:
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        return 1
    except SystemExit as e:
        try:
            return int(e.code or 0)
        except Exception:
            return 0

    if bool(args.version):
        out.emit({"ok": True, "tool": _TOOL, "version": __version__})
        return 0

    if not getattr(args, "cmd", None):
        out.emit(
            {
                "ok": False,
                "error": "Missing command. Use --help to see available commands.",
                "error_type": "ValidationError",
            }
        )
        return 1

    write_capable = bool(getattr(args, "write_capable", False))
    command_str = f"{_TOOL} {' '.join(argv)}"
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
    out.set_provenance(
        {
            "run_id": run_ctx.run_id,
            "artifacts_dir": str(run_ctx.artifacts_dir) if run_ctx.artifacts_dir else None,
            "runs_index": str(runs_index_path),
            "audit_log": run_audit_log_path or global_audit_log_path,
            "audit_log_global": global_audit_log_path,
        }
    )

    try:
        if str(getattr(args, "cmd", "") or "") in {"runs", "onboarding"}:
            env_fingerprint = None
            ctx = {
                "cfg": None,
                "out": out,
                "audit": audit,
                "tool": _TOOL,
                "tool_version": __version__,
                "command_str": command_str,
                "env_file": str(args.env_file),
                "timeout_s": None,
                "verbose": bool(args.verbose),
                "run_id": run_ctx.run_id,
                "artifacts_dir": run_ctx.artifacts_dir,
                "runs_index_path": runs_index_path,
                "env_file": str(args.env_file),
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "plan_out": str(args.plan_out) if args.plan_out else None,
                "plan_in": str(args.plan_in) if args.plan_in else None,
                "receipt_out": str(args.receipt_out) if args.receipt_out else None,
            }
            rc = int(args.func(args, ctx))
            _finalize_run_artifacts(
                run_ctx=run_ctx,
                tool=_TOOL,
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

        cfg = load_config(args.env_file)
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        if timeout_s <= 0:
            raise ValidationError("--timeout-s must be > 0")

        http_client = HttpClient(timeout_s=timeout_s, verbose=bool(args.verbose), user_agent=_user_agent(__version__))
        ctx = {
            "cfg": cfg,
            "http_client": http_client,
            "out": out,
            "audit": audit,
            "tool": _TOOL,
            "tool_version": __version__,
            "command_str": command_str,
            "env_file": str(args.env_file),
            "timeout_s": timeout_s,
            "verbose": bool(args.verbose),
            "run_id": run_ctx.run_id,
            "artifacts_dir": run_ctx.artifacts_dir,
            "runs_index_path": runs_index_path,
            "apply": bool(args.apply),
            "yes": bool(args.yes),
            "plan_out": str(args.plan_out) if args.plan_out else None,
            "plan_in": str(args.plan_in) if args.plan_in else None,
            "receipt_out": str(args.receipt_out) if args.receipt_out else None,
        }

        audit.bind_context(
            {
                "tool": _TOOL,
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "env_fingerprint": cfg.api_host,
                "run_id": run_ctx.run_id,
            }
        )

        rc = int(args.func(args, ctx))
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool=_TOOL,
            version=__version__,
            command=command_str,
            env_fingerprint=cfg.api_host,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return rc
    except SafetyError as e:
        audit.write("refusal", {"reason": str(e), "refusal_type": type(e).__name__})
        out.emit(
            {
                "ok": True,
                "refused": True,
                "reason": str(e),
                "refusal_type": type(e).__name__,
                "dry_run": not bool(getattr(args, "apply", False)),
            }
        )
        return 0
    except ValidationError as e:
        audit.write("error", {"error": str(e), "error_type": type(e).__name__})
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        return 1
    except ToolError as e:
        audit.write("error", {"error": str(e), "error_type": type(e).__name__})
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        return 1
    except Exception as e:  # noqa: BLE001
        if bool(args.debug):
            raise
        audit.write("error", {"error": str(e), "error_type": type(e).__name__})
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        return 1
    finally:
        audit.close()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
