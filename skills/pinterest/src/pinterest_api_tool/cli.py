from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger
from .commands import auth as auth_cmd
from .commands import analytics as analytics_cmd
from .commands import ads as ads_cmd
from .commands import audit as audit_cmd
from .commands import boards as boards_cmd
from .commands import catalogs as catalogs_cmd
from .commands import business_access as business_access_cmd
from .commands import conversions as conversions_cmd
from .commands import jobs as jobs_cmd
from .commands import pin_links as pin_links_cmd
from .commands import pins as pins_cmd
from .commands import report_jobs as report_jobs_cmd
from .commands import resources as resources_cmd
from .commands import user_account as user_account_cmd
from .config import load_config
from .http import HttpClient
from .output import Output
from .project_config import load_project_config


class ValidationError(Exception):
    pass


def _argv_output_mode(argv: list[str]) -> str:
    # Default is json.
    for i, tok in enumerate(argv):
        if tok == "--output" and i + 1 < len(argv):
            return str(argv[i + 1])
        if tok.startswith("--output="):
            return tok.split("=", 1)[1]
    return "json"


def _argv_wants_json(argv: list[str]) -> bool:
    return _argv_output_mode(argv) != "text"


def build_parser() -> argparse.ArgumentParser:
    class _JsonAwareParser(argparse.ArgumentParser):
        def parse_args(self, args=None, namespace=None):  # type: ignore[override]
            self._raw_args = list(args) if args is not None else sys.argv[1:]
            return super().parse_args(args=args, namespace=namespace)

        def error(self, message: str) -> None:  # type: ignore[override]
            raw = getattr(self, "_raw_args", sys.argv[1:])
            if _argv_wants_json(list(raw)):
                raise ValidationError(message)
            super().error(message)

    p = _JsonAwareParser(prog="pinterest-api-tool")
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
    p.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    p.add_argument("--yes", action="store_true", help="Additional confirmation for destructive/batch actions")
    p.add_argument(
        "--ack-no-snapshot",
        action="store_true",
        help="Acknowledge that this approved write may run without a saved before-state snapshot",
    )
    p.add_argument(
        "--ack-irreversible",
        action="store_true",
        help="Acknowledge irreversible/destructive changes (required for delete operations)",
    )
    p.add_argument(
        "--ack-spend",
        action="store_true",
        help="Acknowledge spend risk for ads operations that can increase spend",
    )
    p.add_argument(
        "--ack-volume",
        action="store_true",
        help="Acknowledge volume/cost risk for operations that can trigger significant remote work",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    auth = sub.add_parser("auth", help="Authentication checks and local token setup")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True)
    auth_check = auth_sub.add_parser("check", help="Smoke test credentials")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check)

    auth_login = auth_sub.add_parser(
        "login",
        help="Start a localhost OAuth flow and write local token state (requires --yes --ack-no-snapshot)",
    )
    auth_login.add_argument(
        "--redirect-uri",
        default="http://localhost:8765/",
        help="Redirect URI to listen on (must be registered in Pinterest app; default: http://localhost:8765/)",
    )
    auth_login.add_argument(
        "--scopes",
        default="boards:read,pins:read,pins:write,user_accounts:read",
        help="Comma-separated OAuth scopes (default includes pins:write for demos)",
    )
    auth_login.add_argument("--state", default=None, help="Optional OAuth state (default: random)")
    auth_login.add_argument(
        "--continuous-refresh",
        action="store_true",
        help="Request continuous refresh tokens (recommended for long-term use)",
    )
    auth_login.add_argument(
        "--wait-timeout-s",
        type=float,
        default=180.0,
        help="Seconds to wait for the OAuth redirect (default: 180)",
    )
    auth_login.add_argument(
        "--no-open-browser",
        action="store_true",
        help="Do not try to open a browser automatically (prints URL instead)",
    )
    auth_login.set_defaults(func=auth_cmd.cmd_auth_login)

    token = auth_sub.add_parser("token", help="OAuth token helpers (manual copy/paste; writes local token state)")
    token_sub = token.add_subparsers(dest="token_cmd", required=True)
    token_set = token_sub.add_parser(
        "set",
        help="Store token JSON under .state/token.json (requires --yes --ack-no-snapshot)",
    )
    token_set.add_argument("--file", required=True, help="Token JSON file path (input)")
    token_set.set_defaults(func=auth_cmd.cmd_auth_token_set)
    token_status = token_sub.add_parser("status", help="Show token status (never prints token values)")
    token_status.set_defaults(func=auth_cmd.cmd_auth_token_status)

    code = auth_sub.add_parser("code", help="OAuth authorization-code helpers (local token setup)")
    code_sub = code.add_subparsers(dest="code_cmd", required=True)
    code_exchange = code_sub.add_parser(
        "exchange",
        help="Exchange an OAuth authorization code and write local token state (requires --yes --ack-no-snapshot)",
    )
    code_exchange.add_argument("--code", required=True, help="Authorization code from redirect URL")
    code_exchange.add_argument(
        "--redirect-uri",
        default="http://localhost/",
        help="Redirect URI used in the OAuth flow (default: http://localhost/)",
    )
    code_exchange.add_argument(
        "--continuous-refresh",
        action="store_true",
        help="Request continuous refresh tokens (recommended for long-term use)",
    )
    code_exchange.set_defaults(func=auth_cmd.cmd_auth_code_exchange)

    boards = sub.add_parser("boards", help="Boards inventory")
    boards_sub = boards.add_subparsers(dest="boards_cmd", required=True)
    boards_list = boards_sub.add_parser("list", help="List boards")
    boards_list.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    boards_list.add_argument("--privacy", default=None, help='Optional: PUBLIC, PROTECTED, or SECRET')
    boards_list.add_argument("--limit", type=int, default=100, help="Max items to return (default: 100)")
    boards_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    boards_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    boards_list.set_defaults(func=boards_cmd.cmd_boards_list)
    boards_get = boards_sub.add_parser("get", help="Get a board")
    boards_get.add_argument("--id", required=True, help="Board id")
    boards_get.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    boards_get.set_defaults(func=boards_cmd.cmd_boards_get)

    boards_create = boards_sub.add_parser("create", help="Create a board (dry-run by default; requires --apply --yes)")
    boards_create.add_argument("--name", required=True, help="Board name")
    boards_create.add_argument("--description", default=None, help="Optional board description")
    boards_create.add_argument("--privacy", default=None, help="Optional: PUBLIC, PROTECTED, or SECRET")
    boards_create.add_argument("--is-ads-only", action="store_true", help="Create an ad-only board (Pinterest may force privacy)")
    boards_create.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    boards_create.add_argument(
        "--scan-limit",
        type=int,
        default=5000,
        help="Max boards to scan for same-name duplicates (default: 5000)",
    )
    boards_create.add_argument(
        "--allow-mismatch",
        action="store_true",
        help="Allow applying even if a board with the same name already exists (not recommended)",
    )
    boards_create.set_defaults(func=boards_cmd.cmd_boards_create)

    boards_update = boards_sub.add_parser("update", help="Update a board (dry-run by default; requires --apply --yes)")
    boards_update.add_argument("--id", required=True, help="Board id")
    boards_update.add_argument("--name", default=None, help="Optional board name")
    boards_update.add_argument("--description", default=None, help="Optional board description")
    boards_update.add_argument("--privacy", default=None, help="Optional: PUBLIC, PROTECTED, or SECRET")
    boards_update.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    boards_update.set_defaults(func=boards_cmd.cmd_boards_update)

    boards_delete = boards_sub.add_parser(
        "delete",
        help="Delete a board (dry-run by default; requires --apply --yes --ack-irreversible)",
    )
    boards_delete.add_argument("--id", required=True, help="Board id")
    boards_delete.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    boards_delete.set_defaults(func=boards_cmd.cmd_boards_delete)

    boards_ensure = boards_sub.add_parser("ensure", help="Ensure a board exists (idempotent; dry-run by default)")
    boards_ensure.add_argument("--name", required=True, help="Board name")
    boards_ensure.add_argument("--description", default=None, help="Optional board description (sets if missing/different)")
    boards_ensure.add_argument("--privacy", default=None, help="Optional: PUBLIC, PROTECTED, or SECRET (sets if missing/different)")
    boards_ensure.add_argument("--is-ads-only", action="store_true", help="Create as ad-only if missing")
    boards_ensure.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    boards_ensure.add_argument(
        "--scan-limit",
        type=int,
        default=5000,
        help="Max boards to scan for same-name matches (default: 5000)",
    )
    boards_ensure.set_defaults(func=boards_cmd.cmd_boards_ensure)

    sections = sub.add_parser("board-sections", help="Board sections inventory")
    sections_sub = sections.add_subparsers(dest="sections_cmd", required=True)
    sections_list = sections_sub.add_parser("list", help="List board sections for a board")
    sections_list.add_argument("--board-id", required=True, help="Board id")
    sections_list.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    sections_list.add_argument("--limit", type=int, default=100, help="Max items to return (default: 100)")
    sections_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    sections_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    sections_list.set_defaults(func=boards_cmd.cmd_board_sections_list)

    sections_create = sections_sub.add_parser(
        "create",
        help="Create a board section (dry-run by default; requires --apply --yes)",
    )
    sections_create.add_argument("--board-id", required=True, help="Board id")
    sections_create.add_argument("--name", required=True, help="Section name")
    sections_create.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    sections_create.add_argument(
        "--scan-limit",
        type=int,
        default=5000,
        help="Max sections to scan for same-name duplicates (default: 5000)",
    )
    sections_create.add_argument(
        "--allow-mismatch",
        action="store_true",
        help="Allow applying even if a section with the same name already exists on this board (not recommended)",
    )
    sections_create.set_defaults(func=boards_cmd.cmd_board_sections_create)

    sections_update = sections_sub.add_parser(
        "update",
        help="Update a board section (dry-run by default; requires --apply --yes)",
    )
    sections_update.add_argument("--board-id", required=True, help="Board id")
    sections_update.add_argument("--section-id", required=True, help="Section id")
    sections_update.add_argument("--name", required=True, help="New section name")
    sections_update.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    sections_update.set_defaults(func=boards_cmd.cmd_board_sections_update)

    sections_delete = sections_sub.add_parser(
        "delete",
        help="Delete a board section (dry-run by default; requires --apply --yes --ack-irreversible)",
    )
    sections_delete.add_argument("--board-id", required=True, help="Board id")
    sections_delete.add_argument("--section-id", required=True, help="Section id")
    sections_delete.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    sections_delete.set_defaults(func=boards_cmd.cmd_board_sections_delete)

    sections_ensure = sections_sub.add_parser("ensure", help="Ensure a board section exists (idempotent; dry-run by default)")
    sections_ensure.add_argument("--board-id", required=True, help="Board id")
    sections_ensure.add_argument("--name", required=True, help="Section name")
    sections_ensure.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    sections_ensure.add_argument(
        "--scan-limit",
        type=int,
        default=5000,
        help="Max sections to scan for same-name matches (default: 5000)",
    )
    sections_ensure.set_defaults(func=boards_cmd.cmd_board_sections_ensure)

    pins = sub.add_parser("pins", help="Pins inventory")
    pins_sub = pins.add_subparsers(dest="pins_cmd", required=True)
    pins_list = pins_sub.add_parser("list", help="List Pins")
    pins_list.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    pins_list.add_argument("--limit", type=int, default=100, help="Max items to return (default: 100)")
    pins_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    pins_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    pins_list.add_argument("--include-protected-pins", action="store_true", help="Include Pins from protected boards")
    pins_list.add_argument("--pin-filter", default=None, help="Optional Pin filter (Pinterest API)")
    pins_list.add_argument("--pin-type", default=None, help="Optional Pin type (Pinterest API)")
    pins_list.add_argument(
        "--creative-types",
        default=None,
        help="Optional comma-separated creative types filter (Pinterest API)",
    )
    pins_list.add_argument("--pin-metrics", action="store_true", help="Include metrics in Pin list response")
    pins_list.set_defaults(func=pins_cmd.cmd_pins_list)
    pins_get = pins_sub.add_parser("get", help="Get a Pin")
    pins_get.add_argument("--id", required=True, help="Pin id")
    pins_get.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    pins_get.add_argument("--pin-metrics", action="store_true", help="Include metrics in Pin get response")
    pins_get.set_defaults(func=pins_cmd.cmd_pins_get)

    pins_create = pins_sub.add_parser("create", help="Create a Pin (dry-run by default; requires --apply --yes)")
    pins_create.add_argument("--board-id", required=True, help="Destination board id")
    pins_create.add_argument("--board-section-id", default=None, help="Optional destination board section id")
    pins_create.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    pins_create.add_argument(
        "--scan-limit",
        type=int,
        default=5000,
        help="Max destination pins to scan for duplicate canonical-link matches (default: 5000)",
    )
    pins_create.add_argument(
        "--allow-mismatch",
        action="store_true",
        help="Allow duplicates and bypass strict read-back verification mismatches (not recommended)",
    )
    pins_create.add_argument("--title", default=None, help="Optional Pin title")
    pins_create.add_argument("--description", default=None, help="Optional Pin description")
    pins_create.add_argument("--link", default=None, help="Optional destination URL (used for idempotence checks)")
    pins_create.add_argument("--alt-text", default=None, help="Optional alt text")
    pins_create.add_argument(
        "--media-source-type",
        required=True,
        choices=("image_url", "video_id", "image_base64"),
        help="Media source type discriminator",
    )
    pins_create.add_argument("--media-url", default=None, help="Required when --media-source-type=image_url")
    pins_create.add_argument("--media-id", default=None, help="Required when --media-source-type=video_id")
    pins_create.add_argument(
        "--media-content-type",
        default=None,
        help="Required when --media-source-type=image_base64 (example: image/jpeg)",
    )
    pins_create.add_argument("--media-data", default=None, help="Required when --media-source-type=image_base64 (base64 payload)")
    pins_create.set_defaults(func=pins_cmd.cmd_pins_create)

    pins_update = pins_sub.add_parser("update", help="Update a Pin (dry-run by default; requires --apply --yes)")
    pins_update.add_argument("--id", required=True, help="Pin id")
    pins_update.add_argument("--title", default=None, help="Optional Pin title")
    pins_update.add_argument("--description", default=None, help="Optional Pin description")
    pins_update.add_argument("--link", default=None, help="Optional destination URL")
    pins_update.add_argument("--alt-text", default=None, help="Optional alt text")
    pins_update.add_argument("--board-id", default=None, help="Optional destination board id")
    pins_update.add_argument("--board-section-id", default=None, help="Optional destination board section id")
    pins_update.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    pins_update.add_argument(
        "--allow-mismatch",
        action="store_true",
        help="Bypass strict read-back verification mismatches (not recommended)",
    )
    pins_update.set_defaults(func=pins_cmd.cmd_pins_update)

    pins_delete = pins_sub.add_parser(
        "delete",
        help="Delete a Pin (dry-run by default; requires --apply --yes --ack-irreversible)",
    )
    pins_delete.add_argument("--id", required=True, help="Pin id")
    pins_delete.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    pins_delete.set_defaults(func=pins_cmd.cmd_pins_delete)

    pins_save = pins_sub.add_parser("save", help="Save a Pin to a board/section (dry-run by default; requires --apply --yes)")
    pins_save.add_argument("--id", required=True, help="Source pin id")
    pins_save.add_argument("--board-id", required=True, help="Destination board id")
    pins_save.add_argument("--board-section-id", default=None, help="Optional destination board section id")
    pins_save.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    pins_save.add_argument(
        "--scan-limit",
        type=int,
        default=5000,
        help="Max destination pins to scan for already-saved detection (default: 5000)",
    )
    pins_save.add_argument(
        "--allow-mismatch",
        action="store_true",
        help="Allow saving even when already-saved detection finds a match (not recommended)",
    )
    pins_save.set_defaults(func=pins_cmd.cmd_pins_save)

    pins_ensure = pins_sub.add_parser("ensure", help="Ensure a Pin exists (idempotent; dry-run by default)")
    pins_ensure.add_argument("--board-id", required=True, help="Destination board id")
    pins_ensure.add_argument("--board-section-id", default=None, help="Optional destination board section id")
    pins_ensure.add_argument("--link", required=True, help="Destination URL (canonicalized for idempotence)")
    pins_ensure.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    pins_ensure.add_argument(
        "--scan-limit",
        type=int,
        default=5000,
        help="Max destination pins to scan for canonical-link matches (default: 5000)",
    )
    pins_ensure.add_argument(
        "--allow-mismatch",
        action="store_true",
        help="Allow creating even if strict read-back verification mismatches occur (not recommended)",
    )
    pins_ensure.add_argument("--title", default=None, help="Optional Pin title")
    pins_ensure.add_argument("--description", default=None, help="Optional Pin description")
    pins_ensure.add_argument("--alt-text", default=None, help="Optional alt text")
    pins_ensure.add_argument(
        "--media-source-type",
        required=True,
        choices=("image_url", "video_id", "image_base64"),
        help="Media source type discriminator",
    )
    pins_ensure.add_argument("--media-url", default=None, help="Required when --media-source-type=image_url")
    pins_ensure.add_argument("--media-id", default=None, help="Required when --media-source-type=video_id")
    pins_ensure.add_argument(
        "--media-content-type",
        default=None,
        help="Required when --media-source-type=image_base64 (example: image/jpeg)",
    )
    pins_ensure.add_argument("--media-data", default=None, help="Required when --media-source-type=image_base64 (base64 payload)")
    pins_ensure.set_defaults(func=pins_cmd.cmd_pins_ensure)

    pin_links = pins_sub.add_parser("links", help="Pin link hygiene helpers (writes require --apply --yes)")
    pin_links_sub = pin_links.add_subparsers(dest="pin_links_cmd", required=True)
    pin_links_plan = pin_links_sub.add_parser("plan", help="Build a link update plan from an audit pins.json")
    pin_links_plan.add_argument("--pins-json", required=True, help="Path to an audit pins.json file")
    pin_links_plan.add_argument("--out", required=True, help="Output plan JSON file path")
    pin_links_plan.add_argument(
        "--canonical-host",
        default=None,
        help="Canonical site host to enforce (example: example.com). Can also be set in project config as `canonical_host`.",
    )
    pin_links_plan.add_argument(
        "--allowed-host",
        action="append",
        default=[],
        help="Additional allowed source host to canonicalize (repeatable). Default includes canonical host + www.<canonical>.",
    )
    pin_links_plan.add_argument(
        "--max-actions",
        type=int,
        default=None,
        help="Optional max number of planned updates (default: all matching pins)",
    )
    pin_links_plan.set_defaults(func=pin_links_cmd.cmd_pin_links_plan)

    pin_links_apply = pin_links_sub.add_parser(
        "apply",
        help="Apply a link update plan (dry-run by default; requires --apply --yes to write)",
    )
    pin_links_apply.add_argument("--plan", required=True, help="Plan JSON file path from `pins links plan`")
    pin_links_apply.add_argument("--limit", type=int, default=None, help="Optional limit (apply only first N items)")
    pin_links_apply.add_argument(
        "--allow-mismatch",
        action="store_true",
        help="Allow applying even if the current pin link does not match old_link in the plan (not recommended)",
    )
    pin_links_apply.set_defaults(func=pin_links_cmd.cmd_pin_links_apply)

    board_pins = sub.add_parser("board-pins", help="Pins on a board (and optional section)")
    board_pins_sub = board_pins.add_subparsers(dest="board_pins_cmd", required=True)
    board_pins_list = board_pins_sub.add_parser("list", help="List Pins on a board")
    board_pins_list.add_argument("--board-id", required=True, help="Board id")
    board_pins_list.add_argument("--section-id", default=None, help="Optional board section id")
    board_pins_list.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    board_pins_list.add_argument(
        "--creative-types",
        default=None,
        help="Optional comma-separated creative types filter (board-only endpoint)",
    )
    board_pins_list.add_argument(
        "--pin-metrics",
        action="store_true",
        help="Include metrics (board-only endpoint)",
    )
    board_pins_list.add_argument("--limit", type=int, default=100, help="Max items to return (default: 100)")
    board_pins_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    board_pins_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    board_pins_list.set_defaults(func=boards_cmd.cmd_board_pins_list)

    user_account = sub.add_parser("user-account", help="User account discovery (read-only)")
    user_account_sub = user_account.add_subparsers(dest="user_account_cmd", required=True)

    user_account_get = user_account_sub.add_parser("get", help="Get the current user account")
    user_account_get.set_defaults(func=user_account_cmd.cmd_user_account_get)

    user_account_businesses = user_account_sub.add_parser("businesses", help="List businesses the user has access to")
    user_account_businesses.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    user_account_businesses.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    user_account_businesses.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    user_account_businesses.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    user_account_businesses.set_defaults(func=user_account_cmd.cmd_user_account_businesses_list)

    user_account_followers = user_account_sub.add_parser("followers", help="List followers for the current user")
    user_account_followers.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    user_account_followers.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    user_account_followers.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    user_account_followers.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    user_account_followers.set_defaults(func=user_account_cmd.cmd_user_account_followers_list)

    user_account_following = user_account_sub.add_parser("following", help="List accounts the current user follows")
    user_account_following.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    user_account_following.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    user_account_following.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    user_account_following.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    user_account_following.set_defaults(func=user_account_cmd.cmd_user_account_following_list)

    user_account_following_boards = user_account_sub.add_parser(
        "following-boards",
        help="List boards the current user follows",
    )
    user_account_following_boards.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    user_account_following_boards.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    user_account_following_boards.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    user_account_following_boards.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    user_account_following_boards.set_defaults(func=user_account_cmd.cmd_user_account_following_boards_list)

    user_account_websites = user_account_sub.add_parser("websites", help="Websites for the current user account")
    user_account_websites_sub = user_account_websites.add_subparsers(dest="user_account_websites_cmd", required=True)
    user_account_websites_list = user_account_websites_sub.add_parser("list", help="List websites")
    user_account_websites_list.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    user_account_websites_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    user_account_websites_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    user_account_websites_list.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    user_account_websites_list.set_defaults(func=user_account_cmd.cmd_user_account_websites_list)
    user_account_websites_verification = user_account_websites_sub.add_parser(
        "verification",
        help="Get verification status for websites",
    )
    user_account_websites_verification.set_defaults(func=user_account_cmd.cmd_user_account_websites_verification)

    business_access = sub.add_parser("business-access", help="Business Access inventory (read-only)")
    business_access_sub = business_access.add_subparsers(dest="business_access_cmd", required=True)
    business_access.add_argument("--business-id", required=True, help="Business id")

    business_assets = business_access_sub.add_parser("assets", help="Business assets")
    business_assets_sub = business_assets.add_subparsers(dest="business_assets_cmd", required=True)
    business_assets_list = business_assets_sub.add_parser("list", help="List business assets")
    business_assets_list.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    business_assets_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    business_assets_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    business_assets_list.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    business_assets_list.set_defaults(func=business_access_cmd.cmd_business_assets_list)

    business_members = business_access_sub.add_parser("members", help="Business members")
    business_members_sub = business_members.add_subparsers(dest="business_members_cmd", required=True)
    business_members_list = business_members_sub.add_parser("list", help="List business members")
    business_members_list.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    business_members_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    business_members_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    business_members_list.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    business_members_list.set_defaults(func=business_access_cmd.cmd_business_members_list)

    business_partners = business_access_sub.add_parser("partners", help="Business partners")
    business_partners_sub = business_partners.add_subparsers(dest="business_partners_cmd", required=True)
    business_partners_list = business_partners_sub.add_parser("list", help="List business partners")
    business_partners_list.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    business_partners_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    business_partners_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    business_partners_list.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    business_partners_list.set_defaults(func=business_access_cmd.cmd_business_partners_list)

    business_asset_members = business_access_sub.add_parser("asset-members", help="Members for an asset")
    business_asset_members.add_argument("--asset-id", required=True, help="Asset id")
    business_asset_members.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    business_asset_members.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    business_asset_members.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    business_asset_members.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    business_asset_members.set_defaults(func=business_access_cmd.cmd_business_asset_members_list)

    business_asset_partners = business_access_sub.add_parser("asset-partners", help="Partners for an asset")
    business_asset_partners.add_argument("--asset-id", required=True, help="Asset id")
    business_asset_partners.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    business_asset_partners.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    business_asset_partners.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    business_asset_partners.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    business_asset_partners.set_defaults(func=business_access_cmd.cmd_business_asset_partners_list)

    business_member_assets = business_access_sub.add_parser("member-assets", help="Assets for a member")
    business_member_assets.add_argument("--member-id", required=True, help="Member id")
    business_member_assets.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    business_member_assets.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    business_member_assets.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    business_member_assets.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    business_member_assets.set_defaults(func=business_access_cmd.cmd_business_member_assets_list)

    business_partner_assets = business_access_sub.add_parser("partner-assets", help="Assets for a partner")
    business_partner_assets.add_argument("--partner-id", required=True, help="Partner id")
    business_partner_assets.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    business_partner_assets.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    business_partner_assets.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    business_partner_assets.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    business_partner_assets.set_defaults(func=business_access_cmd.cmd_business_partner_assets_list)

    resources = sub.add_parser("resources", help="Resources / lookup endpoints (read-only)")
    resources_sub = resources.add_subparsers(dest="resources_cmd", required=True)

    resources_ad_account_countries = resources_sub.add_parser(
        "ad-account-countries",
        help="Get supported ad account countries",
    )
    resources_ad_account_countries.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    resources_ad_account_countries.set_defaults(func=resources_cmd.cmd_resources_ad_account_countries)

    resources_delivery_metrics = resources_sub.add_parser("delivery-metrics", help="Get delivery metrics")
    resources_delivery_metrics.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    resources_delivery_metrics.set_defaults(func=resources_cmd.cmd_resources_delivery_metrics)

    resources_metrics_ready_state = resources_sub.add_parser("metrics-ready-state", help="Get metrics ready state")
    resources_metrics_ready_state.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    resources_metrics_ready_state.set_defaults(func=resources_cmd.cmd_resources_metrics_ready_state)

    resources_targeting = resources_sub.add_parser("targeting", help="Get targeting options by targeting type")
    resources_targeting.add_argument("--targeting-type", required=True, help="Targeting type")
    resources_targeting.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    resources_targeting.set_defaults(func=resources_cmd.cmd_resources_targeting)

    resources_interests = resources_sub.add_parser("interest", help="Get a targeting interest by id")
    resources_interests.add_argument("--interest-id", required=True, help="Interest id")
    resources_interests.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    resources_interests.set_defaults(func=resources_cmd.cmd_resources_targeting_interest)

    analytics = sub.add_parser("analytics", help="Read-only analytics (requires appropriate scopes)")
    analytics_sub = analytics.add_subparsers(dest="analytics_cmd", required=True)
    analytics_user = analytics_sub.add_parser("user", help="User account analytics (default: last 90 days)")
    analytics_user.add_argument("--start-date", default=None, help="YYYY-MM-DD (default: last 90 days)")
    analytics_user.add_argument("--end-date", default=None, help="YYYY-MM-DD (default: today)")
    analytics_user.add_argument("--metric", action="append", default=None, help="Metric type (repeatable)")
    analytics_user.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    analytics_user.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    analytics_user.set_defaults(func=analytics_cmd.cmd_analytics_user)

    analytics_top = analytics_sub.add_parser("top-pins", help="Top pins analytics (default: last 90 days)")
    analytics_top.add_argument("--start-date", default=None, help="YYYY-MM-DD (default: last 90 days)")
    analytics_top.add_argument("--end-date", default=None, help="YYYY-MM-DD (default: today)")
    analytics_top.add_argument("--sort-by", default="IMPRESSION", help="Sort metric (default: IMPRESSION)")
    analytics_top.add_argument("--metric", action="append", default=None, help="Metric type (repeatable)")
    analytics_top.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    analytics_top.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    analytics_top.set_defaults(func=analytics_cmd.cmd_analytics_top_pins)

    analytics_top_video = analytics_sub.add_parser(
        "top-video-pins", help="Top video pins analytics (default: last 90 days)"
    )
    analytics_top_video.add_argument("--start-date", default=None, help="YYYY-MM-DD (default: last 90 days)")
    analytics_top_video.add_argument("--end-date", default=None, help="YYYY-MM-DD (default: today)")
    analytics_top_video.add_argument("--sort-by", default="IMPRESSION", help="Sort metric (default: IMPRESSION)")
    analytics_top_video.add_argument("--metric", action="append", default=None, help="Metric type (repeatable)")
    analytics_top_video.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    analytics_top_video.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    analytics_top_video.set_defaults(func=analytics_cmd.cmd_analytics_top_video_pins)

    analytics_pin = analytics_sub.add_parser("pin", help="Pin analytics (default: last 90 days)")
    analytics_pin.add_argument("--id", required=True, help="Pin id")
    analytics_pin.add_argument("--start-date", default=None, help="YYYY-MM-DD (default: last 90 days)")
    analytics_pin.add_argument("--end-date", default=None, help="YYYY-MM-DD (default: today)")
    analytics_pin.add_argument("--metric", action="append", default=None, help="Metric type (repeatable)")
    analytics_pin.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    analytics_pin.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    analytics_pin.set_defaults(func=analytics_cmd.cmd_analytics_pin)

    analytics_pins = analytics_sub.add_parser("pins", help="Multiple Pin analytics (beta; max 100 ids)")
    analytics_pins.add_argument("--ids", required=True, help="Comma-separated Pin ids (max 100)")
    analytics_pins.add_argument("--start-date", default=None, help="YYYY-MM-DD (default: last 90 days)")
    analytics_pins.add_argument("--end-date", default=None, help="YYYY-MM-DD (default: today)")
    analytics_pins.add_argument("--metric", action="append", default=None, help="Metric type (repeatable)")
    analytics_pins.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    analytics_pins.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    analytics_pins.set_defaults(func=analytics_cmd.cmd_analytics_pins)

    ads = sub.add_parser(
        "ads",
        help=(
            "Ads API (writes are dry-run by default; requires --apply --yes; "
            "no-snapshot writes require --ack-no-snapshot; spend-affecting writes require --ack-spend; "
            "report jobs require --ack-volume)"
        ),
    )
    ads_sub = ads.add_subparsers(dest="ads_cmd", required=True)

    ads_accounts = ads_sub.add_parser("accounts", help="Ad accounts inventory")
    ads_accounts_sub = ads_accounts.add_subparsers(dest="ads_accounts_cmd", required=True)
    ads_accounts_list = ads_accounts_sub.add_parser("list", help="List ad accounts")
    ads_accounts_list.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    ads_accounts_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    ads_accounts_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    ads_accounts_list.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_accounts_list.set_defaults(func=ads_cmd.cmd_ads_accounts_list)
    ads_accounts_get = ads_accounts_sub.add_parser("get", help="Get an ad account")
    ads_accounts_get.add_argument("--id", required=True, help="Ad account id")
    ads_accounts_get.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_accounts_get.set_defaults(func=ads_cmd.cmd_ads_accounts_get)

    ads_reports = ads_sub.add_parser(
        "reports",
        help="Async report jobs (create/poll/download; creation requires --apply --yes --ack-volume --ack-no-snapshot)",
    )
    ads_reports_sub = ads_reports.add_subparsers(dest="ads_reports_cmd", required=True)

    ads_reports_create = ads_reports_sub.add_parser(
        "create",
        help="Create an async report job (requires --apply --yes --ack-volume --ack-no-snapshot)",
    )
    ads_reports_create.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_reports_create.add_argument("--body-file", required=True, help="JSON request body file path")
    ads_reports_create.set_defaults(func=report_jobs_cmd.cmd_ads_reports_create)

    ads_reports_get = ads_reports_sub.add_parser("get", help="Get report job status by token")
    ads_reports_get.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_reports_get.add_argument("--token", required=True, help="Report job token")
    ads_reports_get.set_defaults(func=report_jobs_cmd.cmd_ads_reports_get)

    ads_reports_run = ads_reports_sub.add_parser(
        "run",
        help="Create a report job, poll, and download results (requires --apply --yes --ack-volume --ack-no-snapshot)",
    )
    ads_reports_run.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_reports_run.add_argument("--body-file", required=True, help="JSON request body file path")
    ads_reports_run.add_argument("--out-dir", required=True, help="Output directory for downloads and receipts")
    ads_reports_run.add_argument(
        "--max-poll-attempts",
        type=int,
        default=60,
        help="Max polling attempts (default: 60)",
    )
    ads_reports_run.add_argument(
        "--max-poll-seconds",
        type=float,
        default=600.0,
        help="Max polling time in seconds (default: 600)",
    )
    ads_reports_run.add_argument(
        "--poll-interval-s",
        type=float,
        default=10.0,
        help="Seconds between polling attempts (default: 10)",
    )
    ads_reports_run.add_argument(
        "--max-download-bytes",
        type=int,
        default=100 * 1024 * 1024,
        help="Max bytes to download (default: 104857600)",
    )
    ads_reports_run.set_defaults(func=report_jobs_cmd.cmd_ads_reports_run)

    ads_campaigns = ads_sub.add_parser("campaigns", help="Campaigns inventory")
    ads_campaigns_sub = ads_campaigns.add_subparsers(dest="ads_campaigns_cmd", required=True)
    ads_campaigns_list = ads_campaigns_sub.add_parser("list", help="List campaigns for an ad account")
    ads_campaigns_list.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_campaigns_list.add_argument("--limit", type=int, default=10000, help="Max items to return (default: 10000)")
    ads_campaigns_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    ads_campaigns_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    ads_campaigns_list.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_campaigns_list.set_defaults(func=ads_cmd.cmd_ads_campaigns_list)
    ads_campaigns_get = ads_campaigns_sub.add_parser("get", help="Get a campaign")
    ads_campaigns_get.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_campaigns_get.add_argument("--id", required=True, help="Campaign id")
    ads_campaigns_get.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_campaigns_get.set_defaults(func=ads_cmd.cmd_ads_campaigns_get)
    ads_campaigns_create = ads_campaigns_sub.add_parser(
        "create",
        help="Create campaigns (dry-run by default; requires --apply --yes --ack-spend)",
    )
    ads_campaigns_create.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_campaigns_create.add_argument(
        "--body-file",
        "--json",
        dest="body_file",
        required=True,
        help="Path to JSON body file (object)",
    )
    ads_campaigns_create.set_defaults(func=ads_cmd.cmd_ads_campaigns_create)
    ads_campaigns_update = ads_campaigns_sub.add_parser(
        "update",
        help="Update a campaign (dry-run by default; requires --apply --yes --ack-spend)",
    )
    ads_campaigns_update.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_campaigns_update.add_argument("--id", required=True, help="Campaign id")
    ads_campaigns_update.add_argument(
        "--body-file",
        "--json",
        dest="body_file",
        required=True,
        help="Path to JSON body file (object)",
    )
    ads_campaigns_update.set_defaults(func=ads_cmd.cmd_ads_campaigns_update)
    ads_campaigns_pause = ads_campaigns_sub.add_parser(
        "pause",
        help="Pause a campaign (dry-run by default; requires --apply --yes; does not require --ack-spend)",
    )
    ads_campaigns_pause.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_campaigns_pause.add_argument("--id", required=True, help="Campaign id")
    ads_campaigns_pause.set_defaults(func=ads_cmd.cmd_ads_campaigns_pause)
    ads_campaigns_resume = ads_campaigns_sub.add_parser(
        "resume",
        help="Resume a campaign (dry-run by default; requires --apply --yes --ack-spend)",
    )
    ads_campaigns_resume.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_campaigns_resume.add_argument("--id", required=True, help="Campaign id")
    ads_campaigns_resume.set_defaults(func=ads_cmd.cmd_ads_campaigns_resume)

    ads_ad_groups = ads_sub.add_parser("ad-groups", help="Ad groups inventory")
    ads_ad_groups_sub = ads_ad_groups.add_subparsers(dest="ads_ad_groups_cmd", required=True)
    ads_ad_groups_list = ads_ad_groups_sub.add_parser("list", help="List ad groups for an ad account")
    ads_ad_groups_list.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_ad_groups_list.add_argument("--limit", type=int, default=20000, help="Max items to return (default: 20000)")
    ads_ad_groups_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    ads_ad_groups_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    ads_ad_groups_list.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_ad_groups_list.set_defaults(func=ads_cmd.cmd_ads_ad_groups_list)
    ads_ad_groups_get = ads_ad_groups_sub.add_parser("get", help="Get an ad group")
    ads_ad_groups_get.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_ad_groups_get.add_argument("--id", required=True, help="Ad group id")
    ads_ad_groups_get.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_ad_groups_get.set_defaults(func=ads_cmd.cmd_ads_ad_groups_get)
    ads_ad_groups_create = ads_ad_groups_sub.add_parser(
        "create",
        help="Create ad groups (dry-run by default; requires --apply --yes --ack-spend)",
    )
    ads_ad_groups_create.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_ad_groups_create.add_argument(
        "--body-file",
        "--json",
        dest="body_file",
        required=True,
        help="Path to JSON body file (object)",
    )
    ads_ad_groups_create.set_defaults(func=ads_cmd.cmd_ads_ad_groups_create)
    ads_ad_groups_update = ads_ad_groups_sub.add_parser(
        "update",
        help="Update an ad group (dry-run by default; requires --apply --yes --ack-spend)",
    )
    ads_ad_groups_update.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_ad_groups_update.add_argument("--id", required=True, help="Ad group id")
    ads_ad_groups_update.add_argument(
        "--body-file",
        "--json",
        dest="body_file",
        required=True,
        help="Path to JSON body file (object)",
    )
    ads_ad_groups_update.set_defaults(func=ads_cmd.cmd_ads_ad_groups_update)
    ads_ad_groups_pause = ads_ad_groups_sub.add_parser(
        "pause",
        help="Pause an ad group (dry-run by default; requires --apply --yes; does not require --ack-spend)",
    )
    ads_ad_groups_pause.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_ad_groups_pause.add_argument("--id", required=True, help="Ad group id")
    ads_ad_groups_pause.set_defaults(func=ads_cmd.cmd_ads_ad_groups_pause)
    ads_ad_groups_resume = ads_ad_groups_sub.add_parser(
        "resume",
        help="Resume an ad group (dry-run by default; requires --apply --yes --ack-spend)",
    )
    ads_ad_groups_resume.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_ad_groups_resume.add_argument("--id", required=True, help="Ad group id")
    ads_ad_groups_resume.set_defaults(func=ads_cmd.cmd_ads_ad_groups_resume)

    ads_ads = ads_sub.add_parser("ads", help="Ads (creatives) inventory")
    ads_ads_sub = ads_ads.add_subparsers(dest="ads_ads_cmd", required=True)
    ads_ads_list = ads_ads_sub.add_parser("list", help="List ads for an ad account")
    ads_ads_list.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_ads_list.add_argument("--limit", type=int, default=20000, help="Max items to return (default: 20000)")
    ads_ads_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    ads_ads_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    ads_ads_list.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_ads_list.set_defaults(func=ads_cmd.cmd_ads_ads_list)
    ads_ads_get = ads_ads_sub.add_parser("get", help="Get an ad")
    ads_ads_get.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_ads_get.add_argument("--id", required=True, help="Ad id")
    ads_ads_get.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_ads_get.set_defaults(func=ads_cmd.cmd_ads_ads_get)
    ads_ads_create = ads_ads_sub.add_parser(
        "create",
        help="Create ads (dry-run by default; requires --apply --yes --ack-spend)",
    )
    ads_ads_create.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_ads_create.add_argument(
        "--body-file",
        "--json",
        dest="body_file",
        required=True,
        help="Path to JSON body file (object)",
    )
    ads_ads_create.set_defaults(func=ads_cmd.cmd_ads_ads_create)
    ads_ads_update = ads_ads_sub.add_parser(
        "update",
        help="Update an ad (dry-run by default; requires --apply --yes --ack-spend)",
    )
    ads_ads_update.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_ads_update.add_argument("--id", required=True, help="Ad id")
    ads_ads_update.add_argument(
        "--body-file",
        "--json",
        dest="body_file",
        required=True,
        help="Path to JSON body file (object)",
    )
    ads_ads_update.set_defaults(func=ads_cmd.cmd_ads_ads_update)
    ads_ads_pause = ads_ads_sub.add_parser(
        "pause",
        help="Pause an ad (dry-run by default; requires --apply --yes; does not require --ack-spend)",
    )
    ads_ads_pause.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_ads_pause.add_argument("--id", required=True, help="Ad id")
    ads_ads_pause.set_defaults(func=ads_cmd.cmd_ads_ads_pause)
    ads_ads_resume = ads_ads_sub.add_parser(
        "resume",
        help="Resume an ad (dry-run by default; requires --apply --yes --ack-spend)",
    )
    ads_ads_resume.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_ads_resume.add_argument("--id", required=True, help="Ad id")
    ads_ads_resume.set_defaults(func=ads_cmd.cmd_ads_ads_resume)

    ads_analytics = ads_sub.add_parser("analytics", help="Ads analytics/reporting (aggregated; read-only)")
    ads_analytics_sub = ads_analytics.add_subparsers(dest="ads_analytics_cmd", required=True)

    ads_analytics_ad_account = ads_analytics_sub.add_parser("ad-account", help="Ad account analytics")
    ads_analytics_ad_account.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_analytics_ad_account.add_argument("--start-date", default=None, help="YYYY-MM-DD (default: last 30 days)")
    ads_analytics_ad_account.add_argument("--end-date", default=None, help="YYYY-MM-DD (default: today)")
    ads_analytics_ad_account.add_argument("--granularity", default=None, help="Granularity (passed through, if supported)")
    ads_analytics_ad_account.add_argument("--metric", action="append", default=None, help="Metric/column name (repeatable)")
    ads_analytics_ad_account.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_analytics_ad_account.set_defaults(func=ads_cmd.cmd_ads_ad_account_analytics)

    ads_analytics_campaigns = ads_analytics_sub.add_parser("campaigns", help="Campaigns analytics")
    ads_analytics_campaigns.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_analytics_campaigns.add_argument("--start-date", default=None, help="YYYY-MM-DD (default: last 30 days)")
    ads_analytics_campaigns.add_argument("--end-date", default=None, help="YYYY-MM-DD (default: today)")
    ads_analytics_campaigns.add_argument("--granularity", default=None, help="Granularity (passed through, if supported)")
    ads_analytics_campaigns.add_argument("--metric", action="append", default=None, help="Metric/column name (repeatable)")
    ads_analytics_campaigns.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_analytics_campaigns.set_defaults(func=ads_cmd.cmd_ads_campaigns_analytics)

    ads_analytics_ad_groups = ads_analytics_sub.add_parser("ad-groups", help="Ad groups analytics")
    ads_analytics_ad_groups.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_analytics_ad_groups.add_argument("--start-date", default=None, help="YYYY-MM-DD (default: last 30 days)")
    ads_analytics_ad_groups.add_argument("--end-date", default=None, help="YYYY-MM-DD (default: today)")
    ads_analytics_ad_groups.add_argument("--granularity", default=None, help="Granularity (passed through, if supported)")
    ads_analytics_ad_groups.add_argument("--metric", action="append", default=None, help="Metric/column name (repeatable)")
    ads_analytics_ad_groups.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_analytics_ad_groups.set_defaults(func=ads_cmd.cmd_ads_ad_groups_analytics)

    ads_analytics_ads = ads_analytics_sub.add_parser("ads", help="Ads analytics")
    ads_analytics_ads.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_analytics_ads.add_argument("--start-date", default=None, help="YYYY-MM-DD (default: last 30 days)")
    ads_analytics_ads.add_argument("--end-date", default=None, help="YYYY-MM-DD (default: today)")
    ads_analytics_ads.add_argument("--granularity", default=None, help="Granularity (passed through, if supported)")
    ads_analytics_ads.add_argument("--metric", action="append", default=None, help="Metric/column name (repeatable)")
    ads_analytics_ads.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_analytics_ads.set_defaults(func=ads_cmd.cmd_ads_ads_analytics)

    ads_analytics_pins = ads_analytics_sub.add_parser("pins", help="Ad pins analytics")
    ads_analytics_pins.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_analytics_pins.add_argument("--start-date", default=None, help="YYYY-MM-DD (default: last 30 days)")
    ads_analytics_pins.add_argument("--end-date", default=None, help="YYYY-MM-DD (default: today)")
    ads_analytics_pins.add_argument("--granularity", default=None, help="Granularity (passed through, if supported)")
    ads_analytics_pins.add_argument("--metric", action="append", default=None, help="Metric/column name (repeatable)")
    ads_analytics_pins.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_analytics_pins.set_defaults(func=ads_cmd.cmd_ads_pins_analytics)

    ads_targeting_analytics = ads_sub.add_parser("targeting-analytics", help="Targeting analytics (aggregated; read-only)")
    ads_targeting_analytics_sub = ads_targeting_analytics.add_subparsers(dest="ads_targeting_analytics_cmd", required=True)

    ads_targeting_analytics_ad_account = ads_targeting_analytics_sub.add_parser(
        "ad-account",
        help="Targeting analytics for an ad account",
    )
    ads_targeting_analytics_ad_account.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_targeting_analytics_ad_account.add_argument("--start-date", default=None, help="YYYY-MM-DD (default: last 30 days)")
    ads_targeting_analytics_ad_account.add_argument("--end-date", default=None, help="YYYY-MM-DD (default: today)")
    ads_targeting_analytics_ad_account.add_argument("--granularity", default=None, help="Granularity (passed through, if supported)")
    ads_targeting_analytics_ad_account.add_argument("--metric-type", action="append", default=None, help="Metric type (repeatable)")
    ads_targeting_analytics_ad_account.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_targeting_analytics_ad_account.set_defaults(func=ads_cmd.cmd_ads_targeting_analytics_ad_account)

    ads_targeting_analytics_campaigns = ads_targeting_analytics_sub.add_parser(
        "campaigns",
        help="Targeting analytics for campaigns in an ad account",
    )
    ads_targeting_analytics_campaigns.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_targeting_analytics_campaigns.add_argument("--start-date", default=None, help="YYYY-MM-DD (default: last 30 days)")
    ads_targeting_analytics_campaigns.add_argument("--end-date", default=None, help="YYYY-MM-DD (default: today)")
    ads_targeting_analytics_campaigns.add_argument("--granularity", default=None, help="Granularity (passed through, if supported)")
    ads_targeting_analytics_campaigns.add_argument("--metric-type", action="append", default=None, help="Metric type (repeatable)")
    ads_targeting_analytics_campaigns.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_targeting_analytics_campaigns.set_defaults(func=ads_cmd.cmd_ads_targeting_analytics_campaigns)

    ads_targeting_analytics_ad_groups = ads_targeting_analytics_sub.add_parser(
        "ad-groups",
        help="Targeting analytics for ad groups in an ad account",
    )
    ads_targeting_analytics_ad_groups.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_targeting_analytics_ad_groups.add_argument("--start-date", default=None, help="YYYY-MM-DD (default: last 30 days)")
    ads_targeting_analytics_ad_groups.add_argument("--end-date", default=None, help="YYYY-MM-DD (default: today)")
    ads_targeting_analytics_ad_groups.add_argument("--granularity", default=None, help="Granularity (passed through, if supported)")
    ads_targeting_analytics_ad_groups.add_argument("--metric-type", action="append", default=None, help="Metric type (repeatable)")
    ads_targeting_analytics_ad_groups.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_targeting_analytics_ad_groups.set_defaults(func=ads_cmd.cmd_ads_targeting_analytics_ad_groups)

    ads_targeting_analytics_ads = ads_targeting_analytics_sub.add_parser(
        "ads",
        help="Targeting analytics for ads in an ad account",
    )
    ads_targeting_analytics_ads.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_targeting_analytics_ads.add_argument("--start-date", default=None, help="YYYY-MM-DD (default: last 30 days)")
    ads_targeting_analytics_ads.add_argument("--end-date", default=None, help="YYYY-MM-DD (default: today)")
    ads_targeting_analytics_ads.add_argument("--granularity", default=None, help="Granularity (passed through, if supported)")
    ads_targeting_analytics_ads.add_argument("--metric-type", action="append", default=None, help="Metric type (repeatable)")
    ads_targeting_analytics_ads.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_targeting_analytics_ads.set_defaults(func=ads_cmd.cmd_ads_targeting_analytics_ads)

    ads_audience_insights = ads_sub.add_parser("audience-insights", help="Audience insights (read-only)")
    ads_audience_insights.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_audience_insights.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_audience_insights.set_defaults(func=ads_cmd.cmd_ads_audience_insights)

    ads_audiences = ads_sub.add_parser("audiences", help="Audience insights audiences (read-only)")
    ads_audiences.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_audiences.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_audiences.set_defaults(func=ads_cmd.cmd_ads_audiences)

    ads_conversions = ads_sub.add_parser("conversions", help="Conversions status (read-only)")
    ads_conversions_sub = ads_conversions.add_subparsers(dest="ads_conversions_cmd", required=True)

    ads_conversions_tags = ads_conversions_sub.add_parser("tags", help="Conversion tags")
    ads_conversions_tags_sub = ads_conversions_tags.add_subparsers(dest="ads_conversions_tags_cmd", required=True)
    ads_conversions_tags_list = ads_conversions_tags_sub.add_parser("list", help="List conversion tags")
    ads_conversions_tags_list.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_conversions_tags_list.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    ads_conversions_tags_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    ads_conversions_tags_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    ads_conversions_tags_list.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_conversions_tags_list.set_defaults(func=conversions_cmd.cmd_conversions_tags_list)

    ads_conversions_tags_get = ads_conversions_tags_sub.add_parser("get", help="Get a conversion tag")
    ads_conversions_tags_get.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_conversions_tags_get.add_argument("--id", required=True, help="Conversion tag id")
    ads_conversions_tags_get.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_conversions_tags_get.set_defaults(func=conversions_cmd.cmd_conversions_tags_get)

    ads_conversions_page_visit = ads_conversions_sub.add_parser("page-visit", help="Get page visit conversion tag info")
    ads_conversions_page_visit.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_conversions_page_visit.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_conversions_page_visit.set_defaults(func=conversions_cmd.cmd_conversions_page_visit)

    ads_conversions_ocpm_eligible = ads_conversions_sub.add_parser(
        "ocpm-eligible",
        help="Get oCPM eligibility for conversion tags",
    )
    ads_conversions_ocpm_eligible.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_conversions_ocpm_eligible.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_conversions_ocpm_eligible.set_defaults(func=conversions_cmd.cmd_conversions_ocpm_eligible)

    ads_conversions_eqs = ads_conversions_sub.add_parser("eqs", help="Get conversion EQS status")
    ads_conversions_eqs.add_argument("--ad-account-id", required=True, help="Ad account id")
    ads_conversions_eqs.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    ads_conversions_eqs.set_defaults(func=conversions_cmd.cmd_conversions_eqs)

    catalogs = sub.add_parser(
        "catalogs",
        help="Catalogs API (writes are dry-run by default; requires --apply --yes; ingest requires --ack-volume)",
    )
    catalogs_sub = catalogs.add_subparsers(dest="catalogs_cmd", required=True)
    catalogs_create = catalogs_sub.add_parser(
        "create",
        help="Create a catalog (dry-run by default; requires --apply --yes)",
    )
    catalogs_create.add_argument("--ad-account-id", default=None, help="Optional ad account id (Business Access context)")
    catalogs_create.add_argument(
        "--body-file",
        "--json",
        dest="body_file",
        required=True,
        help="Path to JSON body file (object)",
    )
    catalogs_create.set_defaults(func=catalogs_cmd.cmd_catalogs_create)
    catalogs_list = catalogs_sub.add_parser("list", help="List catalogs for an ad account")
    catalogs_list.add_argument("--ad-account-id", required=True, help="Ad account id")
    catalogs_list.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    catalogs_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    catalogs_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    catalogs_list.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    catalogs_list.set_defaults(func=catalogs_cmd.cmd_catalogs_list)

    catalogs_available_filter_values = catalogs_sub.add_parser(
        "available-filter-values",
        help="Catalog diagnostics: available filter values",
    )
    catalogs_available_filter_values.add_argument("--ad-account-id", default=None, help="Optional ad account id (passed through)")
    catalogs_available_filter_values.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    catalogs_available_filter_values.set_defaults(func=catalogs_cmd.cmd_catalogs_available_filter_values)

    catalogs_product_group_counts = catalogs_sub.add_parser(
        "product-group-product-counts",
        help="Catalog diagnostics: product counts for a product group",
    )
    catalogs_product_group_counts.add_argument("--product-group-id", required=True, help="Product group id")
    catalogs_product_group_counts.add_argument("--ad-account-id", default=None, help="Optional ad account id (passed through)")
    catalogs_product_group_counts.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    catalogs_product_group_counts.set_defaults(func=catalogs_cmd.cmd_catalogs_product_group_product_counts)

    catalogs_items_batch = catalogs_sub.add_parser("items-batch", help="Catalog diagnostics: get batch status")
    catalogs_items_batch_sub = catalogs_items_batch.add_subparsers(dest="catalogs_items_batch_cmd", required=True)
    catalogs_items_batch_get = catalogs_items_batch_sub.add_parser("get", help="Get a catalog items batch by id")
    catalogs_items_batch_get.add_argument("--batch-id", required=True, help="Batch id")
    catalogs_items_batch_get.add_argument("--ad-account-id", default=None, help="Optional ad account id (passed through)")
    catalogs_items_batch_get.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    catalogs_items_batch_get.set_defaults(func=catalogs_cmd.cmd_catalogs_items_batch_get)

    catalogs_feeds = catalogs_sub.add_parser("feeds", help="Catalog feeds inventory")
    catalogs_feeds_sub = catalogs_feeds.add_subparsers(dest="catalogs_feeds_cmd", required=True)
    catalogs_feeds_list = catalogs_feeds_sub.add_parser("list", help="List catalog feeds")
    catalogs_feeds_list.add_argument("--ad-account-id", required=True, help="Ad account id")
    catalogs_feeds_list.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    catalogs_feeds_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    catalogs_feeds_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    catalogs_feeds_list.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    catalogs_feeds_list.set_defaults(func=catalogs_cmd.cmd_catalogs_feeds_list)
    catalogs_feeds_get = catalogs_feeds_sub.add_parser("get", help="Get a catalog feed")
    catalogs_feeds_get.add_argument("--ad-account-id", required=True, help="Ad account id")
    catalogs_feeds_get.add_argument("--id", required=True, help="Feed id")
    catalogs_feeds_get.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    catalogs_feeds_get.set_defaults(func=catalogs_cmd.cmd_catalogs_feeds_get)
    catalogs_feeds_create = catalogs_feeds_sub.add_parser(
        "create",
        help="Create a catalog feed (dry-run by default; requires --apply --yes)",
    )
    catalogs_feeds_create.add_argument("--ad-account-id", required=True, help="Ad account id")
    catalogs_feeds_create.add_argument(
        "--body-file",
        "--json",
        dest="body_file",
        required=True,
        help="Path to JSON body file (object)",
    )
    catalogs_feeds_create.set_defaults(func=catalogs_cmd.cmd_catalogs_feeds_create)
    catalogs_feeds_update = catalogs_feeds_sub.add_parser(
        "update",
        help="Update a catalog feed (dry-run by default; requires --apply --yes)",
    )
    catalogs_feeds_update.add_argument("--ad-account-id", required=True, help="Ad account id")
    catalogs_feeds_update.add_argument("--id", required=True, help="Feed id")
    catalogs_feeds_update.add_argument(
        "--body-file",
        "--json",
        dest="body_file",
        required=True,
        help="Path to JSON body file (object)",
    )
    catalogs_feeds_update.set_defaults(func=catalogs_cmd.cmd_catalogs_feeds_update)
    catalogs_feeds_ingest = catalogs_feeds_sub.add_parser(
        "ingest",
        help="Trigger feed ingestion (dry-run by default; requires --apply --yes --ack-volume --ack-no-snapshot)",
    )
    catalogs_feeds_ingest.add_argument("--ad-account-id", required=True, help="Ad account id")
    catalogs_feeds_ingest.add_argument("--id", required=True, help="Feed id")
    catalogs_feeds_ingest.set_defaults(func=catalogs_cmd.cmd_catalogs_feeds_ingest)

    catalogs_feed_processing = catalogs_sub.add_parser("feed-processing-results", help="Feed processing results")
    catalogs_feed_processing_sub = catalogs_feed_processing.add_subparsers(
        dest="catalogs_feed_processing_cmd", required=True
    )
    catalogs_feed_processing_list = catalogs_feed_processing_sub.add_parser(
        "list", help="List processing results for a feed"
    )
    catalogs_feed_processing_list.add_argument("--ad-account-id", required=True, help="Ad account id")
    catalogs_feed_processing_list.add_argument("--feed-id", required=True, help="Feed id")
    catalogs_feed_processing_list.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    catalogs_feed_processing_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    catalogs_feed_processing_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    catalogs_feed_processing_list.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    catalogs_feed_processing_list.set_defaults(func=catalogs_cmd.cmd_catalogs_feed_processing_results_list)

    catalogs_product_groups = catalogs_sub.add_parser("product-groups", help="Catalog product groups inventory")
    catalogs_product_groups_sub = catalogs_product_groups.add_subparsers(dest="catalogs_product_groups_cmd", required=True)
    catalogs_product_groups_list = catalogs_product_groups_sub.add_parser("list", help="List product groups")
    catalogs_product_groups_list.add_argument("--ad-account-id", required=True, help="Ad account id")
    catalogs_product_groups_list.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    catalogs_product_groups_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    catalogs_product_groups_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    catalogs_product_groups_list.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    catalogs_product_groups_list.set_defaults(func=catalogs_cmd.cmd_catalogs_product_groups_list)
    catalogs_product_groups_get = catalogs_product_groups_sub.add_parser("get", help="Get a product group")
    catalogs_product_groups_get.add_argument("--ad-account-id", required=True, help="Ad account id")
    catalogs_product_groups_get.add_argument("--id", required=True, help="Product group id")
    catalogs_product_groups_get.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    catalogs_product_groups_get.set_defaults(func=catalogs_cmd.cmd_catalogs_product_groups_get)

    catalogs_product_group_products = catalogs_sub.add_parser("product-group-products", help="Products in a product group")
    catalogs_product_group_products_sub = catalogs_product_group_products.add_subparsers(
        dest="catalogs_product_group_products_cmd", required=True
    )
    catalogs_product_group_products_list = catalogs_product_group_products_sub.add_parser(
        "list", help="List products for a product group"
    )
    catalogs_product_group_products_list.add_argument("--ad-account-id", required=True, help="Ad account id")
    catalogs_product_group_products_list.add_argument("--product-group-id", required=True, help="Product group id")
    catalogs_product_group_products_list.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    catalogs_product_group_products_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    catalogs_product_group_products_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    catalogs_product_group_products_list.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    catalogs_product_group_products_list.set_defaults(func=catalogs_cmd.cmd_catalogs_product_group_products_list)

    catalogs_item_issues = catalogs_sub.add_parser("item-issues", help="Catalog item issues for a processing result")
    catalogs_item_issues_sub = catalogs_item_issues.add_subparsers(dest="catalogs_item_issues_cmd", required=True)
    catalogs_item_issues_list = catalogs_item_issues_sub.add_parser(
        "list", help="List item issues for a processing result"
    )
    catalogs_item_issues_list.add_argument("--processing-result-id", required=True, help="Processing result id")
    catalogs_item_issues_list.add_argument("--ad-account-id", default=None, help="Optional ad account id (passed through)")
    catalogs_item_issues_list.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    catalogs_item_issues_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    catalogs_item_issues_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    catalogs_item_issues_list.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    catalogs_item_issues_list.set_defaults(func=catalogs_cmd.cmd_catalogs_processing_result_item_issues_list)

    catalogs_reports = catalogs_sub.add_parser("reports", help="Catalog reporting endpoints (aggregated; read-only)")
    catalogs_reports_sub = catalogs_reports.add_subparsers(dest="catalogs_reports_cmd", required=True)
    catalogs_reports_list = catalogs_reports_sub.add_parser("list", help="List catalog reports")
    catalogs_reports_list.add_argument("--ad-account-id", required=True, help="Ad account id")
    catalogs_reports_list.add_argument("--limit", type=int, default=1000, help="Max items to return (default: 1000)")
    catalogs_reports_list.add_argument("--page-size", type=int, default=100, help="Page size (1..100, default: 100)")
    catalogs_reports_list.add_argument("--bookmark", default=None, help="Start pagination from this bookmark")
    catalogs_reports_list.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    catalogs_reports_list.set_defaults(func=catalogs_cmd.cmd_catalogs_reports_list)

    catalogs_reports_stats = catalogs_reports_sub.add_parser("stats", help="Catalog reports aggregated stats")
    catalogs_reports_stats.add_argument("--ad-account-id", required=True, help="Ad account id")
    catalogs_reports_stats.add_argument("--param", action="append", default=None, help="Extra query param key=value")
    catalogs_reports_stats.set_defaults(func=catalogs_cmd.cmd_catalogs_reports_stats)

    jobs = sub.add_parser("jobs", help="Batch runner for write workflows (safe-by-default)")
    jobs_sub = jobs.add_subparsers(dest="jobs_cmd", required=True)

    jobs_run = jobs_sub.add_parser(
        "run",
        help="Run jobs from a .json or .csv file (remote writes require --apply --yes --ack-no-snapshot)",
    )
    jobs_run.add_argument("--file", required=True, help="Job file path (.json or .csv)")
    jobs_run.add_argument("--out-dir", required=True, help="Output directory for receipts and downloaded artifacts")
    jobs_run.add_argument("--limit", type=int, default=None, help="Optional max number of jobs to run")
    jobs_run.set_defaults(func=jobs_cmd.cmd_jobs_run)

    audit = sub.add_parser("audit", help="Read-only audit helpers (write JSON snapshots)")
    audit_sub = audit.add_subparsers(dest="audit_cmd", required=True)
    snapshot = audit_sub.add_parser("snapshot", help="Write a JSON snapshot of your account state")
    snapshot.add_argument("--out-dir", required=True, help="Output directory to write JSON files")
    snapshot.add_argument("--ad-account-id", default=None, help="Optional Business Access ad account id")
    snapshot.add_argument(
        "--include-ads",
        action="store_true",
        help="Include best-effort Ads exports (requires --ad-account-id; failures become warnings)",
    )
    snapshot.add_argument(
        "--include-catalogs",
        action="store_true",
        help="Include best-effort Catalogs exports (requires --ad-account-id; failures become warnings)",
    )
    snapshot.add_argument(
        "--include-user-account",
        action="store_true",
        help="Include best-effort user account discovery exports (failures become warnings)",
    )
    snapshot.add_argument(
        "--include-business-access",
        action="store_true",
        help="Include best-effort Business Access exports (requires --business-id; failures become warnings)",
    )
    snapshot.add_argument("--business-id", default=None, help="Business id for --include-business-access")
    snapshot.add_argument(
        "--include-resources",
        action="store_true",
        help="Include best-effort resources/lookup exports (failures become warnings)",
    )
    snapshot.add_argument(
        "--include-conversions",
        action="store_true",
        help="Include best-effort conversions exports (requires --ad-account-id; failures become warnings)",
    )
    snapshot.add_argument(
        "--export-limit",
        type=int,
        default=50000,
        help="Max items to export for optional ads/catalogs lists (default: 50000)",
    )
    snapshot.add_argument(
        "--export-page-size",
        type=int,
        default=100,
        help="Page size for optional ads/catalogs exports (1..100, default: 100)",
    )
    snapshot.add_argument("--boards-limit", type=int, default=100000, help="Max boards to fetch (default: 100000)")
    snapshot.add_argument("--pins-limit", type=int, default=200000, help="Max pins to fetch (default: 200000)")
    snapshot.add_argument("--page-size", type=int, default=100, help="Page size for list endpoints (default: 100)")
    snapshot.add_argument(
        "--skip-analytics",
        action="store_true",
        help="Skip analytics calls (useful if scopes are missing)",
    )
    snapshot.set_defaults(func=audit_cmd.cmd_audit_snapshot)

    return p


