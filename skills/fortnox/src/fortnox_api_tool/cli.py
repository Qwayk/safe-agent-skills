from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import accounting_reads as accounting_reads_cmd
from .commands import attachment as attachment_cmd
from .commands import article_file_connections as article_file_connections_cmd
from .commands import asset_file_connections as asset_file_connections_cmd
from .commands import asset_types as asset_types_cmd
from .commands import assets as assets_cmd
from .commands import customers as customers_cmd
from .commands import customer_references as customer_references_cmd
from .commands import accounts as accounts_cmd
from .commands import expenses as expenses_cmd
from .commands import financial_years as financial_years_cmd
from .commands import fortnox_finans as fortnox_finans_cmd
from .commands import incoming_goods as incoming_goods_cmd
from .commands import integration_sales as integration_sales_cmd
from .commands import auth as auth_cmd
from .commands import articles as articles_cmd
from .commands import absence_transactions as absence_transactions_cmd
from .commands import attendance_transactions as attendance_transactions_cmd
from .commands import currencies as currencies_cmd
from .commands import cost_centers as cost_centers_cmd
from .commands import employees as employees_cmd
from .commands import contract_accruals as contract_accruals_cmd
from .commands import contract_templates as contract_templates_cmd
from .commands import contracts as contracts_cmd
from .commands import document_intake_writes as document_intake_writes_cmd
from .commands import labels as labels_cmd
from .commands import predefined_accounts as predefined_accounts_cmd
from .commands import predefined_voucher_series as predefined_voucher_series_cmd
from .commands import modes_of_payments as modes_of_payments_cmd
from .commands import price_lists as price_lists_cmd
from .commands import prices as prices_cmd
from .commands import projects as projects_cmd
from .commands import production_orders as production_orders_cmd
from .commands import purchase_orders as purchase_orders_cmd
from .commands import remaining_reads as remaining_reads_cmd
from .commands import salary_transactions as salary_transactions_cmd
from .commands import schedule_times as schedule_times_cmd
from .commands import stock_taking as stock_taking_cmd
from .commands import stock_transfers as stock_transfers_cmd
from .commands import stock_points as stock_points_cmd
from .commands import suppliers as suppliers_cmd
from .commands import invoice_accruals as invoice_accruals_cmd
from .commands import invoice_payments as invoice_payments_cmd
from .commands import invoices as invoices_cmd
from .commands import offers as offers_cmd
from .commands import jobs as jobs_cmd
from .commands import onboarding as onboarding_cmd
from .commands import orders as orders_cmd
from .commands import supplier_invoice_accruals as supplier_invoice_accruals_cmd
from .commands import supplier_invoice_external_url_connections as supplier_invoice_external_url_connections_cmd
from .commands import supplier_invoice_file_connections as supplier_invoice_file_connections_cmd
from .commands import supplier_invoice_payments as supplier_invoice_payments_cmd
from .commands import supplier_invoices as supplier_invoices_cmd
from .commands import terms_of_deliveries as terms_of_deliveries_cmd
from .commands import terms_of_payments as terms_of_payments_cmd
from .commands import tax_reductions as tax_reductions_cmd
from .commands import units as units_cmd
from .commands import voucher_file_connections as voucher_file_connections_cmd
from .commands import voucher_series as voucher_series_cmd
from .commands import vouchers as vouchers_cmd
from .commands import way_of_deliveries as way_of_deliveries_cmd
from .commands import ws as ws_cmd
from .config import load_config
from .project_config import load_project_config
from .errors import SafetyError, ToolError, ValidationError
from .output import Output
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


class _ToolArgumentParser(argparse.ArgumentParser):
    """
    Ensure user-input errors can be surfaced as JSON.

    Argparse defaults to printing usage/help to stderr and raising SystemExit, which makes it
    hard to keep the `--output json` contract (exactly one JSON object to stdout on errors).
    """

    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def _add_local_write_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--apply", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    parser.add_argument("--yes", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    parser.add_argument("--plan-out", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    parser.add_argument("--plan-in", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    parser.add_argument("--receipt-out", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    parser.add_argument("--ack-no-snapshot", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    parser.add_argument("--ack-irreversible", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS)


def _add_bool_choice_flag(parser: argparse.ArgumentParser, flag: str, *, dest: str, help_text: str) -> None:
    parser.add_argument(
        flag,
        dest=dest,
        choices=("true", "false"),
        default=None,
        help=help_text,
    )


def _add_download_output_flag(parser: argparse.ArgumentParser, *, noun: str) -> None:
    parser.add_argument(
        "--output-file",
        default=None,
        help=f"Optional local path to save the downloaded {noun}",
    )


def _add_stock_taking_filter_flags(
    parser: argparse.ArgumentParser,
    *,
    include_non_inbound: bool = False,
    exclude_non_inbound: bool = False,
    include_rows_extras: bool = False,
) -> None:
    parser.add_argument("--item-id", action="append", default=None, help="Filter by one or more item ids")
    parser.add_argument(
        "--supplier-number",
        action="append",
        default=None,
        help="Filter by one or more supplier numbers",
    )
    parser.add_argument(
        "--stock-point-id",
        action="append",
        default=None,
        help="Filter by one or more stock point ids",
    )
    parser.add_argument(
        "--stock-location-id",
        action="append",
        default=None,
        help="Filter by one or more stock location ids",
    )
    parser.add_argument("--transaction-date", help="Filter transaction date in YYYY-MM-DD")
    parser.add_argument("--item-id-search", help="Filter by item-id search text")
    parser.add_argument("--item-description-search", help="Filter by item-description search text")
    parser.add_argument(
        "--exclude-zero-balance-items",
        action="store_true",
        help="Exclude zero-balance items from the warehouse filter",
    )
    if include_non_inbound:
        parser.add_argument(
            "--include-non-inbound-items",
            action="store_true",
            help="Include items without inbound transactions in candidate-row filtering",
        )
    if exclude_non_inbound:
        parser.add_argument(
            "--exclude-non-inbound-items",
            action="store_true",
            help="Exclude items without inbound transactions when adding rows by filter",
        )
    if include_rows_extras:
        parser.add_argument("--secondary-sort-by", help="Secondary row sort field from the official stock-taking docs")
        parser.add_argument("--secondary-order", help="Secondary row sort order from the official stock-taking docs")
        parser.add_argument(
            "--state-filter",
            choices=["all", "notStockTaken", "stockTakenNoDeviation", "stockTakenWithDeviation"],
            help="Row state filter from the official stock-taking docs",
        )
        parser.add_argument("--starting-row-no", type=int, help="Starting row number for paged stock-taking rows")
        parser.add_argument("--starting-item-id", help="Starting item id for paged stock-taking rows")


