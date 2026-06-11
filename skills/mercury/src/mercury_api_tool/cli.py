from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import api as api_cmd
from .commands import auth as auth_cmd
from .commands import downloads as downloads_cmd
from .commands import exports as exports_cmd
from .commands import onboarding as onboarding_cmd
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


def _cmd_runs_list(args: argparse.Namespace, ctx: dict) -> int:
    _ = args
    runs_index = ctx.get("runs_index_path")
    if not runs_index:
        ctx["out"].emit({"ok": True, "runs": [], "count": 0, "runs_index": None})
        return 0
    limit = int(getattr(args, "limit", 20) or 20)
    rows = list_runs(runs_index, limit=limit)
    ctx["out"].emit({"ok": True, "runs": rows, "count": len(rows), "runs_index": str(runs_index)})
    return 0


def _cmd_runs_show(args: argparse.Namespace, ctx: dict) -> int:
    rid = str(getattr(args, "run_id", "") or "").strip()
    if not rid:
        ctx["out"].emit({"ok": False, "error": "Missing --run-id", "error_type": "ValidationError"})
        return 1
    runs_index = ctx.get("runs_index_path")
    if not runs_index or not runs_index.exists():
        ctx["out"].emit({"ok": False, "error": "No runs index found", "error_type": "NotFound", "runs_index": str(runs_index) if runs_index else None})
        return 1
    row = find_run(runs_index, run_id=rid)
    if not row:
        ctx["out"].emit(
            {"ok": False, "error": f"Run not found: {rid}", "error_type": "NotFound", "runs_index": str(runs_index)}
        )
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
    ctx["out"].emit({"ok": True, "run": row, "summary_md": summary, "runs_index": str(runs_index)})
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
    p = _ToolArgumentParser(prog="mercury-api-tool")
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

    organization = sub.add_parser("organization", help="Organization information")
    organization_sub = organization.add_subparsers(
        dest="organization_cmd", required=True, parser_class=_ToolArgumentParser
    )
    organization_get = organization_sub.add_parser("get", help="Get organization info")
    organization_get.set_defaults(func=api_cmd.cmd_get_organization, write_capable=False)

    accounts = sub.add_parser("accounts", help="Accounts API")
    accounts_sub = accounts.add_subparsers(dest="accounts_cmd", required=True, parser_class=_ToolArgumentParser)
    accounts_list = accounts_sub.add_parser("list", help="Get all accounts")
    accounts_list.set_defaults(func=api_cmd.cmd_list_accounts, write_capable=False)
    accounts_get = accounts_sub.add_parser("get", help="Get account by id")
    accounts_get.add_argument("--account-id", required=True)
    accounts_get.set_defaults(func=api_cmd.cmd_get_account, write_capable=False)
    accounts_cards = accounts_sub.add_parser("cards", help="Get cards for account")
    accounts_cards.add_argument("--account-id", required=True)
    accounts_cards.set_defaults(func=api_cmd.cmd_list_account_cards, write_capable=False)
    accounts_statements = accounts_sub.add_parser("statements", help="Get account statements")
    accounts_statements.add_argument("--account-id", required=True)
    accounts_statements.set_defaults(func=api_cmd.cmd_list_account_statements, write_capable=False)
    accounts_transactions = accounts_sub.add_parser("transactions", help="List account transactions")
    accounts_transactions.add_argument("--account-id", required=True)
    accounts_transactions.add_argument("--limit", type=int, default=None)
    accounts_transactions.add_argument("--start", default=None, help="Filter by transaction created date (start)")
    accounts_transactions.add_argument("--end", default=None, help="Filter by transaction created date (end)")
    accounts_transactions.add_argument("--search", default=None)
    accounts_transactions.add_argument("--status", default=None)
    accounts_transactions.add_argument("--offset", type=int, default=None)
    accounts_transactions.add_argument("--order", default=None)
    accounts_transactions.add_argument("--request-id", default=None)
    accounts_transactions.add_argument("--mercury-category", default=None)
    accounts_transactions.add_argument("--category-id", default=None)
    accounts_transactions.set_defaults(func=api_cmd.cmd_list_account_transactions, write_capable=False)
    accounts_transaction_get = accounts_sub.add_parser("transaction", help="Get account transaction by id")
    accounts_transaction_get.add_argument("--account-id", required=True)
    accounts_transaction_get.add_argument("--transaction-id", required=True)
    accounts_transaction_get.set_defaults(func=api_cmd.cmd_get_account_transaction, write_capable=False)

    transactions = sub.add_parser("transactions", help="Transactions API")
    transactions_sub = transactions.add_subparsers(
        dest="transactions_cmd", required=True, parser_class=_ToolArgumentParser
    )
    transactions_list = transactions_sub.add_parser("list", help="List all transactions")
    transactions_list.add_argument("--status", action="append", default=None)
    transactions_list.add_argument("--search", default=None)
    transactions_list.add_argument("--start", default=None)
    transactions_list.add_argument("--end", default=None)
    transactions_list.add_argument("--posted-start", default=None)
    transactions_list.add_argument("--posted-end", default=None)
    transactions_list.add_argument("--account-id", action="append", default=None)
    transactions_list.add_argument("--mercury-category", default=None)
    transactions_list.add_argument("--category-id", default=None)
    transactions_list.add_argument("--start-at", default=None)
    transactions_list.add_argument("--start-after", default=None)
    transactions_list.add_argument("--end-before", default=None)
    transactions_list.add_argument("--limit", type=int, default=None)
    transactions_list.add_argument("--order", default=None)
    transactions_list.set_defaults(func=api_cmd.cmd_list_transactions, write_capable=False)
    transactions_get = transactions_sub.add_parser("get", help="Get a transaction by ID")
    transactions_get.add_argument("--transaction-id", required=True)
    transactions_get.set_defaults(func=api_cmd.cmd_get_transaction, write_capable=False)

    treasury = sub.add_parser("treasury", help="Treasury API")
    treasury_sub = treasury.add_subparsers(dest="treasury_cmd", required=True, parser_class=_ToolArgumentParser)
    treasury_list = treasury_sub.add_parser("list", help="Get all treasury accounts")
    treasury_list.set_defaults(func=api_cmd.cmd_list_treasury, write_capable=False)
    treasury_transactions = treasury_sub.add_parser("transactions", help="Get treasury transactions")
    treasury_transactions.add_argument("--treasury-id", required=True)
    treasury_transactions.add_argument("--limit", type=int, default=None)
    treasury_transactions.add_argument("--order", default=None)
    treasury_transactions.add_argument("--cursor", type=int, default=None)
    treasury_transactions.set_defaults(func=api_cmd.cmd_list_treasury_transactions, write_capable=False)

    users = sub.add_parser("users", help="Users API")
    users_sub = users.add_subparsers(dest="users_cmd", required=True, parser_class=_ToolArgumentParser)
    users_list = users_sub.add_parser("list", help="Get all users")
    users_list.set_defaults(func=api_cmd.cmd_list_users, write_capable=False)
    users_get = users_sub.add_parser("get", help="Get user by id")
    users_get.add_argument("--user-id", required=True)
    users_get.set_defaults(func=api_cmd.cmd_get_user, write_capable=False)

    categories = sub.add_parser("categories", help="Categories API")
    categories_sub = categories.add_subparsers(
        dest="categories_cmd", required=True, parser_class=_ToolArgumentParser
    )
    categories_list = categories_sub.add_parser("list", help="List all categories")
    categories_list.set_defaults(func=api_cmd.cmd_list_categories, write_capable=False)

    credit = sub.add_parser("credit", help="Credit API")
    credit_sub = credit.add_subparsers(dest="credit_cmd", required=True, parser_class=_ToolArgumentParser)
    credit_list = credit_sub.add_parser("list", help="List all credit accounts")
    credit_list.set_defaults(func=api_cmd.cmd_list_credit, write_capable=False)

    events = sub.add_parser("events", help="Events API")
    events_sub = events.add_subparsers(dest="events_cmd", required=True, parser_class=_ToolArgumentParser)
    events_list = events_sub.add_parser("list", help="Get all events")
    events_list.set_defaults(func=api_cmd.cmd_list_events, write_capable=False)
    events_get = events_sub.add_parser("get", help="Get event by id")
    events_get.add_argument("--event-id", required=True)
    events_get.set_defaults(func=api_cmd.cmd_get_event, write_capable=False)

    recipients = sub.add_parser("recipients", help="Recipients API")
    recipients_sub = recipients.add_subparsers(
        dest="recipients_cmd", required=True, parser_class=_ToolArgumentParser
    )
    recipients_list = recipients_sub.add_parser("list", help="Get all recipients")
    recipients_list.set_defaults(func=api_cmd.cmd_list_recipients, write_capable=False)
    recipients_get = recipients_sub.add_parser("get", help="Get recipient by id")
    recipients_get.add_argument("--recipient-id", required=True)
    recipients_get.set_defaults(func=api_cmd.cmd_get_recipient, write_capable=False)
    recipients_attachments = recipients_sub.add_parser("attachments", help="List all recipient attachments")
    recipients_attachments.set_defaults(func=api_cmd.cmd_list_recipient_attachments, write_capable=False)

    send_money = sub.add_parser("send-money", help="Send Money (read-only)")
    send_money_sub = send_money.add_subparsers(
        dest="send_money_cmd", required=True, parser_class=_ToolArgumentParser
    )
    send_money_get = send_money_sub.add_parser(
        "approval-request", help="Get send money approval request by id"
    )
    send_money_get.add_argument("--request-id", required=True)
    send_money_get.set_defaults(func=api_cmd.cmd_get_send_money_approval_request, write_capable=False)

    customers = sub.add_parser("customers", help="Customers API")
    customers_sub = customers.add_subparsers(
        dest="customers_cmd", required=True, parser_class=_ToolArgumentParser
    )
    customers_list = customers_sub.add_parser("list", help="List all customers")
    customers_list.set_defaults(func=api_cmd.cmd_list_customers, write_capable=False)
    customers_get = customers_sub.add_parser("get", help="Get a customer")
    customers_get.add_argument("--customer-id", required=True)
    customers_get.set_defaults(func=api_cmd.cmd_get_customer, write_capable=False)

    invoices = sub.add_parser("invoices", help="Invoices API")
    invoices_sub = invoices.add_subparsers(dest="invoices_cmd", required=True, parser_class=_ToolArgumentParser)
    invoices_list = invoices_sub.add_parser("list", help="List all invoices")
    invoices_list.add_argument("--status", default=None)
    invoices_list.add_argument("--customer-id", default=None)
    invoices_list.add_argument("--limit", type=int, default=None)
    invoices_list.add_argument("--starting-after", default=None)
    invoices_list.add_argument("--ending-before", default=None)
    invoices_list.add_argument("--search", default=None)
    invoices_list.set_defaults(func=api_cmd.cmd_list_invoices, write_capable=False)
    invoices_get = invoices_sub.add_parser("get", help="Get an invoice")
    invoices_get.add_argument("--invoice-id", required=True)
    invoices_get.set_defaults(func=api_cmd.cmd_get_invoice, write_capable=False)
    invoices_attachments = invoices_sub.add_parser("attachments", help="List invoice attachments")
    invoices_attachments.add_argument("--invoice-id", required=True)
    invoices_attachments.set_defaults(func=api_cmd.cmd_list_invoice_attachments, write_capable=False)
    invoices_attachment_get = invoices_sub.add_parser("attachment", help="Get an attachment metadata (JSON)")
    invoices_attachment_get.add_argument("--attachment-id", required=True)
    invoices_attachment_get.set_defaults(func=api_cmd.cmd_get_attachment, write_capable=False)
    invoices_download_pdf = invoices_sub.add_parser("download-pdf", help="Download invoice PDF (local file write)")
    invoices_download_pdf.add_argument("--invoice-id", required=True)
    invoices_download_pdf.add_argument("--out", default=None)
    invoices_download_pdf.add_argument("--out-dir", default=None)
    invoices_download_pdf.set_defaults(func=downloads_cmd.cmd_download_invoice_pdf, write_capable=True)
    invoices_download_attachment = invoices_sub.add_parser(
        "download-attachment", help="Download an attachment (local file write)"
    )
    invoices_download_attachment.add_argument("--attachment-id", required=True)
    invoices_download_attachment.add_argument("--out", default=None)
    invoices_download_attachment.add_argument("--out-dir", default=None)
    invoices_download_attachment.add_argument("--file-name", default=None, help="Override output filename")
    invoices_download_attachment.set_defaults(
        func=downloads_cmd.cmd_download_invoice_attachment, write_capable=True
    )

    statements = sub.add_parser("statements", help="Statements API")
    statements_sub = statements.add_subparsers(
        dest="statements_cmd", required=True, parser_class=_ToolArgumentParser
    )
    statements_download = statements_sub.add_parser(
        "download-pdf", help="Download account statement PDF (local file write)"
    )
    statements_download.add_argument("--statement-id", required=True)
    statements_download.add_argument("--out", default=None)
    statements_download.add_argument("--out-dir", default=None)
    statements_download.set_defaults(func=downloads_cmd.cmd_download_statement_pdf, write_capable=True)

    webhooks = sub.add_parser("webhooks", help="Webhooks API")
    webhooks_sub = webhooks.add_subparsers(dest="webhooks_cmd", required=True, parser_class=_ToolArgumentParser)
    webhooks_list = webhooks_sub.add_parser("list", help="Get webhook endpoints")
    webhooks_list.set_defaults(func=api_cmd.cmd_list_webhooks, write_capable=False)
    webhooks_get = webhooks_sub.add_parser("get", help="Get webhook endpoint by id")
    webhooks_get.add_argument("--webhook-endpoint-id", required=True)
    webhooks_get.set_defaults(func=api_cmd.cmd_get_webhook, write_capable=False)

    books = sub.add_parser("books", help="Books API")
    books_sub = books.add_subparsers(dest="books_cmd", required=True, parser_class=_ToolArgumentParser)
    books_journal_entries = books_sub.add_parser("journal-entries", help="List all journal entries")
    books_journal_entries.add_argument("--books-id", required=True)
    books_journal_entries.set_defaults(func=api_cmd.cmd_list_books_journal_entries, write_capable=False)
    books_journal_entry = books_sub.add_parser("journal-entry", help="Retrieve a Journal Entry")
    books_journal_entry.add_argument("--books-id", required=True)
    books_journal_entry.add_argument("--teal-journal-entry-id", required=True)
    books_journal_entry.set_defaults(func=api_cmd.cmd_get_books_journal_entry, write_capable=False)

    export = sub.add_parser("export", help="Local exports (file writes gated by --apply)")
    export_sub = export.add_subparsers(dest="export_cmd", required=True, parser_class=_ToolArgumentParser)
    export_transactions = export_sub.add_parser("transactions", help="Export transactions to JSON/CSV")
    export_transactions.add_argument("--format", choices=("json", "csv"), default="json")
    export_transactions.add_argument("--out", default=None)
    export_transactions.add_argument("--out-dir", default=None)
    export_transactions.add_argument("--max-pages", type=int, default=10)
    export_transactions.add_argument("--status", action="append", default=None)
    export_transactions.add_argument("--search", default=None)
    export_transactions.add_argument("--start", default=None)
    export_transactions.add_argument("--end", default=None)
    export_transactions.add_argument("--posted-start", default=None)
    export_transactions.add_argument("--posted-end", default=None)
    export_transactions.add_argument("--account-id", action="append", default=None)
    export_transactions.add_argument("--mercury-category", default=None)
    export_transactions.add_argument("--category-id", default=None)
    export_transactions.add_argument("--start-at", default=None)
    export_transactions.add_argument("--start-after", default=None)
    export_transactions.add_argument("--end-before", default=None)
    export_transactions.add_argument("--limit", type=int, default=None)
    export_transactions.add_argument("--order", default=None)
    export_transactions.set_defaults(func=exports_cmd.cmd_export_transactions, write_capable=True)

    report = sub.add_parser("report", help="Read-only reports")
    report_sub = report.add_subparsers(dest="report_cmd", required=True, parser_class=_ToolArgumentParser)
    report_transactions_summary = report_sub.add_parser(
        "transactions-summary", help="Summarize transactions (count + totals by kind/category)"
    )
    report_transactions_summary.add_argument("--max-pages", type=int, default=10)
    report_transactions_summary.add_argument("--status", action="append", default=None)
    report_transactions_summary.add_argument("--search", default=None)
    report_transactions_summary.add_argument("--start", default=None)
    report_transactions_summary.add_argument("--end", default=None)
    report_transactions_summary.add_argument("--posted-start", default=None)
    report_transactions_summary.add_argument("--posted-end", default=None)
    report_transactions_summary.add_argument("--account-id", action="append", default=None)
    report_transactions_summary.add_argument("--mercury-category", default=None)
    report_transactions_summary.add_argument("--category-id", default=None)
    report_transactions_summary.add_argument("--start-at", default=None)
    report_transactions_summary.add_argument("--start-after", default=None)
    report_transactions_summary.add_argument("--end-before", default=None)
    report_transactions_summary.add_argument("--limit", type=int, default=None)
    report_transactions_summary.add_argument("--order", default=None)
    report_transactions_summary.set_defaults(
        func=exports_cmd.cmd_report_transactions_summary, write_capable=False
    )

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

    # Provenance (paths + run ids) is intentionally only included for write-capable commands.
    # This keeps read-only API outputs minimal and avoids printing machine-specific paths unless needed.
    if write_capable:
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
            payload = {"ok": True, "tool": "mercury-api-tool", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"mercury-api-tool {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        command_str = "mercury-api-tool " + " ".join(argv)
        audit.bind_context(
            {
                "tool": "mercury-api-tool",
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
        if str(getattr(args, "cmd", "") or "") in {"runs", "onboarding"}:
            ctx = {
                "cfg": None,
                "out": out,
                "audit": audit,
                "tool": "mercury-api-tool",
                "tool_version": __version__,
                "command_str": command_str,
                "project_cfg": project_cfg,
                "project_dir": project_dir,
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
            "tool": "mercury-api-tool",
            "tool_version": __version__,
            "command_str": command_str,
            "project_cfg": project_cfg,
            "project_dir": project_dir,
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
        }

        if run_ctx.enabled and run_ctx.artifacts_dir:
            if not bool(args.apply) and not ctx.get("plan_out"):
                ctx["plan_out"] = str(run_ctx.artifacts_dir / "plan.json")
            if bool(args.apply) and not ctx.get("receipt_out"):
                ctx["receipt_out"] = str(run_ctx.artifacts_dir / "receipt.json")

        audit.bind_context(
            {
                "tool": "mercury-api-tool",
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
            tool="mercury-api-tool",
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
            tool="mercury-api-tool",
            version=__version__,
            command="mercury-api-tool " + " ".join(argv),
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
            tool="mercury-api-tool",
            version=__version__,
            command="mercury-api-tool " + " ".join(argv),
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
            tool="mercury-api-tool",
            version=__version__,
            command="mercury-api-tool " + " ".join(argv),
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
