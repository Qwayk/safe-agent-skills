from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import auth as auth_cmd
from .commands import account_management as account_management_cmd
from .commands import onboarding as onboarding_cmd
from .commands import business_info as business_info_cmd
from .commands import notifications as notifications_cmd
from .commands import business_calls as business_calls_cmd
from .commands import verifications as verifications_cmd
from .commands import media_upload_v1 as media_upload_v1_cmd
from .commands import legacy_v49 as legacy_v49_cmd
from .commands import lodging as lodging_cmd
from .commands import performance as performance_cmd
from .commands import place_actions as place_actions_cmd
from .config import load_config
from .errors import SafetyError, ToolError, ValidationError
from .output import Output
from .project_config import load_project_config
from .runs import (
    RunContext,
    build_deterministic_summary,
    find_run,
    init_run_context,
    list_runs,
    append_index_row,
    write_summary_md,
    runs_index_path_for_env_file,
)


TOOL_NAME = "google-business-profile-safe-cli"


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
    p = _ToolArgumentParser(prog=TOOL_NAME)
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
    auth_check = auth_sub.add_parser("check", help="Smoke test OAuth credentials")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=False)

    auth_login = auth_sub.add_parser("login", help="OAuth installed-app login")
    auth_login.add_argument(
        "--client-secrets-file",
        default=None,
        help="Path to Google OAuth client secrets JSON (overrides GBP_OAUTH_CLIENT_SECRETS_FILE)",
    )
    auth_login.add_argument(
        "--scopes",
        default=None,
        help="OAuth scopes (space/comma separated; overrides GBP_OAUTH_SCOPES)",
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
        help="Local server port for browser flow (0 = auto). Ignored when --console is set.",
    )
    auth_login.set_defaults(func=auth_cmd.cmd_auth_login, write_capable=True)

    token = auth_sub.add_parser("token", help="OAuth token helpers (manual copy/paste)")
    token_sub = token.add_subparsers(dest="token_cmd", required=True, parser_class=_ToolArgumentParser)
    token_set = token_sub.add_parser("set", help="Store token JSON under .state/")
    token_set.add_argument("--file", required=True, help="Token JSON file path (input)")
    token_set.set_defaults(func=auth_cmd.cmd_auth_token_set, write_capable=True)
    token_status = token_sub.add_parser("status", help="Show token status (never prints token values)")
    token_status.set_defaults(func=auth_cmd.cmd_auth_token_status, write_capable=False)

    account_management = sub.add_parser("account-management", help="Account Management API")
    account_management_sub = account_management.add_subparsers(dest="account_management_cmd", required=True, parser_class=_ToolArgumentParser)

    account_management_accounts = account_management_sub.add_parser("accounts", help="Account resources")
    account_management_accounts_sub = account_management_accounts.add_subparsers(
        dest="account_management_accounts_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    am_accounts_list = account_management_accounts_sub.add_parser("list", help="List accounts")
    am_accounts_list.add_argument("--parent-account", default=None, help="Optional parent account filter")
    am_accounts_list.add_argument("--page-size", type=int, default=None, help="Page size")
    am_accounts_list.add_argument("--page-token", default=None, help="Page token")
    am_accounts_list.add_argument("--filter", default=None, help="Filter query")
    am_accounts_list.set_defaults(func=account_management_cmd.cmd_accounts_list, write_capable=False)

    am_accounts_get = account_management_accounts_sub.add_parser("get", help="Get a specific account")
    am_accounts_get.add_argument("--name", required=True, help="Name in accounts/{account} format")
    am_accounts_get.set_defaults(func=account_management_cmd.cmd_account_get, write_capable=False)

    am_accounts_create = account_management_accounts_sub.add_parser("create", help="Create an account")
    am_accounts_create.add_argument("--account-file", required=True, help="JSON Account object file")
    am_accounts_create.set_defaults(func=account_management_cmd.cmd_accounts_create, write_capable=True)

    am_accounts_patch = account_management_accounts_sub.add_parser("patch", help="Patch an account")
    am_accounts_patch.add_argument("--name", required=True, help="accounts/{account}")
    am_accounts_patch.add_argument("--update-mask", required=True, help="Comma-separated editable fields")
    am_accounts_patch.add_argument("--account-file", required=True, help="JSON Account object file")
    am_accounts_patch.add_argument(
        "--validate-only",
        action="store_true",
        help="Send validateOnly query parameter and stay in dry-run mode",
    )
    am_accounts_patch.set_defaults(func=account_management_cmd.cmd_accounts_patch, write_capable=True)

    am_accounts_admins = account_management_accounts_sub.add_parser("admins", help="Account admins")
    am_accounts_admins_sub = am_accounts_admins.add_subparsers(
        dest="account_management_accounts_admins_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    am_accounts_admins_list = am_accounts_admins_sub.add_parser("list", help="List account admins")
    am_accounts_admins_list.add_argument("--parent", required=True, help="accounts/{account}")
    am_accounts_admins_list.set_defaults(
        func=account_management_cmd.cmd_accounts_admins_list,
        write_capable=False,
    )

    am_accounts_admins_create = am_accounts_admins_sub.add_parser("create", help="Create account admin")
    am_accounts_admins_create.add_argument("--parent", required=True, help="accounts/{account}")
    am_accounts_admins_create.add_argument("--admin-file", required=True, help="JSON AccountAdmin object file")
    am_accounts_admins_create.set_defaults(
        func=account_management_cmd.cmd_accounts_admins_create,
        write_capable=True,
    )

    am_accounts_admins_delete = am_accounts_admins_sub.add_parser("delete", help="Delete account admin")
    am_accounts_admins_delete.add_argument(
        "--name",
        required=True,
        help="accounts/{account}/admins/{admin}",
    )
    am_accounts_admins_delete.set_defaults(
        func=account_management_cmd.cmd_accounts_admins_delete,
        write_capable=True,
    )

    am_accounts_admins_patch = am_accounts_admins_sub.add_parser("patch", help="Patch account admin")
    am_accounts_admins_patch.add_argument(
        "--name",
        required=True,
        help="accounts/{account}/admins/{admin}",
    )
    am_accounts_admins_patch.add_argument("--update-mask", required=True, help="Comma-separated editable fields")
    am_accounts_admins_patch.add_argument("--admin-file", required=True, help="JSON AccountAdmin object file")
    am_accounts_admins_patch.set_defaults(
        func=account_management_cmd.cmd_accounts_admins_patch,
        write_capable=True,
    )

    am_accounts_invitations = account_management_accounts_sub.add_parser("invitations", help="Account invitations")
    am_accounts_invitations_sub = am_accounts_invitations.add_subparsers(
        dest="account_management_accounts_invitations_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    am_accounts_invitations_list = am_accounts_invitations_sub.add_parser(
        "list",
        help="List account invitations",
    )
    am_accounts_invitations_list.add_argument("--parent", required=True, help="accounts/{account}")
    am_accounts_invitations_list.add_argument("--filter", default=None, help="Filter query")
    am_accounts_invitations_list.set_defaults(
        func=account_management_cmd.cmd_accounts_invitations_list,
        write_capable=False,
    )

    am_accounts_invitations_accept = am_accounts_invitations_sub.add_parser(
        "accept",
        help="Accept an account invitation",
    )
    am_accounts_invitations_accept.add_argument(
        "--name",
        required=True,
        help="accounts/{account}/invitations/{invitation}",
    )
    am_accounts_invitations_accept.set_defaults(
        func=account_management_cmd.cmd_accounts_invitations_accept,
        write_capable=True,
    )

    am_accounts_invitations_decline = am_accounts_invitations_sub.add_parser(
        "decline",
        help="Decline an account invitation",
    )
    am_accounts_invitations_decline.add_argument(
        "--name",
        required=True,
        help="accounts/{account}/invitations/{invitation}",
    )
    am_accounts_invitations_decline.set_defaults(
        func=account_management_cmd.cmd_accounts_invitations_decline,
        write_capable=True,
    )

    account_management_locations = account_management_sub.add_parser("locations", help="Location admins")
    account_management_locations_sub = account_management_locations.add_subparsers(
        dest="account_management_locations_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    am_locations_admins = account_management_locations_sub.add_parser("admins", help="Location admins")
    am_locations_admins_sub = am_locations_admins.add_subparsers(
        dest="account_management_locations_admins_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    am_locations_admins_list = am_locations_admins_sub.add_parser(
        "list",
        help="List location admins",
    )
    am_locations_admins_list.add_argument("--parent", required=True, help="locations/{location}")
    am_locations_admins_list.set_defaults(
        func=account_management_cmd.cmd_locations_admins_list,
        write_capable=False,
    )

    am_locations_admins_create = am_locations_admins_sub.add_parser(
        "create",
        help="Create a location admin",
    )
    am_locations_admins_create.add_argument("--parent", required=True, help="locations/{location}")
    am_locations_admins_create.add_argument("--admin-file", required=True, help="JSON LocationAdmin object file")
    am_locations_admins_create.set_defaults(
        func=account_management_cmd.cmd_locations_admins_create,
        write_capable=True,
    )

    am_locations_admins_delete = am_locations_admins_sub.add_parser(
        "delete",
        help="Delete a location admin",
    )
    am_locations_admins_delete.add_argument(
        "--name",
        required=True,
        help="locations/{location}/admins/{admin}",
    )
    am_locations_admins_delete.set_defaults(
        func=account_management_cmd.cmd_locations_admins_delete,
        write_capable=True,
    )

    am_locations_admins_patch = am_locations_admins_sub.add_parser(
        "patch",
        help="Patch a location admin",
    )
    am_locations_admins_patch.add_argument(
        "--name",
        required=True,
        help="locations/{location}/admins/{admin}",
    )
    am_locations_admins_patch.add_argument(
        "--update-mask",
        required=True,
        help="Comma-separated editable fields",
    )
    am_locations_admins_patch.add_argument(
        "--admin-file",
        required=True,
        help="JSON LocationAdmin object file",
    )
    am_locations_admins_patch.set_defaults(
        func=account_management_cmd.cmd_locations_admins_patch,
        write_capable=True,
    )

    am_locations_transfer = account_management_locations_sub.add_parser(
        "transfer",
        help="Transfer a location between accounts",
    )
    am_locations_transfer.add_argument("--name", required=True, help="locations/{location}")
    am_locations_transfer.add_argument(
        "--source-account",
        required=True,
        help="accounts/{account}",
    )
    am_locations_transfer.add_argument(
        "--destination-account",
        required=True,
        help="accounts/{account}",
    )
    am_locations_transfer.set_defaults(
        func=account_management_cmd.cmd_locations_transfer,
        write_capable=True,
    )

    business_info = sub.add_parser("business-info", help="Business Information API")
    business_info_sub = business_info.add_subparsers(dest="business_info_cmd", required=True, parser_class=_ToolArgumentParser)

    business_info_accounts = business_info_sub.add_parser("accounts", help="Account-scoped business info")
    business_info_accounts_sub = business_info_accounts.add_subparsers(
        dest="business_info_accounts_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    business_info_accounts_locations = business_info_accounts_sub.add_parser("locations", help="Account locations")
    business_info_accounts_locations_sub = business_info_accounts_locations.add_subparsers(
        dest="business_info_accounts_locations_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    business_info_accounts_locations_list = business_info_accounts_locations_sub.add_parser(
        "list",
        help="List locations",
    )
    business_info_accounts_locations_list.add_argument("--parent", required=True, help="accounts/{account}")
    business_info_accounts_locations_list.add_argument("--read-mask", required=True, help="Comma-separated fields")
    business_info_accounts_locations_list.add_argument("--page-size", type=int, default=None, help="Page size")
    business_info_accounts_locations_list.add_argument("--page-token", default=None, help="Page token")
    business_info_accounts_locations_list.add_argument("--filter", default=None, help="Filter query")
    business_info_accounts_locations_list.add_argument("--order-by", default=None, help="Sort order")
    business_info_accounts_locations_list.set_defaults(
        func=business_info_cmd.cmd_accounts_locations_list,
        write_capable=False,
    )
    business_info_accounts_locations_create = business_info_accounts_locations_sub.add_parser(
        "create",
        help="Create a location",
    )
    business_info_accounts_locations_create.add_argument(
        "--parent",
        required=True,
        help="accounts/{account}",
    )
    business_info_accounts_locations_create.add_argument(
        "--location-file",
        required=True,
        help="JSON Location object file",
    )
    business_info_accounts_locations_create.add_argument(
        "--validate-only",
        action="store_true",
        help="Send validateOnly request and stay in dry-run mode",
    )
    business_info_accounts_locations_create.add_argument(
        "--request-id",
        default=None,
        help="Optional idempotency token",
    )
    business_info_accounts_locations_create.set_defaults(
        func=business_info_cmd.cmd_accounts_locations_create,
        write_capable=True,
    )

    business_info_locations = business_info_sub.add_parser("locations", help="Location resources")
    business_info_locations_sub = business_info_locations.add_subparsers(
        dest="business_info_locations_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    business_info_locations_get = business_info_locations_sub.add_parser("get", help="Get location")
    business_info_locations_get.add_argument("--name", required=True, help="locations/{location}")
    business_info_locations_get.add_argument("--read-mask", required=True, help="Comma-separated fields")
    business_info_locations_get.set_defaults(
        func=business_info_cmd.cmd_locations_get,
        write_capable=False,
    )
    business_info_locations_delete = business_info_locations_sub.add_parser("delete", help="Delete a location")
    business_info_locations_delete.add_argument("--name", required=True, help="locations/{location}")
    business_info_locations_delete.set_defaults(
        func=business_info_cmd.cmd_locations_delete,
        write_capable=True,
    )
    business_info_locations_get_attrs = business_info_locations_sub.add_parser(
        "get-attributes",
        help="Get location attributes",
    )
    business_info_locations_get_attrs.add_argument("--name", required=True, help="locations/{location}/attributes")
    business_info_locations_get_attrs.set_defaults(
        func=business_info_cmd.cmd_locations_get_attributes,
        write_capable=False,
    )
    business_info_locations_patch = business_info_locations_sub.add_parser(
        "patch",
        help="Patch a location",
    )
    business_info_locations_patch.add_argument("--name", required=True, help="locations/{location}")
    business_info_locations_patch.add_argument("--update-mask", required=True, help="Comma-separated field mask")
    business_info_locations_patch.add_argument("--location-file", required=True, help="JSON Location object file")
    business_info_locations_patch.add_argument(
        "--validate-only",
        action="store_true",
        help="Send validateOnly request and stay in dry-run mode",
    )
    business_info_locations_patch.set_defaults(func=business_info_cmd.cmd_locations_patch, write_capable=True)
    business_info_locations_get_google = business_info_locations_sub.add_parser(
        "get-google-updated",
        help="Get location google-updated metadata",
    )
    business_info_locations_get_google.add_argument("--name", required=True, help="locations/{location}")
    business_info_locations_get_google.add_argument("--read-mask", required=True, help="Comma-separated fields")
    business_info_locations_get_google.set_defaults(
        func=business_info_cmd.cmd_locations_get_google_updated,
        write_capable=False,
    )
    business_info_locations_update_attributes = business_info_locations_sub.add_parser(
        "update-attributes",
        help="Patch location attributes",
    )
    business_info_locations_update_attributes.add_argument(
        "--name", required=True, help="locations/{location}/attributes"
    )
    business_info_locations_update_attributes.add_argument(
        "--attribute-mask", required=True, help="Comma-separated attribute fields"
    )
    business_info_locations_update_attributes.add_argument(
        "--attributes-file", required=True, help="JSON Attributes object file"
    )
    business_info_locations_update_attributes.set_defaults(
        func=business_info_cmd.cmd_locations_update_attributes,
        write_capable=True,
    )
    business_info_locations_attributes = business_info_locations_sub.add_parser(
        "attributes",
        help="Location attributes resources",
    )
    business_info_locations_attributes_sub = business_info_locations_attributes.add_subparsers(
        dest="business_info_locations_attributes_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    business_info_locations_attributes_get_google_updated = business_info_locations_attributes_sub.add_parser(
        "get-google-updated",
        help="Get location Google-updated metadata for attributes",
    )
    business_info_locations_attributes_get_google_updated.add_argument(
        "--name",
        required=True,
        help="locations/{location}/attributes",
    )
    business_info_locations_attributes_get_google_updated.set_defaults(
        func=business_info_cmd.cmd_locations_attributes_get_google_updated,
        write_capable=False,
    )

    business_info_attributes = business_info_sub.add_parser("attributes", help="Attribute catalog")
    business_info_attributes_sub = business_info_attributes.add_subparsers(
        dest="business_info_attributes_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    business_info_attributes_list = business_info_attributes_sub.add_parser("list", help="List attributes")
    business_info_attributes_list.add_argument("--parent", default=None, help="locations/{location}")
    business_info_attributes_list.add_argument("--category-name", default=None, help="categories/{category_id}")
    business_info_attributes_list.add_argument("--show-all", action="store_true", help="List all attributes")
    business_info_attributes_list.add_argument("--region-code", default=None, help="CC")
    business_info_attributes_list.add_argument("--language-code", default=None, help="bcp47 code")
    business_info_attributes_list.add_argument("--page-size", type=int, default=None, help="Page size")
    business_info_attributes_list.add_argument("--page-token", default=None, help="Page token")
    business_info_attributes_list.set_defaults(func=business_info_cmd.cmd_attributes_list, write_capable=False)

    business_info_categories = business_info_sub.add_parser("categories", help="Category metadata")
    business_info_categories_sub = business_info_categories.add_subparsers(
        dest="business_info_categories_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    business_info_categories_list = business_info_categories_sub.add_parser("list", help="List categories")
    business_info_categories_list.add_argument("--region-code", required=True, help="CC")
    business_info_categories_list.add_argument("--language-code", required=True, help="bcp47 code")
    business_info_categories_list.add_argument(
        "--view",
        required=True,
        choices=("BASIC", "FULL"),
        help="Category response detail level",
    )
    business_info_categories_list.add_argument("--filter", default=None, help="Filter query")
    business_info_categories_list.add_argument("--page-size", type=int, default=None, help="Page size")
    business_info_categories_list.add_argument("--page-token", default=None, help="Page token")
    business_info_categories_list.set_defaults(
        func=business_info_cmd.cmd_categories_list,
        write_capable=False,
    )
    business_info_categories_batch_get = business_info_categories_sub.add_parser(
        "batch-get",
        help="Batch get categories",
    )
    business_info_categories_batch_get.add_argument("--names", required=True, action="append", help="categories/{category_id}")
    business_info_categories_batch_get.add_argument("--region-code", default=None, help="CC")
    business_info_categories_batch_get.add_argument(
        "--language-code",
        required=True,
        help="bcp47 code",
    )
    business_info_categories_batch_get.add_argument(
        "--view",
        required=True,
        choices=("BASIC", "FULL"),
        help="Category response detail level",
    )
    business_info_categories_batch_get.set_defaults(
        func=business_info_cmd.cmd_categories_batch_get,
        write_capable=False,
    )

    business_info_chains = business_info_sub.add_parser("chains", help="Chain search")
    business_info_chains_sub = business_info_chains.add_subparsers(
        dest="business_info_chains_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    business_info_chains_search = business_info_chains_sub.add_parser("search", help="Search chains by name")
    business_info_chains_search.add_argument("--chain-name", required=True, help="Chain name")
    business_info_chains_search.add_argument("--page-size", type=int, default=None, help="Page size")
    business_info_chains_search.set_defaults(
        func=business_info_cmd.cmd_chains_search,
        write_capable=False,
    )
    business_info_chains_get = business_info_chains_sub.add_parser("get", help="Get a chain")
    business_info_chains_get.add_argument("--name", required=True, help="chains/{chain_place_id}")
    business_info_chains_get.set_defaults(
        func=business_info_cmd.cmd_chains_get,
        write_capable=False,
    )

    business_info_google_locations = business_info_sub.add_parser(
        "google-locations",
        help="Google location search",
    )
    business_info_google_locations_sub = business_info_google_locations.add_subparsers(
        dest="business_info_google_locations_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    business_info_google_locations_search = business_info_google_locations_sub.add_parser(
        "search",
        help="Search Google locations",
    )
    search_mode = business_info_google_locations_search.add_mutually_exclusive_group(required=True)
    search_mode.add_argument("--query", help="Search text")
    search_mode.add_argument("--location-file", help="JSON Location object file")
    business_info_google_locations_search.add_argument("--page-size", type=int, default=None, help="Page size")
    business_info_google_locations_search.set_defaults(
        func=business_info_cmd.cmd_google_locations_search,
        write_capable=False,
    )

    business_calls = sub.add_parser("business-calls", help="Business Calls API")
    business_calls_locations_root = business_calls.add_subparsers(
        dest="business_calls_locations_root_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    business_calls_locations = business_calls_locations_root.add_parser(
        "locations",
        help="Business Calls location resources",
    )
    business_calls_locations_sub = business_calls_locations.add_subparsers(
        dest="business_calls_locations_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    business_calls_locations_get = business_calls_locations_sub.add_parser(
        "get-business-calls-settings",
        help="Get business calls settings",
    )
    business_calls_locations_get.add_argument(
        "--name",
        required=True,
        help="locations/{location}/businesscallssettings",
    )
    business_calls_locations_get.set_defaults(
        func=business_calls_cmd.cmd_locations_get_business_calls_settings,
        write_capable=False,
    )

    business_calls_locations_update = business_calls_locations_sub.add_parser(
        "update-business-calls-settings",
        help="Update business calls settings",
    )
    business_calls_locations_update.add_argument(
        "--name",
        required=True,
        help="locations/{location}/businesscallssettings",
    )
    business_calls_locations_update.add_argument(
        "--update-mask",
        required=True,
        help="Comma-separated fields",
    )
    business_calls_locations_update.add_argument(
        "--business-calls-settings-file",
        required=True,
        help="JSON BusinessCallsSettings object file",
    )
    business_calls_locations_update.set_defaults(
        func=business_calls_cmd.cmd_locations_update_business_calls_settings,
        write_capable=True,
    )

    business_calls_locations_business_calls_insights = business_calls_locations_sub.add_parser(
        "business-calls-insights",
        help="Business Calls insights",
    )
    business_calls_locations_business_calls_insights_sub = (
        business_calls_locations_business_calls_insights.add_subparsers(
            dest="business_calls_locations_business_calls_insights_cmd",
            required=True,
            parser_class=_ToolArgumentParser,
        )
    )
    business_calls_locations_business_calls_insights_list = (
        business_calls_locations_business_calls_insights_sub.add_parser(
            "list",
            help="List business calls insights",
        )
    )
    business_calls_locations_business_calls_insights_list.add_argument(
        "--parent",
        required=True,
        help="locations/{location}",
    )
    business_calls_locations_business_calls_insights_list.add_argument(
        "--page-size",
        type=int,
        default=None,
        help="Page size",
    )
    business_calls_locations_business_calls_insights_list.add_argument(
        "--page-token",
        default=None,
        help="Page token",
    )
    business_calls_locations_business_calls_insights_list.add_argument(
        "--filter",
        default=None,
        help="Filter query",
    )
    business_calls_locations_business_calls_insights_list.set_defaults(
        func=business_calls_cmd.cmd_locations_business_calls_insights_list,
        write_capable=False,
    )

    media_upload_v1 = sub.add_parser("media-upload-v1", help="Media upload v1")
    media_upload_v1_sub = media_upload_v1.add_subparsers(
        dest="media_upload_v1_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    media_upload_v1_media = media_upload_v1_sub.add_parser("media", help="media")
    media_upload_v1_media_sub = media_upload_v1_media.add_subparsers(
        dest="media_upload_v1_media_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    media_upload_v1_media_upload = media_upload_v1_media_sub.add_parser(
        "upload",
        help="Upload metadata or file media",
    )
    media_upload_v1_media_upload.add_argument(
        "--resource-name",
        required=True,
        help="Location resource name or provider-upload resource",
    )
    media_upload_v1_media_upload.add_argument("--media-file", default=None, help="Path to local media file for binary upload")
    media_upload_v1_media_upload.add_argument(
        "--media-json-file",
        default=None,
        help="Path to media JSON object file for metadata upload",
    )
    media_upload_v1_media_upload.add_argument(
        "--content-type",
        default=None,
        help="Optional MIME type for media-file upload; inferred if omitted",
    )
    media_upload_v1_media_upload.set_defaults(
        func=media_upload_v1_cmd.cmd_media_upload,
        write_capable=True,
    )

    legacy_v49 = sub.add_parser("legacy-v49", help="Legacy Google My Business API (v4.9)")
    legacy_v49_sub = legacy_v49.add_subparsers(
        dest="legacy_v49_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    legacy_v49_accounts = legacy_v49_sub.add_parser("accounts", help="Legacy accounts")
    legacy_v49_accounts_sub = legacy_v49_accounts.add_subparsers(
        dest="legacy_v49_accounts_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    legacy_v49_accounts_locations = legacy_v49_accounts_sub.add_parser("locations", help="Legacy account locations")
    legacy_v49_accounts_locations_sub = legacy_v49_accounts_locations.add_subparsers(
        dest="legacy_v49_accounts_locations_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    legacy_v49_accounts_locations_transfer = legacy_v49_accounts_locations_sub.add_parser(
        "transfer",
        help="Transfer a legacy location between accounts",
    )
    legacy_v49_accounts_locations_transfer.add_argument(
        "--name",
        required=True,
        help="accounts/{account}/locations/{location}",
    )
    legacy_v49_accounts_locations_transfer.add_argument(
        "--to-account",
        required=True,
        help="accounts/{account}",
    )
    legacy_v49_accounts_locations_transfer.set_defaults(
        func=legacy_v49_cmd.cmd_accounts_locations_transfer,
        write_capable=True,
    )
    legacy_v49_accounts_locations_media = legacy_v49_accounts_locations_sub.add_parser(
        "media",
        help="Legacy location media",
    )
    legacy_v49_accounts_locations_media_sub = legacy_v49_accounts_locations_media.add_subparsers(
        dest="legacy_v49_accounts_locations_media_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    legacy_v49_accounts_locations_media_start_upload = legacy_v49_accounts_locations_media_sub.add_parser(
        "start-upload",
        help="Start a legacy media upload",
    )
    legacy_v49_accounts_locations_media_start_upload.add_argument(
        "--parent",
        required=True,
        help="accounts/{account}/locations/{location}",
    )
    legacy_v49_accounts_locations_media_start_upload.set_defaults(
        func=legacy_v49_cmd.cmd_accounts_locations_media_start_upload,
        write_capable=True,
    )
    legacy_v49_accounts_locations_media_create = legacy_v49_accounts_locations_media_sub.add_parser(
        "create",
        help="Create a legacy location media record",
    )
    legacy_v49_accounts_locations_media_create.add_argument(
        "--parent",
        required=True,
        help="accounts/{account}/locations/{location}",
    )
    legacy_v49_accounts_locations_media_create.add_argument(
        "--media-item-file",
        required=True,
        help="JSON MediaItem object file",
    )
    legacy_v49_accounts_locations_media_create.set_defaults(
        func=legacy_v49_cmd.cmd_accounts_locations_media_create,
        write_capable=True,
    )
    legacy_v49_accounts_locations_verifications = legacy_v49_accounts_locations_sub.add_parser(
        "verifications",
        help="Legacy location verifications",
    )
    legacy_v49_accounts_locations_verifications_sub = (
        legacy_v49_accounts_locations_verifications.add_subparsers(
            dest="legacy_v49_accounts_locations_verifications_cmd",
            required=True,
            parser_class=_ToolArgumentParser,
        )
    )
    legacy_v49_accounts_locations_verifications_list = (
        legacy_v49_accounts_locations_verifications_sub.add_parser(
            "list",
            help="List verifications for a legacy location",
        )
    )
    legacy_v49_accounts_locations_verifications_list.add_argument(
        "--parent",
        required=True,
        help="accounts/{account}/locations/{location}",
    )
    legacy_v49_accounts_locations_verifications_list.add_argument(
        "--page-size",
        type=int,
        default=None,
        help="Page size",
    )
    legacy_v49_accounts_locations_verifications_list.add_argument(
        "--page-token",
        default=None,
        help="Page token",
    )
    legacy_v49_accounts_locations_verifications_list.set_defaults(
        func=legacy_v49_cmd.cmd_accounts_locations_verifications_list,
        write_capable=False,
    )
    legacy_v49_accounts_locations_verifications_complete = (
        legacy_v49_accounts_locations_verifications_sub.add_parser(
            "complete",
            help="Complete a legacy location verification",
        )
    )
    legacy_v49_accounts_locations_verifications_complete.add_argument(
        "--name",
        required=True,
        help="accounts/{account}/locations/{location}/verifications/{verification}",
    )
    legacy_v49_accounts_locations_verifications_complete.add_argument(
        "--pin-file",
        required=True,
        help="Path to file containing the verification PIN",
    )
    legacy_v49_accounts_locations_verifications_complete.set_defaults(
        func=legacy_v49_cmd.cmd_accounts_locations_verifications_complete,
        write_capable=True,
    )
    legacy_v49_accounts_locations_reviews = legacy_v49_accounts_locations_sub.add_parser(
        "reviews",
        help="Legacy location reviews",
    )
    legacy_v49_accounts_locations_reviews_sub = legacy_v49_accounts_locations_reviews.add_subparsers(
        dest="legacy_v49_accounts_locations_reviews_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    legacy_v49_accounts_locations_reviews_list = legacy_v49_accounts_locations_reviews_sub.add_parser(
        "list",
        help="List reviews for a legacy location",
    )
    legacy_v49_accounts_locations_reviews_list.add_argument(
        "--parent",
        required=True,
        help="accounts/{account}/locations/{location}",
    )
    legacy_v49_accounts_locations_reviews_list.add_argument(
        "--page-size",
        type=int,
        default=None,
        help="Page size (max 50)",
    )
    legacy_v49_accounts_locations_reviews_list.add_argument(
        "--page-token",
        default=None,
        help="Page token",
    )
    legacy_v49_accounts_locations_reviews_list.add_argument(
        "--order-by",
        default=None,
        help="Sort order (rating, rating desc, updateTime desc)",
    )
    legacy_v49_accounts_locations_reviews_list.set_defaults(
        func=legacy_v49_cmd.cmd_accounts_locations_reviews_list,
        write_capable=False,
    )
    legacy_v49_accounts_locations_reviews_get = legacy_v49_accounts_locations_reviews_sub.add_parser(
        "get",
        help="Get one review",
    )
    legacy_v49_accounts_locations_reviews_get.add_argument(
        "--name",
        required=True,
        help="accounts/{account}/locations/{location}/reviews/{review}",
    )
    legacy_v49_accounts_locations_reviews_get.set_defaults(
        func=legacy_v49_cmd.cmd_accounts_locations_reviews_get,
        write_capable=False,
    )
    legacy_v49_accounts_locations_reviews_update_reply = legacy_v49_accounts_locations_reviews_sub.add_parser(
        "update-reply",
        help="Create or update a review reply",
    )
    legacy_v49_accounts_locations_reviews_update_reply.add_argument(
        "--name",
        required=True,
        help="accounts/{account}/locations/{location}/reviews/{review}",
    )
    legacy_v49_accounts_locations_reviews_update_reply.add_argument(
        "--reply-file",
        required=True,
        help='JSON object with {"comment": "..."}',
    )
    legacy_v49_accounts_locations_reviews_update_reply.set_defaults(
        func=legacy_v49_cmd.cmd_accounts_locations_reviews_update_reply,
        write_capable=True,
    )
    legacy_v49_accounts_locations_reviews_delete_reply = legacy_v49_accounts_locations_reviews_sub.add_parser(
        "delete-reply",
        help="Delete a review reply",
    )
    legacy_v49_accounts_locations_reviews_delete_reply.add_argument(
        "--name",
        required=True,
        help="accounts/{account}/locations/{location}/reviews/{review}",
    )
    legacy_v49_accounts_locations_reviews_delete_reply.set_defaults(
        func=legacy_v49_cmd.cmd_accounts_locations_reviews_delete_reply,
        write_capable=True,
    )

    lodging = sub.add_parser("lodging", help="Lodging API")
    lodging_locations_root = lodging.add_subparsers(
        dest="lodging_locations_root_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    lodging_locations = lodging_locations_root.add_parser(
        "locations",
        help="Lodging location resources",
    )
    lodging_locations_sub = lodging_locations.add_subparsers(
        dest="lodging_locations_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    lodging_locations_get = lodging_locations_sub.add_parser(
        "get-lodging",
        help="Get lodging details",
    )
    lodging_locations_get.add_argument(
        "--name",
        required=True,
        help="locations/{location}/lodging",
    )
    lodging_locations_get.add_argument(
        "--read-mask",
        required=True,
        help="Comma-separated fields",
    )
    lodging_locations_get.set_defaults(
        func=lodging_cmd.cmd_locations_get_lodging,
        write_capable=False,
    )

    lodging_locations_update = lodging_locations_sub.add_parser(
        "update-lodging",
        help="Update lodging details",
    )
    lodging_locations_update.add_argument(
        "--name",
        required=True,
        help="locations/{location}/lodging",
    )
    lodging_locations_update.add_argument(
        "--update-mask",
        required=True,
        help="Comma-separated fields",
    )
    lodging_locations_update.add_argument(
        "--lodging-file",
        required=True,
        help="JSON Lodging object file",
    )
    lodging_locations_update.set_defaults(
        func=lodging_cmd.cmd_locations_update_lodging,
        write_capable=True,
    )

    lodging_locations_lodging = lodging_locations_sub.add_parser(
        "lodging",
        help="Lodging helpers",
    )
    lodging_locations_lodging_sub = lodging_locations_lodging.add_subparsers(
        dest="lodging_locations_lodging_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    lodging_locations_lodging_get_google_updated = lodging_locations_lodging_sub.add_parser(
        "get-google-updated",
        help="Get google-updated metadata for lodging",
    )
    lodging_locations_lodging_get_google_updated.add_argument(
        "--name",
        required=True,
        help="locations/{location}/lodging",
    )
    lodging_locations_lodging_get_google_updated.add_argument(
        "--read-mask",
        required=True,
        help="Comma-separated fields",
    )
    lodging_locations_lodging_get_google_updated.set_defaults(
        func=lodging_cmd.cmd_locations_lodging_get_google_updated,
        write_capable=False,
    )

    performance = sub.add_parser("performance", help="Performance API")
    performance_locations_root = performance.add_subparsers(
        dest="performance_locations_root_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    performance_locations = performance_locations_root.add_parser(
        "locations",
        help="Performance location resources",
    )
    performance_locations_sub = performance_locations.add_subparsers(
        dest="performance_locations_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    performance_locations_fetch = performance_locations_sub.add_parser(
        "fetch-multi-daily-metrics-time-series",
        help="Fetch daily metrics time-series for one location",
    )
    performance_locations_fetch.add_argument("--location", required=True, help="locations/{location}")
    performance_locations_fetch.add_argument(
        "--daily-metrics",
        required=True,
        nargs="+",
        help="One or more daily metrics",
    )
    performance_locations_fetch.add_argument("--daily-range-start-year", required=True, type=int, help="Start year")
    performance_locations_fetch.add_argument(
        "--daily-range-start-month", required=True, type=int, help="Start month"
    )
    performance_locations_fetch.add_argument("--daily-range-start-day", required=True, type=int, help="Start day")
    performance_locations_fetch.add_argument("--daily-range-end-year", required=True, type=int, help="End year")
    performance_locations_fetch.add_argument("--daily-range-end-month", required=True, type=int, help="End month")
    performance_locations_fetch.add_argument("--daily-range-end-day", required=True, type=int, help="End day")
    performance_locations_fetch.set_defaults(
        func=performance_cmd.cmd_locations_fetch_multi_daily_metrics_time_series,
        write_capable=False,
    )

    performance_locations_get = performance_locations_sub.add_parser(
        "get-daily-metrics-time-series",
        help="Get one daily metric time-series for a location",
    )
    performance_locations_get.add_argument("--name", required=True, help="locations/{location}")
    performance_locations_get.add_argument("--daily-metric", required=True, help="Requested daily metric")
    performance_locations_get.add_argument("--daily-range-start-year", required=True, type=int, help="Start year")
    performance_locations_get.add_argument("--daily-range-start-month", required=True, type=int, help="Start month")
    performance_locations_get.add_argument("--daily-range-start-day", required=True, type=int, help="Start day")
    performance_locations_get.add_argument("--daily-range-end-year", required=True, type=int, help="End year")
    performance_locations_get.add_argument("--daily-range-end-month", required=True, type=int, help="End month")
    performance_locations_get.add_argument("--daily-range-end-day", required=True, type=int, help="End day")
    performance_locations_get.set_defaults(
        func=performance_cmd.cmd_locations_get_daily_metrics_time_series,
        write_capable=False,
    )

    performance_locations_search_keywords = performance_locations_sub.add_parser(
        "search-keywords",
        help="Search keyword insights",
    )
    performance_locations_search_keywords_sub = performance_locations_search_keywords.add_subparsers(
        dest="performance_locations_search_keywords_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    performance_locations_search_keywords_impressions = performance_locations_search_keywords_sub.add_parser(
        "impressions",
        help="Search keyword impressions",
    )
    performance_locations_search_keywords_impressions_sub = (
        performance_locations_search_keywords_impressions.add_subparsers(
            dest="performance_locations_search_keywords_impressions_cmd",
            required=True,
            parser_class=_ToolArgumentParser,
        )
    )
    performance_locations_search_keywords_monthly = performance_locations_search_keywords_impressions_sub.add_parser(
        "monthly",
        help="Monthly search-keyword impressions",
    )
    performance_locations_search_keywords_monthly_sub = (
        performance_locations_search_keywords_monthly.add_subparsers(
            dest="performance_locations_search_keywords_monthly_cmd",
            required=True,
            parser_class=_ToolArgumentParser,
        )
    )
    performance_locations_search_keywords_monthly_list = (
        performance_locations_search_keywords_monthly_sub.add_parser(
            "list",
            help="List monthly search-keyword impressions",
        )
    )
    performance_locations_search_keywords_monthly_list.add_argument(
        "--parent",
        required=True,
        help="locations/{location}",
    )
    performance_locations_search_keywords_monthly_list.add_argument(
        "--monthly-range-start-year",
        required=True,
        type=int,
        help="Start year",
    )
    performance_locations_search_keywords_monthly_list.add_argument(
        "--monthly-range-start-month",
        required=True,
        type=int,
        help="Start month",
    )
    performance_locations_search_keywords_monthly_list.add_argument(
        "--monthly-range-end-year",
        required=True,
        type=int,
        help="End year",
    )
    performance_locations_search_keywords_monthly_list.add_argument(
        "--monthly-range-end-month",
        required=True,
        type=int,
        help="End month",
    )
    performance_locations_search_keywords_monthly_list.add_argument(
        "--page-size",
        type=int,
        default=None,
        help="Page size",
    )
    performance_locations_search_keywords_monthly_list.add_argument(
        "--page-token",
        default=None,
        help="Page token",
    )
    performance_locations_search_keywords_monthly_list.set_defaults(
        func=performance_cmd.cmd_locations_search_keywords_impressions_monthly_list,
        write_capable=False,
    )

    place_actions = sub.add_parser("place-actions", help="Place Actions API")
    place_actions_locations_root = place_actions.add_subparsers(
        dest="place_actions_locations_root_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    place_actions_locations = place_actions_locations_root.add_parser(
        "locations",
        help="Place Action Link resources",
    )
    place_actions_locations_sub = place_actions_locations.add_subparsers(
        dest="place_actions_locations_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    place_actions_locations_place_action_links = place_actions_locations_sub.add_parser(
        "place-action-links",
        help="Place action links",
    )
    place_actions_locations_place_action_links_sub = (
        place_actions_locations_place_action_links.add_subparsers(
            dest="place_actions_locations_place_action_links_cmd",
            required=True,
            parser_class=_ToolArgumentParser,
        )
    )
    place_actions_locations_place_action_links_create = place_actions_locations_place_action_links_sub.add_parser(
        "create",
        help="Create a place action link",
    )
    place_actions_locations_place_action_links_create.add_argument(
        "--parent",
        required=True,
        help="locations/{location}",
    )
    place_actions_locations_place_action_links_create.add_argument(
        "--place-action-link-file",
        required=True,
        help="JSON PlaceActionLink object file",
    )
    place_actions_locations_place_action_links_create.set_defaults(
        func=place_actions_cmd.cmd_locations_place_action_links_create,
        write_capable=True,
    )

    place_actions_locations_place_action_links_delete = place_actions_locations_place_action_links_sub.add_parser(
        "delete",
        help="Delete a place action link",
    )
    place_actions_locations_place_action_links_delete.add_argument(
        "--name",
        required=True,
        help="locations/{location}/placeActionLinks/{id}",
    )
    place_actions_locations_place_action_links_delete.set_defaults(
        func=place_actions_cmd.cmd_locations_place_action_links_delete,
        write_capable=True,
    )
    place_actions_locations_place_action_links_get = place_actions_locations_place_action_links_sub.add_parser(
        "get",
        help="Get a place action link",
    )
    place_actions_locations_place_action_links_get.add_argument(
        "--name",
        required=True,
        help="locations/{location}/placeActionLinks/{id}",
    )
    place_actions_locations_place_action_links_get.set_defaults(
        func=place_actions_cmd.cmd_locations_place_action_links_get,
        write_capable=False,
    )

    place_actions_locations_place_action_links_list = place_actions_locations_place_action_links_sub.add_parser(
        "list",
        help="List place action links",
    )
    place_actions_locations_place_action_links_list.add_argument(
        "--parent",
        required=True,
        help="locations/{location}",
    )
    place_actions_locations_place_action_links_list.add_argument(
        "--filter",
        default=None,
        help="Filter query",
    )
    place_actions_locations_place_action_links_list.add_argument(
        "--page-size",
        type=int,
        default=None,
        help="Page size",
    )
    place_actions_locations_place_action_links_list.add_argument(
        "--page-token",
        default=None,
        help="Page token",
    )
    place_actions_locations_place_action_links_list.set_defaults(
        func=place_actions_cmd.cmd_locations_place_action_links_list,
        write_capable=False,
    )

    place_actions_locations_place_action_links_patch = place_actions_locations_place_action_links_sub.add_parser(
        "patch",
        help="Patch a place action link",
    )
    place_actions_locations_place_action_links_patch.add_argument(
        "--name",
        required=True,
        help="locations/{location}/placeActionLinks/{id}",
    )
    place_actions_locations_place_action_links_patch.add_argument(
        "--update-mask",
        required=True,
        help="Comma-separated editable fields",
    )
    place_actions_locations_place_action_links_patch.add_argument(
        "--place-action-link-file",
        required=True,
        help="JSON PlaceActionLink object file",
    )
    place_actions_locations_place_action_links_patch.set_defaults(
        func=place_actions_cmd.cmd_locations_place_action_links_patch,
        write_capable=True,
    )

    place_actions_place_action_type_metadata = place_actions_locations_root.add_parser(
        "place-action-type-metadata",
        help="Place action type metadata",
    )
    place_actions_place_action_type_metadata_sub = place_actions_place_action_type_metadata.add_subparsers(
        dest="place_actions_place_action_type_metadata_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    place_actions_place_action_type_metadata_list = place_actions_place_action_type_metadata_sub.add_parser(
        "list",
        help="List place action type metadata",
    )
    place_actions_place_action_type_metadata_list.add_argument(
        "--language-code",
        default=None,
        help="bcp47 language code",
    )
    place_actions_place_action_type_metadata_list.add_argument(
        "--page-size",
        type=int,
        default=None,
        help="Page size",
    )
    place_actions_place_action_type_metadata_list.add_argument(
        "--page-token",
        default=None,
        help="Page token",
    )
    place_actions_place_action_type_metadata_list.add_argument(
        "--filter",
        default=None,
        help="Filter query",
    )
    place_actions_place_action_type_metadata_list.set_defaults(
        func=place_actions_cmd.cmd_place_action_type_metadata_list,
        write_capable=False,
    )

    verifications = sub.add_parser("verifications", help="Location verification API")
    verifications_locations_root = verifications.add_subparsers(
        dest="verifications_locations_root_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    verifications_locations = verifications_locations_root.add_parser(
        "locations",
        help="Location verification resources",
    )
    verifications_locations_sub = verifications_locations.add_subparsers(
        dest="verifications_locations_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    verifications_locations_fetch_verification_options = verifications_locations_sub.add_parser(
        "fetch-verification-options",
        help="Fetch verification options for a location",
    )
    verifications_locations_fetch_verification_options.add_argument(
        "--location",
        required=True,
        help="locations/{location}",
    )
    verifications_locations_fetch_verification_options.add_argument(
        "--language-code",
        required=True,
        help="bcp47 code",
    )
    verifications_locations_fetch_verification_options.add_argument(
        "--context-file",
        default=None,
        help="Optional JSON ServiceBusinessContext object",
    )
    verifications_locations_fetch_verification_options.set_defaults(
        func=verifications_cmd.cmd_locations_fetch_verification_options,
        write_capable=False,
    )

    verifications_verification_tokens = verifications_locations_root.add_parser(
        "verification-tokens",
        help="Verification token operations.",
    )
    verifications_verification_tokens_sub = verifications_verification_tokens.add_subparsers(
        dest="verifications_verification_tokens_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    verifications_verification_tokens_generate = verifications_verification_tokens_sub.add_parser(
        "generate",
        help="Generate an instant verification token.",
    )
    verifications_verification_tokens_generate.add_argument(
        "--location-id",
        required=True,
        help="Location numeric identifier for token generation.",
    )
    verifications_verification_tokens_generate.add_argument(
        "--verification-token-out",
        required=False,
        default=None,
        help="Output file for the raw token; use only with --apply.",
    )
    verifications_verification_tokens_generate.set_defaults(
        func=verifications_cmd.cmd_verification_tokens_generate,
        write_capable=True,
    )

    verifications_locations_get_voice_of_merchant_state = verifications_locations_sub.add_parser(
        "get-voice-of-merchant-state",
        help="Get voice-of-merchant state for a location",
    )
    verifications_locations_get_voice_of_merchant_state.add_argument(
        "--name",
        required=True,
        help="locations/{location}",
    )
    verifications_locations_get_voice_of_merchant_state.set_defaults(
        func=verifications_cmd.cmd_locations_get_voice_of_merchant_state,
        write_capable=False,
    )

    verifications_locations_verifications = verifications_locations_sub.add_parser(
        "verifications",
        help="Verification resources",
    )
    verifications_locations_verifications_sub = verifications_locations_verifications.add_subparsers(
        dest="verifications_locations_verifications_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    verifications_locations_verifications_list = verifications_locations_verifications_sub.add_parser(
        "list",
        help="List verifications",
    )
    verifications_locations_verifications_list.add_argument(
        "--parent",
        required=True,
        help="locations/{location}",
    )
    verifications_locations_verifications_list.add_argument(
        "--page-size",
        type=int,
        default=None,
        help="Page size",
    )
    verifications_locations_verifications_list.add_argument(
        "--page-token",
        default=None,
        help="Page token",
    )
    verifications_locations_verifications_list.set_defaults(
        func=verifications_cmd.cmd_locations_verifications_list,
        write_capable=False,
    )

    verifications_locations_verify = verifications_locations_sub.add_parser(
        "verify",
        help="Start a verification request for a location",
    )
    verifications_locations_verify.add_argument(
        "--name",
        required=True,
        help="locations/{location}",
    )
    verifications_locations_verify.add_argument(
        "--method",
        required=True,
        help="Verification method: ADDRESS, EMAIL, PHONE_CALL, SMS, AUTO, TRUSTED_PARTNER",
    )
    verifications_locations_verify.add_argument("--language-code", default=None, help="Optional bcp47 language code.")
    verifications_locations_verify.add_argument("--mailer-contact", default=None, help="Optional mailer contact phone or id.")
    verifications_locations_verify.add_argument("--phone-number", default=None, help="Optional phone number.")
    verifications_locations_verify.add_argument("--email-address", default=None, help="Optional email address.")
    verifications_locations_verify.add_argument(
        "--context-file",
        default=None,
        help="Optional JSON ServiceBusinessContext object.",
    )
    verifications_locations_verify.add_argument(
        "--verification-token-file",
        default=None,
        help="Optional JSON VerificationToken object.",
    )
    verifications_locations_verify.add_argument(
        "--trusted-partner-token-file",
        default=None,
        help="Optional plain-text trusted partner token file.",
    )
    verifications_locations_verify.set_defaults(
        func=verifications_cmd.cmd_locations_verify,
        write_capable=True,
    )

    verifications_locations_verifications_complete = verifications_locations_verifications_sub.add_parser(
        "complete",
        help="Complete a verification with a PIN",
    )
    verifications_locations_verifications_complete.add_argument(
        "--name",
        required=True,
        help="locations/{location}/verifications/{verification}",
    )
    verifications_locations_verifications_complete.add_argument(
        "--pin-file",
        required=True,
        help="Plain-text PIN file.",
    )
    verifications_locations_verifications_complete.set_defaults(
        func=verifications_cmd.cmd_locations_verifications_complete,
        write_capable=True,
    )

    notifications = sub.add_parser("notifications", help="Notification settings")
    notifications_sub = notifications.add_subparsers(
        dest="notifications_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    notifications_accounts = notifications_sub.add_parser("accounts", help="Account notification settings")
    notifications_accounts_sub = notifications_accounts.add_subparsers(
        dest="notifications_accounts_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    notifications_accounts_get = notifications_accounts_sub.add_parser(
        "get-notification-setting",
        help="Get account notification setting",
    )
    notifications_accounts_get.add_argument(
        "--name",
        required=True,
        help="accounts/{account}/notificationSetting",
    )
    notifications_accounts_get.set_defaults(
        func=notifications_cmd.cmd_accounts_get_notification_setting,
        write_capable=False,
    )
    notifications_accounts_update = notifications_accounts_sub.add_parser(
        "update-notification-setting",
        help="Update account notification setting",
    )
    notifications_accounts_update.add_argument(
        "--name",
        required=True,
        help="accounts/{account}/notificationSetting",
    )
    notifications_accounts_update.add_argument(
        "--notification-setting-file",
        required=True,
        help="JSON NotificationSetting object file",
    )
    notifications_accounts_update.add_argument(
        "--update-mask",
        required=True,
        help="Comma-separated fields to update",
    )
    notifications_accounts_update.set_defaults(
        func=notifications_cmd.cmd_accounts_update_notification_setting,
        write_capable=True,
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
            payload = {"ok": True, "tool": TOOL_NAME, "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"{TOOL_NAME} {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        command_str = f"{TOOL_NAME} " + " ".join(argv)
        audit.bind_context(
            {
                "tool": TOOL_NAME,
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
                "tool": TOOL_NAME,
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
            "tool": TOOL_NAME,
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
                "tool": TOOL_NAME,
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
            tool=TOOL_NAME,
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
            tool=TOOL_NAME,
            version=__version__,
            command=f"{TOOL_NAME} " + " ".join(argv),
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
            tool=TOOL_NAME,
            version=__version__,
            command=f"{TOOL_NAME} " + " ".join(argv),
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
            tool=TOOL_NAME,
            version=__version__,
            command=f"{TOOL_NAME} " + " ".join(argv),
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
