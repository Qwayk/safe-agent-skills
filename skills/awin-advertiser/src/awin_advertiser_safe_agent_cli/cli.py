from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import auth as auth_cmd
from .commands import conversion as conversion_cmd
from .commands import offers as offers_cmd
from .commands import publishers as publishers_cmd
from .commands import onboarding as onboarding_cmd
from .commands import product_feeds as product_feeds_cmd
from .commands import transactions as transactions_cmd
from .config import load_config
from .errors import ToolError, ValidationError
from .http import HttpClient
from .http import redact_sensitive_text
from .output import Output
from .runs import (
    RunContext,
    build_deterministic_summary,
    append_index_row,
    find_run,
    init_run_context,
    list_runs,
    runs_index_path_for_env_file,
    write_summary_md,
)

_TOOL = "awin-advertiser-safe-cli"


class _ToolArgumentParser(argparse.ArgumentParser):
    """
    Keep parser errors as clean JSON while preserving local CLI contract.
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


def _output_mode_from_argv(argv: list[str]) -> str:
    try:
        idx = argv.index("--output")
    except ValueError:
        return "json"
    if idx + 1 >= len(argv):
        return "json"
    v = str(argv[idx + 1] or "").strip()
    return v if v in {"json", "text"} else "json"


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
    plan_path: str | None,
    receipt_path: str | None,
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


def _user_agent(version: str) -> str:
    return f"{_TOOL}/{version}"


def _safe_error_text(error: Exception, *, cfg=None) -> str:
    secrets: set[str] = set()
    token = getattr(cfg, "token", None)
    if token:
        secrets.add(str(token))
    return redact_sensitive_text(str(error), secrets=secrets or None)


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
    p.add_argument("--yes", action="store_true", help="Required with --apply for risky actions")
    p.add_argument("--plan-out", default=None, help="Optional path to write a dry-run plan JSON")
    p.add_argument("--plan-in", default=None, help="Optional plan JSON to validate before apply")
    p.add_argument("--receipt-out", default=None, help="Optional path to write an apply receipt JSON")
    p.add_argument(
        "--ack-irreversible",
        action="store_true",
        help="Required with --apply --yes for irreversible write actions",
    )
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
    onboarding.add_argument("--no-write-env", action="store_true", help="Do not write/update the env file")
    onboarding.set_defaults(func=onboarding_cmd.cmd_onboarding, write_capable=False)

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Validate credentials against advertiser publishers endpoint")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=False)

    publishers = sub.add_parser("publishers", help="Advertiser publisher reads")
    publishers_sub = publishers.add_subparsers(dest="publishers_cmd", required=True, parser_class=_ToolArgumentParser)
    publishers_list = publishers_sub.add_parser("list", help="List publishers for an advertiser")
    publishers_list.add_argument("--advertiser-id", required=True, help="Advertiser id to query")
    publishers_list.set_defaults(func=publishers_cmd.cmd_publishers_list, write_capable=False)

    transactions = sub.add_parser("transactions", help="Advertiser transaction reads")
    transactions_sub = transactions.add_subparsers(dest="transactions_cmd", required=True, parser_class=_ToolArgumentParser)

    transactions_list = transactions_sub.add_parser("list", help="List advertiser transactions")
    transactions_list.add_argument("--advertiser-id", required=True, help="Advertiser id to query")
    transactions_list.add_argument("--start-date", required=True, help="Filter start date (ISO8601)")
    transactions_list.add_argument("--end-date", required=True, help="Filter end date (ISO8601)")
    transactions_list.add_argument(
        "--date-type",
        default=None,
        choices=("transaction", "validation", "amendment"),
        help="Optional date type filter",
    )
    transactions_list.add_argument(
        "--publisher-id",
        action="append",
        help="Optional publisher id filter (repeatable)",
    )
    transactions_list.add_argument(
        "--status",
        default=None,
        choices=("pending", "approved", "declined", "deleted"),
        help="Optional status filter",
    )
    transactions_list.add_argument("--timezone", default=None, help="Optional timezone value")
    transactions_list.add_argument("--show-basket-products", action="store_true", help="Include basket-product fields")
    transactions_list.set_defaults(func=transactions_cmd.cmd_transactions_list, write_capable=False)

    transactions_by_ids = transactions_sub.add_parser("by-ids", help="Fetch advertiser transactions by ids")
    transactions_by_ids.add_argument("--advertiser-id", required=True, help="Advertiser id to query")
    transactions_by_ids.add_argument("--ids", required=True, help="Comma-separated transaction ids")
    transactions_by_ids.add_argument("--timezone", default=None, help="Optional timezone value")
    transactions_by_ids.add_argument(
        "--show-basket-products",
        action="store_true",
        help="Include basket-product fields",
    )
    transactions_by_ids.set_defaults(func=transactions_cmd.cmd_transactions_by_ids, write_capable=False)

    transactions_batch = transactions_sub.add_parser("batch", help="Advertiser transaction batch operations")
    transactions_batch_sub = transactions_batch.add_subparsers(
        dest="batch_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    transactions_batch_validate = transactions_batch_sub.add_parser("validate", help="Validate and apply advertiser transaction actions")
    transactions_batch_validate.add_argument("--advertiser-id", required=True, help="Advertiser id for batch endpoint")
    transactions_batch_validate.add_argument("--batch-file", required=True, help="JSON file containing batch action array")
    transactions_batch_validate.add_argument("--apply", action="store_true", help="Apply remote change (default is dry-run plan)")
    transactions_batch_validate.add_argument("--yes", action="store_true", help="Required with --apply for risky actions")
    transactions_batch_validate.add_argument("--plan-out", default=None, help="Optional path to write a dry-run plan JSON")
    transactions_batch_validate.add_argument("--plan-in", default=None, help="Optional plan JSON to validate before apply")
    transactions_batch_validate.add_argument("--receipt-out", default=None, help="Optional path to write apply receipt JSON")
    transactions_batch_validate.add_argument(
        "--ack-irreversible",
        action="store_true",
        help="Required with --apply --yes for irreversible write actions",
    )
    transactions_batch_validate.set_defaults(func=transactions_cmd.cmd_transactions_batch_validate, write_capable=True)

    transactions_jobs_list = transactions_sub.add_parser("jobs", help="Advertiser transaction job reads")
    transactions_jobs_sub = transactions_jobs_list.add_subparsers(dest="jobs_cmd", required=True, parser_class=_ToolArgumentParser)

    transactions_jobs_list_cmd = transactions_jobs_sub.add_parser("list", help="List transaction jobs")
    transactions_jobs_list_cmd.add_argument("--advertiser-id", required=True, help="Advertiser id to query")
    transactions_jobs_list_cmd.set_defaults(func=transactions_cmd.cmd_transactions_jobs_list, write_capable=False)

    transactions_jobs_show_cmd = transactions_jobs_sub.add_parser("show", help="Show one transaction job")
    transactions_jobs_show_cmd.add_argument("--advertiser-id", required=True, help="Advertiser id to query")
    transactions_jobs_show_cmd.add_argument("--job-id", required=True, help="Transaction job id to query")
    transactions_jobs_show_cmd.add_argument(
        "--job-output",
        default=None,
        choices=("errors", "all"),
        help="Optional job output filter",
    )
    transactions_jobs_show_cmd.set_defaults(func=transactions_cmd.cmd_transactions_jobs_show, write_capable=False)

    reports = sub.add_parser("reports", help="Advertiser report reads")
    reports_sub = reports.add_subparsers(dest="reports_cmd", required=True, parser_class=_ToolArgumentParser)

    reports_publisher = reports_sub.add_parser("publisher", help="Advertiser publisher report")
    reports_publisher.add_argument("--advertiser-id", required=True, help="Advertiser id to query")
    reports_publisher.add_argument("--start-date", required=True, help="Report start date (YYYY-MM-DD or ISO8601)")
    reports_publisher.add_argument("--end-date", required=True, help="Report end date (YYYY-MM-DD or ISO8601)")
    reports_publisher.add_argument(
        "--date-type",
        default=None,
        choices=("transaction", "validation"),
        help="Optional date type filter",
    )
    reports_publisher.add_argument("--timezone", default=None, help="Optional timezone value")
    reports_publisher.set_defaults(func=transactions_cmd.cmd_reports_publisher, write_capable=False)

    reports_campaign = reports_sub.add_parser("campaign", help="Advertiser campaign report")
    reports_campaign.add_argument("--advertiser-id", required=True, help="Advertiser id to query")
    reports_campaign.add_argument("--start-date", required=True, help="Report start date (YYYY-MM-DD or ISO8601)")
    reports_campaign.add_argument("--end-date", required=True, help="Report end date (YYYY-MM-DD or ISO8601)")
    reports_campaign.add_argument("--campaign", default=None, help="Optional campaign filter")
    reports_campaign.add_argument(
        "--publisher-id",
        action="append",
        help="Optional publisher id filter (repeatable)",
    )
    reports_campaign.add_argument(
        "--include-numbers-without-campaign",
        action="store_true",
        help="Include campaign-less numbers",
    )
    reports_campaign.add_argument(
        "--interval",
        default=None,
        choices=("day", "month", "year"),
        help="Optional interval",
    )
    reports_campaign.add_argument("--timezone", default=None, help="Optional timezone value")
    reports_campaign.set_defaults(func=transactions_cmd.cmd_reports_campaign, write_capable=False)

    conversion = sub.add_parser("conversion", help="Advertiser conversion writes")
    conversion_sub = conversion.add_subparsers(dest="conversion_cmd", required=True, parser_class=_ToolArgumentParser)

    conversion_orders = conversion_sub.add_parser("orders", help="Advertiser conversion order operations")
    conversion_orders_sub = conversion_orders.add_subparsers(dest="conversion_orders_cmd", required=True, parser_class=_ToolArgumentParser)
    conversion_orders_create = conversion_orders_sub.add_parser("create", help="Create advertiser conversion orders")
    conversion_orders_create.add_argument("--advertiser-id", required=True, help="Advertiser id for conversion endpoint")
    conversion_orders_create.add_argument(
        "--orders-file",
        required=True,
        help="JSON file containing conversion orders",
    )
    conversion_orders_create.add_argument("--webhook-url", default=None, help="Optional webhook URL for completion events")
    conversion_orders_create.add_argument("--apply", action="store_true", help="Apply remote change (default is dry-run plan)")
    conversion_orders_create.add_argument("--yes", action="store_true", help="Required with --apply for risky actions")
    conversion_orders_create.add_argument("--plan-out", default=None, help="Optional path to write a dry-run plan JSON")
    conversion_orders_create.add_argument("--plan-in", default=None, help="Optional path to validate against before apply")
    conversion_orders_create.add_argument("--receipt-out", default=None, help="Optional path to write apply receipt JSON")
    conversion_orders_create.add_argument(
        "--ack-irreversible",
        action="store_true",
        help="Required with --apply --yes for irreversible write actions",
    )
    conversion_orders_create.set_defaults(func=conversion_cmd.cmd_conversion_orders_create, write_capable=True)

    offers = sub.add_parser("offers", help="Advertiser offer writes")
    offers_sub = offers.add_subparsers(dest="offers_cmd", required=True, parser_class=_ToolArgumentParser)
    offers_create = offers_sub.add_parser("create", help="Create one advertiser offer")
    offers_create.add_argument("--advertiser-id", required=True, help="Advertiser id for offer endpoint")
    offers_create.add_argument("--offer-file", required=True, help="JSON file containing one offer object")
    offers_create.add_argument("--apply", action="store_true", help="Apply remote change (default is dry-run plan)")
    offers_create.add_argument("--yes", action="store_true", help="Required with --apply for risky actions")
    offers_create.add_argument("--plan-out", default=None, help="Optional path to write a dry-run plan JSON")
    offers_create.add_argument("--plan-in", default=None, help="Optional plan JSON to validate before apply")
    offers_create.add_argument("--receipt-out", default=None, help="Optional path to write apply receipt JSON")
    offers_create.add_argument(
        "--ack-irreversible",
        action="store_true",
        help="Required with --apply --yes for irreversible write actions",
    )
    offers_create.set_defaults(func=offers_cmd.cmd_offers_create, write_capable=True)

    product_feeds = sub.add_parser("product-feeds", help="Advertiser product feed writes")
    product_feeds_sub = product_feeds.add_subparsers(
        dest="product_feeds_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    product_feeds_upload = product_feeds_sub.add_parser("upload", help="Upload advertiser product feed JSONL")
    product_feeds_upload.add_argument("--advertiser-id", required=True, help="Advertiser id for product feeds")
    product_feeds_upload.add_argument("--vertical", required=True, choices=("retail",), help="Feed vertical")
    product_feeds_upload.add_argument("--locale", required=True, help="Feed locale token, e.g. en_GB")
    product_feeds_upload.add_argument("--feed-file", required=True, help="UTF-8 JSONL file path")
    product_feeds_upload.add_argument("--apply", action="store_true", help="Apply remote change (default is dry-run plan)")
    product_feeds_upload.add_argument("--yes", action="store_true", help="Required with --apply for risky actions")
    product_feeds_upload.add_argument("--plan-out", default=None, help="Optional path to write a dry-run plan JSON")
    product_feeds_upload.add_argument("--plan-in", default=None, help="Optional plan JSON to validate before apply")
    product_feeds_upload.add_argument("--receipt-out", default=None, help="Optional path to write apply receipt JSON")
    product_feeds_upload.add_argument(
        "--ack-irreversible",
        action="store_true",
        help="Required with --apply --yes for irreversible write actions",
    )
    product_feeds_upload.set_defaults(func=product_feeds_cmd.cmd_product_feeds_upload, write_capable=True)

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
        out.emit({"ok": False, "error": "Missing command. Use --help to see available commands.", "error_type": "ValidationError"})
        return 1

    command_str = f"{_TOOL} {' '.join(argv)}"
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

    audit.bind_context(
        {
            "tool": _TOOL,
            "version": __version__,
            "command": command_str,
            "apply": False,
            "yes": False,
            "env_fingerprint": None,
            "run_id": run_ctx.run_id,
        }
    )

    try:
        if str(getattr(args, "cmd", "") or "") in {"runs", "onboarding"}:
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
            }
            rc = int(args.func(args, ctx))
            return rc

        cfg = load_config(args.env_file)
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        http = HttpClient(timeout_s=timeout_s, verbose=bool(args.verbose), user_agent=_user_agent(__version__))
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "tool": _TOOL,
            "tool_version": __version__,
            "command_str": command_str,
            "env_file": str(args.env_file),
            "timeout_s": timeout_s,
            "verbose": bool(args.verbose),
            "apply": bool(args.apply),
            "yes": bool(args.yes),
            "plan_out": str(args.plan_out).strip() if getattr(args, "plan_out", None) else None,
            "plan_in": str(args.plan_in).strip() if getattr(args, "plan_in", None) else None,
            "receipt_out": str(args.receipt_out).strip() if getattr(args, "receipt_out", None) else None,
            "ack_irreversible": bool(getattr(args, "ack_irreversible", False)),
            "http_client": http,
            "run_id": run_ctx.run_id,
            "artifacts_dir": run_ctx.artifacts_dir,
            "runs_index_path": run_ctx.runs_index_path,
            "audit_log_path": run_audit_log_path or global_audit_log_path,
            "audit_log_run_path": run_audit_log_path,
            "audit_log_global_path": global_audit_log_path,
        }

        if run_ctx.enabled and run_ctx.artifacts_dir:
            if not ctx.get("plan_out") and not ctx.get("receipt_out"):
                ctx["plan_out"] = str(run_ctx.artifacts_dir / "plan.json")

        audit.bind_context(
            {
                "tool": _TOOL,
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "env_fingerprint": cfg.base_url,
                "run_id": run_ctx.run_id,
            }
        )

        rc = int(args.func(args, ctx))
        output_obj = out.last if isinstance(out.last, dict) else None
        output_plan = output_obj.get("plan_out") if isinstance(output_obj, dict) else None
        output_receipt = output_obj.get("receipt_out") if isinstance(output_obj, dict) else None

        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool=_TOOL,
            version=__version__,
            command=command_str,
            env_fingerprint=cfg.base_url,
            output_obj=output_obj,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
            plan_path=str(output_plan) if isinstance(output_plan, str) else None,
            receipt_path=str(output_receipt) if isinstance(output_receipt, str) else None,
        )
        return rc

    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    except ToolError as e:
        safe_error = _safe_error_text(e, cfg=locals().get("cfg"))
        audit.write("error", {"error": safe_error, "error_type": type(e).__name__})
        out.emit({"ok": False, "error": safe_error, "error_type": type(e).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool=_TOOL,
            version=__version__,
            command=f"{_TOOL} {' '.join(argv)}",
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(getattr(args, "apply", False)),
            yes=bool(getattr(args, "yes", False)),
            plan_path=None,
            receipt_path=None,
        )
        return 1
    except ValidationError as e:
        # Preserve this as a JSON no-secret setup failure and avoid raising generic stack traces.
        safe_error = _safe_error_text(e, cfg=locals().get("cfg"))
        out.emit({"ok": False, "error": safe_error, "error_type": type(e).__name__, "blocked": False})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool=_TOOL,
            version=__version__,
            command=f"{_TOOL} {' '.join(argv)}",
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(getattr(args, "apply", False)),
            yes=bool(getattr(args, "yes", False)),
            plan_path=None,
            receipt_path=None,
        )
        return 1
    except Exception as e:  # noqa: BLE001
        if bool(args.debug):
            raise
        safe_error = _safe_error_text(e, cfg=locals().get("cfg"))
        audit.write("error", {"error": safe_error, "error_type": type(e).__name__})
        out.emit({"ok": False, "error": safe_error, "error_type": type(e).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool=_TOOL,
            version=__version__,
            command=f"{_TOOL} {' '.join(argv)}",
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(getattr(args, "apply", False)),
            yes=bool(getattr(args, "yes", False)),
            plan_path=None,
            receipt_path=None,
        )
        return 1
    finally:
        audit.close()
