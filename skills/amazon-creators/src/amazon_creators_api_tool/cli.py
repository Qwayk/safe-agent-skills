from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import auth as auth_cmd
from .commands import catalog as catalog_cmd
from .commands import locales as locales_cmd
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


def _credential_secret_from_ctx(ctx: dict[str, Any]) -> str | None:
    cfg = ctx.get("cfg")
    if not cfg:
        return None
    secret = getattr(cfg, "credential_secret", None)
    return secret if secret else None


def _redact_secret_value(text: str, secret: str | None) -> str:
    if not secret:
        return text
    return text.replace(secret, "***REDACTED***")


def _sanitize_exception_args(exc: BaseException, secret: str | None) -> None:
    if not secret:
        return
    sanitized = [_redact_secret_value(str(arg), secret) for arg in exc.args]
    exc.args = tuple(sanitized)


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


def build_parser() -> argparse.ArgumentParser:
    p = _ToolArgumentParser(prog="amazon-creators-api-tool")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--config", default=None, help="Optional project defaults JSON (non-secret)")
    p.add_argument("--project-dir", default=None, help="Optional project directory (defaults to config file folder)")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    p.add_argument("--debug", action="store_true", help="Show stack traces on errors")
    p.add_argument("--output", choices=("json", "text"), default="json", help="Output format (default: json)")
    p.add_argument("--log-file", default=None, help="Optional audit log path (JSONL)")
    p.add_argument("--apply", action="store_true", help="Run live catalog reads or attempt local write helpers (default is dry-run)")
    p.add_argument("--yes", action="store_true", help="Additional confirmation for destructive/batch actions")
    p.add_argument(
        "--ack-no-snapshot",
        action="store_true",
        help="Acknowledge that this approved write may run without a saved before-state snapshot",
    )
    p.add_argument("--plan-out", default=None, help="Write a dry-run plan JSON to a file")
    p.add_argument("--plan-in", default=None, help="Reserved for future apply-from-plan flows")
    p.add_argument("--receipt-out", default=None, help="Write a receipt JSON only when a real catalog read apply succeeds")
    p.add_argument(
        "--ack-irreversible",
        action="store_true",
        help="Extra acknowledgement for irreversible actions",
    )
    p.add_argument("--run-id", default=None, help="Optional run id (for run history/audit)")
    p.add_argument("--artifacts-dir", default=None, help="Optional artifacts directory for this run")
    p.add_argument("--no-artifacts", action="store_true", help="Disable writing local run artifacts")
    p.add_argument(
        "--resource",
        action="append",
        dest="resources",
        help="Request a high-level resource (repeatable, comma-separated).",
    )
    p.add_argument(
        "--resource-preset",
        action="append",
        dest="resource_preset",
        help="Use a resource preset (book-media, browse-basic, search-lens, inventory-view, full).",
    )
    p.add_argument("--locale", default=None, help="Override the marketplace locale (zone code).")
    p.add_argument(
        "--include-raw",
        action="store_true",
        help="Include the raw API payload (use sparingly).",
    )

    sub = p.add_subparsers(dest="cmd", required=False, parser_class=_ToolArgumentParser)

    runs = sub.add_parser("runs", help="Run history (local)")
    runs_sub = runs.add_subparsers(dest="runs_cmd", required=True, parser_class=_ToolArgumentParser)
    runs_list = runs_sub.add_parser("list", help="List recent runs")
    runs_list.add_argument("--limit", type=int, default=20, help="Max runs to return (default: 20)")
    runs_list.set_defaults(func=_cmd_runs_list, write_capable=False)
    runs_show = runs_sub.add_parser("show", help="Show one run from the index")
    runs_show.set_defaults(func=_cmd_runs_show, write_capable=False)

    onboarding = sub.add_parser("onboarding", help="First-time setup help (no secrets)")
    onboarding.add_argument(
        "--no-write-env",
        action="store_true",
        help="Do not write/update the env file; print instructions only",
    )
    onboarding.set_defaults(func=onboarding_cmd.cmd_onboarding, write_capable=True)

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Smoke test credentials")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=True)

    token = auth_sub.add_parser("token", help="OAuth token helpers")
    token_sub = token.add_subparsers(dest="token_cmd", required=True, parser_class=_ToolArgumentParser)
    token_set = token_sub.add_parser("set", help="Plan token storage; live local write is not implemented in this command")
    token_set.add_argument("--file", required=True, help="Token JSON file path (input)")
    token_set.set_defaults(func=auth_cmd.cmd_auth_token_set, write_capable=True)
    token_fetch = token_sub.add_parser(
        "fetch",
        help="Plan token fetch; live token fetch/write is not implemented in this command",
    )
    token_fetch.add_argument("--force", action="store_true", help="Refresh even if a cached token exists")
    token_fetch.set_defaults(func=auth_cmd.cmd_auth_token_fetch, write_capable=True)
    token_status = token_sub.add_parser("status", help="Show token status (never prints token values)")
    token_status.set_defaults(func=auth_cmd.cmd_auth_token_status, write_capable=False)

    browse_nodes = sub.add_parser("browse-nodes", help="Browse node catalog operations")
    browse_nodes_sub = browse_nodes.add_subparsers(dest="browse_nodes_cmd", required=True, parser_class=_ToolArgumentParser)
    browse_nodes_describe = browse_nodes_sub.add_parser("describe", help="Call GetBrowseNodes")
    browse_nodes_describe.add_argument(
        "--browse-node-id",
        action="append",
        dest="browse_node_id",
        required=True,
        help="Browse node ID (repeatable).",
    )
    browse_nodes_describe.set_defaults(func=catalog_cmd.cmd_browse_nodes, write_capable=True)

    items = sub.add_parser("items", help="Item catalog operations")
    items_sub = items.add_subparsers(dest="items_cmd", required=True, parser_class=_ToolArgumentParser)
    items_get = items_sub.add_parser("get", help="Call GetItems")
    items_get.add_argument(
        "--item-id",
        action="append",
        required=True,
        help="Item ID (ASIN / SKU).",
    )
    items_get.add_argument("--item-id-type", default="ASIN", help="Item ID type (default: ASIN).")
    items_get.set_defaults(func=catalog_cmd.cmd_items, write_capable=True)

    variations = sub.add_parser("variations", help="Variation catalog operations")
    variations_sub = variations.add_subparsers(dest="variations_cmd", required=True, parser_class=_ToolArgumentParser)
    variations_get = variations_sub.add_parser("get", help="Call GetVariations")
    variations_get.add_argument(
        "--asin",
        "--item-id",
        action="append",
        dest="asin",
        required=True,
        help="ASIN (repeatable; only the first is used). `--item-id` is accepted as an alias.",
    )
    variations_get.add_argument(
        "--variation-page",
        type=int,
        default=1,
        help="Page of variations (default: 1).",
    )
    variations_get.add_argument(
        "--variation-count",
        type=int,
        default=10,
        help="Variations per page (1-10, default: 10).",
    )
    variations_get.set_defaults(func=catalog_cmd.cmd_variations, write_capable=True)

    search = sub.add_parser("search", help="Catalog search operation")
    search.add_argument("--keywords", required=True, help="Search keywords.")
    search.add_argument(
        "--item-count",
        "--max-results",
        dest="item_count",
        type=int,
        default=10,
        help="Items per page (1-10, default: 10). `--max-results` is accepted as an alias.",
    )
    search.add_argument(
        "--item-page",
        "--page",
        dest="item_page",
        type=int,
        default=1,
        help="Page of items (1-10, default: 1). `--page` is accepted as an alias.",
    )
    search.set_defaults(func=catalog_cmd.cmd_search, write_capable=True)

    locales = sub.add_parser("locales", help="Locale reference helpers")
    locales_sub = locales.add_subparsers(dest="locales_cmd", required=True, parser_class=_ToolArgumentParser)
    locales_list = locales_sub.add_parser("list", help="List supported locales")
    locales_list.set_defaults(func=locales_cmd.cmd_locales_list, write_capable=False)
    locales_show = locales_sub.add_parser("show", help="Show one locale")
    locales_show.add_argument("--locale", required=True, help="Locale code to explain.")
    locales_show.set_defaults(func=locales_cmd.cmd_locales_show, write_capable=False)

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