def _is_write_plan_or_refusal_command(args: argparse.Namespace) -> bool:
    cmd = str(getattr(args, "cmd", "") or "")
    if cmd == "boards":
        return str(getattr(args, "boards_cmd", "") or "") in {"create", "update", "delete", "ensure"}
    if cmd == "board-sections":
        return str(getattr(args, "sections_cmd", "") or "") in {"create", "update", "delete", "ensure"}
    if cmd == "pins":
        if str(getattr(args, "pins_cmd", "") or "") in {"create", "update", "delete", "save", "ensure"}:
            return True
        return False
    if cmd == "ads":
        ads_cmd = str(getattr(args, "ads_cmd", "") or "")
        if ads_cmd == "campaigns":
            return str(getattr(args, "ads_campaigns_cmd", "") or "") in {"create", "update", "pause", "resume"}
        if ads_cmd == "ad-groups":
            return str(getattr(args, "ads_ad_groups_cmd", "") or "") in {"create", "update", "pause", "resume"}
        if ads_cmd == "ads":
            return str(getattr(args, "ads_ads_cmd", "") or "") in {"create", "update", "pause", "resume"}
        return False
    if cmd == "catalogs":
        if str(getattr(args, "catalogs_cmd", "") or "") == "create":
            return True
        if str(getattr(args, "catalogs_cmd", "") or "") == "feeds":
            return str(getattr(args, "catalogs_feeds_cmd", "") or "") in {"create", "update", "ingest"}
    return False


