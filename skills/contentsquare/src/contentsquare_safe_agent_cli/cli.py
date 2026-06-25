from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .catalog import ALL_ENDPOINTS, EndpointSpec
from .commands import auth as auth_cmd
from .commands import contentsquare as contentsquare_cmd
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


def _add_common_query_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project-id", default=None, help="Contentsquare project id when the endpoint needs one")
    parser.add_argument("--start-date", default=None, help="Start date, usually YYYY-MM-DD")
    parser.add_argument("--end-date", default=None, help="End date, usually YYYY-MM-DD")
    parser.add_argument("--segment-id", default=None, help="Segment id when supported by the endpoint")
    parser.add_argument("--segment-ids", default=None, help="Comma-separated segment ids when supported by the endpoint")
    parser.add_argument("--goal-id", default=None, help="Goal id when supported by the endpoint")
    parser.add_argument("--ids", default=None, help="Comma-separated object ids when supported by the endpoint")
    parser.add_argument("--state", default=None, help="State/status filter when supported by the endpoint")
    parser.add_argument("--order", default=None, help="Result order when supported by the endpoint")
    parser.add_argument("--format", default=None, help="Data Export format filter when supported by the endpoint")
    parser.add_argument("--frequency", default=None, help="Data Export frequency filter when supported by the endpoint")
    parser.add_argument("--scope-filter", default=None, help="Data Export scope filter when supported by the endpoint")
    parser.add_argument("--from", dest="from_date", default=None, help="Start date filter when the endpoint uses from")
    parser.add_argument("--to", dest="to_date", default=None, help="End date filter when the endpoint uses to")
    parser.add_argument("--page", type=int, default=None, help="Page number when supported by the endpoint")
    parser.add_argument("--limit", type=int, default=None, help="Result limit when supported by the endpoint")
    parser.add_argument("--device", default=None, help="Device filter when supported by the endpoint")
    parser.add_argument("--period", default=None, help="Granularity when supported by the endpoint")
    parser.add_argument("--scope", default=None, help="Optional OAuth scope override")


def _add_path_args(parser: argparse.ArgumentParser, spec: EndpointSpec) -> None:
    if "{jobId}" in spec.path:
        parser.add_argument("--job-id", required=True, help="Export job id")
    if "{runId}" in spec.path:
        parser.add_argument("--run-id-value", required=True, help="Export run id")
    if "{mappingId}" in spec.path:
        parser.add_argument("--mapping-id", required=True, help="Mapping id")
    if "{pageGroupId}" in spec.path:
        parser.add_argument("--page-group-id", required=True, help="Page group id")
    if "{zoningId}" in spec.path:
        parser.add_argument("--zoning-id", required=True, help="Zoning id")
    if "{zoneId}" in spec.path:
        parser.add_argument("--zone-id", required=True, help="Zone id")


def _register_endpoint_command(parser: argparse.ArgumentParser, spec: EndpointSpec) -> None:
    _add_path_args(parser, spec)
    _add_common_query_args(parser)
    if spec.method == "POST":
        parser.add_argument("--body-json", default=None, help="JSON body file for this named Contentsquare operation")
    if spec.family == "enrichment":
        parser.add_argument("--integration-id", required=True, help="Contentsquare enrichment integration id")
    parser.set_defaults(func=contentsquare_cmd.cmd_endpoint, write_capable=spec.safety.startswith("plan_apply"), endpoint_spec=spec)


