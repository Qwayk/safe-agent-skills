from __future__ import annotations

import argparse
import sys
import traceback
from typing import Any

from . import __version__
from .audit_log import AuditLogger
from .commands import asana as asana_cmd
from .commands import onboarding as onboarding_cmd
from .config import load_config
from .errors import SafetyError, ToolError, ValidationError
from .inventory import command_names
from .output import Output


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def _positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="asana-safe")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    parser.add_argument("--env-file", default=".env", help="Secret environment file (default: .env)")
    parser.add_argument("--output", choices=("json", "text"), default="json")
    parser.add_argument("--timeout-s", type=_positive_float, default=None)
    parser.add_argument("--verbose", action="store_true", help="Write request timing to stderr")
    parser.add_argument("--debug", action="store_true", help="Write a traceback to stderr on errors")
    parser.add_argument("--log-file", default=None, help="Optional redacted JSONL audit log")
    sub = parser.add_subparsers(dest="cmd", parser_class=_Parser)

    onboarding = sub.add_parser("onboarding", help="Create a private placeholder env file and show setup")
    onboarding.add_argument("--no-write-env", action="store_true")
    onboarding.set_defaults(func=onboarding_cmd.cmd_onboarding, local_only=True)

    commands = sub.add_parser("commands", help="Browse the fixed Asana command inventory")
    commands_sub = commands.add_subparsers(dest="commands_cmd", required=True, parser_class=_Parser)
    commands_list = commands_sub.add_parser("list", help="List fixed commands")
    commands_list.add_argument("--family", default=None)
    commands_list.add_argument("--method", choices=("GET", "POST", "PUT", "DELETE"), default=None)
    commands_list.add_argument("--writes-only", action="store_true")
    commands_list.set_defaults(func=asana_cmd.cmd_commands_list, local_only=True)
    commands_show = commands_sub.add_parser("show", help="Show one fixed command")
    commands_show.add_argument("operation", choices=command_names())
    commands_show.set_defaults(func=asana_cmd.cmd_commands_show, local_only=True)

    auth = sub.add_parser("auth", help="Check the bearer-token connection")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_Parser)
    auth_check = auth_sub.add_parser("check", help="Read the current Asana user")
    auth_check.set_defaults(func=asana_cmd.cmd_auth_check, local_only=False)

    api = sub.add_parser("api", help="Run one fixed command from the pinned Asana REST inventory")
    api.add_argument("operation", choices=command_names())
    api.add_argument("--param", action="append", default=[], metavar="NAME=VALUE")
    api.add_argument("--data-json", default=None, help="Exact JSON object for the documented body")
    api.add_argument("--data-file", default=None, help="File containing the exact JSON body")
    api.add_argument("--file", action="append", default=[], metavar="FIELD=PATH")
    api.add_argument("--paginate", action="store_true", help="Follow documented offset pagination")
    api.add_argument("--max-pages", type=_positive_int, default=20)
    api.add_argument("--download-to", default=None, help="Required output file for non-JSON content")
    api.add_argument("--plan-out", default=None, help="Optional path for a saved write plan")
    api.add_argument("--plan-in", default=None, help="Reviewed plan to apply")
    api.add_argument("--apply", action="store_true", help="Apply the reviewed saved plan")
    api.add_argument("--approve", default=None, metavar="PLAN_ID", help="Approve this exact plan ID")
    api.add_argument("--acknowledge-no-snapshot", action="store_true")
    api.add_argument("--acknowledge-risk", action="store_true")
    api.add_argument("--receipt-out", default=None)
    api.add_argument("--wait", action="store_true", help="Poll a returned Asana job when available")
    api.add_argument("--wait-timeout-s", type=_positive_float, default=120.0)
    api.add_argument("--poll-interval-s", type=_positive_float, default=2.0)
    api.set_defaults(func=asana_cmd.cmd_api, local_only=False)
    return parser


def _output_mode(argv: list[str]) -> str:
    try:
        index = argv.index("--output")
    except ValueError:
        return "json"
    return argv[index + 1] if index + 1 < len(argv) and argv[index + 1] in {"json", "text"} else "json"


def main(argv: list[str]) -> int:
    out = Output(mode=_output_mode(argv))
    parser = build_parser()
    audit: AuditLogger | None = None
    try:
        args = parser.parse_args(argv)
        if args.version:
            out.emit({"ok": True, "tool": "asana-safe", "version": __version__})
            return 0
        if not args.cmd:
            raise ValidationError("Missing command. Use --help or `commands list`.")
        local_only = bool(getattr(args, "local_only", False))
        cfg = load_config(args.env_file, require_token=not local_only)
        if args.timeout_s is not None:
            cfg = type(cfg)(base_url=cfg.base_url, token=cfg.token, timeout_s=float(args.timeout_s))
        audit = AuditLogger(path=args.log_file, enabled=bool(args.log_file))
        audit.bind_context(
            {
                "tool": "qwayk-asana-safe-agent-cli",
                "version": __version__,
                "command": f"asana-safe {args.cmd}",
            }
        )
        context: dict[str, Any] = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "tool_version": __version__,
            "env_file": args.env_file,
            "verbose": bool(args.verbose),
        }
        return int(args.func(args, context))
    except SafetyError as exc:
        out.emit({"ok": False, "refused": True, "error": str(exc), "error_type": type(exc).__name__})
        return 2
    except ToolError as exc:
        out.emit({"ok": False, "error": str(exc), "error_type": type(exc).__name__})
        return 1
    except Exception as exc:  # noqa: BLE001
        if "--debug" in argv:
            traceback.print_exc(file=sys.stderr)
        out.emit(
            {
                "ok": False,
                "error": f"Unexpected local error: {type(exc).__name__}",
                "error_type": type(exc).__name__,
            }
        )
        return 1
    finally:
        if audit is not None:
            audit.close()