_REQUIRED_GLOBAL_FLAG_SPECS: tuple[tuple[str, bool], ...] = (
    ("--version", False),
    ("--config", True),
    ("--project-dir", True),
    ("--env-file", True),
    ("--timeout-s", True),
    ("--verbose", False),
    ("--debug", False),
    ("--output", True),
    ("--log-file", True),
    ("--apply", False),
    ("--yes", False),
    ("--plan-out", True),
    ("--plan-in", True),
    ("--receipt-out", True),
    ("--ack-irreversible", False),
    ("--run-id", True),
    ("--artifacts-dir", True),
    ("--no-artifacts", False),
    ("--resource", True),
    ("--resource-preset", True),
    ("--locale", True),
    ("--include-raw", False),
)
_GLOBAL_FLAG_SPECS = _REQUIRED_GLOBAL_FLAG_SPECS
_GLOBAL_FLAG_NAMES = {flag for flag, _ in _GLOBAL_FLAG_SPECS}
_GLOBAL_FLAGS_WITH_VALUE = {flag for flag, needs_value in _GLOBAL_FLAG_SPECS if needs_value}
_REQUIRED_GLOBAL_FLAG_NAMES = {flag for flag, _ in _REQUIRED_GLOBAL_FLAG_SPECS}
_REQUIRED_GLOBAL_FLAGS_WITH_VALUE = {flag for flag, needs_value in _REQUIRED_GLOBAL_FLAG_SPECS if needs_value}
_MISSING_NORMALIZER_FLAGS = _REQUIRED_GLOBAL_FLAG_NAMES - _GLOBAL_FLAG_NAMES
if _MISSING_NORMALIZER_FLAGS:
    raise RuntimeError(
        "CLI global flag normalizer lacks these expected flags: "
        f"{sorted(_MISSING_NORMALIZER_FLAGS)}"
    )
