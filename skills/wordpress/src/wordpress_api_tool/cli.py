from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import partial
import sys

from . import __version__
from .audit_log import AuditLogger
from .commands import auth as auth_cmd
from .commands import comments as comments_cmd
from .commands import discover as discover_cmd
from .commands import jobs as jobs_cmd
from .commands import media as media_cmd
from .commands import migration as migration_cmd
from .commands import post as post_cmd
from .commands import search as search_cmd
from .commands import settings as settings_cmd
from .commands import terms as terms_cmd
from .commands import users as users_cmd
from . import v2 as v2util
from .config import load_config
from .output import Output
from .project_config import load_project_config


@dataclass(frozen=True)
class _ParserExit(Exception):
    status: int
    kind: str
    message: str | None = None
    usage: str | None = None
    help_text: str | None = None


def _detect_output_mode(argv: list[str]) -> str:
    # Default is json; treat unknown/missing value as json.
    for i, a in enumerate(argv):
        if a == "--output" and i + 1 < len(argv):
            v = str(argv[i + 1]).strip()
            return v if v in {"json", "text"} else "json"
        if a.startswith("--output="):
            v = str(a.split("=", 1)[1]).strip()
            return v if v in {"json", "text"} else "json"
    return "json"


def build_parser(*, json_mode: bool) -> argparse.ArgumentParser:
    class _JsonArgumentParser(argparse.ArgumentParser):
        def __init__(self, *args, json_mode: bool = False, **kwargs):
            super().__init__(*args, **kwargs)
            self._json_mode = bool(json_mode)
            self._captured_help: str | None = None

        def print_help(self, file=None) -> None:  # noqa: ANN001
            if not self._json_mode:
                return super().print_help(file=file)
            self._captured_help = self.format_help()

        def exit(self, status: int = 0, message: str | None = None) -> None:  # type: ignore[override]
            if not self._json_mode:
                return super().exit(status=status, message=message)
            help_text = self._captured_help
            kind = "exit"
            if status == 0 and help_text:
                kind = "help"
            elif status == 0 and message and message.strip().startswith(f"{self.prog} "):
                kind = "version"
            raise _ParserExit(status=status, kind=kind, message=message, help_text=help_text)

        def error(self, message: str) -> None:  # type: ignore[override]
            if not self._json_mode:
                return super().error(message)
            raise _ParserExit(status=2, kind="usage_error", message=message, usage=self.format_usage())

    p = _JsonArgumentParser(prog="wordpress-api-tool", json_mode=json_mode)
    if json_mode:
        p.add_argument("--version", action="store_true", help="Print tool version and exit")
    else:
        p.add_argument("--version", action="version", version=f"wordpress-api-tool {__version__}")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument("--config", default=None, help="Optional project defaults JSON (non-secret)")
    p.add_argument("--project-dir", default=None, help="Optional project directory (defaults to config file folder)")
    p.add_argument("--timeout-s", type=float, default=30.0)
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    p.add_argument("--debug", action="store_true", help="Show stack traces on errors")

    p.add_argument(
        "--output",
        choices=("json", "text"),
        default="json",
        help="Output format (default: json)",
    )
    p.add_argument("--log-file", default=None, help="Optional audit log path (JSONL)")

    p.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (default is dry-run)",
    )
    p.add_argument(
        "--yes",
        action="store_true",
        help="Additional confirmation for batch jobs",
    )
    p.add_argument(
        "--ack-no-snapshot",
        action="store_true",
        help="Acknowledge that this approved write may run without a saved live before-state snapshot",
    )
    p.add_argument("--plan-out", default=None, help="Write computed plan JSON to a file (v2)")
    p.add_argument("--receipt-out", default=None, help="Write receipt JSON to a file after apply (v2)")

    json_parser_class = partial(_JsonArgumentParser, json_mode=json_mode)
    sub = p.add_subparsers(dest="cmd", required=False, parser_class=json_parser_class)

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=json_parser_class)
    auth_check = auth_sub.add_parser("check", help="Smoke test credentials (/users/me)")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check)

    discover = sub.add_parser("discover", help="Discover supported types/statuses/taxonomies (read-only)")
    discover_sub = discover.add_subparsers(dest="discover_cmd", required=True, parser_class=json_parser_class)

    discover_types = discover_sub.add_parser("post-types", help="List available post types (GET /types)")
    discover_types.add_argument("--include-raw", action="store_true", help="Include full raw response")
    discover_types.add_argument(
        "--context",
        choices=("view", "edit"),
        default="view",
        help="REST API context (default: view; use edit only if needed and allowed)",
    )
    discover_types.set_defaults(func=discover_cmd.cmd_discover_post_types)

    discover_statuses = discover_sub.add_parser("statuses", help="List available post statuses (GET /statuses)")
    discover_statuses.add_argument("--include-raw", action="store_true", help="Include full raw response")
    discover_statuses.add_argument(
        "--context",
        choices=("view", "edit"),
        default="view",
        help="REST API context (default: view; use edit only if needed and allowed)",
    )
    discover_statuses.set_defaults(func=discover_cmd.cmd_discover_statuses)

    discover_taxonomies = discover_sub.add_parser("taxonomies", help="List available taxonomies (GET /taxonomies)")
    discover_taxonomies.add_argument("--include-raw", action="store_true", help="Include full raw response")
    discover_taxonomies.add_argument(
        "--context",
        choices=("view", "edit"),
        default="view",
        help="REST API context (default: view; use edit only if needed and allowed)",
    )
    discover_taxonomies.set_defaults(func=discover_cmd.cmd_discover_taxonomies)

    comments = sub.add_parser("comments", help="Comments (read-only)")
    comments_sub = comments.add_subparsers(dest="comments_cmd", required=True, parser_class=json_parser_class)

    comments_list = comments_sub.add_parser("list", help="List/filter comments (GET /comments)")
    comments_list.add_argument("--post-id", type=int, default=None, help="Filter: post id")
    comments_list.add_argument("--query", default=None, help="Filter: search query")
    comments_list.add_argument("--status", default=None, help="Filter: status (e.g. approve|hold|spam|trash)")
    comments_list.add_argument("--author", type=int, default=None, help="Filter: author user id")
    comments_list.add_argument("--parent", type=int, default=None, help="Filter: parent comment id")
    comments_list.add_argument("--type", default=None, help="Filter: comment type")
    comments_list.add_argument("--after", default=None, help="Filter: ISO8601 after")
    comments_list.add_argument("--before", default=None, help="Filter: ISO8601 before")
    comments_list.add_argument("--order", choices=("asc", "desc"), default=None)
    comments_list.add_argument("--orderby", default=None)
    comments_list.add_argument("--limit", type=int, default=50, help="Max comments to return (default: 50)")
    comments_list.add_argument("--per-page", type=int, default=None, help="Per-page (<=100; default: min(limit, 100))")
    comments_list.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="Pagination guardrail (<=100; default: 10)",
    )
    comments_list.add_argument(
        "--context",
        choices=("view", "edit"),
        default="view",
        help="REST API context (default: view; use edit only if needed and allowed)",
    )
    comments_list.set_defaults(func=comments_cmd.cmd_comments_list)

    comments_get = comments_sub.add_parser("get", help="Fetch comment by id (GET /comments/{id})")
    comments_get.add_argument("--id", type=int, required=True)
    comments_get.add_argument(
        "--context",
        choices=("view", "edit"),
        default="view",
        help="REST API context (default: view; use edit only if needed and allowed)",
    )
    comments_get.set_defaults(func=comments_cmd.cmd_comments_get)

    search = sub.add_parser("search", help="Search results (read-only)")
    search_sub = search.add_subparsers(dest="search_cmd", required=True, parser_class=json_parser_class)
    search_query = search_sub.add_parser("query", help="Query search results (GET /search)")
    search_query.add_argument("--query", required=True, help="Search query string")
    search_query.add_argument("--type", default=None, help="Filter: search type (e.g. post, term)")
    search_query.add_argument("--subtype", default=None, help="Filter: search subtype (e.g. posts, pages, category)")
    search_query.add_argument("--limit", type=int, default=50, help="Max results to return (default: 50)")
    search_query.add_argument("--per-page", type=int, default=None, help="Per-page (<=100; default: min(limit, 100))")
    search_query.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="Pagination guardrail (<=100; default: 10)",
    )
    search_query.set_defaults(func=search_cmd.cmd_search_query)

    settings = sub.add_parser("settings", help="Settings snapshot (read-only; often admin-only)")
    settings_sub = settings.add_subparsers(dest="settings_cmd", required=True, parser_class=json_parser_class)
    settings_get = settings_sub.add_parser("get", help="Fetch site settings (GET /settings)")
    settings_get.add_argument(
        "--context",
        choices=("view", "edit"),
        default="view",
        help="REST API context (default: view; use edit only if needed and allowed)",
    )
    settings_get.set_defaults(func=settings_cmd.cmd_settings_get)

    terms = sub.add_parser("terms", help="Terms (categories/tags) (read-only)")
    terms_sub = terms.add_subparsers(dest="terms_cmd", required=True, parser_class=json_parser_class)

    terms_list = terms_sub.add_parser("list", help="List/search terms (GET /categories or /tags)")
    terms_list.add_argument("--taxonomy", choices=("categories", "tags"), required=True)
    terms_list.add_argument("--query", default=None, help="Filter: search query")
    terms_list.add_argument("--slug", default=None, help="Filter: slug")
    terms_list.add_argument("--hide-empty", action="store_true", help="Filter: hide empty terms")
    terms_list.add_argument("--limit", type=int, default=50, help="Max results to return (default: 50)")
    terms_list.add_argument("--per-page", type=int, default=None, help="Per-page (<=100; default: min(limit, 100))")
    terms_list.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="Pagination guardrail (<=100; default: 10)",
    )
    terms_list.add_argument(
        "--context",
        choices=("view", "edit"),
        default="view",
        help="REST API context (default: view; use edit only if needed and allowed)",
    )
    terms_list.set_defaults(func=terms_cmd.cmd_terms_list)

    terms_get = terms_sub.add_parser("get", help="Fetch a term by id (GET /categories/{id} or /tags/{id})")
    terms_get.add_argument("--taxonomy", choices=("categories", "tags"), required=True)
    terms_get.add_argument("--id", type=int, required=True)
    terms_get.add_argument(
        "--context",
        choices=("view", "edit"),
        default="view",
        help="REST API context (default: view; use edit only if needed and allowed)",
    )
    terms_get.set_defaults(func=terms_cmd.cmd_terms_get)

    users = sub.add_parser("users", help="Users (read-only; often permission-restricted)")
    users_sub = users.add_subparsers(dest="users_cmd", required=True, parser_class=json_parser_class)

    users_list = users_sub.add_parser("list", help="List/search users (GET /users)")
    users_list.add_argument("--query", default=None, help="Filter: search query")
    users_list.add_argument("--slug", default=None, help="Filter: slug")
    users_list.add_argument("--limit", type=int, default=50, help="Max results to return (default: 50)")
    users_list.add_argument("--per-page", type=int, default=None, help="Per-page (<=100; default: min(limit, 100))")
    users_list.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="Pagination guardrail (<=100; default: 10)",
    )
    users_list.add_argument(
        "--context",
        choices=("view", "edit"),
        default="view",
        help="REST API context (default: view; use edit only if needed and allowed)",
    )
    users_list.set_defaults(func=users_cmd.cmd_users_list)

    users_get = users_sub.add_parser("get", help="Fetch a user by id (GET /users/{id})")
    users_get.add_argument("--id", type=int, required=True)
    users_get.add_argument(
        "--context",
        choices=("view", "edit"),
        default="view",
        help="REST API context (default: view; use edit only if needed and allowed)",
    )
    users_get.set_defaults(func=users_cmd.cmd_users_get)

    post = sub.add_parser("post", help="Post/page operations")
    post_sub = post.add_subparsers(dest="post_cmd", required=True, parser_class=json_parser_class)
    post_common(post_sub)

    media = sub.add_parser("media", help="Media (attachments) operations")
    media_sub = media.add_subparsers(dest="media_cmd", required=True, parser_class=json_parser_class)
    media_get = media_sub.add_parser("get", help="Fetch media item by attachment ID")
    media_get.add_argument("--id", type=int, required=True)
    media_get.set_defaults(func=media_cmd.cmd_media_get)

    media_find = media_sub.add_parser("find", help="Search/list media (GET /media) (read-only)")
    media_find.add_argument("--query", default=None, help="Search query (maps to ?search=...)")
    media_find.add_argument("--limit", type=int, default=50, help="Max results to return (default: 50)")
    media_find.add_argument("--per-page", type=int, default=None, help="Per-page (<=100; default: min(limit, 100))")
    media_find.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="Pagination guardrail (<=100; default: 10)",
    )
    media_find.add_argument(
        "--context",
        choices=("view", "edit"),
        default="view",
        help="REST API context (default: view; use edit only if needed and allowed)",
    )
    media_find.set_defaults(func=media_cmd.cmd_media_find)

    media_resolve = media_sub.add_parser("resolve", help="Resolve a media item by source URL (read-only)")
    media_resolve.add_argument("--url", required=True, help="Full media URL (source_url)")
    media_resolve.set_defaults(func=media_cmd.cmd_media_resolve)

    media_download = media_sub.add_parser("download", help="Download a media file (read-only)")
    media_download.add_argument("--id", type=int, default=None, help="Attachment ID")
    media_download.add_argument("--url", default=None, help="Full media URL (source_url)")
    media_download.add_argument(
        "--out-dir",
        default=None,
        help="Output directory (default: <project_dir>/cache/wp-media)",
    )
    media_download.set_defaults(func=media_cmd.cmd_media_download)

    media_download_batch = media_sub.add_parser(
        "download-batch",
        help="Download many media files from a CSV/JSON file (dry-run by default)",
    )
    media_download_batch.add_argument("--file", required=True, help="Input file (.csv or .json) with id/url/filename")
    media_download_batch.add_argument(
        "--out-dir",
        default=None,
        help="Output directory (default: <project_dir>/cache/wp-media)",
    )
    media_download_batch.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip downloads when the output file already exists",
    )
    media_download_batch.add_argument(
        "--max-items",
        type=int,
        default=500,
        help="Guardrail: max items allowed (default: 500; hard cap: 5000)",
    )
    media_download_batch.set_defaults(func=media_cmd.cmd_media_download_batch)

    media_set = media_sub.add_parser("set", help="Update media metadata (dry-run by default)")
    media_set.add_argument("--id", type=int, required=True)
    media_set.add_argument("--caption", default=None, help="Plain text caption")
    media_set.add_argument("--alt-text", default=None, help="Plain text alt text")
    media_set.add_argument("--title", default=None, help="Plain text title")
    media_set.set_defaults(func=media_cmd.cmd_media_set)

    media_set_batch = media_sub.add_parser(
        "set-batch",
        help="Update many media items from a JSON file (dry-run by default)",
    )
    media_set_batch.add_argument("--file", required=True, help="JSON file with updates")
    media_set_batch.set_defaults(func=media_cmd.cmd_media_set_batch)

    migration = sub.add_parser("migration", help="Helpers for mapping/exporting content (read-only)")
    migration_sub = migration.add_subparsers(dest="migration_cmd", required=True, parser_class=json_parser_class)
    track = migration_sub.add_parser(
        "tracking-from-xml",
        help="Generate a tracking CSV from WordPress export XML files (read-only)",
    )
    track.add_argument(
        "--xml",
        action="append",
        required=True,
        help="Path to a WordPress export XML file (repeatable)",
    )
    track.add_argument(
        "--out",
        default=None,
        help="Output CSV path (default: <project_dir>/tracking.csv)",
    )
    track.add_argument(
        "--append",
        action="store_true",
        help="Append unique posts to an existing CSV (preserves existing rows/columns)",
    )
    track.set_defaults(func=migration_cmd.cmd_tracking_from_xml)

    jobs = sub.add_parser("jobs", help="Batch operations from job files")
    jobs_sub = jobs.add_subparsers(dest="jobs_cmd", required=True, parser_class=json_parser_class)
    jobs_run = jobs_sub.add_parser("run", help="Run a CSV/JSON job file (dry-run by default)")
    jobs_run.add_argument("--file", required=True, help="Path to job file (.csv or .json)")
    jobs_run.add_argument("--limit", type=int, default=None, help="Max number of job rows to process")
    jobs_run.set_defaults(func=jobs_cmd.cmd_jobs_run)

    return p


