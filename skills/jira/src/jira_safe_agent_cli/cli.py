from __future__ import annotations

import argparse
import time
from typing import Any

from . import __version__
from .audit_log import AuditLogger
from .commands.auth import cmd_auth_check
from .commands.onboarding import cmd_onboarding
from .config import load_config
from .errors import SafetyError, ToolError, ValidationError
from .operations import load_inventory, operation_map, run_operation
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


class ToolArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def parse_bool(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes"}:
        return True
    if lowered in {"0", "false", "no"}:
        return False
    raise argparse.ArgumentTypeError("expected true or false")


def output_mode(argv: list[str]) -> str:
    try:
        index = argv.index("--output")
        return argv[index + 1] if argv[index + 1] in {"json", "text"} else "json"
    except (ValueError, IndexError):
        return "json"


def add_operation_argument(parser: argparse.ArgumentParser, parameter: dict[str, Any]) -> None:
    kwargs: dict[str, Any] = {
        "required": False,
        "help": parameter["description"]
        or f"Jira {parameter['in']} parameter: {parameter['name']}",
    }
    if parameter["array"] or parameter["free_form_object"]:
        kwargs["action"] = "append"
    elif parameter["schema_type"] == "integer":
        kwargs["type"] = int
    elif parameter["schema_type"] == "number":
        kwargs["type"] = float
    elif parameter["schema_type"] == "boolean":
        kwargs["type"] = parse_bool
    parser.add_argument(parameter["cli_flag"], **kwargs)


def build_parser(inventory: dict[str, Any]) -> argparse.ArgumentParser:
    parser = ToolArgumentParser(prog="jira-safe", description="Fixed-command Jira Cloud API tool")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    parser.add_argument("--env-file", default=".env", help="Local environment file (default: .env)")
    parser.add_argument("--timeout-s", type=float, default=None, help="Override JIRA_TIMEOUT_S")
    parser.add_argument("--verbose", action="store_true", help="Print request timing to stderr")
    parser.add_argument("--debug", action="store_true", help="Raise unexpected errors")
    parser.add_argument("--output", choices=("json", "text"), default="json", help="Output format")
    parser.add_argument("--log-file", default=None, help="Optional redacted JSONL audit log")
    parser.add_argument("--apply", action="store_true", help="Apply a reviewed write plan")
    parser.add_argument("--yes", action="store_true", help="Confirm the reviewed write plan")
    parser.add_argument("--plan-out", default=None, help="Saved dry-run plan path")
    parser.add_argument("--plan-in", default=None, help="Reviewed plan path used for apply")
    parser.add_argument("--receipt-out", default=None, help="Saved apply receipt path")
    parser.add_argument(
        "--ack-no-snapshot", action="store_true", help="Accept a write without saved before-state"
    )
    parser.add_argument(
        "--ack-high-risk", action="store_true", help="Approve a production-risk operation"
    )
    parser.add_argument("--run-id", default=None, help="Optional local run ID")
    parser.add_argument("--artifacts-dir", default=None, help="Override the local run directory")
    parser.add_argument(
        "--no-artifacts", action="store_true", help="Disable artifacts for read-only commands"
    )

    root = parser.add_subparsers(dest="root_command", parser_class=ToolArgumentParser)

    onboarding = root.add_parser("onboarding", help="Create placeholder setup and show next steps")
    onboarding.add_argument(
        "--no-write-env", action="store_true", help="Show setup without creating .env"
    )
    onboarding.add_argument("--auth-mode", choices=("basic", "oauth"), default="basic")
    onboarding.set_defaults(func=cmd_onboarding, local_command=True, write_capable=False)

    auth = root.add_parser("auth", help="Check Jira authentication")
    auth_sub = auth.add_subparsers(
        dest="auth_command", required=True, parser_class=ToolArgumentParser
    )
    auth_check = auth_sub.add_parser("check", help="Read the current Jira user")
    auth_check.set_defaults(func=cmd_auth_check, local_command=False, write_capable=False)

    operations_parser = root.add_parser("operations", help="Inspect the fixed command inventory")
    operations_sub = operations_parser.add_subparsers(
        dest="operations_command", required=True, parser_class=ToolArgumentParser
    )
    operations_list = operations_sub.add_parser("list", help="List fixed commands")
    operations_list.add_argument("--surface", choices=("platform", "software"), default=None)
    operations_list.add_argument("--kind", choices=("read", "write"), default=None)
    operations_list.add_argument("--status", default=None)
    operations_list.add_argument("--limit", type=int, default=50)
    operations_list.set_defaults(func=cmd_operations_list, local_command=True, write_capable=False)
    operations_show = operations_sub.add_parser("show", help="Show one fixed command")
    operations_show.add_argument("--surface", choices=("platform", "software"), required=True)
    operations_show.add_argument("--command", required=True)
    operations_show.set_defaults(func=cmd_operations_show, local_command=True, write_capable=False)

    runs = root.add_parser("runs", help="Review local write runs")
    runs_sub = runs.add_subparsers(
        dest="runs_command", required=True, parser_class=ToolArgumentParser
    )
    runs_list = runs_sub.add_parser("list", help="List recent write runs")
    runs_list.add_argument("--limit", type=int, default=20)
    runs_list.set_defaults(func=cmd_runs_list, local_command=True, write_capable=False)
    runs_show = runs_sub.add_parser("show", help="Show one write run")
    runs_show.add_argument("--run-id", required=True)
    runs_show.set_defaults(func=cmd_runs_show, local_command=True, write_capable=False)

    by_surface: dict[str, list[dict[str, Any]]] = {"platform": [], "software": []}
    for operation in inventory["operations"]:
        by_surface[operation["surface"]].append(operation)
    for surface in ("platform", "software"):
        surface_parser = root.add_parser(surface, help=f"Fixed Jira {surface} commands")
        surface_sub = surface_parser.add_subparsers(
            dest=f"{surface}_command", required=True, parser_class=ToolArgumentParser
        )
        for operation in by_surface[surface]:
            command_parser = surface_sub.add_parser(
                operation["command"],
                help=operation["summary"],
                description=f"{operation['summary']} ({operation['method']} {operation['path']})",
            )
            for parameter in operation["parameters"]:
                add_operation_argument(command_parser, parameter)
            if operation["request_content_types"]:
                command_parser.add_argument("--body-file", default=None, help="Request body file")
                command_parser.add_argument(
                    "--content-type", choices=operation["request_content_types"], default=None
                )
            if "multipart/form-data" in operation["request_content_types"]:
                command_parser.add_argument(
                    "--file",
                    action="append",
                    default=None,
                    help="Multipart file as field=path; repeatable",
                )
                command_parser.add_argument(
                    "--form",
                    action="append",
                    default=None,
                    help="Multipart text field as name=value; repeatable",
                )
            command_parser.add_argument(
                "--response-out", default=None, help="Required destination for binary output"
            )
            command_parser.set_defaults(
                func=run_operation,
                local_command=False,
                write_capable=operation["kind"] == "write",
                operation=operation,
                surface=surface,
                command_name=operation["command"],
            )
    return parser


def cmd_operations_list(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    rows = []
    for operation in ctx["inventory"]["operations"]:
        if args.surface and operation["surface"] != args.surface:
            continue
        if args.kind and operation["kind"] != args.kind:
            continue
        if args.status and operation["coverage_status"] != args.status:
            continue
        rows.append(
            {
                "command": operation["full_command"],
                "summary": operation["summary"],
                "kind": operation["kind"],
                "coverage_status": operation["coverage_status"],
            }
        )
    limit = max(1, min(int(args.limit), 721))
    ctx["out"].emit(
        {"ok": True, "count": len(rows), "shown": min(limit, len(rows)), "operations": rows[:limit]}
    )
    return 0


def cmd_operations_show(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    operation = operation_map(ctx["inventory"]).get((args.surface, args.command))
    if not operation:
        raise ValidationError(f"Unknown fixed command: jira-safe {args.surface} {args.command}")
    ctx["out"].emit({"ok": True, "operation": operation})
    return 0


def cmd_runs_list(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    index = runs_index_path_for_env_file(args.env_file)
    rows = list_runs(index, limit=max(1, min(args.limit, 100)))
    ctx["out"].emit({"ok": True, "count": len(rows), "runs": rows})
    return 0


def cmd_runs_show(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    index = runs_index_path_for_env_file(args.env_file)
    row = find_run(index, run_id=args.run_id)
    if not row:
        raise ValidationError(f"Run not found: {args.run_id}")
    ctx["out"].emit({"ok": True, "run": row})
    return 0


def finalize_run(run_ctx: RunContext, args: argparse.Namespace, out: Output) -> None:
    if (
        not run_ctx.enabled
        or not run_ctx.artifacts_dir
        or not run_ctx.runs_index_path
        or not run_ctx.run_id
    ):
        return
    plan_path = run_ctx.artifacts_dir / "plan.json"
    receipt_path = run_ctx.artifacts_dir / "receipt.json"
    summary = build_deterministic_summary(
        tool="jira-safe",
        version=__version__,
        run_id=run_ctx.run_id,
        env_fingerprint=None,
        command=f"jira-safe {getattr(args, 'surface', '')} {getattr(args, 'command_name', '')}".strip(),
        output_obj=out.last if isinstance(out.last, dict) else None,
        plan_path=str(plan_path) if plan_path.exists() else None,
        receipt_path=str(receipt_path) if receipt_path.exists() else None,
        audit_log_path=str(run_ctx.audit_log_path) if run_ctx.audit_log_path else None,
        audit_log_global_path=str(args.log_file) if args.log_file else None,
        runs_index_path=str(run_ctx.runs_index_path),
    )
    write_summary_md(path=run_ctx.artifacts_dir / "summary.md", lines=summary)
    append_index_row(
        run_ctx.runs_index_path,
        {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "run_id": run_ctx.run_id,
            "artifacts_dir": str(run_ctx.artifacts_dir),
            "tool": "jira-safe",
            "operation": getattr(args, "operation", {}).get("operation_id")
            if hasattr(args, "operation")
            else None,
            "ok": bool(out.last.get("ok")) if isinstance(out.last, dict) else False,
            "refused": bool(out.last.get("refused")) if isinstance(out.last, dict) else False,
            "plan_path": str(plan_path) if plan_path.exists() else None,
            "receipt_path": str(receipt_path) if receipt_path.exists() else None,
        },
    )


def main(argv: list[str]) -> int:
    inventory = load_inventory()
    parser = build_parser(inventory)
    out = Output(mode=output_mode(argv))
    args: argparse.Namespace | None = None
    audit = AuditLogger(path=None, enabled=False)
    run_ctx = RunContext(False, None, None, None, None)
    try:
        args = parser.parse_args(argv)
        if args.version:
            out.emit({"ok": True, "tool": "jira-safe", "version": __version__})
            return 0
        if not getattr(args, "root_command", None):
            raise ValidationError("Missing command. Use --help to see fixed Jira commands.")
        if args.timeout_s is not None:
            if args.timeout_s <= 0:
                raise ValidationError("--timeout-s must be greater than zero")
        write_capable = bool(getattr(args, "write_capable", False))
        if write_capable and args.no_artifacts:
            raise SafetyError(
                "Write plans and receipts require local run artifacts; remove --no-artifacts"
            )
        run_ctx = init_run_context(
            env_file=args.env_file,
            enabled=write_capable,
            run_id=args.run_id,
            artifacts_dir=args.artifacts_dir,
            no_artifacts=bool(args.no_artifacts),
        )
        if write_capable and run_ctx.artifacts_dir:
            if not args.apply and not args.plan_out:
                args.plan_out = str(run_ctx.artifacts_dir / "plan.json")
            if args.apply and not args.receipt_out:
                args.receipt_out = str(run_ctx.artifacts_dir / "receipt.json")
        audit_path = str(run_ctx.audit_log_path) if run_ctx.audit_log_path else args.log_file
        audit = AuditLogger(path=audit_path, enabled=bool(audit_path))
        command_label = f"jira-safe {getattr(args, 'surface', args.root_command)} {getattr(args, 'command_name', '')}".strip()
        audit.bind_context(
            {
                "tool": "jira-safe",
                "version": __version__,
                "command": command_label,
                "run_id": run_ctx.run_id,
            }
        )
        out.set_provenance(
            {
                "run_id": run_ctx.run_id,
                "artifacts_dir": str(run_ctx.artifacts_dir) if run_ctx.artifacts_dir else None,
                "runs_index": str(run_ctx.runs_index_path) if run_ctx.runs_index_path else None,
            }
        )

        def config_loader(*, require_auth: bool) -> Any:
            config = load_config(args.env_file, require_auth=require_auth)
            if args.timeout_s is not None:
                return type(config)(
                    base_url=config.base_url,
                    email=config.email,
                    api_token=config.api_token,
                    oauth_access_token=config.oauth_access_token,
                    timeout_s=float(args.timeout_s),
                )
            return config

        ctx = {
            "inventory": inventory,
            "operation": getattr(args, "operation", None),
            "out": out,
            "audit": audit,
            "run_ctx": run_ctx,
            "artifacts_dir": str(run_ctx.artifacts_dir) if run_ctx.artifacts_dir else None,
            "plan_out": args.plan_out,
            "receipt_out": args.receipt_out,
            "env_file": args.env_file,
            "config_loader": config_loader,
        }
        rc = int(args.func(args, ctx))
        finalize_run(run_ctx, args, out)
        return rc
    except ValidationError as exc:
        out.emit({"ok": False, "error": str(exc), "error_type": type(exc).__name__})
        if args is not None:
            finalize_run(run_ctx, args, out)
        return 1
    except SafetyError as exc:
        audit.write("refused", {"reason": str(exc)})
        out.emit(
            {"ok": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError"}
        )
        if args is not None:
            finalize_run(run_ctx, args, out)
        return 0
    except ToolError as exc:
        audit.write("error", {"error": str(exc), "error_type": type(exc).__name__})
        out.emit({"ok": False, "error": str(exc), "error_type": type(exc).__name__})
        if args is not None:
            finalize_run(run_ctx, args, out)
        return 1
    except KeyboardInterrupt:
        return 130
    except SystemExit as exc:
        return int(exc.code or 0)
    except Exception as exc:  # noqa: BLE001
        if args is not None and bool(getattr(args, "debug", False)):
            raise
        out.emit({"ok": False, "error": str(exc), "error_type": type(exc).__name__})
        if args is not None:
            finalize_run(run_ctx, args, out)
        return 1
    finally:
        audit.close()
