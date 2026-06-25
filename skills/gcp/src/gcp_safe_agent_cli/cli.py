from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import auth as auth_cmd
from .commands import onboarding as onboarding_cmd
from .config import load_config
from .generated_registry import load_registry
from .generated_runtime import execute_generated_operation, inventory_summary
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


def _env_base_dir(env_file: str) -> Path:
    return Path(env_file or ".env").expanduser().resolve().parent


def _display_path(path: str | Path | None, *, env_file: str) -> str | None:
    if path is None:
        return None
    raw = str(path).strip()
    if not raw:
        return None
    base = _env_base_dir(env_file)
    resolved = Path(raw).expanduser().resolve()
    try:
        return str(resolved.relative_to(base))
    except ValueError:
        return f"<outside-env-dir>/{resolved.name}"


def _resolve_display_path(path: str, *, env_file: str) -> Path:
    raw = str(path or "").strip()
    if not raw or raw.startswith("<outside-env-dir>/"):
        return Path()
    p = Path(raw)
    if p.is_absolute():
        return p
    return _env_base_dir(env_file) / p


def _display_argv(argv: list[str], *, env_file: str) -> str:
    shown: list[str] = []
    for item in argv:
        text = str(item)
        if text.startswith("--") and "=" in text:
            flag, value = text.split("=", 1)
            p = Path(value).expanduser()
            if p.is_absolute():
                shown.append(f"{flag}={_display_path(p, env_file=env_file) or '<path>'}")
            else:
                shown.append(text)
            continue
        if text.startswith("-"):
            shown.append(text)
            continue
        p = Path(text).expanduser()
        if p.is_absolute():
            shown.append(_display_path(p, env_file=env_file) or "<path>")
        else:
            shown.append(text)
    return "qwayk-gcp-safe-agent-cli " + " ".join(shown)


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
            p = _resolve_display_path(ad, env_file=str(ctx.get("env_file") or ".env")) / "summary.md"
            if p.exists():
                summary = p.read_text(encoding="utf-8")
    except Exception:
        summary = None
    ctx["out"].emit({"ok": True, "run": row, "summary_md": summary})
    return 0


def _cmd_inventory_summary(args: argparse.Namespace, ctx: dict) -> int:
    _ = args, ctx
    payload = inventory_summary()
    ctx["out"].emit(payload)
    return 0


def _register_generated_services(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    registry = load_registry()
    reserved = {"auth", "inventory", "onboarding", "runs"}
    services = sorted(
        [
            service
            for service in registry.data.get("services", [])
            if str(service.get("api_id") or "").strip() and str(service.get("api_id") or "").strip() not in reserved
        ],
        key=lambda service: str(service.get("api_id") or ""),
    )
    for service in services:
        service_id = str(service.get("api_id") or "").strip()
        if not service_id:
            continue
        operations = sorted(
            [operation for operation in service.get("operations", []) if str(operation.get("operation_name") or "").strip()],
            key=lambda operation: str(operation.get("operation_name") or ""),
        )
        service_parser = sub.add_parser(service_id, help=f"{service.get('title') or service_id} ({len(operations)} operations)")
        service_parser.add_argument(
            "operation",
            choices=[str(operation.get("operation_name") or "").strip() for operation in operations],
            metavar="OPERATION",
            help="Pinned generated operation name",
        )
        service_parser.add_argument("--input-json", required=True, help="Path to the generated input JSON file")
        service_parser.add_argument(
            "--apply",
            action="store_true",
            default=argparse.SUPPRESS,
            help="Apply changes (default is dry-run)",
        )
        service_parser.add_argument(
            "--yes",
            action="store_true",
            default=argparse.SUPPRESS,
            help="Additional confirmation for destructive/batch actions",
        )
        service_parser.add_argument(
            "--ack-no-snapshot",
            action="store_true",
            default=argparse.SUPPRESS,
            help="Extra acknowledgement for high-risk or no-snapshot writes",
        )
        service_parser.add_argument(
            "--plan-out",
            default=argparse.SUPPRESS,
            help="Write a dry-run plan JSON to a file",
        )
        service_parser.add_argument(
            "--plan-in",
            default=argparse.SUPPRESS,
            help="Apply from an existing plan JSON file (high-risk writes)",
        )
        service_parser.add_argument(
            "--receipt-out",
            default=argparse.SUPPRESS,
            help="Write an apply receipt JSON to a file",
        )
        service_parser.add_argument(
            "--ack-irreversible",
            action="store_true",
            default=argparse.SUPPRESS,
            help="Extra acknowledgement for irreversible actions",
        )
        service_parser.add_argument(
            "--quota-project",
            default=argparse.SUPPRESS,
            help="Override the quota/billing project used for requests",
        )
        service_parser.add_argument(
            "--output-file",
            default=argparse.SUPPRESS,
            help="Write the safe command result JSON to a file",
        )
        service_parser.set_defaults(func=execute_generated_operation, write_capable=True)


def _register_inventory_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    inventory = sub.add_parser("inventory", help="Generated discovery inventory helpers")
    inventory_sub = inventory.add_subparsers(dest="inventory_cmd", required=True, parser_class=_ToolArgumentParser)
    summary = inventory_sub.add_parser("summary", help="Show the generated discovery inventory summary")
    summary.set_defaults(func=_cmd_inventory_summary, write_capable=False)


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
    env_file: str,
) -> None:
    if not run_ctx.enabled or not run_ctx.artifacts_dir or not run_ctx.runs_index_path or not run_ctx.run_id:
        return

    plan_file = run_ctx.artifacts_dir / "plan.json"
    receipt_file = run_ctx.artifacts_dir / "receipt.json"
    plan_path = _display_path(plan_file, env_file=env_file) if plan_file.exists() else None
    receipt_path = _display_path(receipt_file, env_file=env_file) if receipt_file.exists() else None
    audit_log_display = _display_path(audit_log_path, env_file=env_file)
    audit_log_global_display = _display_path(audit_log_global_path, env_file=env_file)
    runs_index_display = _display_path(run_ctx.runs_index_path, env_file=env_file)

    summary_lines = build_deterministic_summary(
        tool=tool,
        version=version,
        run_id=run_ctx.run_id,
        env_fingerprint=env_fingerprint,
        command=command,
        output_obj=output_obj,
        plan_path=plan_path,
        receipt_path=receipt_path,
        audit_log_path=audit_log_display,
        audit_log_global_path=audit_log_global_display,
        runs_index_path=runs_index_display,
    )
    write_summary_md(path=run_ctx.artifacts_dir / "summary.md", lines=summary_lines)

    append_index_row(
        run_ctx.runs_index_path,
        {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "run_id": run_ctx.run_id,
            "artifacts_dir": _display_path(run_ctx.artifacts_dir, env_file=env_file),
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
            "audit_log": audit_log_display,
            "audit_log_global": audit_log_global_display,
        },
    )


