from __future__ import annotations

import argparse
import dataclasses
import sys
from dataclasses import dataclass
from functools import partial
from typing import Any

from . import __version__
from .audit_log import AuditLogger
from .commands import auth as auth_cmd
from .commands import download as download_cmd
from .commands import jobs as jobs_cmd
from .commands import preview as preview_cmd
from .commands import resource as resource_cmd
from .commands import search as search_cmd
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


class _JsonArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args: Any, json_mode: bool = False, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._json_mode = bool(json_mode)
        self._captured_help: str | None = None

    def print_help(self, file: Any | None = None) -> None:  # noqa: ANN401
        if not self._json_mode:
            return super().print_help(file=file)
        self._captured_help = self.format_help()

    def exit(self, status: int = 0, message: str | None = None) -> None:
        if not self._json_mode:
            return super().exit(status=status, message=message)
        help_text = self._captured_help
        kind = "exit"
        if status == 0 and help_text:
            kind = "help"
        elif status == 0 and message and message.strip().startswith(f"{self.prog} "):
            kind = "version"
        raise _ParserExit(status=status, kind=kind, message=message, help_text=help_text)

    def error(self, message: str) -> None:
        if not self._json_mode:
            return super().error(message)
        raise _ParserExit(status=2, kind="usage_error", message=message, usage=self.format_usage())


def _detect_output_mode(argv: list[str]) -> str:
    for i, a in enumerate(argv):
        if a == "--output" and i + 1 < len(argv):
            return str(argv[i + 1]).strip()
        if a.startswith("--output="):
            return str(a.split("=", 1)[1]).strip()
    return "json"