def _apply_project_defaults(args: argparse.Namespace) -> None:
    project_cfg, config_dir = load_project_config(str(getattr(args, "config", None) or "") or None)
    setattr(args, "_project_cfg", project_cfg)
    project_dir_arg = str(getattr(args, "project_dir", "") or "").strip()
    if project_dir_arg:
        project_dir = project_dir_arg
    else:
        cfg_v = project_cfg.get("project_dir")
        if isinstance(cfg_v, str) and cfg_v.strip():
            project_dir = str((config_dir / cfg_v) if (config_dir is not None and not Path(cfg_v).is_absolute()) else cfg_v)
        elif config_dir is not None:
            project_dir = str(config_dir)
        else:
            project_dir = "."
    setattr(args, "_project_dir", project_dir)

    # Only apply defaults for the relevant subcommands.
    if str(getattr(args, "cmd", "") or "") == "media" and str(getattr(args, "media_cmd", "") or "") in {"download", "download-batch"}:
        if getattr(args, "out_dir", None) is None:
            cfg_out = project_cfg.get("wp_media_out_dir")
            args.out_dir = str(cfg_out) if isinstance(cfg_out, str) and cfg_out.strip() else str(Path(project_dir) / "cache" / "wp-media")

    if str(getattr(args, "cmd", "") or "") == "migration" and str(getattr(args, "migration_cmd", "") or "") == "tracking-from-xml":
        if getattr(args, "out", None) is None:
            cfg_out = project_cfg.get("tracking_csv")
            args.out = str(cfg_out) if isinstance(cfg_out, str) and cfg_out.strip() else str(Path(project_dir) / "tracking.csv")


