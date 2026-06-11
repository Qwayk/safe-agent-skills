from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import analytics as analytics_cmd
from .commands import accounts as accounts_cmd
from .commands import account_campaign_mappings as account_campaign_mappings_cmd
from .commands import auth as auth_cmd
from .commands import api_keys as api_keys_cmd
from .commands import audit_log_api as audit_log_cmd
from .commands import background_jobs as background_jobs_cmd
from .commands import campaigns as campaigns_cmd
from .commands import crm_actions as crm_actions_cmd
from .commands import custom_tag_mappings as custom_tag_mappings_cmd
from .commands import custom_tags as custom_tags_cmd
from .commands import dfy_email_account_orders as dfy_cmd
from .commands import do_not_contact as dnc_cmd
from .commands import email_verification as email_verification_cmd
from .commands import emails as emails_cmd
from .commands import inbox_placement as inbox_placement_cmd
from .commands import lead_labels as lead_labels_cmd
from .commands import lead_lists as lead_lists_cmd
from .commands import leads as leads_cmd
from .commands import onboarding as onboarding_cmd
from .commands import subsequences as subsequences_cmd
from .commands import supersearch_enrichment as supersearch_enrichment_cmd
from .commands import oauth as oauth_cmd
from .commands import threads as threads_cmd
from .commands import webhook_events as webhook_events_cmd
from .commands import webhooks as webhooks_cmd
from .commands import whoami as whoami_cmd
from .commands import workspace as workspace_cmd
from .commands import workspace_billing as workspace_billing_cmd
from .commands import workspace_group_members as workspace_group_members_cmd
from .commands import workspace_members as workspace_members_cmd
from .before_state import write_context
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
    p = _ToolArgumentParser(prog="instantly-api-tool")
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
    auth_check = auth_sub.add_parser("check", help="Smoke test credentials")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=False)

    whoami = sub.add_parser("whoami", help="Show current workspace (who am I)")
    whoami.set_defaults(func=whoami_cmd.cmd_whoami, write_capable=False)

    health = sub.add_parser("health", help="Health check (workspaces/current)")
    health.set_defaults(func=whoami_cmd.cmd_health, write_capable=False)

    workspace = sub.add_parser("workspace", help="Workspace admin operations")
    workspace_sub = workspace.add_subparsers(dest="workspace_cmd", required=True, parser_class=_ToolArgumentParser)
    workspace_get_current = workspace_sub.add_parser("get-current", help="Get current workspace")
    workspace_get_current.set_defaults(func=workspace_cmd.cmd_workspace_get_current, write_capable=False)
    workspace_patch_current = workspace_sub.add_parser("patch-current", help="Patch current workspace (apply requires --plan-in)")
    workspace_patch_current.add_argument("--file", required=False, help="Workspace patch JSON (required unless --plan-in)")
    workspace_patch_current.set_defaults(func=workspace_cmd.cmd_workspace_patch_current, write_capable=True)
    workspace_create = workspace_sub.add_parser("create", help="Create a workspace (JSON file)")
    workspace_create.add_argument("--file", required=True, help="Workspace create JSON file")
    workspace_create.set_defaults(func=workspace_cmd.cmd_workspace_create, write_capable=True)
    workspace_change_owner = workspace_sub.add_parser("change-owner", help="Change workspace owner (apply requires --plan-in)")
    workspace_change_owner.add_argument("--file", required=False, help="Change-owner JSON file (required unless --plan-in)")
    workspace_change_owner.set_defaults(func=workspace_cmd.cmd_workspace_change_owner, write_capable=True)
    wl = workspace_sub.add_parser("whitelabel-domain", help="Workspace whitelabel domain")
    wl_sub = wl.add_subparsers(dest="wl_cmd", required=True, parser_class=_ToolArgumentParser)
    wl_get = wl_sub.add_parser("get", help="Get current whitelabel domain")
    wl_get.set_defaults(func=workspace_cmd.cmd_workspace_whitelabel_get, write_capable=False)
    wl_set = wl_sub.add_parser("set", help="Set current whitelabel domain (JSON file)")
    wl_set.add_argument("--file", required=True, help="Whitelabel-domain JSON file")
    wl_set.set_defaults(func=workspace_cmd.cmd_workspace_whitelabel_set, write_capable=True)
    wl_delete = wl_sub.add_parser("delete", help="Delete current whitelabel domain (requires --apply --yes --plan-in)")
    wl_delete.set_defaults(func=workspace_cmd.cmd_workspace_whitelabel_delete, write_capable=True)

    workspace_billing = sub.add_parser("workspace-billing", help="Workspace billing (read-only)")
    workspace_billing_sub = workspace_billing.add_subparsers(
        dest="workspace_billing_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    wbp = workspace_billing_sub.add_parser("plan-details", help="Get plan details")
    wbp.set_defaults(func=workspace_billing_cmd.cmd_workspace_billing_plan_details, write_capable=False)
    wbs = workspace_billing_sub.add_parser("subscription-details", help="Get subscription details")
    wbs.set_defaults(func=workspace_billing_cmd.cmd_workspace_billing_subscription_details, write_capable=False)

    workspace_members = sub.add_parser("workspace-members", help="Workspace members")
    workspace_members_sub = workspace_members.add_subparsers(
        dest="workspace_members_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    wml = workspace_members_sub.add_parser("list", help="List workspace members")
    wml.add_argument("--limit", type=int, default=None, help="Page size")
    wml.add_argument("--starting-after", default=None, help="Pagination cursor")
    wml.set_defaults(func=workspace_members_cmd.cmd_workspace_members_list, write_capable=False)
    wmg = workspace_members_sub.add_parser("get", help="Get workspace member by id")
    wmg.add_argument("--id", required=True, help="Workspace member id")
    wmg.set_defaults(func=workspace_members_cmd.cmd_workspace_members_get, write_capable=False)
    wmc = workspace_members_sub.add_parser("create", help="Create workspace member (JSON file)")
    wmc.add_argument("--file", required=True, help="Workspace member create JSON file")
    wmc.set_defaults(func=workspace_members_cmd.cmd_workspace_members_create, write_capable=True)
    wmp = workspace_members_sub.add_parser("patch", help="Patch workspace member (JSON file)")
    wmp.add_argument("--id", required=True, help="Workspace member id")
    wmp.add_argument("--file", required=True, help="Workspace member patch JSON file")
    wmp.set_defaults(func=workspace_members_cmd.cmd_workspace_members_patch, write_capable=True)
    wmd = workspace_members_sub.add_parser("delete", help="Delete workspace member (requires --apply --yes --plan-in)")
    wmd.add_argument("--id", required=False, help="Workspace member id (required unless --plan-in)")
    wmd.set_defaults(func=workspace_members_cmd.cmd_workspace_members_delete, write_capable=True)

    workspace_group_members = sub.add_parser("workspace-group-members", help="Workspace group members")
    workspace_group_members_sub = workspace_group_members.add_subparsers(
        dest="workspace_group_members_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    wgm_list = workspace_group_members_sub.add_parser("list", help="List workspace group members")
    wgm_list.add_argument("--limit", type=int, default=None, help="Page size")
    wgm_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    wgm_list.set_defaults(func=workspace_group_members_cmd.cmd_workspace_group_members_list, write_capable=False)
    wgm_admin = workspace_group_members_sub.add_parser("admin", help="List admin group memberships")
    wgm_admin.set_defaults(func=workspace_group_members_cmd.cmd_workspace_group_members_admin, write_capable=False)
    wgm_get = workspace_group_members_sub.add_parser("get", help="Get workspace group member by id")
    wgm_get.add_argument("--id", required=True, help="Workspace group member id")
    wgm_get.set_defaults(func=workspace_group_members_cmd.cmd_workspace_group_members_get, write_capable=False)
    wgm_create = workspace_group_members_sub.add_parser("create", help="Create workspace group member (JSON file)")
    wgm_create.add_argument("--file", required=True, help="Workspace group member create JSON file")
    wgm_create.set_defaults(func=workspace_group_members_cmd.cmd_workspace_group_members_create, write_capable=True)
    wgm_delete = workspace_group_members_sub.add_parser(
        "delete",
        help="Delete workspace group member (requires --apply --yes --plan-in)",
    )
    wgm_delete.add_argument("--id", required=False, help="Workspace group member id (required unless --plan-in)")
    wgm_delete.set_defaults(func=workspace_group_members_cmd.cmd_workspace_group_members_delete, write_capable=True)

    oauth = sub.add_parser("oauth", help="OAuth session init/status")
    oauth_sub = oauth.add_subparsers(dest="oauth_cmd", required=True, parser_class=_ToolArgumentParser)
    og = oauth_sub.add_parser("google-init", help="Init a Google OAuth session (JSON file)")
    og.add_argument("--file", required=True, help="OAuth init JSON file")
    og.set_defaults(func=oauth_cmd.cmd_oauth_google_init, write_capable=True)
    om = oauth_sub.add_parser("microsoft-init", help="Init a Microsoft OAuth session (JSON file)")
    om.add_argument("--file", required=True, help="OAuth init JSON file")
    om.set_defaults(func=oauth_cmd.cmd_oauth_microsoft_init, write_capable=True)
    osess = oauth_sub.add_parser("session-status", help="Check OAuth session status")
    osess.add_argument("--session-id", required=True, help="OAuth session id")
    osess.set_defaults(func=oauth_cmd.cmd_oauth_session_status, write_capable=False)

    api_keys = sub.add_parser("api-keys", help="API keys (secret-safe)")
    api_keys_sub = api_keys.add_subparsers(dest="api_keys_cmd", required=True, parser_class=_ToolArgumentParser)
    ak_list = api_keys_sub.add_parser("list", help="List API keys")
    ak_list.add_argument("--limit", type=int, default=None, help="Page size")
    ak_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    ak_list.set_defaults(func=api_keys_cmd.cmd_api_keys_list, write_capable=False)
    ak_create = api_keys_sub.add_parser(
        "create",
        help="Create API key (apply requires --yes --plan-in and stores raw key locally)",
    )
    ak_create.add_argument("--file", required=False, help="API key create JSON file (required unless --plan-in)")
    ak_create.add_argument(
        "--ack-store-secret-locally",
        action="store_true",
        help="Acknowledge storing secret-bearing output under .state/ (required on apply)",
    )
    ak_create.set_defaults(func=api_keys_cmd.cmd_api_keys_create, write_capable=True)
    ak_delete = api_keys_sub.add_parser("delete", help="Delete API key (requires --apply --yes --plan-in)")
    ak_delete.add_argument("--id", required=False, help="API key id (required unless --plan-in)")
    ak_delete.set_defaults(func=api_keys_cmd.cmd_api_keys_delete, write_capable=True)

    dfy = sub.add_parser("dfy-email-account-orders", help="DFY email account orders")
    dfy_sub = dfy.add_subparsers(dest="dfy_cmd", required=True, parser_class=_ToolArgumentParser)
    dfy_list_orders = dfy_sub.add_parser("list-orders", help="List DFY orders")
    dfy_list_orders.add_argument("--limit", type=int, default=None, help="Page size")
    dfy_list_orders.add_argument("--starting-after", default=None, help="Pagination cursor")
    dfy_list_orders.set_defaults(func=dfy_cmd.cmd_dfy_list_orders, write_capable=False)
    dfy_list_accounts = dfy_sub.add_parser("list-accounts", help="List DFY email accounts")
    dfy_list_accounts.add_argument("--limit", type=int, default=None, help="Page size")
    dfy_list_accounts.add_argument("--starting-after", default=None, help="Pagination cursor")
    dfy_list_accounts.add_argument(
        "--with-passwords",
        action="store_true",
        help="Request password fields (secret-bearing; requires --ack-store-secret-locally)",
    )
    dfy_list_accounts.add_argument(
        "--ack-store-secret-locally",
        action="store_true",
        help="Acknowledge storing secret-bearing output under .state/ (required with --with-passwords)",
    )
    dfy_list_accounts.set_defaults(func=dfy_cmd.cmd_dfy_list_accounts, write_capable=False)
    dfy_create = dfy_sub.add_parser("create-order", help="Create DFY order (JSON file)")
    dfy_create.add_argument("--file", required=True, help="Create-order JSON file")
    dfy_create.set_defaults(func=dfy_cmd.cmd_dfy_create_order, write_capable=True)
    dfy_cancel = dfy_sub.add_parser(
        "cancel-accounts",
        help="Cancel DFY accounts (apply requires --yes --plan-in)",
    )
    dfy_cancel.add_argument("--file", required=False, help="Cancel-accounts JSON file (required unless --plan-in)")
    dfy_cancel.set_defaults(func=dfy_cmd.cmd_dfy_cancel_accounts, write_capable=True)
    dfy_check = dfy_sub.add_parser("check-domains", help="Check domains (JSON file)")
    dfy_check.add_argument("--file", required=True, help="Check-domains JSON file")
    dfy_check.set_defaults(func=dfy_cmd.cmd_dfy_check_domains, write_capable=True)
    dfy_similar = dfy_sub.add_parser("similar-domains", help="Get similar domains (JSON file)")
    dfy_similar.add_argument("--file", required=True, help="Similar-domains JSON file")
    dfy_similar.set_defaults(func=dfy_cmd.cmd_dfy_similar_domains, write_capable=True)
    dfy_prewarmed = dfy_sub.add_parser("prewarmed-domains", help="List prewarmed domains")
    dfy_prewarmed.set_defaults(func=dfy_cmd.cmd_dfy_prewarmed_domains, write_capable=False)

    crm = sub.add_parser("crm-actions", help="CRM actions")
    crm_sub = crm.add_subparsers(dest="crm_cmd", required=True, parser_class=_ToolArgumentParser)
    crm_list = crm_sub.add_parser("list-phone-numbers", help="List CRM phone numbers")
    crm_list.set_defaults(func=crm_actions_cmd.cmd_crm_actions_list_phone_numbers, write_capable=False)
    crm_del = crm_sub.add_parser("delete-phone-number", help="Delete a CRM phone number (requires --apply --yes --plan-in)")
    crm_del.add_argument("--id", required=False, help="Phone number id (required unless --plan-in)")
    crm_del.set_defaults(func=crm_actions_cmd.cmd_crm_actions_delete_phone_number, write_capable=True)

    campaigns = sub.add_parser("campaigns", help="Campaigns")
    campaigns_sub = campaigns.add_subparsers(dest="campaigns_cmd", required=True, parser_class=_ToolArgumentParser)
    campaigns_list = campaigns_sub.add_parser("list", help="List campaigns")
    campaigns_list.add_argument("--limit", type=int, default=None, help="Page size")
    campaigns_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    campaigns_list.set_defaults(func=campaigns_cmd.cmd_campaigns_list, write_capable=False)
    campaigns_get = campaigns_sub.add_parser("get", help="Get campaign by id")
    campaigns_get.add_argument("--campaign-id", required=True, help="Campaign id")
    campaigns_get.set_defaults(func=campaigns_cmd.cmd_campaigns_get, write_capable=False)
    campaigns_create = campaigns_sub.add_parser("create", help="Create campaign from JSON file")
    campaigns_create.add_argument("--file", required=True, help="Campaign create JSON file")
    campaigns_create.set_defaults(func=campaigns_cmd.cmd_campaigns_create, write_capable=True)
    campaigns_activate = campaigns_sub.add_parser("activate", help="Activate a campaign")
    campaigns_activate.add_argument("--campaign-id", required=True, help="Campaign id")
    campaigns_activate.set_defaults(func=campaigns_cmd.cmd_campaigns_activate, write_capable=True)
    campaigns_pause = campaigns_sub.add_parser("pause", help="Pause a campaign")
    campaigns_pause.add_argument("--campaign-id", required=True, help="Campaign id")
    campaigns_pause.set_defaults(func=campaigns_cmd.cmd_campaigns_pause, write_capable=True)
    campaigns_patch = campaigns_sub.add_parser("patch", help="Patch campaign (JSON file)")
    campaigns_patch.add_argument("--campaign-id", required=True, help="Campaign id")
    campaigns_patch.add_argument("--file", required=True, help="Campaign patch JSON file")
    campaigns_patch.set_defaults(func=campaigns_cmd.cmd_campaigns_patch, write_capable=True)
    campaigns_delete = campaigns_sub.add_parser(
        "delete",
        help="Delete campaign (requires plan-file workflow; --apply --yes --plan-in)",
    )
    campaigns_delete.add_argument("--campaign-id", required=False, help="Campaign id (required unless --plan-in)")
    campaigns_delete.set_defaults(func=campaigns_cmd.cmd_campaigns_delete, write_capable=True)
    campaigns_sending = campaigns_sub.add_parser("sending-status", help="Get campaign sending status")
    campaigns_sending.add_argument("--campaign-id", required=True, help="Campaign id")
    campaigns_sending.add_argument(
        "--with-ai-summary", action="store_true", help="Include AI summary (optional; can be a larger payload)"
    )
    campaigns_sending.set_defaults(func=campaigns_cmd.cmd_campaigns_sending_status, write_capable=False)
    campaigns_search = campaigns_sub.add_parser("search-by-contact", help="Search campaigns by lead email")
    campaigns_search.add_argument("--email", required=True, help="Lead email to search")
    campaigns_search.add_argument("--sort-column", default=None, help="Optional sort column")
    campaigns_search.add_argument("--sort-order", default=None, help="Optional sort order")
    campaigns_search.set_defaults(func=campaigns_cmd.cmd_campaigns_search_by_contact, write_capable=False)
    campaigns_share = campaigns_sub.add_parser("share", help="Share campaign (apply requires --yes)")
    campaigns_share.add_argument("--campaign-id", required=True, help="Campaign id")
    campaigns_share.set_defaults(func=campaigns_cmd.cmd_campaigns_share, write_capable=True)
    campaigns_from_export = campaigns_sub.add_parser(
        "create-from-export", help="Create a new campaign from an export (apply requires --yes)"
    )
    campaigns_from_export.add_argument("--campaign-id", required=True, help="Campaign id")
    campaigns_from_export.set_defaults(func=campaigns_cmd.cmd_campaigns_create_from_export, write_capable=True)
    campaigns_export = campaigns_sub.add_parser("export", help="Export campaign (returns export payload)")
    campaigns_export.add_argument("--campaign-id", required=True, help="Campaign id")
    campaigns_export.set_defaults(func=campaigns_cmd.cmd_campaigns_export, write_capable=True)
    campaigns_duplicate = campaigns_sub.add_parser("duplicate", help="Duplicate campaign (JSON file; apply requires --yes)")
    campaigns_duplicate.add_argument("--campaign-id", required=True, help="Campaign id")
    campaigns_duplicate.add_argument("--file", required=True, help="Duplicate JSON file")
    campaigns_duplicate.set_defaults(func=campaigns_cmd.cmd_campaigns_duplicate, write_capable=True)
    campaigns_count_launched = campaigns_sub.add_parser("count-launched", help="Count launched campaigns")
    campaigns_count_launched.set_defaults(func=campaigns_cmd.cmd_campaigns_count_launched, write_capable=False)
    campaigns_vars = campaigns_sub.add_parser("add-variables", help="Add variables to campaign (JSON file)")
    campaigns_vars.add_argument("--campaign-id", required=True, help="Campaign id")
    campaigns_vars.add_argument("--file", required=True, help="Variables JSON file")
    campaigns_vars.set_defaults(func=campaigns_cmd.cmd_campaigns_add_variables, write_capable=True)

    accounts = sub.add_parser("accounts", help="Email accounts")
    accounts_sub = accounts.add_subparsers(dest="accounts_cmd", required=True, parser_class=_ToolArgumentParser)
    accounts_list = accounts_sub.add_parser("list", help="List accounts")
    accounts_list.add_argument("--limit", type=int, default=None, help="Page size")
    accounts_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    accounts_list.set_defaults(func=accounts_cmd.cmd_accounts_list, write_capable=True)
    accounts_get = accounts_sub.add_parser("get", help="Get account by email")
    accounts_get.add_argument("--email", required=True, help="Account email address")
    accounts_get.set_defaults(func=accounts_cmd.cmd_accounts_get, write_capable=True)
    accounts_create = accounts_sub.add_parser("create", help="Create an account from JSON file")
    accounts_create.add_argument("--file", required=True, help="Account create JSON file")
    accounts_create.set_defaults(func=accounts_cmd.cmd_accounts_create, write_capable=True)
    accounts_patch = accounts_sub.add_parser("patch", help="Patch an account from JSON file")
    accounts_patch.add_argument("--email", required=True, help="Account email address")
    accounts_patch.add_argument("--file", required=True, help="Account patch JSON file")
    accounts_patch.set_defaults(func=accounts_cmd.cmd_accounts_patch, write_capable=True)
    accounts_delete = accounts_sub.add_parser(
        "delete",
        help="Delete an account (requires plan-file workflow; --apply --yes --plan-in)",
    )
    accounts_delete.add_argument("--email", required=False, help="Account email address (required unless --plan-in)")
    accounts_delete.set_defaults(func=accounts_cmd.cmd_accounts_delete, write_capable=True)
    accounts_warmup_enable = accounts_sub.add_parser("warmup-enable", help="Enable warmup for accounts (batch)")
    accounts_warmup_enable.add_argument("--file", required=True, help="Warmup enable JSON file")
    accounts_warmup_enable.set_defaults(func=accounts_cmd.cmd_accounts_warmup_enable, write_capable=True)
    accounts_warmup_disable = accounts_sub.add_parser("warmup-disable", help="Disable warmup for accounts (batch)")
    accounts_warmup_disable.add_argument("--file", required=True, help="Warmup disable JSON file")
    accounts_warmup_disable.set_defaults(func=accounts_cmd.cmd_accounts_warmup_disable, write_capable=True)
    accounts_pause = accounts_sub.add_parser("pause", help="Pause an account")
    accounts_pause.add_argument("--email", required=True, help="Account email address")
    accounts_pause.set_defaults(func=accounts_cmd.cmd_accounts_pause, write_capable=True)
    accounts_resume = accounts_sub.add_parser("resume", help="Resume an account")
    accounts_resume.add_argument("--email", required=True, help="Account email address")
    accounts_resume.set_defaults(func=accounts_cmd.cmd_accounts_resume, write_capable=True)
    accounts_mark_fixed = accounts_sub.add_parser("mark-fixed", help="Mark an account as fixed")
    accounts_mark_fixed.add_argument("--email", required=True, help="Account email address")
    accounts_mark_fixed.set_defaults(func=accounts_cmd.cmd_accounts_mark_fixed, write_capable=True)
    accounts_move = accounts_sub.add_parser("move", help="Move accounts (batch; apply requires --yes)")
    accounts_move.add_argument("--file", required=True, help="Move accounts JSON file")
    accounts_move.set_defaults(func=accounts_cmd.cmd_accounts_move, write_capable=True)
    accounts_test_vitals = accounts_sub.add_parser("test-vitals", help="Test account vitals (v2 API)")
    accounts_test_vitals.add_argument("--file", required=True, help="Vitals test JSON file")
    accounts_test_vitals.set_defaults(func=accounts_cmd.cmd_accounts_test_vitals, write_capable=True)
    accounts_ctd_status = accounts_sub.add_parser("ctd-status", help="Get CTD status")
    accounts_ctd_status.set_defaults(func=accounts_cmd.cmd_accounts_ctd_status, write_capable=True)

    leads = sub.add_parser("leads", help="Leads")
    leads_sub = leads.add_subparsers(dest="leads_cmd", required=True, parser_class=_ToolArgumentParser)
    leads_list = leads_sub.add_parser("list", help="List leads")
    leads_list.add_argument("--campaign-id", default=None, help="Optional campaign id filter")
    leads_list.add_argument("--limit", type=int, default=None, help="Page size")
    leads_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    leads_list.set_defaults(func=leads_cmd.cmd_leads_list, write_capable=False)
    leads_get = leads_sub.add_parser("get", help="Get lead by id")
    leads_get.add_argument("--lead-id", required=True, help="Lead id")
    leads_get.set_defaults(func=leads_cmd.cmd_leads_get, write_capable=False)
    leads_create = leads_sub.add_parser("create", help="Create a lead (JSON file)")
    leads_create.add_argument("--file", required=True, help="Lead create JSON file")
    leads_create.set_defaults(func=leads_cmd.cmd_leads_create, write_capable=True)
    leads_patch = leads_sub.add_parser("patch", help="Patch a lead (JSON file)")
    leads_patch.add_argument("--lead-id", required=True, help="Lead id")
    leads_patch.add_argument("--file", required=True, help="Lead patch JSON file")
    leads_patch.set_defaults(func=leads_cmd.cmd_leads_patch, write_capable=True)
    leads_delete = leads_sub.add_parser(
        "delete",
        help="Delete a lead (requires plan-file workflow; --apply --yes --plan-in)",
    )
    leads_delete.add_argument("--lead-id", required=False, help="Lead id (required unless --plan-in)")
    leads_delete.add_argument("--file", required=False, help="Optional delete body JSON file (rare; required by some accounts)")
    leads_delete.set_defaults(func=leads_cmd.cmd_leads_delete, write_capable=True)
    leads_bulk_delete = leads_sub.add_parser(
        "bulk-delete",
        help="Bulk delete leads (requires plan-file workflow; --apply --yes --plan-in)",
    )
    leads_bulk_delete.add_argument("--file", required=False, help="Bulk delete JSON file (required unless --plan-in)")
    leads_bulk_delete.set_defaults(func=leads_cmd.cmd_leads_bulk_delete, write_capable=True)
    leads_merge = leads_sub.add_parser(
        "merge",
        help="Merge leads (requires plan-file workflow; --apply --yes --plan-in)",
    )
    leads_merge.add_argument("--file", required=False, help="Merge JSON file (required unless --plan-in)")
    leads_merge.set_defaults(func=leads_cmd.cmd_leads_merge, write_capable=True)
    leads_interest = leads_sub.add_parser("update-interest-status", help="Update lead interest status (JSON file; apply requires --yes)")
    leads_interest.add_argument("--file", required=True, help="Update interest status JSON file")
    leads_interest.set_defaults(func=leads_cmd.cmd_leads_update_interest_status, write_capable=True)
    leads_remove_subseq = leads_sub.add_parser(
        "remove-from-subsequence", help="Remove leads from subsequence (JSON file; apply requires --yes)"
    )
    leads_remove_subseq.add_argument("--file", required=True, help="Remove-from-subsequence JSON file")
    leads_remove_subseq.set_defaults(func=leads_cmd.cmd_leads_remove_from_subsequence, write_capable=True)
    leads_bulk_assign = leads_sub.add_parser("bulk-assign", help="Bulk assign leads (JSON file; apply requires --yes)")
    leads_bulk_assign.add_argument("--file", required=True, help="Bulk assign JSON file")
    leads_bulk_assign.set_defaults(func=leads_cmd.cmd_leads_bulk_assign, write_capable=True)
    leads_move = leads_sub.add_parser("move", help="Move leads (JSON file; apply requires --yes)")
    leads_move.add_argument("--file", required=True, help="Move leads JSON file")
    leads_move.set_defaults(func=leads_cmd.cmd_leads_move, write_capable=True)
    leads_move_subseq = leads_sub.add_parser("move-to-subsequence", help="Move leads to subsequence (JSON file; apply requires --yes)")
    leads_move_subseq.add_argument("--file", required=True, help="Move-to-subsequence JSON file")
    leads_move_subseq.set_defaults(func=leads_cmd.cmd_leads_move_to_subsequence, write_capable=True)
    leads_add_bulk = leads_sub.add_parser("add-bulk", help="Add leads in bulk (CSV or JSON)")
    leads_add_bulk.add_argument("--campaign-id", required=True, help="Campaign id")
    leads_add_bulk.add_argument("--csv", default=None, help="CSV input path (must include email column)")
    leads_add_bulk.add_argument("--json", default=None, help="JSON input path (list of objects with email)")
    leads_add_bulk.add_argument("--chunk-size", type=int, default=1000, help="Chunk size (<= 1000; default: 1000)")
    leads_add_bulk.set_defaults(func=leads_cmd.cmd_leads_add_bulk, write_capable=True)

    supersearch_enrichment = sub.add_parser("supersearch-enrichment", help="Supersearch enrichment (advanced)")
    supersearch_enrichment_sub = supersearch_enrichment.add_subparsers(
        dest="supersearch_enrichment_cmd", required=True, parser_class=_ToolArgumentParser
    )
    ss_create = supersearch_enrichment_sub.add_parser("create", help="Create enrichment (JSON file; apply requires --yes)")
    ss_create.add_argument("--file", required=True, help="Create enrichment JSON file")
    ss_create.set_defaults(func=supersearch_enrichment_cmd.cmd_supersearch_enrichment_create, write_capable=True)
    ss_get = supersearch_enrichment_sub.add_parser("get", help="Get enrichment by resource id")
    ss_get.add_argument("--resource-id", required=True, help="Resource id")
    ss_get.set_defaults(func=supersearch_enrichment_cmd.cmd_supersearch_enrichment_get, write_capable=False)
    ss_patch_settings = supersearch_enrichment_sub.add_parser(
        "patch-settings", help="Patch enrichment settings (JSON file; apply requires --yes)"
    )
    ss_patch_settings.add_argument("--resource-id", required=True, help="Resource id")
    ss_patch_settings.add_argument("--file", required=True, help="Patch settings JSON file")
    ss_patch_settings.set_defaults(func=supersearch_enrichment_cmd.cmd_supersearch_enrichment_patch_settings, write_capable=True)
    ss_history = supersearch_enrichment_sub.add_parser("history", help="Get enrichment history by resource id")
    ss_history.add_argument("--resource-id", required=True, help="Resource id")
    ss_history.set_defaults(func=supersearch_enrichment_cmd.cmd_supersearch_enrichment_history, write_capable=False)
    ss_run = supersearch_enrichment_sub.add_parser("run", help="Run enrichment (JSON file; apply requires --yes)")
    ss_run.add_argument("--file", required=True, help="Run enrichment JSON file")
    ss_run.set_defaults(func=supersearch_enrichment_cmd.cmd_supersearch_enrichment_run, write_capable=True)
    ss_enrich_leads = supersearch_enrichment_sub.add_parser(
        "enrich-leads", help="Enrich leads from supersearch (JSON file; apply requires --yes)"
    )
    ss_enrich_leads.add_argument("--file", required=True, help="Enrich leads JSON file")
    ss_enrich_leads.set_defaults(func=supersearch_enrichment_cmd.cmd_supersearch_enrichment_enrich_leads, write_capable=True)
    ss_ai = supersearch_enrichment_sub.add_parser("ai", help="Create AI enrichment (JSON file; apply requires --yes)")
    ss_ai.add_argument("--file", required=True, help="AI enrichment JSON file")
    ss_ai.set_defaults(func=supersearch_enrichment_cmd.cmd_supersearch_enrichment_ai, write_capable=True)
    ss_count = supersearch_enrichment_sub.add_parser("count-leads", help="Count leads from supersearch (JSON file)")
    ss_count.add_argument("--file", required=True, help="Count leads JSON file")
    ss_count.set_defaults(func=supersearch_enrichment_cmd.cmd_supersearch_enrichment_count_leads, write_capable=False)
    ss_preview = supersearch_enrichment_sub.add_parser("preview-leads", help="Preview leads from supersearch (JSON file)")
    ss_preview.add_argument("--file", required=True, help="Preview leads JSON file")
    ss_preview.set_defaults(func=supersearch_enrichment_cmd.cmd_supersearch_enrichment_preview_leads, write_capable=False)

    analytics = sub.add_parser("analytics", help="Analytics (read-only reporting)")
    analytics_sub = analytics.add_subparsers(dest="analytics_cmd", required=True, parser_class=_ToolArgumentParser)
    analytics_warmup = analytics_sub.add_parser("warmup", help="Warmup analytics (POST /accounts/warmup-analytics)")
    analytics_warmup.add_argument("--emails", required=True, help="Comma-separated email account list")
    analytics_warmup.set_defaults(func=analytics_cmd.cmd_analytics_warmup, write_capable=False)
    analytics_accounts_daily = analytics_sub.add_parser(
        "accounts-daily", help="Daily account analytics (GET /accounts/analytics/daily)"
    )
    analytics_accounts_daily.add_argument("--emails", required=True, help="Comma-separated email account list")
    analytics_accounts_daily.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    analytics_accounts_daily.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    analytics_accounts_daily.set_defaults(func=analytics_cmd.cmd_analytics_accounts_daily, write_capable=False)
    analytics_account_vitals = analytics_sub.add_parser(
        "account-vitals", help="Account vitals diagnostic (POST /accounts/test/vitals)"
    )
    analytics_account_vitals.add_argument("--emails", required=True, help="Comma-separated email account list")
    analytics_account_vitals.set_defaults(func=analytics_cmd.cmd_analytics_account_vitals, write_capable=False)
    analytics_campaigns = analytics_sub.add_parser("campaigns", help="Campaign analytics (GET /campaigns/analytics)")
    analytics_campaigns.add_argument(
        "--campaign-id",
        action="append",
        default=None,
        help="Optional campaign id filter (repeatable; maps to id/ids query params)",
    )
    analytics_campaigns.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    analytics_campaigns.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    analytics_campaigns.add_argument(
        "--exclude-total-leads-count",
        action="store_true",
        help="Exclude total leads count (safety: reduces payload size)",
    )
    analytics_campaigns.set_defaults(func=analytics_cmd.cmd_analytics_campaigns, write_capable=False)
    analytics_campaigns_overview = analytics_sub.add_parser(
        "campaigns-overview", help="Campaign analytics overview (GET /campaigns/analytics/overview)"
    )
    analytics_campaigns_overview.add_argument(
        "--campaign-id",
        action="append",
        default=None,
        help="Optional campaign id filter (repeatable; maps to id/ids query params)",
    )
    analytics_campaigns_overview.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    analytics_campaigns_overview.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    analytics_campaigns_overview.add_argument("--campaign-status", type=int, default=None, help="Optional status filter")
    analytics_campaigns_overview.add_argument(
        "--expand-crm-events", action="store_true", help="Expand CRM events (may increase payload)"
    )
    analytics_campaigns_overview.set_defaults(func=analytics_cmd.cmd_analytics_campaigns_overview, write_capable=False)
    analytics_campaigns_daily = analytics_sub.add_parser(
        "campaigns-daily", help="Daily campaign analytics (GET /campaigns/analytics/daily)"
    )
    analytics_campaigns_daily.add_argument("--campaign-id", required=True, help="Campaign id")
    analytics_campaigns_daily.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    analytics_campaigns_daily.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    analytics_campaigns_daily.add_argument("--campaign-status", type=int, default=None, help="Optional status filter")
    analytics_campaigns_daily.set_defaults(func=analytics_cmd.cmd_analytics_campaigns_daily, write_capable=False)
    analytics_campaign_steps = analytics_sub.add_parser(
        "campaign-steps", help="Campaign steps analytics (GET /campaigns/analytics/steps)"
    )
    analytics_campaign_steps.add_argument("--campaign-id", required=True, help="Campaign id")
    analytics_campaign_steps.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    analytics_campaign_steps.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    analytics_campaign_steps.add_argument(
        "--include-opportunities-count", action="store_true", help="Include opportunities count"
    )
    analytics_campaign_steps.set_defaults(func=analytics_cmd.cmd_analytics_campaign_steps, write_capable=False)

    inbox = sub.add_parser("inbox-placement", help="Inbox placement tests + analytics + reports")
    inbox_sub = inbox.add_subparsers(dest="inbox_cmd", required=True, parser_class=_ToolArgumentParser)

    inbox_tests = inbox_sub.add_parser("tests", help="Inbox placement tests (write-like; may send emails)")
    inbox_tests_sub = inbox_tests.add_subparsers(dest="inbox_tests_cmd", required=True, parser_class=_ToolArgumentParser)
    inbox_tests_list = inbox_tests_sub.add_parser("list", help="List inbox placement tests")
    inbox_tests_list.add_argument("--limit", type=int, default=20, help="Page size (default: 20; max: 50)")
    inbox_tests_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    inbox_tests_list.add_argument("--search", default=None, help="Optional search string")
    inbox_tests_list.add_argument("--status", type=int, default=None, help="Optional status filter")
    inbox_tests_list.add_argument("--sort-order", default=None, help="Optional sort order (e.g. asc/desc)")
    inbox_tests_list.set_defaults(func=inbox_placement_cmd.cmd_inbox_placement_tests_list, write_capable=False)
    inbox_tests_get = inbox_tests_sub.add_parser("get", help="Get inbox placement test by id")
    inbox_tests_get.add_argument("--test-id", required=True, help="Test id")
    inbox_tests_get.set_defaults(func=inbox_placement_cmd.cmd_inbox_placement_tests_get, write_capable=False)
    inbox_tests_esp = inbox_tests_sub.add_parser("esp-options", help="List ESP options")
    inbox_tests_esp.set_defaults(func=inbox_placement_cmd.cmd_inbox_placement_tests_esp_options, write_capable=False)
    inbox_tests_create = inbox_tests_sub.add_parser(
        "create", help="Create inbox placement test (requires --apply --yes --ack-irreversible on apply)"
    )
    inbox_tests_create.add_argument("--file", required=True, help="Create JSON file")
    inbox_tests_create.set_defaults(func=inbox_placement_cmd.cmd_inbox_placement_tests_create, write_capable=True)
    inbox_tests_patch = inbox_tests_sub.add_parser(
        "patch", help="Patch inbox placement test (requires --apply --yes on apply)"
    )
    inbox_tests_patch.add_argument("--test-id", required=True, help="Test id")
    inbox_tests_patch.add_argument("--file", required=True, help="Patch JSON file")
    inbox_tests_patch.set_defaults(func=inbox_placement_cmd.cmd_inbox_placement_tests_patch, write_capable=True)
    inbox_tests_delete = inbox_tests_sub.add_parser(
        "delete", help="Delete inbox placement test (requires --apply --yes on apply)"
    )
    inbox_tests_delete.add_argument("--test-id", required=True, help="Test id")
    inbox_tests_delete.set_defaults(func=inbox_placement_cmd.cmd_inbox_placement_tests_delete, write_capable=True)

    inbox_analytics = inbox_sub.add_parser("analytics", help="Inbox placement analytics")
    inbox_analytics_sub = inbox_analytics.add_subparsers(
        dest="inbox_analytics_cmd", required=True, parser_class=_ToolArgumentParser
    )
    inbox_analytics_list = inbox_analytics_sub.add_parser("list", help="List inbox placement analytics (requires --test-id)")
    inbox_analytics_list.add_argument("--test-id", required=True, help="Test id")
    inbox_analytics_list.add_argument("--limit", type=int, default=20, help="Page size (default: 20; max: 50)")
    inbox_analytics_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    inbox_analytics_list.add_argument("--date-from", default=None, help="Optional date_from (provider format; see docs)")
    inbox_analytics_list.add_argument("--date-to", default=None, help="Optional date_to (provider format; see docs)")
    inbox_analytics_list.add_argument("--sender-email", default=None, help="Optional sender email filter")
    inbox_analytics_list.add_argument("--recipient-esp", default=None, help="Optional recipient_esp comma-separated ints")
    inbox_analytics_list.add_argument("--recipient-geo", default=None, help="Optional recipient_geo comma-separated ints")
    inbox_analytics_list.add_argument("--recipient-type", default=None, help="Optional recipient_type comma-separated ints")
    inbox_analytics_list.set_defaults(func=inbox_placement_cmd.cmd_inbox_placement_analytics_list, write_capable=False)
    inbox_analytics_get = inbox_analytics_sub.add_parser("get", help="Get one inbox placement analytics entry by id")
    inbox_analytics_get.add_argument("--analytics-id", required=True, help="Analytics id")
    inbox_analytics_get.set_defaults(func=inbox_placement_cmd.cmd_inbox_placement_analytics_get, write_capable=False)
    inbox_stats_test = inbox_analytics_sub.add_parser("stats-by-test-id", help="Stats by test id (POST)")
    inbox_stats_test.add_argument("--test-id", required=True, help="Test id")
    inbox_stats_test.set_defaults(func=inbox_placement_cmd.cmd_inbox_placement_analytics_stats_by_test_id, write_capable=False)
    inbox_deliverability = inbox_analytics_sub.add_parser("deliverability-insights", help="Deliverability insights (POST)")
    inbox_deliverability.add_argument("--test-id", required=True, help="Test id")
    inbox_deliverability.set_defaults(
        func=inbox_placement_cmd.cmd_inbox_placement_analytics_deliverability_insights, write_capable=False
    )
    inbox_stats_date = inbox_analytics_sub.add_parser("stats-by-date", help="Stats by date (POST)")
    inbox_stats_date.add_argument("--test-id", required=True, help="Test id")
    inbox_stats_date.set_defaults(func=inbox_placement_cmd.cmd_inbox_placement_analytics_stats_by_date, write_capable=False)

    inbox_reports = inbox_sub.add_parser("reports", help="Inbox placement reports (blacklist/spamassassin)")
    inbox_reports_sub = inbox_reports.add_subparsers(dest="inbox_reports_cmd", required=True, parser_class=_ToolArgumentParser)
    inbox_reports_list = inbox_reports_sub.add_parser("list", help="List reports (requires --test-id)")
    inbox_reports_list.add_argument("--test-id", required=True, help="Test id")
    inbox_reports_list.add_argument("--limit", type=int, default=20, help="Page size (default: 20; max: 50)")
    inbox_reports_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    inbox_reports_list.add_argument("--date-from", default=None, help="Optional date_from (provider format; see docs)")
    inbox_reports_list.add_argument("--date-to", default=None, help="Optional date_to (provider format; see docs)")
    inbox_reports_list.add_argument("--skip-blacklist-report", action="store_true", help="Skip blacklist report content")
    inbox_reports_list.add_argument("--skip-spam-assassin-report", action="store_true", help="Skip spam assassin report content")
    inbox_reports_list.set_defaults(func=inbox_placement_cmd.cmd_inbox_placement_reports_list, write_capable=False)
    inbox_reports_get = inbox_reports_sub.add_parser("get", help="Get a report by id")
    inbox_reports_get.add_argument("--report-id", required=True, help="Report id")
    inbox_reports_get.set_defaults(func=inbox_placement_cmd.cmd_inbox_placement_reports_get, write_capable=False)

    email_verification = sub.add_parser("email-verification", help="Email verification (create is apply-gated)")
    email_verification_sub = email_verification.add_subparsers(
        dest="email_verification_cmd", required=True, parser_class=_ToolArgumentParser
    )
    email_verification_status = email_verification_sub.add_parser("status", help="Check verification status for an email")
    email_verification_status.add_argument("--email", required=True, help="Email address")
    email_verification_status.set_defaults(func=email_verification_cmd.cmd_email_verification_status, write_capable=False)
    email_verification_create = email_verification_sub.add_parser(
        "create", help="Trigger email verification (requires --apply --yes on apply)"
    )
    email_verification_create.add_argument("--email", required=True, help="Email address")
    email_verification_create.set_defaults(func=email_verification_cmd.cmd_email_verification_create, write_capable=True)

    audit_log = sub.add_parser("audit-log", help="Audit log (read-only; items hidden by default)")
    audit_log_sub = audit_log.add_subparsers(dest="audit_log_cmd", required=True, parser_class=_ToolArgumentParser)
    audit_log_list = audit_log_sub.add_parser("list", help="List audit log events")
    audit_log_list.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    audit_log_list.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    audit_log_list.add_argument("--limit", type=int, default=20, help="Page size (default: 20; max: 50)")
    audit_log_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    audit_log_list.add_argument("--search", default=None, help="Optional search query")
    audit_log_list.add_argument("--activity-type", type=int, default=None, help="Optional activity type filter")
    audit_log_list.add_argument("--include-items", action="store_true", help="Include raw event objects (requires --out)")
    audit_log_list.add_argument("--out", default=None, help="Output file path for raw items (required with --include-items)")
    audit_log_list.set_defaults(func=audit_log_cmd.cmd_audit_log_list, write_capable=False)

    lead_lists = sub.add_parser("lead-lists", help="Lead lists")
    lead_lists_sub = lead_lists.add_subparsers(dest="lead_lists_cmd", required=True, parser_class=_ToolArgumentParser)
    lead_lists_list = lead_lists_sub.add_parser("list", help="List lead lists")
    lead_lists_list.add_argument("--limit", type=int, default=None, help="Page size")
    lead_lists_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    lead_lists_list.set_defaults(func=lead_lists_cmd.cmd_lead_lists_list, write_capable=False)
    lead_lists_get = lead_lists_sub.add_parser("get", help="Get lead list by id")
    lead_lists_get.add_argument("--lead-list-id", required=True, help="Lead list id")
    lead_lists_get.set_defaults(func=lead_lists_cmd.cmd_lead_lists_get, write_capable=False)
    lead_lists_verification_stats = lead_lists_sub.add_parser("verification-stats", help="Get lead list verification stats")
    lead_lists_verification_stats.add_argument("--lead-list-id", required=True, help="Lead list id")
    lead_lists_verification_stats.set_defaults(func=lead_lists_cmd.cmd_lead_lists_verification_stats, write_capable=False)
    lead_lists_create = lead_lists_sub.add_parser("create", help="Create lead list from JSON file")
    lead_lists_create.add_argument("--file", required=True, help="Lead list create JSON file")
    lead_lists_create.set_defaults(func=lead_lists_cmd.cmd_lead_lists_create, write_capable=True)
    lead_lists_patch = lead_lists_sub.add_parser("patch", help="Patch lead list from JSON file")
    lead_lists_patch.add_argument("--lead-list-id", required=True, help="Lead list id")
    lead_lists_patch.add_argument("--file", required=True, help="Lead list patch JSON file")
    lead_lists_patch.set_defaults(func=lead_lists_cmd.cmd_lead_lists_patch, write_capable=True)
    lead_lists_delete = lead_lists_sub.add_parser(
        "delete",
        help="Delete a lead list (requires plan-file workflow; --apply --yes --plan-in)",
    )
    lead_lists_delete.add_argument("--lead-list-id", required=False, help="Lead list id (required unless --plan-in)")
    lead_lists_delete.set_defaults(func=lead_lists_cmd.cmd_lead_lists_delete, write_capable=True)

    lead_labels = sub.add_parser("lead-labels", help="Lead labels")
    lead_labels_sub = lead_labels.add_subparsers(dest="lead_labels_cmd", required=True, parser_class=_ToolArgumentParser)
    lead_labels_list = lead_labels_sub.add_parser("list", help="List lead labels")
    lead_labels_list.add_argument("--limit", type=int, default=None, help="Page size")
    lead_labels_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    lead_labels_list.set_defaults(func=lead_labels_cmd.cmd_lead_labels_list, write_capable=False)
    lead_labels_get = lead_labels_sub.add_parser("get", help="Get lead label by id")
    lead_labels_get.add_argument("--lead-label-id", required=True, help="Lead label id")
    lead_labels_get.set_defaults(func=lead_labels_cmd.cmd_lead_labels_get, write_capable=False)
    lead_labels_create = lead_labels_sub.add_parser("create", help="Create lead label from JSON file")
    lead_labels_create.add_argument("--file", required=True, help="Lead label create JSON file")
    lead_labels_create.set_defaults(func=lead_labels_cmd.cmd_lead_labels_create, write_capable=True)
    lead_labels_patch = lead_labels_sub.add_parser("patch", help="Patch lead label from JSON file")
    lead_labels_patch.add_argument("--lead-label-id", required=True, help="Lead label id")
    lead_labels_patch.add_argument("--file", required=True, help="Lead label patch JSON file")
    lead_labels_patch.set_defaults(func=lead_labels_cmd.cmd_lead_labels_patch, write_capable=True)
    lead_labels_delete = lead_labels_sub.add_parser(
        "delete",
        help="Delete a lead label (requires plan-file workflow; --apply --yes --plan-in)",
    )
    lead_labels_delete.add_argument("--lead-label-id", required=False, help="Lead label id (required unless --plan-in)")
    lead_labels_delete.set_defaults(func=lead_labels_cmd.cmd_lead_labels_delete, write_capable=True)

    custom_tags = sub.add_parser("custom-tags", help="Custom tags")
    custom_tags_sub = custom_tags.add_subparsers(dest="custom_tags_cmd", required=True, parser_class=_ToolArgumentParser)
    custom_tags_list = custom_tags_sub.add_parser("list", help="List custom tags")
    custom_tags_list.add_argument("--limit", type=int, default=None, help="Page size")
    custom_tags_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    custom_tags_list.set_defaults(func=custom_tags_cmd.cmd_custom_tags_list, write_capable=False)
    custom_tags_get = custom_tags_sub.add_parser("get", help="Get custom tag by id")
    custom_tags_get.add_argument("--tag-id", required=True, help="Custom tag id")
    custom_tags_get.set_defaults(func=custom_tags_cmd.cmd_custom_tags_get, write_capable=False)
    custom_tags_create = custom_tags_sub.add_parser("create", help="Create custom tag from JSON file")
    custom_tags_create.add_argument("--file", required=True, help="Custom tag create JSON file")
    custom_tags_create.set_defaults(func=custom_tags_cmd.cmd_custom_tags_create, write_capable=True)
    custom_tags_patch = custom_tags_sub.add_parser("patch", help="Patch custom tag from JSON file")
    custom_tags_patch.add_argument("--tag-id", required=True, help="Custom tag id")
    custom_tags_patch.add_argument("--file", required=True, help="Custom tag patch JSON file")
    custom_tags_patch.set_defaults(func=custom_tags_cmd.cmd_custom_tags_patch, write_capable=True)
    custom_tags_delete = custom_tags_sub.add_parser(
        "delete",
        help="Delete a custom tag (requires plan-file workflow; --apply --yes --plan-in)",
    )
    custom_tags_delete.add_argument("--tag-id", required=False, help="Custom tag id (required unless --plan-in)")
    custom_tags_delete.set_defaults(func=custom_tags_cmd.cmd_custom_tags_delete, write_capable=True)
    custom_tags_toggle = custom_tags_sub.add_parser(
        "toggle-resource",
        help="Toggle a custom tag mapping for a resource (high-risk; requires --apply --yes)",
    )
    custom_tags_toggle.add_argument("--file", required=True, help="Toggle-resource JSON file")
    custom_tags_toggle.set_defaults(func=custom_tags_cmd.cmd_custom_tags_toggle_resource, write_capable=True)

    custom_tag_mappings = sub.add_parser("custom-tag-mappings", help="Custom tag mappings")
    ctm_sub = custom_tag_mappings.add_subparsers(dest="custom_tag_mappings_cmd", required=True, parser_class=_ToolArgumentParser)
    ctm_list = ctm_sub.add_parser("list", help="List custom tag mappings")
    ctm_list.add_argument("--limit", type=int, default=None, help="Page size")
    ctm_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    ctm_list.set_defaults(func=custom_tag_mappings_cmd.cmd_custom_tag_mappings_list, write_capable=False)

    account_campaign_mappings = sub.add_parser("account-campaign-mappings", help="Account↔campaign mappings")
    acm_sub = account_campaign_mappings.add_subparsers(
        dest="account_campaign_mappings_cmd", required=True, parser_class=_ToolArgumentParser
    )
    acm_get = acm_sub.add_parser("get", help="Get account campaign mapping by email")
    acm_get.add_argument("--email", required=True, help="Account email address")
    acm_get.set_defaults(func=account_campaign_mappings_cmd.cmd_account_campaign_mappings_get, write_capable=False)

    subsequences = sub.add_parser("subsequences", help="Campaign subsequences")
    subseq_sub = subsequences.add_subparsers(dest="subsequences_cmd", required=True, parser_class=_ToolArgumentParser)
    subseq_list = subseq_sub.add_parser("list", help="List subsequences")
    subseq_list.add_argument("--limit", type=int, default=None, help="Page size")
    subseq_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    subseq_list.set_defaults(func=subsequences_cmd.cmd_subsequences_list, write_capable=False)
    subseq_get = subseq_sub.add_parser("get", help="Get subsequence by id")
    subseq_get.add_argument("--subsequence-id", required=True, help="Subsequence id")
    subseq_get.set_defaults(func=subsequences_cmd.cmd_subsequences_get, write_capable=False)
    subseq_create = subseq_sub.add_parser("create", help="Create subsequence from JSON file")
    subseq_create.add_argument("--file", required=True, help="Subsequence create JSON file")
    subseq_create.set_defaults(func=subsequences_cmd.cmd_subsequences_create, write_capable=True)
    subseq_patch = subseq_sub.add_parser("patch", help="Patch subsequence from JSON file")
    subseq_patch.add_argument("--subsequence-id", required=True, help="Subsequence id")
    subseq_patch.add_argument("--file", required=True, help="Subsequence patch JSON file")
    subseq_patch.set_defaults(func=subsequences_cmd.cmd_subsequences_patch, write_capable=True)
    subseq_delete = subseq_sub.add_parser(
        "delete",
        help="Delete a subsequence (requires plan-file workflow; --apply --yes --plan-in)",
    )
    subseq_delete.add_argument("--subsequence-id", required=False, help="Subsequence id (required unless --plan-in)")
    subseq_delete.set_defaults(func=subsequences_cmd.cmd_subsequences_delete, write_capable=True)
    subseq_sending = subseq_sub.add_parser("sending-status", help="Get subsequence sending status")
    subseq_sending.add_argument("--subsequence-id", required=True, help="Subsequence id")
    subseq_sending.add_argument(
        "--with-ai-summary", action="store_true", help="Include AI summary (optional; can be a larger payload)"
    )
    subseq_sending.set_defaults(func=subsequences_cmd.cmd_subsequences_sending_status, write_capable=False)
    subseq_duplicate = subseq_sub.add_parser("duplicate", help="Duplicate subsequence (apply requires --yes)")
    subseq_duplicate.add_argument("--subsequence-id", required=True, help="Subsequence id")
    subseq_duplicate.set_defaults(func=subsequences_cmd.cmd_subsequences_duplicate, write_capable=True)
    subseq_pause = subseq_sub.add_parser("pause", help="Pause a subsequence")
    subseq_pause.add_argument("--subsequence-id", required=True, help="Subsequence id")
    subseq_pause.set_defaults(func=subsequences_cmd.cmd_subsequences_pause, write_capable=True)
    subseq_resume = subseq_sub.add_parser("resume", help="Resume a subsequence")
    subseq_resume.add_argument("--subsequence-id", required=True, help="Subsequence id")
    subseq_resume.set_defaults(func=subsequences_cmd.cmd_subsequences_resume, write_capable=True)

    webhooks = sub.add_parser("webhooks", help="Webhooks")
    webhooks_sub = webhooks.add_subparsers(dest="webhooks_cmd", required=True, parser_class=_ToolArgumentParser)
    webhooks_list = webhooks_sub.add_parser("list", help="List webhooks")
    webhooks_list.add_argument("--limit", type=int, default=None, help="Page size")
    webhooks_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    webhooks_list.set_defaults(func=webhooks_cmd.cmd_webhooks_list, write_capable=False)
    webhooks_get = webhooks_sub.add_parser("get", help="Get webhook by id")
    webhooks_get.add_argument("--webhook-id", required=True, help="Webhook id")
    webhooks_get.set_defaults(func=webhooks_cmd.cmd_webhooks_get, write_capable=False)
    webhooks_event_types = webhooks_sub.add_parser("event-types", help="List supported webhook event types")
    webhooks_event_types.set_defaults(func=webhooks_cmd.cmd_webhooks_event_types, write_capable=False)
    webhooks_create = webhooks_sub.add_parser("create", help="Create webhook (JSON file)")
    webhooks_create.add_argument("--file", required=True, help="Webhook create JSON file")
    webhooks_create.set_defaults(func=webhooks_cmd.cmd_webhooks_create, write_capable=True)
    webhooks_patch = webhooks_sub.add_parser("patch", help="Patch webhook (JSON file)")
    webhooks_patch.add_argument("--file", required=True, help="Webhook patch JSON file")
    webhooks_patch.add_argument("--webhook-id", required=True, help="Webhook id")
    webhooks_patch.set_defaults(func=webhooks_cmd.cmd_webhooks_patch, write_capable=True)
    webhooks_delete = webhooks_sub.add_parser("delete", help="Delete webhook (requires --apply; and --yes on apply)")
    webhooks_delete.add_argument("--webhook-id", required=False, help="Webhook id (required unless --plan-in)")
    webhooks_delete.set_defaults(func=webhooks_cmd.cmd_webhooks_delete, write_capable=True)
    webhooks_test = webhooks_sub.add_parser("test", help="Send a test webhook event")
    webhooks_test.add_argument("--webhook-id", required=True, help="Webhook id")
    webhooks_test.set_defaults(func=webhooks_cmd.cmd_webhooks_test, write_capable=True)
    webhooks_resume = webhooks_sub.add_parser("resume", help="Resume webhook delivery")
    webhooks_resume.add_argument("--webhook-id", required=True, help="Webhook id")
    webhooks_resume.set_defaults(func=webhooks_cmd.cmd_webhooks_resume, write_capable=True)

    webhook_events = sub.add_parser("webhook-events", help="Webhook events")
    webhook_events_sub = webhook_events.add_subparsers(dest="webhook_events_cmd", required=True, parser_class=_ToolArgumentParser)
    webhook_events_list = webhook_events_sub.add_parser("list", help="List webhook events")
    webhook_events_list.add_argument("--webhook-id", default=None, help="Optional webhook id filter")
    webhook_events_list.add_argument("--limit", type=int, default=20, help="Page size (default: 20; max: 50)")
    webhook_events_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    webhook_events_list.set_defaults(func=webhook_events_cmd.cmd_webhook_events_list, write_capable=False)
    webhook_events_get = webhook_events_sub.add_parser("get", help="Get webhook event by id")
    webhook_events_get.add_argument("--event-id", required=True, help="Event id")
    webhook_events_get.set_defaults(func=webhook_events_cmd.cmd_webhook_events_get, write_capable=False)
    webhook_events_summary = webhook_events_sub.add_parser("summary", help="Webhook events summary (requires date range)")
    webhook_events_summary.add_argument("--from", dest="from_date", required=True, help="From date (YYYY-MM-DD)")
    webhook_events_summary.add_argument("--to", dest="to_date", required=True, help="To date (YYYY-MM-DD)")
    webhook_events_summary.set_defaults(func=webhook_events_cmd.cmd_webhook_events_summary, write_capable=False)
    webhook_events_summary_by_date = webhook_events_sub.add_parser(
        "summary-by-date", help="Webhook events summary by date (requires date range)"
    )
    webhook_events_summary_by_date.add_argument("--from", dest="from_date", required=True, help="From date (YYYY-MM-DD)")
    webhook_events_summary_by_date.add_argument("--to", dest="to_date", required=True, help="To date (YYYY-MM-DD)")
    webhook_events_summary_by_date.set_defaults(func=webhook_events_cmd.cmd_webhook_events_summary_by_date, write_capable=False)

    emails = sub.add_parser("emails", help="Emails")
    emails_sub = emails.add_subparsers(dest="emails_cmd", required=True, parser_class=_ToolArgumentParser)
    emails_list = emails_sub.add_parser("list", help="List emails")
    emails_list.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Page size (default: 20; email endpoints are rate-limit-sensitive in Instantly)",
    )
    emails_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    emails_list.set_defaults(func=emails_cmd.cmd_emails_list, write_capable=False)
    emails_get = emails_sub.add_parser("get", help="Get email by id")
    emails_get.add_argument("--email-id", required=True, help="Email id")
    emails_get.set_defaults(func=emails_cmd.cmd_emails_get, write_capable=False)
    emails_unread = emails_sub.add_parser("unread-count", help="Get unread count")
    emails_unread.set_defaults(func=emails_cmd.cmd_emails_unread_count, write_capable=False)
    emails_forward = emails_sub.add_parser(
        "forward",
        help="Forward an email (irreversible; requires --apply --yes --ack-irreversible --plan-in)",
    )
    emails_forward.add_argument("--file", required=False, help="Forward email JSON file (required unless --plan-in)")
    emails_forward.set_defaults(func=emails_cmd.cmd_emails_forward, write_capable=True)
    emails_patch = emails_sub.add_parser("patch", help="Patch email (apply-gated)")
    emails_patch.add_argument("--email-id", required=True, help="Email id")
    emails_patch.add_argument("--file", required=True, help="Email patch JSON file")
    emails_patch.set_defaults(func=emails_cmd.cmd_emails_patch, write_capable=True)
    emails_delete = emails_sub.add_parser(
        "delete",
        help="Delete email (destructive; requires --apply --yes --plan-in)",
    )
    emails_delete.add_argument("--email-id", required=False, help="Email id (required unless --plan-in)")
    emails_delete.set_defaults(func=emails_cmd.cmd_emails_delete, write_capable=True)

    threads = sub.add_parser("threads", help="Inbox threads (mark read, reply)")
    threads_sub = threads.add_subparsers(dest="threads_cmd", required=True, parser_class=_ToolArgumentParser)
    threads_mark = threads_sub.add_parser("mark-as-read", help="Mark a conversation/thread as read")
    threads_mark.add_argument("--thread-id", required=True, help="Thread id")
    threads_mark.set_defaults(func=threads_cmd.cmd_threads_mark_as_read, write_capable=True)
    threads_reply = threads_sub.add_parser(
        "reply",
        help="Reply to a conversation (irreversible; requires --apply --yes --ack-irreversible --plan-in)",
    )
    threads_reply.add_argument("--thread-id", required=False, help="Thread id (required unless --plan-in)")
    threads_reply.add_argument("--reply-to-uuid", required=False, help="Reply-to uuid (required unless --plan-in)")
    threads_reply.add_argument("--eaccount", default=None, help="Optional email account identifier (per Instantly schema)")
    threads_reply.add_argument("--subject", default=None, help="Optional subject")
    threads_reply.add_argument("--message", default=None, help="Reply message body (required unless --plan-in)")
    threads_reply.add_argument("--extra-json", default=None, help="Optional JSON object to merge into the request body")
    threads_reply.set_defaults(func=threads_cmd.cmd_threads_reply, write_capable=True)

    dnc = sub.add_parser("do-not-contact", help="Do-not-contact / block list entries")
    dnc_sub = dnc.add_subparsers(dest="dnc_cmd", required=True, parser_class=_ToolArgumentParser)
    dnc_list = dnc_sub.add_parser("list", help="List do-not-contact entries")
    dnc_list.add_argument("--limit", type=int, default=None, help="Page size")
    dnc_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    dnc_list.set_defaults(func=dnc_cmd.cmd_dnc_list, write_capable=False)
    dnc_get = dnc_sub.add_parser("get", help="Get a do-not-contact entry by id")
    dnc_get.add_argument("--entry-id", required=True, help="Do-not-contact entry id")
    dnc_get.set_defaults(func=dnc_cmd.cmd_dnc_get, write_capable=False)
    dnc_create = dnc_sub.add_parser("create", help="Add an email to do-not-contact (requires --apply; and --yes on apply)")
    dnc_create.add_argument("--email", required=True, help="Email address")
    dnc_create.set_defaults(func=dnc_cmd.cmd_dnc_create, write_capable=True)
    dnc_patch = dnc_sub.add_parser("patch", help="Patch a do-not-contact entry (JSON file; apply requires --yes)")
    dnc_patch.add_argument("--entry-id", required=True, help="Do-not-contact entry id")
    dnc_patch.add_argument("--file", required=True, help="Do-not-contact patch JSON file")
    dnc_patch.set_defaults(func=dnc_cmd.cmd_dnc_patch, write_capable=True)
    dnc_delete = dnc_sub.add_parser("delete", help="Remove an email from do-not-contact (requires --apply; and --yes on apply)")
    dnc_delete.add_argument("--entry-id", required=False, help="Do-not-contact entry id (required unless --plan-in)")
    dnc_delete.set_defaults(func=dnc_cmd.cmd_dnc_delete, write_capable=True)

    bg = sub.add_parser("background-jobs", help="Background jobs")
    bg_sub = bg.add_subparsers(dest="bg_cmd", required=True, parser_class=_ToolArgumentParser)
    bg_list = bg_sub.add_parser("list", help="List background jobs")
    bg_list.add_argument("--limit", type=int, default=None, help="Page size")
    bg_list.add_argument("--starting-after", default=None, help="Pagination cursor")
    bg_list.set_defaults(func=background_jobs_cmd.cmd_background_jobs_list, write_capable=False)
    bg_get = bg_sub.add_parser("get", help="Get background job by id")
    bg_get.add_argument("--job-id", required=True, help="Background job id")
    bg_get.set_defaults(func=background_jobs_cmd.cmd_background_jobs_get, write_capable=False)

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
            payload = {"ok": True, "tool": "instantly-api-tool", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"instantly-api-tool {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        command_str = "instantly-api-tool " + " ".join(argv)
        audit.bind_context(
            {
                "tool": "instantly-api-tool",
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
                "tool": "instantly-api-tool",
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
                "write_capable": write_capable,
                "run_id": run_ctx.run_id,
                "artifacts_dir": run_ctx.artifacts_dir,
                "runs_index_path": runs_index_path,
            }
            with write_context(ctx):
                rc = int(args.func(args, ctx))
            return rc

        cfg = load_config(args.env_file)
        env_fingerprint = cfg.base_url
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "tool": "instantly-api-tool",
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
            "write_capable": write_capable,
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
                "tool": "instantly-api-tool",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "env_fingerprint": cfg.base_url,
                "run_id": run_ctx.run_id,
            }
        )
        with write_context(ctx):
            rc = int(args.func(args, ctx))

        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="instantly-api-tool",
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
            tool="instantly-api-tool",
            version=__version__,
            command="instantly-api-tool " + " ".join(argv),
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
            tool="instantly-api-tool",
            version=__version__,
            command="instantly-api-tool " + " ".join(argv),
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
            tool="instantly-api-tool",
            version=__version__,
            command="instantly-api-tool " + " ".join(argv),
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
