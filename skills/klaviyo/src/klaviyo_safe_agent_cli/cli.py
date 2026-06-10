from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import api as api_cmd
from .commands import auth as auth_cmd
from .commands import onboarding as onboarding_cmd
from .config import build_env_fingerprint, load_config
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
    """Keep JSON mode as one object for parse errors."""

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


def _api_op_shared_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--path-json", default=None, help="JSON object (or file path) for path params")
    p.add_argument("--query-json", default=None, help="JSON object (or file path) for query params")
    p.add_argument("--body-json", default=None, help="JSON object (or file path) for request body")
    p.add_argument("--path", action="append", default=None, help="Path param as key=value")
    p.add_argument("--query", action="append", default=None, help="Query param as key=value")
    p.add_argument("--file", action="append", default=None, help="Multipart file as field=path")


def build_parser() -> argparse.ArgumentParser:
    p = _ToolArgumentParser(prog="klaviyo-safe-agent-cli")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--config", default=None, help="Optional project defaults JSON (non-secret)")
    p.add_argument("--project-dir", default=None, help="Optional project defaults JSON directory")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--live", action="store_true", help="Allow real HTTP calls (plan-only by default)")
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    p.add_argument("--debug", action="store_true", help="Show stack traces on errors")
    p.add_argument("--output", choices=("json", "text"), default="json", help="Output format")
    p.add_argument("--log-file", default=None, help="Optional audit log path (JSONL)")
    p.add_argument("--apply", action="store_true", help="Apply (run real API calls, requires --live)")
    p.add_argument("--yes", action="store_true", help="Required for high-impact operations")
    p.add_argument(
        "--ack-no-snapshot",
        action="store_true",
        help="Acknowledge that this approved write may run without a saved before-state snapshot",
    )
    p.add_argument("--plan-out", default=None, help="Write plan JSON")
    p.add_argument("--plan-in", default=None, help="Use plan JSON for apply")
    p.add_argument("--receipt-out", default=None, help="Write receipt JSON")
    p.add_argument("--run-id", default=None, help="Optional run id")
    p.add_argument("--artifacts-dir", default=None, help="Optional artifacts directory")
    p.add_argument("--no-artifacts", action="store_true", help="Disable local artifacts")

    sub = p.add_subparsers(dest="cmd", required=False, parser_class=_ToolArgumentParser)

    runs = sub.add_parser("runs", help="Run history (local)")
    runs_sub = runs.add_subparsers(dest="runs_cmd", required=True, parser_class=_ToolArgumentParser)
    runs_list = runs_sub.add_parser("list", help="List recent runs")
    runs_list.add_argument("--limit", type=int, default=20, help="Max rows")
    runs_list.set_defaults(func=_cmd_runs_list, write_capable=False)
    runs_show = runs_sub.add_parser("show", help="Show one run by id")
    runs_show.add_argument("--run-id", required=True, help="Run id")
    runs_show.set_defaults(func=_cmd_runs_show, write_capable=False)

    onboarding = sub.add_parser("onboarding", help="Setup helper")
    onboarding.add_argument(
        "--no-write-env",
        action="store_true",
        help="Do not copy .env.example to .env",
    )
    onboarding.set_defaults(func=onboarding_cmd.cmd_onboarding, write_capable=False)

    auth = sub.add_parser("auth", help="Auth checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Check auth config")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=False)

    api = sub.add_parser("api", help="Klaviyo API operations")
    api_sub = api.add_subparsers(dest="api_cmd", required=True, parser_class=_ToolArgumentParser)
    api_ops = api_sub.add_parser("ops", help="Show pinned operations")
    api_ops_sub = api_ops.add_subparsers(dest="api_ops_cmd", required=True, parser_class=_ToolArgumentParser)
    api_ops_list = api_ops_sub.add_parser("list", help="List pinned operations")
    api_ops_list.add_argument("--method", default=None, help="Filter by method")
    api_ops_list.add_argument("--tag", default=None, help="Filter by tag")
    api_ops_list.set_defaults(func=api_cmd.cmd_api_ops_list, write_capable=False)
    api_ops_show = api_ops_sub.add_parser("show", help="Show one pinned operation")
    api_ops_show.add_argument("--op", required=True, help="Operation command name")
    api_ops_show.set_defaults(func=api_cmd.cmd_api_ops_show, write_capable=False)

    from .api_dispatch import load_operations_from_pinned_snapshot

    operations = load_operations_from_pinned_snapshot()
    reserved = {"ops", "show"}
    collisions = {op.operation_command for op in operations if op.operation_command in reserved}
    if collisions:
        raise RuntimeError(f"Operation commands collide with reserved api names: {', '.join(sorted(collisions))}")
    for op in operations:
        api_op = api_sub.add_parser(op.operation_command, help=f"{op.method} {op.path}")
        _api_op_shared_args(api_op)
        api_op.set_defaults(func=api_cmd.cmd_api_call, write_capable=True, op=op.operation_command)

    return p


