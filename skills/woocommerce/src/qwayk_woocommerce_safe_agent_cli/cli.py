from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .catalog import OperationSpec, operations_by_family
from .commands import auth as auth_cmd
from .commands import onboarding as onboarding_cmd
from .commands import operations as operations_cmd
from .config import load_config
from .errors import SafetyError, ToolError, ValidationError
from .output import Output
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


TOOL_NAME = "qwayk-woocommerce-safe-agent-cli"


class _ToolArgumentParser(argparse.ArgumentParser):
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
    run_id = str(getattr(args, "run_id", "") or "").strip()
    if not run_id:
        ctx["out"].emit({"ok": False, "error": "Missing --run-id", "error_type": "ValidationError"})
        return 1
    runs_index = ctx.get("runs_index_path")
    if not runs_index or not runs_index.exists():
        ctx["out"].emit({"ok": False, "error": "No runs index found", "error_type": "NotFound"})
        return 1
    row = find_run(runs_index, run_id=run_id)
    if not row:
        ctx["out"].emit({"ok": False, "error": f"Run not found: {run_id}", "error_type": "NotFound"})
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


def _add_operation_parser(parent: argparse._SubParsersAction[argparse.ArgumentParser], spec: OperationSpec) -> None:
    family_parser = parent.choices.get(spec.family)
    if family_parser is None:
        family_parser = parent.add_parser(spec.family, help=f"{spec.family} endpoints")
        family_parser._operation_subparsers = family_parser.add_subparsers(  # type: ignore[attr-defined]
            dest=f"{spec.family.replace('-', '_')}_cmd",
            required=True,
            parser_class=_ToolArgumentParser,
        )
    family_subparsers = family_parser._operation_subparsers  # type: ignore[attr-defined]
    op = family_subparsers.add_parser(spec.action, help=f"{spec.method} {spec.path}")
    for path_param in spec.path_parameters:
        op.add_argument(
            f"--{path_param.replace('_', '-')}",
            dest=path_param,
            required=True,
            help=f"Path parameter: {path_param}",
        )
    op.add_argument("--params-file", default=None, help="JSON file with query params")
    op.add_argument("--params-json", default=None, help="Inline JSON object with query params")
    if spec.supports_pagination:
        op.add_argument("--page", type=int, default=None, help="Result page number")
        op.add_argument("--per-page", type=int, default=None, help="Per-page size")
        op.add_argument("--all", action="store_true", help="Collect all pages up to --max-pages")
        op.add_argument("--max-pages", type=int, default=10, help="Pagination guardrail when using --all")
    if spec.body_mode != "none":
        op.add_argument("--body-file", default=None, help="JSON file with request body")
        op.add_argument("--body-json", default=None, help="Inline JSON object or array with request body")
    op.set_defaults(
        func=operations_cmd.cmd_execute_operation,
        write_capable=spec.method != "GET",
        operation_spec=spec,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = _ToolArgumentParser(prog=TOOL_NAME)
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    parser.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    parser.add_argument(
        "--config",
        default=None,
        help="Optional JSON config file for non-secret defaults",
    )
    parser.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    parser.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    parser.add_argument("--debug", action="store_true", help="Show stack traces on errors")
    parser.add_argument("--output", choices=("json", "text"), default="json", help="Output format (default: json)")
    parser.add_argument("--log-file", default=None, help="Optional audit log path (JSONL)")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    parser.add_argument("--yes", action="store_true", help="Extra confirmation for high-risk writes")
    parser.add_argument(
        "--ack-no-snapshot",
        action="store_true",
        help="Acknowledge that this approved write may run without a saved before-state snapshot",
    )
    parser.add_argument("--plan-out", default=None, help="Write a dry-run plan JSON to a file")
    parser.add_argument("--plan-in", default=None, help="Apply from an existing reviewed plan JSON file")
    parser.add_argument("--receipt-out", default=None, help="Write an approved apply receipt JSON to a file")
    parser.add_argument("--run-id", default=None, help="Optional run id (for local run history)")
    parser.add_argument("--artifacts-dir", default=None, help="Optional artifacts directory for this run")
    parser.add_argument("--no-artifacts", action="store_true", help="Disable writing local run artifacts")

    sub = parser.add_subparsers(dest="cmd", required=False, parser_class=_ToolArgumentParser)

    runs = sub.add_parser("runs", help="Run history (local)")
    runs_sub = runs.add_subparsers(dest="runs_cmd", required=True, parser_class=_ToolArgumentParser)
    runs_list = runs_sub.add_parser("list", help="List recent runs")
    runs_list.add_argument("--limit", type=int, default=20, help="Max runs to return (default: 20)")
    runs_list.set_defaults(func=_cmd_runs_list, write_capable=False)
    runs_show = runs_sub.add_parser("show", help="Show one run from the index")
    runs_show.add_argument("--run-id", required=True, help="Run id to show")
    runs_show.set_defaults(func=_cmd_runs_show, write_capable=False)

    onboarding = sub.add_parser("onboarding", help="First-time setup help (no secrets)")
    onboarding.add_argument("--no-write-env", action="store_true", help="Do not write .env; print steps only")
    onboarding.set_defaults(func=onboarding_cmd.cmd_onboarding, write_capable=False)

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Smoke test WooCommerce REST credentials")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=False)

    operations = sub.add_parser("operations", help="Official WooCommerce REST API inventory")
    operations_sub = operations.add_subparsers(dest="operations_cmd", required=True, parser_class=_ToolArgumentParser)
    operations_list = operations_sub.add_parser("list", help="List all packaged WooCommerce operations")
    operations_list.set_defaults(func=operations_cmd.cmd_operations_list, write_capable=False)

    for specs in operations_by_family().values():
        for spec in specs:
            _add_operation_parser(sub, spec)

    return parser


def _output_mode_from_argv(argv: list[str]) -> str:
    try:
        idx = argv.index("--output")
    except ValueError:
        return "json"
    if idx + 1 >= len(argv):
        return "json"
    value = str(argv[idx + 1] or "").strip()
    return value if value in {"json", "text"} else "json"


def main(argv: list[str]) -> int:
    parser = build_parser()
    out = Output(mode=_output_mode_from_argv(argv))
    try:
        args = parser.parse_args(argv)
    except ValidationError as exc:
        out.emit({"ok": False, "error": str(exc), "error_type": type(exc).__name__})
        return 1
    except SystemExit as exc:
        try:
            return int(exc.code or 0)
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
            payload = {"ok": True, "tool": TOOL_NAME, "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"{TOOL_NAME} {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        command_str = TOOL_NAME + " " + " ".join(argv)
        audit.bind_context(
            {
                "tool": TOOL_NAME,
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "env_fingerprint": None,
                "run_id": run_ctx.run_id,
            }
        )

        if str(getattr(args, "cmd", "") or "") in {"runs", "onboarding", "operations"}:
            ctx = {
                "cfg": None,
                "out": out,
                "audit": audit,
                "tool": TOOL_NAME,
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
                "run_id": run_ctx.run_id,
                "artifacts_dir": run_ctx.artifacts_dir,
                "runs_index_path": runs_index_path,
            }
            return int(args.func(args, ctx))

        cfg = load_config(args.env_file, config_file=args.config)
        env_fingerprint = cfg.api_base_url
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "tool": TOOL_NAME,
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
                "tool": TOOL_NAME,
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "env_fingerprint": cfg.api_base_url,
                "run_id": run_ctx.run_id,
            }
        )
        rc = int(args.func(args, ctx))
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool=TOOL_NAME,
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
    except SafetyError as exc:
        audit.write("refused", {"reason": str(exc)})
        out.emit({"ok": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError"})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool=TOOL_NAME,
            version=__version__,
            command=TOOL_NAME + " " + " ".join(argv),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 0
    except ToolError as exc:
        audit.write("error", {"error": str(exc), "error_type": type(exc).__name__})
        out.emit({"ok": False, "error": str(exc), "error_type": type(exc).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool=TOOL_NAME,
            version=__version__,
            command=TOOL_NAME + " " + " ".join(argv),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 1
    except Exception as exc:  # noqa: BLE001
        if bool(args.debug):
            raise
        audit.write("error", {"error": str(exc), "error_type": type(exc).__name__})
        out.emit({"ok": False, "error": str(exc), "error_type": type(exc).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool=TOOL_NAME,
            version=__version__,
            command=TOOL_NAME + " " + " ".join(argv),
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