def build_parser(*, json_mode: bool) -> argparse.ArgumentParser:
    p = _JsonArgumentParser(prog="freepik-api-tool", json_mode=json_mode)
    if json_mode:
        p.add_argument("--version", action="store_true", help="Print tool version and exit")
    else:
        p.add_argument("--version", action="version", version=f"freepik-api-tool {__version__}")
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
    p.add_argument(
        "--accept-language",
        default=None,
        help="Optional Accept-Language header (e.g. en-US). Overrides FREEPIK_ACCEPT_LANGUAGE.",
    )
    p.add_argument(
        "--output",
        choices=("json", "text"),
        default="json",
        help="Output format (default: json)",
    )
    p.add_argument("--log-file", default=None, help="Optional audit log path (JSONL)")
    p.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    p.add_argument("--yes", action="store_true", help="Additional confirmation for batch jobs")
    p.add_argument(
        "--ack-no-snapshot",
        action="store_true",
        help="Acknowledge that this approved write may run without a saved before-state snapshot",
    )

    json_parser_class = partial(_JsonArgumentParser, json_mode=json_mode)

    sub = p.add_subparsers(dest="cmd", required=True, parser_class=json_parser_class)

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=json_parser_class)
    auth_check = auth_sub.add_parser("check", help="Smoke test credentials (GET /resources?limit=1)")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check)

    search = sub.add_parser("search", help="Search resources")
    search_sub = search.add_subparsers(dest="search_cmd", required=True, parser_class=json_parser_class)
    search_images = search_sub.add_parser("images", help="Search images/templates")
    search_images.add_argument("--query", required=True, help="Search query")
    search_images.add_argument("--limit", type=int, default=20)
    search_images.add_argument("--page", type=int, default=1)
    search_images.add_argument(
        "--param",
        action="append",
        default=[],
        help="Additional query parameter (key=value), repeatable",
    )
    search_images.add_argument(
        "--shortlist",
        action="store_true",
        help="Emit a compact, stable JSON shortlist optimized for selection",
    )
    search_images.add_argument(
        "--write-jobs",
        default=None,
        help="Write a jobs CSV compatible with `jobs run` (local-only file output)",
    )
    search_images.add_argument(
        "--job-format",
        default="jpg",
        help="Job download format for `--write-jobs` (default: jpg)",
    )
    search_images.add_argument(
        "--job-image-size",
        default=None,
        help="Optional `image_size` column value for `--write-jobs` (e.g. 2000px)",
    )
    search_images.add_argument(
        "--exclude-ai",
        action="store_true",
        help=(
            "Exclude AI-generated results by fetching each resource detail and filtering on "
            "`is_ai_generated`/`has_prompt` (slower)."
        ),
    )
    search_images.set_defaults(func=search_cmd.cmd_search_images)

    search_photos = search_sub.add_parser("photos", help="Search photos (photo-first defaults)")
    search_photos.add_argument("--query", required=True, help="Search query")
    search_photos.add_argument("--limit", type=int, default=20)
    search_photos.add_argument("--page", type=int, default=1)
    search_photos.add_argument(
        "--param",
        action="append",
        default=[],
        help="Additional query parameter (key=value), repeatable",
    )
    search_photos.add_argument(
        "--shortlist",
        action="store_true",
        help="Emit a compact, stable JSON shortlist optimized for selection",
    )
    search_photos.add_argument(
        "--write-jobs",
        default=None,
        help="Write a jobs CSV compatible with `jobs run` (local-only file output)",
    )
    search_photos.add_argument(
        "--job-format",
        default="jpg",
        help="Job download format for `--write-jobs` (default: jpg)",
    )
    search_photos.add_argument(
        "--job-image-size",
        default=None,
        help="Optional `image_size` column value for `--write-jobs` (e.g. 2000px)",
    )
    search_photos.add_argument(
        "--exclude-ai",
        action="store_true",
        help=(
            "Exclude AI-generated results by fetching each resource detail and filtering on "
            "`is_ai_generated`/`has_prompt` (slower)."
        ),
    )
    search_photos.set_defaults(func=search_cmd.cmd_search_photos)

    resource = sub.add_parser("resource", help="Resource operations")
    resource_sub = resource.add_subparsers(dest="resource_cmd", required=True, parser_class=json_parser_class)
    resource_get = resource_sub.add_parser("get", help="Get resource details by id")
    resource_get.add_argument("--id", required=True, help="Resource id")
    resource_get.set_defaults(func=resource_cmd.cmd_resource_get)
    resource_related = resource_sub.add_parser(
        "related",
        help="Find related resources (API-native if available; otherwise tag-based search)",
    )
    resource_related.add_argument("--id", required=True, help="Resource id")
    resource_related.add_argument("--limit", type=int, default=20)
    resource_related.set_defaults(func=resource_cmd.cmd_resource_related)

    resource_shoot_pack = resource_sub.add_parser(
        "shoot-pack",
        help="Export a deterministic 'same shoot' pack when available (or fall back to related/search)",
    )
    resource_shoot_pack.add_argument("--id", required=True, help="Resource id")
    resource_shoot_pack.add_argument("--limit", type=int, default=50)
    resource_shoot_pack.add_argument("--same-series", action="store_true", help="Include same_series group")
    resource_shoot_pack.add_argument("--same-collection", action="store_true", help="Include same_collection group")
    resource_shoot_pack.add_argument("--same-author", action="store_true", help="Include same_author group")
    resource_shoot_pack.add_argument("--suggested", action="store_true", help="Include suggested group (when present)")
    resource_shoot_pack.add_argument(
        "--write-jobs",
        default=None,
        help="Write a jobs CSV compatible with `jobs run` (local-only file output)",
    )
    resource_shoot_pack.add_argument(
        "--job-format",
        default="jpg",
        help="Job download format for `--write-jobs` (default: jpg)",
    )
    resource_shoot_pack.add_argument(
        "--job-image-size",
        default=None,
        help="Optional `image_size` column value for `--write-jobs` (e.g. 2000px)",
    )
    resource_shoot_pack.set_defaults(func=resource_cmd.cmd_resource_shoot_pack)

    preview = sub.add_parser("preview", help="Preview a resource without licensing/downloading it")
    preview.add_argument("--id", required=True, help="Resource id")
    preview.add_argument("--save-preview", default=None, help="Optional directory to save preview image")
    preview.set_defaults(func=preview_cmd.cmd_preview)

    download = sub.add_parser("download", help="Download a resource (dry-run by default)")
    download.add_argument("--id", required=True, help="Resource id")
    download.add_argument("--format", required=True, help="Requested download format (e.g., jpg, png)")
    download.add_argument("--out-dir", default=None, help="Directory to save downloaded file(s) (or use project config `downloads_dir`)")
    download.add_argument("--inventory", default=None, help="Inventory CSV path (append/update) (or use project config `inventory_csv`)")
    download.add_argument(
        "--post-slug",
        default="",
        help="Optional post slug to record in the inventory ledger (e.g., Ghost post slug)",
    )
    download.add_argument(
        "--ghost-id",
        default="",
        help="Optional Ghost post id to record in the inventory ledger",
    )
    download.add_argument(
        "--usage-role",
        default="",
        choices=["", "featured", "body"],
        help="Optional usage role to record in the inventory ledger",
    )
    download.add_argument(
        "--image-size",
        default=None,
        help=(
            "Photo resize for the /download endpoint: small|medium|large|original or 100px..2000px. "
            "Overrides FREEPIK_IMAGE_SIZE. Only used when calling the /download (no-format) endpoint."
        ),
    )
    download.add_argument(
        "--download-url-jsonpath",
        default=None,
        help="Optional JSONPath to find download URL in the download JSON response",
    )
    download.add_argument(
        "--license-url-jsonpath",
        default=None,
        help="Optional JSONPath to find license PDF URL in the resource detail JSON",
    )
    download.add_argument(
        "--force",
        action="store_true",
        help="Allow re-downloading a resource already present in inventory",
    )
    download.set_defaults(func=download_cmd.cmd_download)

    jobs = sub.add_parser("jobs", help="Batch operations from job files")
    jobs_sub = jobs.add_subparsers(dest="jobs_cmd", required=True, parser_class=json_parser_class)
    jobs_run = jobs_sub.add_parser("run", help="Run a CSV job file (downloads; dry-run by default)")
    jobs_run.add_argument("--file", required=True, help="Job CSV file")
    jobs_run.add_argument("--out-dir", default=None, help="Directory to save downloaded file(s) (or use project config `downloads_dir`)")
    jobs_run.add_argument("--inventory", default=None, help="Inventory CSV path (append/update) (or use project config `inventory_csv`)")
    jobs_run.add_argument("--limit", type=int, default=None, help="Max number of rows to process")
    jobs_run.set_defaults(func=jobs_cmd.cmd_jobs_run)

    return p