def _output_mode_from_argv(argv: list[str]) -> str:
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
        try:
            return int(e.code or 0)
        except Exception:
            return 0

    write_capable = bool(getattr(args, "write_capable", False))
    run_ctx: RunContext = init_run_context(
        env_file=str(args.env_file),
        enabled=write_capable,
        run_id=str(args.run_id) if getattr(args, "run_id", None) else None,
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
        run_ctx = RunContext(enabled=False, run_id=None, artifacts_dir=None, runs_index_path=runs_index_path, audit_log_path=None)

    if bool(args.no_artifacts):
        run_ctx = RunContext(enabled=False, run_id=None, artifacts_dir=None, runs_index_path=runs_index_path, audit_log_path=None)

    out.set_provenance(
        {
            "run_id": run_ctx.run_id,
            "artifacts_dir": str(run_ctx.artifacts_dir) if run_ctx.artifacts_dir else None,
            "runs_index": str(run_ctx.runs_index_path) if run_ctx.runs_index_path else str(runs_index_path),
            "audit_log": run_audit_log_path or global_audit_log_path,
            "audit_log_global": global_audit_log_path,
        }
    )

    command_str = "klaviyo-safe-agent-cli " + " ".join(argv)
    if bool(getattr(args, "version", False)):
        payload = {"ok": True, "tool": "klaviyo-safe-agent-cli", "version": __version__}
        out.emit(payload)
        audit.close()
        return 0

    if not getattr(args, "cmd", None):
        out.emit(
            {
                "ok": False,
                "error": "Missing command. Use --help to see available commands.",
                "error_type": "ValidationError",
            }
        )
        audit.close()
        return 1

    local_only = str(getattr(args, "cmd", "") or "") in {"runs", "onboarding"}
    cfg = load_config(args.env_file) if not local_only else None

    try:
        env_fingerprint = build_env_fingerprint(cfg) if cfg else None
    except Exception:
        env_fingerprint = None

    ctx = {
        "cfg": cfg,
        "out": out,
        "audit": audit,
        "tool": "klaviyo-safe-agent-cli",
        "tool_version": __version__,
        "command_str": command_str,
        "project_cfg": project_cfg,
        "project_dir": project_dir,
        "env_file": str(args.env_file),
        "timeout_s": float(args.timeout_s) if args.timeout_s is not None and cfg is not None else (cfg.timeout_s if cfg else None),
        "live": bool(args.live),
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
        if not ctx.get("apply") and not ctx.get("plan_out"):
            ctx["plan_out"] = str(run_ctx.artifacts_dir / "plan.json")
        if ctx.get("apply") and not ctx.get("receipt_out"):
            ctx["receipt_out"] = str(run_ctx.artifacts_dir / "receipt.json")

    try:
        audit.bind_context(
            {
                "tool": "klaviyo-safe-agent-cli",
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
            tool="klaviyo-safe-agent-cli",
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
    except SafetyError as e:
        audit.write("safety_refusal", {"reason": str(e)})
        out.emit({"ok": True, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError"})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="klaviyo-safe-agent-cli",
            version=__version__,
            command=command_str,
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
            tool="klaviyo-safe-agent-cli",
            version=__version__,
            command=command_str,
            env_fingerprint=env_fingerprint,
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
            tool="klaviyo-safe-agent-cli",
            version=__version__,
            command=command_str,
            env_fingerprint=env_fingerprint,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 1
    finally:
        audit.close()