_MISSING_VALUE_FLAGS = _REQUIRED_GLOBAL_FLAGS_WITH_VALUE - _GLOBAL_FLAGS_WITH_VALUE
if _MISSING_VALUE_FLAGS:
    raise RuntimeError(
        "CLI global flag normalizer mis-classified these flags as flag-only: "
        f"{sorted(_MISSING_VALUE_FLAGS)}"
    )

def _collect_global_flag_metadata(parser: argparse.ArgumentParser) -> tuple[set[str], set[str]]:
    global_flags: set[str] = set()
    global_flags_with_value: set[str] = set()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            break
        for option in action.option_strings:
            if not option.startswith("--") or option == "--help":
                continue
            global_flags.add(option)
            nargs = getattr(action, "nargs", None)
            if nargs == 0:
                continue
            global_flags_with_value.add(option)
    global_flags.update(_GLOBAL_FLAG_NAMES)
    global_flags_with_value.update(_GLOBAL_FLAGS_WITH_VALUE)
    return global_flags_with_value, global_flags


def _split_option_and_value(arg: str) -> tuple[str, bool]:
    if arg.startswith("--") and "=" in arg:
        flag, _ = arg.split("=", 1)
        return flag, True
    return arg, False


def _normalize_global_flags(
    argv: list[str],
    global_flags: set[str],
    global_flags_with_value: set[str],
) -> list[str]:
    global_flags = set(global_flags) | _GLOBAL_FLAG_NAMES
    global_flags_with_value = set(global_flags_with_value) | _GLOBAL_FLAGS_WITH_VALUE
    normalized: list[str] = []
    rest: list[str] = []
    idx = 0
    command_tokens: list[str] = []
    in_locales_show = False
    while idx < len(argv):
        arg = argv[idx]
        if arg == "--":
            rest.append(arg)
            rest.extend(argv[idx + 1 :])
            break
        if not arg.startswith("-") or arg == "":
            command_tokens.append(arg)
            if command_tokens[-2:] == ["locales", "show"]:
                in_locales_show = True
            rest.append(arg)
            idx += 1
            continue
        flag, has_inline_value = _split_option_and_value(arg)
        if in_locales_show and flag == "--locale":
            rest.append(arg)
            idx += 1
            if flag in global_flags_with_value and not has_inline_value and idx < len(argv):
                rest.append(argv[idx])
                idx += 1
            continue
        if flag in global_flags:
            normalized.append(arg)
            if flag in global_flags_with_value and not has_inline_value:
                if idx + 1 < len(argv):
                    normalized.append(argv[idx + 1])
                    idx += 1
            idx += 1
            continue
        rest.append(arg)
        idx += 1
    else:
        idx = len(argv)
    return normalized + rest


