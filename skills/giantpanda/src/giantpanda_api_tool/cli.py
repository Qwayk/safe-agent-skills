from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime

from . import __version__
from .commands import auth as auth_cmd
from .commands import domains as domains_cmd
from .commands import onboarding as onboarding_cmd
from .config import load_config
from .errors import ToolError, ValidationError
from .output import Output


class _ToolArgumentParser(argparse.ArgumentParser):
    """Turn argparse parse errors into JSON-able errors."""

    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def _parse_date(value: str) -> str:
    if not re.match(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$", value):
        raise ValidationError("start_date and end_date must be strict YYYY-MM-DD")
    try:
        dt = datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValidationError("start_date and end_date must be strict YYYY-MM-DD") from exc
    return dt.strftime("%Y-%m-%d")


def _validate_window(args: argparse.Namespace) -> None:
    start = _parse_date(args.start_date)
    end = _parse_date(args.end_date)
    if start > end:
        raise ValidationError("start_date must be <= end_date")
    args.start_date = start
    args.end_date = end


def _validate_optional_positive(name: str, value: str | None) -> int | None:
    if value is None:
        return None
    try:
        ivalue = int(value)
    except ValueError as exc:
        raise ValidationError(f"{name} must be a positive integer") from exc
    if ivalue <= 0:
        raise ValidationError(f"{name} must be > 0")
    return ivalue


def _output_mode_from_argv(argv: list[str]) -> str:
    try:
        idx = argv.index("--output")
    except ValueError:
        return "json"
    if idx + 1 >= len(argv):
        return "json"
    return argv[idx + 1] if argv[idx + 1] in {"json", "text"} else "json"


def _build_parser() -> argparse.ArgumentParser:
    parser = _ToolArgumentParser(prog="giantpanda")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    parser.add_argument("--env-file", default=".env", help="Path to .env file (default: .env)")
    parser.add_argument("--output", choices=("json", "text"), default="json", help="Output mode")
    parser.add_argument("--verbose", action="store_true", help="Verbose HTTP trace to stderr")

    sub = parser.add_subparsers(dest="command", required=False, parser_class=_ToolArgumentParser)

    sub.add_parser("onboarding", help="Create .env from .env.example").set_defaults(
        func=onboarding_cmd.cmd_onboarding, write_capable=False
    )

    auth = sub.add_parser("auth", help="Auth checks").add_subparsers(
        dest="auth_command",
        required=False,
        parser_class=_ToolArgumentParser,
    )
    auth.add_parser("check", help="Check local credential readiness").set_defaults(
        func=auth_cmd.cmd_auth_check,
        write_capable=False,
    )

    domains = sub.add_parser("domains", help="Domain operations").add_subparsers(
        dest="domains_command",
        required=False,
        parser_class=_ToolArgumentParser,
    )
    stats = domains.add_parser("stats", help="Read domain parking stats")
    stats.add_argument("--start-date", required=True, help="Start date YYYY-MM-DD")
    stats.add_argument("--end-date", required=True, help="End date YYYY-MM-DD")
    stats.add_argument("--page", required=False, default=None)
    stats.add_argument("--page-size", required=False, default=None, dest="page_size")
    stats.set_defaults(func=domains_cmd.cmd_domains_stats, write_capable=False)

    add = domains.add_parser("add", help="Prepare or apply a domain add plan")
    add.add_argument("--domain", action="append", help="Domain to add (repeatable)")
    add.add_argument("--plan-out", help="Write plan to this exact path")
    add.add_argument("--plan-in", help="Read plan from this exact path")
    add.add_argument(
        "--approve-plan",
        help="Exact plan id required to apply a prepared plan",
    )
    add.add_argument("--receipt-out", help="Write receipt to this exact path")
    mode = add.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Apply prepared plan")
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Prepare plan only (default)",
    )
    add.add_argument(
        "--ack-no-snapshot",
        action="store_true",
        help="Acknowledge no-snapshot and no-rollback execution",
    )
    add.set_defaults(func=domains_cmd.cmd_domains_add, write_capable=True)

    return parser


def build_parser() -> argparse.ArgumentParser:
    return _build_parser()


def main(argv: list[str]) -> int:
    parser = _build_parser()
    out = Output(mode=_output_mode_from_argv(argv))
    if _output_mode_from_argv(argv) == "json" and ("-h" in argv or "--help" in argv):
        out.emit({"ok": False, "error": "Help unavailable in JSON output", "error_type": "HelpRequested"})
        return 1
    try:
        args = parser.parse_args(argv)
    except ValidationError as exc:
        payload = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        out.emit(payload)
        return 1
    except SystemExit:
        # argparse uses SystemExit for `--help` and some parser-level errors.
        # Keep this path in JSON mode as a single JSON object.
        if _output_mode_from_argv(argv) == "json":
            payload = {"ok": False, "error": "Invalid command arguments", "error_type": "ValidationError"}
            out.emit(payload)
            return 1
        return 0

    if args.version:
        out.emit({"ok": True, "tool": "giantpanda", "version": __version__})
        return 0

    if not getattr(args, "command", None):
        out.emit({"ok": False, "error": "Missing command", "error_type": "ValidationError"})
        return 1

    if args.command == "auth" and not getattr(args, "auth_command", None):
        out.emit({"ok": False, "error": "Missing auth subcommand", "error_type": "ValidationError"})
        return 1

    if args.command == "domains" and not getattr(args, "domains_command", None):
        out.emit({"ok": False, "error": "Missing domains subcommand", "error_type": "ValidationError"})
        return 1

    if args.command == "domains" and args.domains_command == "stats":
        try:
            _validate_window(args)
            args.page = _validate_optional_positive("page", args.page)
            args.page_size = _validate_optional_positive("page_size", args.page_size)
        except ValidationError as exc:
            out.emit({"ok": False, "error": str(exc), "error_type": "ValidationError"})
            return 1
    if args.command == "onboarding":
        onboarding_ctx = {"out": out}
        try:
            return int(args.func(args, onboarding_ctx))
        except ToolError as exc:
            out.emit({"ok": False, "error": str(exc), "error_type": type(exc).__name__})
            return 1

    try:
        cfg = load_config(env_file=args.env_file)
        ctx: dict[str, object] = {"out": out, "cfg": cfg, "args": args, "env_file": args.env_file}
        return int(args.func(args, ctx))
    except ValidationError as exc:
        out.emit({"ok": False, "error": str(exc), "error_type": "ValidationError"})
        return 1
    except ToolError as exc:
        out.emit({"ok": False, "error": str(exc), "error_type": type(exc).__name__})
        return 1
    except Exception as exc:  # noqa: BLE001
        out.emit({"ok": False, "error": "Unexpected error", "error_type": type(exc).__name__})
        return 1


def main_cli(argv: list[str]) -> int:
    """Compatibility wrapper for __main__.py tests."""
    return main(argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