def main(argv: list[str]) -> int:
    pre_out = Output(mode=_argv_output_mode(argv))

    if "--version" in argv or any(a.startswith("--version=") for a in argv):
        if _argv_wants_json(argv):
            pre_out.emit({"ok": True, "tool": "pinterest-api-tool", "version": __version__})
        else:
            pre_out.emit(f"pinterest-api-tool {__version__}")
        return 0

    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except ValidationError as e:
        pre_out.emit({"ok": False, "error": str(e), "error_type": "ValidationError"})
        return 2

    out = Output(mode=args.output)
    audit = AuditLogger(path=args.log_file, enabled=bool(args.log_file))

    try:
        if bool(getattr(args, "version", False)):
            if _argv_wants_json(argv):
                out.emit({"ok": True, "tool": "pinterest-api-tool", "version": __version__})
            else:
                out.emit(f"pinterest-api-tool {__version__}")
            return 0

        cfg = load_config(args.env_file)
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        http = HttpClient(
            timeout_s=timeout_s,
            verbose=bool(args.verbose),
            user_agent=f"pinterest-api-tool/{__version__}",
        )
        project_cfg, cfg_base_dir = load_project_config(getattr(args, "config", None))
        project_dir = Path(str(getattr(args, "project_dir", "") or "")).expanduser()
        if not str(getattr(args, "project_dir", "") or "").strip():
            project_dir = cfg_base_dir or Path.cwd()
        project_dir = project_dir.resolve()
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "http": http,
            "env_file": str(args.env_file),
            "timeout_s": timeout_s,
            "verbose": bool(args.verbose),
            "apply": bool(args.apply),
            "yes": bool(args.yes),
            "ack_no_snapshot": bool(args.ack_no_snapshot),
            "ack_irreversible": bool(getattr(args, "ack_irreversible", False)),
            "ack_spend": bool(getattr(args, "ack_spend", False)),
            "ack_volume": bool(getattr(args, "ack_volume", False)),
            "project_cfg": project_cfg,
            "project_dir": str(project_dir),
            "skip_auth_for_write_plan": _is_write_plan_or_refusal_command(args),
        }
        return int(args.func(args, ctx))
    except KeyboardInterrupt:
        if _argv_wants_json(argv):
            out.emit({"ok": False, "error": "Interrupted", "error_type": "KeyboardInterrupt"})
        else:
            print("Interrupted.", file=sys.stderr)
        return 130
    except Exception as e:  # noqa: BLE001
        if bool(args.debug):
            traceback.print_exc(file=sys.stderr)
        audit.write("error", {"error": str(e), "error_type": type(e).__name__})
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        return 1
    finally:
        audit.close()
