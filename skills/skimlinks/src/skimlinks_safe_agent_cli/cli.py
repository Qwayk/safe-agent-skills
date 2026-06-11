from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import auth as auth_cmd
from .commands import link_wrapper as link_wrapper_cmd
from .commands import merchant as merchant_cmd
from .commands import onboarding as onboarding_cmd
from .commands import product_key as product_key_cmd
from .commands import reporting as reporting_cmd
from .config import load_config
from .errors import SafetyError, ToolError, ValidationError
from .output import Output
from .project_config import load_project_config
from .runs import (
    RunContext,
    append_index_row,
    build_deterministic_summary,
    find_run,
    init_run_context,
    list_runs,
    runs_index_path_for_env_file,
    write_summary_md,
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


def _add_publisher_id(p: argparse.ArgumentParser) -> None:
    p.add_argument("--publisher-id", default=None, help="Override SKIMLINKS_PUBLISHER_ID")


def _add_publisher_domain_id(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--publisher-domain-id",
        default=None,
        help="Publisher domain ID (defaults to SKIMLINKS_PUBLISHER_DOMAIN_ID when supported or required)",
    )


def _add_pagination(p: argparse.ArgumentParser) -> None:
    p.add_argument("--limit", type=int, default=None, help="Result limit")
    p.add_argument("--offset", type=int, default=None, help="Pagination offset")


def _add_sort(p: argparse.ArgumentParser) -> None:
    p.add_argument("--sort-by", default=None, help="Official sort field")
    p.add_argument("--sort-dir", default=None, choices=("ASC", "DESC", "asc", "desc"), help="Sort direction")


def _add_date_range(p: argparse.ArgumentParser, *, required: bool) -> None:
    p.add_argument("--start-date", required=required, help="Start date or datetime")
    p.add_argument("--end-date", required=required, help="End date or datetime")


def build_parser() -> argparse.ArgumentParser:
    p = _ToolArgumentParser(prog="skimlinks-safe-cli")
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
    auth_check.add_argument(
        "--scope",
        choices=("shared", "product", "all"),
        default="shared",
        help="Credential scope to check (default: shared)",
    )
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=False)

    merchant = sub.add_parser("merchant", help="Merchant API")
    merchant_sub = merchant.add_subparsers(
        dest="merchant_cmd", required=True, parser_class=_ToolArgumentParser
    )
    merchant_merchants = merchant_sub.add_parser("merchants", help="Merchant records")
    merchant_merchants_sub = merchant_merchants.add_subparsers(
        dest="merchant_merchants_cmd", required=True, parser_class=_ToolArgumentParser
    )
    merchant_merchants_list = merchant_merchants_sub.add_parser("list", help="List/search merchants")
    _add_publisher_id(merchant_merchants_list)
    _add_publisher_domain_id(merchant_merchants_list)
    _add_pagination(merchant_merchants_list)
    _add_sort(merchant_merchants_list)
    merchant_merchants_list.add_argument("--search", default=None)
    merchant_merchants_list.add_argument("--vertical", default=None)
    merchant_merchants_list.add_argument("--id", default=None)
    merchant_merchants_list.add_argument("--country", default=None)
    merchant_merchants_list.add_argument("--favourite-type", default=None)
    merchant_merchants_list.add_argument("--a-id", default=None)
    merchant_merchants_list.add_argument("--merchant-id", default=None)
    merchant_merchants_list.add_argument("--alternative-vertical-id", default=None)
    merchant_merchants_list.add_argument("--alternative-vertical-taxonomy", default=None)
    merchant_merchants_list.add_argument("--alternative-vertical-country", default=None)
    merchant_merchants_list.set_defaults(func=merchant_cmd.cmd_merchants_list, write_capable=False)

    merchant_domains = merchant_sub.add_parser("domains", help="Merchant domains")
    merchant_domains_sub = merchant_domains.add_subparsers(
        dest="merchant_domains_cmd", required=True, parser_class=_ToolArgumentParser
    )
    merchant_domains_list = merchant_domains_sub.add_parser("list", help="List domains")
    _add_publisher_id(merchant_domains_list)
    merchant_domains_list.set_defaults(func=merchant_cmd.cmd_domains_list, write_capable=False)

    merchant_verticals = merchant_sub.add_parser("verticals", help="Verticals")
    merchant_verticals_sub = merchant_verticals.add_subparsers(
        dest="merchant_verticals_cmd", required=True, parser_class=_ToolArgumentParser
    )
    merchant_verticals_list = merchant_verticals_sub.add_parser("list", help="List verticals")
    merchant_verticals_list.set_defaults(func=merchant_cmd.cmd_verticals_list, write_capable=False)

    merchant_alt_verticals = merchant_sub.add_parser("alternative-verticals", help="Alternative verticals")
    merchant_alt_verticals_sub = merchant_alt_verticals.add_subparsers(
        dest="merchant_alt_verticals_cmd", required=True, parser_class=_ToolArgumentParser
    )
    merchant_alt_verticals_list = merchant_alt_verticals_sub.add_parser(
        "list", help="List alternative verticals"
    )
    merchant_alt_verticals_list.set_defaults(
        func=merchant_cmd.cmd_alternative_verticals_list, write_capable=False
    )

    merchant_offers = merchant_sub.add_parser("offers", help="Offers")
    merchant_offers_sub = merchant_offers.add_subparsers(
        dest="merchant_offers_cmd", required=True, parser_class=_ToolArgumentParser
    )
    merchant_offers_list = merchant_offers_sub.add_parser("list", help="List/search offers")
    _add_publisher_id(merchant_offers_list)
    _add_pagination(merchant_offers_list)
    _add_sort(merchant_offers_list)
    merchant_offers_list.add_argument("--search", default=None)
    merchant_offers_list.add_argument("--merchant-id", default=None)
    merchant_offers_list.add_argument("--vertical", default=None)
    merchant_offers_list.add_argument("--country", default=None)
    merchant_offers_list.add_argument("--period", default=None)
    merchant_offers_list.add_argument("--favourite-type", default=None)
    merchant_offers_list.add_argument("--a-id", default=None)
    merchant_offers_list.set_defaults(func=merchant_cmd.cmd_offers_list, write_capable=False)

    reporting = sub.add_parser("reporting", help="Reporting API")
    reporting_sub = reporting.add_subparsers(
        dest="reporting_cmd", required=True, parser_class=_ToolArgumentParser
    )

    commissions = reporting_sub.add_parser("commissions", help="Commission report")
    commissions_sub = commissions.add_subparsers(
        dest="commissions_cmd", required=True, parser_class=_ToolArgumentParser
    )
    commissions_search = commissions_sub.add_parser("search", help="Search commissions")
    _add_publisher_id(commissions_search)
    _add_date_range(commissions_search, required=False)
    _add_pagination(commissions_search)
    _add_sort(commissions_search)
    commissions_search.add_argument("--updated-since", default=None)
    commissions_search.add_argument("--custom-id", default=None)
    commissions_search.add_argument("--merchant-id", default=None)
    commissions_search.add_argument("--a-id", default=None)
    commissions_search.add_argument("--domain-id", default=None)
    commissions_search.add_argument("--commission-id", default=None)
    commissions_search.add_argument("--status", default=None)
    commissions_search.add_argument("--commission-type", default=None)
    commissions_search.set_defaults(func=reporting_cmd.cmd_commissions_search, write_capable=False)

    aggregated = reporting_sub.add_parser("aggregated", help="Aggregated performance report")
    aggregated_sub = aggregated.add_subparsers(
        dest="aggregated_cmd", required=True, parser_class=_ToolArgumentParser
    )
    aggregated_get = aggregated_sub.add_parser("get", help="Get aggregated report")
    _add_publisher_id(aggregated_get)
    _add_date_range(aggregated_get, required=True)
    _add_pagination(aggregated_get)
    _add_sort(aggregated_get)
    aggregated_get.add_argument("--report-by", required=True)
    aggregated_get.add_argument("--time-period", default=None)
    aggregated_get.add_argument("--currency", default=None)
    aggregated_get.add_argument("--user-country", default=None)
    aggregated_get.add_argument("--user-ip-countries", default=None)
    aggregated_get.add_argument("--device-type", default=None)
    aggregated_get.add_argument("--a-id", default=None)
    aggregated_get.add_argument("--domain-id", default=None)
    aggregated_get.add_argument("--page-search", default=None)
    aggregated_get.add_argument("--link-search", default=None)
    aggregated_get.add_argument("--merchant-search", default=None)
    aggregated_get.set_defaults(func=reporting_cmd.cmd_aggregated_get, write_capable=False)

    link_report = reporting_sub.add_parser("link-report", help="Multi-aggregated link report")
    link_report_sub = link_report.add_subparsers(
        dest="link_report_cmd", required=True, parser_class=_ToolArgumentParser
    )
    link_report_query = link_report_sub.add_parser("query", help="Query link report")
    _add_publisher_id(link_report_query)
    _add_date_range(link_report_query, required=True)
    _add_pagination(link_report_query)
    link_report_query.add_argument("--dim", action="append", required=True)
    link_report_query.add_argument("--met", action="append", required=True)
    link_report_query.add_argument("--currency", default=None)
    link_report_query.set_defaults(func=reporting_cmd.cmd_link_report_query, write_capable=False)
    link_report_dimensions = link_report_sub.add_parser("dimensions", help="List link dimensions")
    _add_publisher_id(link_report_dimensions)
    link_report_dimensions.set_defaults(
        func=reporting_cmd.cmd_link_report_dimensions, write_capable=False
    )
    link_report_metrics = link_report_sub.add_parser("metrics", help="List link metrics")
    _add_publisher_id(link_report_metrics)
    link_report_metrics.set_defaults(func=reporting_cmd.cmd_link_report_metrics, write_capable=False)

    page_report = reporting_sub.add_parser("page-report", help="Multi-aggregated page report")
    page_report_sub = page_report.add_subparsers(
        dest="page_report_cmd", required=True, parser_class=_ToolArgumentParser
    )
    page_report_query = page_report_sub.add_parser("query", help="Query page report")
    _add_publisher_id(page_report_query)
    _add_date_range(page_report_query, required=True)
    _add_pagination(page_report_query)
    page_report_query.add_argument("--dim", action="append", required=True)
    page_report_query.add_argument("--met", action="append", required=True)
    page_report_query.add_argument("--currency", default=None)
    page_report_query.set_defaults(func=reporting_cmd.cmd_page_report_query, write_capable=False)
    page_report_dimensions = page_report_sub.add_parser("dimensions", help="List page dimensions")
    _add_publisher_id(page_report_dimensions)
    page_report_dimensions.set_defaults(
        func=reporting_cmd.cmd_page_report_dimensions, write_capable=False
    )
    page_report_metrics = page_report_sub.add_parser("metrics", help="List page metrics")
    _add_publisher_id(page_report_metrics)
    page_report_metrics.set_defaults(func=reporting_cmd.cmd_page_report_metrics, write_capable=False)

    trending_products = reporting_sub.add_parser("trending-products", help="Trending products")
    trending_products_sub = trending_products.add_subparsers(
        dest="trending_products_cmd", required=True, parser_class=_ToolArgumentParser
    )
    trending_products_get = trending_products_sub.add_parser("get", help="Get trending products")
    _add_publisher_id(trending_products_get)
    _add_pagination(trending_products_get)
    _add_sort(trending_products_get)
    trending_products_get.add_argument("--period", required=True)
    trending_products_get.add_argument("--a-id", default=None)
    trending_products_get.add_argument("--country-code", default=None)
    trending_products_get.add_argument("--audience-country-code", default=None)
    trending_products_get.add_argument("--vertical-id", default=None)
    trending_products_get.add_argument("--product-search", default=None)
    trending_products_get.set_defaults(
        func=reporting_cmd.cmd_trending_products_get, write_capable=False
    )

    product_report = reporting_sub.add_parser("product-report", help="Product bought report")
    product_report_sub = product_report.add_subparsers(
        dest="product_report_cmd", required=True, parser_class=_ToolArgumentParser
    )
    product_report_get = product_report_sub.add_parser("get", help="Get product bought report")
    _add_publisher_id(product_report_get)
    _add_date_range(product_report_get, required=True)
    _add_pagination(product_report_get)
    _add_sort(product_report_get)
    product_report_get.add_argument("--currency", default=None)
    product_report_get.add_argument("--product-search", default=None)
    product_report_get.add_argument("--domain-id", default=None)
    product_report_get.set_defaults(func=reporting_cmd.cmd_product_report_get, write_capable=False)

    payment_status = reporting_sub.add_parser("payment-status", help="Payment status report")
    payment_status_sub = payment_status.add_subparsers(
        dest="payment_status_cmd", required=True, parser_class=_ToolArgumentParser
    )
    payment_status_get = payment_status_sub.add_parser("get", help="Get payment status")
    _add_publisher_id(payment_status_get)
    _add_date_range(payment_status_get, required=True)
    _add_pagination(payment_status_get)
    _add_sort(payment_status_get)
    payment_status_get.add_argument("--invoice-id", default=None)
    payment_status_get.add_argument("--payment-status", default=None)
    payment_status_get.add_argument("--payment-type", default=None)
    payment_status_get.add_argument("--saas-fee", default=None)
    payment_status_get.set_defaults(func=reporting_cmd.cmd_payment_status_get, write_capable=False)

    deactivated = reporting_sub.add_parser("deactivated-merchants", help="Deactivated merchants")
    deactivated_sub = deactivated.add_subparsers(
        dest="deactivated_cmd", required=True, parser_class=_ToolArgumentParser
    )
    deactivated_get = deactivated_sub.add_parser("get", help="Get deactivated merchants")
    _add_publisher_id(deactivated_get)
    _add_pagination(deactivated_get)
    _add_sort(deactivated_get)
    deactivated_get.set_defaults(
        sort_by="publisher_combined_commission_amount",
        sort_dir="DESC",
        limit=30,
        offset=0,
    )
    deactivated_get.add_argument(
        "--min-publisher-combined-commission-amount", type=float, default=0.01
    )
    deactivated_get.add_argument("--domain-id", default=None)
    deactivated_get.add_argument("--currency", default=None)
    deactivated_get.add_argument("--timezone", default=None)
    deactivated_get.set_defaults(
        func=reporting_cmd.cmd_deactivated_merchants_get, write_capable=False
    )

    product_key = sub.add_parser("product-key", help="Product Key API")
    product_key_sub = product_key.add_subparsers(
        dest="product_key_cmd", required=True, parser_class=_ToolArgumentParser
    )
    product = product_key_sub.add_parser("product", help="Single product lookup")
    product_sub = product.add_subparsers(
        dest="product_cmd", required=True, parser_class=_ToolArgumentParser
    )
    product_get = product_sub.add_parser("get", help="Get product details and alternatives")
    _add_publisher_id(product_get)
    _add_publisher_domain_id(product_get)
    product_get.add_argument("--product-url", default=None)
    product_get.add_argument("--product-keywords", default=None)
    product_get.add_argument("--upc", default=None)
    product_get.add_argument("--product-id", default=None)
    product_get.add_argument("--product-id-type", default=None)
    product_get.add_argument("--alternative-country-code", default=None)
    product_get.add_argument("--country-code", default=None)
    product_get.add_argument("--merchant-type", default=None)
    product_get.add_argument("--domains", default=None)
    product_get.add_argument("--exclude-domains", default=None)
    product_get.add_argument("--referrer-url", default=None)
    product_get.add_argument("--per-merchant-limit", type=int, default=None)
    product_get.add_argument("--alternatives-size", type=int, default=None)
    product_get.add_argument(
        "--sort-desc",
        choices=("asc", "desc"),
        default=None,
        help="Official Product Key sort_desc value for alternatives",
    )
    product_get.add_argument("--sort-by", default=None)
    product_get.set_defaults(func=product_key_cmd.cmd_product_get, write_capable=False)

    products = product_key_sub.add_parser("products", help="Multi-product lookup")
    products_sub = products.add_subparsers(
        dest="products_cmd", required=True, parser_class=_ToolArgumentParser
    )
    products_get = products_sub.add_parser("get", help="Get multiple products")
    _add_publisher_id(products_get)
    _add_publisher_domain_id(products_get)
    products_get.add_argument("--product-url", action="append", default=None)
    products_get.add_argument("--product-id", action="append", default=None)
    products_get.add_argument("--product-id-type", default=None)
    products_get.add_argument("--alternative-country-code", default=None)
    products_get.add_argument("--country-code", default=None)
    products_get.add_argument("--merchant-type", default=None)
    products_get.add_argument("--domains", default=None)
    products_get.add_argument("--exclude-domains", default=None)
    products_get.add_argument("--referrer-url", default=None)
    products_get.add_argument("--per-merchant-limit", type=int, default=None)
    products_get.add_argument("--alternatives-size", type=int, default=None)
    products_get.add_argument(
        "--sort-desc",
        choices=("asc", "desc"),
        default=None,
        help="Official Product Key sort_desc value for alternatives",
    )
    products_get.add_argument("--sort-by", default=None)
    products_get.set_defaults(func=product_key_cmd.cmd_products_get, write_capable=False)

    link_wrapper = sub.add_parser("link-wrapper", help="Link Wrapper")
    link_wrapper_sub = link_wrapper.add_subparsers(
        dest="link_wrapper_cmd", required=True, parser_class=_ToolArgumentParser
    )
    link_wrapper_build = link_wrapper_sub.add_parser("build", help="Build a Link Wrapper URL")
    link_wrapper_build.add_argument("--id", default=None, help="Domain-specific Link Wrapper ID")
    link_wrapper_build.add_argument("--url", required=True, help="Destination URL to wrap")
    link_wrapper_build.add_argument("--xcust", default=None, help="Optional custom tracking value")
    link_wrapper_build.add_argument("--sref", default=None, help="Optional referring page URL")
    link_wrapper_build.set_defaults(func=link_wrapper_cmd.cmd_build, write_capable=False)

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
            payload = {"ok": True, "tool": "skimlinks-safe-cli", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"skimlinks-safe-cli {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        command_str = "skimlinks-safe-cli " + " ".join(argv)
        audit.bind_context(
            {
                "tool": "skimlinks-safe-cli",
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
                "tool": "skimlinks-safe-cli",
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
                "ack_irreversible": bool(args.ack_irreversible),
                "run_id": run_ctx.run_id,
                "artifacts_dir": run_ctx.artifacts_dir,
                "runs_index_path": runs_index_path,
            }
            rc = int(args.func(args, ctx))
            return rc

        cfg = load_config(args.env_file)
        env_fingerprint = cfg.env_fingerprint
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "tool": "skimlinks-safe-cli",
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
                "tool": "skimlinks-safe-cli",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "env_fingerprint": cfg.env_fingerprint,
                "run_id": run_ctx.run_id,
            }
        )
        rc = int(args.func(args, ctx))

        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="skimlinks-safe-cli",
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
            tool="skimlinks-safe-cli",
            version=__version__,
            command="skimlinks-safe-cli " + " ".join(argv),
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
            tool="skimlinks-safe-cli",
            version=__version__,
            command="skimlinks-safe-cli " + " ".join(argv),
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
            tool="skimlinks-safe-cli",
            version=__version__,
            command="skimlinks-safe-cli " + " ".join(argv),
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