def _add_stock_point_state_flag(parser: argparse.ArgumentParser, *, help_text: str) -> None:
    parser.add_argument(
        "--state",
        choices=["ALL", "ACTIVE", "INACTIVE"],
        help=help_text,
    )


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
    p = _ToolArgumentParser(prog="fortnox-api-tool")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--config", default=None, help="Optional project defaults JSON (non-secret)")
    p.add_argument("--project-dir", default=None, help="Optional project directory (defaults to config file folder)")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    p.add_argument("--debug", action="store_true", help="Show stack traces on errors")
    p.add_argument("--output", choices=("json", "text"), default="json", help="Output format (default: json)")
    p.add_argument("--log-file", default=None, help="Optional audit log path (JSONL)")
    p.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    p.add_argument("--yes", action="store_true", help="Additional confirmation for destructive/batch actions")
    p.add_argument("--plan-out", default=None, help="Write a dry-run plan JSON to a file")
    p.add_argument("--plan-in", default=None, help="Apply from an existing plan JSON file (high-risk writes)")
    p.add_argument("--receipt-out", default=None, help="Write an apply receipt JSON to a file")
    p.add_argument(
        "--ack-no-snapshot",
        action="store_true",
        help="Extra acknowledgement when a high-risk apply has no useful before-state snapshot",
    )
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
    auth_check.add_argument("--skip-live", action="store_true", help="Validate token discovery only; do not call Fortnox")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=False)

    auth_login = auth_sub.add_parser("login", help="Build the Fortnox authorize URL and save a local state file")
    auth_login.add_argument("--scope", action="append", help="Override scopes for this auth login request")
    auth_login.add_argument("--state", default=None, help="Optional explicit OAuth state value")
    auth_login.add_argument(
        "--service-account",
        action="store_true",
        help="Request service-account consent (`account_type=service`)",
    )
    auth_login.set_defaults(func=auth_cmd.cmd_auth_login, write_capable=True)

    auth_exchange = auth_sub.add_parser("exchange-code", help="Exchange an authorization code for access and refresh tokens")
    auth_exchange.add_argument("--code", required=True, help="Authorization code returned by Fortnox")
    auth_exchange.add_argument("--state", default=None, help="OAuth state returned by Fortnox")
    auth_exchange.set_defaults(func=auth_cmd.cmd_auth_exchange_code, write_capable=True)

    auth_refresh = auth_sub.add_parser("refresh", help="Refresh the stored Fortnox OAuth token")
    auth_refresh.set_defaults(func=auth_cmd.cmd_auth_refresh, write_capable=True)

    auth_service = auth_sub.add_parser(
        "service-account-token",
        help="Fetch a service-account access token using client credentials and tenant id",
    )
    auth_service.add_argument("--scope", action="append", help="Optional explicit scopes for this token request")
    auth_service.set_defaults(func=auth_cmd.cmd_auth_service_account_token, write_capable=True)

    token = auth_sub.add_parser("token", help="OAuth token helpers (manual copy/paste)")
    token_sub = token.add_subparsers(dest="token_cmd", required=True, parser_class=_ToolArgumentParser)
    token_set = token_sub.add_parser("set", help="Store token JSON under .state/token.json")
    token_set.add_argument("--file", required=True, help="Token JSON file path (input)")
    token_set.set_defaults(func=auth_cmd.cmd_auth_token_set, write_capable=True)
    token_status = token_sub.add_parser("status", help="Show token status (never prints token values)")
    token_status.set_defaults(func=auth_cmd.cmd_auth_token_status, write_capable=False)

    ws = sub.add_parser("ws", help="Fortnox websocket controls and subscription")
    ws_sub = ws.add_subparsers(dest="ws_cmd", required=True, parser_class=_ToolArgumentParser)

    ws_tenants = ws_sub.add_parser("tenants", help="Manage websocket tenant selection")
    ws_tenants_sub = ws_tenants.add_subparsers(dest="ws_tenants_cmd", required=True, parser_class=_ToolArgumentParser)

    ws_tenants_add = ws_tenants_sub.add_parser("add", help="Send the official add-tenants websocket command")
    ws_tenants_add.add_argument(
        "--access-token",
        action="append",
        default=None,
        help="Tenant access token to add. Repeat for multiple tenants. If omitted, the current Fortnox access token is used.",
    )
    ws_tenants_add.add_argument(
        "--client-secret",
        default=None,
        help="Optional websocket client secret override. Defaults to FORTNOX_CLIENT_SECRET.",
    )
    ws_tenants_add.add_argument(
        "--include-child-tenants",
        action="store_true",
        help="Include child tenants as documented by Fortnox.",
    )
    ws_tenants_add.set_defaults(func=ws_cmd.cmd_ws_tenants_add, write_capable=False)

    ws_tenants_remove = ws_tenants_sub.add_parser("remove", help="Send the official remove-tenants websocket command")
    ws_tenants_remove.add_argument(
        "--tenant-id",
        action="append",
        type=int,
        default=None,
        help="Tenant id to remove from the active websocket stream. Repeat for multiple tenants.",
    )
    ws_tenants_remove.set_defaults(func=ws_cmd.cmd_ws_tenants_remove, write_capable=False)

    ws_tenants_list = ws_tenants_sub.add_parser("list", help="Send the official list-tenants websocket command")
    ws_tenants_list.set_defaults(func=ws_cmd.cmd_ws_tenants_list, write_capable=False)

    ws_topics = ws_sub.add_parser("topics", help="Manage websocket topics")
    ws_topics_sub = ws_topics.add_subparsers(dest="ws_topics_cmd", required=True, parser_class=_ToolArgumentParser)

    ws_topics_add = ws_topics_sub.add_parser("add", help="Send the official add-topics websocket command")
    ws_topics_add.add_argument(
        "--topic",
        action="append",
        choices=ws_cmd.topic_choice_list(),
        default=None,
        help="Topic to add. Repeat for multiple topics.",
    )
    ws_topics_add.add_argument(
        "--topic-offset",
        action="append",
        default=None,
        help="Topic replay offset in the form `<topic>=<offset>`. Repeat for multiple topics.",
    )
    ws_topics_add.set_defaults(func=ws_cmd.cmd_ws_topics_add, write_capable=False)

    ws_subscribe = ws_sub.add_parser("subscribe", help="Start a live websocket subscription")
    ws_subscribe_sub = ws_subscribe.add_subparsers(dest="ws_subscribe_cmd", required=True, parser_class=_ToolArgumentParser)
    ws_subscribe_start = ws_subscribe_sub.add_parser(
        "start",
        help="Open one websocket connection, add tenants, add topics, subscribe, and collect events",
    )
    ws_subscribe_start.add_argument(
        "--access-token",
        action="append",
        default=None,
        help="Tenant access token to add before subscribing. Repeat for multiple tenants. If omitted, the current Fortnox access token is used.",
    )
    ws_subscribe_start.add_argument(
        "--client-secret",
        default=None,
        help="Optional websocket client secret override. Defaults to FORTNOX_CLIENT_SECRET.",
    )
    ws_subscribe_start.add_argument(
        "--include-child-tenants",
        action="store_true",
        help="Include child tenants as documented by Fortnox.",
    )
    ws_subscribe_start.add_argument(
        "--topic",
        action="append",
        choices=ws_cmd.topic_choice_list(),
        default=None,
        help="Topic to subscribe to. Repeat for multiple topics.",
    )
    ws_subscribe_start.add_argument(
        "--topic-offset",
        action="append",
        default=None,
        help="Topic replay offset in the form `<topic>=<offset>`. Repeat for multiple topics.",
    )
    ws_subscribe_start.add_argument(
        "--max-events",
        type=int,
        default=10,
        help="Stop after this many events. Use 0 to wait until idle timeout instead.",
    )
    ws_subscribe_start.add_argument(
        "--idle-timeout-s",
        type=float,
        default=30.0,
        help="Stop if no websocket event arrives within this many seconds after subscription starts.",
    )
    ws_subscribe_start.set_defaults(func=ws_cmd.cmd_ws_subscribe_start, write_capable=False)

    company_information = sub.add_parser("company-information", help="Company information reads")
    company_information_sub = company_information.add_subparsers(
        dest="company_information_cmd", required=True, parser_class=_ToolArgumentParser
    )
    company_information_get = company_information_sub.add_parser("get", help="Retrieve company information")
    company_information_get.set_defaults(func=accounting_reads_cmd.cmd_company_information_get, write_capable=False)

    company_settings = sub.add_parser("company-settings", help="Company settings reads")
    company_settings_sub = company_settings.add_subparsers(
        dest="company_settings_cmd", required=True, parser_class=_ToolArgumentParser
    )
    company_settings_get = company_settings_sub.add_parser("get", help="Retrieve company settings")
    company_settings_get.set_defaults(func=accounting_reads_cmd.cmd_company_settings_get, write_capable=False)

    asset_file_connections = sub.add_parser("asset-file-connections", help="Asset file connection commands")
    asset_file_connections_sub = asset_file_connections.add_subparsers(
        dest="asset_file_connections_cmd", required=True, parser_class=_ToolArgumentParser
    )
    asset_file_connections_list = asset_file_connections_sub.add_parser(
        "list",
        help="List asset file connections",
    )
    asset_file_connections_list.set_defaults(
        func=asset_file_connections_cmd.cmd_asset_file_connections_list,
        write_capable=False,
    )
    asset_file_connections_create = asset_file_connections_sub.add_parser(
        "create",
        help="Plan or create one asset file connection from a JSON payload file",
    )
    asset_file_connections_create.add_argument(
        "--json-file",
        required=True,
        help="Path to the asset file connection JSON payload file",
    )
    _add_local_write_flags(asset_file_connections_create)
    asset_file_connections_create.set_defaults(
        func=asset_file_connections_cmd.cmd_asset_file_connections_create,
        write_capable=True,
    )
    asset_file_connections_remove = asset_file_connections_sub.add_parser(
        "remove",
        help="Plan or remove one asset file connection",
    )
    asset_file_connections_remove.add_argument("--file-id", required=True, help="Fortnox asset file id")
    _add_local_write_flags(asset_file_connections_remove)
    asset_file_connections_remove.set_defaults(
        func=asset_file_connections_cmd.cmd_asset_file_connections_remove,
        write_capable=True,
    )

    article_file_connections = sub.add_parser("article-file-connections", help="Article file connection commands")
    article_file_connections_sub = article_file_connections.add_subparsers(
        dest="article_file_connections_cmd", required=True, parser_class=_ToolArgumentParser
    )
    article_file_connections_list = article_file_connections_sub.add_parser(
        "list",
        help="List article file connections",
    )
    article_file_connections_list.add_argument(
        "--article-number",
        help="Filter by Fortnox article number",
    )
    article_file_connections_list.set_defaults(
        func=article_file_connections_cmd.cmd_article_file_connections_list,
        write_capable=False,
    )
    article_file_connections_get = article_file_connections_sub.add_parser(
        "get",
        help="Get one article file connection",
    )
    article_file_connections_get.add_argument("--file-id", required=True, help="Fortnox file id")
    article_file_connections_get.set_defaults(
        func=article_file_connections_cmd.cmd_article_file_connections_get,
        write_capable=False,
    )
    article_file_connections_create = article_file_connections_sub.add_parser(
        "create",
        help="Plan or create one article file connection from a JSON payload file",
    )
    article_file_connections_create.add_argument(
        "--json-file",
        required=True,
        help="Path to the article file connection JSON payload file",
    )
    _add_local_write_flags(article_file_connections_create)
    article_file_connections_create.set_defaults(
        func=article_file_connections_cmd.cmd_article_file_connections_create,
        write_capable=True,
    )
    article_file_connections_remove = article_file_connections_sub.add_parser(
        "remove",
        help="Plan or remove one article file connection",
    )
    article_file_connections_remove.add_argument("--file-id", required=True, help="Fortnox file id")
    _add_local_write_flags(article_file_connections_remove)
    article_file_connections_remove.set_defaults(
        func=article_file_connections_cmd.cmd_article_file_connections_remove,
        write_capable=True,
    )

    attachment = sub.add_parser("attachment", help="Attachment commands")
    attachment_sub = attachment.add_subparsers(dest="attachment_cmd", required=True, parser_class=_ToolArgumentParser)
    attachment_get = attachment_sub.add_parser("get", help="Get attached files on one entity type")
    attachment_get.add_argument(
        "--entity-id",
        action="append",
        type=int,
        required=True,
        help="One or more Fortnox entity ids",
    )
    attachment_get.add_argument(
        "--entity-type",
        required=True,
        help="Fortnox attachment entity type",
    )
    attachment_get.set_defaults(func=attachment_cmd.cmd_attachment_get, write_capable=False)
    attachment_list = attachment_sub.add_parser("list", help="List the number of attachments on one entity type")
    attachment_list.add_argument(
        "--entity-id",
        action="append",
        type=int,
        required=True,
        help="One or more Fortnox entity ids",
    )
    attachment_list.add_argument(
        "--entity-type",
        required=True,
        help="Fortnox attachment entity type",
    )
    attachment_list.set_defaults(func=attachment_cmd.cmd_attachment_list, write_capable=False)
    attachment_attach = attachment_sub.add_parser(
        "attach-files-to-one-or-more-entities",
        help="Plan or attach one or more files from a JSON array payload file",
    )
    attachment_attach.add_argument("--json-file", required=True, help="Path to the attachment JSON array payload file")
    _add_local_write_flags(attachment_attach)
    attachment_attach.set_defaults(
        func=attachment_cmd.cmd_attachment_attach,
        write_capable=True,
    )
    attachment_detach = attachment_sub.add_parser("detach-file", help="Plan or detach one attachment by id")
    attachment_detach.add_argument("--attachment-id", required=True, help="Fortnox attachment id (UUID)")
    _add_local_write_flags(attachment_detach)
    attachment_detach.set_defaults(func=attachment_cmd.cmd_attachment_detach, write_capable=True)
    attachment_update = attachment_sub.add_parser("update", help="Plan or update one attachment from a JSON payload file")
    attachment_update.add_argument("--attachment-id", required=True, help="Fortnox attachment id (UUID)")
    attachment_update.add_argument("--json-file", required=True, help="Path to the attachment JSON payload file")
    _add_local_write_flags(attachment_update)
    attachment_update.set_defaults(func=attachment_cmd.cmd_attachment_update, write_capable=True)
    attachment_validate = attachment_sub.add_parser(
        "validates-a-list-of-attachments-that-will-be-included-on-send",
        help="Validate one JSON array of attachments for include-on-send without changing Fortnox state",
    )
    attachment_validate.add_argument("--json-file", required=True, help="Path to the attachment JSON array payload file")
    attachment_validate.set_defaults(
        func=attachment_cmd.cmd_attachment_validate_included_on_send,
        write_capable=False,
    )

    asset_types = sub.add_parser("asset-types", help="Asset type commands")
    asset_types_sub = asset_types.add_subparsers(dest="asset_types_cmd", required=True, parser_class=_ToolArgumentParser)
    asset_types_list = asset_types_sub.add_parser("list", help="List asset types")
    asset_types_list.set_defaults(func=asset_types_cmd.cmd_asset_types_list, write_capable=False)
    asset_types_get = asset_types_sub.add_parser("get", help="Get one asset type")
    asset_types_get.add_argument("--id", required=True, help="Fortnox asset type id")
    asset_types_get.set_defaults(func=asset_types_cmd.cmd_asset_types_get, write_capable=False)
    asset_types_create = asset_types_sub.add_parser(
        "create",
        help="Plan or create one asset type from a JSON payload file",
    )
    asset_types_create.add_argument(
        "--json-file",
        required=True,
        help="Path to the asset type JSON payload file",
    )
    _add_local_write_flags(asset_types_create)
    asset_types_create.set_defaults(func=asset_types_cmd.cmd_asset_types_create, write_capable=True)
    asset_types_update = asset_types_sub.add_parser(
        "update",
        help="Plan or update one asset type from a JSON payload file",
    )
    asset_types_update.add_argument("--id", required=True, help="Fortnox asset type id")
    asset_types_update.add_argument(
        "--json-file",
        required=True,
        help="Path to the asset type JSON payload file",
    )
    _add_local_write_flags(asset_types_update)
    asset_types_update.set_defaults(func=asset_types_cmd.cmd_asset_types_update, write_capable=True)
    asset_types_delete = asset_types_sub.add_parser(
        "delete",
        help="Plan or delete one asset type",
    )
    asset_types_delete.add_argument("--id", required=True, help="Fortnox asset type id")
    _add_local_write_flags(asset_types_delete)
    asset_types_delete.set_defaults(func=asset_types_cmd.cmd_asset_types_delete, write_capable=True)

    assets = sub.add_parser("assets", help="Asset commands")
    assets_sub = assets.add_subparsers(dest="assets_cmd", required=True, parser_class=_ToolArgumentParser)
    assets_list = assets_sub.add_parser("list", help="List assets")
    assets_list.set_defaults(func=assets_cmd.cmd_assets_list, write_capable=False)
    assets_get = assets_sub.add_parser("get", help="Get one asset")
    assets_get.add_argument("--id", required=True, help="Fortnox asset id")
    assets_get.set_defaults(func=assets_cmd.cmd_assets_get, write_capable=False)
    assets_create = assets_sub.add_parser(
        "create",
        help="Plan or create one asset from a JSON payload file",
    )
    assets_create.add_argument("--json-file", required=True, help="Path to the asset JSON payload file")
    _add_local_write_flags(assets_create)
    assets_create.set_defaults(func=assets_cmd.cmd_assets_create, write_capable=True)
    assets_update = assets_sub.add_parser(
        "update",
        help="Plan or update one asset from a JSON payload file",
    )
    assets_update.add_argument("--id", required=True, help="Fortnox asset id")
    assets_update.add_argument("--json-file", required=True, help="Path to the asset JSON payload file")
    _add_local_write_flags(assets_update)
    assets_update.set_defaults(func=assets_cmd.cmd_assets_update, write_capable=True)
    assets_delete = assets_sub.add_parser(
        "delete",
        help="Plan or delete one asset",
    )
    assets_delete.add_argument("--id", required=True, help="Fortnox asset id")
    _add_local_write_flags(assets_delete)
    assets_delete.set_defaults(func=assets_cmd.cmd_assets_delete, write_capable=True)
    assets_depreciation_list = assets_sub.add_parser(
        "assets-depreciation-list",
        help="Get the asset depreciation list for one date",
    )
    assets_depreciation_list.add_argument("--to-date", required=True, help="Fortnox depreciation date (YYYY-MM-DD)")
    assets_depreciation_list.set_defaults(func=assets_cmd.cmd_assets_depreciation_list, write_capable=False)
    assets_change_manual_ob = assets_sub.add_parser(
        "change-manual-ob-value-of-an-asset",
        help="Plan or change the manual OB value of one asset",
    )
    assets_change_manual_ob.add_argument("--id", required=True, help="Fortnox asset id")
    assets_change_manual_ob.add_argument("--json-file", required=True, help="Path to the asset change JSON payload file")
    _add_local_write_flags(assets_change_manual_ob)
    assets_change_manual_ob.set_defaults(func=assets_cmd.cmd_assets_change_manual_ob, write_capable=True)
    assets_depreciate = assets_sub.add_parser(
        "perform-a-depreciation-of-an-asset",
        help="Plan or perform one asset depreciation from a JSON payload file",
    )
    assets_depreciate.add_argument("--json-file", required=True, help="Path to the asset depreciation JSON payload file")
    _add_local_write_flags(assets_depreciate)
    assets_depreciate.set_defaults(func=assets_cmd.cmd_assets_depreciate, write_capable=True)
    assets_scrap = assets_sub.add_parser(
        "scrap-an-asset",
        help="Plan or scrap one asset from a JSON payload file",
    )
    assets_scrap.add_argument("--id", required=True, help="Fortnox asset id")
    assets_scrap.add_argument("--json-file", required=True, help="Path to the asset scrap JSON payload file")
    _add_local_write_flags(assets_scrap)
    assets_scrap.set_defaults(func=assets_cmd.cmd_assets_scrap, write_capable=True)
    assets_sell = assets_sub.add_parser(
        "sell-an-asset",
        help="Plan or sell one asset from a JSON payload file",
    )
    assets_sell.add_argument("--id", required=True, help="Fortnox asset id")
    assets_sell.add_argument("--json-file", required=True, help="Path to the asset sell JSON payload file")
    _add_local_write_flags(assets_sell)
    assets_sell.set_defaults(func=assets_cmd.cmd_assets_sell, write_capable=True)
    assets_write_down = assets_sub.add_parser(
        "write-down-an-asset",
        help="Plan or write down one asset from a JSON payload file",
    )
    assets_write_down.add_argument("--id", required=True, help="Fortnox asset id")
    assets_write_down.add_argument("--json-file", required=True, help="Path to the asset write-down JSON payload file")
    _add_local_write_flags(assets_write_down)
    assets_write_down.set_defaults(func=assets_cmd.cmd_assets_write_down, write_capable=True)
    assets_write_up = assets_sub.add_parser(
        "write-up-an-asset",
        help="Plan or write up one asset from a JSON payload file",
    )
    assets_write_up.add_argument("--id", required=True, help="Fortnox asset id")
    assets_write_up.add_argument("--json-file", required=True, help="Path to the asset write-up JSON payload file")
    _add_local_write_flags(assets_write_up)
    assets_write_up.set_defaults(func=assets_cmd.cmd_assets_write_up, write_capable=True)

    archive = sub.add_parser("archive", help="Archive reads and writes")
    archive_sub = archive.add_subparsers(dest="archive_cmd", required=True, parser_class=_ToolArgumentParser)
    archive_get_root = archive_sub.add_parser("get-root", help="Retrieve the archive root folder or one folder path")
    archive_get_root.add_argument("--path", default=None, help="Optional archive folder path")
    archive_get_root.add_argument("--file-id", default=None, help="Optional fileId from fileattachments")
    archive_get_root.set_defaults(func=accounting_reads_cmd.cmd_archive_get_root, write_capable=False)
    archive_get_file = archive_sub.add_parser("get-file", help="Retrieve one archive file")
    archive_get_file.add_argument("--id", required=True, help="Fortnox archive file id")
    archive_get_file.set_defaults(func=accounting_reads_cmd.cmd_archive_get_file, write_capable=False)
    archive_delete = archive_sub.add_parser("delete", help="Plan or delete one archive file by id")
    archive_delete.add_argument("--id", required=True, help="Fortnox archive file id")
    archive_delete.add_argument("--path", default=None, help="Optional archive folder path for delete verification")
    _add_local_write_flags(archive_delete)
    archive_delete.set_defaults(func=document_intake_writes_cmd.cmd_archive_delete, write_capable=True)
    archive_remove = archive_sub.add_parser("remove", help="Plan or remove archive content by explicit path")
    archive_remove.add_argument("--path", required=True, help="Archive folder or file path to remove")
    _add_local_write_flags(archive_remove)
    archive_remove.set_defaults(func=document_intake_writes_cmd.cmd_archive_remove, write_capable=True)
    archive_upload = archive_sub.add_parser(
        "upload-a-file-to-a-specific-subdirectory",
        help="Plan or upload one file to an explicit archive subdirectory",
    )
    archive_upload.add_argument("--file", required=True, help="Path to the local file to upload")
    archive_upload.add_argument("--path", default=None, help="Archive folder path target")
    archive_upload.add_argument("--folder-id", default=None, help="Archive folder id target")
    _add_local_write_flags(archive_upload)
    archive_upload.set_defaults(func=document_intake_writes_cmd.cmd_archive_upload, write_capable=True)

    inbox = sub.add_parser("inbox", help="Inbox reads and writes")
    inbox_sub = inbox.add_subparsers(dest="inbox_cmd", required=True, parser_class=_ToolArgumentParser)
    inbox_get_root = inbox_sub.add_parser("get-root", help="Retrieve the inbox root folder")
    inbox_get_root.set_defaults(func=accounting_reads_cmd.cmd_inbox_get_root, write_capable=False)
    inbox_get_file = inbox_sub.add_parser("get-file", help="Retrieve one inbox file")
    inbox_get_file.add_argument("--id", required=True, help="Fortnox inbox file id")
    inbox_get_file.set_defaults(func=accounting_reads_cmd.cmd_inbox_get_file, write_capable=False)
    inbox_remove = inbox_sub.add_parser("remove", help="Plan or remove one inbox file or folder by id")
    inbox_remove.add_argument("--id", required=True, help="Fortnox inbox file or folder id")
    _add_local_write_flags(inbox_remove)
    inbox_remove.set_defaults(func=document_intake_writes_cmd.cmd_inbox_remove, write_capable=True)
    inbox_upload = inbox_sub.add_parser("upload-a-file", help="Plan or upload one file to the inbox")
    inbox_upload.add_argument("--file", required=True, help="Path to the local file to upload")
    inbox_upload.add_argument("--path", default=None, help="Inbox path target")
    inbox_upload.add_argument("--folder-id", default=None, help="Inbox folder id target")
    _add_local_write_flags(inbox_upload)
    inbox_upload.set_defaults(func=document_intake_writes_cmd.cmd_inbox_upload, write_capable=True)

    custom_document_types = sub.add_parser("custom-document-types", help="Custom document type reads and writes")
    custom_document_types_sub = custom_document_types.add_subparsers(
        dest="custom_document_types_cmd", required=True, parser_class=_ToolArgumentParser
    )
    custom_document_types_list = custom_document_types_sub.add_parser("list", help="List custom document types")
    custom_document_types_list.set_defaults(
        func=accounting_reads_cmd.cmd_custom_document_types_list,
        write_capable=False,
    )
    custom_document_types_get = custom_document_types_sub.add_parser("get", help="Get one custom document type")
    custom_document_types_get.add_argument("--type", dest="doc_type", required=True, help="Fortnox custom document type")
    custom_document_types_get.set_defaults(
        func=accounting_reads_cmd.cmd_custom_document_types_get,
        write_capable=False,
    )
    custom_document_types_create = custom_document_types_sub.add_parser(
        "create",
        help="Plan or create one custom document type from a JSON payload file",
    )
    custom_document_types_create.add_argument("--json-file", required=True, help="Path to the custom document type JSON payload file")
    _add_local_write_flags(custom_document_types_create)
    custom_document_types_create.set_defaults(
        func=document_intake_writes_cmd.cmd_custom_document_types_create,
        write_capable=True,
    )

    custom_inbound_documents = sub.add_parser("custom-inbound-documents", help="Custom inbound document reads and writes")
    custom_inbound_documents_sub = custom_inbound_documents.add_subparsers(
        dest="custom_inbound_documents_cmd", required=True, parser_class=_ToolArgumentParser
    )
    custom_inbound_documents_get = custom_inbound_documents_sub.add_parser(
        "get",
        help="Get one custom inbound document",
    )
    custom_inbound_documents_get.add_argument("--type", dest="doc_type", required=True, help="Fortnox custom document type")
    custom_inbound_documents_get.add_argument("--id", required=True, help="Fortnox custom inbound document id")
    custom_inbound_documents_get.set_defaults(
        func=accounting_reads_cmd.cmd_custom_inbound_documents_get,
        write_capable=False,
    )
    custom_inbound_documents_save = custom_inbound_documents_sub.add_parser(
        "save",
        help="Plan or save one custom inbound document from a JSON payload file",
    )
    custom_inbound_documents_save.add_argument("--type", dest="doc_type", required=True, help="Fortnox custom document type")
    custom_inbound_documents_save.add_argument("--id", required=True, help="Fortnox custom inbound document id")
    custom_inbound_documents_save.add_argument("--json-file", required=True, help="Path to the custom inbound document JSON payload file")
    _add_local_write_flags(custom_inbound_documents_save)
    custom_inbound_documents_save.set_defaults(
        func=document_intake_writes_cmd.cmd_custom_inbound_documents_save,
        write_capable=True,
    )
    custom_inbound_documents_release = custom_inbound_documents_sub.add_parser(
        "release",
        help="Plan or release one custom inbound document from a JSON payload file",
    )
    custom_inbound_documents_release.add_argument("--type", dest="doc_type", required=True, help="Fortnox custom document type")
    custom_inbound_documents_release.add_argument("--id", required=True, help="Fortnox custom inbound document id")
    custom_inbound_documents_release.add_argument("--json-file", required=True, help="Path to the custom inbound document JSON payload file")
    _add_local_write_flags(custom_inbound_documents_release)
    custom_inbound_documents_release.set_defaults(
        func=document_intake_writes_cmd.cmd_custom_inbound_documents_release,
        write_capable=True,
    )
    custom_inbound_documents_void = custom_inbound_documents_sub.add_parser(
        "void",
        help="Plan or void one custom inbound document from a JSON payload file",
    )
    custom_inbound_documents_void.add_argument("--type", dest="doc_type", required=True, help="Fortnox custom document type")
    custom_inbound_documents_void.add_argument("--id", required=True, help="Fortnox custom inbound document id")
    custom_inbound_documents_void.add_argument("--json-file", required=True, help="Path to the custom inbound document JSON payload file")
    _add_local_write_flags(custom_inbound_documents_void)
    custom_inbound_documents_void.set_defaults(
        func=document_intake_writes_cmd.cmd_custom_inbound_documents_void,
        write_capable=True,
    )

    custom_outbound_documents = sub.add_parser("custom-outbound-documents", help="Custom outbound document reads and writes")
    custom_outbound_documents_sub = custom_outbound_documents.add_subparsers(
        dest="custom_outbound_documents_cmd", required=True, parser_class=_ToolArgumentParser
    )
    custom_outbound_documents_get = custom_outbound_documents_sub.add_parser(
        "get",
        help="Get one custom outbound document",
    )
    custom_outbound_documents_get.add_argument("--type", dest="doc_type", required=True, help="Fortnox custom document type")
    custom_outbound_documents_get.add_argument("--id", required=True, help="Fortnox custom outbound document id")
    custom_outbound_documents_get.set_defaults(
        func=accounting_reads_cmd.cmd_custom_outbound_documents_get,
        write_capable=False,
    )
    custom_outbound_documents_save = custom_outbound_documents_sub.add_parser(
        "save",
        help="Plan or save one custom outbound document from a JSON payload file",
    )
    custom_outbound_documents_save.add_argument("--type", dest="doc_type", required=True, help="Fortnox custom document type")
    custom_outbound_documents_save.add_argument("--id", required=True, help="Fortnox custom outbound document id")
    custom_outbound_documents_save.add_argument("--json-file", required=True, help="Path to the custom outbound document JSON payload file")
    _add_local_write_flags(custom_outbound_documents_save)
    custom_outbound_documents_save.set_defaults(
        func=document_intake_writes_cmd.cmd_custom_outbound_documents_save,
        write_capable=True,
    )
    custom_outbound_documents_release = custom_outbound_documents_sub.add_parser(
        "release",
        help="Plan or release one custom outbound document from a JSON payload file",
    )
    custom_outbound_documents_release.add_argument("--type", dest="doc_type", required=True, help="Fortnox custom document type")
    custom_outbound_documents_release.add_argument("--id", required=True, help="Fortnox custom outbound document id")
    custom_outbound_documents_release.add_argument("--json-file", required=True, help="Path to the custom outbound document JSON payload file")
    _add_local_write_flags(custom_outbound_documents_release)
    custom_outbound_documents_release.set_defaults(
        func=document_intake_writes_cmd.cmd_custom_outbound_documents_release,
        write_capable=True,
    )
    custom_outbound_documents_void = custom_outbound_documents_sub.add_parser(
        "void",
        help="Plan or void one custom outbound document from a JSON payload file",
    )
    custom_outbound_documents_void.add_argument("--type", dest="doc_type", required=True, help="Fortnox custom document type")
    custom_outbound_documents_void.add_argument("--id", required=True, help="Fortnox custom outbound document id")
    custom_outbound_documents_void.add_argument("--json-file", required=True, help="Path to the custom outbound document JSON payload file")
    _add_local_write_flags(custom_outbound_documents_void)
    custom_outbound_documents_void.set_defaults(
        func=document_intake_writes_cmd.cmd_custom_outbound_documents_void,
        write_capable=True,
    )

    manual_documents = sub.add_parser("manual-documents", help="Manual document reads")
    manual_documents_sub = manual_documents.add_subparsers(
        dest="manual_documents_cmd", required=True, parser_class=_ToolArgumentParser
    )
    manual_documents_list = manual_documents_sub.add_parser("list", help="List manual documents")
    manual_documents_list.set_defaults(func=accounting_reads_cmd.cmd_manual_documents_list, write_capable=False)

    manual_inbound_documents = sub.add_parser("manual-inbound-documents", help="Manual inbound document reads and writes")
    manual_inbound_documents_sub = manual_inbound_documents.add_subparsers(
        dest="manual_inbound_documents_cmd", required=True, parser_class=_ToolArgumentParser
    )
    manual_inbound_documents_get = manual_inbound_documents_sub.add_parser(
        "get",
        help="Get one manual inbound document",
    )
    manual_inbound_documents_get.add_argument("--id", required=True, help="Fortnox manual inbound document id")
    manual_inbound_documents_get.set_defaults(
        func=accounting_reads_cmd.cmd_manual_inbound_documents_get,
        write_capable=False,
    )
    manual_inbound_documents_create = manual_inbound_documents_sub.add_parser(
        "create",
        help="Plan or create one manual inbound document from a JSON payload file",
    )
    manual_inbound_documents_create.add_argument("--json-file", required=True, help="Path to the manual inbound document JSON payload file")
    _add_local_write_flags(manual_inbound_documents_create)
    manual_inbound_documents_create.set_defaults(
        func=document_intake_writes_cmd.cmd_manual_inbound_documents_create,
        write_capable=True,
    )
    manual_inbound_documents_update = manual_inbound_documents_sub.add_parser(
        "update",
        help="Plan or update one manual inbound document from a JSON payload file",
    )
    manual_inbound_documents_update.add_argument("--id", required=True, help="Fortnox manual inbound document id")
    manual_inbound_documents_update.add_argument("--json-file", required=True, help="Path to the manual inbound document JSON payload file")
    _add_local_write_flags(manual_inbound_documents_update)
    manual_inbound_documents_update.set_defaults(
        func=document_intake_writes_cmd.cmd_manual_inbound_documents_update,
        write_capable=True,
    )
    manual_inbound_documents_update_note = manual_inbound_documents_sub.add_parser(
        "update-note",
        help="Plan or patch the note on one manual inbound document from a JSON payload file",
    )
    manual_inbound_documents_update_note.add_argument("--id", required=True, help="Fortnox manual inbound document id")
    manual_inbound_documents_update_note.add_argument("--json-file", required=True, help="Path to the manual inbound document JSON payload file")
    _add_local_write_flags(manual_inbound_documents_update_note)
    manual_inbound_documents_update_note.set_defaults(
        func=document_intake_writes_cmd.cmd_manual_inbound_documents_update_note,
        write_capable=True,
    )
    manual_inbound_documents_release = manual_inbound_documents_sub.add_parser(
        "release",
        help="Plan or release one manual inbound document from a JSON payload file",
    )
    manual_inbound_documents_release.add_argument("--id", required=True, help="Fortnox manual inbound document id")
    manual_inbound_documents_release.add_argument("--json-file", required=True, help="Path to the manual inbound document JSON payload file")
    _add_local_write_flags(manual_inbound_documents_release)
    manual_inbound_documents_release.set_defaults(
        func=document_intake_writes_cmd.cmd_manual_inbound_documents_release,
        write_capable=True,
    )
    manual_inbound_documents_void = manual_inbound_documents_sub.add_parser(
        "void",
        help="Plan or void one manual inbound document from a JSON payload file",
    )
    manual_inbound_documents_void.add_argument("--id", required=True, help="Fortnox manual inbound document id")
    manual_inbound_documents_void.add_argument("--json-file", required=True, help="Path to the manual inbound document JSON payload file")
    _add_local_write_flags(manual_inbound_documents_void)
    manual_inbound_documents_void.set_defaults(
        func=document_intake_writes_cmd.cmd_manual_inbound_documents_void,
        write_capable=True,
    )

    manual_outbound_documents = sub.add_parser("manual-outbound-documents", help="Manual outbound document reads and writes")
    manual_outbound_documents_sub = manual_outbound_documents.add_subparsers(
        dest="manual_outbound_documents_cmd", required=True, parser_class=_ToolArgumentParser
    )
    manual_outbound_documents_get = manual_outbound_documents_sub.add_parser(
        "get",
        help="Get one manual outbound document",
    )
    manual_outbound_documents_get.add_argument("--id", required=True, help="Fortnox manual outbound document id")
    manual_outbound_documents_get.set_defaults(
        func=accounting_reads_cmd.cmd_manual_outbound_documents_get,
        write_capable=False,
    )
    manual_outbound_documents_create = manual_outbound_documents_sub.add_parser(
        "create",
        help="Plan or create one manual outbound document from a JSON payload file",
    )
    manual_outbound_documents_create.add_argument("--json-file", required=True, help="Path to the manual outbound document JSON payload file")
    _add_local_write_flags(manual_outbound_documents_create)
    manual_outbound_documents_create.set_defaults(
        func=document_intake_writes_cmd.cmd_manual_outbound_documents_create,
        write_capable=True,
    )
    manual_outbound_documents_update = manual_outbound_documents_sub.add_parser(
        "update",
        help="Plan or update one manual outbound document from a JSON payload file",
    )
    manual_outbound_documents_update.add_argument("--id", required=True, help="Fortnox manual outbound document id")
    manual_outbound_documents_update.add_argument("--json-file", required=True, help="Path to the manual outbound document JSON payload file")
    _add_local_write_flags(manual_outbound_documents_update)
    manual_outbound_documents_update.set_defaults(
        func=document_intake_writes_cmd.cmd_manual_outbound_documents_update,
        write_capable=True,
    )
    manual_outbound_documents_update_note = manual_outbound_documents_sub.add_parser(
        "update-note",
        help="Plan or patch the note on one manual outbound document from a JSON payload file",
    )
    manual_outbound_documents_update_note.add_argument("--id", required=True, help="Fortnox manual outbound document id")
    manual_outbound_documents_update_note.add_argument("--json-file", required=True, help="Path to the manual outbound document JSON payload file")
    _add_local_write_flags(manual_outbound_documents_update_note)
    manual_outbound_documents_update_note.set_defaults(
        func=document_intake_writes_cmd.cmd_manual_outbound_documents_update_note,
        write_capable=True,
    )
    manual_outbound_documents_release = manual_outbound_documents_sub.add_parser(
        "release",
        help="Plan or release one manual outbound document from a JSON payload file",
    )
    manual_outbound_documents_release.add_argument("--id", required=True, help="Fortnox manual outbound document id")
    manual_outbound_documents_release.add_argument("--json-file", required=True, help="Path to the manual outbound document JSON payload file")
    _add_local_write_flags(manual_outbound_documents_release)
    manual_outbound_documents_release.set_defaults(
        func=document_intake_writes_cmd.cmd_manual_outbound_documents_release,
        write_capable=True,
    )
    manual_outbound_documents_void = manual_outbound_documents_sub.add_parser(
        "void",
        help="Plan or void one manual outbound document from a JSON payload file",
    )
    manual_outbound_documents_void.add_argument("--id", required=True, help="Fortnox manual outbound document id")
    manual_outbound_documents_void.add_argument("--json-file", required=True, help="Path to the manual outbound document JSON payload file")
    _add_local_write_flags(manual_outbound_documents_void)
    manual_outbound_documents_void.set_defaults(
        func=document_intake_writes_cmd.cmd_manual_outbound_documents_void,
        write_capable=True,
    )

    email_senders = sub.add_parser("email-senders", help="Trusted sender reads and writes")
    email_senders_sub = email_senders.add_subparsers(
        dest="email_senders_cmd", required=True, parser_class=_ToolArgumentParser
    )
    email_senders_list = email_senders_sub.add_parser(
        "list",
        help="Retrieve trusted and rejected email senders",
    )
    email_senders_list.set_defaults(func=accounting_reads_cmd.cmd_email_senders_list, write_capable=False)
    email_senders_add_trusted = email_senders_sub.add_parser(
        "add-a-new-email-address-as-trusted",
        help="Plan or add one trusted sender from a JSON payload file",
    )
    email_senders_add_trusted.add_argument("--json-file", required=True, help="Path to the TrustedSender JSON payload file")
    _add_local_write_flags(email_senders_add_trusted)
    email_senders_add_trusted.set_defaults(
        func=document_intake_writes_cmd.cmd_email_senders_add_trusted,
        write_capable=True,
    )
    email_senders_delete = email_senders_sub.add_parser(
        "delete",
        help="Plan or delete one trusted sender by id",
    )
    email_senders_delete.add_argument("--id", required=True, help="Fortnox trusted sender id")
    _add_local_write_flags(email_senders_delete)
    email_senders_delete.set_defaults(
        func=document_intake_writes_cmd.cmd_email_senders_delete,
        write_capable=True,
    )

    locked_period = sub.add_parser("locked-period", help="Locked-period reads")
    locked_period_sub = locked_period.add_subparsers(
        dest="locked_period_cmd", required=True, parser_class=_ToolArgumentParser
    )
    locked_period_get = locked_period_sub.add_parser("get", help="Retrieve the locked period")
    locked_period_get.set_defaults(func=accounting_reads_cmd.cmd_locked_period_get, write_capable=False)

    print_templates = sub.add_parser("print-templates", help="Print-template reads")
    print_templates_sub = print_templates.add_subparsers(
        dest="print_templates_cmd", required=True, parser_class=_ToolArgumentParser
    )
    print_templates_list = print_templates_sub.add_parser("list", help="List print templates")
    print_templates_list.set_defaults(func=accounting_reads_cmd.cmd_print_templates_list, write_capable=False)

    labels = sub.add_parser("labels", help="Label reads and writes")
    labels_sub = labels.add_subparsers(dest="labels_cmd", required=True, parser_class=_ToolArgumentParser)
    labels_list = labels_sub.add_parser("list", help="List labels")
    labels_list.set_defaults(func=labels_cmd.cmd_labels_list, write_capable=False)
    labels_create = labels_sub.add_parser(
        "create",
        help="Plan or create one label from a JSON payload file",
    )
    labels_create.add_argument("--json-file", required=True, help="Path to the Label JSON payload file")
    _add_local_write_flags(labels_create)
    labels_create.set_defaults(func=labels_cmd.cmd_labels_create, write_capable=True)
    labels_update = labels_sub.add_parser(
        "update",
        help="Plan or update one label from a JSON payload file",
    )
    labels_update.add_argument("--id", required=True, help="Fortnox label id")
    labels_update.add_argument("--json-file", required=True, help="Path to the Label JSON payload file")
    _add_local_write_flags(labels_update)
    labels_update.set_defaults(func=labels_cmd.cmd_labels_update, write_capable=True)
    labels_delete = labels_sub.add_parser("delete", help="Plan or delete one label")
    labels_delete.add_argument("--id", required=True, help="Fortnox label id")
    _add_local_write_flags(labels_delete)
    labels_delete.set_defaults(func=labels_cmd.cmd_labels_delete, write_capable=True)

    customer_references = sub.add_parser("customer-references", help="Customer-reference reads and writes")
    customer_references_sub = customer_references.add_subparsers(
        dest="customer_references_cmd", required=True, parser_class=_ToolArgumentParser
    )
    customer_references_list = customer_references_sub.add_parser("list", help="List customer reference rows")
    customer_references_list.set_defaults(func=customer_references_cmd.cmd_customer_references_list, write_capable=False)
    customer_references_get = customer_references_sub.add_parser("get", help="Get one customer reference row")
    customer_references_get.add_argument("--row-id", required=True, help="Fortnox customer reference row id")
    customer_references_get.set_defaults(func=customer_references_cmd.cmd_customer_references_get, write_capable=False)
    customer_references_create = customer_references_sub.add_parser(
        "create",
        help="Plan or create one customer reference row from a JSON payload file",
    )
    customer_references_create.add_argument("--json-file", required=True, help="Path to the CustomerReference JSON payload file")
    _add_local_write_flags(customer_references_create)
    customer_references_create.set_defaults(func=customer_references_cmd.cmd_customer_references_create, write_capable=True)
    customer_references_update = customer_references_sub.add_parser(
        "update",
        help="Plan or update one customer reference row from a JSON payload file",
    )
    customer_references_update.add_argument("--row-id", required=True, help="Fortnox customer reference row id")
    customer_references_update.add_argument("--json-file", required=True, help="Path to the CustomerReference JSON payload file")
    _add_local_write_flags(customer_references_update)
    customer_references_update.set_defaults(func=customer_references_cmd.cmd_customer_references_update, write_capable=True)
    customer_references_delete = customer_references_sub.add_parser("delete", help="Plan or delete one customer reference row")
    customer_references_delete.add_argument("--row-id", required=True, help="Fortnox customer reference row id")
    _add_local_write_flags(customer_references_delete)
    customer_references_delete.set_defaults(func=customer_references_cmd.cmd_customer_references_delete, write_capable=True)

    expenses = sub.add_parser("expenses", help="Expense reads and writes")
    expenses_sub = expenses.add_subparsers(dest="expenses_cmd", required=True, parser_class=_ToolArgumentParser)
    expenses_list = expenses_sub.add_parser("list", help="List expenses")
    expenses_list.set_defaults(func=expenses_cmd.cmd_expenses_list, write_capable=False)
    expenses_get = expenses_sub.add_parser("get", help="Get one expense")
    expenses_get.add_argument("--expense-code", required=True, help="Fortnox expense code")
    expenses_get.set_defaults(func=expenses_cmd.cmd_expenses_get, write_capable=False)
    expenses_create = expenses_sub.add_parser(
        "create",
        help="Plan or create one expense from a JSON payload file",
    )
    expenses_create.add_argument("--json-file", required=True, help="Path to the Expense JSON payload file")
    _add_local_write_flags(expenses_create)
    expenses_create.set_defaults(func=expenses_cmd.cmd_expenses_create, write_capable=True)

    customers = sub.add_parser("customers", help="Customer reads")
    customers_sub = customers.add_subparsers(dest="customers_cmd", required=True, parser_class=_ToolArgumentParser)
    customers_list = customers_sub.add_parser("list", help="List customers")
    customers_list.add_argument("--filter", choices=["active", "inactive"], help="Optional official customer filter")
    customers_list.add_argument(
        "--sort-by",
        choices=["customernumber", "name"],
        help="Optional official customer sort field",
    )
    customers_list.add_argument("--customer-number", help="Optional official customer-number filter")
    customers_list.add_argument("--name", help="Optional official name filter")
    customers_list.add_argument("--zip-code", help="Optional official zip-code filter")
    customers_list.add_argument("--city", help="Optional official city filter")
    customers_list.add_argument("--email", help="Optional official email filter")
    customers_list.add_argument("--phone", help="Optional official phone filter")
    customers_list.add_argument("--organisation-number", help="Optional official organisation-number filter")
    customers_list.add_argument("--gln", help="Optional official GLN filter")
    customers_list.add_argument("--gln-delivery", help="Optional official GLN delivery filter")
    customers_list.add_argument("--last-modified", help="Optional official last-modified filter")
    customers_list.set_defaults(func=accounting_reads_cmd.cmd_customers_list, write_capable=False)
    customers_get = customers_sub.add_parser("get", help="Get one customer")
    customers_get.add_argument("--customer-number", required=True, help="Fortnox customer number")
    customers_get.set_defaults(func=accounting_reads_cmd.cmd_customers_get, write_capable=False)
    customers_create = customers_sub.add_parser(
        "create",
        help="Plan or create one customer from a JSON payload file",
    )
    customers_create.add_argument("--json-file", required=True, help="Path to the Customer JSON payload file")
    _add_local_write_flags(customers_create)
    customers_create.set_defaults(func=customers_cmd.cmd_customers_create, write_capable=True)
    customers_update = customers_sub.add_parser(
        "update",
        help="Plan or update one customer from a JSON payload file",
    )
    customers_update.add_argument("--customer-number", required=True, help="Fortnox customer number")
    customers_update.add_argument("--json-file", required=True, help="Path to the Customer JSON payload file")
    _add_local_write_flags(customers_update)
    customers_update.set_defaults(func=customers_cmd.cmd_customers_update, write_capable=True)
    customers_delete = customers_sub.add_parser("delete", help="Plan or delete one customer")
    customers_delete.add_argument("--customer-number", required=True, help="Fortnox customer number")
    _add_local_write_flags(customers_delete)
    customers_delete.set_defaults(func=customers_cmd.cmd_customers_delete, write_capable=True)

    suppliers = sub.add_parser("suppliers", help="Supplier commands")
    suppliers_sub = suppliers.add_subparsers(dest="suppliers_cmd", required=True, parser_class=_ToolArgumentParser)
    suppliers_list = suppliers_sub.add_parser("list", help="List suppliers")
    suppliers_list.add_argument("--supplier-number", help="Optional official supplier-number filter")
    suppliers_list.add_argument("--name", help="Optional official name filter")
    suppliers_list.add_argument("--organisation-number", help="Optional official organisation-number filter")
    suppliers_list.add_argument("--phone", help="Optional official phone filter")
    suppliers_list.add_argument("--zip-code", help="Optional official zip-code filter")
    suppliers_list.add_argument("--city", help="Optional official city filter")
    suppliers_list.add_argument("--email", help="Optional official email filter")
    suppliers_list.add_argument("--last-modified", help="Optional official last-modified filter")
    suppliers_list.set_defaults(func=accounting_reads_cmd.cmd_suppliers_list, write_capable=False)
    suppliers_get = suppliers_sub.add_parser("get", help="Get one supplier")
    suppliers_get.add_argument("--supplier-number", required=True, help="Fortnox supplier number")
    suppliers_get.set_defaults(func=accounting_reads_cmd.cmd_suppliers_get, write_capable=False)
    suppliers_create = suppliers_sub.add_parser(
        "create",
        help="Plan or create one supplier from a JSON payload file",
    )
    suppliers_create.add_argument("--json-file", required=True, help="Path to the Supplier JSON payload file")
    _add_local_write_flags(suppliers_create)
    suppliers_create.set_defaults(func=suppliers_cmd.cmd_suppliers_create, write_capable=True)
    suppliers_update = suppliers_sub.add_parser(
        "update",
        help="Plan or update one supplier from a JSON payload file",
    )
    suppliers_update.add_argument("--supplier-number", required=True, help="Fortnox supplier number")
    suppliers_update.add_argument("--json-file", required=True, help="Path to the Supplier JSON payload file")
    _add_local_write_flags(suppliers_update)
    suppliers_update.set_defaults(func=suppliers_cmd.cmd_suppliers_update, write_capable=True)

    supplier_invoice_external_url_connections = sub.add_parser(
        "supplier-invoice-external-url-connections",
        help="Supplier invoice external URL connection commands",
    )
    supplier_invoice_external_url_connections_sub = supplier_invoice_external_url_connections.add_subparsers(
        dest="supplier_invoice_external_url_connections_cmd", required=True, parser_class=_ToolArgumentParser
    )
    supplier_invoice_external_url_connections_get = supplier_invoice_external_url_connections_sub.add_parser(
        "get",
        help="Get one supplier invoice external URL connection",
    )
    supplier_invoice_external_url_connections_get.add_argument("--id", required=True, help="Fortnox external URL connection id")
    supplier_invoice_external_url_connections_get.set_defaults(
        func=supplier_invoice_external_url_connections_cmd.cmd_supplier_invoice_external_url_connections_get,
        write_capable=False,
    )
    supplier_invoice_external_url_connections_create = supplier_invoice_external_url_connections_sub.add_parser(
        "create",
        help="Plan or create one supplier invoice external URL connection from a JSON payload file",
    )
    supplier_invoice_external_url_connections_create.add_argument(
        "--json-file",
        required=True,
        help="Path to the supplier invoice external URL connection JSON payload file",
    )
    _add_local_write_flags(supplier_invoice_external_url_connections_create)
    supplier_invoice_external_url_connections_create.set_defaults(
        func=supplier_invoice_external_url_connections_cmd.cmd_supplier_invoice_external_url_connections_create,
        write_capable=True,
    )
    supplier_invoice_external_url_connections_update = supplier_invoice_external_url_connections_sub.add_parser(
        "update",
        help="Plan or update one supplier invoice external URL connection from a JSON payload file",
    )
    supplier_invoice_external_url_connections_update.add_argument(
        "--id",
        required=True,
        help="Fortnox external URL connection id",
    )
    supplier_invoice_external_url_connections_update.add_argument(
        "--json-file",
        required=True,
        help="Path to the supplier invoice external URL connection JSON payload file",
    )
    _add_local_write_flags(supplier_invoice_external_url_connections_update)
    supplier_invoice_external_url_connections_update.set_defaults(
        func=supplier_invoice_external_url_connections_cmd.cmd_supplier_invoice_external_url_connections_update,
        write_capable=True,
    )
    supplier_invoice_external_url_connections_remove = supplier_invoice_external_url_connections_sub.add_parser(
        "remove",
        help="Plan or remove one supplier invoice external URL connection",
    )
    supplier_invoice_external_url_connections_remove.add_argument(
        "--id",
        required=True,
        help="Fortnox external URL connection id",
    )
    _add_local_write_flags(supplier_invoice_external_url_connections_remove)
    supplier_invoice_external_url_connections_remove.set_defaults(
        func=supplier_invoice_external_url_connections_cmd.cmd_supplier_invoice_external_url_connections_remove,
        write_capable=True,
    )

    supplier_invoice_file_connections = sub.add_parser(
        "supplier-invoice-file-connections",
        help="Supplier invoice file connection commands",
    )
    supplier_invoice_file_connections_sub = supplier_invoice_file_connections.add_subparsers(
        dest="supplier_invoice_file_connections_cmd", required=True, parser_class=_ToolArgumentParser
    )
    supplier_invoice_file_connections_list = supplier_invoice_file_connections_sub.add_parser(
        "list",
        help="List supplier invoice file connections",
    )
    supplier_invoice_file_connections_list.add_argument(
        "--supplier-invoice-number",
        type=int,
        help="Filter by Fortnox supplier invoice number",
    )
    supplier_invoice_file_connections_list.set_defaults(
        func=supplier_invoice_file_connections_cmd.cmd_supplier_invoice_file_connections_list,
        write_capable=False,
    )
    supplier_invoice_file_connections_get = supplier_invoice_file_connections_sub.add_parser(
        "get",
        help="Get one supplier invoice file connection",
    )
    supplier_invoice_file_connections_get.add_argument("--file-id", required=True, help="Fortnox file id")
    supplier_invoice_file_connections_get.set_defaults(
        func=supplier_invoice_file_connections_cmd.cmd_supplier_invoice_file_connections_get,
        write_capable=False,
    )
    supplier_invoice_file_connections_create = supplier_invoice_file_connections_sub.add_parser(
        "create",
        help="Plan or create one supplier invoice file connection from a JSON payload file",
    )
    supplier_invoice_file_connections_create.add_argument(
        "--json-file",
        required=True,
        help="Path to the supplier invoice file connection JSON payload file",
    )
    _add_local_write_flags(supplier_invoice_file_connections_create)
    supplier_invoice_file_connections_create.set_defaults(
        func=supplier_invoice_file_connections_cmd.cmd_supplier_invoice_file_connections_create,
        write_capable=True,
    )
    supplier_invoice_file_connections_remove = supplier_invoice_file_connections_sub.add_parser(
        "remove",
        help="Plan or remove one supplier invoice file connection",
    )
    supplier_invoice_file_connections_remove.add_argument("--file-id", required=True, help="Fortnox file id")
    _add_local_write_flags(supplier_invoice_file_connections_remove)
    supplier_invoice_file_connections_remove.set_defaults(
        func=supplier_invoice_file_connections_cmd.cmd_supplier_invoice_file_connections_remove,
        write_capable=True,
    )

    tax_reductions = sub.add_parser("tax-reductions", help="Tax-reduction reads and writes")
    tax_reductions_sub = tax_reductions.add_subparsers(
        dest="tax_reductions_cmd", required=True, parser_class=_ToolArgumentParser
    )
    tax_reductions_list = tax_reductions_sub.add_parser("list", help="List tax reductions")
    tax_reductions_list.set_defaults(func=tax_reductions_cmd.cmd_tax_reductions_list, write_capable=False)
    tax_reductions_get = tax_reductions_sub.add_parser("get", help="Get one tax reduction")
    tax_reductions_get.add_argument("--id", required=True, help="Fortnox tax reduction id")
    tax_reductions_get.set_defaults(func=tax_reductions_cmd.cmd_tax_reductions_get, write_capable=False)
    tax_reductions_create = tax_reductions_sub.add_parser(
        "create",
        help="Plan or create one tax reduction from a JSON payload file",
    )
    tax_reductions_create.add_argument("--json-file", required=True, help="Path to the TaxReduction JSON payload file")
    _add_local_write_flags(tax_reductions_create)
    tax_reductions_create.set_defaults(func=tax_reductions_cmd.cmd_tax_reductions_create, write_capable=True)
    tax_reductions_update = tax_reductions_sub.add_parser(
        "update",
        help="Plan or update one tax reduction from a JSON payload file",
    )
    tax_reductions_update.add_argument("--id", required=True, help="Fortnox tax reduction id")
    tax_reductions_update.add_argument("--json-file", required=True, help="Path to the TaxReduction JSON payload file")
    _add_local_write_flags(tax_reductions_update)
    tax_reductions_update.set_defaults(func=tax_reductions_cmd.cmd_tax_reductions_update, write_capable=True)
    tax_reductions_remove = tax_reductions_sub.add_parser("remove", help="Plan or remove one tax reduction")
    tax_reductions_remove.add_argument("--id", required=True, help="Fortnox tax reduction id")
    _add_local_write_flags(tax_reductions_remove)
    tax_reductions_remove.set_defaults(func=tax_reductions_cmd.cmd_tax_reductions_remove, write_capable=True)

    employees = sub.add_parser("employees", help="Employee commands")
    employees_sub = employees.add_subparsers(dest="employees_cmd", required=True, parser_class=_ToolArgumentParser)
    employees_list = employees_sub.add_parser("list", help="List employees")
    employees_list.set_defaults(func=accounting_reads_cmd.cmd_employees_list, write_capable=False)
    employees_get = employees_sub.add_parser("get", help="Get one employee")
    employees_get.add_argument("--employee-id", required=True, help="Fortnox employee id")
    employees_get.set_defaults(func=accounting_reads_cmd.cmd_employees_get, write_capable=False)
    employees_create = employees_sub.add_parser(
        "create",
        help="Create an employee from a reviewed JSON payload",
    )
    employees_create.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level Employee object",
    )
    _add_local_write_flags(employees_create)
    employees_create.set_defaults(func=employees_cmd.cmd_employees_create, write_capable=True)
    employees_update = employees_sub.add_parser(
        "update",
        help="Update an employee from a reviewed JSON payload",
    )
    employees_update.add_argument("--employee-id", required=True, help="Fortnox employee id")
    employees_update.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level Employee object",
    )
    _add_local_write_flags(employees_update)
    employees_update.set_defaults(func=employees_cmd.cmd_employees_update, write_capable=True)

    absence_transactions = sub.add_parser("absence-transactions", help="Absence-transaction reads and writes")
    absence_transactions_sub = absence_transactions.add_subparsers(
        dest="absence_transactions_cmd", required=True, parser_class=_ToolArgumentParser
    )
    absence_transactions_list = absence_transactions_sub.add_parser("list", help="List absence transactions")
    absence_transactions_list.set_defaults(func=accounting_reads_cmd.cmd_absence_transactions_list, write_capable=False)
    absence_transactions_get = absence_transactions_sub.add_parser("get", help="Get one absence transaction by transaction id")
    absence_transactions_get.add_argument("--id", required=True, help="Fortnox absence-transaction id")
    absence_transactions_get.set_defaults(func=accounting_reads_cmd.cmd_absence_transactions_get, write_capable=False)
    absence_transactions_get_by_employee_date_code = absence_transactions_sub.add_parser(
        "get-by-employee-date-code",
        help="Get absence transactions for one employee, date, and cause code",
    )
    absence_transactions_get_by_employee_date_code.add_argument("--employee-id", required=True, help="Fortnox employee id")
    absence_transactions_get_by_employee_date_code.add_argument("--date", required=True, help="Fortnox date value (YYYY-MM-DD)")
    absence_transactions_get_by_employee_date_code.add_argument("--code", required=True, help="Fortnox cause code")
    absence_transactions_get_by_employee_date_code.set_defaults(
        func=accounting_reads_cmd.cmd_absence_transactions_get_by_employee_date_code,
        write_capable=False,
    )
    absence_transactions_create = absence_transactions_sub.add_parser(
        "create",
        help="Create an absence transaction from a reviewed JSON payload",
    )
    absence_transactions_create.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level AbsenceTransaction object",
    )
    _add_local_write_flags(absence_transactions_create)
    absence_transactions_create.set_defaults(func=absence_transactions_cmd.cmd_absence_transactions_create, write_capable=True)
    absence_transactions_update = absence_transactions_sub.add_parser(
        "update",
        help="Update an absence transaction from a reviewed JSON payload",
    )
    absence_transactions_update.add_argument("--id", required=True, help="Fortnox absence-transaction id")
    absence_transactions_update.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level AbsenceTransaction object",
    )
    _add_local_write_flags(absence_transactions_update)
    absence_transactions_update.set_defaults(func=absence_transactions_cmd.cmd_absence_transactions_update, write_capable=True)
    absence_transactions_delete = absence_transactions_sub.add_parser(
        "delete",
        help="Delete an absence transaction after dry-run plan review",
    )
    absence_transactions_delete.add_argument("--id", required=True, help="Fortnox absence-transaction id")
    _add_local_write_flags(absence_transactions_delete)
    absence_transactions_delete.set_defaults(func=absence_transactions_cmd.cmd_absence_transactions_delete, write_capable=True)

    attendance_transactions = sub.add_parser("attendance-transactions", help="Attendance-transaction reads and writes")
    attendance_transactions_sub = attendance_transactions.add_subparsers(
        dest="attendance_transactions_cmd", required=True, parser_class=_ToolArgumentParser
    )
    attendance_transactions_list = attendance_transactions_sub.add_parser("list", help="List attendance transactions")
    attendance_transactions_list.set_defaults(func=accounting_reads_cmd.cmd_attendance_transactions_list, write_capable=False)
    attendance_transactions_get = attendance_transactions_sub.add_parser("get", help="Get one attendance transaction by transaction id")
    attendance_transactions_get.add_argument("--id", required=True, help="Fortnox attendance-transaction id")
    attendance_transactions_get.set_defaults(func=accounting_reads_cmd.cmd_attendance_transactions_get, write_capable=False)
    attendance_transactions_get_by_employee_date_code = attendance_transactions_sub.add_parser(
        "get-by-employee-date-code",
        help="Get attendance transactions for one employee, date, and cause code",
    )
    attendance_transactions_get_by_employee_date_code.add_argument("--employee-id", required=True, help="Fortnox employee id")
    attendance_transactions_get_by_employee_date_code.add_argument("--date", required=True, help="Fortnox date value (YYYY-MM-DD)")
    attendance_transactions_get_by_employee_date_code.add_argument("--code", required=True, help="Fortnox cause code")
    attendance_transactions_get_by_employee_date_code.set_defaults(
        func=accounting_reads_cmd.cmd_attendance_transactions_get_by_employee_date_code,
        write_capable=False,
    )
    attendance_transactions_create = attendance_transactions_sub.add_parser(
        "create",
        help="Create an attendance transaction from a reviewed JSON payload",
    )
    attendance_transactions_create.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level AttendanceTransaction object",
    )
    _add_local_write_flags(attendance_transactions_create)
    attendance_transactions_create.set_defaults(
        func=attendance_transactions_cmd.cmd_attendance_transactions_create,
        write_capable=True,
    )
    attendance_transactions_update = attendance_transactions_sub.add_parser(
        "update",
        help="Update an attendance transaction from a reviewed JSON payload",
    )
    attendance_transactions_update.add_argument("--id", required=True, help="Fortnox attendance-transaction id")
    attendance_transactions_update.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level AttendanceTransaction object",
    )
    _add_local_write_flags(attendance_transactions_update)
    attendance_transactions_update.set_defaults(
        func=attendance_transactions_cmd.cmd_attendance_transactions_update,
        write_capable=True,
    )
    attendance_transactions_delete = attendance_transactions_sub.add_parser(
        "delete",
        help="Delete an attendance transaction after dry-run plan review",
    )
    attendance_transactions_delete.add_argument("--id", required=True, help="Fortnox attendance-transaction id")
    _add_local_write_flags(attendance_transactions_delete)
    attendance_transactions_delete.set_defaults(
        func=attendance_transactions_cmd.cmd_attendance_transactions_delete,
        write_capable=True,
    )

    salary_transactions = sub.add_parser("salary-transactions", help="Salary-transaction reads and writes")
    salary_transactions_sub = salary_transactions.add_subparsers(
        dest="salary_transactions_cmd", required=True, parser_class=_ToolArgumentParser
    )
    salary_transactions_list = salary_transactions_sub.add_parser("list", help="List salary transactions")
    salary_transactions_list.set_defaults(func=accounting_reads_cmd.cmd_salary_transactions_list, write_capable=False)
    salary_transactions_get = salary_transactions_sub.add_parser("get", help="Get one salary transaction")
    salary_transactions_get.add_argument("--salary-row", required=True, help="Fortnox salary-row value")
    salary_transactions_get.set_defaults(func=accounting_reads_cmd.cmd_salary_transactions_get, write_capable=False)
    salary_transactions_create = salary_transactions_sub.add_parser(
        "create",
        help="Create a salary transaction from a reviewed JSON payload",
    )
    salary_transactions_create.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level SalaryTransaction object",
    )
    _add_local_write_flags(salary_transactions_create)
    salary_transactions_create.set_defaults(func=salary_transactions_cmd.cmd_salary_transactions_create, write_capable=True)
    salary_transactions_update = salary_transactions_sub.add_parser(
        "update",
        help="Update a salary transaction from a reviewed JSON payload",
    )
    salary_transactions_update.add_argument("--salary-row", required=True, help="Fortnox salary-row value")
    salary_transactions_update.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level SalaryTransaction object",
    )
    _add_local_write_flags(salary_transactions_update)
    salary_transactions_update.set_defaults(func=salary_transactions_cmd.cmd_salary_transactions_update, write_capable=True)
    salary_transactions_delete = salary_transactions_sub.add_parser(
        "delete",
        help="Delete a salary transaction after dry-run plan review",
    )
    salary_transactions_delete.add_argument("--salary-row", required=True, help="Fortnox salary-row value")
    _add_local_write_flags(salary_transactions_delete)
    salary_transactions_delete.set_defaults(func=salary_transactions_cmd.cmd_salary_transactions_delete, write_capable=True)

    schedule_times = sub.add_parser("schedule-times", help="Schedule-time reads and writes")
    schedule_times_sub = schedule_times.add_subparsers(
        dest="schedule_times_cmd", required=True, parser_class=_ToolArgumentParser
    )
    schedule_times_get = schedule_times_sub.add_parser("get", help="Get one schedule-time record")
    schedule_times_get.add_argument("--employee-id", required=True, help="Fortnox employee id")
    schedule_times_get.add_argument("--date", required=True, help="Fortnox date value (YYYY-MM-DD)")
    schedule_times_get.set_defaults(func=accounting_reads_cmd.cmd_schedule_times_get, write_capable=False)
    schedule_times_update = schedule_times_sub.add_parser(
        "update",
        help="Update a schedule-time record from a reviewed JSON payload",
    )
    schedule_times_update.add_argument("--employee-id", required=True, help="Fortnox employee id")
    schedule_times_update.add_argument("--date", required=True, help="Fortnox date value (YYYY-MM-DD)")
    schedule_times_update.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level ScheduleTime object",
    )
    _add_local_write_flags(schedule_times_update)
    schedule_times_update.set_defaults(func=schedule_times_cmd.cmd_schedule_times_update, write_capable=True)
    schedule_times_reset_day = schedule_times_sub.add_parser(
        "reset-day",
        help="Reset a schedule-time record from a reviewed JSON payload",
    )
    schedule_times_reset_day.add_argument("--employee-id", required=True, help="Fortnox employee id")
    schedule_times_reset_day.add_argument("--date", required=True, help="Fortnox date value (YYYY-MM-DD)")
    schedule_times_reset_day.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level ScheduleTime object",
    )
    _add_local_write_flags(schedule_times_reset_day)
    schedule_times_reset_day.set_defaults(func=schedule_times_cmd.cmd_schedule_times_reset_day, write_capable=True)

    registrations = sub.add_parser("registrations", help="Time-registration reads")
    registrations_sub = registrations.add_subparsers(dest="registrations_cmd", required=True, parser_class=_ToolArgumentParser)
    registrations_get = registrations_sub.add_parser("get", help="Get time and absence registrations")
    registrations_get.set_defaults(func=accounting_reads_cmd.cmd_registrations_get, write_capable=False)

    vacation_debt_basis = sub.add_parser("vacation-debt-basis", help="Vacation-debt-basis reads")
    vacation_debt_basis_sub = vacation_debt_basis.add_subparsers(
        dest="vacation_debt_basis_cmd", required=True, parser_class=_ToolArgumentParser
    )
    vacation_debt_basis_get = vacation_debt_basis_sub.add_parser("get", help="Get one vacation-debt-basis record")
    vacation_debt_basis_get.add_argument("--year", required=True, help="Fortnox year value")
    vacation_debt_basis_get.add_argument("--month", required=True, help="Fortnox month value")
    vacation_debt_basis_get.set_defaults(func=accounting_reads_cmd.cmd_vacation_debt_basis_get, write_capable=False)

    articles = sub.add_parser("articles", help="Article commands")
    articles_sub = articles.add_subparsers(dest="articles_cmd", required=True, parser_class=_ToolArgumentParser)
    articles_list = articles_sub.add_parser("list", help="List articles")
    articles_list.add_argument("--filter", choices=["active", "inactive"], help="Optional official article filter")
    articles_list.add_argument(
        "--sort-by",
        choices=["articlenumber", "quantityinstock", "reservedquantity", "stockvalue"],
        help="Optional official article sort field",
    )
    articles_list.add_argument("--article-number", help="Optional official article-number filter")
    articles_list.add_argument("--description", help="Optional official description filter")
    articles_list.add_argument("--ean", help="Optional official EAN filter")
    articles_list.add_argument("--supplier-number", help="Optional official supplier-number filter")
    articles_list.add_argument("--manufacturer", help="Optional official manufacturer filter")
    articles_list.add_argument(
        "--manufacturer-article-number",
        help="Optional official manufacturer article number filter",
    )
    articles_list.add_argument("--webshop", help="Optional official webshop filter")
    articles_list.add_argument("--last-modified", help="Optional official last-modified filter")
    articles_list.set_defaults(func=accounting_reads_cmd.cmd_articles_list, write_capable=False)
    articles_get = articles_sub.add_parser("get", help="Get one article")
    articles_get.add_argument("--article-number", required=True, help="Fortnox article number")
    articles_get.set_defaults(func=accounting_reads_cmd.cmd_articles_get, write_capable=False)
    articles_list_time_article_registrations = articles_sub.add_parser(
        "list-time-article-registrations",
        help="List full time-reporting article registrations that match the documented filters",
    )
    articles_list_time_article_registrations.add_argument("--from-date", default=None, help="Optional official fromDate filter in YYYY-MM-DD")
    articles_list_time_article_registrations.add_argument("--to-date", default=None, help="Optional official toDate filter in YYYY-MM-DD")
    articles_list_time_article_registrations.add_argument("--customer-id", action="append", default=None, help="Optional repeated official customerIds filter")
    articles_list_time_article_registrations.add_argument("--project-id", action="append", default=None, help="Optional repeated official projectIds filter")
    articles_list_time_article_registrations.add_argument("--item-id", action="append", default=None, help="Optional repeated official itemIds filter")
    articles_list_time_article_registrations.add_argument("--cost-center-id", action="append", default=None, help="Optional repeated official costCenterIds filter")
    articles_list_time_article_registrations.add_argument("--owner-id", action="append", default=None, help="Optional repeated official ownerIds filter")
    _add_bool_choice_flag(
        articles_list_time_article_registrations,
        "--include-registrations-without-project",
        dest="include_registrations_without_project",
        help_text="Optional official includeRegistrationsWithoutProject filter",
    )
    _add_bool_choice_flag(
        articles_list_time_article_registrations,
        "--invoiced",
        dest="invoiced",
        help_text="Optional official invoiced filter",
    )
    _add_bool_choice_flag(
        articles_list_time_article_registrations,
        "--in-invoice-basis",
        dest="in_invoice_basis",
        help_text="Optional official inInvoiceBasis filter",
    )
    _add_bool_choice_flag(
        articles_list_time_article_registrations,
        "--internal-articles",
        dest="internal_articles",
        help_text="Optional official internalArticles filter",
    )
    _add_bool_choice_flag(
        articles_list_time_article_registrations,
        "--non-invoiceable",
        dest="non_invoiceable",
        help_text="Optional official nonInvoiceable filter",
    )
    _add_bool_choice_flag(
        articles_list_time_article_registrations,
        "--include-non-invoiceable-price",
        dest="include_non_invoiceable_price",
        help_text="Optional official includeNonInvoiceablePrice filter",
    )
    articles_list_time_article_registrations.set_defaults(
        func=accounting_reads_cmd.cmd_articles_list_time_article_registrations,
        write_capable=False,
    )
    articles_create = articles_sub.add_parser(
        "create",
        help="Plan or create one article from a JSON payload file",
    )
    articles_create.add_argument("--json-file", required=True, help="Path to the Article JSON payload file")
    _add_local_write_flags(articles_create)
    articles_create.set_defaults(func=articles_cmd.cmd_articles_create, write_capable=True)
    articles_update = articles_sub.add_parser(
        "update",
        help="Plan or update one article from a JSON payload file",
    )
    articles_update.add_argument("--article-number", required=True, help="Fortnox article number")
    articles_update.add_argument("--json-file", required=True, help="Path to the Article JSON payload file")
    _add_local_write_flags(articles_update)
    articles_update.set_defaults(func=articles_cmd.cmd_articles_update, write_capable=True)
    articles_delete = articles_sub.add_parser("delete", help="Plan or delete one article")
    articles_delete.add_argument("--article-number", required=True, help="Fortnox article number")
    _add_local_write_flags(articles_delete)
    articles_delete.set_defaults(func=articles_cmd.cmd_articles_delete, write_capable=True)

    price_lists = sub.add_parser("price-lists", help="Price list commands")
    price_lists_sub = price_lists.add_subparsers(dest="price_lists_cmd", required=True, parser_class=_ToolArgumentParser)
    price_lists_list = price_lists_sub.add_parser("list", help="List price lists")
    price_lists_list.set_defaults(func=accounting_reads_cmd.cmd_price_lists_list, write_capable=False)
    price_lists_get = price_lists_sub.add_parser("get", help="Get one price list")
    price_lists_get.add_argument("--code", required=True, help="Fortnox price-list code")
    price_lists_get.set_defaults(func=accounting_reads_cmd.cmd_price_lists_get, write_capable=False)
    price_lists_create = price_lists_sub.add_parser(
        "create",
        help="Plan or create one price list from a JSON payload file",
    )
    price_lists_create.add_argument("--json-file", required=True, help="Path to the PriceList JSON payload file")
    _add_local_write_flags(price_lists_create)
    price_lists_create.set_defaults(func=price_lists_cmd.cmd_price_lists_create, write_capable=True)
    price_lists_update = price_lists_sub.add_parser(
        "update",
        help="Plan or update one price list from a JSON payload file",
    )
    price_lists_update.add_argument("--code", required=True, help="Fortnox price-list code")
    price_lists_update.add_argument("--json-file", required=True, help="Path to the PriceList JSON payload file")
    _add_local_write_flags(price_lists_update)
    price_lists_update.set_defaults(func=price_lists_cmd.cmd_price_lists_update, write_capable=True)

    prices = sub.add_parser("prices", help="Price commands")
    prices_sub = prices.add_subparsers(dest="prices_cmd", required=True, parser_class=_ToolArgumentParser)
    prices_list = prices_sub.add_parser("list", help="List prices")
    prices_list.set_defaults(func=accounting_reads_cmd.cmd_prices_list, write_capable=False)
    prices_get = prices_sub.add_parser("get", help="Get the first price for one article in one price list")
    prices_get.add_argument("--price-list", required=True, help="Fortnox price-list code")
    prices_get.add_argument("--article-number", required=True, help="Fortnox article number")
    prices_get.set_defaults(func=accounting_reads_cmd.cmd_prices_get, write_capable=False)
    prices_get_by_from_quantity = prices_sub.add_parser("get-by-from-quantity", help="Get one price by from-quantity")
    prices_get_by_from_quantity.add_argument("--price-list", required=True, help="Fortnox price-list code")
    prices_get_by_from_quantity.add_argument("--article-number", required=True, help="Fortnox article number")
    prices_get_by_from_quantity.add_argument("--from-quantity", required=True, help="Fortnox from-quantity value")
    prices_get_by_from_quantity.set_defaults(func=accounting_reads_cmd.cmd_prices_get_by_from_quantity, write_capable=False)
    prices_list_sublist = prices_sub.add_parser("list-sublist", help="List all prices for one article inside one price list")
    prices_list_sublist.add_argument("--price-list", required=True, help="Fortnox price-list code")
    prices_list_sublist.add_argument("--article-number", required=True, help="Fortnox article number")
    prices_list_sublist.set_defaults(func=accounting_reads_cmd.cmd_prices_list_sublist, write_capable=False)
    prices_create = prices_sub.add_parser("create", help="Plan or create one price from a JSON payload file")
    prices_create.add_argument("--json-file", required=True, help="Path to the Price JSON payload file")
    _add_local_write_flags(prices_create)
    prices_create.set_defaults(func=prices_cmd.cmd_prices_create, write_capable=True)
    prices_update = prices_sub.add_parser("update", help="Plan or update the first price for one article")
    prices_update.add_argument("--price-list", required=True, help="Fortnox price-list code")
    prices_update.add_argument("--article-number", required=True, help="Fortnox article number")
    prices_update.add_argument("--json-file", required=True, help="Path to the Price JSON payload file")
    _add_local_write_flags(prices_update)
    prices_update.set_defaults(func=prices_cmd.cmd_prices_update, write_capable=True)
    prices_update_by_from_quantity = prices_sub.add_parser(
        "update-by-from-quantity",
        help="Plan or update one price by from-quantity",
    )
    prices_update_by_from_quantity.add_argument("--price-list", required=True, help="Fortnox price-list code")
    prices_update_by_from_quantity.add_argument("--article-number", required=True, help="Fortnox article number")
    prices_update_by_from_quantity.add_argument("--from-quantity", required=True, help="Fortnox from-quantity value")
    prices_update_by_from_quantity.add_argument("--json-file", required=True, help="Path to the Price JSON payload file")
    _add_local_write_flags(prices_update_by_from_quantity)
    prices_update_by_from_quantity.set_defaults(func=prices_cmd.cmd_prices_update_by_from_quantity, write_capable=True)
    prices_delete = prices_sub.add_parser("delete", help="Plan or delete one price by from-quantity")
    prices_delete.add_argument("--price-list", required=True, help="Fortnox price-list code")
    prices_delete.add_argument("--article-number", required=True, help="Fortnox article number")
    prices_delete.add_argument("--from-quantity", required=True, help="Fortnox from-quantity value")
    _add_local_write_flags(prices_delete)
    prices_delete.set_defaults(func=prices_cmd.cmd_prices_delete, write_capable=True)

    projects = sub.add_parser("projects", help="Project reads and writes")
    projects_sub = projects.add_subparsers(dest="projects_cmd", required=True, parser_class=_ToolArgumentParser)
    projects_list = projects_sub.add_parser("list", help="List projects")
    projects_list.set_defaults(func=accounting_reads_cmd.cmd_projects_list, write_capable=False)
    projects_get = projects_sub.add_parser("get", help="Get one project")
    projects_get.add_argument("--project-number", required=True, help="Fortnox project number")
    projects_get.set_defaults(func=accounting_reads_cmd.cmd_projects_get, write_capable=False)
    projects_create = projects_sub.add_parser(
        "create",
        help="Create a project from a reviewed JSON payload",
    )
    projects_create.add_argument("--json-file", required=True, help="Path to the Project JSON payload file")
    _add_local_write_flags(projects_create)
    projects_create.set_defaults(func=projects_cmd.cmd_projects_create, write_capable=True)
    projects_update = projects_sub.add_parser(
        "update",
        help="Update one project from a reviewed JSON payload",
    )
    projects_update.add_argument("--project-number", required=True, help="Fortnox project number")
    projects_update.add_argument("--json-file", required=True, help="Path to the Project JSON payload file")
    _add_local_write_flags(projects_update)
    projects_update.set_defaults(func=projects_cmd.cmd_projects_update, write_capable=True)
    projects_remove = projects_sub.add_parser(
        "remove",
        help="Remove a project after dry-run plan review",
    )
    projects_remove.add_argument("--project-number", required=True, help="Fortnox project number")
    _add_local_write_flags(projects_remove)
    projects_remove.set_defaults(func=projects_cmd.cmd_projects_remove, write_capable=True)

    purchase_orders = sub.add_parser("purchase-orders", help="Purchase-order commands")
    purchase_orders_sub = purchase_orders.add_subparsers(
        dest="purchase_orders_cmd", required=True, parser_class=_ToolArgumentParser
    )
    purchase_orders_list = purchase_orders_sub.add_parser("list", help="List purchase orders")
    purchase_orders_list.set_defaults(func=purchase_orders_cmd.cmd_purchase_orders_list, write_capable=False)
    purchase_orders_get = purchase_orders_sub.add_parser("get", help="Get one purchase order")
    purchase_orders_get.add_argument("--id", required=True, help="Fortnox purchase-order id")
    purchase_orders_get.set_defaults(func=purchase_orders_cmd.cmd_purchase_orders_get, write_capable=False)
    purchase_orders_get_csv = purchase_orders_sub.add_parser("get-csv", help="Get the purchase-order CSV list")
    purchase_orders_get_csv.set_defaults(func=purchase_orders_cmd.cmd_purchase_orders_get_csv, write_capable=False)
    purchase_orders_get_note = purchase_orders_sub.add_parser("get-note", help="Get attached notes for one purchase order")
    purchase_orders_get_note.add_argument("--id", required=True, help="Fortnox purchase-order id")
    purchase_orders_get_note.set_defaults(func=purchase_orders_cmd.cmd_purchase_orders_get_note, write_capable=False)
    purchase_orders_list_matches = purchase_orders_sub.add_parser(
        "list-matches",
        help="List matched documents for one purchase order",
    )
    purchase_orders_list_matches.add_argument("--id", required=True, help="Fortnox purchase-order id")
    purchase_orders_list_matches.set_defaults(func=purchase_orders_cmd.cmd_purchase_orders_list_matches, write_capable=False)
    purchase_orders_create = purchase_orders_sub.add_parser(
        "create",
        help="Plan or create one purchase order from a JSON payload file",
    )
    purchase_orders_create.add_argument("--json-file", required=True, help="Path to the PurchaseOrder JSON payload file")
    _add_local_write_flags(purchase_orders_create)
    purchase_orders_create.set_defaults(func=purchase_orders_cmd.cmd_purchase_orders_create, write_capable=True)
    purchase_orders_update = purchase_orders_sub.add_parser(
        "update",
        help="Plan or update one purchase order from a JSON payload file",
    )
    purchase_orders_update.add_argument("--id", required=True, help="Fortnox purchase-order id")
    purchase_orders_update.add_argument("--json-file", required=True, help="Path to the PurchaseOrder JSON payload file")
    _add_local_write_flags(purchase_orders_update)
    purchase_orders_update.set_defaults(func=purchase_orders_cmd.cmd_purchase_orders_update, write_capable=True)
    purchase_orders_partial_update = purchase_orders_sub.add_parser(
        "partial-update-purchase-order",
        help="Plan or partially update one purchase order from a JSON payload file",
    )
    purchase_orders_partial_update.add_argument("--id", required=True, help="Fortnox purchase-order id")
    purchase_orders_partial_update.add_argument(
        "--json-file",
        required=True,
        help="Path to the PartialPurchaseOrder JSON payload file",
    )
    _add_local_write_flags(purchase_orders_partial_update)
    purchase_orders_partial_update.set_defaults(
        func=purchase_orders_cmd.cmd_purchase_orders_partial_update,
        write_capable=True,
    )
    purchase_orders_complete_dropship = purchase_orders_sub.add_parser(
        "manually-complete-dropship-order",
        help="Plan or manually complete one dropship purchase order",
    )
    purchase_orders_complete_dropship.add_argument("--id", required=True, help="Fortnox purchase-order id")
    _add_local_write_flags(purchase_orders_complete_dropship)
    purchase_orders_complete_dropship.set_defaults(
        func=purchase_orders_cmd.cmd_purchase_orders_manually_complete_dropship_order,
        write_capable=True,
    )
    purchase_orders_complete = purchase_orders_sub.add_parser(
        "manually-complete-purchase-order",
        help="Plan or manually complete one purchase order",
    )
    purchase_orders_complete.add_argument("--id", required=True, help="Fortnox purchase-order id")
    _add_local_write_flags(purchase_orders_complete)
    purchase_orders_complete.set_defaults(
        func=purchase_orders_cmd.cmd_purchase_orders_manually_complete_purchase_order,
        write_capable=True,
    )
    purchase_orders_send = purchase_orders_sub.add_parser(
        "send-purchase-order-via-email",
        help="Plan or send one purchase order via email from a JSON payload file",
    )
    purchase_orders_send.add_argument("--id", required=True, help="Fortnox purchase-order id")
    purchase_orders_send.add_argument(
        "--json-file",
        required=True,
        help="Path to the PurchaseOrderMailSettings JSON payload file",
    )
    _add_local_write_flags(purchase_orders_send)
    purchase_orders_send.set_defaults(func=purchase_orders_cmd.cmd_purchase_orders_send_via_email, write_capable=True)
    purchase_orders_send_many = purchase_orders_sub.add_parser(
        "sends-multiple-purchase-orders-via-email",
        help="Plan or send multiple purchase orders via email",
    )
    purchase_orders_send_many.add_argument(
        "--id",
        required=True,
        action="append",
        help="Repeat for each Fortnox purchase-order id to send",
    )
    _add_local_write_flags(purchase_orders_send_many)
    purchase_orders_send_many.set_defaults(
        func=purchase_orders_cmd.cmd_purchase_orders_send_many_via_email,
        write_capable=True,
    )
    purchase_orders_update_response = purchase_orders_sub.add_parser(
        "update-response",
        help="Plan or update one purchase-order response state from a JSON payload file",
    )
    purchase_orders_update_response.add_argument("--id", required=True, help="Fortnox purchase-order id")
    purchase_orders_update_response.add_argument(
        "--json-file",
        required=True,
        help="Path to the PurchaseOrderResponseState JSON payload file",
    )
    _add_local_write_flags(purchase_orders_update_response)
    purchase_orders_update_response.set_defaults(
        func=purchase_orders_cmd.cmd_purchase_orders_update_response,
        write_capable=True,
    )
    purchase_orders_update_response_bulk = purchase_orders_sub.add_parser(
        "update-response-bulk",
        help="Plan or bulk update purchase-order response states from a JSON payload file",
    )
    purchase_orders_update_response_bulk.add_argument(
        "--id",
        required=True,
        action="append",
        help="Repeat for each Fortnox purchase-order id to update",
    )
    purchase_orders_update_response_bulk.add_argument(
        "--json-file",
        required=True,
        help="Path to the PurchaseOrderResponseState JSON payload file",
    )
    _add_local_write_flags(purchase_orders_update_response_bulk)
    purchase_orders_update_response_bulk.set_defaults(
        func=purchase_orders_cmd.cmd_purchase_orders_update_response_bulk,
        write_capable=True,
    )
    purchase_orders_void = purchase_orders_sub.add_parser(
        "void",
        help="Plan or void one purchase order",
    )
    purchase_orders_void.add_argument("--id", required=True, help="Fortnox purchase-order id")
    _add_local_write_flags(purchase_orders_void)
    purchase_orders_void.set_defaults(func=purchase_orders_cmd.cmd_purchase_orders_void, write_capable=True)

    production_orders = sub.add_parser("production-orders", help="Production-order commands")
    production_orders_sub = production_orders.add_subparsers(
        dest="production_orders_cmd", required=True, parser_class=_ToolArgumentParser
    )
    production_orders_list = production_orders_sub.add_parser("list", help="List production orders")
    production_orders_list.set_defaults(func=production_orders_cmd.cmd_production_orders_list, write_capable=False)
    production_orders_get = production_orders_sub.add_parser("get", help="Get one production order")
    production_orders_get.add_argument("--id", required=True, help="Fortnox production-order id")
    production_orders_get.set_defaults(func=production_orders_cmd.cmd_production_orders_get, write_capable=False)
    production_orders_get_bill_of_materials = production_orders_sub.add_parser(
        "get-bill-of-materials",
        help="Get bill of materials for one production article",
    )
    production_orders_get_bill_of_materials.add_argument(
        "--item-id",
        required=True,
        help="Fortnox item id",
    )
    production_orders_get_bill_of_materials.set_defaults(
        func=production_orders_cmd.cmd_production_orders_get_bill_of_materials,
        write_capable=False,
    )
    production_orders_create = production_orders_sub.add_parser(
        "create",
        help="Plan or create one production order from a JSON payload file",
    )
    production_orders_create.add_argument(
        "--json-file",
        required=True,
        help="Path to the ProductionOrder JSON payload file",
    )
    _add_local_write_flags(production_orders_create)
    production_orders_create.set_defaults(func=production_orders_cmd.cmd_production_orders_create, write_capable=True)
    production_orders_update = production_orders_sub.add_parser(
        "update",
        help="Plan or update one production order from a JSON payload file",
    )
    production_orders_update.add_argument("--id", required=True, help="Fortnox production-order id")
    production_orders_update.add_argument(
        "--json-file",
        required=True,
        help="Path to the ProductionOrder JSON payload file",
    )
    _add_local_write_flags(production_orders_update)
    production_orders_update.set_defaults(func=production_orders_cmd.cmd_production_orders_update, write_capable=True)
    production_orders_update_note = production_orders_sub.add_parser(
        "update-note",
        help="Plan or patch the note on one production order from a JSON payload file",
    )
    production_orders_update_note.add_argument("--id", required=True, help="Fortnox production-order id")
    production_orders_update_note.add_argument(
        "--json-file",
        required=True,
        help="Path to the ProductionOrder JSON payload file",
    )
    _add_local_write_flags(production_orders_update_note)
    production_orders_update_note.set_defaults(
        func=production_orders_cmd.cmd_production_orders_update_note,
        write_capable=True,
    )
    production_orders_release = production_orders_sub.add_parser(
        "release",
        help="Plan or release one production order",
    )
    production_orders_release.add_argument("--id", required=True, help="Fortnox production-order id")
    _add_local_write_flags(production_orders_release)
    production_orders_release.set_defaults(func=production_orders_cmd.cmd_production_orders_release, write_capable=True)
    production_orders_void = production_orders_sub.add_parser(
        "void",
        help="Plan or void one production order",
    )
    production_orders_void.add_argument("--id", required=True, help="Fortnox production-order id")
    _add_local_write_flags(production_orders_void)
    production_orders_void.set_defaults(func=production_orders_cmd.cmd_production_orders_void, write_capable=True)

    incoming_goods = sub.add_parser("incoming-goods", help="Incoming-goods commands")
    incoming_goods_sub = incoming_goods.add_subparsers(
        dest="incoming_goods_cmd", required=True, parser_class=_ToolArgumentParser
    )
    incoming_goods_list = incoming_goods_sub.add_parser("list", help="List incoming-goods documents")
    incoming_goods_list.set_defaults(func=incoming_goods_cmd.cmd_incoming_goods_list, write_capable=False)
    incoming_goods_get = incoming_goods_sub.add_parser("get", help="Get one incoming-goods document")
    incoming_goods_get.add_argument("--id", required=True, help="Fortnox incoming-goods id")
    incoming_goods_get.set_defaults(func=incoming_goods_cmd.cmd_incoming_goods_get, write_capable=False)
    incoming_goods_create = incoming_goods_sub.add_parser(
        "create",
        help="Plan or create one incoming-goods document from a JSON payload file",
    )
    incoming_goods_create.add_argument("--json-file", required=True, help="Path to the IncomingGoods JSON payload file")
    _add_local_write_flags(incoming_goods_create)
    incoming_goods_create.set_defaults(func=incoming_goods_cmd.cmd_incoming_goods_create, write_capable=True)
    incoming_goods_update = incoming_goods_sub.add_parser(
        "update",
        help="Plan or update one incoming-goods document from a JSON payload file",
    )
    incoming_goods_update.add_argument("--id", required=True, help="Fortnox incoming-goods id")
    incoming_goods_update.add_argument("--json-file", required=True, help="Path to the IncomingGoods JSON payload file")
    _add_local_write_flags(incoming_goods_update)
    incoming_goods_update.set_defaults(func=incoming_goods_cmd.cmd_incoming_goods_update, write_capable=True)
    incoming_goods_partial_update = incoming_goods_sub.add_parser(
        "partial-update-incoming-goods-document",
        help="Plan or partially update one incoming-goods document from a JSON payload file",
    )
    incoming_goods_partial_update.add_argument("--id", required=True, help="Fortnox incoming-goods id")
    incoming_goods_partial_update.add_argument(
        "--json-file",
        required=True,
        help="Path to the partial IncomingGoods JSON payload file",
    )
    _add_local_write_flags(incoming_goods_partial_update)
    incoming_goods_partial_update.set_defaults(
        func=incoming_goods_cmd.cmd_incoming_goods_partial_update,
        write_capable=True,
    )
    incoming_goods_complete = incoming_goods_sub.add_parser(
        "complete-incoming-goods-document",
        help="Plan or complete one incoming-goods document for a bookkeeping date",
    )
    incoming_goods_complete.add_argument("--id", required=True, help="Fortnox incoming-goods id")
    incoming_goods_complete.add_argument("--date", required=True, help="Bookkeeping date in YYYY-MM-DD")
    _add_local_write_flags(incoming_goods_complete)
    incoming_goods_complete.set_defaults(func=incoming_goods_cmd.cmd_incoming_goods_complete, write_capable=True)
    incoming_goods_release = incoming_goods_sub.add_parser(
        "release",
        help="Plan or release one incoming-goods document",
    )
    incoming_goods_release.add_argument("--id", required=True, help="Fortnox incoming-goods id")
    _add_local_write_flags(incoming_goods_release)
    incoming_goods_release.set_defaults(func=incoming_goods_cmd.cmd_incoming_goods_release, write_capable=True)
    incoming_goods_void = incoming_goods_sub.add_parser(
        "void",
        help="Plan or void one incoming-goods document",
    )
    incoming_goods_void.add_argument("--id", required=True, help="Fortnox incoming-goods id")
    _add_local_write_flags(incoming_goods_void)
    incoming_goods_void.set_defaults(func=incoming_goods_cmd.cmd_incoming_goods_void, write_capable=True)

    stock_taking = sub.add_parser("stock-taking", help="Stock-taking reads and writes")
    stock_taking_sub = stock_taking.add_subparsers(dest="stock_taking_cmd", required=True, parser_class=_ToolArgumentParser)
    stock_taking_list = stock_taking_sub.add_parser("list", help="List stock-taking documents")
    stock_taking_list.set_defaults(func=stock_taking_cmd.cmd_stock_taking_list, write_capable=False)
    stock_taking_get = stock_taking_sub.add_parser("get", help="Get one stock-taking document")
    stock_taking_get.add_argument("--id", required=True, help="Fortnox stock-taking id")
    stock_taking_get.set_defaults(func=stock_taking_cmd.cmd_stock_taking_get, write_capable=False)
    stock_taking_get_candidate_rows = stock_taking_sub.add_parser(
        "get-candidate-rows",
        help="Get candidate rows for one stock-taking document",
    )
    stock_taking_get_candidate_rows.add_argument("--id", required=True, help="Fortnox stock-taking id")
    _add_stock_taking_filter_flags(stock_taking_get_candidate_rows, include_non_inbound=True)
    stock_taking_get_candidate_rows.set_defaults(
        func=stock_taking_cmd.cmd_stock_taking_get_candidate_rows,
        write_capable=False,
    )
    stock_taking_get_rows = stock_taking_sub.add_parser(
        "get-rows",
        help="Get rows for one stock-taking document",
    )
    stock_taking_get_rows.add_argument("--id", required=True, help="Fortnox stock-taking id")
    _add_stock_taking_filter_flags(stock_taking_get_rows, include_rows_extras=True)
    stock_taking_get_rows.set_defaults(func=stock_taking_cmd.cmd_stock_taking_get_rows, write_capable=False)
    stock_taking_create = stock_taking_sub.add_parser(
        "create",
        help="Plan or create one stock-taking document from a JSON payload file",
    )
    stock_taking_create.add_argument("--json-file", required=True, help="Path to the StockTaking JSON payload file")
    _add_local_write_flags(stock_taking_create)
    stock_taking_create.set_defaults(func=stock_taking_cmd.cmd_stock_taking_create, write_capable=True)
    stock_taking_update = stock_taking_sub.add_parser(
        "update",
        help="Plan or update one stock-taking document from a JSON payload file",
    )
    stock_taking_update.add_argument("--id", required=True, help="Fortnox stock-taking id")
    stock_taking_update.add_argument("--json-file", required=True, help="Path to the StockTaking JSON payload file")
    _add_local_write_flags(stock_taking_update)
    stock_taking_update.set_defaults(func=stock_taking_cmd.cmd_stock_taking_update, write_capable=True)
    stock_taking_add_rows = stock_taking_sub.add_parser(
        "add-rows",
        help="Plan or add stock-taking rows from a JSON payload file",
    )
    stock_taking_add_rows.add_argument("--id", required=True, help="Fortnox stock-taking id")
    stock_taking_add_rows.add_argument(
        "--json-file",
        required=True,
        help="Path to the StockTakingRows JSON payload file",
    )
    _add_local_write_flags(stock_taking_add_rows)
    stock_taking_add_rows.set_defaults(func=stock_taking_cmd.cmd_stock_taking_add_rows, write_capable=True)
    stock_taking_add_rows_by_filter = stock_taking_sub.add_parser(
        "add-rows-by-filter",
        help="Plan or add stock-taking rows by the documented row filters",
    )
    stock_taking_add_rows_by_filter.add_argument("--id", required=True, help="Fortnox stock-taking id")
    _add_stock_taking_filter_flags(stock_taking_add_rows_by_filter, exclude_non_inbound=True)
    _add_local_write_flags(stock_taking_add_rows_by_filter)
    stock_taking_add_rows_by_filter.set_defaults(
        func=stock_taking_cmd.cmd_stock_taking_add_rows_by_filter,
        write_capable=True,
    )
    stock_taking_delete = stock_taking_sub.add_parser(
        "delete",
        help="Plan or delete one stock-taking document",
    )
    stock_taking_delete.add_argument("--id", required=True, help="Fortnox stock-taking id")
    _add_local_write_flags(stock_taking_delete)
    stock_taking_delete.set_defaults(func=stock_taking_cmd.cmd_stock_taking_delete, write_capable=True)
    stock_taking_delete_row = stock_taking_sub.add_parser(
        "delete-row",
        help="Plan or delete one stock-taking row",
    )
    stock_taking_delete_row.add_argument("--id", required=True, help="Fortnox stock-taking id")
    stock_taking_delete_row.add_argument("--row-id", required=True, help="Fortnox stock-taking row id")
    _add_local_write_flags(stock_taking_delete_row)
    stock_taking_delete_row.set_defaults(func=stock_taking_cmd.cmd_stock_taking_delete_row, write_capable=True)
    stock_taking_delete_rows = stock_taking_sub.add_parser(
        "delete-rows",
        help="Plan or delete stock-taking rows by the documented row filters",
    )
    stock_taking_delete_rows.add_argument("--id", required=True, help="Fortnox stock-taking id")
    _add_stock_taking_filter_flags(stock_taking_delete_rows)
    _add_local_write_flags(stock_taking_delete_rows)
    stock_taking_delete_rows.set_defaults(func=stock_taking_cmd.cmd_stock_taking_delete_rows, write_capable=True)
    stock_taking_release = stock_taking_sub.add_parser(
        "release",
        help="Plan or release one stock-taking document",
    )
    stock_taking_release.add_argument("--id", required=True, help="Fortnox stock-taking id")
    _add_local_write_flags(stock_taking_release)
    stock_taking_release.set_defaults(func=stock_taking_cmd.cmd_stock_taking_release, write_capable=True)
    stock_taking_void = stock_taking_sub.add_parser(
        "void",
        help="Plan or void one stock-taking document",
    )
    stock_taking_void.add_argument("--id", required=True, help="Fortnox stock-taking id")
    _add_local_write_flags(stock_taking_void)
    stock_taking_void.set_defaults(func=stock_taking_cmd.cmd_stock_taking_void, write_capable=True)

    stock_transfers = sub.add_parser("stock-transfers", help="Stock-transfer reads and writes")
    stock_transfers_sub = stock_transfers.add_subparsers(
        dest="stock_transfers_cmd", required=True, parser_class=_ToolArgumentParser
    )
    stock_transfers_get = stock_transfers_sub.add_parser("get", help="Get one stock transfer document")
    stock_transfers_get.add_argument("--id", required=True, help="Fortnox stock transfer id")
    stock_transfers_get.set_defaults(func=stock_transfers_cmd.cmd_stock_transfers_get, write_capable=False)
    stock_transfers_create = stock_transfers_sub.add_parser(
        "create",
        help="Plan or create one stock transfer document from a JSON payload file",
    )
    stock_transfers_create.add_argument("--json-file", required=True, help="Path to the StockTransfer JSON payload file")
    _add_local_write_flags(stock_transfers_create)
    stock_transfers_create.set_defaults(func=stock_transfers_cmd.cmd_stock_transfers_create, write_capable=True)
    stock_transfers_update = stock_transfers_sub.add_parser(
        "update",
        help="Plan or update one stock transfer document from a JSON payload file",
    )
    stock_transfers_update.add_argument("--id", required=True, help="Fortnox stock transfer id")
    stock_transfers_update.add_argument("--json-file", required=True, help="Path to the StockTransfer JSON payload file")
    _add_local_write_flags(stock_transfers_update)
    stock_transfers_update.set_defaults(func=stock_transfers_cmd.cmd_stock_transfers_update, write_capable=True)
    stock_transfers_release = stock_transfers_sub.add_parser(
        "release",
        help="Plan or release one stock transfer document",
    )
    stock_transfers_release.add_argument("--id", required=True, help="Fortnox stock transfer id")
    _add_local_write_flags(stock_transfers_release)
    stock_transfers_release.set_defaults(func=stock_transfers_cmd.cmd_stock_transfers_release, write_capable=True)
    stock_transfers_void = stock_transfers_sub.add_parser(
        "void",
        help="Plan or void one stock transfer document",
    )
    stock_transfers_void.add_argument("--id", required=True, help="Fortnox stock transfer id")
    _add_local_write_flags(stock_transfers_void)
    stock_transfers_void.set_defaults(func=stock_transfers_cmd.cmd_stock_transfers_void, write_capable=True)

    stock_points = sub.add_parser("stock-points", help="Stock-point reads and writes")
    stock_points_sub = stock_points.add_subparsers(dest="stock_points_cmd", required=True, parser_class=_ToolArgumentParser)
    stock_points_list = stock_points_sub.add_parser("list", help="List stock points")
    stock_points_list.add_argument("--q", help="Filter by stock point code or name")
    _add_stock_point_state_flag(stock_points_list, help_text="Filter by stock point state")
    stock_points_list.set_defaults(func=stock_points_cmd.cmd_stock_points_list, write_capable=False)
    stock_points_get = stock_points_sub.add_parser("get", help="Get one stock point by id or code")
    stock_points_get.add_argument("--id", required=True, help="Fortnox stock point id or code")
    stock_points_get.set_defaults(func=stock_points_cmd.cmd_stock_points_get, write_capable=False)
    stock_points_get_stock_locations = stock_points_sub.add_parser(
        "get-stock-locations",
        help="Get stock locations for one stock point by id or code",
    )
    stock_points_get_stock_locations.add_argument("--id", required=True, help="Fortnox stock point id or code")
    stock_points_get_stock_locations.add_argument("--q", help="Filter stock locations by code or name")
    stock_points_get_stock_locations.set_defaults(
        func=stock_points_cmd.cmd_stock_points_get_stock_locations,
        write_capable=False,
    )
    stock_points_list_multi = stock_points_sub.add_parser(
        "list-multi",
        help="Get multiple stock points by repeated ids",
    )
    stock_points_list_multi.add_argument("--id", action="append", required=True, help="Fortnox stock point id")
    _add_stock_point_state_flag(stock_points_list_multi, help_text="Filter returned stock points by state")
    stock_points_list_multi.set_defaults(func=stock_points_cmd.cmd_stock_points_list_multi, write_capable=False)
    stock_points_create = stock_points_sub.add_parser(
        "create",
        help="Plan or create one stock point from a JSON payload file",
    )
    stock_points_create.add_argument("--json-file", required=True, help="Path to the StockPoint JSON payload file")
    _add_local_write_flags(stock_points_create)
    stock_points_create.set_defaults(func=stock_points_cmd.cmd_stock_points_create, write_capable=True)
    stock_points_update = stock_points_sub.add_parser(
        "update",
        help="Plan or update one stock point from a JSON payload file",
    )
    stock_points_update.add_argument("--id", required=True, help="Fortnox stock point id")
    stock_points_update.add_argument("--json-file", required=True, help="Path to the StockPoint JSON payload file")
    _add_local_write_flags(stock_points_update)
    stock_points_update.set_defaults(func=stock_points_cmd.cmd_stock_points_update, write_capable=True)
    stock_points_append_stock_locations = stock_points_sub.add_parser(
        "append-stock-locations",
        help="Plan or append stock locations from a JSON payload file",
    )
    stock_points_append_stock_locations.add_argument("--id", required=True, help="Fortnox stock point id")
    stock_points_append_stock_locations.add_argument(
        "--json-file",
        required=True,
        help="Path to the StockLocation array JSON payload file",
    )
    _add_local_write_flags(stock_points_append_stock_locations)
    stock_points_append_stock_locations.set_defaults(
        func=stock_points_cmd.cmd_stock_points_append_stock_locations,
        write_capable=True,
    )
    stock_points_delete = stock_points_sub.add_parser(
        "delete",
        help="Plan or delete one stock point",
    )
    stock_points_delete.add_argument("--id", required=True, help="Fortnox stock point id")
    _add_local_write_flags(stock_points_delete)
    stock_points_delete.set_defaults(func=stock_points_cmd.cmd_stock_points_delete, write_capable=True)

    cost_centers = sub.add_parser("cost-centers", help="Cost-center reads and writes")
    cost_centers_sub = cost_centers.add_subparsers(dest="cost_centers_cmd", required=True, parser_class=_ToolArgumentParser)
    cost_centers_list = cost_centers_sub.add_parser("list", help="List cost centers")
    cost_centers_list.set_defaults(func=accounting_reads_cmd.cmd_cost_centers_list, write_capable=False)
    cost_centers_get = cost_centers_sub.add_parser("get", help="Get one cost center")
    cost_centers_get.add_argument("--code", required=True, help="Fortnox cost-center code")
    cost_centers_get.set_defaults(func=accounting_reads_cmd.cmd_cost_centers_get, write_capable=False)
    cost_centers_create = cost_centers_sub.add_parser(
        "create",
        help="Create a cost center from a reviewed JSON payload",
    )
    cost_centers_create.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level CostCenter object",
    )
    _add_local_write_flags(cost_centers_create)
    cost_centers_create.set_defaults(func=cost_centers_cmd.cmd_cost_centers_create, write_capable=True)
    cost_centers_update = cost_centers_sub.add_parser(
        "update",
        help="Update a cost center from a reviewed JSON payload",
    )
    cost_centers_update.add_argument("--code", required=True, help="Fortnox cost-center code")
    cost_centers_update.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level CostCenter object",
    )
    _add_local_write_flags(cost_centers_update)
    cost_centers_update.set_defaults(func=cost_centers_cmd.cmd_cost_centers_update, write_capable=True)
    cost_centers_remove = cost_centers_sub.add_parser(
        "remove",
        help="Remove a cost center after dry-run plan review",
    )
    cost_centers_remove.add_argument("--code", required=True, help="Fortnox cost-center code")
    _add_local_write_flags(cost_centers_remove)
    cost_centers_remove.set_defaults(func=cost_centers_cmd.cmd_cost_centers_remove, write_capable=True)

    currencies = sub.add_parser("currencies", help="Currency reads and writes")
    currencies_sub = currencies.add_subparsers(dest="currencies_cmd", required=True, parser_class=_ToolArgumentParser)
    currencies_list = currencies_sub.add_parser("list", help="List currencies")
    currencies_list.set_defaults(func=accounting_reads_cmd.cmd_currencies_list, write_capable=False)
    currencies_get = currencies_sub.add_parser("get", help="Get one currency")
    currencies_get.add_argument("--code", required=True, help="Fortnox currency code")
    currencies_get.set_defaults(func=accounting_reads_cmd.cmd_currencies_get, write_capable=False)
    currencies_create = currencies_sub.add_parser(
        "create",
        help="Create a currency from a reviewed JSON payload",
    )
    currencies_create.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level Currency object",
    )
    _add_local_write_flags(currencies_create)
    currencies_create.set_defaults(func=currencies_cmd.cmd_currencies_create, write_capable=True)
    currencies_update = currencies_sub.add_parser(
        "update",
        help="Update a currency from a reviewed JSON payload",
    )
    currencies_update.add_argument("--code", required=True, help="Fortnox currency code")
    currencies_update.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level Currency object",
    )
    _add_local_write_flags(currencies_update)
    currencies_update.set_defaults(func=currencies_cmd.cmd_currencies_update, write_capable=True)
    currencies_remove = currencies_sub.add_parser(
        "remove",
        help="Remove a currency after dry-run plan review",
    )
    currencies_remove.add_argument("--code", required=True, help="Fortnox currency code")
    _add_local_write_flags(currencies_remove)
    currencies_remove.set_defaults(func=currencies_cmd.cmd_currencies_remove, write_capable=True)

    units = sub.add_parser("units", help="Unit reads and writes")
    units_sub = units.add_subparsers(dest="units_cmd", required=True, parser_class=_ToolArgumentParser)
    units_list = units_sub.add_parser("list", help="List units")
    units_list.set_defaults(func=accounting_reads_cmd.cmd_units_list, write_capable=False)
    units_get = units_sub.add_parser("get", help="Get one unit")
    units_get.add_argument("--code", required=True, help="Fortnox unit code")
    units_get.set_defaults(func=accounting_reads_cmd.cmd_units_get, write_capable=False)
    units_create = units_sub.add_parser(
        "create",
        help="Create a unit from a reviewed JSON payload",
    )
    units_create.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level Unit object",
    )
    _add_local_write_flags(units_create)
    units_create.set_defaults(func=units_cmd.cmd_units_create, write_capable=True)
    units_update = units_sub.add_parser(
        "update",
        help="Update a unit from a reviewed JSON payload",
    )
    units_update.add_argument("--code", required=True, help="Fortnox unit code")
    units_update.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level Unit object",
    )
    _add_local_write_flags(units_update)
    units_update.set_defaults(func=units_cmd.cmd_units_update, write_capable=True)
    units_remove = units_sub.add_parser(
        "remove",
        help="Remove a unit after dry-run plan review",
    )
    units_remove.add_argument("--code", required=True, help="Fortnox unit code")
    _add_local_write_flags(units_remove)
    units_remove.set_defaults(func=units_cmd.cmd_units_remove, write_capable=True)

    terms_of_deliveries = sub.add_parser("terms-of-deliveries", help="Terms-of-delivery reads")
    terms_of_deliveries_sub = terms_of_deliveries.add_subparsers(
        dest="terms_of_deliveries_cmd", required=True, parser_class=_ToolArgumentParser
    )
    terms_of_deliveries_list = terms_of_deliveries_sub.add_parser("list", help="List terms of deliveries")
    terms_of_deliveries_list.set_defaults(func=accounting_reads_cmd.cmd_terms_of_deliveries_list, write_capable=False)
    terms_of_deliveries_get = terms_of_deliveries_sub.add_parser("get", help="Get one terms-of-delivery record")
    terms_of_deliveries_get.add_argument("--code", required=True, help="Fortnox terms-of-delivery code")
    terms_of_deliveries_get.set_defaults(func=accounting_reads_cmd.cmd_terms_of_deliveries_get, write_capable=False)
    terms_of_deliveries_create = terms_of_deliveries_sub.add_parser(
        "create",
        help="Create a terms-of-delivery record from a reviewed JSON payload",
    )
    terms_of_deliveries_create.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level TermsOfDelivery object",
    )
    _add_local_write_flags(terms_of_deliveries_create)
    terms_of_deliveries_create.set_defaults(
        func=terms_of_deliveries_cmd.cmd_terms_of_deliveries_create,
        write_capable=True,
    )
    terms_of_deliveries_update = terms_of_deliveries_sub.add_parser(
        "update",
        help="Update a terms-of-delivery record from a reviewed JSON payload",
    )
    terms_of_deliveries_update.add_argument("--code", required=True, help="Fortnox terms-of-delivery code")
    terms_of_deliveries_update.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level TermsOfDelivery object",
    )
    _add_local_write_flags(terms_of_deliveries_update)
    terms_of_deliveries_update.set_defaults(
        func=terms_of_deliveries_cmd.cmd_terms_of_deliveries_update,
        write_capable=True,
    )

    way_of_deliveries = sub.add_parser("way-of-deliveries", help="Way-of-delivery reads and writes")
    way_of_deliveries_sub = way_of_deliveries.add_subparsers(
        dest="way_of_deliveries_cmd", required=True, parser_class=_ToolArgumentParser
    )
    way_of_deliveries_list = way_of_deliveries_sub.add_parser("list", help="List way of deliveries")
    way_of_deliveries_list.set_defaults(func=accounting_reads_cmd.cmd_way_of_deliveries_list, write_capable=False)
    way_of_deliveries_get = way_of_deliveries_sub.add_parser("get", help="Get one way-of-delivery record")
    way_of_deliveries_get.add_argument("--code", required=True, help="Fortnox way-of-delivery code")
    way_of_deliveries_get.set_defaults(func=accounting_reads_cmd.cmd_way_of_deliveries_get, write_capable=False)
    way_of_deliveries_create = way_of_deliveries_sub.add_parser(
        "create",
        help="Create a way-of-delivery record from a reviewed JSON payload",
    )
    way_of_deliveries_create.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level WayOfDelivery object",
    )
    _add_local_write_flags(way_of_deliveries_create)
    way_of_deliveries_create.set_defaults(
        func=way_of_deliveries_cmd.cmd_way_of_deliveries_create,
        write_capable=True,
    )
    way_of_deliveries_update = way_of_deliveries_sub.add_parser(
        "update",
        help="Update a way-of-delivery record from a reviewed JSON payload",
    )
    way_of_deliveries_update.add_argument("--code", required=True, help="Fortnox way-of-delivery code")
    way_of_deliveries_update.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level WayOfDelivery object",
    )
    _add_local_write_flags(way_of_deliveries_update)
    way_of_deliveries_update.set_defaults(
        func=way_of_deliveries_cmd.cmd_way_of_deliveries_update,
        write_capable=True,
    )
    way_of_deliveries_remove = way_of_deliveries_sub.add_parser(
        "remove",
        help="Remove a way-of-delivery record after dry-run plan review",
    )
    way_of_deliveries_remove.add_argument("--code", required=True, help="Fortnox way-of-delivery code")
    _add_local_write_flags(way_of_deliveries_remove)
    way_of_deliveries_remove.set_defaults(
        func=way_of_deliveries_cmd.cmd_way_of_deliveries_remove,
        write_capable=True,
    )

    terms_of_payments = sub.add_parser("terms-of-payments", help="Terms-of-payment reads and writes")
    terms_of_payments_sub = terms_of_payments.add_subparsers(
        dest="terms_of_payments_cmd", required=True, parser_class=_ToolArgumentParser
    )
    terms_of_payments_list = terms_of_payments_sub.add_parser("list", help="List terms of payments")
    terms_of_payments_list.set_defaults(func=accounting_reads_cmd.cmd_terms_of_payments_list, write_capable=False)
    terms_of_payments_get = terms_of_payments_sub.add_parser("get", help="Get one terms-of-payment record")
    terms_of_payments_get.add_argument("--code", required=True, help="Fortnox terms-of-payment code")
    terms_of_payments_get.set_defaults(func=accounting_reads_cmd.cmd_terms_of_payments_get, write_capable=False)
    terms_of_payments_create = terms_of_payments_sub.add_parser(
        "create",
        help="Create a terms-of-payment from a reviewed JSON payload",
    )
    terms_of_payments_create.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level TermsOfPayment object",
    )
    _add_local_write_flags(terms_of_payments_create)
    terms_of_payments_create.set_defaults(
        func=terms_of_payments_cmd.cmd_terms_of_payments_create,
        write_capable=True,
    )
    terms_of_payments_update = terms_of_payments_sub.add_parser(
        "update",
        help="Update a terms-of-payment from a reviewed JSON payload",
    )
    terms_of_payments_update.add_argument("--code", required=True, help="Fortnox terms-of-payment code")
    terms_of_payments_update.add_argument(
        "--json-file",
        required=True,
        help="Path to a JSON file containing a top-level TermsOfPayment object",
    )
    _add_local_write_flags(terms_of_payments_update)
    terms_of_payments_update.set_defaults(
        func=terms_of_payments_cmd.cmd_terms_of_payments_update,
        write_capable=True,
    )
    terms_of_payments_remove = terms_of_payments_sub.add_parser(
        "remove",
        help="Remove a terms-of-payment after dry-run plan review",
    )
    terms_of_payments_remove.add_argument("--code", required=True, help="Fortnox terms-of-payment code")
    _add_local_write_flags(terms_of_payments_remove)
    terms_of_payments_remove.set_defaults(
        func=terms_of_payments_cmd.cmd_terms_of_payments_remove,
        write_capable=True,
    )

    account_charts = sub.add_parser("account-charts", help="Account-chart reads")
    account_charts_sub = account_charts.add_subparsers(
        dest="account_charts_cmd", required=True, parser_class=_ToolArgumentParser
    )
    account_charts_list = account_charts_sub.add_parser("list", help="List account charts")
    account_charts_list.set_defaults(func=accounting_reads_cmd.cmd_account_charts_list, write_capable=False)

    accounts = sub.add_parser("accounts", help="Account commands")
    accounts_sub = accounts.add_subparsers(dest="accounts_cmd", required=True, parser_class=_ToolArgumentParser)
    accounts_list = accounts_sub.add_parser("list", help="List accounts")
    accounts_list.set_defaults(func=accounting_reads_cmd.cmd_accounts_list, write_capable=False)
    accounts_get = accounts_sub.add_parser("get", help="Get one account")
    accounts_get.add_argument("--number", required=True, help="Fortnox account number")
    accounts_get.set_defaults(func=accounting_reads_cmd.cmd_accounts_get, write_capable=False)
    accounts_create = accounts_sub.add_parser(
        "create",
        help="Plan or create one account from a JSON payload file",
    )
    accounts_create.add_argument("--json-file", required=True, help="Path to the Account JSON payload file")
    accounts_create.add_argument("--financial-year", type=int, default=None, help="Fortnox financial year id")
    _add_local_write_flags(accounts_create)
    accounts_create.set_defaults(func=accounts_cmd.cmd_accounts_create, write_capable=True)
    accounts_update = accounts_sub.add_parser(
        "update",
        help="Plan or update one account from a JSON payload file",
    )
    accounts_update.add_argument("--number", required=True, help="Fortnox account number")
    accounts_update.add_argument("--json-file", required=True, help="Path to the Account JSON payload file")
    accounts_update.add_argument("--financial-year", type=int, default=None, help="Fortnox financial year id")
    _add_local_write_flags(accounts_update)
    accounts_update.set_defaults(func=accounts_cmd.cmd_accounts_update, write_capable=True)
    accounts_delete = accounts_sub.add_parser("delete", help="Plan or delete one account")
    accounts_delete.add_argument("--number", required=True, help="Fortnox account number")
    _add_local_write_flags(accounts_delete)
    accounts_delete.set_defaults(func=accounts_cmd.cmd_accounts_delete, write_capable=True)

    financial_years = sub.add_parser("financial-years", help="Financial-year reads and writes")
    financial_years_sub = financial_years.add_subparsers(
        dest="financial_years_cmd", required=True, parser_class=_ToolArgumentParser
    )
    financial_years_list = financial_years_sub.add_parser("list", help="List financial years")
    financial_years_list.set_defaults(func=accounting_reads_cmd.cmd_financial_years_list, write_capable=False)
    financial_years_get = financial_years_sub.add_parser("get", help="Get one financial year")
    financial_years_get.add_argument("--year-id", required=True, help="Fortnox financial-year id")
    financial_years_get.set_defaults(func=accounting_reads_cmd.cmd_financial_years_get, write_capable=False)
    financial_years_create = financial_years_sub.add_parser(
        "create",
        help="Create a financial year from a reviewed JSON payload",
    )
    financial_years_create.add_argument(
        "--json-file",
        required=True,
        help="Path to the FinancialYear JSON payload file",
    )
    _add_local_write_flags(financial_years_create)
    financial_years_create.set_defaults(func=financial_years_cmd.cmd_financial_years_create, write_capable=True)

    fortnox_finans = sub.add_parser("fortnox-finans", help="Fortnox Finans commands")
    fortnox_finans_sub = fortnox_finans.add_subparsers(dest="fortnox_finans_cmd", required=True, parser_class=_ToolArgumentParser)
    fortnox_finans_get = fortnox_finans_sub.add_parser("get", help="Get one Fortnox Finans invoice")
    fortnox_finans_get.add_argument("--invoice-number", required=True, help="Fortnox invoice number")
    fortnox_finans_get.set_defaults(func=fortnox_finans_cmd.cmd_fortnox_finans_get, write_capable=False)
    fortnox_finans_send = fortnox_finans_sub.add_parser(
        "send-an-invoice-with-fortnox-finans",
        help="Plan or send one invoice with Fortnox Finans from a JSON payload file",
    )
    fortnox_finans_send.add_argument("--json-file", required=True, help="Path to the NoxFinansInvoice JSON payload file")
    _add_local_write_flags(fortnox_finans_send)
    fortnox_finans_send.set_defaults(
        func=fortnox_finans_cmd.cmd_fortnox_finans_send_an_invoice_with_fortnox_finans,
        write_capable=True,
    )
    fortnox_finans_pause = fortnox_finans_sub.add_parser("action-pause", help="Plan or pause one Fortnox Finans invoice")
    fortnox_finans_pause.add_argument("--invoice-number", required=True, help="Fortnox invoice number")
    fortnox_finans_pause.add_argument("--json-file", default=None, help="Optional path to the NoxFinansInvoice JSON payload file")
    _add_local_write_flags(fortnox_finans_pause)
    fortnox_finans_pause.set_defaults(func=fortnox_finans_cmd.cmd_fortnox_finans_action_pause, write_capable=True)
    fortnox_finans_report_payment = fortnox_finans_sub.add_parser(
        "action-report-payment",
        help="Plan or report payment on one Fortnox Finans invoice",
    )
    fortnox_finans_report_payment.add_argument("--invoice-number", required=True, help="Fortnox invoice number")
    fortnox_finans_report_payment.add_argument("--json-file", default=None, help="Optional path to the NoxFinansInvoice JSON payload file")
    _add_local_write_flags(fortnox_finans_report_payment)
    fortnox_finans_report_payment.set_defaults(
        func=fortnox_finans_cmd.cmd_fortnox_finans_action_report_payment,
        write_capable=True,
    )
    fortnox_finans_stop = fortnox_finans_sub.add_parser("action-stop", help="Plan or stop one Fortnox Finans invoice")
    fortnox_finans_stop.add_argument("--invoice-number", required=True, help="Fortnox invoice number")
    fortnox_finans_stop.add_argument("--json-file", default=None, help="Optional path to the NoxFinansInvoice JSON payload file")
    _add_local_write_flags(fortnox_finans_stop)
    fortnox_finans_stop.set_defaults(func=fortnox_finans_cmd.cmd_fortnox_finans_action_stop, write_capable=True)
    fortnox_finans_take_fees = fortnox_finans_sub.add_parser(
        "action-take-fees",
        help="Plan or take fees on one Fortnox Finans invoice",
    )
    fortnox_finans_take_fees.add_argument("--invoice-number", required=True, help="Fortnox invoice number")
    fortnox_finans_take_fees.add_argument("--json-file", default=None, help="Optional path to the NoxFinansInvoice JSON payload file")
    _add_local_write_flags(fortnox_finans_take_fees)
    fortnox_finans_take_fees.set_defaults(
        func=fortnox_finans_cmd.cmd_fortnox_finans_action_take_fees,
        write_capable=True,
    )
    fortnox_finans_unpause = fortnox_finans_sub.add_parser("action-unpause", help="Plan or unpause one Fortnox Finans invoice")
    fortnox_finans_unpause.add_argument("--invoice-number", required=True, help="Fortnox invoice number")
    fortnox_finans_unpause.add_argument("--json-file", default=None, help="Optional path to the NoxFinansInvoice JSON payload file")
    _add_local_write_flags(fortnox_finans_unpause)
    fortnox_finans_unpause.set_defaults(func=fortnox_finans_cmd.cmd_fortnox_finans_action_unpause, write_capable=True)

    integration_sales = sub.add_parser("integration-sales", help="Integration sales reads")
    integration_sales_sub = integration_sales.add_subparsers(
        dest="integration_sales_cmd", required=True, parser_class=_ToolArgumentParser
    )
    integration_sales_get_by_app_id = integration_sales_sub.add_parser(
        "get-by-app-id",
        help="Get sales information and active users for one app id (deprecated official endpoint)",
    )
    integration_sales_get_by_app_id.add_argument("--app-id", required=True, help="Fortnox app id")
    integration_sales_get_by_app_id.set_defaults(
        func=integration_sales_cmd.cmd_integration_sales_get_by_app_id,
        write_capable=False,
    )
    integration_sales_get_by_app_id_and_tenant = integration_sales_sub.add_parser(
        "get-by-app-id-and-tenant",
        help="Get sales information and active users for one app id and tenant id (deprecated official endpoint)",
    )
    integration_sales_get_by_app_id_and_tenant.add_argument("--app-id", required=True, help="Fortnox app id")
    integration_sales_get_by_app_id_and_tenant.add_argument("--tenant-id", required=True, help="Fortnox tenant id")
    integration_sales_get_by_app_id_and_tenant.set_defaults(
        func=integration_sales_cmd.cmd_integration_sales_get_by_app_id_and_tenant,
        write_capable=False,
    )
    integration_sales_get_by_integration = integration_sales_sub.add_parser(
        "resolves-sales-information-of-an-integration",
        help="Get sales information for one published integration",
    )
    integration_sales_get_by_integration.add_argument("--integration-id", required=True, help="Fortnox integration id")
    integration_sales_get_by_integration.set_defaults(
        func=integration_sales_cmd.cmd_integration_sales_resolves_sales_information_of_an_integration,
        write_capable=False,
    )

    article_url_connections = sub.add_parser("article-url-connections", help="Article URL-connection reads and writes")
    article_url_connections_sub = article_url_connections.add_subparsers(
        dest="article_url_connections_cmd", required=True, parser_class=_ToolArgumentParser
    )
    article_url_connections_list = article_url_connections_sub.add_parser(
        "list",
        help="List article URL connections",
    )
    article_url_connections_list.add_argument(
        "--article-number",
        default=None,
        help="Optional Fortnox article number filter for the documented articlenumber query parameter",
    )
    article_url_connections_list.set_defaults(
        func=remaining_reads_cmd.cmd_article_url_connections_list,
        write_capable=False,
    )
    article_url_connections_create = article_url_connections_sub.add_parser(
        "create",
        help="Plan or create one article URL connection",
    )
    article_url_connections_create.add_argument(
        "--json-file",
        required=True,
        help="Path to the JSON payload file containing the official ArticleUrlConnection wrapper",
    )
    _add_local_write_flags(article_url_connections_create)
    article_url_connections_create.set_defaults(
        func=remaining_reads_cmd.cmd_article_url_connections_create,
        write_capable=True,
    )
    article_url_connections_get = article_url_connections_sub.add_parser(
        "get",
        help="Get one article URL connection by id",
    )
    article_url_connections_get.add_argument("--id", required=True, help="Fortnox article URL connection id")
    article_url_connections_get.set_defaults(
        func=remaining_reads_cmd.cmd_article_url_connections_get,
        write_capable=False,
    )
    article_url_connections_update = article_url_connections_sub.add_parser(
        "update",
        help="Plan or update one article URL connection by id",
    )
    article_url_connections_update.add_argument("--id", required=True, help="Fortnox article URL connection id")
    article_url_connections_update.add_argument(
        "--json-file",
        required=True,
        help="Path to the JSON payload file containing the official ArticleUrlConnection wrapper",
    )
    _add_local_write_flags(article_url_connections_update)
    article_url_connections_update.set_defaults(
        func=remaining_reads_cmd.cmd_article_url_connections_update,
        write_capable=True,
    )
    article_url_connections_delete = article_url_connections_sub.add_parser(
        "delete",
        help="Plan or delete one article URL connection by id",
    )
    article_url_connections_delete.add_argument("--id", required=True, help="Fortnox article URL connection id")
    _add_local_write_flags(article_url_connections_delete)
    article_url_connections_delete.set_defaults(
        func=remaining_reads_cmd.cmd_article_url_connections_delete,
        write_capable=True,
    )

    eu_vat_limit_regulation = sub.add_parser("eu-vat-limit-regulation", help="EU VAT limit-regulation reads")
    eu_vat_limit_regulation_sub = eu_vat_limit_regulation.add_subparsers(
        dest="eu_vat_limit_regulation_cmd", required=True, parser_class=_ToolArgumentParser
    )
    eu_vat_limit_regulation_get = eu_vat_limit_regulation_sub.add_parser(
        "get",
        help="Get EU VAT limit-regulation details",
    )
    eu_vat_limit_regulation_get.add_argument("--year", type=int, default=None, help="Optional official year query filter")
    eu_vat_limit_regulation_get.set_defaults(
        func=remaining_reads_cmd.cmd_eu_vat_limit_regulation_get,
        write_capable=False,
    )

    integration_ratings = sub.add_parser("integration-ratings", help="Integration ratings reads")
    integration_ratings_sub = integration_ratings.add_subparsers(
        dest="integration_ratings_cmd", required=True, parser_class=_ToolArgumentParser
    )
    integration_ratings_list = integration_ratings_sub.add_parser("list", help="List ratings and reviews for owned integrations")
    integration_ratings_list.set_defaults(func=remaining_reads_cmd.cmd_integration_ratings_list, write_capable=False)

    sie = sub.add_parser("sie", help="SIE export reads")
    sie_sub = sie.add_subparsers(dest="sie_cmd", required=True, parser_class=_ToolArgumentParser)
    sie_get = sie_sub.add_parser("get", help="Get one streamed SIE export")
    sie_get.add_argument("--type", dest="sie_type", required=True, help="Official SIE type path value")
    sie_get.add_argument("--selection", default=None, help="Optional official selection query value")
    sie_get.add_argument("--financial-year", type=int, default=None, help="Optional official financialYear query value")
    sie_get.add_argument("--export-all", default=None, help="Optional official exportall query value")
    sie_get.add_argument("--from-date", default=None, help="Optional official fromdate query value in YYYY-MM-DD")
    sie_get.add_argument("--to-date", default=None, help="Optional official todate query value in YYYY-MM-DD")
    sie_get.set_defaults(func=remaining_reads_cmd.cmd_sie_get, write_capable=False)

    stock_status = sub.add_parser("stock-status", help="Warehouse stock-status reads")
    stock_status_sub = stock_status.add_subparsers(dest="stock_status_cmd", required=True, parser_class=_ToolArgumentParser)
    stock_status_get_stock_balance = stock_status_sub.add_parser(
        "get-stock-balance",
        help="Get stock balance, optionally filtered by item id or stock point code",
    )
    stock_status_get_stock_balance.add_argument("--item-id", action="append", default=None, help="Optional repeatable item id filter")
    stock_status_get_stock_balance.add_argument(
        "--stock-point-code",
        action="append",
        default=None,
        help="Optional repeatable stock point code filter",
    )
    stock_status_get_stock_balance.set_defaults(
        func=remaining_reads_cmd.cmd_stock_status_get_stock_balance,
        write_capable=False,
    )

    tenant = sub.add_parser("tenant", help="Warehouse tenant reads")
    tenant_sub = tenant.add_subparsers(dest="tenant_cmd", required=True, parser_class=_ToolArgumentParser)
    tenant_get = tenant_sub.add_parser("get", help="Get Warehouse activation status for the current tenant")
    tenant_get.set_defaults(func=remaining_reads_cmd.cmd_tenant_get, write_capable=False)

    users = sub.add_parser("users", help="Integration user reads")
    users_sub = users.add_subparsers(dest="users_cmd", required=True, parser_class=_ToolArgumentParser)
    users_fetch_single = users_sub.add_parser(
        "fetch-user-information-for-a-single-published-integration-and-tenant",
        help="Fetch user information for one published integration and tenant",
    )
    users_fetch_single.add_argument("--integration-id", required=True, help="Fortnox integration id")
    users_fetch_single.add_argument("--tenant-id", required=True, help="Fortnox tenant id")
    users_fetch_single.set_defaults(
        func=remaining_reads_cmd.cmd_users_fetch_user_information_for_a_single_published_integration_and_tenant,
        write_capable=False,
    )

    predefined_accounts = sub.add_parser("predefined-accounts", help="Predefined-account reads and writes")
    predefined_accounts_sub = predefined_accounts.add_subparsers(
        dest="predefined_accounts_cmd", required=True, parser_class=_ToolArgumentParser
    )
    predefined_accounts_list = predefined_accounts_sub.add_parser("list", help="List predefined accounts")
    predefined_accounts_list.set_defaults(func=accounting_reads_cmd.cmd_predefined_accounts_list, write_capable=False)
    predefined_accounts_get = predefined_accounts_sub.add_parser("get", help="Get one predefined account")
    predefined_accounts_get.add_argument("--name", required=True, help="Fortnox predefined-account name")
    predefined_accounts_get.set_defaults(func=accounting_reads_cmd.cmd_predefined_accounts_get, write_capable=False)
    predefined_accounts_update = predefined_accounts_sub.add_parser(
        "update",
        help="Update one predefined account from a reviewed JSON payload",
    )
    predefined_accounts_update.add_argument("--name", required=True, help="Fortnox predefined-account name")
    predefined_accounts_update.add_argument(
        "--json-file",
        required=True,
        help="Path to the PreDefinedAccount JSON payload file",
    )
    _add_local_write_flags(predefined_accounts_update)
    predefined_accounts_update.set_defaults(
        func=predefined_accounts_cmd.cmd_predefined_accounts_update,
        write_capable=True,
    )

    predefined_voucher_series = sub.add_parser("predefined-voucher-series", help="Predefined-voucher-series reads and writes")
    predefined_voucher_series_sub = predefined_voucher_series.add_subparsers(
        dest="predefined_voucher_series_cmd", required=True, parser_class=_ToolArgumentParser
    )
    predefined_voucher_series_list = predefined_voucher_series_sub.add_parser("list", help="List predefined voucher series")
    predefined_voucher_series_list.set_defaults(func=accounting_reads_cmd.cmd_predefined_voucher_series_list, write_capable=False)
    predefined_voucher_series_get = predefined_voucher_series_sub.add_parser("get", help="Get one predefined voucher series")
    predefined_voucher_series_get.add_argument("--name", required=True, help="Fortnox predefined voucher-series name")
    predefined_voucher_series_get.set_defaults(func=accounting_reads_cmd.cmd_predefined_voucher_series_get, write_capable=False)
    predefined_voucher_series_update = predefined_voucher_series_sub.add_parser(
        "update",
        help="Update one predefined voucher series from a reviewed JSON payload",
    )
    predefined_voucher_series_update.add_argument("--name", required=True, help="Fortnox predefined voucher-series name")
    predefined_voucher_series_update.add_argument(
        "--json-file",
        required=True,
        help="Path to the PreDefinedVoucherSeries JSON payload file",
    )
    _add_local_write_flags(predefined_voucher_series_update)
    predefined_voucher_series_update.set_defaults(
        func=predefined_voucher_series_cmd.cmd_predefined_voucher_series_update,
        write_capable=True,
    )

    modes_of_payments = sub.add_parser("modes-of-payments", help="Mode-of-payment reads and writes")
    modes_of_payments_sub = modes_of_payments.add_subparsers(
        dest="modes_of_payments_cmd", required=True, parser_class=_ToolArgumentParser
    )
    modes_of_payments_list = modes_of_payments_sub.add_parser("list", help="List modes of payments")
    modes_of_payments_list.set_defaults(func=accounting_reads_cmd.cmd_modes_of_payments_list, write_capable=False)
    modes_of_payments_get = modes_of_payments_sub.add_parser("get", help="Get one mode of payment")
    modes_of_payments_get.add_argument("--code", required=True, help="Fortnox mode-of-payment code")
    modes_of_payments_get.set_defaults(func=accounting_reads_cmd.cmd_modes_of_payments_get, write_capable=False)
    modes_of_payments_create = modes_of_payments_sub.add_parser(
        "create",
        help="Create a mode of payment from a reviewed JSON payload",
    )
    modes_of_payments_create.add_argument("--json-file", required=True, help="Path to the ModeOfPayment JSON payload file")
    _add_local_write_flags(modes_of_payments_create)
    modes_of_payments_create.set_defaults(
        func=modes_of_payments_cmd.cmd_modes_of_payments_create,
        write_capable=True,
    )
    modes_of_payments_update = modes_of_payments_sub.add_parser(
        "update",
        help="Update one mode of payment from a reviewed JSON payload",
    )
    modes_of_payments_update.add_argument("--code", required=True, help="Fortnox mode-of-payment code")
    modes_of_payments_update.add_argument(
        "--json-file",
        required=True,
        help="Path to the ModeOfPayment JSON payload file",
    )
    _add_local_write_flags(modes_of_payments_update)
    modes_of_payments_update.set_defaults(
        func=modes_of_payments_cmd.cmd_modes_of_payments_update,
        write_capable=True,
    )
    modes_of_payments_remove = modes_of_payments_sub.add_parser(
        "remove",
        help="Remove a mode of payment after dry-run plan review",
    )
    modes_of_payments_remove.add_argument("--code", required=True, help="Fortnox mode-of-payment code")
    _add_local_write_flags(modes_of_payments_remove)
    modes_of_payments_remove.set_defaults(
        func=modes_of_payments_cmd.cmd_modes_of_payments_remove,
        write_capable=True,
    )

    voucher_series = sub.add_parser("voucher-series", help="Voucher-series reads and writes")
    voucher_series_sub = voucher_series.add_subparsers(
        dest="voucher_series_cmd", required=True, parser_class=_ToolArgumentParser
    )
    voucher_series_list = voucher_series_sub.add_parser("list", help="List voucher series")
    voucher_series_list.set_defaults(func=accounting_reads_cmd.cmd_voucher_series_list, write_capable=False)
    voucher_series_get = voucher_series_sub.add_parser("get", help="Get one voucher series")
    voucher_series_get.add_argument("--code", required=True, help="Fortnox voucher-series code")
    voucher_series_get.set_defaults(func=accounting_reads_cmd.cmd_voucher_series_get, write_capable=False)
    voucher_series_create = voucher_series_sub.add_parser(
        "create",
        help="Create a voucher series from a reviewed JSON payload",
    )
    voucher_series_create.add_argument(
        "--json-file",
        required=True,
        help="Path to the VoucherSeries JSON payload file",
    )
    _add_local_write_flags(voucher_series_create)
    voucher_series_create.set_defaults(
        func=voucher_series_cmd.cmd_voucher_series_create,
        write_capable=True,
    )
    voucher_series_update = voucher_series_sub.add_parser(
        "update",
        help="Update one voucher series from a reviewed JSON payload",
    )
    voucher_series_update.add_argument("--code", required=True, help="Fortnox voucher-series code")
    voucher_series_update.add_argument(
        "--json-file",
        required=True,
        help="Path to the VoucherSeries JSON payload file",
    )
    _add_local_write_flags(voucher_series_update)
    voucher_series_update.set_defaults(
        func=voucher_series_cmd.cmd_voucher_series_update,
        write_capable=True,
    )

    voucher_file_connections = sub.add_parser("voucher-file-connections", help="Voucher file connection commands")
    voucher_file_connections_sub = voucher_file_connections.add_subparsers(
        dest="voucher_file_connections_cmd", required=True, parser_class=_ToolArgumentParser
    )
    voucher_file_connections_list = voucher_file_connections_sub.add_parser(
        "list",
        help="List voucher file connections",
    )
    voucher_file_connections_list.add_argument("--voucher-year", type=int, help="Filter by voucher year")
    voucher_file_connections_list.add_argument(
        "--voucher-description",
        help="Filter by voucher description",
    )
    voucher_file_connections_list.add_argument("--voucher-number", type=int, help="Filter by voucher number")
    voucher_file_connections_list.add_argument("--voucher-series", help="Filter by voucher series")
    voucher_file_connections_list.set_defaults(
        func=voucher_file_connections_cmd.cmd_voucher_file_connections_list,
        write_capable=False,
    )
    voucher_file_connections_get = voucher_file_connections_sub.add_parser(
        "get",
        help="Get one voucher file connection",
    )
    voucher_file_connections_get.add_argument("--file-id", required=True, help="Fortnox file id")
    voucher_file_connections_get.set_defaults(
        func=voucher_file_connections_cmd.cmd_voucher_file_connections_get,
        write_capable=False,
    )
    voucher_file_connections_create = voucher_file_connections_sub.add_parser(
        "create",
        help="Plan or create one voucher file connection from a JSON payload file",
    )
    voucher_file_connections_create.add_argument(
        "--json-file",
        required=True,
        help="Path to the voucher file connection JSON payload file",
    )
    _add_local_write_flags(voucher_file_connections_create)
    voucher_file_connections_create.set_defaults(
        func=voucher_file_connections_cmd.cmd_voucher_file_connections_create,
        write_capable=True,
    )
    voucher_file_connections_remove = voucher_file_connections_sub.add_parser(
        "remove",
        help="Plan or remove one voucher file connection",
    )
    voucher_file_connections_remove.add_argument("--file-id", required=True, help="Fortnox file id")
    _add_local_write_flags(voucher_file_connections_remove)
    voucher_file_connections_remove.set_defaults(
        func=voucher_file_connections_cmd.cmd_voucher_file_connections_remove,
        write_capable=True,
    )

    vouchers = sub.add_parser("vouchers", help="Voucher reads and writes")
    vouchers_sub = vouchers.add_subparsers(dest="vouchers_cmd", required=True, parser_class=_ToolArgumentParser)
    vouchers_list = vouchers_sub.add_parser("list", help="List vouchers")
    vouchers_list.set_defaults(func=accounting_reads_cmd.cmd_vouchers_list, write_capable=False)
    vouchers_get = vouchers_sub.add_parser("get", help="Get one voucher")
    vouchers_get.add_argument("--voucher-series", required=True, help="Fortnox voucher-series code")
    vouchers_get.add_argument("--voucher-number", required=True, help="Fortnox voucher number")
    vouchers_get.set_defaults(func=accounting_reads_cmd.cmd_vouchers_get, write_capable=False)
    vouchers_list_by_series = vouchers_sub.add_parser("list-by-series", help="List vouchers for one series")
    vouchers_list_by_series.add_argument("--voucher-series", required=True, help="Fortnox voucher-series code")
    vouchers_list_by_series.set_defaults(func=accounting_reads_cmd.cmd_vouchers_list_by_series, write_capable=False)
    vouchers_list_current_financial_year = vouchers_sub.add_parser(
        "list-current-financial-year",
        help="List vouchers for the current financial year",
    )
    vouchers_list_current_financial_year.set_defaults(
        func=accounting_reads_cmd.cmd_vouchers_list_current_financial_year,
        write_capable=False,
    )
    vouchers_create = vouchers_sub.add_parser(
        "create",
        help="Create a voucher from a reviewed JSON payload",
    )
    vouchers_create.add_argument("--json-file", required=True, help="Path to the Voucher JSON payload file")
    vouchers_create.add_argument("--financial-year", type=int, default=None, help="Fortnox financial year id")
    _add_local_write_flags(vouchers_create)
    vouchers_create.set_defaults(func=vouchers_cmd.cmd_vouchers_create, write_capable=True)

    invoice_payments = sub.add_parser("invoice-payments", help="Invoice-payment commands")
    invoice_payments_sub = invoice_payments.add_subparsers(
        dest="invoice_payments_cmd", required=True, parser_class=_ToolArgumentParser
    )
    invoice_payments_list = invoice_payments_sub.add_parser("list", help="List invoice payments")
    invoice_payments_list.set_defaults(func=accounting_reads_cmd.cmd_invoice_payments_list, write_capable=False)
    invoice_payments_get = invoice_payments_sub.add_parser("get", help="Get one invoice payment")
    invoice_payments_get.add_argument("--number", required=True, help="Fortnox invoice-payment number")
    invoice_payments_get.set_defaults(func=accounting_reads_cmd.cmd_invoice_payments_get, write_capable=False)
    invoice_payments_create = invoice_payments_sub.add_parser(
        "create",
        help="Plan or create one invoice payment from a JSON payload file",
    )
    invoice_payments_create.add_argument("--json-file", required=True, help="Path to the InvoicePayment JSON payload file")
    _add_local_write_flags(invoice_payments_create)
    invoice_payments_create.set_defaults(func=invoice_payments_cmd.cmd_invoice_payments_create, write_capable=True)
    invoice_payments_update = invoice_payments_sub.add_parser(
        "update",
        help="Plan or update one invoice payment from a JSON payload file",
    )
    invoice_payments_update.add_argument("--number", required=True, help="Fortnox invoice-payment number")
    invoice_payments_update.add_argument("--json-file", required=True, help="Path to the InvoicePayment JSON payload file")
    _add_local_write_flags(invoice_payments_update)
    invoice_payments_update.set_defaults(func=invoice_payments_cmd.cmd_invoice_payments_update, write_capable=True)
    invoice_payments_remove = invoice_payments_sub.add_parser("remove", help="Plan or remove one invoice payment")
    invoice_payments_remove.add_argument("--number", required=True, help="Fortnox invoice-payment number")
    _add_local_write_flags(invoice_payments_remove)
    invoice_payments_remove.set_defaults(func=invoice_payments_cmd.cmd_invoice_payments_remove, write_capable=True)
    invoice_payments_bookkeep = invoice_payments_sub.add_parser(
        "bookkeep",
        help="Plan or bookkeep one invoice payment from a JSON payload file",
    )
    invoice_payments_bookkeep.add_argument("--number", required=True, help="Fortnox invoice-payment number")
    invoice_payments_bookkeep.add_argument("--json-file", required=True, help="Path to the InvoicePayment JSON payload file")
    _add_local_write_flags(invoice_payments_bookkeep)
    invoice_payments_bookkeep.set_defaults(func=invoice_payments_cmd.cmd_invoice_payments_bookkeep, write_capable=True)

    invoices = sub.add_parser("invoices", help="Invoice commands")
    invoices_sub = invoices.add_subparsers(dest="invoices_cmd", required=True, parser_class=_ToolArgumentParser)
    invoices_list = invoices_sub.add_parser("list", help="List invoices")
    invoices_list.set_defaults(func=accounting_reads_cmd.cmd_invoices_list, write_capable=False)
    invoices_get = invoices_sub.add_parser("get", help="Get one invoice")
    invoices_get.add_argument("--document-number", required=True, help="Fortnox invoice document number")
    invoices_get.set_defaults(func=accounting_reads_cmd.cmd_invoices_get, write_capable=False)
    invoices_preview = invoices_sub.add_parser("preview", help="Preview one invoice as PDF")
    invoices_preview.add_argument("--document-number", required=True, help="Fortnox invoice document number")
    _add_download_output_flag(invoices_preview, noun="invoice PDF")
    invoices_preview.set_defaults(func=accounting_reads_cmd.cmd_invoices_preview, write_capable=False)
    invoices_print = invoices_sub.add_parser("print", help="Print one invoice as PDF")
    invoices_print.add_argument("--document-number", required=True, help="Fortnox invoice document number")
    _add_download_output_flag(invoices_print, noun="invoice PDF")
    invoices_print.set_defaults(func=accounting_reads_cmd.cmd_invoices_print, write_capable=False)
    invoices_print_reminder = invoices_sub.add_parser("print-reminder", help="Print one invoice reminder as PDF")
    invoices_print_reminder.add_argument("--document-number", required=True, help="Fortnox invoice document number")
    _add_download_output_flag(invoices_print_reminder, noun="invoice reminder PDF")
    invoices_print_reminder.set_defaults(func=accounting_reads_cmd.cmd_invoices_print_reminder, write_capable=False)
    invoices_send_as_e_invoice = invoices_sub.add_parser(
        "send-an-invoice-as-e-invoice",
        help="Plan or send one invoice as e-invoice",
    )
    invoices_send_as_e_invoice.add_argument("--document-number", required=True, help="Fortnox invoice document number")
    _add_local_write_flags(invoices_send_as_e_invoice)
    invoices_send_as_e_invoice.set_defaults(func=invoices_cmd.cmd_invoices_send_as_e_invoice, write_capable=True)
    invoices_send_as_e_print = invoices_sub.add_parser(
        "send-an-invoice-as-e-print",
        help="Plan or send one invoice as e-print",
    )
    invoices_send_as_e_print.add_argument("--document-number", required=True, help="Fortnox invoice document number")
    _add_local_write_flags(invoices_send_as_e_print)
    invoices_send_as_e_print.set_defaults(func=invoices_cmd.cmd_invoices_send_as_e_print, write_capable=True)
    invoices_send_as_email = invoices_sub.add_parser(
        "send-an-invoice-as-email",
        help="Plan or send one invoice as email",
    )
    invoices_send_as_email.add_argument("--document-number", required=True, help="Fortnox invoice document number")
    _add_local_write_flags(invoices_send_as_email)
    invoices_send_as_email.set_defaults(func=invoices_cmd.cmd_invoices_send_as_email, write_capable=True)
    invoices_create = invoices_sub.add_parser(
        "create",
        help="Plan or create one invoice from a JSON payload file",
    )
    invoices_create.add_argument("--json-file", required=True, help="Path to the Invoice JSON payload file")
    _add_local_write_flags(invoices_create)
    invoices_create.set_defaults(func=invoices_cmd.cmd_invoices_create, write_capable=True)
    invoices_update = invoices_sub.add_parser(
        "update",
        help="Plan or update one invoice from a JSON payload file",
    )
    invoices_update.add_argument("--document-number", required=True, help="Fortnox invoice document number")
    invoices_update.add_argument("--json-file", required=True, help="Path to the Invoice JSON payload file")
    _add_local_write_flags(invoices_update)
    invoices_update.set_defaults(func=invoices_cmd.cmd_invoices_update, write_capable=True)
    invoices_bookkeep = invoices_sub.add_parser(
        "bookkeep",
        help="Plan or bookkeep one invoice from an optional JSON payload file",
    )
    invoices_bookkeep.add_argument("--document-number", required=True, help="Fortnox invoice document number")
    invoices_bookkeep.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the Invoice JSON payload file",
    )
    _add_local_write_flags(invoices_bookkeep)
    invoices_bookkeep.set_defaults(func=invoices_cmd.cmd_invoices_bookkeep, write_capable=True)
    invoices_cancel = invoices_sub.add_parser(
        "cancel",
        help="Plan or cancel one invoice from an optional JSON payload file",
    )
    invoices_cancel.add_argument("--document-number", required=True, help="Fortnox invoice document number")
    invoices_cancel.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the Invoice JSON payload file",
    )
    _add_local_write_flags(invoices_cancel)
    invoices_cancel.set_defaults(func=invoices_cmd.cmd_invoices_cancel, write_capable=True)
    invoices_credit = invoices_sub.add_parser(
        "credit",
        help="Plan or credit one invoice from an optional JSON payload file",
    )
    invoices_credit.add_argument("--document-number", required=True, help="Fortnox invoice document number")
    invoices_credit.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the Invoice JSON payload file",
    )
    _add_local_write_flags(invoices_credit)
    invoices_credit.set_defaults(func=invoices_cmd.cmd_invoices_credit, write_capable=True)
    invoices_warehouseready = invoices_sub.add_parser(
        "warehouseready",
        help="Plan or mark warehouse-ready one invoice from an optional JSON payload file",
    )
    invoices_warehouseready.add_argument("--document-number", required=True, help="Fortnox invoice document number")
    invoices_warehouseready.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the Invoice JSON payload file",
    )
    _add_local_write_flags(invoices_warehouseready)
    invoices_warehouseready.set_defaults(
        func=invoices_cmd.cmd_invoices_warehouseready,
        write_capable=True,
    )
    invoices_externalprint = invoices_sub.add_parser(
        "externalprint",
        help="Plan or send one invoice to external print from an optional JSON payload file",
    )
    invoices_externalprint.add_argument("--document-number", required=True, help="Fortnox invoice document number")
    invoices_externalprint.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the Invoice JSON payload file",
    )
    _add_local_write_flags(invoices_externalprint)
    invoices_externalprint.set_defaults(func=invoices_cmd.cmd_invoices_externalprint, write_capable=True)

    invoice_accruals = sub.add_parser("invoice-accruals", help="Invoice accrual commands")
    invoice_accruals_sub = invoice_accruals.add_subparsers(
        dest="invoice_accruals_cmd", required=True, parser_class=_ToolArgumentParser
    )
    invoice_accruals_list = invoice_accruals_sub.add_parser("list", help="List invoice accruals")
    invoice_accruals_list.set_defaults(func=invoice_accruals_cmd.cmd_invoice_accruals_list, write_capable=False)
    invoice_accruals_get = invoice_accruals_sub.add_parser("get", help="Get one invoice accrual")
    invoice_accruals_get.add_argument("--invoice-number", required=True, help="Fortnox invoice number")
    invoice_accruals_get.set_defaults(func=invoice_accruals_cmd.cmd_invoice_accruals_get, write_capable=False)
    invoice_accruals_create = invoice_accruals_sub.add_parser(
        "create",
        help="Plan or create one invoice accrual from a JSON payload file",
    )
    invoice_accruals_create.add_argument("--json-file", required=True, help="Path to the InvoiceAccrual JSON payload file")
    _add_local_write_flags(invoice_accruals_create)
    invoice_accruals_create.set_defaults(func=invoice_accruals_cmd.cmd_invoice_accruals_create, write_capable=True)
    invoice_accruals_update = invoice_accruals_sub.add_parser(
        "update",
        help="Plan or update one invoice accrual from a JSON payload file",
    )
    invoice_accruals_update.add_argument("--invoice-number", required=True, help="Fortnox invoice number")
    invoice_accruals_update.add_argument("--json-file", required=True, help="Path to the InvoiceAccrual JSON payload file")
    _add_local_write_flags(invoice_accruals_update)
    invoice_accruals_update.set_defaults(func=invoice_accruals_cmd.cmd_invoice_accruals_update, write_capable=True)
    invoice_accruals_remove = invoice_accruals_sub.add_parser("remove", help="Plan or remove one invoice accrual")
    invoice_accruals_remove.add_argument("--invoice-number", required=True, help="Fortnox invoice number")
    _add_local_write_flags(invoice_accruals_remove)
    invoice_accruals_remove.set_defaults(func=invoice_accruals_cmd.cmd_invoice_accruals_remove, write_capable=True)

    contract_accruals = sub.add_parser("contract-accruals", help="Contract accrual commands")
    contract_accruals_sub = contract_accruals.add_subparsers(
        dest="contract_accruals_cmd", required=True, parser_class=_ToolArgumentParser
    )
    contract_accruals_list = contract_accruals_sub.add_parser("list", help="List contract accruals")
    contract_accruals_list.set_defaults(func=contract_accruals_cmd.cmd_contract_accruals_list, write_capable=False)
    contract_accruals_get = contract_accruals_sub.add_parser("get", help="Get one contract accrual")
    contract_accruals_get.add_argument("--document-number", required=True, help="Fortnox contract document number")
    contract_accruals_get.set_defaults(func=contract_accruals_cmd.cmd_contract_accruals_get, write_capable=False)
    contract_accruals_create = contract_accruals_sub.add_parser(
        "create",
        help="Plan or create one contract accrual from a JSON payload file",
    )
    contract_accruals_create.add_argument(
        "--json-file",
        required=True,
        help="Path to the ContractAccrual JSON payload file",
    )
    _add_local_write_flags(contract_accruals_create)
    contract_accruals_create.set_defaults(func=contract_accruals_cmd.cmd_contract_accruals_create, write_capable=True)
    contract_accruals_update = contract_accruals_sub.add_parser(
        "update",
        help="Plan or update one contract accrual from a JSON payload file",
    )
    contract_accruals_update.add_argument("--document-number", required=True, help="Fortnox contract document number")
    contract_accruals_update.add_argument(
        "--json-file",
        required=True,
        help="Path to the ContractAccrual JSON payload file",
    )
    _add_local_write_flags(contract_accruals_update)
    contract_accruals_update.set_defaults(func=contract_accruals_cmd.cmd_contract_accruals_update, write_capable=True)
    contract_accruals_remove = contract_accruals_sub.add_parser(
        "remove",
        help="Plan or remove one contract accrual",
    )
    contract_accruals_remove.add_argument("--document-number", required=True, help="Fortnox contract document number")
    _add_local_write_flags(contract_accruals_remove)
    contract_accruals_remove.set_defaults(func=contract_accruals_cmd.cmd_contract_accruals_remove, write_capable=True)

    contract_templates = sub.add_parser("contract-templates", help="Contract template commands")
    contract_templates_sub = contract_templates.add_subparsers(
        dest="contract_templates_cmd", required=True, parser_class=_ToolArgumentParser
    )
    contract_templates_list = contract_templates_sub.add_parser("list", help="List contract templates")
    contract_templates_list.set_defaults(func=contract_templates_cmd.cmd_contract_templates_list, write_capable=False)
    contract_templates_get = contract_templates_sub.add_parser("get", help="Get one contract template")
    contract_templates_get.add_argument("--template-number", required=True, help="Fortnox contract template number")
    contract_templates_get.set_defaults(func=contract_templates_cmd.cmd_contract_templates_get, write_capable=False)
    contract_templates_create = contract_templates_sub.add_parser(
        "create",
        help="Plan or create one contract template from a JSON payload file",
    )
    contract_templates_create.add_argument(
        "--json-file",
        required=True,
        help="Path to the ContractTemplate JSON payload file",
    )
    _add_local_write_flags(contract_templates_create)
    contract_templates_create.set_defaults(
        func=contract_templates_cmd.cmd_contract_templates_create,
        write_capable=True,
    )
    contract_templates_update = contract_templates_sub.add_parser(
        "update",
        help="Plan or update one contract template from a JSON payload file",
    )
    contract_templates_update.add_argument("--template-number", required=True, help="Fortnox contract template number")
    contract_templates_update.add_argument(
        "--json-file",
        required=True,
        help="Path to the ContractTemplate JSON payload file",
    )
    _add_local_write_flags(contract_templates_update)
    contract_templates_update.set_defaults(
        func=contract_templates_cmd.cmd_contract_templates_update,
        write_capable=True,
    )

    contracts = sub.add_parser("contracts", help="Contract commands")
    contracts_sub = contracts.add_subparsers(dest="contracts_cmd", required=True, parser_class=_ToolArgumentParser)
    contracts_list = contracts_sub.add_parser("list", help="List contracts")
    contracts_list.add_argument("--period-start", required=False, help="Filter by contract period start date")
    contracts_list.add_argument("--period-end", required=False, help="Filter by contract period end date")
    contracts_list.add_argument(
        "--filter",
        required=False,
        choices=["active", "inactive", "finished"],
        help="Fortnox contract filter",
    )
    contracts_list.add_argument("--document-number", required=False, type=int, help="Filter by contract document number")
    contracts_list.add_argument("--customer-number", required=False, help="Filter by customer number")
    contracts_list.add_argument("--template-number", required=False, type=int, help="Filter by template number")
    contracts_list.add_argument(
        "--invoices-remaining",
        required=False,
        type=int,
        help="Filter by remaining invoice count",
    )
    contracts_list.add_argument("--last-modified", required=False, help="Filter by last-modified date")
    contracts_list.set_defaults(func=contracts_cmd.cmd_contracts_list, write_capable=False)
    contracts_get = contracts_sub.add_parser("get", help="Get one contract")
    contracts_get.add_argument("--document-number", required=True, help="Fortnox contract document number")
    contracts_get.set_defaults(func=contracts_cmd.cmd_contracts_get, write_capable=False)
    contracts_create = contracts_sub.add_parser(
        "create",
        help="Plan or create one contract from a JSON payload file",
    )
    contracts_create.add_argument("--json-file", required=True, help="Path to the Contract JSON payload file")
    _add_local_write_flags(contracts_create)
    contracts_create.set_defaults(func=contracts_cmd.cmd_contracts_create, write_capable=True)
    contracts_update = contracts_sub.add_parser(
        "update",
        help="Plan or update one contract from a JSON payload file",
    )
    contracts_update.add_argument("--document-number", required=True, help="Fortnox contract document number")
    contracts_update.add_argument("--json-file", required=True, help="Path to the Contract JSON payload file")
    _add_local_write_flags(contracts_update)
    contracts_update.set_defaults(func=contracts_cmd.cmd_contracts_update, write_capable=True)
    contracts_createinvoice = contracts_sub.add_parser(
        "create-invoice",
        help="Plan or create one invoice from one contract from an optional JSON payload file",
    )
    contracts_createinvoice.add_argument("--document-number", required=True, help="Fortnox contract document number")
    contracts_createinvoice.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the Contract JSON payload file",
    )
    contracts_createinvoice.add_argument(
        "--invoice-date",
        required=False,
        help="Optional invoice date for the Fortnox createinvoice query parameter",
    )
    _add_local_write_flags(contracts_createinvoice)
    contracts_createinvoice.set_defaults(func=contracts_cmd.cmd_contracts_createinvoice, write_capable=True)
    contracts_increaseinvoicecount = contracts_sub.add_parser(
        "increase-invoice-count",
        help="Plan or increase remaining invoice count from an optional JSON payload file",
    )
    contracts_increaseinvoicecount.add_argument(
        "--document-number",
        required=True,
        help="Fortnox contract document number",
    )
    contracts_increaseinvoicecount.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the Contract JSON payload file",
    )
    _add_local_write_flags(contracts_increaseinvoicecount)
    contracts_increaseinvoicecount.set_defaults(
        func=contracts_cmd.cmd_contracts_increaseinvoicecount,
        write_capable=True,
    )
    contracts_finish = contracts_sub.add_parser(
        "finish",
        help="Plan or set one contract as finished from an optional JSON payload file",
    )
    contracts_finish.add_argument("--document-number", required=True, help="Fortnox contract document number")
    contracts_finish.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the Contract JSON payload file",
    )
    _add_local_write_flags(contracts_finish)
    contracts_finish.set_defaults(func=contracts_cmd.cmd_contracts_finish, write_capable=True)

    supplier_invoice_accruals = sub.add_parser("supplier-invoice-accruals", help="Supplier invoice accrual commands")
    supplier_invoice_accruals_sub = supplier_invoice_accruals.add_subparsers(
        dest="supplier_invoice_accruals_cmd", required=True, parser_class=_ToolArgumentParser
    )
    supplier_invoice_accruals_list = supplier_invoice_accruals_sub.add_parser(
        "list",
        help="List supplier invoice accruals",
    )
    supplier_invoice_accruals_list.set_defaults(
        func=supplier_invoice_accruals_cmd.cmd_supplier_invoice_accruals_list,
        write_capable=False,
    )
    supplier_invoice_accruals_get = supplier_invoice_accruals_sub.add_parser(
        "get",
        help="Get one supplier invoice accrual",
    )
    supplier_invoice_accruals_get.add_argument(
        "--supplier-invoice-number",
        required=True,
        help="Fortnox supplier invoice number",
    )
    supplier_invoice_accruals_get.set_defaults(
        func=supplier_invoice_accruals_cmd.cmd_supplier_invoice_accruals_get,
        write_capable=False,
    )
    supplier_invoice_accruals_create = supplier_invoice_accruals_sub.add_parser(
        "create",
        help="Plan or create one supplier invoice accrual from a JSON payload file",
    )
    supplier_invoice_accruals_create.add_argument(
        "--json-file",
        required=True,
        help="Path to the SupplierInvoiceAccrual JSON payload file",
    )
    _add_local_write_flags(supplier_invoice_accruals_create)
    supplier_invoice_accruals_create.set_defaults(
        func=supplier_invoice_accruals_cmd.cmd_supplier_invoice_accruals_create,
        write_capable=True,
    )
    supplier_invoice_accruals_update = supplier_invoice_accruals_sub.add_parser(
        "update",
        help="Plan or update one supplier invoice accrual from a JSON payload file",
    )
    supplier_invoice_accruals_update.add_argument(
        "--supplier-invoice-number",
        required=True,
        help="Fortnox supplier invoice number",
    )
    supplier_invoice_accruals_update.add_argument(
        "--json-file",
        required=True,
        help="Path to the SupplierInvoiceAccrual JSON payload file",
    )
    _add_local_write_flags(supplier_invoice_accruals_update)
    supplier_invoice_accruals_update.set_defaults(
        func=supplier_invoice_accruals_cmd.cmd_supplier_invoice_accruals_update,
        write_capable=True,
    )
    supplier_invoice_accruals_remove = supplier_invoice_accruals_sub.add_parser(
        "remove",
        help="Plan or remove one supplier invoice accrual",
    )
    supplier_invoice_accruals_remove.add_argument(
        "--supplier-invoice-number",
        required=True,
        help="Fortnox supplier invoice number",
    )
    _add_local_write_flags(supplier_invoice_accruals_remove)
    supplier_invoice_accruals_remove.set_defaults(
        func=supplier_invoice_accruals_cmd.cmd_supplier_invoice_accruals_remove,
        write_capable=True,
    )

    supplier_invoices = sub.add_parser("supplier-invoices", help="Supplier invoice commands")
    supplier_invoices_sub = supplier_invoices.add_subparsers(
        dest="supplier_invoices_cmd", required=True, parser_class=_ToolArgumentParser
    )
    supplier_invoices_list = supplier_invoices_sub.add_parser(
        "list",
        help="List supplier invoices",
    )
    supplier_invoices_list.set_defaults(
        func=supplier_invoices_cmd.cmd_supplier_invoices_list,
        write_capable=False,
    )
    supplier_invoices_get = supplier_invoices_sub.add_parser(
        "get",
        help="Get one supplier invoice",
    )
    supplier_invoices_get.add_argument(
        "--supplier-invoice-number",
        required=True,
        help="Fortnox supplier invoice number",
    )
    supplier_invoices_get.set_defaults(
        func=supplier_invoices_cmd.cmd_supplier_invoices_get,
        write_capable=False,
    )
    supplier_invoices_create = supplier_invoices_sub.add_parser(
        "create",
        help="Plan or create one supplier invoice from a JSON payload file",
    )
    supplier_invoices_create.add_argument(
        "--json-file",
        required=True,
        help="Path to the SupplierInvoice JSON payload file",
    )
    _add_local_write_flags(supplier_invoices_create)
    supplier_invoices_create.set_defaults(
        func=supplier_invoices_cmd.cmd_supplier_invoices_create,
        write_capable=True,
    )
    supplier_invoices_update = supplier_invoices_sub.add_parser(
        "update",
        help="Plan or update one supplier invoice from a JSON payload file",
    )
    supplier_invoices_update.add_argument(
        "--supplier-invoice-number",
        required=True,
        help="Fortnox supplier invoice number",
    )
    supplier_invoices_update.add_argument(
        "--json-file",
        required=True,
        help="Path to the SupplierInvoice JSON payload file",
    )
    _add_local_write_flags(supplier_invoices_update)
    supplier_invoices_update.set_defaults(
        func=supplier_invoices_cmd.cmd_supplier_invoices_update,
        write_capable=True,
    )
    supplier_invoices_approvalbookkeep = supplier_invoices_sub.add_parser(
        "approvalbookkeep",
        help="Plan or approvalbookkeep one supplier invoice from an optional JSON payload file",
    )
    supplier_invoices_approvalbookkeep.add_argument(
        "--supplier-invoice-number",
        required=True,
        help="Fortnox supplier invoice number",
    )
    supplier_invoices_approvalbookkeep.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the SupplierInvoice JSON payload file",
    )
    _add_local_write_flags(supplier_invoices_approvalbookkeep)
    supplier_invoices_approvalbookkeep.set_defaults(
        func=supplier_invoices_cmd.cmd_supplier_invoices_approvalbookkeep,
        write_capable=True,
    )
    supplier_invoices_approvalpayment = supplier_invoices_sub.add_parser(
        "approvalpayment",
        help="Plan or approvalpayment one supplier invoice from an optional JSON payload file",
    )
    supplier_invoices_approvalpayment.add_argument(
        "--supplier-invoice-number",
        required=True,
        help="Fortnox supplier invoice number",
    )
    supplier_invoices_approvalpayment.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the SupplierInvoice JSON payload file",
    )
    _add_local_write_flags(supplier_invoices_approvalpayment)
    supplier_invoices_approvalpayment.set_defaults(
        func=supplier_invoices_cmd.cmd_supplier_invoices_approvalpayment,
        write_capable=True,
    )
    supplier_invoices_bookkeep = supplier_invoices_sub.add_parser(
        "bookkeep",
        help="Plan or bookkeep one supplier invoice from an optional JSON payload file",
    )
    supplier_invoices_bookkeep.add_argument(
        "--supplier-invoice-number",
        required=True,
        help="Fortnox supplier invoice number",
    )
    supplier_invoices_bookkeep.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the SupplierInvoice JSON payload file",
    )
    _add_local_write_flags(supplier_invoices_bookkeep)
    supplier_invoices_bookkeep.set_defaults(
        func=supplier_invoices_cmd.cmd_supplier_invoices_bookkeep,
        write_capable=True,
    )
    supplier_invoices_cancel = supplier_invoices_sub.add_parser(
        "cancel",
        help="Plan or cancel one supplier invoice from an optional JSON payload file",
    )
    supplier_invoices_cancel.add_argument(
        "--supplier-invoice-number",
        required=True,
        help="Fortnox supplier invoice number",
    )
    supplier_invoices_cancel.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the SupplierInvoice JSON payload file",
    )
    _add_local_write_flags(supplier_invoices_cancel)
    supplier_invoices_cancel.set_defaults(
        func=supplier_invoices_cmd.cmd_supplier_invoices_cancel,
        write_capable=True,
    )
    supplier_invoices_credit = supplier_invoices_sub.add_parser(
        "credit",
        help="Plan or credit one supplier invoice from an optional JSON payload file",
    )
    supplier_invoices_credit.add_argument(
        "--supplier-invoice-number",
        required=True,
        help="Fortnox supplier invoice number",
    )
    supplier_invoices_credit.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the SupplierInvoice JSON payload file",
    )
    _add_local_write_flags(supplier_invoices_credit)
    supplier_invoices_credit.set_defaults(
        func=supplier_invoices_cmd.cmd_supplier_invoices_credit,
        write_capable=True,
    )

    supplier_invoice_payments = sub.add_parser("supplier-invoice-payments", help="Supplier invoice payment commands")
    supplier_invoice_payments_sub = supplier_invoice_payments.add_subparsers(
        dest="supplier_invoice_payments_cmd", required=True, parser_class=_ToolArgumentParser
    )
    supplier_invoice_payments_list = supplier_invoice_payments_sub.add_parser(
        "list",
        help="List supplier invoice payments",
    )
    supplier_invoice_payments_list.set_defaults(
        func=supplier_invoice_payments_cmd.cmd_supplier_invoice_payments_list,
        write_capable=False,
    )
    supplier_invoice_payments_get = supplier_invoice_payments_sub.add_parser(
        "get",
        help="Get one supplier invoice payment",
    )
    supplier_invoice_payments_get.add_argument(
        "--number",
        required=True,
        help="Fortnox supplier invoice payment number",
    )
    supplier_invoice_payments_get.set_defaults(
        func=supplier_invoice_payments_cmd.cmd_supplier_invoice_payments_get,
        write_capable=False,
    )
    supplier_invoice_payments_create = supplier_invoice_payments_sub.add_parser(
        "create",
        help="Plan or create one supplier invoice payment from a JSON payload file",
    )
    supplier_invoice_payments_create.add_argument(
        "--json-file",
        required=True,
        help="Path to the SupplierInvoicePayment JSON payload file",
    )
    _add_local_write_flags(supplier_invoice_payments_create)
    supplier_invoice_payments_create.set_defaults(
        func=supplier_invoice_payments_cmd.cmd_supplier_invoice_payments_create,
        write_capable=True,
    )
    supplier_invoice_payments_update = supplier_invoice_payments_sub.add_parser(
        "update",
        help="Plan or update one supplier invoice payment from a JSON payload file",
    )
    supplier_invoice_payments_update.add_argument(
        "--number",
        required=True,
        help="Fortnox supplier invoice payment number",
    )
    supplier_invoice_payments_update.add_argument(
        "--json-file",
        required=True,
        help="Path to the SupplierInvoicePayment JSON payload file",
    )
    _add_local_write_flags(supplier_invoice_payments_update)
    supplier_invoice_payments_update.set_defaults(
        func=supplier_invoice_payments_cmd.cmd_supplier_invoice_payments_update,
        write_capable=True,
    )
    supplier_invoice_payments_remove = supplier_invoice_payments_sub.add_parser(
        "remove",
        help="Plan or remove one supplier invoice payment",
    )
    supplier_invoice_payments_remove.add_argument(
        "--number",
        required=True,
        help="Fortnox supplier invoice payment number",
    )
    _add_local_write_flags(supplier_invoice_payments_remove)
    supplier_invoice_payments_remove.set_defaults(
        func=supplier_invoice_payments_cmd.cmd_supplier_invoice_payments_remove,
        write_capable=True,
    )
    supplier_invoice_payments_bookkeep = supplier_invoice_payments_sub.add_parser(
        "bookkeep",
        help="Plan or bookkeep one supplier invoice payment from a JSON payload file",
    )
    supplier_invoice_payments_bookkeep.add_argument(
        "--number",
        required=True,
        help="Fortnox supplier invoice payment number",
    )
    supplier_invoice_payments_bookkeep.add_argument(
        "--json-file",
        required=True,
        help="Path to the SupplierInvoicePayment JSON payload file",
    )
    _add_local_write_flags(supplier_invoice_payments_bookkeep)
    supplier_invoice_payments_bookkeep.set_defaults(
        func=supplier_invoice_payments_cmd.cmd_supplier_invoice_payments_bookkeep,
        write_capable=True,
    )

    offers = sub.add_parser("offers", help="Offer commands")
    offers_sub = offers.add_subparsers(dest="offers_cmd", required=True, parser_class=_ToolArgumentParser)
    offers_list = offers_sub.add_parser("list", help="List offers")
    offers_list.set_defaults(func=accounting_reads_cmd.cmd_offers_list, write_capable=False)
    offers_get = offers_sub.add_parser("get", help="Get one offer")
    offers_get.add_argument("--document-number", required=True, help="Fortnox offer document number")
    offers_get.set_defaults(func=accounting_reads_cmd.cmd_offers_get, write_capable=False)
    offers_preview = offers_sub.add_parser("preview", help="Preview one offer as PDF")
    offers_preview.add_argument("--document-number", required=True, help="Fortnox offer document number")
    _add_download_output_flag(offers_preview, noun="offer PDF")
    offers_preview.set_defaults(func=accounting_reads_cmd.cmd_offers_preview, write_capable=False)
    offers_print = offers_sub.add_parser("print", help="Print one offer as PDF")
    offers_print.add_argument("--document-number", required=True, help="Fortnox offer document number")
    _add_download_output_flag(offers_print, noun="offer PDF")
    offers_print.set_defaults(func=accounting_reads_cmd.cmd_offers_print, write_capable=False)
    offers_send_as_email = offers_sub.add_parser(
        "send-given-offer-as-email",
        help="Plan or send one offer as email",
    )
    offers_send_as_email.add_argument("--document-number", required=True, help="Fortnox offer document number")
    _add_local_write_flags(offers_send_as_email)
    offers_send_as_email.set_defaults(func=offers_cmd.cmd_offers_send_as_email, write_capable=True)
    offers_create = offers_sub.add_parser(
        "create",
        help="Plan or create one offer from a JSON payload file",
    )
    offers_create.add_argument("--json-file", required=True, help="Path to the Offer JSON payload file")
    _add_local_write_flags(offers_create)
    offers_create.set_defaults(func=offers_cmd.cmd_offers_create, write_capable=True)
    offers_update = offers_sub.add_parser(
        "update",
        help="Plan or update one offer from a JSON payload file",
    )
    offers_update.add_argument("--document-number", required=True, help="Fortnox offer document number")
    offers_update.add_argument("--json-file", required=True, help="Path to the Offer JSON payload file")
    _add_local_write_flags(offers_update)
    offers_update.set_defaults(func=offers_cmd.cmd_offers_update, write_capable=True)
    offers_cancel = offers_sub.add_parser(
        "cancel",
        help="Plan or cancel one offer from an optional JSON payload file",
    )
    offers_cancel.add_argument("--document-number", required=True, help="Fortnox offer document number")
    offers_cancel.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the Offer JSON payload file",
    )
    _add_local_write_flags(offers_cancel)
    offers_cancel.set_defaults(func=offers_cmd.cmd_offers_cancel, write_capable=True)
    offers_createinvoice = offers_sub.add_parser(
        "create-invoice",
        help="Plan or create invoice from one offer from an optional JSON payload file",
    )
    offers_createinvoice.add_argument("--document-number", required=True, help="Fortnox offer document number")
    offers_createinvoice.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the Offer JSON payload file",
    )
    _add_local_write_flags(offers_createinvoice)
    offers_createinvoice.set_defaults(func=offers_cmd.cmd_offers_createinvoice, write_capable=True)
    offers_createorder = offers_sub.add_parser(
        "create-order",
        help="Plan or create order from one offer from an optional JSON payload file",
    )
    offers_createorder.add_argument("--document-number", required=True, help="Fortnox offer document number")
    offers_createorder.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the Offer JSON payload file",
    )
    _add_local_write_flags(offers_createorder)
    offers_createorder.set_defaults(func=offers_cmd.cmd_offers_createorder, write_capable=True)
    offers_externalprint = offers_sub.add_parser(
        "externalprint",
        help="Plan or send one offer to external print from an optional JSON payload file",
    )
    offers_externalprint.add_argument("--document-number", required=True, help="Fortnox offer document number")
    offers_externalprint.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the Offer JSON payload file",
    )
    _add_local_write_flags(offers_externalprint)
    offers_externalprint.set_defaults(func=offers_cmd.cmd_offers_externalprint, write_capable=True)

    orders = sub.add_parser("orders", help="Order commands")
    orders_sub = orders.add_subparsers(dest="orders_cmd", required=True, parser_class=_ToolArgumentParser)
    orders_list = orders_sub.add_parser("list", help="List orders")
    orders_list.set_defaults(func=accounting_reads_cmd.cmd_orders_list, write_capable=False)
    orders_get = orders_sub.add_parser("get", help="Get one order")
    orders_get.add_argument("--document-number", required=True, help="Fortnox order document number")
    orders_get.set_defaults(func=accounting_reads_cmd.cmd_orders_get, write_capable=False)
    orders_preview = orders_sub.add_parser("preview", help="Preview one order as PDF")
    orders_preview.add_argument("--document-number", required=True, help="Fortnox order document number")
    _add_download_output_flag(orders_preview, noun="order PDF")
    orders_preview.set_defaults(func=accounting_reads_cmd.cmd_orders_preview, write_capable=False)
    orders_print = orders_sub.add_parser("print", help="Print one order as PDF")
    orders_print.add_argument("--document-number", required=True, help="Fortnox order document number")
    _add_download_output_flag(orders_print, noun="order PDF")
    orders_print.set_defaults(func=accounting_reads_cmd.cmd_orders_print, write_capable=False)
    orders_send_as_email = orders_sub.add_parser(
        "send-given-order-as-email",
        help="Plan or send one order as email",
    )
    orders_send_as_email.add_argument("--document-number", required=True, help="Fortnox order document number")
    _add_local_write_flags(orders_send_as_email)
    orders_send_as_email.set_defaults(func=orders_cmd.cmd_orders_send_as_email, write_capable=True)
    orders_create = orders_sub.add_parser(
        "create",
        help="Plan or create one order from a JSON payload file",
    )
    orders_create.add_argument("--json-file", required=True, help="Path to the Order JSON payload file")
    _add_local_write_flags(orders_create)
    orders_create.set_defaults(func=orders_cmd.cmd_orders_create, write_capable=True)
    orders_update = orders_sub.add_parser(
        "update",
        help="Plan or update one order from a JSON payload file",
    )
    orders_update.add_argument("--document-number", required=True, help="Fortnox order document number")
    orders_update.add_argument("--json-file", required=True, help="Path to the Order JSON payload file")
    _add_local_write_flags(orders_update)
    orders_update.set_defaults(func=orders_cmd.cmd_orders_update, write_capable=True)
    orders_cancel = orders_sub.add_parser(
        "cancel",
        help="Plan or cancel one order from an optional JSON payload file",
    )
    orders_cancel.add_argument("--document-number", required=True, help="Fortnox order document number")
    orders_cancel.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the Order JSON payload file",
    )
    _add_local_write_flags(orders_cancel)
    orders_cancel.set_defaults(func=orders_cmd.cmd_orders_cancel, write_capable=True)
    orders_createinvoice = orders_sub.add_parser(
        "create-invoice",
        help="Plan or create invoice from one order from an optional JSON payload file",
    )
    orders_createinvoice.add_argument("--document-number", required=True, help="Fortnox order document number")
    orders_createinvoice.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the Order JSON payload file",
    )
    _add_local_write_flags(orders_createinvoice)
    orders_createinvoice.set_defaults(func=orders_cmd.cmd_orders_createinvoice, write_capable=True)
    orders_externalprint = orders_sub.add_parser(
        "externalprint",
        help="Plan or send one order to external print from an optional JSON payload file",
    )
    orders_externalprint.add_argument("--document-number", required=True, help="Fortnox order document number")
    orders_externalprint.add_argument(
        "--json-file",
        required=False,
        help="Optional path to the Order JSON payload file",
    )
    _add_local_write_flags(orders_externalprint)
    orders_externalprint.set_defaults(func=orders_cmd.cmd_orders_externalprint, write_capable=True)

    jobs = sub.add_parser("jobs", help="Batch operations from job files")
    jobs_sub = jobs.add_subparsers(dest="jobs_cmd", required=True, parser_class=_ToolArgumentParser)
    jobs_run = jobs_sub.add_parser("run", help="Reserved for future registry-backed Fortnox batch rows")
    jobs_run.add_argument("--file", required=False, help="Reserved job CSV file path")
    jobs_run.add_argument("--limit", type=int, default=None, help="Reserved max row count")
    jobs_run.set_defaults(func=jobs_cmd.cmd_jobs_run, write_capable=True)

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

    project_cfg, config_dir = load_project_config(str(getattr(args, "config", None) or "") or None)
    project_dir_arg = str(getattr(args, "project_dir", "") or "").strip()
    project_dir = Path(project_dir_arg) if project_dir_arg else (Path(config_dir) if config_dir else Path("."))

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
            payload = {"ok": True, "tool": "fortnox-api-tool", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"fortnox-api-tool {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        command_str = "fortnox-api-tool " + " ".join(argv)
        audit.bind_context(
            {
                "tool": "fortnox-api-tool",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "env_fingerprint": None,
                "run_id": run_ctx.run_id,
            }
        )

        # Some commands are local-only and don't need API config.
        if str(getattr(args, "cmd", "") or "") in {"runs", "onboarding"}:
            ctx = {
                "cfg": None,
                "out": out,
                "audit": audit,
                "tool": "fortnox-api-tool",
                "tool_version": __version__,
                "command_str": command_str,
                "project_cfg": project_cfg,
                "project_dir": project_dir,
                "env_file": str(args.env_file),
                "timeout_s": None,
                "verbose": bool(args.verbose),
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "plan_out": args.plan_out,
                "plan_in": args.plan_in,
                "receipt_out": args.receipt_out,
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "ack_irreversible": bool(args.ack_irreversible),
                "run_id": run_ctx.run_id,
                "artifacts_dir": run_ctx.artifacts_dir,
                "runs_index_path": runs_index_path,
            }
            rc = int(args.func(args, ctx))
            return rc

        cfg = load_config(args.env_file)
        env_fingerprint = cfg.base_url
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "tool": "fortnox-api-tool",
            "tool_version": __version__,
            "command_str": command_str,
            "project_cfg": project_cfg,
            "project_dir": project_dir,
            "env_file": str(args.env_file),
            "timeout_s": timeout_s,
            "verbose": bool(args.verbose),
            "apply": bool(args.apply),
            "yes": bool(args.yes),
            "plan_out": args.plan_out,
            "plan_in": args.plan_in,
            "receipt_out": args.receipt_out,
            "ack_no_snapshot": bool(args.ack_no_snapshot),
            "ack_irreversible": bool(args.ack_irreversible),
            "run_id": run_ctx.run_id,
            "artifacts_dir": run_ctx.artifacts_dir,
            "runs_index_path": run_ctx.runs_index_path,
            "audit_log_path": run_audit_log_path or global_audit_log_path,
            "audit_log_run_path": run_audit_log_path,
            "audit_log_global_path": global_audit_log_path,
        }

        if run_ctx.enabled and run_ctx.artifacts_dir:
            if not bool(args.apply) and not ctx.get("plan_out"):
                ctx["plan_out"] = str(run_ctx.artifacts_dir / "plan.json")
            if bool(args.apply) and not ctx.get("receipt_out"):
                ctx["receipt_out"] = str(run_ctx.artifacts_dir / "receipt.json")

        audit.bind_context(
            {
                "tool": "fortnox-api-tool",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "env_fingerprint": cfg.base_url,
                "run_id": run_ctx.run_id,
            }
        )
        rc = int(args.func(args, ctx))

        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="fortnox-api-tool",
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
            tool="fortnox-api-tool",
            version=__version__,
            command="fortnox-api-tool " + " ".join(argv),
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
            tool="fortnox-api-tool",
            version=__version__,
            command="fortnox-api-tool " + " ".join(argv),
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
            tool="fortnox-api-tool",
            version=__version__,
            command="fortnox-api-tool " + " ".join(argv),
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
