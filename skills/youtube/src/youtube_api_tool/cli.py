from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import api as api_cmd
from .commands import auth as auth_cmd
from .commands import channels as channels_cmd
from .commands import demo as demo_cmd
from .commands import jobs as jobs_cmd
from .commands import methods as methods_cmd
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

    def __init__(self, *args: object, **kwargs: object) -> None:
        # Determinism: with hundreds of subcommands, abbreviations become ambiguous and unsafe.
        kwargs.setdefault("allow_abbrev", False)
        super().__init__(*args, **kwargs)

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


def build_parser() -> argparse.ArgumentParser:
    p = _ToolArgumentParser(prog="youtube-api-tool")
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
    p.add_argument("--yes", action="store_true", help="Additional confirmation for destructive/batch actions")
    p.add_argument(
        "--ack-no-snapshot",
        action="store_true",
        help="Acknowledge that this approved write may run without a saved before-state snapshot",
    )
    p.add_argument("--plan-out", default=None, help="Write a dry-run plan JSON to a file")
    p.add_argument("--plan-in", default=None, help="Apply from an existing plan JSON file (high-risk writes)")
    p.add_argument("--receipt-out", default=None, help="Write a receipt JSON only when a real apply succeeds")
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
    auth_check = auth_sub.add_parser("check", help="Smoke test credentials")
    auth_check.add_argument(
        "--live",
        action="store_true",
        help="Optional: attempt a minimal live check (may require network; not used in tests)",
    )
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=False)

    auth_login = auth_sub.add_parser("login", help="Plan OAuth login; live local token write is not implemented in this command")
    auth_login.add_argument(
        "--client-secrets-file",
        default=None,
        help="Path to Google OAuth client secrets JSON (overrides YOUTUBE_OAUTH_CLIENT_SECRETS_FILE)",
    )
    auth_login.add_argument(
        "--scopes",
        default=None,
        help="OAuth scopes (space or comma separated; overrides YOUTUBE_OAUTH_SCOPES)",
    )
    auth_login.add_argument(
        "--console",
        action="store_true",
        help="Use console flow (recommended for headless environments)",
    )
    auth_login.add_argument(
        "--port",
        type=int,
        default=0,
        help="Local server port (0 = auto). Ignored when --console is set.",
    )
    auth_login.set_defaults(func=auth_cmd.cmd_auth_login, write_capable=True)

    token = auth_sub.add_parser("token", help="OAuth token helpers")
    token_sub = token.add_subparsers(dest="token_cmd", required=True, parser_class=_ToolArgumentParser)
    token_set = token_sub.add_parser("set", help="Plan token storage; live local token write is not implemented in this command")
    token_set.add_argument("--file", required=True, help="Token JSON file path (input)")
    token_set.set_defaults(func=auth_cmd.cmd_auth_token_set, write_capable=True)
    token_status = token_sub.add_parser("status", help="Show token status (never prints token values)")
    token_status.set_defaults(func=auth_cmd.cmd_auth_token_status, write_capable=False)
    token_show_safe = token_sub.add_parser("show-safe", help="Show a redacted view of token.json (never prints token values)")
    token_show_safe.set_defaults(func=auth_cmd.cmd_auth_token_show_safe, write_capable=False)

    methods = sub.add_parser("methods", help="Discovery snapshot helpers (local; no network)")
    methods_sub = methods.add_subparsers(dest="methods_cmd", required=True, parser_class=_ToolArgumentParser)
    methods_list = methods_sub.add_parser("list", help="List all discovery methods (pinned snapshot)")
    methods_list.add_argument("--resource", default=None, help="Optional resource prefix filter (example: search)")
    methods_list.set_defaults(func=methods_cmd.cmd_methods_list, write_capable=False)

    def _add_api_request_building_flags(ap: argparse.ArgumentParser) -> None:
        ap.add_argument(
            "--live",
            action="store_true",
            help="Execute live reads for GET methods without --apply (default is plan-only)",
        )
        ap.add_argument(
            "--paginate",
            action="store_true",
            help="For GET list methods: follow nextPageToken until exhaustion (requires --live; capped by --max-pages)",
        )
        ap.add_argument(
            "--max-pages",
            type=int,
            default=5,
            help="Max pages when using --paginate (default: 5)",
        )
        ap.add_argument("--params-json", default=None, help="Query/path params as JSON object")
        ap.add_argument("--params-file", default=None, help="Query/path params JSON file (object)")
        ap.add_argument("--body-json", default=None, help="Request body as JSON")
        ap.add_argument("--body-file", default=None, help="Request body JSON file")
        ap.add_argument("--body-stdin", action="store_true", help="Read request body JSON from stdin")
        ap.add_argument("--upload-file", default=None, help="Path to media file for mediaUpload methods (example: videos.insert)")
        ap.add_argument(
            "--upload-protocol",
            choices=("simple", "resumable"),
            default="simple",
            help="Upload protocol for mediaUpload methods (default: simple)",
        )
        ap.add_argument("--upload-mime", default=None, help="Override upload MIME type (optional)")
        ap.add_argument(
            "--download-to",
            default=None,
            help="For supportsMediaDownload GET methods (example: captions.download): save the response body to this file path",
        )
        ap.add_argument(
            "--download-overwrite",
            action="store_true",
            help="Allow overwriting an existing --download-to file (or use global --yes)",
        )

    api = sub.add_parser(
        "api",
        help="YouTube Data API requests (pinned discovery; explicit per-method commands)",
    )
    api_sub = api.add_subparsers(dest="api_cmd", required=True, parser_class=_ToolArgumentParser)
    from .youtube_discovery import tool_root_dir, extract_method_metadata, load_official_discovery_doc

    root = tool_root_dir()
    methods_txt = root / "docs" / "official_methods.txt"
    if not methods_txt.exists():
        raise RuntimeError(f"Missing docs/official_methods.txt: {methods_txt}")
    methods = [ln.strip() for ln in methods_txt.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not methods:
        raise RuntimeError("No methods found in docs/official_methods.txt")

    discovery = load_official_discovery_doc()
    meta = extract_method_metadata(discovery_obj=discovery)

    for mid in methods:
        m = meta.get(mid)
        suffix = ""
        if m and m.http_method and m.path:
            suffix = f"{m.http_method.upper()} {m.path}"
        mp = api_sub.add_parser(mid, help=suffix or "Pinned discovery method")
        _add_api_request_building_flags(mp)
        mp.set_defaults(func=api_cmd.cmd_api_call, write_capable=True, api_method_id=mid)

    channels = sub.add_parser("channels", help="Channel helpers (official-only)")
    channels_sub = channels.add_subparsers(dest="channels_cmd", required=True, parser_class=_ToolArgumentParser)
    channels_resolve = channels_sub.add_parser("resolve", help="Resolve a channel from common inputs (plan-first)")
    channels_resolve.add_argument(
        "--channel",
        required=True,
        help="Channel identifier (channelId/URL/@handle/user URL/custom URL/plain text)",
    )
    channels_resolve.add_argument(
        "--live",
        action="store_true",
        help="Execute official API reads (default is plan-only)",
    )
    channels_resolve.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Max candidates for search fallback (default: 5)",
    )
    channels_resolve.add_argument(
        "--pick",
        type=int,
        default=None,
        help="When multiple candidates exist, pick 1-based index to select exactly one",
    )
    channels_resolve.set_defaults(func=channels_cmd.cmd_channels_resolve, write_capable=True)

    channels_export = channels_sub.add_parser("export", help="Export an analysis-ready dataset of channel videos (plan-first)")
    channels_export.add_argument(
        "--channel",
        required=True,
        help="Channel identifier (channelId/URL/@handle/user URL/custom URL/plain text)",
    )
    channels_export.add_argument("--out-dir", required=True, help="Output directory for the dataset")
    channels_export.add_argument(
        "--live",
        action="store_true",
        help="Execute official API reads and write the dataset (default is plan-only)",
    )
    channels_export.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting output files in an existing directory (or use global --yes)",
    )
    channels_export.add_argument(
        "--resume",
        action="store_true",
        help="Resume from an existing checkpoint in --out-dir",
    )
    channels_export.add_argument(
        "--max-pages",
        type=int,
        default=2000,
        help="Max playlistItems pages to fetch (default: 2000)",
    )
    channels_export.add_argument(
        "--video-parts",
        default="snippet,contentDetails,statistics",
        help="videos.list part value (default: snippet,contentDetails,statistics)",
    )
    channels_export.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Max candidates for search fallback during resolution (default: 5)",
    )
    channels_export.add_argument(
        "--pick",
        type=int,
        default=None,
        help="When multiple resolution candidates exist, pick 1-based index to select exactly one",
    )
    channels_export.set_defaults(func=channels_cmd.cmd_channels_export, write_capable=True)

    jobs = sub.add_parser("jobs", help="Batch operations from job files")
    jobs_sub = jobs.add_subparsers(dest="jobs_cmd", required=True, parser_class=_ToolArgumentParser)
    jobs_run = jobs_sub.add_parser("run", help="Run a CSV job file (demo actions)")
    jobs_run.add_argument("--file", required=False, help="Job CSV file (must include action column)")
    jobs_run.add_argument("--limit", type=int, default=None, help="Max number of rows to process")
    jobs_run.set_defaults(func=jobs_cmd.cmd_jobs_run, write_capable=True)

    demo = sub.add_parser("demo", help="Demo commands that show the plan/refusal workflow")
    demo_sub = demo.add_subparsers(dest="demo_cmd", required=True, parser_class=_ToolArgumentParser)
    demo_read = demo_sub.add_parser("read", help="Safe read (demo)")
    demo_read.set_defaults(func=demo_cmd.cmd_demo_read, write_capable=False)
    demo_write = demo_sub.add_parser("write", help="Write plan/refusal demo")
    demo_write.add_argument("--selector", default="demo-resource", help="Target selector (demo)")
    demo_write.set_defaults(func=demo_cmd.cmd_demo_write, write_capable=True)

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
            "artifacts_dir": str(run_ctx.artifacts_dir) if run_ctx.artifacts_dir else None,
            "runs_index": str(run_ctx.runs_index_path) if run_ctx.runs_index_path else str(runs_index_path),
            "audit_log": run_audit_log_path or global_audit_log_path,
            "audit_log_global": global_audit_log_path,
        }
    )

    try:
        if bool(args.version):
            payload = {"ok": True, "tool": "youtube-api-tool", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"youtube-api-tool {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        command_str = "youtube-api-tool " + " ".join(argv)
        audit.bind_context(
            {
                "tool": "youtube-api-tool",
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
        if str(getattr(args, "cmd", "") or "") in {"runs", "onboarding", "methods"}:
            ctx = {
                "cfg": None,
                "out": out,
                "audit": audit,
                "tool": "youtube-api-tool",
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
            return rc

        cfg = load_config(args.env_file)
        env_fingerprint = cfg.base_url
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "tool": "youtube-api-tool",
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
                "tool": "youtube-api-tool",
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
            tool="youtube-api-tool",
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
            tool="youtube-api-tool",
            version=__version__,
            command="youtube-api-tool " + " ".join(argv),
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
            tool="youtube-api-tool",
            version=__version__,
            command="youtube-api-tool " + " ".join(argv),
            env_fingerprint=None,
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
            tool="youtube-api-tool",
            version=__version__,
            command="youtube-api-tool " + " ".join(argv),
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
