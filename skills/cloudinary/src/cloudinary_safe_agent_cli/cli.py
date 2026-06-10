from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import auth as auth_cmd
from .commands import onboarding as onboarding_cmd
from .commands import operation_runner as operation_runner_cmd
from .commands import operations as operations_cmd
from .config import load_config
from .errors import SafetyError, ToolError, ValidationError
from .http import HttpClient
from .inventory import load_specs_by_area
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


def _add_operation_call_args(op_p: argparse.ArgumentParser) -> None:
    op_p.add_argument("--path-param", action="append", default=[], help="Path param key=value (repeatable)")
    op_p.add_argument("--query", action="append", default=[], help="Query param key=value (repeatable)")
    op_p.add_argument("--form-field", action="append", default=[], help="Form field key=value (repeatable)")
    op_p.add_argument("--body-json-file", default=None, help="JSON request body file")
    op_p.add_argument("--multipart-spec-file", default=None, help="Multipart spec JSON file (fields + file parts)")
    op_p.add_argument("--out", default=None, help="Write sensitive or binary output to this file under --project-dir")
    op_p.add_argument("--overwrite", action="store_true", help="Allow overwriting --out")


def build_parser() -> argparse.ArgumentParser:
    p = _ToolArgumentParser(prog="cloudinary-safe-agent-cli")
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
    p.add_argument("--yes", action="store_true", help="Additional confirmation for state-changing actions")
    p.add_argument(
        "--ack-no-snapshot",
        action="store_true",
        help="Acknowledge that this approved write may run without a saved before-state snapshot",
    )
    p.add_argument("--plan-out", default=None, help="Write a dry-run plan JSON to a file")
    p.add_argument("--plan-in", default=None, help="Apply from an existing plan JSON file")
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
    auth_check = auth_sub.add_parser("check", help="Smoke test product and account credentials")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=False)

    operations = sub.add_parser("operations", help="Explicit per-operation Cloudinary commands")
    ops_sub = operations.add_subparsers(dest="operations_cmd", required=True, parser_class=_ToolArgumentParser)

    ops_list = ops_sub.add_parser("list", help="Search allowlisted Cloudinary operations")
    ops_list.add_argument("--contains", default=None, help="Substring filter")
    ops_list.add_argument("--tag", default=None, help="Group or summary filter (substring)")
    ops_list.add_argument("--method", default=None, help="Method filter (GET/POST/PUT/PATCH/DELETE)")
    ops_list.add_argument("--area", default=None, help="Area filter (exact match)")
    ops_list.add_argument("--limit", type=int, default=200, help="Max operations to return (default: 200)")
    ops_list.add_argument("--include-deprecated", action="store_true", help="Include deprecated operations")
    ops_list.add_argument("--include-sensitive", action="store_true", help="Include sensitive or binary operations")
    ops_list.set_defaults(func=operations_cmd.cmd_operations_list, write_capable=False)

    ops_show = ops_sub.add_parser("show", help="Show one allowlisted Cloudinary operation")
    ops_show.add_argument("--area", required=True, help="Area name")
    ops_show.add_argument("--op", required=True, help="Operation key (op_key)")
    ops_show.set_defaults(func=operations_cmd.cmd_operations_show, write_capable=False)

    for area, specs in load_specs_by_area().items():
        area_parser = ops_sub.add_parser(area, help=f"Cloudinary operations: {area}")
        area_sub = area_parser.add_subparsers(dest="operation_key", required=True, parser_class=_ToolArgumentParser)
        for spec in specs:
            help_text = str(spec.summary or "").strip() or f"{spec.method} {spec.path_template}"
            if spec.requires_out:
                help_text = argparse.SUPPRESS
            op_p = area_sub.add_parser(spec.op_key, help=help_text)
            _add_operation_call_args(op_p)
            op_p.set_defaults(
                func=operation_runner_cmd.cmd_operation_call,
                write_capable=spec.is_write,
                operation_area=area,
            )

    return p


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
    cfg = None
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
            payload = {"ok": True, "tool": "cloudinary-safe-agent-cli", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"cloudinary-safe-agent-cli {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        command_str = "cloudinary-safe-agent-cli " + " ".join(argv)
        audit.bind_context(
            {
                "tool": "cloudinary-safe-agent-cli",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "env_fingerprint": None,
                "run_id": run_ctx.run_id,
            }
        )

        if str(getattr(args, "cmd", "") or "") in {"runs", "onboarding"}:
            ctx = {
                "cfg": None,
                "out": out,
                "audit": audit,
                "tool": "cloudinary-safe-agent-cli",
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
            return int(args.func(args, ctx))

        cfg = load_config(args.env_file)
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        env_fingerprint = cfg.env_fingerprint()

        ctx = {
            "cfg": cfg,
            "http": HttpClient(
                timeout_s=timeout_s,
                verbose=bool(args.verbose),
                user_agent=f"cloudinary-safe-agent-cli/{__version__}",
            ),
            "out": out,
            "audit": audit,
            "tool": "cloudinary-safe-agent-cli",
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
                "tool": "cloudinary-safe-agent-cli",
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
            tool="cloudinary-safe-agent-cli",
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
        message = cfg.redact(str(exc)) if cfg is not None else str(exc)
        audit.write("refused", {"reason": message})
        out.emit({"ok": True, "refused": True, "reasons": [message], "refusal_type": "SafetyError"})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="cloudinary-safe-agent-cli",
            version=__version__,
            command="cloudinary-safe-agent-cli " + " ".join(argv),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 0
    except ToolError as exc:
        message = cfg.redact(str(exc)) if cfg is not None else str(exc)
        audit.write("error", {"error": message, "error_type": type(exc).__name__})
        out.emit({"ok": False, "error": message, "error_type": type(exc).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="cloudinary-safe-agent-cli",
            version=__version__,
            command="cloudinary-safe-agent-cli " + " ".join(argv),
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
        message = cfg.redact(str(exc)) if cfg is not None else str(exc)
        audit.write("error", {"error": message, "error_type": type(exc).__name__})
        out.emit({"ok": False, "error": message, "error_type": type(exc).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="cloudinary-safe-agent-cli",
            version=__version__,
            command="cloudinary-safe-agent-cli " + " ".join(argv),
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
