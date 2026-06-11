from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger
from .commands import auth as auth_cmd
from .commands import browse as browse_cmd
from .commands import jobs as jobs_cmd
from .commands import link as link_cmd
from .commands import product as product_cmd
from .commands._shared import (
    PAAPI_MAX_BROWSE_NODE_IDS_PER_REQUEST,
    PAAPI_MAX_ITEM_IDS_PER_REQUEST,
    PAAPI_MAX_VARIATION_COUNT_PER_REQUEST,
    RESOURCE_PRESET_CHOICES,
)
from .config import load_config
from .output import Output
from .project_config import load_project_config


class ValidationError(Exception):
    pass


class _ToolArgumentParser(argparse.ArgumentParser):
    """
    Ensure user-input errors can be surfaced as JSON.

    Argparse defaults to printing usage/help to stderr and raising SystemExit, which makes it
    hard to keep the `--output json` contract (exactly one JSON object to stdout on errors).
    """

    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def build_parser() -> argparse.ArgumentParser:
    p = _ToolArgumentParser(prog="amazon-pa-api-tool")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument(
        "--config",
        default=None,
        help="Optional non-secret project config JSON (paths/defaults). Use for customer projects; do not store API keys here.",
    )
    p.add_argument(
        "--project-dir",
        default=None,
        help="Optional project root dir for outputs. If omitted and --config is provided, defaults to the config file's directory; otherwise defaults to the current working directory.",
    )
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    p.add_argument("--debug", action="store_true", help="Show stack traces on errors")
    p.add_argument("--output", choices=("json", "text"), default="json", help="Output format (default: json)")
    p.add_argument("--log-file", default=None, help="Optional audit log path (JSONL)")
    p.add_argument(
        "--include-raw",
        action="store_true",
        help="Include raw PA-API responses in output (default: false)",
    )
    p.add_argument("--apply", action="store_true", help="Apply changes (unused: all Amazon API calls are read-only)")
    p.add_argument("--yes", action="store_true", help="Additional confirmation for destructive/batch actions")
    p.add_argument(
        "--ack-no-snapshot",
        action="store_true",
        help="Acknowledge that this approved write may run without a saved before-state snapshot",
    )

    sub = p.add_subparsers(dest="cmd", required=False, parser_class=_ToolArgumentParser)

    def add_resources_args(cmd_p: argparse.ArgumentParser) -> None:
        cmd_p.add_argument(
            "--resources-preset",
            default=None,
            choices=RESOURCE_PRESET_CHOICES,
            help="Resource preset (default: tool default per command)",
        )
        cmd_p.add_argument(
            "--resource",
            action="append",
            default=None,
            help="PA-API resource name (repeatable; appended to preset deterministically)",
        )

    def add_batching_args(cmd_p: argparse.ArgumentParser, *, default_batch_size: int) -> None:
        cmd_p.add_argument(
            "--batch-size",
            type=int,
            default=default_batch_size,
            help=f"Max IDs per request (1-{default_batch_size}, default: {default_batch_size})",
        )
        cmd_p.add_argument(
            "--max-requests",
            type=int,
            default=10,
            help="Hard cap on requests allowed for batching (default: 10)",
        )

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Smoke test credentials")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check)

    product = sub.add_parser("product", help="Amazon product operations (PA-API v5)")
    product_sub = product.add_subparsers(dest="product_cmd", required=True, parser_class=_ToolArgumentParser)
    product_get = product_sub.add_parser("get", help="Fetch one or more ASINs")
    product_get.add_argument("--asin", action="append", required=True, help="ASIN (repeatable)")
    add_resources_args(product_get)
    add_batching_args(product_get, default_batch_size=PAAPI_MAX_ITEM_IDS_PER_REQUEST)
    product_get.set_defaults(func=product_cmd.cmd_product_get)

    product_search = product_sub.add_parser("search", help="Search products by keyword")
    product_search.add_argument("--query", required=True, help="Search keywords")
    product_search.add_argument("--search-index", default="All", help="Amazon SearchIndex (default: All)")
    product_search.add_argument("--limit", type=int, default=10, help="Max results (1-10, default: 10)")
    product_search.add_argument("--item-page", type=int, default=1, help="Result page (default: 1)")
    add_resources_args(product_search)
    product_search.set_defaults(func=product_cmd.cmd_product_search)

    product_variations = product_sub.add_parser("variations", help="Fetch variation items for an ASIN")
    product_variations.add_argument("--asin", required=True, help="ASIN")
    product_variations.add_argument(
        "--variation-page",
        type=int,
        default=1,
        help="Variations page number (default: 1)",
    )
    product_variations.add_argument(
        "--variation-count",
        type=int,
        default=PAAPI_MAX_VARIATION_COUNT_PER_REQUEST,
        help=f"Variations per page (1-{PAAPI_MAX_VARIATION_COUNT_PER_REQUEST}, default: {PAAPI_MAX_VARIATION_COUNT_PER_REQUEST})",
    )
    add_resources_args(product_variations)
    product_variations.set_defaults(func=product_cmd.cmd_product_variations)

    product_resolve = product_sub.add_parser("resolve", help="Extract ASIN from an Amazon URL")
    product_resolve.add_argument("--url", required=True, help="Amazon product URL")
    product_resolve.set_defaults(func=product_cmd.cmd_product_resolve)

    link = sub.add_parser("link", help="Affiliate link helpers")
    link_sub = link.add_subparsers(dest="link_cmd", required=True, parser_class=_ToolArgumentParser)
    link_build = link_sub.add_parser("build", help="Build a simple amazon.com affiliate link from ASIN")
    link_build.add_argument("--asin", required=True, help="ASIN")
    link_build.set_defaults(func=link_cmd.cmd_link_build)

    jobs = sub.add_parser("jobs", help="Batch operations from job files")
    jobs_sub = jobs.add_subparsers(dest="jobs_cmd", required=True, parser_class=_ToolArgumentParser)
    jobs_run = jobs_sub.add_parser("run", help="Run a CSV job file (read-only)")
    jobs_run.add_argument("--file", required=True, help="Job CSV file (must include action column)")
    jobs_run.add_argument("--limit", type=int, default=None, help="Max number of rows to process")
    jobs_run.set_defaults(func=jobs_cmd.cmd_jobs_run)

    browse = sub.add_parser("browse", help="Amazon browse node operations (PA-API v5)")
    browse_sub = browse.add_subparsers(dest="browse_cmd", required=True, parser_class=_ToolArgumentParser)
    browse_get = browse_sub.add_parser("get", help="Fetch one or more browse nodes by id")
    browse_get.add_argument("--browse-node-id", action="append", required=True, help="Browse node id (repeatable)")
    add_resources_args(browse_get)
    add_batching_args(browse_get, default_batch_size=PAAPI_MAX_BROWSE_NODE_IDS_PER_REQUEST)
    browse_get.set_defaults(func=browse_cmd.cmd_browse_get)

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
        if _output_mode_from_argv(argv) == "json":
            out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
            return 1
        print(str(e), file=sys.stderr)
        return 2
    except SystemExit as e:
        try:
            return int(e.code or 0)
        except Exception:
            return 0

    out = Output(mode=args.output)
    audit = AuditLogger(path=args.log_file, enabled=bool(args.log_file))

    try:
        if bool(args.version):
            payload = {"ok": True, "tool": "amazon-pa-api-tool", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"amazon-pa-api-tool {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            msg = "Missing command. Use --help to see available commands."
            if args.output == "json":
                out.emit({"ok": False, "error": msg, "error_type": "ValidationError"})
                return 1
            print(msg, file=sys.stderr)
            return 2

        project_cfg, cfg_base_dir = load_project_config(getattr(args, "config", None))
        project_dir = Path(str(getattr(args, "project_dir", "") or "")).expanduser()
        if not str(getattr(args, "project_dir", "") or "").strip():
            project_dir = cfg_base_dir or Path.cwd()
        project_dir = project_dir.resolve()

        cfg = load_config(args.env_file)
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "env_file": str(args.env_file),
            "timeout_s": timeout_s,
            "verbose": bool(args.verbose),
            "apply": bool(args.apply),
            "yes": bool(args.yes),
            "ack_no_snapshot": bool(args.ack_no_snapshot),
            "include_raw": bool(args.include_raw),
            "user_agent": f"amazon-pa-api-tool/{__version__}",
            "project_cfg": project_cfg,
            "project_dir": str(project_dir),
        }
        return int(args.func(args, ctx))
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    except ValidationError as e:
        audit.write("error", {"error": str(e), "error_type": type(e).__name__})
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        return 1
    except Exception as e:  # noqa: BLE001
        if bool(args.debug):
            raise
        audit.write("error", {"error": str(e), "error_type": type(e).__name__})
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        return 1
    finally:
        audit.close()
