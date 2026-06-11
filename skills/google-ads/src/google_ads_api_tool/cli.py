from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import auth as auth_cmd
from .commands import builders as builders_cmd
from .commands import customers as customers_cmd
from .commands import fields as fields_cmd
from .commands import gaql as gaql_cmd
from .commands import helpers as helpers_cmd
from .commands import onboarding as onboarding_cmd
from .commands import presets as presets_cmd
from .commands import snapshot as snapshot_cmd
from .config import load_config
from .errors import SafetyError, ToolError, ValidationError
from .output import Output
from .project_config import load_project_config
from .rpc_commands import register_v22_rpc_commands
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
from .secrets import redact_secrets


class _ToolArgumentParser(argparse.ArgumentParser):
    """
    Ensure user-input errors can be surfaced as JSON.

    Argparse defaults to printing usage/help to stderr and raising SystemExit, which makes it
    hard to keep the `--output json` contract (exactly one JSON object to stdout on errors).
    """

    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def _cmd_runs_list(args: argparse.Namespace, ctx: dict) -> int:
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
            p = Path(ad) / "summary.md"
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
    p = _ToolArgumentParser(prog="google-ads-api-tool")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--config", default=None, help="Optional project defaults JSON (non-secret)")
    p.add_argument("--project-dir", default=None, help="Optional project directory (defaults to config file folder)")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--verbose", action="store_true", help="Verbose logging to stderr")
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
    p.add_argument("--ack-irreversible", action="store_true", help="Extra acknowledgement for irreversible actions")
    p.add_argument(
        "--ack-spend",
        action="store_true",
        help="Extra acknowledgement for budget/billing/spend-impacting writes",
    )
    p.add_argument(
        "--include-rpc-payload",
        action="store_true",
        help="Include raw RPC request/response payloads in plan/receipt outputs (sensitive; requires --ack-sensitive-payload)",
    )
    p.add_argument(
        "--ack-sensitive-payload",
        action="store_true",
        help="Acknowledge that raw RPC payloads may contain sensitive data (required for --include-rpc-payload)",
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
    onboarding.add_argument("--no-write-env", action="store_true", help="Do not write/update the env file")
    onboarding.set_defaults(func=onboarding_cmd.cmd_onboarding, write_capable=False)

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Smoke test credentials (read-only)")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=False)

    customers = sub.add_parser("customers", help="Customer access helpers")
    customers_sub = customers.add_subparsers(dest="customers_cmd", required=True, parser_class=_ToolArgumentParser)
    customers_list = customers_sub.add_parser("list-accessible", help="List accessible customers (read-only)")
    customers_list.set_defaults(func=customers_cmd.cmd_customers_list_accessible, write_capable=False)

    gaql = sub.add_parser("gaql", help="Run a GAQL query (read-only)")
    gaql.add_argument("--customer-id", required=True, help="Customer id (digits)")
    gaql.add_argument("--query", required=True, help="GAQL query string")
    gaql.add_argument("--limit", type=int, default=None, help="Max rows to return (client-side limit)")
    gaql.add_argument("--page-size", type=int, default=1000, help="API page size (default: 1000)")
    gaql.set_defaults(func=gaql_cmd.cmd_gaql, write_capable=False)

    fields = sub.add_parser("fields", help="Google Ads field discovery helpers")
    fields_sub = fields.add_subparsers(dest="fields_cmd", required=True, parser_class=_ToolArgumentParser)
    fields_search = fields_sub.add_parser("search", help="Search field metadata (read-only)")
    fields_search.add_argument("--query", default=None, help="FieldService query (advanced)")
    fields_search.add_argument("--contains", default=None, help="Convenience: substring match against field name")
    fields_search.add_argument("--limit", type=int, default=50, help="Max results (default: 50)")
    fields_search.set_defaults(func=fields_cmd.cmd_fields_search, write_capable=False)

    builders_cmd.register_builder_commands(sub)
    helpers_cmd.register_helper_commands(sub)

    presets = sub.add_parser("presets", help="GAQL preset packs (no GAQL knowledge required)")
    presets_sub = presets.add_subparsers(dest="presets_cmd", required=True, parser_class=_ToolArgumentParser)
    presets_list = presets_sub.add_parser("list", help="List built-in presets")
    presets_list.set_defaults(func=presets_cmd.cmd_presets_list, write_capable=False)
    presets_show = presets_sub.add_parser("show", help="Show one preset JSON")
    presets_show.add_argument("--preset", required=True, help="Preset name")
    presets_show.set_defaults(func=presets_cmd.cmd_presets_show, write_capable=False)
    presets_validate = presets_sub.add_parser("validate", help="Validate built-in presets")
    presets_validate.add_argument("--preset", required=False, default=None, help="Validate just one preset")
    presets_validate.set_defaults(func=presets_cmd.cmd_presets_validate, write_capable=False)

    snapshot = sub.add_parser("snapshot", help="Export analysis packs (read-only to Google Ads; writes local files)")
    snapshot_sub = snapshot.add_subparsers(dest="snapshot_cmd", required=True, parser_class=_ToolArgumentParser)
    snap_export = snapshot_sub.add_parser("export", help="Export a joinable analysis pack to a local folder")
    snap_export.add_argument("--preset", required=True, help="Preset name (see: presets list)")
    snap_export.add_argument("--customer-id", required=True, help="Customer id (digits)")
    snap_export.add_argument("--since", required=True, help="Start date (YYYY-MM-DD)")
    snap_export.add_argument("--until", required=True, help="End date (YYYY-MM-DD)")
    snap_export.add_argument("--out-dir", required=True, help="Output folder for the pack")
    snap_export.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing out-dir")
    snap_export.add_argument("--max-rows", type=int, default=None, help="Cap rows per query-group output")
    snap_export.add_argument("--page-size", type=int, default=1000, help="API page size (default: 1000)")
    snap_export.add_argument("--segmentation", default="base", help="Preset template variant (bounded by preset)")
    snap_export.add_argument("--strict", action="store_true", help="Fail if any required group fails")
    snap_export.add_argument(
        "--include-optional",
        action="store_true",
        help="Include non-required preset groups (may increase time/quota; errors are recorded as optional)",
    )
    snap_export.set_defaults(func=snapshot_cmd.cmd_snapshot_export, write_capable=True)

    snap_compare = snapshot_sub.add_parser("compare", help="Compare two local packs (descriptive diffs only)")
    snap_compare.add_argument("--pack-a", required=True, help="Pack A folder (must contain manifest.json)")
    snap_compare.add_argument("--pack-b", required=True, help="Pack B folder (must contain manifest.json)")
    snap_compare.add_argument("--out-dir", required=True, help="Output folder for compare_summary.json")
    snap_compare.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing out-dir")
    snap_compare.set_defaults(func=snapshot_cmd.cmd_snapshot_compare, write_capable=True)

    snap_analyze = snapshot_sub.add_parser("analyze", help="Analyze an existing local pack (offline)")
    snap_analyze_sub = snap_analyze.add_subparsers(dest="snapshot_analyze_cmd", required=True, parser_class=_ToolArgumentParser)
    snap_opt = snap_analyze_sub.add_parser("optimize", help="Generate an offline optimization report from a pack")
    snap_opt.add_argument("--pack-dir", required=True, help="Pack folder (must contain manifest.json)")
    snap_opt.add_argument("--top-n", type=int, default=50, help="Max items per recommendation list (default: 50)")
    snap_opt.add_argument(
        "--min-negative-cost-micros",
        type=int,
        default=5000000,
        help="Candidate negatives: minimum total cost_micros (default: 5000000)",
    )
    snap_opt.add_argument(
        "--min-negative-clicks",
        type=int,
        default=3,
        help="Candidate negatives: minimum total clicks (default: 3)",
    )
    snap_opt.add_argument(
        "--min-negative-impressions",
        type=int,
        default=100,
        help="Candidate negatives: minimum total impressions (default: 100)",
    )
    snap_opt.set_defaults(func=snapshot_cmd.cmd_snapshot_analyze_optimize, write_capable=False)
    snap_diag = snap_analyze_sub.add_parser("diagnose", help="Generate a structured offline diagnosis from a pack")
    snap_diag.add_argument("--pack-dir", required=True, help="Pack folder (must contain manifest.json)")
    snap_diag.set_defaults(func=snapshot_cmd.cmd_snapshot_analyze_diagnose, write_capable=False)

    # Explicit per-RPC-method commands (Google Ads API v22).
    register_v22_rpc_commands(sub)

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


def _normalize_global_flags(argv: list[str]) -> list[str]:
    """
    Allow global flags (like --apply/--yes) to appear after subcommands.

    Argparse only recognizes parent-parser flags before the subcommand token. We keep
    the CLI ergonomic by moving known global flags (and their values) to the front.
    """

    flags_no_value = {
        "--version",
        "--verbose",
        "--debug",
        "--apply",
        "--yes",
        "--ack-irreversible",
        "--ack-spend",
        "--include-rpc-payload",
        "--ack-sensitive-payload",
        "--no-artifacts",
    }
    flags_with_value = {
        "--config",
        "--project-dir",
        "--env-file",
        "--timeout-s",
        "--output",
        "--log-file",
        "--plan-out",
        "--plan-in",
        "--receipt-out",
        "--run-id",
        "--artifacts-dir",
    }

    moved: list[str] = []
    rest: list[str] = []
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok in flags_no_value:
            moved.append(tok)
            i += 1
            continue
        if tok in flags_with_value:
            moved.append(tok)
            if i + 1 < len(argv):
                moved.append(argv[i + 1])
                i += 2
            else:
                i += 1
            continue
        rest.append(tok)
        i += 1
    return moved + rest


def main(argv: list[str]) -> int:
    argv = _normalize_global_flags(list(argv or []))
    parser = build_parser()
    out = Output(mode=_output_mode_from_argv(argv))
    secret_values: list[str] = []
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
    audit = (
        CompositeAuditLogger(loggers)
        if len(loggers) > 1
        else (loggers[0] if loggers else AuditLogger(path=None, enabled=False))
    )

    runs_index_path = runs_index_path_for_env_file(str(args.env_file))
    if str(getattr(args, "cmd", "") or "") == "runs":
        run_ctx = RunContext(
            enabled=False,
            run_id=None,
            artifacts_dir=None,
            runs_index_path=runs_index_path,
            audit_log_path=None,
        )

    provenance_runs_index = None
    if run_ctx.runs_index_path:
        provenance_runs_index = str(run_ctx.runs_index_path)
    elif str(getattr(args, "cmd", "") or "") == "runs":
        provenance_runs_index = str(runs_index_path)
    elif not bool(args.no_artifacts):
        provenance_runs_index = str(runs_index_path)

    out.set_provenance(
        {
            "run_id": run_ctx.run_id,
            "artifacts_dir": str(run_ctx.artifacts_dir) if run_ctx.artifacts_dir else None,
            "runs_index": provenance_runs_index,
            "audit_log": run_audit_log_path or global_audit_log_path,
            "audit_log_global": global_audit_log_path,
        }
    )

    try:
        if bool(args.version):
            payload = {"ok": True, "tool": "google-ads-api-tool", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"google-ads-api-tool {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        command_str = "google-ads-api-tool " + " ".join(argv)
        audit.bind_context(
            {
                "tool": "google-ads-api-tool",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "env_fingerprint": None,
                "run_id": run_ctx.run_id,
            }
        )

        # Local-only commands that don't need API config.
        if str(getattr(args, "cmd", "") or "") in {"runs", "onboarding", "presets", "snapshot"}:
            ctx = {
                "cfg": None,
                "out": out,
                "audit": audit,
                "tool": "google-ads-api-tool",
                "tool_version": __version__,
                "command_str": command_str,
                "project_cfg": project_cfg,
                "project_dir": project_dir,
                "env_file": str(args.env_file),
                "timeout_s": float(args.timeout_s) if args.timeout_s is not None else None,
                "verbose": bool(args.verbose),
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "plan_out": args.plan_out,
                "plan_in": args.plan_in,
                "receipt_out": args.receipt_out,
                "ack_irreversible": bool(args.ack_irreversible),
                "ack_spend": bool(args.ack_spend),
                "run_id": run_ctx.run_id,
                "artifacts_dir": run_ctx.artifacts_dir,
                "runs_index_path": runs_index_path,
            }
            rc = int(args.func(args, ctx))
            _finalize_run_artifacts(
                run_ctx=run_ctx,
                tool="google-ads-api-tool",
                version=__version__,
                command=command_str,
                env_fingerprint=None,
                output_obj=out.last if isinstance(out.last, dict) else None,
                audit_log_path=run_audit_log_path or global_audit_log_path,
                audit_log_global_path=global_audit_log_path,
                apply=bool(args.apply),
                yes=bool(args.yes),
            )
            return rc

        cfg = load_config(args.env_file)
        secret_values = cfg.secret_values()
        env_fingerprint = cfg.login_customer_id or "google-ads"
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "tool": "google-ads-api-tool",
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
            "ack_spend": bool(args.ack_spend),
            "include_rpc_payload": bool(args.include_rpc_payload),
            "ack_sensitive_payload": bool(args.ack_sensitive_payload),
            "run_id": run_ctx.run_id,
            "artifacts_dir": run_ctx.artifacts_dir,
            "runs_index_path": run_ctx.runs_index_path,
            "audit_log_path": run_audit_log_path or global_audit_log_path,
            "audit_log_run_path": run_audit_log_path,
            "audit_log_global_path": global_audit_log_path,
        }

        audit.bind_context(
            {
                "tool": "google-ads-api-tool",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "env_fingerprint": env_fingerprint,
                "run_id": run_ctx.run_id,
            }
        )
        rc = int(args.func(args, ctx))

        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="google-ads-api-tool",
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
        msg = redact_secrets(str(e), secret_values)
        audit.write("refused", {"reason": msg})
        out.emit({"ok": True, "refused": True, "reasons": [msg], "refusal_type": "SafetyError"})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="google-ads-api-tool",
            version=__version__,
            command="google-ads-api-tool " + " ".join(argv),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 0
    except ToolError as e:
        msg = redact_secrets(str(e), secret_values)
        audit.write("error", {"error": msg, "error_type": type(e).__name__})
        out.emit({"ok": False, "error": msg, "error_type": type(e).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="google-ads-api-tool",
            version=__version__,
            command="google-ads-api-tool " + " ".join(argv),
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
        msg = redact_secrets(str(e), secret_values)
        audit.write("error", {"error": msg, "error_type": type(e).__name__})
        out.emit({"ok": False, "error": msg, "error_type": type(e).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="google-ads-api-tool",
            version=__version__,
            command="google-ads-api-tool " + " ".join(argv),
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
