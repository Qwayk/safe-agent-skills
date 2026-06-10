from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import auth as auth_cmd
from .commands import history as history_cmd
from .commands import models as models_cmd
from .commands import onboarding as onboarding_cmd
from .commands import tts as tts_cmd
from .commands import usage as usage_cmd
from .commands import voices as voices_cmd
from .commands.operation_runner import register_operation_commands
from .config import load_config
from .project_config import load_project_config
from .errors import SafetyError, ToolError, ValidationError
from .output import Output
from .http import HttpClient
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
    p = _ToolArgumentParser(prog="elevenlabs-api-tool")
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
    p.add_argument("--receipt-out", default=None, help="Write an apply receipt JSON to a file")
    p.add_argument(
        "--ack-irreversible",
        action="store_true",
        help="Extra acknowledgement for irreversible actions",
    )
    p.add_argument(
        "--live",
        action="store_true",
        help="Allow live API calls (off by default)",
    )
    p.add_argument(
        "--ack-spend-money",
        action="store_true",
        help="Acknowledgement required for spend-money operations",
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
    auth_check.add_argument("--out", help="JSON file for live auth output")
    auth_check.add_argument("--overwrite", action="store_true", help="Overwrite existing output file")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=True)

    voices = sub.add_parser("voices", help="Workspace voice inventory")
    voices_sub = voices.add_subparsers(dest="voices_cmd", required=True, parser_class=_ToolArgumentParser)
    voices_list = voices_sub.add_parser("list", help="List available voices")
    voices_list.set_defaults(func=voices_cmd.cmd_voices_list, write_capable=True)

    models = sub.add_parser("models", help="Available ElevenLabs models")
    models_sub = models.add_subparsers(dest="models_cmd", required=True, parser_class=_ToolArgumentParser)
    models_list = models_sub.add_parser("list", help="List available models")
    models_list.set_defaults(func=models_cmd.cmd_models_list, write_capable=True)

    usage = sub.add_parser("usage", help="Workspace usage and quota")
    usage_sub = usage.add_subparsers(dest="usage_cmd", required=True, parser_class=_ToolArgumentParser)
    usage_get = usage_sub.add_parser("get", help="Fetch usage metrics")
    usage_get.add_argument("--start-unix", type=int, help="UTC window start in milliseconds")
    usage_get.add_argument("--end-unix", type=int, help="UTC window end in milliseconds")
    usage_get.add_argument(
        "--include-workspace-metrics",
        action="store_true",
        help="Include workspace-wide metrics",
    )
    usage_get.add_argument("--breakdown-type", help="Usage breakdown type")
    usage_get.add_argument("--aggregation-interval", help="Aggregation interval")
    usage_get.add_argument("--aggregation-bucket-size", type=int, help="Bucket size in seconds")
    usage_get.add_argument("--metric", help="Usage metric to aggregate")
    usage_get.set_defaults(func=usage_cmd.cmd_usage_get, write_capable=True)

    history = sub.add_parser("history", help="Speech history queries")
    history_sub = history.add_subparsers(dest="history_cmd", required=True, parser_class=_ToolArgumentParser)
    history_list = history_sub.add_parser("list", help="List speech history entries")
    history_list.add_argument("--limit", type=int, default=None, help="Max entries to fetch")
    history_list.add_argument("--out", help="JSON file for live history output")
    history_list.add_argument("--overwrite", action="store_true", help="Overwrite existing output file")
    history_list.set_defaults(func=history_cmd.cmd_history_list, write_capable=True)
    history_download = history_sub.add_parser("download", help="Download audio from history")
    history_download.add_argument("--history-item-id", required=True, help="History item to download")
    history_download.add_argument("--format", default="mp3", help="Audio format (mp3/wav)")
    history_download.add_argument("--out", required=True, help="Output file path")
    history_download.add_argument("--overwrite", action="store_true", help="Overwrite existing output file")
    history_download.set_defaults(func=history_cmd.cmd_history_download, write_capable=True)

    tts = sub.add_parser("tts", help="Text-to-speech commands")
    tts_sub = tts.add_subparsers(dest="tts_cmd", required=True, parser_class=_ToolArgumentParser)
    tts_synthesize = tts_sub.add_parser("synthesize", help="Synthesize text to speech")
    tts_synthesize.add_argument("--voice-id", required=True, help="Voice to use")
    tts_synthesize.add_argument("--text", required=True, help="Text to synthesize")
    tts_synthesize.add_argument("--model-id", help="Model override")
    tts_synthesize.add_argument("--format", default="mp3", help="Output format")
    tts_synthesize.add_argument("--voice-settings", help="JSON voice settings")
    tts_synthesize.add_argument("--out", required=True, help="Output file path")
    tts_synthesize.add_argument("--overwrite", action="store_true", help="Overwrite existing file")
    tts_synthesize.set_defaults(func=tts_cmd.cmd_tts_synthesize, write_capable=True)

    existing_subparsers = {
        ("auth",): auth_sub,
        ("voices",): voices_sub,
        ("models",): models_sub,
        ("usage",): usage_sub,
        ("history",): history_sub,
        ("tts",): tts_sub,
    }
    register_operation_commands(
        sub,
        _ToolArgumentParser,
        skip_commands={
            "auth check",
            "voices list",
            "models list",
            "usage get",
            "history list",
            "history download",
            "tts synthesize",
        },
        existing_subparsers=existing_subparsers,
    )

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
    live_flag = bool(args.live)
    ack_spend_money = bool(args.ack_spend_money)
    local_ctx_flags = {
        "live": live_flag,
        "ack_spend_money": ack_spend_money,
    }
    cmd = getattr(args, "cmd", None)
    command_str = "elevenlabs-api-tool " + " ".join(argv)

    if cmd == "runs":
        run_ctx = RunContext(
            enabled=False,
            run_id=None,
            artifacts_dir=None,
            runs_index_path=runs_index_path,
            audit_log_path=None,
        )
        local_ctx_flags = {
            "live": live_flag,
            "ack_spend_money": ack_spend_money,
        }
        ctx = {
            "cfg": None,
            "out": out,
            "audit": audit,
            "tool": "elevenlabs-api-tool",
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
            **local_ctx_flags,
        }
        out.set_provenance(
            {
                "run_id": run_ctx.run_id,
                "artifacts_dir": str(run_ctx.artifacts_dir) if run_ctx.artifacts_dir else None,
                "runs_index": str(run_ctx.runs_index_path) if run_ctx.runs_index_path else str(runs_index_path),
                "audit_log": run_audit_log_path or global_audit_log_path,
                "audit_log_global": global_audit_log_path,
            }
        )
        rc = int(args.func(args, ctx))
        return rc

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
            payload = {"ok": True, "tool": "elevenlabs-api-tool", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"elevenlabs-api-tool {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        command_str = "elevenlabs-api-tool " + " ".join(argv)
        audit.bind_context(
            {
                "tool": "elevenlabs-api-tool",
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
        if cmd == "onboarding":
            ctx = {
                "cfg": None,
                "out": out,
                "audit": audit,
                "tool": "elevenlabs-api-tool",
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
                **local_ctx_flags,
            }
            rc = int(args.func(args, ctx))
            return rc

        cfg = load_config(args.env_file)
        env_fingerprint = cfg.base_url
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        secret_values = tuple(secret for secret in (cfg.token,) if secret)
        http_client = HttpClient(
            timeout_s=timeout_s,
            verbose=bool(args.verbose),
            user_agent=f"elevenlabs-api-tool/{__version__}",
            secrets=secret_values,
        )
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "tool": "elevenlabs-api-tool",
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
            "http_client": http_client,
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
            **local_ctx_flags,
        }

        if run_ctx.enabled and run_ctx.artifacts_dir:
            if not bool(args.apply) and not ctx.get("plan_out"):
                ctx["plan_out"] = str(run_ctx.artifacts_dir / "plan.json")
            if bool(args.apply) and not ctx.get("receipt_out"):
                ctx["receipt_out"] = str(run_ctx.artifacts_dir / "receipt.json")

        audit.bind_context(
            {
                "tool": "elevenlabs-api-tool",
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
            tool="elevenlabs-api-tool",
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
            tool="elevenlabs-api-tool",
            version=__version__,
            command="elevenlabs-api-tool " + " ".join(argv),
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
            tool="elevenlabs-api-tool",
            version=__version__,
            command="elevenlabs-api-tool " + " ".join(argv),
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
            tool="elevenlabs-api-tool",
            version=__version__,
            command="elevenlabs-api-tool " + " ".join(argv),
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
