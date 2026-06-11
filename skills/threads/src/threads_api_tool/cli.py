from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import auth as auth_cmd
from .commands import onboarding as onboarding_cmd
from .commands import insights as insights_cmd
from .commands import locations as locations_cmd
from .commands import mentions as mentions_cmd
from .commands import oembed as oembed_cmd
from .commands import posts as posts_cmd
from .commands import profiles as profiles_cmd
from .commands import replies as replies_cmd
from .commands import search as search_cmd
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
    p = _ToolArgumentParser(prog="threads-api-tool")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--config", default=None, help="Optional project defaults JSON (non-secret)")
    p.add_argument("--project-dir", default=None, help="Optional project directory (defaults to config file folder)")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument("--api-version", default=None, help="Override Graph API version (default: v1.0)")
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

    auth = sub.add_parser("auth", help="Authentication helpers")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Smoke test credentials")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=False)
    auth_authorize_url = auth_sub.add_parser("authorize-url", help="Build OAuth authorization URL")
    auth_authorize_url.add_argument("--scope", default=None, help="OAuth scope(s)")
    auth_authorize_url.add_argument("--state", default=None, help="OAuth state")
    auth_authorize_url.set_defaults(func=auth_cmd.cmd_auth_authorize_url, write_capable=False)
    auth_code_exchange = auth_sub.add_parser("code", help="OAuth authorization code")
    auth_code_exchange_sub = auth_code_exchange.add_subparsers(dest="code_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_code_exchange = auth_code_exchange_sub.add_parser("exchange", help="Exchange authorization code")
    auth_code_exchange.add_argument("--code", required=True, help="Authorization code")
    auth_code_exchange.set_defaults(func=auth_cmd.cmd_auth_code_exchange, write_capable=True)
    auth_debug_token = auth_sub.add_parser("debug-token", help="Debug an access token")
    auth_debug_token.add_argument("--input-token", default=None, help="Optional token to debug")
    auth_debug_token.set_defaults(func=auth_cmd.cmd_auth_debug_token, write_capable=False)

    auth_app_token = auth_sub.add_parser("app-token", help="App-token helpers")
    auth_app_sub = auth_app_token.add_subparsers(dest="app_token_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_app_generate = auth_app_sub.add_parser("generate", help="Generate app access token")
    auth_app_generate.set_defaults(func=auth_cmd.cmd_auth_app_token_generate, write_capable=False)

    token = auth_sub.add_parser("token", help="OAuth token helpers (manual copy/paste)")
    token_sub = token.add_subparsers(dest="token_cmd", required=True, parser_class=_ToolArgumentParser)
    token_status = token_sub.add_parser("status", help="Show token status (never prints token values)")
    token_status.set_defaults(func=auth_cmd.cmd_auth_token_status, write_capable=False)
    token_exchange_long = token_sub.add_parser("exchange-long", help="Exchange short-lived token for long-lived")
    token_exchange_long.add_argument("--short-token", default=None, help="Short-lived token (optional)")
    token_exchange_long.set_defaults(func=auth_cmd.cmd_auth_token_exchange_long, write_capable=True)
    token_refresh = token_sub.add_parser("refresh", help="Refresh long-lived token")
    token_refresh.add_argument("--long-token", default=None, help="Long-lived token (optional)")
    token_refresh.set_defaults(func=auth_cmd.cmd_auth_token_refresh, write_capable=True)

    profiles = sub.add_parser("profiles", help="Profile and account commands")
    profiles_sub = profiles.add_subparsers(dest="profiles_cmd", required=True, parser_class=_ToolArgumentParser)
    profiles_me = profiles_sub.add_parser("me", help="Read current user profile")
    profiles_me.add_argument("--fields", default=None)
    profiles_me.set_defaults(func=profiles_cmd.cmd_profiles_me, write_capable=False)
    profiles_get = profiles_sub.add_parser("get", help="Read profile by user id")
    profiles_get.add_argument("--threads-user-id", default=None, dest="threads_user_id", help="Target user id")
    profiles_get.add_argument("--fields", default=None)
    profiles_get.set_defaults(func=profiles_cmd.cmd_profiles_get, write_capable=False)
    profiles_lookup = profiles_sub.add_parser("lookup", help="Lookup profile by username")
    profiles_lookup.add_argument("--username", required=True)
    profiles_lookup.add_argument("--fields", default=None)
    profiles_lookup.set_defaults(func=profiles_cmd.cmd_profiles_lookup, write_capable=False)

    posts = sub.add_parser("posts", help="Posts and publishing commands")
    posts_sub = posts.add_subparsers(dest="posts_cmd", required=True, parser_class=_ToolArgumentParser)

    def add_posts_write_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--threads-user-id", default=None, dest="threads_user_id")
        parser.add_argument("--text", default=None)
        parser.add_argument("--image-url", default=None, dest="image_url")
        parser.add_argument("--video-url", default=None, dest="video_url")
        parser.add_argument("--topic-tag", default=None)
        parser.add_argument("--reply-to-id", default=None, dest="reply_to_id")
        parser.add_argument("--reply-control", default=None, dest="reply_control")
        parser.add_argument("--enable-reply-approvals", action="store_true", dest="enable_reply_approvals")
        parser.add_argument("--quote-post-id", default=None, dest="quote_post_id")
        parser.add_argument("--link-attachment", default=None, dest="link_attachment")
        parser.add_argument("--gif-id", default=None, dest="gif_id")
        parser.add_argument("--gif-provider", default=None, dest="gif_provider")
        parser.add_argument("--location-id", default=None, dest="location_id")
        parser.add_argument("--spoiler-media", action="store_true", dest="spoiler_media")
        parser.add_argument(
            "--text-spoiler-range",
            action="append",
            default=None,
            dest="text_spoiler_ranges",
            help="Repeatable text spoiler range in offset:length format",
        )
        parser.add_argument("--poll-option", action="append", default=None, dest="poll_options")
        parser.add_argument("--poll-options", default=None, dest="poll_options_csv")
        parser.add_argument("--children", default=None)
        parser.add_argument("--is-carousel-item", action="store_true", dest="is_carousel_item")

    posts_list_owned = posts_sub.add_parser("list-owned", help="List user-owned posts")
    posts_list_owned.add_argument("--threads-user-id", default=None, dest="threads_user_id")
    posts_list_owned.add_argument("--fields", default=None)
    posts_list_owned.add_argument("--limit", type=int, default=None)
    posts_list_owned.add_argument("--before", default=None)
    posts_list_owned.add_argument("--after", default=None)
    posts_list_owned.add_argument("--since", default=None)
    posts_list_owned.add_argument("--until", default=None)
    posts_list_owned.add_argument("--reverse", action="store_true")
    posts_list_owned.set_defaults(func=posts_cmd.cmd_posts_list_owned, write_capable=False)
    posts_list_public = posts_sub.add_parser("list-public", help="List public posts")
    posts_list_public.add_argument("--username", required=True)
    posts_list_public.add_argument("--fields", default=None)
    posts_list_public.add_argument("--limit", type=int, default=None)
    posts_list_public.add_argument("--before", default=None)
    posts_list_public.add_argument("--after", default=None)
    posts_list_public.add_argument("--since", default=None)
    posts_list_public.add_argument("--until", default=None)
    posts_list_public.add_argument("--reverse", action="store_true")
    posts_list_public.set_defaults(func=posts_cmd.cmd_posts_list_public, write_capable=False)
    posts_get = posts_sub.add_parser("get", help="Read one post container")
    posts_get.add_argument("--threads-media-id", required=True, dest="threads_media_id")
    posts_get.add_argument("--fields", default=None)
    posts_get.set_defaults(func=posts_cmd.cmd_posts_get, write_capable=False)
    posts_limits = posts_sub.add_parser("limits", help="Read publishing limits")
    posts_limits.add_argument("--threads-user-id", default=None, dest="threads_user_id")
    posts_limits.set_defaults(func=posts_cmd.cmd_posts_limits, write_capable=False)

    posts_create_text = posts_sub.add_parser("create-text", help="Create draft post text container")
    add_posts_write_args(posts_create_text)
    posts_create_text.set_defaults(func=posts_cmd.cmd_posts_create_text, write_capable=True)

    posts_create_image = posts_sub.add_parser("create-image", help="Create draft image post")
    add_posts_write_args(posts_create_image)
    posts_create_image.set_defaults(func=posts_cmd.cmd_posts_create_image, write_capable=True)

    posts_create_video = posts_sub.add_parser("create-video", help="Create draft video post")
    add_posts_write_args(posts_create_video)
    posts_create_video.set_defaults(func=posts_cmd.cmd_posts_create_video, write_capable=True)

    posts_create_carousel_item = posts_sub.add_parser("create-carousel-item", help="Create carousel item draft")
    add_posts_write_args(posts_create_carousel_item)
    posts_create_carousel_item.set_defaults(func=posts_cmd.cmd_posts_create_carousel_item, write_capable=True)

    posts_create_carousel = posts_sub.add_parser("create-carousel", help="Create carousel draft")
    add_posts_write_args(posts_create_carousel)
    posts_create_carousel.set_defaults(func=posts_cmd.cmd_posts_create_carousel, write_capable=True)

    posts_publish = posts_sub.add_parser("publish", help="Publish a post container")
    posts_publish.add_argument("--threads-user-id", default=None, dest="threads_user_id")
    posts_publish.add_argument("--threads-container-id", required=True, dest="threads_container_id")
    posts_publish.set_defaults(func=posts_cmd.cmd_posts_publish, write_capable=True)

    posts_status = posts_sub.add_parser("status", help="Read post status")
    posts_status.add_argument("--threads-container-id", required=True, dest="threads_container_id")
    posts_status.add_argument("--fields", default=None)
    posts_status.set_defaults(func=posts_cmd.cmd_posts_status, write_capable=False)

    posts_repost = posts_sub.add_parser("repost", help="Repost one media")
    posts_repost.add_argument("--threads-media-id", required=True, dest="threads_media_id")
    posts_repost.set_defaults(func=posts_cmd.cmd_posts_repost, write_capable=True)
    posts_delete = posts_sub.add_parser("delete", help="Delete a post")
    posts_delete.add_argument("--threads-media-id", required=True, dest="threads_media_id")
    posts_delete.set_defaults(func=posts_cmd.cmd_posts_delete, write_capable=True)

    replies = sub.add_parser("replies", help="Reply list and moderation")
    replies_sub = replies.add_subparsers(dest="replies_cmd", required=True, parser_class=_ToolArgumentParser)
    replies_list = replies_sub.add_parser("list", help="List replies for a post")
    replies_list.add_argument("--threads-media-id", required=True, dest="threads_media_id")
    replies_list.add_argument("--fields", default=None)
    replies_list.add_argument("--limit", type=int, default=None)
    replies_list.add_argument("--before", default=None)
    replies_list.add_argument("--after", default=None)
    replies_list.add_argument("--since", default=None)
    replies_list.add_argument("--until", default=None)
    replies_list.add_argument("--reverse", action="store_true")
    replies_list.set_defaults(func=replies_cmd.cmd_replies_list, write_capable=False)
    replies_conversation = replies_sub.add_parser("conversation", help="Show reply conversation")
    replies_conversation.add_argument("--threads-media-id", required=True, dest="threads_media_id")
    replies_conversation.add_argument("--fields", default=None)
    replies_conversation.add_argument("--limit", type=int, default=None)
    replies_conversation.set_defaults(func=replies_cmd.cmd_replies_conversation, write_capable=False)
    replies_hide = replies_sub.add_parser("hide", help="Hide a reply")
    replies_hide.add_argument("--threads-reply-id", required=True, dest="threads_reply_id")
    replies_hide.add_argument("--hide", required=True)
    replies_hide.set_defaults(func=replies_cmd.cmd_replies_hide, write_capable=True)
    replies_pending = replies_sub.add_parser("pending", help="Pending reply actions")
    replies_pending_sub = replies_pending.add_subparsers(dest="pending_cmd", required=True, parser_class=_ToolArgumentParser)
    replies_pending_list = replies_pending_sub.add_parser("list", help="List pending replies")
    replies_pending_list.add_argument("--threads-media-id", required=True, dest="threads_media_id")
    replies_pending_list.add_argument("--fields", default=None)
    replies_pending_list.add_argument("--limit", type=int, default=None)
    replies_pending_list.add_argument("--before", default=None)
    replies_pending_list.add_argument("--after", default=None)
    replies_pending_list.set_defaults(func=replies_cmd.cmd_replies_pending_list, write_capable=False)
    replies_pending_decide = replies_pending_sub.add_parser("decide", help="Moderate pending reply")
    replies_pending_decide.add_argument("--threads-reply-id", required=True, dest="threads_reply_id")
    replies_pending_decide.add_argument("--approve", required=True)
    replies_pending_decide.set_defaults(func=replies_cmd.cmd_replies_pending_decide, write_capable=True)

    mentions = sub.add_parser("mentions", help="Mention reads")
    mentions_sub = mentions.add_subparsers(dest="mentions_cmd", required=True, parser_class=_ToolArgumentParser)
    mentions_list = mentions_sub.add_parser("list", help="List mentions for user")
    mentions_list.add_argument("--threads-user-id", default=None, dest="threads_user_id")
    mentions_list.add_argument("--fields", default=None)
    mentions_list.add_argument("--limit", type=int, default=None)
    mentions_list.add_argument("--before", default=None)
    mentions_list.add_argument("--after", default=None)
    mentions_list.set_defaults(func=mentions_cmd.cmd_mentions_list, write_capable=False)

    insights = sub.add_parser("insights", help="Insights reads")
    insights_sub = insights.add_subparsers(dest="insights_cmd", required=True, parser_class=_ToolArgumentParser)
    insights_media = insights_sub.add_parser("media", help="Read post insights")
    insights_media.add_argument("--threads-media-id", required=True, dest="threads_media_id")
    insights_media.add_argument("--fields", default=None)
    insights_media.add_argument("--since", default=None)
    insights_media.add_argument("--until", default=None)
    insights_media.add_argument("--period", default=None)
    insights_media.add_argument("--metric", default=None)
    insights_media.set_defaults(func=insights_cmd.cmd_insights_media, write_capable=False)
    insights_user = insights_sub.add_parser("user", help="Read account insights")
    insights_user.add_argument("--threads-user-id", default=None, dest="threads_user_id")
    insights_user.add_argument("--fields", default=None)
    insights_user.add_argument("--since", default=None)
    insights_user.add_argument("--until", default=None)
    insights_user.add_argument("--period", default=None)
    insights_user.add_argument("--metric", default=None)
    insights_user.set_defaults(func=insights_cmd.cmd_insights_user, write_capable=False)

    search = sub.add_parser("search", help="Search and discovery")
    search_sub = search.add_subparsers(dest="search_cmd", required=True, parser_class=_ToolArgumentParser)
    search_keyword = search_sub.add_parser("keyword", help="Keyword search")
    search_keyword.add_argument("--q", required=True)
    search_keyword.add_argument("--fields", default=None)
    search_keyword.add_argument("--limit", type=int, default=None)
    search_keyword.add_argument("--search-type", default=None, dest="search_type")
    search_keyword.add_argument("--search-mode", default=None, dest="search_mode")
    search_keyword.add_argument("--media-type", default=None, dest="media_type")
    search_keyword.set_defaults(func=search_cmd.cmd_search_keyword, write_capable=False)
    search_topic = search_sub.add_parser("topic-tag", help="Search by topic tag")
    search_topic.add_argument("--topic-tag", required=True, dest="topic_tag")
    search_topic.add_argument("--fields", default=None)
    search_topic.add_argument("--limit", type=int, default=None)
    search_topic.add_argument("--search-type", default=None, dest="search_type")
    search_topic.add_argument("--search-mode", default="TAG", dest="search_mode")
    search_topic.add_argument("--media-type", default=None, dest="media_type")
    search_topic.set_defaults(func=search_cmd.cmd_search_topic_tag, write_capable=False)
    search_recent = search_sub.add_parser("recent-keywords", help="Recent keyword suggestions")
    search_recent.set_defaults(func=search_cmd.cmd_search_recent_keywords, write_capable=False)

    locations = sub.add_parser("locations", help="Location lookup")
    locations_sub = locations.add_subparsers(dest="locations_cmd", required=True, parser_class=_ToolArgumentParser)
    locations_query = locations_sub.add_parser("search-query", help="Search locations by query")
    locations_query.add_argument("--q", required=True)
    locations_query.add_argument("--fields", default=None)
    locations_query.set_defaults(func=locations_cmd.cmd_locations_search_query, write_capable=False)
    locations_coordinates = locations_sub.add_parser("search-coordinates", help="Search by latitude/longitude")
    locations_coordinates.add_argument("--latitude", required=True)
    locations_coordinates.add_argument("--longitude", required=True)
    locations_coordinates.add_argument("--fields", default=None)
    locations_coordinates.set_defaults(func=locations_cmd.cmd_locations_search_coordinates, write_capable=False)
    locations_get = locations_sub.add_parser("get", help="Get location details")
    locations_get.add_argument("--location-id", required=True, dest="location_id")
    locations_get.add_argument("--fields", default=None)
    locations_get.set_defaults(func=locations_cmd.cmd_locations_get, write_capable=False)

    oembed = sub.add_parser("oembed", help="Embedded content metadata")
    oembed_sub = oembed.add_subparsers(dest="oembed_cmd", required=True, parser_class=_ToolArgumentParser)
    oembed_get = oembed_sub.add_parser("get", help="Fetch oEmbed data")
    oembed_get.add_argument("--url", required=True)
    oembed_get.add_argument("--fields", default=None)
    oembed_get.add_argument("--maxwidth", default=None, type=int)
    oembed_get.set_defaults(func=oembed_cmd.cmd_oembed_get, write_capable=False)

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
            payload = {"ok": True, "tool": "threads-api-tool", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"threads-api-tool {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        command_str = "threads-api-tool " + " ".join(argv)
        audit.bind_context(
            {
                "tool": "threads-api-tool",
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
                "tool": "threads-api-tool",
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

        cfg = load_config(args.env_file, api_version_override=args.api_version)
        env_fingerprint = cfg.base_url
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "tool": "threads-api-tool",
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
                "tool": "threads-api-tool",
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
            tool="threads-api-tool",
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
            tool="threads-api-tool",
            version=__version__,
            command="threads-api-tool " + " ".join(argv),
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
            tool="threads-api-tool",
            version=__version__,
            command="threads-api-tool " + " ".join(argv),
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
            tool="threads-api-tool",
            version=__version__,
            command="threads-api-tool " + " ".join(argv),
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
