from __future__ import annotations

import argparse
import sys

from . import __version__
from .audit_log import AuditLogger
from .commands import auth as auth_cmd
from .commands import meals as meals_cmd
from .commands import onboarding as onboarding_cmd
from .config import load_config
from .errors import ToolError, ValidationError
from .http import HttpClient
from .output import Output


class _ToolArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def build_parser() -> argparse.ArgumentParser:
    parser = _ToolArgumentParser(prog="qwayk-themealdb-safe-agent-cli")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    parser.add_argument("--config", default=None, help="Optional project defaults JSON (non-secret)")
    parser.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    parser.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    parser.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    parser.add_argument("--debug", action="store_true", help="Show stack traces on errors")
    parser.add_argument("--output", choices=("json", "text"), default="json", help="Output format (default: json)")
    parser.add_argument("--log-file", default=None, help="Optional audit log path (JSONL)")

    sub = parser.add_subparsers(dest="cmd", required=False, parser_class=_ToolArgumentParser)

    onboarding = sub.add_parser("onboarding", help="First-time setup help (no secrets)")
    onboarding.add_argument(
        "--no-write-env",
        action="store_true",
        help="Do not write/update the env file; print instructions only",
    )
    onboarding.set_defaults(func=onboarding_cmd.cmd_onboarding)

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Read-only API connection check")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check)

    categories = sub.add_parser("categories", help="List full category records")
    categories.set_defaults(func=meals_cmd.cmd_categories)

    random = sub.add_parser("random", help="Fetch one random meal")
    random.set_defaults(func=meals_cmd.cmd_random)

    search = sub.add_parser("search", help="Search meals")
    search_sub = search.add_subparsers(dest="search_cmd", required=True, parser_class=_ToolArgumentParser)
    search_name = search_sub.add_parser("name", help="Search meals by full name")
    search_name.add_argument("--name", required=True, help="Meal name to search for")
    search_name.set_defaults(func=meals_cmd.cmd_search_name)
    search_letter = search_sub.add_parser("first-letter", help="Search meals by first letter")
    search_letter.add_argument("--letter", required=True, help="One letter")
    search_letter.set_defaults(func=meals_cmd.cmd_search_first_letter)

    lookup = sub.add_parser("lookup", help="Lookup one meal")
    lookup_sub = lookup.add_subparsers(dest="lookup_cmd", required=True, parser_class=_ToolArgumentParser)
    lookup_id = lookup_sub.add_parser("id", help="Lookup full meal details by ID")
    lookup_id.add_argument("--meal-id", required=True, help="Meal ID")
    lookup_id.set_defaults(func=meals_cmd.cmd_lookup_id)

    list_cmd = sub.add_parser("list", help="List names or records")
    list_sub = list_cmd.add_subparsers(dest="list_cmd", required=True, parser_class=_ToolArgumentParser)
    list_categories = list_sub.add_parser("categories", help="List category names")
    list_categories.set_defaults(func=meals_cmd.cmd_list_categories)
    list_areas = list_sub.add_parser("areas", help="List areas")
    list_areas.set_defaults(func=meals_cmd.cmd_list_areas)
    list_ingredients = list_sub.add_parser("ingredients", help="List ingredients")
    list_ingredients.set_defaults(func=meals_cmd.cmd_list_ingredients)

    filter_cmd = sub.add_parser("filter", help="Filter meals by one field")
    filter_sub = filter_cmd.add_subparsers(dest="filter_cmd", required=True, parser_class=_ToolArgumentParser)
    filter_ingredient = filter_sub.add_parser("ingredient", help="Filter meals by ingredient")
    filter_ingredient.add_argument("--ingredient", required=True, help="Ingredient name")
    filter_ingredient.set_defaults(func=meals_cmd.cmd_filter_ingredient)
    filter_category = filter_sub.add_parser("category", help="Filter meals by category")
    filter_category.add_argument("--category", required=True, help="Category name")
    filter_category.set_defaults(func=meals_cmd.cmd_filter_category)
    filter_area = filter_sub.add_parser("area", help="Filter meals by area")
    filter_area.add_argument("--area", required=True, help="Area or country value")
    filter_area.set_defaults(func=meals_cmd.cmd_filter_area)

    return parser


def _output_mode_from_argv(argv: list[str]) -> str:
    try:
        index = argv.index("--output")
    except ValueError:
        return "json"
    if index + 1 >= len(argv):
        return "json"
    value = str(argv[index + 1] or "").strip()
    return value if value in {"json", "text"} else "json"


def _build_context(args: argparse.Namespace, argv: list[str], out: Output) -> dict:
    cfg = load_config(
        str(getattr(args, "env_file", ".env")),
        config_file=str(getattr(args, "config", "") or "") or None,
        timeout_override=getattr(args, "timeout_s", None),
    )
    audit = AuditLogger(path=str(getattr(args, "log_file", "") or "") or None, enabled=bool(args.log_file))
    http = HttpClient(
        timeout_s=cfg.timeout_s,
        verbose=bool(getattr(args, "verbose", False)),
        user_agent=f"qwayk-themealdb-safe-agent-cli/{__version__}",
        redacted_values=(() if cfg.api_key == "1" else (cfg.api_key,)),
    )
    command_str = "qwayk-themealdb-safe-agent-cli " + " ".join(argv)
    audit.bind_context(
        {
            "tool": "qwayk-themealdb-safe-agent-cli",
            "version": __version__,
            "command": command_str,
            "output": getattr(args, "output", "json"),
            "api_key_mode": "default_public_key" if cfg.api_key == "1" else "custom_key",
        }
    )
    return {
        "cfg": cfg,
        "http": http,
        "out": out,
        "audit": audit,
        "env_file": str(getattr(args, "env_file", ".env")),
        "tool": "qwayk-themealdb-safe-agent-cli",
        "command": command_str,
    }


def main(argv: list[str]) -> int:
    parser = build_parser()
    out = Output(mode=_output_mode_from_argv(argv))
    out.set_provenance({"tool": "qwayk-themealdb-safe-agent-cli", "version": __version__})
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

    if args.version:
        out.emit({"ok": True, "version": __version__})
        return 0

    if not getattr(args, "func", None):
        out.emit({"ok": False, "error": "Missing command", "error_type": "ValidationError"})
        return 1

    audit: AuditLogger | None = None
    try:
        ctx = _build_context(args, argv, out)
        audit = ctx["audit"]
        return int(args.func(args, ctx) or 0)
    except ToolError as exc:
        payload = {"ok": False, "error": str(exc), "error_type": type(exc).__name__}
        if audit:
            audit.write("error", payload)
        out.emit(payload)
        return 1
    except Exception as exc:
        if getattr(args, "debug", False):
            raise
        payload = {"ok": False, "error": str(exc), "error_type": type(exc).__name__}
        if audit:
            audit.write("error", payload)
        out.emit(payload)
        return 1
    finally:
        if audit:
            audit.close()