def build_parser() -> argparse.ArgumentParser:
    p = _ToolArgumentParser(prog="qwayk-gcp-safe-agent-cli")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--config", default=None, help="Optional project defaults JSON (non-secret)")
    p.add_argument("--project-dir", default=None, help="Optional project directory (defaults to config file folder)")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    p.add_argument("--debug", action="store_true", help="Show stack traces on errors")
    p.add_argument("--output", choices=("json", "text"), default="json", help="Output format (default: json)")
    p.add_argument("--output-file", default=None, help="Write the safe command result JSON to a file")
    p.add_argument("--log-file", default=None, help="Optional audit log path (JSONL)")
    p.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    p.add_argument("--yes", action="store_true", help="Additional confirmation for destructive/batch actions")
    p.add_argument(
        "--ack-no-snapshot",
        action="store_true",
        help="Extra acknowledgement for high-risk or no-snapshot writes",
    )
    p.add_argument("--plan-out", default=None, help="Write a dry-run plan JSON to a file")
    p.add_argument("--plan-in", default=None, help="Apply from an existing plan JSON file (high-risk writes)")
    p.add_argument("--receipt-out", default=None, help="Write an apply receipt JSON to a file")
    p.add_argument(
        "--ack-irreversible",
        action="store_true",
        help="Extra acknowledgement for irreversible actions",
    )
    p.add_argument("--quota-project", default=None, help="Override the quota/billing project used for requests")
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

    _register_inventory_command(sub)
    _register_generated_services(sub)

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
            "artifacts_dir": _display_path(run_ctx.artifacts_dir, env_file=str(args.env_file)) if run_ctx.artifacts_dir else None,
            "runs_index": _display_path(run_ctx.runs_index_path, env_file=str(args.env_file)) if run_ctx.runs_index_path else _display_path(runs_index_path, env_file=str(args.env_file)),
            "audit_log": _display_path(run_audit_log_path or global_audit_log_path, env_file=str(args.env_file)),
            "audit_log_global": _display_path(global_audit_log_path, env_file=str(args.env_file)),
        }
    )

    try:
        if bool(args.version):
            payload = {"ok": True, "tool": "qwayk-gcp-safe-agent-cli", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"qwayk-gcp-safe-agent-cli {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        command_str = _display_argv(argv, env_file=str(args.env_file))
        audit.bind_context(
            {
                "tool": "qwayk-gcp-safe-agent-cli",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "env_fingerprint": None,
                "run_id": run_ctx.run_id,
            }
        )

        # Some commands are local-only and don't need API config.
        if str(getattr(args, "cmd", "") or "") in {"runs", "onboarding", "inventory"}:
            ctx = {
                "cfg": None,
                "out": out,
                "audit": audit,
                "tool": "qwayk-gcp-safe-agent-cli",
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
                "quota_project": str(args.quota_project) if args.quota_project else None,
                "output_file": str(args.output_file) if args.output_file else None,
                "run_id": run_ctx.run_id,
                "artifacts_dir": run_ctx.artifacts_dir,
                "runs_index_path": runs_index_path,
            }
            rc = int(args.func(args, ctx))
            return rc

        cfg = load_config(args.env_file)
        env_fingerprint = None
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "tool": "qwayk-gcp-safe-agent-cli",
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
            "quota_project": str(args.quota_project) if args.quota_project else None,
            "output_file": str(args.output_file) if args.output_file else None,
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
                "tool": "qwayk-gcp-safe-agent-cli",
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
            tool="qwayk-gcp-safe-agent-cli",
            version=__version__,
            command=command_str,
            env_fingerprint=env_fingerprint,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
            env_file=str(args.env_file),
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
            tool="qwayk-gcp-safe-agent-cli",
            version=__version__,
            command=_display_argv(argv, env_file=str(args.env_file)),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
            env_file=str(args.env_file),
        )
        return 0
    except ToolError as e:
        audit.write("error", {"error": str(e), "error_type": type(e).__name__})
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="qwayk-gcp-safe-agent-cli",
            version=__version__,
            command=_display_argv(argv, env_file=str(args.env_file)),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
            env_file=str(args.env_file),
        )
        return 1
    except Exception as e:  # noqa: BLE001
        if bool(args.debug):
            raise
        audit.write("error", {"error": str(e), "error_type": type(e).__name__})
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="qwayk-gcp-safe-agent-cli",
            version=__version__,
            command=_display_argv(argv, env_file=str(args.env_file)),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
            env_file=str(args.env_file),
        )
        return 1
    finally:
        audit.close()