def main(argv: list[str]) -> int:
    parser = build_parser()
    global_flags_with_value, global_flags = _collect_global_flag_metadata(parser)
    normalized_argv = _normalize_global_flags(argv, global_flags, global_flags_with_value)
    out = Output(mode=_output_mode_from_argv(argv))
    ctx: dict[str, Any] = {"cfg": None}
    try:
        args = parser.parse_args(normalized_argv)
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
            payload = {"ok": True, "tool": "amazon-creators-api-tool", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"amazon-creators-api-tool {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        command_str = "amazon-creators-api-tool " + " ".join(argv)
        audit.bind_context(
            {
                "tool": "amazon-creators-api-tool",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "env_fingerprint": None,
                "run_id": run_ctx.run_id,
            }
        )

        # Some commands are local-only and don't need API config.
        if str(getattr(args, "cmd", "") or "") in {"runs", "onboarding", "locales"}:
            ctx = {
                "cfg": None,
                "out": out,
                "audit": audit,
                "tool": "amazon-creators-api-tool",
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
            rc = int(args.func(args, ctx))
            if run_ctx.enabled and run_ctx.artifacts_dir:
                _finalize_run_artifacts(
                    run_ctx=run_ctx,
                    tool="amazon-creators-api-tool",
                    version=__version__,
                    command=command_str,
                    env_fingerprint=None,
                    output_obj=out.last if isinstance(out.last, dict) else None,
                    audit_log_path=run_audit_log_path or global_audit_log_path,
                    audit_log_global_path=global_audit_log_path,
                    apply=bool(args.apply),
                    yes=bool(args.yes),
                )
            return rc

        cfg = load_config(args.env_file)
        env_fingerprint = cfg.base_url
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "tool": "amazon-creators-api-tool",
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
                "tool": "amazon-creators-api-tool",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "env_fingerprint": cfg.base_url,
                "run_id": run_ctx.run_id,
            }
        )
        rc = int(args.func(args, ctx))

        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="amazon-creators-api-tool",
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
            tool="amazon-creators-api-tool",
            version=__version__,
            command="amazon-creators-api-tool " + " ".join(argv),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 0
    except ToolError as e:
        secret = _credential_secret_from_ctx(ctx)
        error_text = _redact_secret_value(str(e), secret)
        audit.write("error", {"error": error_text, "error_type": type(e).__name__})
        out.emit({"ok": False, "error": error_text, "error_type": type(e).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="amazon-creators-api-tool",
            version=__version__,
            command="amazon-creators-api-tool " + " ".join(argv),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 1
    except Exception as e:  # noqa: BLE001
        secret = _credential_secret_from_ctx(ctx)
        if bool(args.debug):
            _sanitize_exception_args(e, secret)
            raise
        error_text = _redact_secret_value(str(e), secret)
        audit.write("error", {"error": error_text, "error_type": type(e).__name__})
        out.emit({"ok": False, "error": error_text, "error_type": type(e).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="amazon-creators-api-tool",
            version=__version__,
            command="amazon-creators-api-tool " + " ".join(argv),
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