def main(argv: list[str]) -> int:
    output_mode = _detect_output_mode(argv)
    json_mode = output_mode == "json"

    if json_mode and "--version" in argv:
        Output(mode="json").emit({"ok": True, "tool": "freepik-api-tool", "version": __version__})
        return 0

    parser = build_parser(json_mode=json_mode)
    if json_mode:
        out = Output(mode="json")
        try:
            args = parser.parse_args(argv)
        except _ParserExit as e:
            if e.kind == "help":
                out.emit({"ok": True, "tool": "freepik-api-tool", "version": __version__, "help": e.help_text or ""})
                return int(e.status)
            if e.kind == "version":
                out.emit({"ok": True, "tool": "freepik-api-tool", "version": __version__})
                return 0
            if e.kind == "usage_error":
                out.emit({"ok": False, "error": e.message or "Invalid arguments", "error_type": "UsageError"})
                return int(e.status)
            out.emit({"ok": False, "error": e.message or "Exited", "error_type": "UsageError"})
            return int(e.status)
    else:
        args = parser.parse_args(argv)

    out = Output(mode=args.output)
    audit = AuditLogger(path=args.log_file, enabled=bool(args.log_file))

    try:
        cfg = load_config(args.env_file)
        if args.accept_language is not None:
            cfg = dataclasses.replace(cfg, accept_language=(str(args.accept_language).strip() or None))
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        project_cfg, cfg_base_dir = load_project_config(getattr(args, "config", None))
        project_dir = Path(str(getattr(args, "project_dir", "") or "")).expanduser()
        if not str(getattr(args, "project_dir", "") or "").strip():
            project_dir = cfg_base_dir or Path.cwd()
        project_dir = project_dir.resolve()

        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "timeout_s": timeout_s,
            "verbose": bool(args.verbose),
            "apply": bool(args.apply),
            "yes": bool(args.yes),
            "ack_no_snapshot": bool(args.ack_no_snapshot),
            "project_cfg": project_cfg,
            "project_dir": str(project_dir),
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