def post_common(post_sub: argparse._SubParsersAction) -> None:
    post_find = post_sub.add_parser("find", help="Search posts by query")
    post_find.add_argument("--query", required=True)
    post_find.add_argument("--post-type", default="posts", help="WP REST type (default: posts)")
    post_find.add_argument("--limit", type=int, default=20)
    post_find.set_defaults(func=post_cmd.cmd_post_find)

    post_get = post_sub.add_parser("get", help="Fetch post by slug")
    post_get.add_argument("--slug", required=True)
    post_get.add_argument("--post-type", default="posts")
    post_get.add_argument("--include-raw", action="store_true", help="Include raw content")
    post_get.set_defaults(func=post_cmd.cmd_post_get)

    post_truth = post_sub.add_parser(
        "truth",
        help="Fetch a post with source-of-truth details (images, featured, terms) (read-only)",
    )
    post_truth.add_argument("--slug", default=None, help="Post slug")
    post_truth.add_argument("--id", type=int, default=None, help="Post id")
    post_truth.add_argument("--post-type", default="posts")
    post_truth.add_argument(
        "--resolve-urls",
        action="store_true",
        help="Try to resolve <img src> URLs to Media Library IDs (slower)",
    )
    post_truth.set_defaults(func=post_cmd.cmd_post_truth)

    post_images = post_sub.add_parser("images", help="List images referenced by the post")
    post_images.add_argument("--slug", required=True)
    post_images.add_argument("--post-type", default="posts")
    post_images.add_argument("--include-featured", action="store_true")
    post_images.set_defaults(func=post_cmd.cmd_post_images)

    post_set_caps = post_sub.add_parser(
        "set-image-captions",
        help="Update captions/alt inside post content (Gutenberg image blocks only)",
    )
    post_set_caps.add_argument("--slug", required=True)
    post_set_caps.add_argument("--post-type", default="posts")
    post_set_caps.add_argument("--caption", default=None, help="Plain text caption")
    post_set_caps.add_argument("--caption-html", default=None, help="HTML caption (advanced)")
    post_set_caps.add_argument(
        "--captions-file",
        default=None,
        help="JSON mapping of attachment id -> caption (updates multiple images in one post update)",
    )
    post_set_caps.add_argument("--alt-text", default=None, help="Plain text alt text")
    post_set_caps.add_argument(
        "--only-ids",
        default=None,
        help="Comma-separated list of attachment IDs to target",
    )
    post_set_caps.add_argument("--diff", action="store_true", help="Include unified diff")
    post_set_caps.set_defaults(func=post_cmd.cmd_post_set_image_captions)

    post_set_status = post_sub.add_parser(
        "set-status",
        help="Change post status (dry-run by default; require --apply)",
    )
    post_set_status.add_argument("--slug", default=None, help="Target post slug (recommended)")
    post_set_status.add_argument("--id", type=int, default=None, help="Target post id")
    post_set_status.add_argument("--post-type", default="posts")
    post_set_status.add_argument("--to", required=True, help="New status (e.g. publish)")
    post_set_status.add_argument(
        "--require-current",
        default=None,
        help="Refuse unless current status matches (e.g. draft)",
    )
    post_set_status.set_defaults(func=post_cmd.cmd_post_set_status)

    post_set_terms = post_sub.add_parser(
        "set-terms",
        help="Set categories/tags for a post (dry-run by default; require --apply)",
    )
    post_set_terms.add_argument("--slug", default=None, help="Target post slug (recommended)")
    post_set_terms.add_argument("--id", type=int, default=None, help="Target post id")
    post_set_terms.add_argument("--post-type", default="posts")
    post_set_terms.add_argument(
        "--set",
        action="store_true",
        help="Explicit full replacement of the specified taxonomies (required)",
    )
    post_set_terms.add_argument("--category-id", action="append", type=int, default=None, help="Category term id (repeatable)")
    post_set_terms.add_argument("--category-slug", action="append", default=None, help="Category term slug (repeatable)")
    post_set_terms.add_argument("--clear-categories", action="store_true", help="Set categories to []")
    post_set_terms.add_argument("--tag-id", action="append", type=int, default=None, help="Tag term id (repeatable)")
    post_set_terms.add_argument("--tag-slug", action="append", default=None, help="Tag term slug (repeatable)")
    post_set_terms.add_argument("--clear-tags", action="store_true", help="Set tags to []")
    post_set_terms.set_defaults(func=post_cmd.cmd_post_set_terms)

    post_replace = post_sub.add_parser(
        "replace-in-content",
        help="Replace an exact string inside post content.raw (dry-run by default; require --apply)",
    )
    post_replace.add_argument("--slug", default=None, help="Target post slug (recommended)")
    post_replace.add_argument("--id", type=int, default=None, help="Target post id")
    post_replace.add_argument("--post-type", default="posts")
    post_replace.add_argument("--from", dest="from_text", required=True, help="Exact string to replace")
    post_replace.add_argument("--to", dest="to_text", required=True, help="Replacement string")
    post_replace.add_argument(
        "--expected-count",
        type=int,
        required=True,
        help="Guardrail: refuse unless the source string occurs exactly N times",
    )
    post_replace.add_argument(
        "--max-replacements",
        type=int,
        default=None,
        help="Max replacements to perform (default: expected-count)",
    )
    post_replace.add_argument(
        "--backup-out",
        default=None,
        help="Write a pre-change content.raw snapshot to this path (required with --apply)",
    )
    post_replace.add_argument("--diff", action="store_true", help="Include unified diff in output")
    post_replace.set_defaults(func=post_cmd.cmd_post_replace_in_content)


