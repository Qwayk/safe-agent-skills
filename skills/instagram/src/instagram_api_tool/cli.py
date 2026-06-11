from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import auth as auth_cmd
from .commands import onboarding as onboarding_cmd
from .commands import comments as comments_cmd
from .commands import insights as insights_cmd
from .commands import live_media as live_media_cmd
from .commands import media as media_cmd
from .commands import messages as messages_cmd
from .commands import mentions as mentions_cmd
from .commands import stories as stories_cmd
from .commands import tags as tags_cmd
from .commands import users as users_cmd
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
    p = _ToolArgumentParser(prog="instagram-api-tool")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--config", default=None, help="Optional project defaults JSON (non-secret)")
    p.add_argument("--project-dir", default=None, help="Optional project directory (defaults to config file folder)")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    p.add_argument("--debug", action="store_true", help="Show stack traces on errors")
    p.add_argument("--output", choices=("json", "text"), default="json", help="Output format (default: json)")
    p.add_argument("--log-file", default=None, help="Optional audit log path (JSONL)")
    p.add_argument("--apply", action="store_true", help="Attempt apply after safety gates (default is dry-run)")
    p.add_argument("--yes", action="store_true", help="Additional confirmation for destructive/batch actions")
    p.add_argument(
        "--ack-no-snapshot",
        action="store_true",
        help="Acknowledge that this approved write may run without a saved before-state snapshot",
    )
    p.add_argument("--plan-out", default=None, help="Write a dry-run plan JSON to a file")
    p.add_argument("--plan-in", default=None, help="Apply from an existing plan JSON file (high-risk writes)")
    p.add_argument(
        "--receipt-out",
        default=None,
        help="Write approved apply receipts; missing-approval refusals do not write it",
    )
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
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=False)

    auth_login_url = auth_sub.add_parser("login-url", help="Build Instagram OAuth consent URL")
    auth_login_url.add_argument("--state", default=None, help="Optional OAuth state value")
    auth_login_url.add_argument(
        "--scope",
        default=None,
        help=(
            "Optional OAuth scope list. "
            "Examples: instagram_business_basic,instagram_business_content_publish,"
            "instagram_business_manage_comments"
        ),
    )
    auth_login_url.set_defaults(func=auth_cmd.cmd_auth_login_url, write_capable=False)

    auth_code = auth_sub.add_parser("code", help="OAuth code helpers")
    auth_code_sub = auth_code.add_subparsers(dest="auth_code_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_code_exchange = auth_code_sub.add_parser("exchange", help="Exchange authorization code")
    auth_code_exchange.add_argument("--code", required=True, help="Authorization code from the redirect")
    auth_code_exchange.set_defaults(func=auth_cmd.cmd_auth_code_exchange, write_capable=True)

    token = auth_sub.add_parser("token", help="OAuth token helpers (manual copy/paste)")
    token_sub = token.add_subparsers(dest="token_cmd", required=True, parser_class=_ToolArgumentParser)
    token_set = token_sub.add_parser("set", help="Store token JSON under .state/token.json")
    token_set.add_argument("--file", required=True, help="Token JSON file path (input)")
    token_set.set_defaults(func=auth_cmd.cmd_auth_token_set, write_capable=True)
    token_status = token_sub.add_parser("status", help="Show token status (never prints token values)")
    token_status.set_defaults(func=auth_cmd.cmd_auth_token_status, write_capable=False)
    token_exchange_long = token_sub.add_parser("exchange-long", help="Exchange short-lived token for long-lived")
    token_exchange_long.add_argument("--short-token", default=None, help="Short-lived access token (optional)")
    token_exchange_long.set_defaults(func=auth_cmd.cmd_auth_token_exchange_long, write_capable=True)
    token_refresh = token_sub.add_parser("refresh", help="Refresh long-lived token")
    token_refresh.add_argument("--long-token", default=None, help="Long-lived token override (optional)")
    token_refresh.set_defaults(func=auth_cmd.cmd_auth_token_refresh, write_capable=True)

    users = sub.add_parser("users", help="IG user read operations")
    users_sub = users.add_subparsers(dest="users_cmd", required=True, parser_class=_ToolArgumentParser)
    users_me = users_sub.add_parser("me", help="Resolve app user")
    users_me.add_argument("--fields", default=None, help="Comma-separated field list")
    users_me.set_defaults(func=users_cmd.cmd_users_me, write_capable=False)
    users_get = users_sub.add_parser("get", help="Get IG User fields")
    users_get.add_argument("--ig-user-id", required=True, help="IG User ID")
    users_get.add_argument("--fields", default=None, help="Comma-separated field list")
    users_get.set_defaults(func=users_cmd.cmd_users_get, write_capable=False)

    media = sub.add_parser("media", help="Media operations")
    media_sub = media.add_subparsers(dest="media_cmd", required=True, parser_class=_ToolArgumentParser)
    media_list = media_sub.add_parser("list", help="List owned media")
    media_list.add_argument("--ig-user-id", required=True, help="IG User ID")
    media_list.add_argument("--fields", default=None, help="Comma-separated field list")
    media_list.add_argument("--limit", type=int, default=None)
    media_list.add_argument("--before", default=None)
    media_list.add_argument("--after", default=None)
    media_list.set_defaults(func=media_cmd.cmd_media_list, write_capable=False)
    media_create = media_sub.add_parser("create-container", help="Create publishing container")
    media_create.add_argument("--ig-user-id", required=True, help="IG User ID")
    media_create.add_argument("--media-type", default=None, help="IG media_type value")
    media_create.add_argument("--image-url", default=None, help="Image URL")
    media_create.add_argument("--video-url", default=None, help="Video URL")
    media_create.add_argument("--children", default=None, help="Comma list of child media IDs")
    media_create.add_argument("--caption", default=None, help="Optional caption")
    media_create.add_argument("--fields", default=None, help="Comma-separated field list")
    media_create.set_defaults(func=media_cmd.cmd_media_create_container, write_capable=True)
    media_publish = media_sub.add_parser("publish", help="Publish a created container")
    media_publish.add_argument("--ig-user-id", required=True, help="IG User ID")
    media_publish.add_argument("--creation-id", required=True, help="Container ID from create-container")
    media_publish.set_defaults(func=media_cmd.cmd_media_publish, write_capable=True)
    media_container = media_sub.add_parser("container", help="Media container ops")
    media_container_sub = media_container.add_subparsers(dest="media_container_cmd", required=True, parser_class=_ToolArgumentParser)
    media_container_get = media_container_sub.add_parser("get", help="Get container status")
    media_container_get.add_argument("--container-id", required=True, help="Container ID")
    media_container_get.add_argument("--fields", default=None, help="Comma-separated field list")
    media_container_get.set_defaults(func=media_cmd.cmd_media_container_get, write_capable=False)
    media_publish_limit = media_sub.add_parser("publish-limit", help="Read publish quota")
    media_publish_limit.add_argument("--ig-user-id", required=True, help="IG User ID")
    media_publish_limit.add_argument("--fields", default=None, help="Comma-separated field list")
    media_publish_limit.set_defaults(func=media_cmd.cmd_media_publish_limit, write_capable=False)
    media_get = media_sub.add_parser("get", help="Get IG media fields")
    media_get.add_argument("--media-id", required=True, help="IG Media ID")
    media_get.add_argument("--fields", default=None, help="Comma-separated field list")
    media_get.set_defaults(func=media_cmd.cmd_media_get, write_capable=False)
    media_children = media_sub.add_parser("children", help="List carousel children")
    media_children.add_argument("--media-id", required=True, help="IG Media ID")
    media_children.add_argument("--fields", default=None, help="Comma-separated field list")
    media_children.set_defaults(func=media_cmd.cmd_media_children, write_capable=False)
    media_comments = media_sub.add_parser("comments", help="Media comment settings")
    media_comments_sub = media_comments.add_subparsers(dest="media_comments_cmd", required=True, parser_class=_ToolArgumentParser)
    media_comments_set = media_comments_sub.add_parser("set", help="Enable or disable comments")
    media_comments_set.add_argument("--media-id", required=True, help="IG Media ID")
    media_comments_set.add_argument("--enabled", required=True, choices=("true", "false"), help="true|false")
    media_comments_set.set_defaults(func=media_cmd.cmd_media_comments_set, write_capable=True)

    comments = sub.add_parser("comments", help="Comment operations")
    comments_sub = comments.add_subparsers(dest="comments_cmd", required=True, parser_class=_ToolArgumentParser)
    comments_list = comments_sub.add_parser("list", help="List comments on media")
    comments_list.add_argument("--media-id", required=True, help="IG Media ID")
    comments_list.add_argument("--fields", default=None, help="Comma-separated field list")
    comments_list.set_defaults(func=comments_cmd.cmd_comments_list, write_capable=False)
    comments_create = comments_sub.add_parser("create", help="Create a comment")
    comments_create.add_argument("--media-id", required=True, help="IG Media ID")
    comments_create.add_argument("--message", required=True, help="Comment text")
    comments_create.set_defaults(func=comments_cmd.cmd_comments_create, write_capable=True)
    comments_get = comments_sub.add_parser("get", help="Get one comment")
    comments_get.add_argument("--comment-id", required=True, help="IG Comment ID")
    comments_get.add_argument("--fields", default=None, help="Comma-separated field list")
    comments_get.set_defaults(func=comments_cmd.cmd_comments_get, write_capable=False)
    comments_hide = comments_sub.add_parser("hide", help="Hide or unhide comment")
    comments_hide.add_argument("--comment-id", required=True, help="IG Comment ID")
    comments_hide.add_argument("--hidden", required=True, choices=("true", "false"), help="true|false")
    comments_hide.set_defaults(func=comments_cmd.cmd_comments_hide, write_capable=True)
    comments_delete = comments_sub.add_parser("delete", help="Delete comment (destructive)")
    comments_delete.add_argument("--comment-id", required=True, help="IG Comment ID")
    comments_delete.set_defaults(func=comments_cmd.cmd_comments_delete, write_capable=True)
    comments_replies = comments_sub.add_parser("replies", help="Comment replies")
    comments_replies_sub = comments_replies.add_subparsers(dest="comments_replies_cmd", required=True, parser_class=_ToolArgumentParser)
    comments_replies_list = comments_replies_sub.add_parser("list", help="List replies")
    comments_replies_list.add_argument("--comment-id", required=True, help="IG Comment ID")
    comments_replies_list.set_defaults(func=comments_cmd.cmd_comments_replies_list, write_capable=False)
    comments_replies_create = comments_replies_sub.add_parser("create", help="Reply to a comment")
    comments_replies_create.add_argument("--comment-id", required=True, help="IG Comment ID")
    comments_replies_create.add_argument("--message", required=True, help="Reply text")
    comments_replies_create.set_defaults(func=comments_cmd.cmd_comments_replies_create, write_capable=True)

    mentions = sub.add_parser("mentions", help="Mention operations")
    mentions_sub = mentions.add_subparsers(dest="mentions_cmd", required=True, parser_class=_ToolArgumentParser)
    mentions_media = mentions_sub.add_parser("media", help="Read media mention")
    mentions_media.add_argument("--ig-user-id", required=True, help="IG User ID")
    mentions_media.add_argument("--media-id", required=True, help="Mentioned media ID")
    mentions_media.set_defaults(func=mentions_cmd.cmd_mentions_media_get, write_capable=False)
    mentions_comment = mentions_sub.add_parser("comment", help="Read comment mention")
    mentions_comment.add_argument("--ig-user-id", required=True, help="IG User ID")
    mentions_comment.add_argument("--comment-id", required=True, help="Mentioned comment ID")
    mentions_comment.set_defaults(func=mentions_cmd.cmd_mentions_comment_get, write_capable=False)
    mentions_reply_media = mentions_sub.add_parser("reply-media", help="Reply to a media mention")
    mentions_reply_media.add_argument("--ig-user-id", required=True, help="IG User ID")
    mentions_reply_media.add_argument("--media-id", required=True, help="Media mention ID")
    mentions_reply_media.add_argument("--message", required=True, help="Reply text")
    mentions_reply_media.set_defaults(func=mentions_cmd.cmd_mentions_reply_media, write_capable=True)
    mentions_reply_comment = mentions_sub.add_parser("reply-comment", help="Reply to a comment mention")
    mentions_reply_comment.add_argument("--ig-user-id", required=True, help="IG User ID")
    mentions_reply_comment.add_argument("--media-id", required=True, help="Mentioned media ID")
    mentions_reply_comment.add_argument("--comment-id", required=True, help="Mentioned comment ID")
    mentions_reply_comment.add_argument("--message", required=True, help="Reply text")
    mentions_reply_comment.set_defaults(func=mentions_cmd.cmd_mentions_reply_comment, write_capable=True)

    insights = sub.add_parser("insights", help="Insight operations")
    insights_sub = insights.add_subparsers(dest="insights_cmd", required=True, parser_class=_ToolArgumentParser)
    insights_account = insights_sub.add_parser("account", help="Account insights")
    insights_account_sub = insights_account.add_subparsers(dest="insights_account_cmd", required=True, parser_class=_ToolArgumentParser)
    insights_account_get = insights_account_sub.add_parser("get", help="Get account insights")
    insights_account_get.add_argument("--ig-user-id", required=True, help="IG User ID")
    insights_account_get.add_argument("--metric", required=True, help="Comma-separated metric names")
    insights_account_get.add_argument("--period", default=None, help="Insight period")
    insights_account_get.add_argument("--breakdown", default=None, help="Comma-separated breakdown values")
    insights_account_get.set_defaults(func=insights_cmd.cmd_insights_account_get, write_capable=False)
    insights_media = insights_sub.add_parser("media", help="Media insights")
    insights_media_sub = insights_media.add_subparsers(dest="insights_media_cmd", required=True, parser_class=_ToolArgumentParser)
    insights_media_get = insights_media_sub.add_parser("get", help="Get media insights")
    insights_media_get.add_argument("--media-id", required=True, help="IG Media ID")
    insights_media_get.add_argument("--metric", required=True, help="Comma-separated metric names")
    insights_media_get.add_argument("--period", default=None, help="Insight period")
    insights_media_get.add_argument("--breakdown", default=None, help="Comma-separated breakdown values")
    insights_media_get.set_defaults(func=insights_cmd.cmd_insights_media_get, write_capable=False)

    messages = sub.add_parser("messages", help="Message operations")
    messages_sub = messages.add_subparsers(dest="messages_cmd", required=True, parser_class=_ToolArgumentParser)
    messages_send = messages_sub.add_parser("send", help="Send a message")
    messages_send.add_argument("--ig-user-id", required=True, help="IG User ID")
    messages_send.add_argument("--recipient-id", required=True, help="Recipient user ID")
    messages_send.add_argument("--message", required=True, help="Message text")
    messages_send.set_defaults(func=messages_cmd.cmd_messages_send, write_capable=True)
    messages_private_reply = messages_sub.add_parser("private-reply", help="Send private reply")
    messages_private_reply.add_argument("--ig-user-id", required=True, help="IG User ID")
    messages_private_reply.add_argument("--recipient-id", required=True, help="Recipient user ID")
    messages_private_reply.add_argument("--message", required=True, help="Message text")
    messages_private_reply.set_defaults(func=messages_cmd.cmd_messages_private_reply, write_capable=True)

    tags = sub.add_parser("tags", help="Tags operations")
    tags_sub = tags.add_subparsers(dest="tags_cmd", required=True, parser_class=_ToolArgumentParser)
    tags_list = tags_sub.add_parser("list", help="List tags on media owned by user")
    tags_list.add_argument("--ig-user-id", required=True, help="IG User ID")
    tags_list.add_argument("--fields", default=None, help="Comma-separated field list")
    tags_list.set_defaults(func=tags_cmd.cmd_tags_list, write_capable=False)

    stories = sub.add_parser("stories", help="Stories operations")
    stories_sub = stories.add_subparsers(dest="stories_cmd", required=True, parser_class=_ToolArgumentParser)
    stories_list = stories_sub.add_parser("list", help="List current stories")
    stories_list.add_argument("--ig-user-id", required=True, help="IG User ID")
    stories_list.add_argument("--fields", default=None, help="Comma-separated field list")
    stories_list.set_defaults(func=stories_cmd.cmd_stories_list, write_capable=False)

    live_media = sub.add_parser("live-media", help="Live media operations")
    live_media_sub = live_media.add_subparsers(dest="live_media_cmd", required=True, parser_class=_ToolArgumentParser)
    live_media_list = live_media_sub.add_parser("list", help="List active live media")
    live_media_list.add_argument("--ig-user-id", required=True, help="IG User ID")
    live_media_list.add_argument("--fields", default=None, help="Comma-separated field list")
    live_media_list.set_defaults(func=live_media_cmd.cmd_live_media_list, write_capable=False)

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
            payload = {"ok": True, "tool": "instagram-api-tool", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"instagram-api-tool {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        command_str = "instagram-api-tool " + " ".join(argv)
        audit.bind_context(
            {
                "tool": "instagram-api-tool",
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
        if str(getattr(args, "cmd", "") or "") in {"runs", "onboarding"}:
            ctx = {
                "cfg": None,
                "out": out,
                "audit": audit,
                "tool": "instagram-api-tool",
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
            "tool": "instagram-api-tool",
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
                "tool": "instagram-api-tool",
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
            tool="instagram-api-tool",
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
            tool="instagram-api-tool",
            version=__version__,
            command="instagram-api-tool " + " ".join(argv),
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
            tool="instagram-api-tool",
            version=__version__,
            command="instagram-api-tool " + " ".join(argv),
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
            tool="instagram-api-tool",
            version=__version__,
            command="instagram-api-tool " + " ".join(argv),
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