def _add_contentsquare_commands(sub: argparse._SubParsersAction) -> None:
    families: dict[str, argparse._SubParsersAction] = {}
    nested: dict[tuple[str, ...], argparse._SubParsersAction] = {}
    for family in ("data-export", "metrics", "enrichment", "speed-analysis"):
        family_parser = sub.add_parser(family, help=f"Contentsquare {family} operations")
        families[family] = family_parser.add_subparsers(dest=f"{family.replace('-', '_')}_cmd", required=True, parser_class=_ToolArgumentParser)
        nested[(family,)] = families[family]

    # Register one explicit parser per documented endpoint row.
    for spec in ALL_ENDPOINTS:
        current_sub = families[spec.command[0]]
        prefix = (spec.command[0],)
        for part in spec.command[1:-1]:
            prefix = prefix + (part,)
            if prefix not in nested:
                parent = current_sub.add_parser(part, help=f"{part} commands")
                nested[prefix] = parent.add_subparsers(dest=f"{part.replace('-', '_')}_cmd", required=True, parser_class=_ToolArgumentParser)
            current_sub = nested[prefix]
        leaf = current_sub.add_parser(spec.command[-1], help=f"{spec.method} {spec.path}")
        _register_endpoint_command(leaf, spec)

    de = families["data-export"].add_parser("download-run-file", help="Download a Data Export run file from the run's returned URL")
    de.add_argument("--job-id", required=True, help="Export job id")
    de.add_argument("--run-id-value", required=True, help="Export run id")
    de.add_argument("--output-file", required=True, help="Safe local output file path")
    de.add_argument("--file-index", type=int, default=None, help="Zero-based files[] index to download when a run has multiple files")
    de.add_argument("--part-id", default=None, help="files[].partId value to download when a run has multiple files")
    de.add_argument("--overwrite", action="store_true", help="Replace an existing output file")
    de.add_argument("--scope", default=None, help="Optional OAuth scope override")
    de.set_defaults(func=contentsquare_cmd.cmd_download_run_file, write_capable=True)


def build_parser() -> argparse.ArgumentParser:
    p = _ToolArgumentParser(prog="contentsquare-safe-cli")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--config", default=None, help="Optional project defaults JSON (non-secret)")
    p.add_argument("--project-dir", default=None, help="Optional project directory (defaults to config file folder)")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument("--oauth-project-id", default=None, help="Project id for account-level OAuth credentials")
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
    p.add_argument(
        "--ack-no-snapshot",
        action="store_true",
        help="Acknowledge that the provider does not expose a safe before/after snapshot",
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
    auth_check.add_argument("--scope", default=None, help="OAuth scope to check (default: data-export)")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=False)
    auth_me = auth_sub.add_parser("me", help="Check the OAuth credential identity")
    auth_me.set_defaults(func=auth_cmd.cmd_auth_me, write_capable=False)

    _add_contentsquare_commands(sub)

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
            payload = {"ok": True, "tool": "contentsquare-safe-cli", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"contentsquare-safe-cli {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        command_str = "contentsquare-safe-cli " + " ".join(argv)
        audit.bind_context(
            {
                "tool": "contentsquare-safe-cli",
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
                "tool": "contentsquare-safe-cli",
                "tool_version": __version__,
                "command_str": command_str,
                "project_cfg": project_cfg,
                "project_dir": project_dir,
                "env_file": str(args.env_file),
                "oauth_project_id": getattr(args, "oauth_project_id", None),
                "timeout_s": None,
                "verbose": bool(args.verbose),
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "plan_out": args.plan_out,
                "plan_in": args.plan_in,
                "receipt_out": args.receipt_out,
                "ack_irreversible": bool(args.ack_irreversible),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "run_id": run_ctx.run_id,
                "artifacts_dir": run_ctx.artifacts_dir,
                "runs_index_path": runs_index_path,
            }
            rc = int(args.func(args, ctx))
            return rc

        cfg = load_config(args.env_file)
        env_fingerprint = cfg.api_base_url or cfg.auth_base_url
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "tool": "contentsquare-safe-cli",
            "tool_version": __version__,
            "command_str": command_str,
            "project_cfg": project_cfg,
            "project_dir": project_dir,
            "env_file": str(args.env_file),
            "oauth_project_id": getattr(args, "oauth_project_id", None),
            "timeout_s": timeout_s,
            "verbose": bool(args.verbose),
            "apply": bool(args.apply),
            "yes": bool(args.yes),
            "plan_out": args.plan_out,
            "plan_in": args.plan_in,
            "receipt_out": args.receipt_out,
            "ack_irreversible": bool(args.ack_irreversible),
            "ack_no_snapshot": bool(args.ack_no_snapshot),
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
                "tool": "contentsquare-safe-cli",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "env_fingerprint": env_fingerprint,
                "run_id": run_ctx.run_id,
            }
        )
        rc = int(args.func(args, ctx))

        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="contentsquare-safe-cli",
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
            tool="contentsquare-safe-cli",
            version=__version__,
            command="contentsquare-safe-cli " + " ".join(argv),
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
            tool="contentsquare-safe-cli",
            version=__version__,
            command="contentsquare-safe-cli " + " ".join(argv),
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
            tool="contentsquare-safe-cli",
            version=__version__,
            command="contentsquare-safe-cli " + " ".join(argv),
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