def main(argv: list[str]) -> int:
    json_mode = _detect_output_mode(argv) != "text"
    out = Output(mode=_detect_output_mode(argv))
    parser = build_parser(json_mode=json_mode)

    try:
        args = parser.parse_args(argv)
    except _ParserExit as e:
        if _detect_output_mode(argv) == "json":
            if e.kind == "help":
                out.emit({"ok": True, "kind": "help", "help": e.help_text or ""})
                return 0
            if e.kind == "version":
                out.emit({"ok": True, "tool": "wordpress-api-tool", "version": __version__})
                return 0
            if e.kind == "usage_error":
                payload = {
                    "ok": False,
                    "error": e.message or "Invalid arguments",
                    "error_type": "ValidationError",
                }
                if e.usage:
                    payload["usage"] = e.usage
                out.emit(payload)
                return 2
            out.emit({"ok": False, "error": e.message or "Exited", "error_type": "ValidationError"})
            return int(e.status or 0)
        return int(e.status or 0)
    except SystemExit as e:
        try:
            return int(e.code or 0)
        except Exception:
            return 0

    out = Output(mode=args.output)
    audit = AuditLogger(path=args.log_file, enabled=bool(args.log_file))

    try:
        _apply_project_defaults(args)

        if bool(getattr(args, "version", False)):
            payload = {"ok": True, "tool": "wordpress-api-tool", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"wordpress-api-tool {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            msg = "Missing command. Use --help to see available commands."
            if args.output == "json":
                out.emit({"ok": False, "error": msg, "error_type": "ValidationError"})
                return 2
            print(msg, file=sys.stderr)
            return 2

        cfg = load_config(args.env_file)
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "project_cfg": getattr(args, "_project_cfg", {}) or {},
            "project_dir": str(getattr(args, "_project_dir", ".") or "."),
            "env_file": str(args.env_file),
            "timeout_s": float(args.timeout_s),
            "verbose": bool(args.verbose),
            "apply": bool(args.apply),
            "yes": bool(args.yes),
            "ack_no_snapshot": bool(args.ack_no_snapshot),
            "argv": list(argv),
            "plan_out": args.plan_out,
            "receipt_out": args.receipt_out,
            "before_state_run_id": v2util.default_run_id(),
        }
        return int(args.func(args, ctx))
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    except Exception as e:  # noqa: BLE001
        if bool(args.debug):
            raise
        audit.write("error", {"error": str(e), "error_type": type(e).__name__})
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        return 1
    finally:
        audit.close()
