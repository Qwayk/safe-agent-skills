from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .cache import ShortTtlCache
from .cloudflare import CloudflareClient
from .commands import auth as auth_cmd
from .commands import accounts as accounts_cmd
from .commands import browser_run as browser_run_cmd
from .commands import onboarding as onboarding_cmd
from .commands import workers as workers_cmd
from .commands import workers_sensitive as workers_sensitive_cmd
from .commands import workers_write as workers_write_cmd
from .commands import workers_tails_stream as workers_tails_stream_cmd
from .commands import workers_logs as workers_logs_cmd
from .commands import openapi_runner as openapi_runner_cmd
from .commands import operations as operations_cmd
from .commands import jobs as jobs_cmd
from .commands import d1 as d1_cmd
from .commands import queues as queues_cmd
from .commands import r2 as r2_cmd
from .commands import zero_trust as zero_trust_cmd
from .commands import zones as zones_cmd
from .commands import dns as dns_cmd
from .commands import observability as observability_cmd
from .commands import waf as waf_cmd
from .commands import custom_hostnames as custom_hostnames_cmd
from .commands import pages as pages_cmd
from .commands import ssl_tls as ssl_tls_cmd
from .commands import load_balancers as load_balancers_cmd
from .commands import cache as cache_cmd
from .commands import registrar as registrar_cmd
from .commands import turnstile as turnstile_cmd
from .commands import email_routing as email_routing_cmd
from .commands import tunnels as tunnels_cmd
from .commands import config_local as config_cmd
from .config import load_config
from .project_config import load_project_config
from .errors import SafetyError, ToolError, ValidationError
from .output import Output
from .secrets import redact_secrets
from .state import cache_dir_for_env_file
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
from .operation_keys import load_allowlisted_operation_commands


class _ToolArgumentParser(argparse.ArgumentParser):
    """
    Ensure user-input errors can be surfaced as JSON.

    Argparse defaults to printing usage/help to stderr and raising SystemExit, which makes it
    hard to keep the `--output json` contract (exactly one JSON object to stdout on errors).
    """

    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


_PARSER_CACHE: argparse.ArgumentParser | None = None

_NAMED_APPLY_BEFORE_STATE_EXEMPT_FUNCS = {
    # Local-only state.
    "cloudflare_api_tool.commands.config_local.cmd_config_init",
    "cloudflare_api_tool.commands.accounts.cmd_accounts_set_default",
    # Sensitive reads and file-only reads that are marked write-capable only because they require --apply/--out.
    "cloudflare_api_tool.commands.accounts.cmd_accounts_members_list",
    "cloudflare_api_tool.commands.accounts.cmd_accounts_members_get",
    "cloudflare_api_tool.commands.browser_run.cmd_browser_run_markdown",
    "cloudflare_api_tool.commands.browser_run.cmd_browser_run_links",
    "cloudflare_api_tool.commands.browser_run.cmd_browser_run_scrape",
    "cloudflare_api_tool.commands.browser_run.cmd_browser_run_screenshot",
    "cloudflare_api_tool.commands.browser_run.cmd_browser_run_crawl",
    "cloudflare_api_tool.commands.browser_run.cmd_browser_run_crawl_result",
    "cloudflare_api_tool.commands.dns.cmd_dns_records_export",
    "cloudflare_api_tool.commands.dns.cmd_secondary_tsigs_list",
    "cloudflare_api_tool.commands.dns.cmd_secondary_tsigs_get",
    "cloudflare_api_tool.commands.d1.cmd_d1_export",
    "cloudflare_api_tool.commands.jobs.cmd_jobs_run",
    "cloudflare_api_tool.commands.queues.cmd_queues_pull",
    "cloudflare_api_tool.commands.observability.cmd_logpush_account_ownership_challenge",
    "cloudflare_api_tool.commands.observability.cmd_logpush_account_ownership_validate",
    "cloudflare_api_tool.commands.observability.cmd_logpush_account_validate_destination",
    "cloudflare_api_tool.commands.observability.cmd_logpush_account_validate_destination_exists",
    "cloudflare_api_tool.commands.observability.cmd_logpush_account_validate_origin",
    "cloudflare_api_tool.commands.observability.cmd_logpush_zone_ownership_challenge",
    "cloudflare_api_tool.commands.observability.cmd_logpush_zone_ownership_validate",
    "cloudflare_api_tool.commands.observability.cmd_logpush_zone_validate_destination",
    "cloudflare_api_tool.commands.observability.cmd_logpush_zone_validate_destination_exists",
    "cloudflare_api_tool.commands.observability.cmd_logpush_zone_validate_origin",
    "cloudflare_api_tool.commands.observability.cmd_logs_received_get",
    "cloudflare_api_tool.commands.observability.cmd_logs_received_fields",
    "cloudflare_api_tool.commands.observability.cmd_logs_rayid_get",
    "cloudflare_api_tool.commands.observability.cmd_audit_logs_account_list",
    "cloudflare_api_tool.commands.observability.cmd_audit_logs_account_list_v2",
    "cloudflare_api_tool.commands.observability.cmd_audit_logs_user_list",
    "cloudflare_api_tool.commands.observability.cmd_request_tracer_trace",
    "cloudflare_api_tool.commands.waf.cmd_waf_snippets_content_get",
    "cloudflare_api_tool.commands.workers_sensitive.cmd_workers_scripts_download",
    "cloudflare_api_tool.commands.workers_sensitive.cmd_workers_scripts_content_get",
    "cloudflare_api_tool.commands.workers_sensitive.cmd_workers_kv_values_get",
    "cloudflare_api_tool.commands.workers_logs.cmd_workers_logs_keys",
    "cloudflare_api_tool.commands.workers_logs.cmd_workers_logs_values",
    "cloudflare_api_tool.commands.workers_logs.cmd_workers_logs_search",
    "cloudflare_api_tool.commands.workers_tails_stream.cmd_workers_tails_stream",
}


def _func_id(func: object) -> str:
    module = str(getattr(func, "__module__", "") or "")
    name = str(getattr(func, "__name__", "") or "")
    return f"{module}.{name}" if module and name else ""


def _live_apply_before_state_block_reason(args: argparse.Namespace) -> str | None:
    if not bool(getattr(args, "apply", False)):
        return None
    if not bool(getattr(args, "write_capable", False)):
        return None
    if bool(getattr(args, "ack_no_snapshot", False)):
        return None
    func_id = _func_id(getattr(args, "func", None))
    if func_id == "cloudflare_api_tool.commands.openapi_runner.cmd_openapi_call":
        return None
    if func_id in _NAMED_APPLY_BEFORE_STATE_EXEMPT_FUNCS:
        return None
    return (
        "Refused: this Cloudflare write has no saved before-state snapshot. Review the dry-run plan "
        "and pass --ack-no-snapshot only when the approved change should continue without an automatic "
        "restore point."
    )


def _cmd_runs_list(args: argparse.Namespace, ctx: dict) -> int:
    _ = args
    runs_index = ctx.get("runs_index_path")
    if not runs_index:
        ctx["out"].emit({"ok": True, "runs": [], "count": 0})
        return 0
    limit = int(getattr(args, "limit", 20) or 20)
    rows = list_runs(runs_index, limit=limit, tool="cloudflare-api-tool")
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
    row = find_run(runs_index, run_id=rid, tool="cloudflare-api-tool")
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
    global _PARSER_CACHE
    if _PARSER_CACHE is not None:
        return _PARSER_CACHE
    p = _ToolArgumentParser(prog="cloudflare-api-tool")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--config", default=None, help="Optional project defaults JSON (non-secret)")
    p.add_argument("--project-dir", default=None, help="Optional project directory (defaults to config file folder)")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--connect-timeout-s", type=float, default=None, help="Override connect timeout seconds")
    p.add_argument("--read-timeout-s", type=float, default=None, help="Override read timeout seconds")
    p.add_argument(
        "--timeout-profile",
        choices=("default", "slow"),
        default=None,
        help="Timeout profile for vendor-slow endpoints (default: auto)",
    )
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    p.add_argument("--progress", action="store_true", help="Emit periodic 'still waiting' lines to stderr on slow requests")
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
    p.add_argument("--cache-ttl-s", type=float, default=60.0, help="Short-TTL cache seconds for safe GET reads (default: 60)")
    p.add_argument("--no-cache", action="store_true", help="Disable short-TTL caching for safe GET reads")
    p.add_argument("--parallel", type=int, default=1, help="Max parallelism for batch read helpers (default: 1)")

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

    config = sub.add_parser("config", help="Local config helpers (no API calls)")
    config_sub = config.add_subparsers(dest="config_cmd", required=True, parser_class=_ToolArgumentParser)
    config_init = config_sub.add_parser("init", help="Create/seed the env file from .env.example (placeholders only)")
    config_init.add_argument("--force", action="store_true", help="Overwrite env file if it already exists")
    config_init.add_argument("--env-example", default=None, help="Optional .env.example path (default: alongside --env-file)")
    config_init.set_defaults(func=config_cmd.cmd_config_init, write_capable=True)
    config_check = config_sub.add_parser("check", help="Validate env file basics (no secrets; no API calls)")
    config_check.set_defaults(func=config_cmd.cmd_config_check, write_capable=False)

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Smoke test credentials")
    auth_check.set_defaults(func=auth_cmd.cmd_auth_check, write_capable=False)
    auth_probe = auth_sub.add_parser("probe", help="Read-only capability probe (no secrets; no writes)")
    auth_probe.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    auth_probe.set_defaults(func=auth_cmd.cmd_auth_probe, write_capable=False)
    auth_zone_create_check = auth_sub.add_parser(
        "zone-create-check",
        help="Safe preflight for zone creation permission on one account",
    )
    auth_zone_create_check.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    auth_zone_create_check.set_defaults(func=auth_cmd.cmd_auth_zone_create_check, write_capable=False)
    auth_doctor = auth_sub.add_parser("doctor", help="Read-only latency/permissions doctor for common endpoints")
    auth_doctor.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    auth_doctor.set_defaults(func=auth_cmd.cmd_auth_doctor, write_capable=False)
    auth_explain = auth_sub.add_parser("explain", help="Explain the likely permissions for a higher-level command")
    auth_explain.add_argument("--for", dest="for_command", nargs=argparse.REMAINDER, required=True, help="Command words to explain, for example: --for observability speed page trend")
    auth_explain.set_defaults(func=auth_cmd.cmd_auth_explain, write_capable=False)

    accounts = sub.add_parser("accounts", help="Accounts (read-only + local defaults)")
    accounts_sub = accounts.add_subparsers(dest="accounts_cmd", required=True, parser_class=_ToolArgumentParser)
    accounts_list = accounts_sub.add_parser("list", help="List accounts")
    accounts_list.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    accounts_list.add_argument("--per-page", type=int, default=50, help="Page size (default: 50)")
    accounts_list.set_defaults(func=accounts_cmd.cmd_accounts_list, write_capable=False)
    accounts_set_default = accounts_sub.add_parser("set-default", help="Set local default account id (non-secret)")
    accounts_set_default.add_argument("--account-id", required=True, help="Cloudflare account id")
    accounts_set_default.set_defaults(func=accounts_cmd.cmd_accounts_set_default, write_capable=True)

    accounts_roles = accounts_sub.add_parser("roles", help="Account roles (read-only)")
    accounts_roles_sub = accounts_roles.add_subparsers(dest="accounts_roles_cmd", required=True, parser_class=_ToolArgumentParser)
    accounts_roles_list = accounts_roles_sub.add_parser("list", help="List account roles")
    accounts_roles_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    accounts_roles_list.set_defaults(func=accounts_cmd.cmd_accounts_roles_list, write_capable=False)
    accounts_roles_get = accounts_roles_sub.add_parser("get", help="Get one account role")
    accounts_roles_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    accounts_roles_get.add_argument("--role-id", required=True, help="Role id")
    accounts_roles_get.set_defaults(func=accounts_cmd.cmd_accounts_roles_get, write_capable=False)

    accounts_members = accounts_sub.add_parser("members", help="Account members (PII-safe; file-only output)")
    accounts_members_sub = accounts_members.add_subparsers(dest="accounts_members_cmd", required=True, parser_class=_ToolArgumentParser)
    accounts_members_list = accounts_members_sub.add_parser("list", help="List account members (file-only output)")
    accounts_members_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    accounts_members_list.add_argument("--status", default=None, choices=["accepted", "pending"], help="Optional member status filter")
    accounts_members_list.add_argument("--out", required=True, help="Output JSON file path (under --project-dir)")
    accounts_members_list.add_argument("--overwrite", action="store_true", help="Allow overwriting the output file")
    accounts_members_list.set_defaults(func=accounts_cmd.cmd_accounts_members_list, write_capable=True)

    accounts_members_get = accounts_members_sub.add_parser("get", help="Get one account member (file-only output)")
    accounts_members_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    accounts_members_get.add_argument("--member-id", required=True, help="Member id")
    accounts_members_get.add_argument("--out", required=True, help="Output JSON file path (under --project-dir)")
    accounts_members_get.add_argument("--overwrite", action="store_true", help="Allow overwriting the output file")
    accounts_members_get.set_defaults(func=accounts_cmd.cmd_accounts_members_get, write_capable=True)

    accounts_members_add = accounts_members_sub.add_parser("add", help="Add an account member (write)")
    accounts_members_add.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    accounts_members_add.add_argument("--email", required=True, help="Member email (never printed; stored only in API request)")
    accounts_members_add.add_argument("--role-id", action="append", default=[], help="Role id to assign (repeatable)")
    accounts_members_add.add_argument("--status", default=None, choices=["accepted", "pending"], help="Optional initial status")
    accounts_members_add.set_defaults(func=accounts_cmd.cmd_accounts_members_add, write_capable=True)

    accounts_members_update = accounts_members_sub.add_parser("update", help="Update an account member (write)")
    accounts_members_update.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    accounts_members_update.add_argument("--member-id", required=True, help="Member id")
    accounts_members_update.add_argument("--role-id", action="append", default=[], help="Role id to set (repeatable)")
    accounts_members_update.add_argument("--status", default=None, choices=["accepted", "pending"], help="Optional status")
    accounts_members_update.set_defaults(func=accounts_cmd.cmd_accounts_members_update, write_capable=True)

    accounts_members_remove = accounts_members_sub.add_parser("remove", help="Remove an account member (write)")
    accounts_members_remove.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    accounts_members_remove.add_argument("--member-id", required=True, help="Member id")
    accounts_members_remove.set_defaults(func=accounts_cmd.cmd_accounts_members_remove, write_capable=True)

    zones = sub.add_parser("zones", help="Zones (read-only)")
    zones_sub = zones.add_subparsers(dest="zones_cmd", required=True, parser_class=_ToolArgumentParser)
    zones_list = zones_sub.add_parser("list", help="List zones")
    zones_list.add_argument("--name", default=None, help="Optional zone name filter")
    zones_list.add_argument("--account-id", default=None, help="Optional account id filter")
    zones_list.add_argument("--status", default=None, help="Optional status filter (e.g. active)")
    zones_list.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    zones_list.add_argument("--per-page", type=int, default=50, help="Page size (default: 50)")
    zones_list.set_defaults(func=zones_cmd.cmd_zones_list, write_capable=False)
    zones_resolve = zones_sub.add_parser("resolve", help="Resolve a zone id by name")
    zones_resolve.add_argument("--name", required=True, help="Zone name (e.g. example.com)")
    zones_resolve.add_argument("--account-id", default=None, help="Optional account id filter")
    zones_resolve.set_defaults(func=zones_cmd.cmd_zones_resolve, write_capable=False)

    zones_settings = zones_sub.add_parser("settings", help="Zone settings (safe-by-default; allowlisted)")
    zones_settings_sub = zones_settings.add_subparsers(dest="zones_settings_cmd", required=True, parser_class=_ToolArgumentParser)

    zones_settings_list = zones_settings_sub.add_parser("list", help="List all zone settings")
    zones_settings_list.add_argument("--zone-id", required=True, help="Zone id")
    zones_settings_list.set_defaults(func=zones_cmd.cmd_zones_settings_list, write_capable=False)

    zones_settings_patch = zones_settings_sub.add_parser("patch", help="Patch multiple zone settings (write)")
    zones_settings_patch.add_argument("--zone-id", required=True, help="Zone id")
    zones_settings_patch.add_argument("--body-json-file", required=True, help="JSON body file")
    zones_settings_patch.set_defaults(func=zones_cmd.cmd_zones_settings_patch, write_capable=True)

    zones_settings_setting_get = zones_settings_sub.add_parser("setting-get", help="Get one allowlisted zone setting")
    zones_settings_setting_get.add_argument("--zone-id", required=True, help="Zone id")
    zones_settings_setting_get.add_argument("--setting-path", required=True, help="Setting path (must be allowlisted)")
    zones_settings_setting_get.set_defaults(func=zones_cmd.cmd_zones_settings_setting_get, write_capable=False)

    zones_settings_setting_patch = zones_settings_sub.add_parser("setting-patch", help="Patch one allowlisted zone setting (write)")
    zones_settings_setting_patch.add_argument("--zone-id", required=True, help="Zone id")
    zones_settings_setting_patch.add_argument("--setting-path", required=True, help="Setting path (must be allowlisted)")
    zones_settings_setting_patch.add_argument("--body-json-file", required=True, help="JSON body file")
    zones_settings_setting_patch.set_defaults(func=zones_cmd.cmd_zones_settings_setting_patch, write_capable=True)

    observability = sub.add_parser("observability", help="Observability (Logpush, Audit Logs, Request Tracer, RUM)")
    obs_sub = observability.add_subparsers(dest="observability_cmd", required=True, parser_class=_ToolArgumentParser)

    def _add_query_flags(pp) -> None:  # noqa: ANN001
        pp.add_argument("--query", action="append", default=None, help="Optional query param: key=value (repeatable)")

    def _add_body_flags(pp, *, required: bool = True) -> None:  # noqa: ANN001
        pp.add_argument("--body-json-file", required=required, help="JSON body file (no secrets printed)")
        pp.add_argument("--content-type", default=None, help="Optional content type override")

    def _add_out_flags(pp) -> None:  # noqa: ANN001
        pp.add_argument("--out", default=None, help="Output file under --project-dir (required on --apply)")
        pp.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing output file")

    def _add_account_id_flag(pp) -> None:  # noqa: ANN001
        pp.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")

    def _add_zone_id_flag(pp) -> None:  # noqa: ANN001
        pp.add_argument("--zone-id", required=True, help="Zone id")

    def _add_browser_run_input_flags(pp, *, allow_html: bool = True) -> None:  # noqa: ANN001
        if allow_html:
            source_group = pp.add_mutually_exclusive_group(required=True)
            source_group.add_argument("--url", default=None, help="Target URL")
            source_group.add_argument("--html", default=None, help="Raw HTML instead of a URL")
        else:
            pp.add_argument("--url", required=True, help="Target URL")

    def _add_browser_run_render_flags(pp) -> None:  # noqa: ANN001
        pp.add_argument("--user-agent", default=None, help="Optional browser user agent")
        pp.add_argument("--cache-ttl", type=int, default=None, help="Optional cache TTL seconds")
        pp.add_argument("--goto-timeout-ms", type=int, default=None, help="Optional page navigation timeout")
        pp.add_argument("--goto-wait-until", default=None, help="Optional navigation wait mode (for example: load, networkidle0)")
        pp.add_argument("--wait-for-timeout-ms", type=int, default=None, help="Optional extra wait after page load")
        pp.add_argument("--wait-for-selector", default=None, help="Optional CSS selector to wait for")
        pp.add_argument("--wait-for-selector-timeout-ms", type=int, default=None, help="Optional selector wait timeout")
        pp.add_argument("--wait-for-selector-visible", action="store_true", help="Require the selector to become visible")
        pp.add_argument(
            "--reject-resource-type",
            action="append",
            default=None,
            help="Optional resource type to block while rendering (repeatable)",
        )
        pp.add_argument("--viewport-width", type=int, default=None, help="Optional viewport width")
        pp.add_argument("--viewport-height", type=int, default=None, help="Optional viewport height")

    browser_run = sub.add_parser("browser-run", help="Cloudflare Browser Run quick actions (file-only output)")
    browser_run_sub = browser_run.add_subparsers(dest="browser_run_cmd", required=True, parser_class=_ToolArgumentParser)

    browser_run_markdown = browser_run_sub.add_parser("markdown", help="Get markdown from a page or HTML")
    _add_account_id_flag(browser_run_markdown)
    _add_browser_run_input_flags(browser_run_markdown, allow_html=True)
    _add_browser_run_render_flags(browser_run_markdown)
    browser_run_markdown.add_argument("--out", required=True, help="Output file under --project-dir")
    browser_run_markdown.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing output file")
    browser_run_markdown.set_defaults(func=browser_run_cmd.cmd_browser_run_markdown, write_capable=True)

    browser_run_links = browser_run_sub.add_parser("links", help="Extract links from a page or HTML")
    _add_account_id_flag(browser_run_links)
    _add_browser_run_input_flags(browser_run_links, allow_html=True)
    _add_browser_run_render_flags(browser_run_links)
    browser_run_links.add_argument("--visible-links-only", action="store_true", help="Only return visible links")
    browser_run_links.add_argument("--exclude-external-links", action="store_true", help="Drop external links")
    browser_run_links.add_argument("--out", required=True, help="Output file under --project-dir")
    browser_run_links.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing output file")
    browser_run_links.set_defaults(func=browser_run_cmd.cmd_browser_run_links, write_capable=True)

    browser_run_scrape = browser_run_sub.add_parser("scrape", help="Scrape selected elements from a page or HTML")
    _add_account_id_flag(browser_run_scrape)
    _add_browser_run_input_flags(browser_run_scrape, allow_html=True)
    _add_browser_run_render_flags(browser_run_scrape)
    browser_run_scrape.add_argument("--selector", action="append", required=True, help="CSS selector to extract (repeatable)")
    browser_run_scrape.add_argument("--out", required=True, help="Output file under --project-dir")
    browser_run_scrape.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing output file")
    browser_run_scrape.set_defaults(func=browser_run_cmd.cmd_browser_run_scrape, write_capable=True)

    browser_run_screenshot = browser_run_sub.add_parser("screenshot", help="Capture a screenshot from a page or HTML")
    _add_account_id_flag(browser_run_screenshot)
    _add_browser_run_input_flags(browser_run_screenshot, allow_html=True)
    _add_browser_run_render_flags(browser_run_screenshot)
    browser_run_screenshot.add_argument("--full-page", action="store_true", help="Capture the full page")
    browser_run_screenshot.add_argument("--omit-background", action="store_true", help="Keep transparent backgrounds when supported")
    browser_run_screenshot.add_argument("--image-type", choices=("png", "jpeg", "webp"), default=None, help="Optional screenshot format")
    browser_run_screenshot.add_argument("--out", required=True, help="Output file under --project-dir")
    browser_run_screenshot.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing output file")
    browser_run_screenshot.set_defaults(func=browser_run_cmd.cmd_browser_run_screenshot, write_capable=True)

    browser_run_crawl = browser_run_sub.add_parser("crawl", help="Start a crawl job from one URL")
    _add_account_id_flag(browser_run_crawl)
    _add_browser_run_input_flags(browser_run_crawl, allow_html=False)
    _add_browser_run_render_flags(browser_run_crawl)
    browser_run_crawl.add_argument("--depth", type=int, default=None, help="Optional crawl depth")
    browser_run_crawl.add_argument("--limit", type=int, default=None, help="Optional max pages")
    browser_run_crawl.add_argument("--source", choices=("links", "sitemaps"), default=None, help="Optional crawl source")
    browser_run_crawl.add_argument("--format", action="append", default=None, help="Optional output format filter (repeatable)")
    browser_run_crawl.add_argument("--include-pattern", action="append", default=None, help="Optional include URL pattern (repeatable)")
    browser_run_crawl.add_argument("--exclude-pattern", action="append", default=None, help="Optional exclude URL pattern (repeatable)")
    browser_run_crawl.add_argument("--include-subdomains", action="store_true", help="Allow subdomain traversal")
    browser_run_crawl.add_argument("--include-external-links", action="store_true", help="Allow external links")
    browser_run_crawl.add_argument("--no-render", action="store_true", help="Do not render each crawled page in a browser")
    browser_run_crawl.add_argument("--out", required=True, help="Output file under --project-dir")
    browser_run_crawl.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing output file")
    browser_run_crawl.set_defaults(func=browser_run_cmd.cmd_browser_run_crawl, write_capable=True)

    browser_run_crawl_result = browser_run_sub.add_parser("crawl-result", help="Fetch a saved crawl job result")
    _add_account_id_flag(browser_run_crawl_result)
    browser_run_crawl_result.add_argument("--job-id", required=True, help="Crawl job id")
    browser_run_crawl_result.add_argument("--cache-ttl", type=int, default=None, help="Optional cache TTL seconds")
    browser_run_crawl_result.add_argument("--limit", type=int, default=None, help="Optional result limit")
    browser_run_crawl_result.add_argument("--cursor", default=None, help="Optional result cursor")
    browser_run_crawl_result.add_argument("--status", default=None, help="Optional page status filter")
    browser_run_crawl_result.add_argument("--out", required=True, help="Output file under --project-dir")
    browser_run_crawl_result.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing output file")
    browser_run_crawl_result.set_defaults(func=browser_run_cmd.cmd_browser_run_crawl_result, write_capable=True)

    # Logpush
    logpush = obs_sub.add_parser("logpush", help="Logpush (account + zone + instant logs jobs)")
    logpush_sub = logpush.add_subparsers(dest="observability_logpush_cmd", required=True, parser_class=_ToolArgumentParser)

    # Logpush: account-scoped
    lp_account = logpush_sub.add_parser("account", help="Account-scoped Logpush")
    lp_account_sub = lp_account.add_subparsers(dest="observability_logpush_account_cmd", required=True, parser_class=_ToolArgumentParser)

    lp_account_datasets = lp_account_sub.add_parser("datasets", help="Datasets (account-scoped)")
    lp_account_datasets_sub = lp_account_datasets.add_subparsers(dest="observability_logpush_account_datasets_cmd", required=True, parser_class=_ToolArgumentParser)
    lp_account_datasets_fields = lp_account_datasets_sub.add_parser("fields", help="List dataset fields")
    _add_account_id_flag(lp_account_datasets_fields)
    lp_account_datasets_fields.add_argument("--dataset-id", required=True, help="Dataset id")
    _add_query_flags(lp_account_datasets_fields)
    _add_out_flags(lp_account_datasets_fields)
    lp_account_datasets_fields.set_defaults(func=observability_cmd.cmd_logpush_account_datasets_fields, write_capable=False)
    lp_account_datasets_jobs = lp_account_datasets_sub.add_parser("jobs", help="List jobs for a dataset")
    _add_account_id_flag(lp_account_datasets_jobs)
    lp_account_datasets_jobs.add_argument("--dataset-id", required=True, help="Dataset id")
    _add_query_flags(lp_account_datasets_jobs)
    _add_out_flags(lp_account_datasets_jobs)
    lp_account_datasets_jobs.set_defaults(func=observability_cmd.cmd_logpush_account_datasets_jobs, write_capable=False)

    lp_account_jobs = lp_account_sub.add_parser("jobs", help="Logpush jobs (account-scoped)")
    lp_account_jobs_sub = lp_account_jobs.add_subparsers(dest="observability_logpush_account_jobs_cmd", required=True, parser_class=_ToolArgumentParser)
    lp_account_jobs_list = lp_account_jobs_sub.add_parser("list", help="List jobs")
    _add_account_id_flag(lp_account_jobs_list)
    _add_query_flags(lp_account_jobs_list)
    _add_out_flags(lp_account_jobs_list)
    lp_account_jobs_list.set_defaults(func=observability_cmd.cmd_logpush_account_jobs_list, write_capable=False)
    lp_account_jobs_create = lp_account_jobs_sub.add_parser("create", help="Create a job (write)")
    _add_account_id_flag(lp_account_jobs_create)
    _add_body_flags(lp_account_jobs_create, required=True)
    _add_query_flags(lp_account_jobs_create)
    _add_out_flags(lp_account_jobs_create)
    lp_account_jobs_create.set_defaults(func=observability_cmd.cmd_logpush_account_jobs_create, write_capable=True)
    lp_account_jobs_get = lp_account_jobs_sub.add_parser("get", help="Get one job")
    _add_account_id_flag(lp_account_jobs_get)
    lp_account_jobs_get.add_argument("--job-id", required=True, help="Job id")
    _add_query_flags(lp_account_jobs_get)
    _add_out_flags(lp_account_jobs_get)
    lp_account_jobs_get.set_defaults(func=observability_cmd.cmd_logpush_account_jobs_get, write_capable=False)
    lp_account_jobs_update = lp_account_jobs_sub.add_parser("update", help="Update a job (write)")
    _add_account_id_flag(lp_account_jobs_update)
    lp_account_jobs_update.add_argument("--job-id", required=True, help="Job id")
    _add_body_flags(lp_account_jobs_update, required=True)
    _add_query_flags(lp_account_jobs_update)
    _add_out_flags(lp_account_jobs_update)
    lp_account_jobs_update.set_defaults(func=observability_cmd.cmd_logpush_account_jobs_update, write_capable=True)
    lp_account_jobs_delete = lp_account_jobs_sub.add_parser("delete", help="Delete a job (write)")
    _add_account_id_flag(lp_account_jobs_delete)
    lp_account_jobs_delete.add_argument("--job-id", required=True, help="Job id")
    _add_query_flags(lp_account_jobs_delete)
    _add_out_flags(lp_account_jobs_delete)
    lp_account_jobs_delete.set_defaults(func=observability_cmd.cmd_logpush_account_jobs_delete, write_capable=True)

    lp_account_ownership = lp_account_sub.add_parser("ownership", help="Logpush ownership challenge (account-scoped)")
    lp_account_ownership_sub = lp_account_ownership.add_subparsers(dest="observability_logpush_account_ownership_cmd", required=True, parser_class=_ToolArgumentParser)
    lp_account_ownership_challenge = lp_account_ownership_sub.add_parser("challenge", help="Get ownership challenge (write)")
    _add_account_id_flag(lp_account_ownership_challenge)
    _add_body_flags(lp_account_ownership_challenge, required=True)
    _add_out_flags(lp_account_ownership_challenge)
    lp_account_ownership_challenge.set_defaults(func=observability_cmd.cmd_logpush_account_ownership_challenge, write_capable=True)
    lp_account_ownership_validate = lp_account_ownership_sub.add_parser("validate", help="Validate ownership challenge (write)")
    _add_account_id_flag(lp_account_ownership_validate)
    _add_body_flags(lp_account_ownership_validate, required=True)
    _add_out_flags(lp_account_ownership_validate)
    lp_account_ownership_validate.set_defaults(func=observability_cmd.cmd_logpush_account_ownership_validate, write_capable=True)

    lp_account_validate = lp_account_sub.add_parser("validate", help="Validate origin/destination (account-scoped; write-like)")
    lp_account_validate_sub = lp_account_validate.add_subparsers(dest="observability_logpush_account_validate_cmd", required=True, parser_class=_ToolArgumentParser)
    lp_account_validate_destination = lp_account_validate_sub.add_parser("destination", help="Validate destination (write-like)")
    _add_account_id_flag(lp_account_validate_destination)
    _add_body_flags(lp_account_validate_destination, required=True)
    _add_out_flags(lp_account_validate_destination)
    lp_account_validate_destination.set_defaults(func=observability_cmd.cmd_logpush_account_validate_destination, write_capable=True)
    lp_account_validate_destination_exists = lp_account_validate_sub.add_parser("destination-exists", help="Check destination exists (write-like)")
    _add_account_id_flag(lp_account_validate_destination_exists)
    _add_body_flags(lp_account_validate_destination_exists, required=True)
    _add_out_flags(lp_account_validate_destination_exists)
    lp_account_validate_destination_exists.set_defaults(func=observability_cmd.cmd_logpush_account_validate_destination_exists, write_capable=True)
    lp_account_validate_origin = lp_account_validate_sub.add_parser("origin", help="Validate origin (write-like)")
    _add_account_id_flag(lp_account_validate_origin)
    _add_body_flags(lp_account_validate_origin, required=True)
    _add_out_flags(lp_account_validate_origin)
    lp_account_validate_origin.set_defaults(func=observability_cmd.cmd_logpush_account_validate_origin, write_capable=True)

    # Logpush: zone-scoped
    lp_zone = logpush_sub.add_parser("zone", help="Zone-scoped Logpush")
    lp_zone_sub = lp_zone.add_subparsers(dest="observability_logpush_zone_cmd", required=True, parser_class=_ToolArgumentParser)

    lp_zone_datasets = lp_zone_sub.add_parser("datasets", help="Datasets (zone-scoped)")
    lp_zone_datasets_sub = lp_zone_datasets.add_subparsers(dest="observability_logpush_zone_datasets_cmd", required=True, parser_class=_ToolArgumentParser)
    lp_zone_datasets_fields = lp_zone_datasets_sub.add_parser("fields", help="List dataset fields")
    _add_zone_id_flag(lp_zone_datasets_fields)
    lp_zone_datasets_fields.add_argument("--dataset-id", required=True, help="Dataset id")
    _add_query_flags(lp_zone_datasets_fields)
    _add_out_flags(lp_zone_datasets_fields)
    lp_zone_datasets_fields.set_defaults(func=observability_cmd.cmd_logpush_zone_datasets_fields, write_capable=False)
    lp_zone_datasets_jobs = lp_zone_datasets_sub.add_parser("jobs", help="List jobs for a dataset")
    _add_zone_id_flag(lp_zone_datasets_jobs)
    lp_zone_datasets_jobs.add_argument("--dataset-id", required=True, help="Dataset id")
    _add_query_flags(lp_zone_datasets_jobs)
    _add_out_flags(lp_zone_datasets_jobs)
    lp_zone_datasets_jobs.set_defaults(func=observability_cmd.cmd_logpush_zone_datasets_jobs, write_capable=False)

    lp_zone_jobs = lp_zone_sub.add_parser("jobs", help="Logpush jobs (zone-scoped)")
    lp_zone_jobs_sub = lp_zone_jobs.add_subparsers(dest="observability_logpush_zone_jobs_cmd", required=True, parser_class=_ToolArgumentParser)
    lp_zone_jobs_list = lp_zone_jobs_sub.add_parser("list", help="List jobs")
    _add_zone_id_flag(lp_zone_jobs_list)
    _add_query_flags(lp_zone_jobs_list)
    _add_out_flags(lp_zone_jobs_list)
    lp_zone_jobs_list.set_defaults(func=observability_cmd.cmd_logpush_zone_jobs_list, write_capable=False)
    lp_zone_jobs_create = lp_zone_jobs_sub.add_parser("create", help="Create a job (write)")
    _add_zone_id_flag(lp_zone_jobs_create)
    _add_body_flags(lp_zone_jobs_create, required=True)
    _add_query_flags(lp_zone_jobs_create)
    _add_out_flags(lp_zone_jobs_create)
    lp_zone_jobs_create.set_defaults(func=observability_cmd.cmd_logpush_zone_jobs_create, write_capable=True)
    lp_zone_jobs_get = lp_zone_jobs_sub.add_parser("get", help="Get one job")
    _add_zone_id_flag(lp_zone_jobs_get)
    lp_zone_jobs_get.add_argument("--job-id", required=True, help="Job id")
    _add_query_flags(lp_zone_jobs_get)
    _add_out_flags(lp_zone_jobs_get)
    lp_zone_jobs_get.set_defaults(func=observability_cmd.cmd_logpush_zone_jobs_get, write_capable=False)
    lp_zone_jobs_update = lp_zone_jobs_sub.add_parser("update", help="Update a job (write)")
    _add_zone_id_flag(lp_zone_jobs_update)
    lp_zone_jobs_update.add_argument("--job-id", required=True, help="Job id")
    _add_body_flags(lp_zone_jobs_update, required=True)
    _add_query_flags(lp_zone_jobs_update)
    _add_out_flags(lp_zone_jobs_update)
    lp_zone_jobs_update.set_defaults(func=observability_cmd.cmd_logpush_zone_jobs_update, write_capable=True)
    lp_zone_jobs_delete = lp_zone_jobs_sub.add_parser("delete", help="Delete a job (write)")
    _add_zone_id_flag(lp_zone_jobs_delete)
    lp_zone_jobs_delete.add_argument("--job-id", required=True, help="Job id")
    _add_query_flags(lp_zone_jobs_delete)
    _add_out_flags(lp_zone_jobs_delete)
    lp_zone_jobs_delete.set_defaults(func=observability_cmd.cmd_logpush_zone_jobs_delete, write_capable=True)

    lp_zone_instant = lp_zone_sub.add_parser("instant-jobs", help="Instant Logs jobs (zone-scoped)")
    lp_zone_instant_sub = lp_zone_instant.add_subparsers(dest="observability_logpush_zone_instant_cmd", required=True, parser_class=_ToolArgumentParser)
    lp_zone_instant_list = lp_zone_instant_sub.add_parser("list", help="List Instant Logs jobs")
    _add_zone_id_flag(lp_zone_instant_list)
    _add_query_flags(lp_zone_instant_list)
    _add_out_flags(lp_zone_instant_list)
    lp_zone_instant_list.set_defaults(func=observability_cmd.cmd_logpush_zone_instant_jobs_list, write_capable=False)
    lp_zone_instant_create = lp_zone_instant_sub.add_parser("create", help="Create Instant Logs job (write)")
    _add_zone_id_flag(lp_zone_instant_create)
    _add_body_flags(lp_zone_instant_create, required=True)
    _add_query_flags(lp_zone_instant_create)
    _add_out_flags(lp_zone_instant_create)
    lp_zone_instant_create.set_defaults(func=observability_cmd.cmd_logpush_zone_instant_jobs_create, write_capable=True)

    lp_zone_ownership = lp_zone_sub.add_parser("ownership", help="Logpush ownership challenge (zone-scoped)")
    lp_zone_ownership_sub = lp_zone_ownership.add_subparsers(dest="observability_logpush_zone_ownership_cmd", required=True, parser_class=_ToolArgumentParser)
    lp_zone_ownership_challenge = lp_zone_ownership_sub.add_parser("challenge", help="Get ownership challenge (write)")
    _add_zone_id_flag(lp_zone_ownership_challenge)
    _add_body_flags(lp_zone_ownership_challenge, required=True)
    _add_out_flags(lp_zone_ownership_challenge)
    lp_zone_ownership_challenge.set_defaults(func=observability_cmd.cmd_logpush_zone_ownership_challenge, write_capable=True)
    lp_zone_ownership_validate = lp_zone_ownership_sub.add_parser("validate", help="Validate ownership challenge (write)")
    _add_zone_id_flag(lp_zone_ownership_validate)
    _add_body_flags(lp_zone_ownership_validate, required=True)
    _add_out_flags(lp_zone_ownership_validate)
    lp_zone_ownership_validate.set_defaults(func=observability_cmd.cmd_logpush_zone_ownership_validate, write_capable=True)

    lp_zone_validate = lp_zone_sub.add_parser("validate", help="Validate origin/destination (zone-scoped; write-like)")
    lp_zone_validate_sub = lp_zone_validate.add_subparsers(dest="observability_logpush_zone_validate_cmd", required=True, parser_class=_ToolArgumentParser)
    lp_zone_validate_destination = lp_zone_validate_sub.add_parser("destination", help="Validate destination (write-like)")
    _add_zone_id_flag(lp_zone_validate_destination)
    _add_body_flags(lp_zone_validate_destination, required=True)
    _add_out_flags(lp_zone_validate_destination)
    lp_zone_validate_destination.set_defaults(func=observability_cmd.cmd_logpush_zone_validate_destination, write_capable=True)
    lp_zone_validate_destination_exists = lp_zone_validate_sub.add_parser("destination-exists", help="Check destination exists (write-like)")
    _add_zone_id_flag(lp_zone_validate_destination_exists)
    _add_body_flags(lp_zone_validate_destination_exists, required=True)
    _add_out_flags(lp_zone_validate_destination_exists)
    lp_zone_validate_destination_exists.set_defaults(func=observability_cmd.cmd_logpush_zone_validate_destination_exists, write_capable=True)
    lp_zone_validate_origin = lp_zone_validate_sub.add_parser("origin", help="Validate origin (write-like)")
    _add_zone_id_flag(lp_zone_validate_origin)
    _add_body_flags(lp_zone_validate_origin, required=True)
    _add_out_flags(lp_zone_validate_origin)
    lp_zone_validate_origin.set_defaults(func=observability_cmd.cmd_logpush_zone_validate_origin, write_capable=True)

    # Zone logs (sensitive read; file-only)
    logs = obs_sub.add_parser("logs", help="Zone logs (received fields, rayid lookup)")
    logs_sub = logs.add_subparsers(dest="observability_logs_cmd", required=True, parser_class=_ToolArgumentParser)
    logs_received = logs_sub.add_parser("received", help="Get received logs (sensitive; file-only)")
    logs_received.add_argument("--zone-id", required=True, help="Zone id")
    _add_out_flags(logs_received)
    _add_query_flags(logs_received)
    logs_received.set_defaults(func=observability_cmd.cmd_logs_received_get, write_capable=True)
    logs_received_fields = logs_sub.add_parser("received-fields", help="List received logs fields (sensitive; file-only)")
    logs_received_fields.add_argument("--zone-id", required=True, help="Zone id")
    _add_out_flags(logs_received_fields)
    _add_query_flags(logs_received_fields)
    logs_received_fields.set_defaults(func=observability_cmd.cmd_logs_received_fields, write_capable=True)
    logs_rayid = logs_sub.add_parser("rayid", help="Lookup one ray id (sensitive; file-only)")
    logs_rayid.add_argument("--zone-id", required=True, help="Zone id")
    logs_rayid.add_argument("--ray-id", required=True, help="Ray id")
    _add_out_flags(logs_rayid)
    _add_query_flags(logs_rayid)
    logs_rayid.set_defaults(func=observability_cmd.cmd_logs_rayid_get, write_capable=True)

    # Audit logs (sensitive read; file-only)
    audit_logs = obs_sub.add_parser("audit-logs", help="Audit logs (sensitive; file-only)")
    audit_logs_sub = audit_logs.add_subparsers(dest="observability_audit_logs_cmd", required=True, parser_class=_ToolArgumentParser)
    audit_account = audit_logs_sub.add_parser("account", help="Account audit logs (sensitive; file-only)")
    audit_account_sub = audit_account.add_subparsers(dest="observability_audit_account_cmd", required=True, parser_class=_ToolArgumentParser)
    audit_account_list = audit_account_sub.add_parser("list", help="List account audit logs")
    _add_account_id_flag(audit_account_list)
    _add_out_flags(audit_account_list)
    _add_query_flags(audit_account_list)
    audit_account_list.set_defaults(func=observability_cmd.cmd_audit_logs_account_list, write_capable=True)
    audit_account_list_v2 = audit_account_sub.add_parser("list-v2", help="List account audit logs (v2 beta path)")
    _add_account_id_flag(audit_account_list_v2)
    _add_out_flags(audit_account_list_v2)
    _add_query_flags(audit_account_list_v2)
    audit_account_list_v2.set_defaults(func=observability_cmd.cmd_audit_logs_account_list_v2, write_capable=True)
    audit_user = audit_logs_sub.add_parser("user", help="User audit logs (sensitive; file-only)")
    audit_user_sub = audit_user.add_subparsers(dest="observability_audit_user_cmd", required=True, parser_class=_ToolArgumentParser)
    audit_user_list = audit_user_sub.add_parser("list", help="List user audit logs")
    _add_out_flags(audit_user_list)
    _add_query_flags(audit_user_list)
    audit_user_list.set_defaults(func=observability_cmd.cmd_audit_logs_user_list, write_capable=True)

    # Logs control
    logs_control = obs_sub.add_parser("logs-control", help="Logs control settings (CMB config)")
    logs_control_sub = logs_control.add_subparsers(dest="observability_logs_control_cmd", required=True, parser_class=_ToolArgumentParser)
    cmb = logs_control_sub.add_parser("cmb", help="CMB config")
    cmb_sub = cmb.add_subparsers(dest="observability_logs_control_cmb_cmd", required=True, parser_class=_ToolArgumentParser)
    cmb_get = cmb_sub.add_parser("get", help="Get CMB config")
    _add_account_id_flag(cmb_get)
    _add_query_flags(cmb_get)
    cmb_get.set_defaults(func=observability_cmd.cmd_logs_control_cmb_get, write_capable=False)
    cmb_update = cmb_sub.add_parser("update", help="Update CMB config (write)")
    _add_account_id_flag(cmb_update)
    _add_body_flags(cmb_update, required=True)
    cmb_update.set_defaults(func=observability_cmd.cmd_logs_control_cmb_update, write_capable=True)
    cmb_delete = cmb_sub.add_parser("delete", help="Delete CMB config (write)")
    _add_account_id_flag(cmb_delete)
    cmb_delete.set_defaults(func=observability_cmd.cmd_logs_control_cmb_delete, write_capable=True)

    # Request tracer
    request_tracer = obs_sub.add_parser("request-tracer", help="Request Tracer (sensitive; file-only)")
    request_tracer_sub = request_tracer.add_subparsers(dest="observability_request_tracer_cmd", required=True, parser_class=_ToolArgumentParser)
    trace = request_tracer_sub.add_parser("trace", help="Request a trace (read-like POST; sensitive; file-only)")
    _add_account_id_flag(trace)
    _add_body_flags(trace, required=True)
    _add_out_flags(trace)
    _add_query_flags(trace)
    trace.set_defaults(func=observability_cmd.cmd_request_tracer_trace, write_capable=True)

    # Observatory speed
    speed = obs_sub.add_parser("speed", help="Cloudflare Observatory speed checks and summaries")
    speed_sub = speed.add_subparsers(dest="observability_speed_cmd", required=True, parser_class=_ToolArgumentParser)
    speed_availabilities = speed_sub.add_parser("availabilities", help="Get Observatory quota/availability for a zone")
    _add_zone_id_flag(speed_availabilities)
    speed_availabilities.set_defaults(func=observability_cmd.cmd_speed_availabilities, write_capable=False)
    speed_pages = speed_sub.add_parser("pages", help="List Observatory-tested pages for a zone")
    speed_pages_sub = speed_pages.add_subparsers(dest="observability_speed_pages_cmd", required=True, parser_class=_ToolArgumentParser)
    speed_pages_list = speed_pages_sub.add_parser("list", help="List tested pages")
    _add_zone_id_flag(speed_pages_list)
    speed_pages_list.set_defaults(func=observability_cmd.cmd_speed_pages_list, write_capable=False)
    speed_page = speed_sub.add_parser("page", help="Page-level Observatory summaries")
    speed_page_sub = speed_page.add_subparsers(dest="observability_speed_page_cmd", required=True, parser_class=_ToolArgumentParser)
    speed_page_latest = speed_page_sub.add_parser("latest", help="Show the latest saved test for one page URL")
    _add_zone_id_flag(speed_page_latest)
    speed_page_latest.add_argument("--url", required=True, help="Page URL or hostname/path")
    speed_page_latest.set_defaults(func=observability_cmd.cmd_speed_page_latest, write_capable=False)
    speed_page_trend = speed_page_sub.add_parser("trend", help="Show the saved trend series for one page URL")
    _add_zone_id_flag(speed_page_trend)
    speed_page_trend.add_argument("--url", required=True, help="Page URL or hostname/path")
    speed_page_trend.set_defaults(func=observability_cmd.cmd_speed_page_trend, write_capable=False)
    speed_page_history = speed_page_sub.add_parser("history", help="Show saved test history for one page URL")
    _add_zone_id_flag(speed_page_history)
    speed_page_history.add_argument("--url", required=True, help="Page URL or hostname/path")
    speed_page_history.set_defaults(func=observability_cmd.cmd_speed_page_history, write_capable=False)

    web_analytics = obs_sub.add_parser("web-analytics", help="Cloudflare Web Analytics / RUM summaries")
    web_analytics_sub = web_analytics.add_subparsers(dest="observability_web_analytics_cmd", required=True, parser_class=_ToolArgumentParser)
    web_analytics_status = web_analytics_sub.add_parser("status", help="Check whether Web Analytics / RUM is wired up for a zone")
    _add_zone_id_flag(web_analytics_status)
    _add_account_id_flag(web_analytics_status)
    web_analytics_status.set_defaults(func=observability_cmd.cmd_web_analytics_status, write_capable=False)

    audit = obs_sub.add_parser("audit", help="Bundled observability audit for one zone")
    _add_zone_id_flag(audit)
    _add_account_id_flag(audit)
    audit.add_argument("--url", default=None, help="Optional page URL to use for the speed summary (defaults to homepage guess)")
    audit.set_defaults(func=observability_cmd.cmd_observability_audit, write_capable=False)

    # RUM / Web Analytics
    rum = obs_sub.add_parser("rum", help="RUM and Web Analytics")
    rum_sub = rum.add_subparsers(dest="observability_rum_cmd", required=True, parser_class=_ToolArgumentParser)

    rum_sites = rum_sub.add_parser("sites", help="Web Analytics sites (account-scoped)")
    rum_sites_sub = rum_sites.add_subparsers(dest="observability_rum_sites_cmd", required=True, parser_class=_ToolArgumentParser)
    rum_sites_list = rum_sites_sub.add_parser("list", help="List sites")
    _add_account_id_flag(rum_sites_list)
    _add_query_flags(rum_sites_list)
    rum_sites_list.set_defaults(func=observability_cmd.cmd_rum_sites_list, write_capable=False)
    rum_sites_create = rum_sites_sub.add_parser("create", help="Create a site (write)")
    _add_account_id_flag(rum_sites_create)
    _add_body_flags(rum_sites_create, required=True)
    rum_sites_create.set_defaults(func=observability_cmd.cmd_rum_sites_create, write_capable=True)
    rum_sites_get = rum_sites_sub.add_parser("get", help="Get one site")
    _add_account_id_flag(rum_sites_get)
    rum_sites_get.add_argument("--site-id", required=True, help="Site id")
    _add_query_flags(rum_sites_get)
    rum_sites_get.set_defaults(func=observability_cmd.cmd_rum_sites_get, write_capable=False)
    rum_sites_update = rum_sites_sub.add_parser("update", help="Update a site (write)")
    _add_account_id_flag(rum_sites_update)
    rum_sites_update.add_argument("--site-id", required=True, help="Site id")
    _add_body_flags(rum_sites_update, required=True)
    rum_sites_update.set_defaults(func=observability_cmd.cmd_rum_sites_update, write_capable=True)
    rum_sites_delete = rum_sites_sub.add_parser("delete", help="Delete a site (write)")
    _add_account_id_flag(rum_sites_delete)
    rum_sites_delete.add_argument("--site-id", required=True, help="Site id")
    rum_sites_delete.set_defaults(func=observability_cmd.cmd_rum_sites_delete, write_capable=True)

    rum_rules = rum_sub.add_parser("rules", help="Web Analytics rules (account-scoped)")
    rum_rules_sub = rum_rules.add_subparsers(dest="observability_rum_rules_cmd", required=True, parser_class=_ToolArgumentParser)
    rum_rules_list = rum_rules_sub.add_parser("list", help="List rules in a ruleset")
    _add_account_id_flag(rum_rules_list)
    rum_rules_list.add_argument("--ruleset-id", required=True, help="Ruleset id")
    _add_query_flags(rum_rules_list)
    rum_rules_list.set_defaults(func=observability_cmd.cmd_rum_rules_list, write_capable=False)
    rum_rules_bulk_update = rum_rules_sub.add_parser("bulk-update", help="Bulk update rules (write)")
    _add_account_id_flag(rum_rules_bulk_update)
    rum_rules_bulk_update.add_argument("--ruleset-id", required=True, help="Ruleset id")
    _add_body_flags(rum_rules_bulk_update, required=True)
    rum_rules_bulk_update.set_defaults(func=observability_cmd.cmd_rum_rules_bulk_update, write_capable=True)
    rum_rule_create = rum_rules_sub.add_parser("create", help="Create one rule (write)")
    _add_account_id_flag(rum_rule_create)
    rum_rule_create.add_argument("--ruleset-id", required=True, help="Ruleset id")
    _add_body_flags(rum_rule_create, required=True)
    rum_rule_create.set_defaults(func=observability_cmd.cmd_rum_rule_create, write_capable=True)
    rum_rule_update = rum_rules_sub.add_parser("update", help="Update one rule (write)")
    _add_account_id_flag(rum_rule_update)
    rum_rule_update.add_argument("--ruleset-id", required=True, help="Ruleset id")
    rum_rule_update.add_argument("--rule-id", required=True, help="Rule id")
    _add_body_flags(rum_rule_update, required=True)
    rum_rule_update.set_defaults(func=observability_cmd.cmd_rum_rule_update, write_capable=True)
    rum_rule_delete = rum_rules_sub.add_parser("delete", help="Delete one rule (write)")
    _add_account_id_flag(rum_rule_delete)
    rum_rule_delete.add_argument("--ruleset-id", required=True, help="Ruleset id")
    rum_rule_delete.add_argument("--rule-id", required=True, help="Rule id")
    rum_rule_delete.set_defaults(func=observability_cmd.cmd_rum_rule_delete, write_capable=True)

    rum_zone = rum_sub.add_parser("zone-settings", help="Zone RUM status (zone-scoped)")
    rum_zone_sub = rum_zone.add_subparsers(dest="observability_rum_zone_cmd", required=True, parser_class=_ToolArgumentParser)
    rum_zone_get = rum_zone_sub.add_parser("get", help="Get RUM status")
    rum_zone_get.add_argument("--zone-id", required=True, help="Zone id")
    _add_query_flags(rum_zone_get)
    rum_zone_get.set_defaults(func=observability_cmd.cmd_rum_zone_settings_get, write_capable=False)
    rum_zone_toggle = rum_zone_sub.add_parser("toggle", help="Toggle RUM on/off (write)")
    rum_zone_toggle.add_argument("--zone-id", required=True, help="Zone id")
    _add_body_flags(rum_zone_toggle, required=True)
    rum_zone_toggle.set_defaults(func=observability_cmd.cmd_rum_zone_settings_toggle, write_capable=True)

    dns = sub.add_parser("dns", help="DNS (records + scans; safe-by-default)")
    dns_sub = dns.add_subparsers(dest="dns_cmd", required=True, parser_class=_ToolArgumentParser)

    dns_records = dns_sub.add_parser("records", help="DNS records (zone-scoped)")
    dns_records_sub = dns_records.add_subparsers(dest="dns_records_cmd", required=True, parser_class=_ToolArgumentParser)
    dns_records_list = dns_records_sub.add_parser("list", help="List DNS records")
    dns_records_list.add_argument("--zone-id", required=True, help="Zone id")
    dns_records_list.add_argument("--name", default=None, help="Optional name filter")
    dns_records_list.add_argument("--type", default=None, help="Optional type filter (A/AAAA/CNAME/TXT/...)")
    dns_records_list.add_argument("--content", default=None, help="Optional content/value filter")
    dns_records_list.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    dns_records_list.add_argument("--per-page", type=int, default=50, help="Page size (default: 50)")
    dns_records_list.set_defaults(func=dns_cmd.cmd_dns_records_list, write_capable=False)

    dns_records_get = dns_records_sub.add_parser("get", help="Get one DNS record")
    dns_records_get.add_argument("--zone-id", required=True, help="Zone id")
    dns_records_get.add_argument("--record-id", required=True, help="DNS record id")
    dns_records_get.set_defaults(func=dns_cmd.cmd_dns_records_get, write_capable=False)

    dns_records_ensure = dns_records_sub.add_parser("ensure", help="Ensure a DNS record exists (write)")
    dns_records_ensure.add_argument("--zone-id", required=True, help="Zone id")
    dns_records_ensure.add_argument("--name", required=True, help="Record name (e.g. www.example.com)")
    dns_records_ensure.add_argument("--type", required=True, help="Record type (A/AAAA/CNAME/TXT/...)")
    dns_records_ensure.add_argument("--content", required=True, help="Record content/value")
    dns_records_ensure.add_argument("--ttl", type=int, default=None, help="Optional TTL")
    px = dns_records_ensure.add_mutually_exclusive_group()
    px.add_argument("--proxied", action="store_true", default=None, help="Set proxied=true")
    px.add_argument("--no-proxied", action="store_false", dest="proxied", default=None, help="Set proxied=false")
    dns_records_ensure.add_argument("--comment", default=None, help="Optional comment")
    dns_records_ensure.set_defaults(func=dns_cmd.cmd_dns_records_ensure, write_capable=True)

    dns_records_absent = dns_records_sub.add_parser("ensure-absent", help="Ensure a DNS record is absent (write)")
    dns_records_absent.add_argument("--zone-id", required=True, help="Zone id")
    dns_records_absent.add_argument("--record-id", default=None, help="DNS record id (preferred)")
    dns_records_absent.add_argument("--name", default=None, help="Record name (required if --record-id is omitted)")
    dns_records_absent.add_argument("--type", default=None, help="Record type (required if --record-id is omitted)")
    dns_records_absent.add_argument("--content", default=None, help="Optional content/value filter (for disambiguation)")
    dns_records_absent.set_defaults(func=dns_cmd.cmd_dns_records_ensure_absent, write_capable=True)

    dns_records_export = dns_records_sub.add_parser("export", help="Export DNS records to a file (sensitive read)")
    dns_records_export.add_argument("--zone-id", required=True, help="Zone id")
    dns_records_export.add_argument("--out", default=None, help="Output file under --project-dir (required on --apply)")
    dns_records_export.add_argument("--overwrite", action="store_true", help="Allow overwriting --out")
    dns_records_export.set_defaults(func=dns_cmd.cmd_dns_records_export, write_capable=True)

    dns_records_import = dns_records_sub.add_parser("import", help="Import DNS records from a file (bulk write)")
    dns_records_import.add_argument("--zone-id", required=True, help="Zone id")
    dns_records_import.add_argument("--file", required=True, help="Import file path")
    px2 = dns_records_import.add_mutually_exclusive_group()
    px2.add_argument("--proxied", action="store_true", default=None, help="Set proxied=true for imported records")
    px2.add_argument("--no-proxied", action="store_false", dest="proxied", default=None, help="Set proxied=false for imported records")
    dns_records_import.set_defaults(func=dns_cmd.cmd_dns_records_import, write_capable=True)

    dns_scan = dns_sub.add_parser("scan", help="DNS scan (plan-first; high risk)")
    dns_scan_sub = dns_scan.add_subparsers(dest="dns_scan_cmd", required=True, parser_class=_ToolArgumentParser)
    dns_scan_trigger = dns_scan_sub.add_parser("trigger", help="Trigger a DNS scan (write)")
    dns_scan_trigger.add_argument("--zone-id", required=True, help="Zone id")
    dns_scan_trigger.set_defaults(func=dns_cmd.cmd_dns_scan_trigger, write_capable=True)
    dns_scan_review = dns_scan_sub.add_parser("review", help="Review DNS scan results (read-only)")
    dns_scan_review.add_argument("--zone-id", required=True, help="Zone id")
    dns_scan_review.set_defaults(func=dns_cmd.cmd_dns_scan_review, write_capable=False)
    dns_scan_apply = dns_scan_sub.add_parser("apply", help="Apply DNS scan results (bulk write)")
    dns_scan_apply.add_argument("--zone-id", required=True, help="Zone id")
    dns_scan_apply.add_argument("--body-json-file", default=None, help="Optional JSON body file (advanced)")
    dns_scan_apply.set_defaults(func=dns_cmd.cmd_dns_scan_apply, write_capable=True)

    dns_settings = dns_sub.add_parser("settings", help="DNS settings + Internal DNS views")
    dns_settings_sub = dns_settings.add_subparsers(dest="dns_settings_cmd", required=True, parser_class=_ToolArgumentParser)

    dns_settings_zone = dns_settings_sub.add_parser("zone", help="Zone DNS settings")
    dns_settings_zone_sub = dns_settings_zone.add_subparsers(dest="dns_settings_zone_cmd", required=True, parser_class=_ToolArgumentParser)
    dns_settings_zone_get = dns_settings_zone_sub.add_parser("get", help="Get zone DNS settings")
    dns_settings_zone_get.add_argument("--zone-id", required=True, help="Zone id")
    dns_settings_zone_get.set_defaults(func=dns_cmd.cmd_dns_settings_zone_get, write_capable=False)
    dns_settings_zone_update = dns_settings_zone_sub.add_parser("update", help="Update zone DNS settings (write)")
    dns_settings_zone_update.add_argument("--zone-id", required=True, help="Zone id")
    dns_settings_zone_update.add_argument("--body-json-file", required=True, help="JSON body file (no secrets printed)")
    dns_settings_zone_update.set_defaults(func=dns_cmd.cmd_dns_settings_zone_update, write_capable=True)

    dns_settings_account = dns_settings_sub.add_parser("account", help="Account DNS settings")
    dns_settings_account_sub = dns_settings_account.add_subparsers(dest="dns_settings_account_cmd", required=True, parser_class=_ToolArgumentParser)
    dns_settings_account_get = dns_settings_account_sub.add_parser("get", help="Get account DNS settings")
    dns_settings_account_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    dns_settings_account_get.set_defaults(func=dns_cmd.cmd_dns_settings_account_get, write_capable=False)
    dns_settings_account_update = dns_settings_account_sub.add_parser("update", help="Update account DNS settings (write)")
    dns_settings_account_update.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    dns_settings_account_update.add_argument("--body-json-file", required=True, help="JSON body file (no secrets printed)")
    dns_settings_account_update.set_defaults(func=dns_cmd.cmd_dns_settings_account_update, write_capable=True)

    dns_views = dns_settings_sub.add_parser("views", help="Internal DNS views (account-scoped)")
    dns_views_sub = dns_views.add_subparsers(dest="dns_views_cmd", required=True, parser_class=_ToolArgumentParser)
    dns_views_list = dns_views_sub.add_parser("list", help="List Internal DNS views")
    dns_views_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    dns_views_list.set_defaults(func=dns_cmd.cmd_dns_views_list, write_capable=False)
    dns_views_get = dns_views_sub.add_parser("get", help="Get one Internal DNS view")
    dns_views_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    dns_views_get.add_argument("--view-id", required=True, help="View id")
    dns_views_get.set_defaults(func=dns_cmd.cmd_dns_views_get, write_capable=False)
    dns_views_create = dns_views_sub.add_parser("create", help="Create Internal DNS view (write)")
    dns_views_create.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    dns_views_create.add_argument("--body-json-file", required=True, help="JSON body file (no secrets printed)")
    dns_views_create.set_defaults(func=dns_cmd.cmd_dns_views_create, write_capable=True)
    dns_views_update = dns_views_sub.add_parser("update", help="Update Internal DNS view (write)")
    dns_views_update.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    dns_views_update.add_argument("--view-id", required=True, help="View id")
    dns_views_update.add_argument("--body-json-file", required=True, help="JSON body file (no secrets printed)")
    dns_views_update.set_defaults(func=dns_cmd.cmd_dns_views_update, write_capable=True)
    dns_views_delete = dns_views_sub.add_parser("delete", help="Delete Internal DNS view (write)")
    dns_views_delete.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    dns_views_delete.add_argument("--view-id", required=True, help="View id")
    dns_views_delete.set_defaults(func=dns_cmd.cmd_dns_views_delete, write_capable=True)

    dnssec = dns_sub.add_parser("dnssec", help="DNSSEC (zone-scoped)")
    dnssec_sub = dnssec.add_subparsers(dest="dnssec_cmd", required=True, parser_class=_ToolArgumentParser)
    dnssec_get = dnssec_sub.add_parser("get", help="Get DNSSEC")
    dnssec_get.add_argument("--zone-id", required=True, help="Zone id")
    dnssec_get.set_defaults(func=dns_cmd.cmd_dnssec_get, write_capable=False)
    dnssec_set = dnssec_sub.add_parser("set", help="Set DNSSEC status (write)")
    dnssec_set.add_argument("--zone-id", required=True, help="Zone id")
    dnssec_set.add_argument("--body-json-file", required=True, help="JSON body file (no secrets printed)")
    dnssec_set.set_defaults(func=dns_cmd.cmd_dnssec_set, write_capable=True)
    dnssec_delete = dnssec_sub.add_parser("delete", help="Delete DNSSEC records (write)")
    dnssec_delete.add_argument("--zone-id", required=True, help="Zone id")
    dnssec_delete.set_defaults(func=dns_cmd.cmd_dnssec_delete, write_capable=True)

    secondary = dns_sub.add_parser("secondary", help="Secondary DNS (ACL/Peer/TSIG + zone transfers)")
    secondary_sub = secondary.add_subparsers(dest="secondary_cmd", required=True, parser_class=_ToolArgumentParser)

    secondary_account = secondary_sub.add_parser("account", help="Secondary DNS (account-scoped)")
    secondary_account_sub = secondary_account.add_subparsers(dest="secondary_account_cmd", required=True, parser_class=_ToolArgumentParser)

    # ACLs
    acls = secondary_account_sub.add_parser("acls", help="Secondary DNS ACLs")
    acls_sub = acls.add_subparsers(dest="secondary_acls_cmd", required=True, parser_class=_ToolArgumentParser)
    acls_list = acls_sub.add_parser("list", help="List ACLs")
    acls_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    acls_list.set_defaults(func=dns_cmd.cmd_secondary_acls_list, write_capable=False)
    acls_get = acls_sub.add_parser("get", help="Get one ACL")
    acls_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    acls_get.add_argument("--acl-id", required=True, help="ACL id")
    acls_get.set_defaults(func=dns_cmd.cmd_secondary_acls_get, write_capable=False)
    acls_create = acls_sub.add_parser("create", help="Create ACL (write)")
    acls_create.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    acls_create.add_argument("--body-json-file", required=True, help="JSON body file (no secrets printed)")
    acls_create.set_defaults(func=dns_cmd.cmd_secondary_acls_create, write_capable=True)
    acls_update = acls_sub.add_parser("update", help="Update ACL (write)")
    acls_update.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    acls_update.add_argument("--acl-id", required=True, help="ACL id")
    acls_update.add_argument("--body-json-file", required=True, help="JSON body file (no secrets printed)")
    acls_update.set_defaults(func=dns_cmd.cmd_secondary_acls_update, write_capable=True)
    acls_delete = acls_sub.add_parser("delete", help="Delete ACL (write)")
    acls_delete.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    acls_delete.add_argument("--acl-id", required=True, help="ACL id")
    acls_delete.set_defaults(func=dns_cmd.cmd_secondary_acls_delete, write_capable=True)

    # Peers
    peers = secondary_account_sub.add_parser("peers", help="Secondary DNS peers")
    peers_sub = peers.add_subparsers(dest="secondary_peers_cmd", required=True, parser_class=_ToolArgumentParser)
    peers_list = peers_sub.add_parser("list", help="List peers")
    peers_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    peers_list.set_defaults(func=dns_cmd.cmd_secondary_peers_list, write_capable=False)
    peers_get = peers_sub.add_parser("get", help="Get one peer")
    peers_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    peers_get.add_argument("--peer-id", required=True, help="Peer id")
    peers_get.set_defaults(func=dns_cmd.cmd_secondary_peers_get, write_capable=False)
    peers_create = peers_sub.add_parser("create", help="Create peer (write)")
    peers_create.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    peers_create.add_argument("--body-json-file", required=True, help="JSON body file (no secrets printed)")
    peers_create.set_defaults(func=dns_cmd.cmd_secondary_peers_create, write_capable=True)
    peers_update = peers_sub.add_parser("update", help="Update peer (write)")
    peers_update.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    peers_update.add_argument("--peer-id", required=True, help="Peer id")
    peers_update.add_argument("--body-json-file", required=True, help="JSON body file (no secrets printed)")
    peers_update.set_defaults(func=dns_cmd.cmd_secondary_peers_update, write_capable=True)
    peers_delete = peers_sub.add_parser("delete", help="Delete peer (write)")
    peers_delete.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    peers_delete.add_argument("--peer-id", required=True, help="Peer id")
    peers_delete.set_defaults(func=dns_cmd.cmd_secondary_peers_delete, write_capable=True)

    # TSIGs (secret-bearing)
    tsigs = secondary_account_sub.add_parser("tsigs", help="Secondary DNS TSIGs (secret-bearing)")
    tsigs_sub = tsigs.add_subparsers(dest="secondary_tsigs_cmd", required=True, parser_class=_ToolArgumentParser)
    tsigs_list = tsigs_sub.add_parser("list", help="List TSIGs (sensitive read; file-only)")
    tsigs_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    tsigs_list.add_argument("--out", default=None, help="Output file under --project-dir (required on --apply)")
    tsigs_list.add_argument("--overwrite", action="store_true", help="Allow overwriting --out")
    tsigs_list.set_defaults(func=dns_cmd.cmd_secondary_tsigs_list, write_capable=True)
    tsigs_get = tsigs_sub.add_parser("get", help="Get TSIG details (sensitive read; file-only)")
    tsigs_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    tsigs_get.add_argument("--tsig-id", required=True, help="TSIG id")
    tsigs_get.add_argument("--out", default=None, help="Output file under --project-dir (required on --apply)")
    tsigs_get.add_argument("--overwrite", action="store_true", help="Allow overwriting --out")
    tsigs_get.set_defaults(func=dns_cmd.cmd_secondary_tsigs_get, write_capable=True)
    tsigs_create = tsigs_sub.add_parser("create", help="Create TSIG (secret-bearing; file-only)")
    tsigs_create.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    tsigs_create.add_argument("--body-json-file", required=True, help="JSON body file (may contain secrets; never printed)")
    tsigs_create.add_argument("--out", default=None, help="Output file under --project-dir (required on --apply)")
    tsigs_create.add_argument("--overwrite", action="store_true", help="Allow overwriting --out")
    tsigs_create.set_defaults(func=dns_cmd.cmd_secondary_tsigs_create, write_capable=True)
    tsigs_update = tsigs_sub.add_parser("update", help="Update TSIG (secret-bearing; file-only)")
    tsigs_update.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    tsigs_update.add_argument("--tsig-id", required=True, help="TSIG id")
    tsigs_update.add_argument("--body-json-file", required=True, help="JSON body file (may contain secrets; never printed)")
    tsigs_update.add_argument("--out", default=None, help="Output file under --project-dir (required on --apply)")
    tsigs_update.add_argument("--overwrite", action="store_true", help="Allow overwriting --out")
    tsigs_update.set_defaults(func=dns_cmd.cmd_secondary_tsigs_update, write_capable=True)
    tsigs_delete = tsigs_sub.add_parser("delete", help="Delete TSIG (write)")
    tsigs_delete.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    tsigs_delete.add_argument("--tsig-id", required=True, help="TSIG id")
    tsigs_delete.set_defaults(func=dns_cmd.cmd_secondary_tsigs_delete, write_capable=True)

    secondary_zone = secondary_sub.add_parser("zone", help="Zone transfers (zone-scoped)")
    secondary_zone_sub = secondary_zone.add_subparsers(dest="secondary_zone_cmd", required=True, parser_class=_ToolArgumentParser)

    incoming = secondary_zone_sub.add_parser("incoming", help="Incoming zone transfers (secondary)")
    incoming_sub = incoming.add_subparsers(dest="secondary_incoming_cmd", required=True, parser_class=_ToolArgumentParser)
    incoming_get = incoming_sub.add_parser("get", help="Get incoming config")
    incoming_get.add_argument("--zone-id", required=True, help="Zone id")
    incoming_get.set_defaults(func=dns_cmd.cmd_secondary_zone_incoming_get, write_capable=False)
    incoming_create = incoming_sub.add_parser("create", help="Create incoming config (write)")
    incoming_create.add_argument("--zone-id", required=True, help="Zone id")
    incoming_create.add_argument("--body-json-file", required=True, help="JSON body file (no secrets printed)")
    incoming_create.set_defaults(func=dns_cmd.cmd_secondary_zone_incoming_create, write_capable=True)
    incoming_update = incoming_sub.add_parser("update", help="Update incoming config (write)")
    incoming_update.add_argument("--zone-id", required=True, help="Zone id")
    incoming_update.add_argument("--body-json-file", required=True, help="JSON body file (no secrets printed)")
    incoming_update.set_defaults(func=dns_cmd.cmd_secondary_zone_incoming_update, write_capable=True)
    incoming_delete = incoming_sub.add_parser("delete", help="Delete incoming config (write)")
    incoming_delete.add_argument("--zone-id", required=True, help="Zone id")
    incoming_delete.set_defaults(func=dns_cmd.cmd_secondary_zone_incoming_delete, write_capable=True)

    outgoing = secondary_zone_sub.add_parser("outgoing", help="Outgoing zone transfers (primary)")
    outgoing_sub = outgoing.add_subparsers(dest="secondary_outgoing_cmd", required=True, parser_class=_ToolArgumentParser)
    outgoing_get = outgoing_sub.add_parser("get", help="Get outgoing config")
    outgoing_get.add_argument("--zone-id", required=True, help="Zone id")
    outgoing_get.set_defaults(func=dns_cmd.cmd_secondary_zone_outgoing_get, write_capable=False)
    outgoing_create = outgoing_sub.add_parser("create", help="Create outgoing config (write)")
    outgoing_create.add_argument("--zone-id", required=True, help="Zone id")
    outgoing_create.add_argument("--body-json-file", required=True, help="JSON body file (no secrets printed)")
    outgoing_create.set_defaults(func=dns_cmd.cmd_secondary_zone_outgoing_create, write_capable=True)
    outgoing_update = outgoing_sub.add_parser("update", help="Update outgoing config (write)")
    outgoing_update.add_argument("--zone-id", required=True, help="Zone id")
    outgoing_update.add_argument("--body-json-file", required=True, help="JSON body file (no secrets printed)")
    outgoing_update.set_defaults(func=dns_cmd.cmd_secondary_zone_outgoing_update, write_capable=True)
    outgoing_delete = outgoing_sub.add_parser("delete", help="Delete outgoing config (write)")
    outgoing_delete.add_argument("--zone-id", required=True, help="Zone id")
    outgoing_delete.set_defaults(func=dns_cmd.cmd_secondary_zone_outgoing_delete, write_capable=True)

    outgoing_status = outgoing_sub.add_parser("status", help="Get outgoing transfer status (read-only)")
    outgoing_status.add_argument("--zone-id", required=True, help="Zone id")
    outgoing_status.set_defaults(func=dns_cmd.cmd_secondary_zone_outgoing_status, write_capable=False)
    outgoing_enable = outgoing_sub.add_parser("enable", help="Enable outgoing transfers (write)")
    outgoing_enable.add_argument("--zone-id", required=True, help="Zone id")
    outgoing_enable.set_defaults(func=dns_cmd.cmd_secondary_zone_outgoing_enable, write_capable=True)
    outgoing_disable = outgoing_sub.add_parser("disable", help="Disable outgoing transfers (write)")
    outgoing_disable.add_argument("--zone-id", required=True, help="Zone id")
    outgoing_disable.set_defaults(func=dns_cmd.cmd_secondary_zone_outgoing_disable, write_capable=True)
    outgoing_force_notify = outgoing_sub.add_parser("force-notify", help="Force DNS notify (write)")
    outgoing_force_notify.add_argument("--zone-id", required=True, help="Zone id")
    outgoing_force_notify.set_defaults(func=dns_cmd.cmd_secondary_zone_outgoing_force_notify, write_capable=True)
    force_axfr = secondary_zone_sub.add_parser("force-axfr", help="Force AXFR (write)")
    force_axfr.add_argument("--zone-id", required=True, help="Zone id")
    force_axfr.set_defaults(func=dns_cmd.cmd_secondary_zone_force_axfr, write_capable=True)

    d1 = sub.add_parser("d1", help="D1 databases (safe-by-default)")
    d1_sub = d1.add_subparsers(dest="d1_cmd", required=True, parser_class=_ToolArgumentParser)

    d1_databases = d1_sub.add_parser("databases", help="Databases (read-only)")
    d1_databases_sub = d1_databases.add_subparsers(dest="d1_databases_cmd", required=True, parser_class=_ToolArgumentParser)
    d1_databases_list = d1_databases_sub.add_parser("list", help="List D1 databases")
    d1_databases_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    d1_databases_list.set_defaults(func=d1_cmd.cmd_d1_databases_list, write_capable=False)
    d1_databases_get = d1_databases_sub.add_parser("get", help="Get one D1 database")
    d1_databases_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    d1_databases_get.add_argument("--database-id", required=True, help="Database id")
    d1_databases_get.set_defaults(func=d1_cmd.cmd_d1_databases_get, write_capable=False)

    d1_export = d1_sub.add_parser("export", help="Export database as SQL (sensitive read; file-only)")
    d1_export.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    d1_export.add_argument("--database-id", required=True, help="Database id")
    d1_export.add_argument("--out", default=None, help="Output file under --project-dir (required on --apply)")
    d1_export.add_argument("--overwrite", action="store_true", help="Allow overwriting --out")
    d1_export.set_defaults(func=d1_cmd.cmd_d1_export, write_capable=True)

    d1_query = d1_sub.add_parser("query", help="Query database (sensitive output; requires --yes; file-only)")
    d1_query.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    d1_query.add_argument("--database-id", required=True, help="Database id")
    d1_query.add_argument("--body-json-file", required=True, help="JSON request body file (no secrets printed)")
    d1_query.add_argument("--out", default=None, help="Output file under --project-dir (required on --apply)")
    d1_query.add_argument("--overwrite", action="store_true", help="Allow overwriting --out")
    d1_query.set_defaults(func=d1_cmd.cmd_d1_query, write_capable=True)

    queues = sub.add_parser("queues", help="Queues (safe-by-default)")
    queues_sub = queues.add_subparsers(dest="queues_cmd", required=True, parser_class=_ToolArgumentParser)
    queues_list = queues_sub.add_parser("list", help="List queues")
    queues_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    queues_list.set_defaults(func=queues_cmd.cmd_queues_list, write_capable=False)
    queues_get = queues_sub.add_parser("get", help="Get one queue")
    queues_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    queues_get.add_argument("--queue-id", required=True, help="Queue id")
    queues_get.set_defaults(func=queues_cmd.cmd_queues_get, write_capable=False)
    queues_pull = queues_sub.add_parser("pull", help="Pull queue messages (sensitive read; file-only)")
    queues_pull.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    queues_pull.add_argument("--queue-id", required=True, help="Queue id")
    queues_pull.add_argument("--out", default=None, help="Output file under --project-dir (required on --apply)")
    queues_pull.add_argument("--overwrite", action="store_true", help="Allow overwriting --out")
    queues_pull.set_defaults(func=queues_cmd.cmd_queues_pull, write_capable=True)

    r2 = sub.add_parser("r2", help="R2 storage (safe-by-default)")
    r2_sub = r2.add_subparsers(dest="r2_cmd", required=True, parser_class=_ToolArgumentParser)

    r2_buckets = r2_sub.add_parser("buckets", help="Buckets (read-only)")
    r2_buckets_sub = r2_buckets.add_subparsers(dest="r2_buckets_cmd", required=True, parser_class=_ToolArgumentParser)
    r2_buckets_list = r2_buckets_sub.add_parser("list", help="List buckets")
    r2_buckets_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    r2_buckets_list.set_defaults(func=r2_cmd.cmd_r2_buckets_list, write_capable=False)
    r2_buckets_get = r2_buckets_sub.add_parser("get", help="Get one bucket")
    r2_buckets_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    r2_buckets_get.add_argument("--bucket-name", required=True, help="Bucket name")
    r2_buckets_get.set_defaults(func=r2_cmd.cmd_r2_buckets_get, write_capable=False)

    r2_temp_creds = r2_sub.add_parser("temp-creds", help="Temporary access credentials (secret-bearing; file-only)")
    r2_temp_creds_sub = r2_temp_creds.add_subparsers(dest="r2_temp_creds_cmd", required=True, parser_class=_ToolArgumentParser)
    r2_temp_creds_create = r2_temp_creds_sub.add_parser("create", help="Create temporary access credentials (write)")
    r2_temp_creds_create.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    r2_temp_creds_create.add_argument("--bucket", required=True, help="Bucket name")
    r2_temp_creds_create.add_argument("--permission", required=True, help="Permission string (as defined by Cloudflare API)")
    r2_temp_creds_create.add_argument("--ttl-seconds", required=True, type=int, help="TTL in seconds")
    r2_temp_creds_create.add_argument("--parent-access-key-id", required=True, help="Parent access key id")
    r2_temp_creds_create.add_argument("--prefix", action="append", default=[], help="Optional prefix restriction (repeatable)")
    r2_temp_creds_create.add_argument("--object", action="append", default=[], help="Optional object restriction (repeatable)")
    r2_temp_creds_create.add_argument("--out", default=None, help="Output file under --project-dir (required on --apply)")
    r2_temp_creds_create.add_argument("--overwrite", action="store_true", help="Allow overwriting --out")
    r2_temp_creds_create.set_defaults(func=r2_cmd.cmd_r2_temp_creds_create, write_capable=True)

    custom_hostnames = sub.add_parser("custom-hostnames", help="Custom Hostnames (SSL for SaaS; sensitive output)")
    custom_hostnames_sub = custom_hostnames.add_subparsers(dest="custom_hostnames_cmd", required=True, parser_class=_ToolArgumentParser)

    custom_hostnames_list = custom_hostnames_sub.add_parser("list", help="List custom hostnames (sensitive; file-only)")
    _add_zone_id_flag(custom_hostnames_list)
    _add_query_flags(custom_hostnames_list)
    _add_out_flags(custom_hostnames_list)
    custom_hostnames_list.set_defaults(func=custom_hostnames_cmd.cmd_custom_hostnames_list, write_capable=False)

    custom_hostnames_get = custom_hostnames_sub.add_parser("get", help="Get one custom hostname (sensitive; file-only)")
    _add_zone_id_flag(custom_hostnames_get)
    custom_hostnames_get.add_argument("--custom-hostname-id", required=True, help="Custom hostname id")
    _add_query_flags(custom_hostnames_get)
    _add_out_flags(custom_hostnames_get)
    custom_hostnames_get.set_defaults(func=custom_hostnames_cmd.cmd_custom_hostnames_get, write_capable=False)

    custom_hostnames_create = custom_hostnames_sub.add_parser("create", help="Create one custom hostname (write; sensitive output)")
    _add_zone_id_flag(custom_hostnames_create)
    _add_query_flags(custom_hostnames_create)
    _add_body_flags(custom_hostnames_create, required=True)
    _add_out_flags(custom_hostnames_create)
    custom_hostnames_create.set_defaults(func=custom_hostnames_cmd.cmd_custom_hostnames_create, write_capable=True)

    custom_hostnames_update = custom_hostnames_sub.add_parser("update", help="Update one custom hostname (write; sensitive output)")
    _add_zone_id_flag(custom_hostnames_update)
    custom_hostnames_update.add_argument("--custom-hostname-id", required=True, help="Custom hostname id")
    _add_query_flags(custom_hostnames_update)
    _add_body_flags(custom_hostnames_update, required=True)
    _add_out_flags(custom_hostnames_update)
    custom_hostnames_update.set_defaults(func=custom_hostnames_cmd.cmd_custom_hostnames_update, write_capable=True)

    custom_hostnames_delete = custom_hostnames_sub.add_parser("delete", help="Delete one custom hostname (write; sensitive output)")
    _add_zone_id_flag(custom_hostnames_delete)
    custom_hostnames_delete.add_argument("--custom-hostname-id", required=True, help="Custom hostname id")
    _add_query_flags(custom_hostnames_delete)
    _add_out_flags(custom_hostnames_delete)
    custom_hostnames_delete.set_defaults(func=custom_hostnames_cmd.cmd_custom_hostnames_delete, write_capable=True)

    fallback_origin = custom_hostnames_sub.add_parser("fallback-origin", help="Fallback origin (zone-scoped)")
    fallback_origin_sub = fallback_origin.add_subparsers(dest="custom_hostnames_fallback_origin_cmd", required=True, parser_class=_ToolArgumentParser)
    fallback_origin_get = fallback_origin_sub.add_parser("get", help="Get fallback origin (sensitive; file-only)")
    _add_zone_id_flag(fallback_origin_get)
    _add_query_flags(fallback_origin_get)
    _add_out_flags(fallback_origin_get)
    fallback_origin_get.set_defaults(func=custom_hostnames_cmd.cmd_custom_hostnames_fallback_origin_get, write_capable=False)
    fallback_origin_update = fallback_origin_sub.add_parser("update", help="Update fallback origin (write; sensitive output)")
    _add_zone_id_flag(fallback_origin_update)
    _add_query_flags(fallback_origin_update)
    _add_body_flags(fallback_origin_update, required=True)
    _add_out_flags(fallback_origin_update)
    fallback_origin_update.set_defaults(func=custom_hostnames_cmd.cmd_custom_hostnames_fallback_origin_update, write_capable=True)
    fallback_origin_delete = fallback_origin_sub.add_parser("delete", help="Delete fallback origin (write; sensitive output)")
    _add_zone_id_flag(fallback_origin_delete)
    _add_query_flags(fallback_origin_delete)
    _add_out_flags(fallback_origin_delete)
    fallback_origin_delete.set_defaults(func=custom_hostnames_cmd.cmd_custom_hostnames_fallback_origin_delete, write_capable=True)

    custom_cert = custom_hostnames_sub.add_parser("cert", help="Custom hostname certificate operations (write; sensitive output)")
    custom_cert_sub = custom_cert.add_subparsers(dest="custom_hostnames_cert_cmd", required=True, parser_class=_ToolArgumentParser)
    cert_replace = custom_cert_sub.add_parser("replace", help="Replace one custom certificate (write)")
    _add_zone_id_flag(cert_replace)
    cert_replace.add_argument("--custom-hostname-id", required=True, help="Custom hostname id")
    cert_replace.add_argument("--certificate-pack-id", required=True, help="Certificate pack id")
    cert_replace.add_argument("--certificate-id", required=True, help="Certificate id")
    _add_query_flags(cert_replace)
    _add_body_flags(cert_replace, required=True)
    _add_out_flags(cert_replace)
    cert_replace.set_defaults(func=custom_hostnames_cmd.cmd_custom_hostnames_cert_replace, write_capable=True)

    cert_delete = custom_cert_sub.add_parser("delete", help="Delete one custom certificate (write)")
    _add_zone_id_flag(cert_delete)
    cert_delete.add_argument("--custom-hostname-id", required=True, help="Custom hostname id")
    cert_delete.add_argument("--certificate-pack-id", required=True, help="Certificate pack id")
    cert_delete.add_argument("--certificate-id", required=True, help="Certificate id")
    _add_query_flags(cert_delete)
    _add_out_flags(cert_delete)
    cert_delete.set_defaults(func=custom_hostnames_cmd.cmd_custom_hostnames_cert_delete, write_capable=True)

    ssl_tls = sub.add_parser("ssl-tls", help="SSL/TLS (Phase 7E-1; sensitive output)")
    ssl_tls_sub = ssl_tls.add_subparsers(dest="ssl_tls_cmd", required=True, parser_class=_ToolArgumentParser)

    automatic_mode = ssl_tls_sub.add_parser("automatic-mode", help="Automatic SSL/TLS enrollment (zone-scoped)")
    automatic_mode_sub = automatic_mode.add_subparsers(dest="ssl_tls_automatic_mode_cmd", required=True, parser_class=_ToolArgumentParser)
    automatic_mode_get = automatic_mode_sub.add_parser("get", help="Get enrollment status (sensitive; file-only)")
    _add_zone_id_flag(automatic_mode_get)
    _add_query_flags(automatic_mode_get)
    _add_out_flags(automatic_mode_get)
    automatic_mode_get.set_defaults(func=ssl_tls_cmd.cmd_ssl_automatic_mode_get, write_capable=False)
    automatic_mode_set = automatic_mode_sub.add_parser("set", help="Set enrollment status (write; sensitive output)")
    _add_zone_id_flag(automatic_mode_set)
    _add_query_flags(automatic_mode_set)
    _add_body_flags(automatic_mode_set, required=True)
    _add_out_flags(automatic_mode_set)
    automatic_mode_set.set_defaults(func=ssl_tls_cmd.cmd_ssl_automatic_mode_set, write_capable=True)

    analyze = ssl_tls_sub.add_parser("analyze", help="Analyze certificate (read-like POST; sensitive output)")
    _add_zone_id_flag(analyze)
    _add_query_flags(analyze)
    _add_body_flags(analyze, required=False)
    _add_out_flags(analyze)
    analyze.set_defaults(func=ssl_tls_cmd.cmd_ssl_analyze, write_capable=False)

    recommendation = ssl_tls_sub.add_parser("recommendation", help="Get SSL recommendation (sensitive; file-only)")
    _add_zone_id_flag(recommendation)
    _add_query_flags(recommendation)
    _add_out_flags(recommendation)
    recommendation.set_defaults(func=ssl_tls_cmd.cmd_ssl_recommendation, write_capable=False)

    universal_ssl = ssl_tls_sub.add_parser("universal-ssl", help="Universal SSL settings (zone-scoped)")
    universal_ssl_sub = universal_ssl.add_subparsers(dest="ssl_tls_universal_ssl_cmd", required=True, parser_class=_ToolArgumentParser)
    universal_ssl_get = universal_ssl_sub.add_parser("get", help="Get Universal SSL settings (sensitive; file-only)")
    _add_zone_id_flag(universal_ssl_get)
    _add_query_flags(universal_ssl_get)
    _add_out_flags(universal_ssl_get)
    universal_ssl_get.set_defaults(func=ssl_tls_cmd.cmd_universal_ssl_get, write_capable=False)
    universal_ssl_set = universal_ssl_sub.add_parser("set", help="Update Universal SSL settings (write; sensitive output)")
    _add_zone_id_flag(universal_ssl_set)
    _add_query_flags(universal_ssl_set)
    _add_body_flags(universal_ssl_set, required=True)
    _add_out_flags(universal_ssl_set)
    universal_ssl_set.set_defaults(func=ssl_tls_cmd.cmd_universal_ssl_set, write_capable=True)

    verification = ssl_tls_sub.add_parser("verification", help="Verification (zone-scoped)")
    verification_sub = verification.add_subparsers(dest="ssl_tls_verification_cmd", required=True, parser_class=_ToolArgumentParser)
    verification_get = verification_sub.add_parser("get", help="Get SSL verification info (sensitive; file-only)")
    _add_zone_id_flag(verification_get)
    _add_query_flags(verification_get)
    _add_out_flags(verification_get)
    verification_get.set_defaults(func=ssl_tls_cmd.cmd_ssl_verification_get, write_capable=False)
    verification_update = verification_sub.add_parser("update", help="Update SSL verification (write; sensitive output)")
    _add_zone_id_flag(verification_update)
    verification_update.add_argument("--certificate-pack-id", required=True, help="Certificate pack id")
    _add_query_flags(verification_update)
    _add_body_flags(verification_update, required=True)
    _add_out_flags(verification_update)
    verification_update.set_defaults(func=ssl_tls_cmd.cmd_ssl_verification_update, write_capable=True)

    certificate_packs = ssl_tls_sub.add_parser("certificate-packs", help="Certificate packs (zone-scoped)")
    certificate_packs_sub = certificate_packs.add_subparsers(dest="ssl_tls_certificate_packs_cmd", required=True, parser_class=_ToolArgumentParser)
    certificate_packs_list = certificate_packs_sub.add_parser("list", help="List certificate packs (sensitive; file-only)")
    _add_zone_id_flag(certificate_packs_list)
    _add_query_flags(certificate_packs_list)
    _add_out_flags(certificate_packs_list)
    certificate_packs_list.set_defaults(func=ssl_tls_cmd.cmd_certificate_packs_list, write_capable=False)
    certificate_packs_get = certificate_packs_sub.add_parser("get", help="Get one certificate pack (sensitive; file-only)")
    _add_zone_id_flag(certificate_packs_get)
    certificate_packs_get.add_argument("--certificate-pack-id", required=True, help="Certificate pack id")
    _add_query_flags(certificate_packs_get)
    _add_out_flags(certificate_packs_get)
    certificate_packs_get.set_defaults(func=ssl_tls_cmd.cmd_certificate_packs_get, write_capable=False)
    certificate_packs_quota = certificate_packs_sub.add_parser("quota", help="Get certificate pack quotas (sensitive; file-only)")
    _add_zone_id_flag(certificate_packs_quota)
    _add_query_flags(certificate_packs_quota)
    _add_out_flags(certificate_packs_quota)
    certificate_packs_quota.set_defaults(func=ssl_tls_cmd.cmd_certificate_packs_quota, write_capable=False)
    certificate_packs_order = certificate_packs_sub.add_parser("order", help="Order a certificate pack (write; sensitive output)")
    _add_zone_id_flag(certificate_packs_order)
    _add_query_flags(certificate_packs_order)
    _add_body_flags(certificate_packs_order, required=True)
    _add_out_flags(certificate_packs_order)
    certificate_packs_order.set_defaults(func=ssl_tls_cmd.cmd_certificate_packs_order, write_capable=True)
    certificate_packs_update = certificate_packs_sub.add_parser("update", help="Update one certificate pack (write; sensitive output)")
    _add_zone_id_flag(certificate_packs_update)
    certificate_packs_update.add_argument("--certificate-pack-id", required=True, help="Certificate pack id")
    _add_query_flags(certificate_packs_update)
    _add_body_flags(certificate_packs_update, required=True)
    _add_out_flags(certificate_packs_update)
    certificate_packs_update.set_defaults(func=ssl_tls_cmd.cmd_certificate_packs_update, write_capable=True)
    certificate_packs_restart = certificate_packs_sub.add_parser(
        "restart", help="Restart certificate pack validation (write; sensitive output)"
    )
    _add_zone_id_flag(certificate_packs_restart)
    certificate_packs_restart.add_argument("--certificate-pack-id", required=True, help="Certificate pack id")
    _add_query_flags(certificate_packs_restart)
    _add_body_flags(certificate_packs_restart, required=True)
    _add_out_flags(certificate_packs_restart)
    certificate_packs_restart.set_defaults(func=ssl_tls_cmd.cmd_certificate_packs_restart, write_capable=True)
    certificate_packs_delete = certificate_packs_sub.add_parser("delete", help="Delete one certificate pack (write; sensitive output)")
    _add_zone_id_flag(certificate_packs_delete)
    certificate_packs_delete.add_argument("--certificate-pack-id", required=True, help="Certificate pack id")
    _add_query_flags(certificate_packs_delete)
    _add_out_flags(certificate_packs_delete)
    certificate_packs_delete.set_defaults(func=ssl_tls_cmd.cmd_certificate_packs_delete, write_capable=True)

    cache = sub.add_parser("cache", help="Cache management")
    cache_sub = cache.add_subparsers(dest="cache_cmd", required=True, parser_class=_ToolArgumentParser)
    cache_purge = cache_sub.add_parser("purge", help="Purge zone cache (write)")
    _add_zone_id_flag(cache_purge)
    _add_query_flags(cache_purge)
    _add_body_flags(cache_purge, required=True)
    cache_purge.set_defaults(func=cache_cmd.cmd_cache_purge, write_capable=True)

    registrar = sub.add_parser("registrar", help="Registrar (Phase 7E-4; PII-safe file-only output)")
    registrar_sub = registrar.add_subparsers(dest="registrar_cmd", required=True, parser_class=_ToolArgumentParser)
    registrar_domains = registrar_sub.add_parser("domains", help="Domains (account-scoped; sensitive file-only output)")
    registrar_domains_sub = registrar_domains.add_subparsers(dest="registrar_domains_cmd", required=True, parser_class=_ToolArgumentParser)

    registrar_domains_list = registrar_domains_sub.add_parser("list", help="List domains (PII-safe; file-only)")
    _add_account_id_flag(registrar_domains_list)
    _add_query_flags(registrar_domains_list)
    _add_out_flags(registrar_domains_list)
    registrar_domains_list.set_defaults(func=registrar_cmd.cmd_registrar_domains_list, write_capable=False)

    registrar_domains_get = registrar_domains_sub.add_parser("get", help="Get one domain (PII-safe; file-only)")
    _add_account_id_flag(registrar_domains_get)
    registrar_domains_get.add_argument("--domain-name", required=True, help="Domain name")
    _add_query_flags(registrar_domains_get)
    _add_out_flags(registrar_domains_get)
    registrar_domains_get.set_defaults(func=registrar_cmd.cmd_registrar_domains_get, write_capable=False)

    registrar_domains_update = registrar_domains_sub.add_parser("update", help="Update one domain (write; PII-safe file-only output)")
    _add_account_id_flag(registrar_domains_update)
    registrar_domains_update.add_argument("--domain-name", required=True, help="Domain name")
    _add_query_flags(registrar_domains_update)
    _add_body_flags(registrar_domains_update, required=True)
    _add_out_flags(registrar_domains_update)
    registrar_domains_update.set_defaults(func=registrar_cmd.cmd_registrar_domains_update, write_capable=True)

    turnstile = sub.add_parser("turnstile", help="Turnstile (Phase 7E-5; sensitive output)")
    turnstile_sub = turnstile.add_subparsers(dest="turnstile_cmd", required=True, parser_class=_ToolArgumentParser)

    turnstile_widgets = turnstile_sub.add_parser("widgets", help="Widgets (account-scoped)")
    turnstile_widgets_sub = turnstile_widgets.add_subparsers(dest="turnstile_widgets_cmd", required=True, parser_class=_ToolArgumentParser)

    turnstile_widgets_list = turnstile_widgets_sub.add_parser("list", help="List widgets (sensitive; file-only)")
    _add_account_id_flag(turnstile_widgets_list)
    _add_query_flags(turnstile_widgets_list)
    _add_out_flags(turnstile_widgets_list)
    turnstile_widgets_list.set_defaults(func=turnstile_cmd.cmd_turnstile_widgets_list, write_capable=False)

    turnstile_widgets_get = turnstile_widgets_sub.add_parser("get", help="Get one widget (sensitive; file-only)")
    _add_account_id_flag(turnstile_widgets_get)
    turnstile_widgets_get.add_argument("--sitekey", required=True, help="Widget site key")
    _add_query_flags(turnstile_widgets_get)
    _add_out_flags(turnstile_widgets_get)
    turnstile_widgets_get.set_defaults(func=turnstile_cmd.cmd_turnstile_widgets_get, write_capable=False)

    turnstile_widgets_create = turnstile_widgets_sub.add_parser("create", help="Create one widget (secret-bearing; file-only)")
    _add_account_id_flag(turnstile_widgets_create)
    _add_query_flags(turnstile_widgets_create)
    _add_body_flags(turnstile_widgets_create, required=True)
    _add_out_flags(turnstile_widgets_create)
    turnstile_widgets_create.set_defaults(func=turnstile_cmd.cmd_turnstile_widgets_create, write_capable=True)

    turnstile_widgets_update = turnstile_widgets_sub.add_parser("update", help="Update one widget (write; sensitive output)")
    _add_account_id_flag(turnstile_widgets_update)
    turnstile_widgets_update.add_argument("--sitekey", required=True, help="Widget site key")
    _add_query_flags(turnstile_widgets_update)
    _add_body_flags(turnstile_widgets_update, required=True)
    _add_out_flags(turnstile_widgets_update)
    turnstile_widgets_update.set_defaults(func=turnstile_cmd.cmd_turnstile_widgets_update, write_capable=True)

    turnstile_widgets_delete = turnstile_widgets_sub.add_parser("delete", help="Delete one widget (write; sensitive output)")
    _add_account_id_flag(turnstile_widgets_delete)
    turnstile_widgets_delete.add_argument("--sitekey", required=True, help="Widget site key")
    _add_query_flags(turnstile_widgets_delete)
    _add_out_flags(turnstile_widgets_delete)
    turnstile_widgets_delete.set_defaults(func=turnstile_cmd.cmd_turnstile_widgets_delete, write_capable=True)

    turnstile_widgets_rotate_secret = turnstile_widgets_sub.add_parser(
        "rotate-secret", help="Rotate widget secret (secret-bearing; file-only)"
    )
    _add_account_id_flag(turnstile_widgets_rotate_secret)
    turnstile_widgets_rotate_secret.add_argument("--sitekey", required=True, help="Widget site key")
    _add_query_flags(turnstile_widgets_rotate_secret)
    _add_out_flags(turnstile_widgets_rotate_secret)
    turnstile_widgets_rotate_secret.set_defaults(func=turnstile_cmd.cmd_turnstile_widgets_rotate_secret, write_capable=True)

    email_routing = sub.add_parser("email-routing", help="Email Routing (Phase 7E-6; sensitive; file-only)")
    email_routing_sub = email_routing.add_subparsers(dest="email_routing_cmd", required=True, parser_class=_ToolArgumentParser)

    # Destination addresses (account-scoped)
    er_addresses = email_routing_sub.add_parser("addresses", help="Destination addresses (account-scoped; sensitive; file-only)")
    er_addresses_sub = er_addresses.add_subparsers(dest="email_routing_addresses_cmd", required=True, parser_class=_ToolArgumentParser)

    er_addresses_list = er_addresses_sub.add_parser("list", help="List destination addresses (sensitive; file-only)")
    _add_account_id_flag(er_addresses_list)
    _add_query_flags(er_addresses_list)
    _add_out_flags(er_addresses_list)
    er_addresses_list.set_defaults(func=email_routing_cmd.cmd_email_routing_addresses_list, write_capable=False)

    er_addresses_get = er_addresses_sub.add_parser("get", help="Get one destination address (sensitive; file-only)")
    _add_account_id_flag(er_addresses_get)
    er_addresses_get.add_argument("--destination-address-identifier", required=True, help="Destination address identifier")
    _add_query_flags(er_addresses_get)
    _add_out_flags(er_addresses_get)
    er_addresses_get.set_defaults(func=email_routing_cmd.cmd_email_routing_addresses_get, write_capable=False)

    er_addresses_create = er_addresses_sub.add_parser("create", help="Create a destination address (write; sensitive; file-only)")
    _add_account_id_flag(er_addresses_create)
    _add_query_flags(er_addresses_create)
    _add_body_flags(er_addresses_create, required=True)
    _add_out_flags(er_addresses_create)
    er_addresses_create.set_defaults(func=email_routing_cmd.cmd_email_routing_addresses_create, write_capable=True)

    er_addresses_delete = er_addresses_sub.add_parser("delete", help="Delete a destination address (write; sensitive; file-only)")
    _add_account_id_flag(er_addresses_delete)
    er_addresses_delete.add_argument("--destination-address-identifier", required=True, help="Destination address identifier")
    _add_query_flags(er_addresses_delete)
    _add_out_flags(er_addresses_delete)
    er_addresses_delete.set_defaults(func=email_routing_cmd.cmd_email_routing_addresses_delete, write_capable=True)

    # Settings (zone-scoped)
    er_settings = email_routing_sub.add_parser("settings", help="Email Routing settings (zone-scoped; sensitive; file-only)")
    er_settings_sub = er_settings.add_subparsers(dest="email_routing_settings_cmd", required=True, parser_class=_ToolArgumentParser)

    er_settings_get = er_settings_sub.add_parser("get", help="Get Email Routing settings (sensitive; file-only)")
    _add_zone_id_flag(er_settings_get)
    _add_query_flags(er_settings_get)
    _add_out_flags(er_settings_get)
    er_settings_get.set_defaults(func=email_routing_cmd.cmd_email_routing_settings_get, write_capable=False)

    er_settings_enable = er_settings_sub.add_parser("enable", help="Enable Email Routing (write; sensitive; file-only)")
    _add_zone_id_flag(er_settings_enable)
    _add_query_flags(er_settings_enable)
    _add_out_flags(er_settings_enable)
    er_settings_enable.set_defaults(func=email_routing_cmd.cmd_email_routing_settings_enable, write_capable=True)

    er_settings_disable = er_settings_sub.add_parser("disable", help="Disable Email Routing (write; sensitive; file-only)")
    _add_zone_id_flag(er_settings_disable)
    _add_query_flags(er_settings_disable)
    _add_out_flags(er_settings_disable)
    er_settings_disable.set_defaults(func=email_routing_cmd.cmd_email_routing_settings_disable, write_capable=True)

    # DNS (zone-scoped)
    er_dns = email_routing_sub.add_parser("dns", help="Email Routing DNS settings (zone-scoped; sensitive; file-only)")
    er_dns_sub = er_dns.add_subparsers(dest="email_routing_dns_cmd", required=True, parser_class=_ToolArgumentParser)

    er_dns_get = er_dns_sub.add_parser("get", help="Get Email Routing DNS settings (sensitive; file-only)")
    _add_zone_id_flag(er_dns_get)
    _add_query_flags(er_dns_get)
    _add_out_flags(er_dns_get)
    er_dns_get.set_defaults(func=email_routing_cmd.cmd_email_routing_dns_get, write_capable=False)

    er_dns_enable = er_dns_sub.add_parser("enable", help="Enable Email Routing DNS (write; sensitive; file-only)")
    _add_zone_id_flag(er_dns_enable)
    _add_query_flags(er_dns_enable)
    _add_out_flags(er_dns_enable)
    er_dns_enable.set_defaults(func=email_routing_cmd.cmd_email_routing_dns_enable, write_capable=True)

    er_dns_disable = er_dns_sub.add_parser("disable", help="Disable Email Routing DNS (write; sensitive; file-only)")
    _add_zone_id_flag(er_dns_disable)
    _add_query_flags(er_dns_disable)
    _add_out_flags(er_dns_disable)
    er_dns_disable.set_defaults(func=email_routing_cmd.cmd_email_routing_dns_disable, write_capable=True)

    er_dns_unlock = er_dns_sub.add_parser("unlock", help="Unlock Email Routing DNS (write; sensitive; file-only)")
    _add_zone_id_flag(er_dns_unlock)
    _add_query_flags(er_dns_unlock)
    _add_out_flags(er_dns_unlock)
    er_dns_unlock.set_defaults(func=email_routing_cmd.cmd_email_routing_dns_unlock, write_capable=True)

    # Routing rules (zone-scoped)
    er_rules = email_routing_sub.add_parser("rules", help="Routing rules (zone-scoped; sensitive; file-only)")
    er_rules_sub = er_rules.add_subparsers(dest="email_routing_rules_cmd", required=True, parser_class=_ToolArgumentParser)

    er_rules_list = er_rules_sub.add_parser("list", help="List routing rules (sensitive; file-only)")
    _add_zone_id_flag(er_rules_list)
    _add_query_flags(er_rules_list)
    _add_out_flags(er_rules_list)
    er_rules_list.set_defaults(func=email_routing_cmd.cmd_email_routing_rules_list, write_capable=False)

    er_rules_get = er_rules_sub.add_parser("get", help="Get one routing rule (sensitive; file-only)")
    _add_zone_id_flag(er_rules_get)
    er_rules_get.add_argument("--rule-identifier", required=True, help="Rule identifier")
    _add_query_flags(er_rules_get)
    _add_out_flags(er_rules_get)
    er_rules_get.set_defaults(func=email_routing_cmd.cmd_email_routing_rules_get, write_capable=False)

    er_rules_create = er_rules_sub.add_parser("create", help="Create a routing rule (write; sensitive; file-only)")
    _add_zone_id_flag(er_rules_create)
    _add_query_flags(er_rules_create)
    _add_body_flags(er_rules_create, required=True)
    _add_out_flags(er_rules_create)
    er_rules_create.set_defaults(func=email_routing_cmd.cmd_email_routing_rules_create, write_capable=True)

    er_rules_update = er_rules_sub.add_parser("update", help="Update a routing rule (write; sensitive; file-only)")
    _add_zone_id_flag(er_rules_update)
    er_rules_update.add_argument("--rule-identifier", required=True, help="Rule identifier")
    _add_query_flags(er_rules_update)
    _add_body_flags(er_rules_update, required=True)
    _add_out_flags(er_rules_update)
    er_rules_update.set_defaults(func=email_routing_cmd.cmd_email_routing_rules_update, write_capable=True)

    er_rules_delete = er_rules_sub.add_parser("delete", help="Delete a routing rule (write; sensitive; file-only)")
    _add_zone_id_flag(er_rules_delete)
    er_rules_delete.add_argument("--rule-identifier", required=True, help="Rule identifier")
    _add_query_flags(er_rules_delete)
    _add_out_flags(er_rules_delete)
    er_rules_delete.set_defaults(func=email_routing_cmd.cmd_email_routing_rules_delete, write_capable=True)

    er_catch_all = er_rules_sub.add_parser("catch-all", help="Catch-all routing rule (zone-scoped; sensitive; file-only)")
    er_catch_all_sub = er_catch_all.add_subparsers(dest="email_routing_catch_all_cmd", required=True, parser_class=_ToolArgumentParser)

    er_catch_all_get = er_catch_all_sub.add_parser("get", help="Get catch-all routing rule (sensitive; file-only)")
    _add_zone_id_flag(er_catch_all_get)
    _add_query_flags(er_catch_all_get)
    _add_out_flags(er_catch_all_get)
    er_catch_all_get.set_defaults(func=email_routing_cmd.cmd_email_routing_rules_catch_all_get, write_capable=False)

    er_catch_all_update = er_catch_all_sub.add_parser("update", help="Update catch-all routing rule (write; sensitive; file-only)")
    _add_zone_id_flag(er_catch_all_update)
    _add_query_flags(er_catch_all_update)
    _add_body_flags(er_catch_all_update, required=True)
    _add_out_flags(er_catch_all_update)
    er_catch_all_update.set_defaults(func=email_routing_cmd.cmd_email_routing_rules_catch_all_update, write_capable=True)

    load_balancers = sub.add_parser("load-balancers", help="Load Balancing (Phase 7E-2; sensitive output)")
    load_balancers_sub = load_balancers.add_subparsers(dest="load_balancers_cmd", required=True, parser_class=_ToolArgumentParser)

    lb_monitors = load_balancers_sub.add_parser("monitors", help="Monitors (account-scoped)")
    lb_monitors_sub = lb_monitors.add_subparsers(dest="load_balancers_monitors_cmd", required=True, parser_class=_ToolArgumentParser)
    lb_monitors_list = lb_monitors_sub.add_parser("list", help="List monitors (sensitive; file-only)")
    _add_account_id_flag(lb_monitors_list)
    _add_query_flags(lb_monitors_list)
    _add_out_flags(lb_monitors_list)
    lb_monitors_list.set_defaults(func=load_balancers_cmd.cmd_load_balancers_monitors_list, write_capable=False)
    lb_monitors_get = lb_monitors_sub.add_parser("get", help="Get one monitor (sensitive; file-only)")
    _add_account_id_flag(lb_monitors_get)
    lb_monitors_get.add_argument("--monitor-id", required=True, help="Monitor id")
    _add_query_flags(lb_monitors_get)
    _add_out_flags(lb_monitors_get)
    lb_monitors_get.set_defaults(func=load_balancers_cmd.cmd_load_balancers_monitors_get, write_capable=False)
    lb_monitors_create = lb_monitors_sub.add_parser("create", help="Create one monitor (write; sensitive output)")
    _add_account_id_flag(lb_monitors_create)
    _add_query_flags(lb_monitors_create)
    _add_body_flags(lb_monitors_create, required=True)
    _add_out_flags(lb_monitors_create)
    lb_monitors_create.set_defaults(func=load_balancers_cmd.cmd_load_balancers_monitors_create, write_capable=True)
    lb_monitors_update = lb_monitors_sub.add_parser("update", help="Update one monitor (write; sensitive output)")
    _add_account_id_flag(lb_monitors_update)
    lb_monitors_update.add_argument("--monitor-id", required=True, help="Monitor id")
    _add_query_flags(lb_monitors_update)
    _add_body_flags(lb_monitors_update, required=True)
    _add_out_flags(lb_monitors_update)
    lb_monitors_update.set_defaults(func=load_balancers_cmd.cmd_load_balancers_monitors_update, write_capable=True)
    lb_monitors_patch = lb_monitors_sub.add_parser("patch", help="Patch one monitor (write; sensitive output)")
    _add_account_id_flag(lb_monitors_patch)
    lb_monitors_patch.add_argument("--monitor-id", required=True, help="Monitor id")
    _add_query_flags(lb_monitors_patch)
    _add_body_flags(lb_monitors_patch, required=True)
    _add_out_flags(lb_monitors_patch)
    lb_monitors_patch.set_defaults(func=load_balancers_cmd.cmd_load_balancers_monitors_patch, write_capable=True)
    lb_monitors_delete = lb_monitors_sub.add_parser("delete", help="Delete one monitor (write; sensitive output)")
    _add_account_id_flag(lb_monitors_delete)
    lb_monitors_delete.add_argument("--monitor-id", required=True, help="Monitor id")
    _add_query_flags(lb_monitors_delete)
    _add_out_flags(lb_monitors_delete)
    lb_monitors_delete.set_defaults(func=load_balancers_cmd.cmd_load_balancers_monitors_delete, write_capable=True)
    lb_monitors_preview = lb_monitors_sub.add_parser("preview", help="Preview one monitor (read-like POST; sensitive output)")
    _add_account_id_flag(lb_monitors_preview)
    lb_monitors_preview.add_argument("--monitor-id", required=True, help="Monitor id")
    _add_query_flags(lb_monitors_preview)
    _add_body_flags(lb_monitors_preview, required=False)
    _add_out_flags(lb_monitors_preview)
    lb_monitors_preview.set_defaults(func=load_balancers_cmd.cmd_load_balancers_monitors_preview, write_capable=False)
    lb_monitors_references = lb_monitors_sub.add_parser("references", help="List references for one monitor (sensitive; file-only)")
    _add_account_id_flag(lb_monitors_references)
    lb_monitors_references.add_argument("--monitor-id", required=True, help="Monitor id")
    _add_query_flags(lb_monitors_references)
    _add_out_flags(lb_monitors_references)
    lb_monitors_references.set_defaults(func=load_balancers_cmd.cmd_load_balancers_monitors_references, write_capable=False)

    lb_pools = load_balancers_sub.add_parser("pools", help="Pools (account-scoped)")
    lb_pools_sub = lb_pools.add_subparsers(dest="load_balancers_pools_cmd", required=True, parser_class=_ToolArgumentParser)
    lb_pools_list = lb_pools_sub.add_parser("list", help="List pools (sensitive; file-only)")
    _add_account_id_flag(lb_pools_list)
    _add_query_flags(lb_pools_list)
    _add_out_flags(lb_pools_list)
    lb_pools_list.set_defaults(func=load_balancers_cmd.cmd_load_balancers_pools_list, write_capable=False)
    lb_pools_get = lb_pools_sub.add_parser("get", help="Get one pool (sensitive; file-only)")
    _add_account_id_flag(lb_pools_get)
    lb_pools_get.add_argument("--pool-id", required=True, help="Pool id")
    _add_query_flags(lb_pools_get)
    _add_out_flags(lb_pools_get)
    lb_pools_get.set_defaults(func=load_balancers_cmd.cmd_load_balancers_pools_get, write_capable=False)
    lb_pools_create = lb_pools_sub.add_parser("create", help="Create one pool (write; sensitive output)")
    _add_account_id_flag(lb_pools_create)
    _add_query_flags(lb_pools_create)
    _add_body_flags(lb_pools_create, required=True)
    _add_out_flags(lb_pools_create)
    lb_pools_create.set_defaults(func=load_balancers_cmd.cmd_load_balancers_pools_create, write_capable=True)
    lb_pools_update = lb_pools_sub.add_parser("update", help="Update one pool (write; sensitive output)")
    _add_account_id_flag(lb_pools_update)
    lb_pools_update.add_argument("--pool-id", required=True, help="Pool id")
    _add_query_flags(lb_pools_update)
    _add_body_flags(lb_pools_update, required=True)
    _add_out_flags(lb_pools_update)
    lb_pools_update.set_defaults(func=load_balancers_cmd.cmd_load_balancers_pools_update, write_capable=True)
    lb_pools_patch = lb_pools_sub.add_parser("patch", help="Patch one pool (write; sensitive output)")
    _add_account_id_flag(lb_pools_patch)
    lb_pools_patch.add_argument("--pool-id", required=True, help="Pool id")
    _add_query_flags(lb_pools_patch)
    _add_body_flags(lb_pools_patch, required=True)
    _add_out_flags(lb_pools_patch)
    lb_pools_patch.set_defaults(func=load_balancers_cmd.cmd_load_balancers_pools_patch, write_capable=True)
    lb_pools_patch_all = lb_pools_sub.add_parser("patch-all", help="Patch multiple pools (write; sensitive output)")
    _add_account_id_flag(lb_pools_patch_all)
    _add_query_flags(lb_pools_patch_all)
    _add_body_flags(lb_pools_patch_all, required=True)
    _add_out_flags(lb_pools_patch_all)
    lb_pools_patch_all.set_defaults(func=load_balancers_cmd.cmd_load_balancers_pools_patch_all, write_capable=True)
    lb_pools_delete = lb_pools_sub.add_parser("delete", help="Delete one pool (write; sensitive output)")
    _add_account_id_flag(lb_pools_delete)
    lb_pools_delete.add_argument("--pool-id", required=True, help="Pool id")
    _add_query_flags(lb_pools_delete)
    _add_out_flags(lb_pools_delete)
    lb_pools_delete.set_defaults(func=load_balancers_cmd.cmd_load_balancers_pools_delete, write_capable=True)
    lb_pools_health = lb_pools_sub.add_parser("health", help="Get pool health details (sensitive; file-only)")
    _add_account_id_flag(lb_pools_health)
    lb_pools_health.add_argument("--pool-id", required=True, help="Pool id")
    _add_query_flags(lb_pools_health)
    _add_out_flags(lb_pools_health)
    lb_pools_health.set_defaults(func=load_balancers_cmd.cmd_load_balancers_pools_health, write_capable=False)
    lb_pools_preview = lb_pools_sub.add_parser("preview", help="Preview one pool (read-like POST; sensitive output)")
    _add_account_id_flag(lb_pools_preview)
    lb_pools_preview.add_argument("--pool-id", required=True, help="Pool id")
    _add_query_flags(lb_pools_preview)
    _add_body_flags(lb_pools_preview, required=False)
    _add_out_flags(lb_pools_preview)
    lb_pools_preview.set_defaults(func=load_balancers_cmd.cmd_load_balancers_pools_preview, write_capable=False)
    lb_pools_references = lb_pools_sub.add_parser("references", help="List references for one pool (sensitive; file-only)")
    _add_account_id_flag(lb_pools_references)
    lb_pools_references.add_argument("--pool-id", required=True, help="Pool id")
    _add_query_flags(lb_pools_references)
    _add_out_flags(lb_pools_references)
    lb_pools_references.set_defaults(func=load_balancers_cmd.cmd_load_balancers_pools_references, write_capable=False)

    lb_monitor_groups = load_balancers_sub.add_parser("monitor-groups", help="Monitor groups (account-scoped)")
    lb_monitor_groups_sub = lb_monitor_groups.add_subparsers(dest="load_balancers_monitor_groups_cmd", required=True, parser_class=_ToolArgumentParser)
    lb_monitor_groups_list = lb_monitor_groups_sub.add_parser("list", help="List monitor groups (sensitive; file-only)")
    _add_account_id_flag(lb_monitor_groups_list)
    _add_query_flags(lb_monitor_groups_list)
    _add_out_flags(lb_monitor_groups_list)
    lb_monitor_groups_list.set_defaults(func=load_balancers_cmd.cmd_load_balancers_monitor_groups_list, write_capable=False)
    lb_monitor_groups_get = lb_monitor_groups_sub.add_parser("get", help="Get one monitor group (sensitive; file-only)")
    _add_account_id_flag(lb_monitor_groups_get)
    lb_monitor_groups_get.add_argument("--monitor-group-id", required=True, help="Monitor group id")
    _add_query_flags(lb_monitor_groups_get)
    _add_out_flags(lb_monitor_groups_get)
    lb_monitor_groups_get.set_defaults(func=load_balancers_cmd.cmd_load_balancers_monitor_groups_get, write_capable=False)
    lb_monitor_groups_create = lb_monitor_groups_sub.add_parser("create", help="Create one monitor group (write; sensitive output)")
    _add_account_id_flag(lb_monitor_groups_create)
    _add_query_flags(lb_monitor_groups_create)
    _add_body_flags(lb_monitor_groups_create, required=True)
    _add_out_flags(lb_monitor_groups_create)
    lb_monitor_groups_create.set_defaults(func=load_balancers_cmd.cmd_load_balancers_monitor_groups_create, write_capable=True)
    lb_monitor_groups_update = lb_monitor_groups_sub.add_parser("update", help="Update one monitor group (write; sensitive output)")
    _add_account_id_flag(lb_monitor_groups_update)
    lb_monitor_groups_update.add_argument("--monitor-group-id", required=True, help="Monitor group id")
    _add_query_flags(lb_monitor_groups_update)
    _add_body_flags(lb_monitor_groups_update, required=True)
    _add_out_flags(lb_monitor_groups_update)
    lb_monitor_groups_update.set_defaults(func=load_balancers_cmd.cmd_load_balancers_monitor_groups_update, write_capable=True)
    lb_monitor_groups_patch = lb_monitor_groups_sub.add_parser("patch", help="Patch one monitor group (write; sensitive output)")
    _add_account_id_flag(lb_monitor_groups_patch)
    lb_monitor_groups_patch.add_argument("--monitor-group-id", required=True, help="Monitor group id")
    _add_query_flags(lb_monitor_groups_patch)
    _add_body_flags(lb_monitor_groups_patch, required=True)
    _add_out_flags(lb_monitor_groups_patch)
    lb_monitor_groups_patch.set_defaults(func=load_balancers_cmd.cmd_load_balancers_monitor_groups_patch, write_capable=True)
    lb_monitor_groups_delete = lb_monitor_groups_sub.add_parser("delete", help="Delete one monitor group (write; sensitive output)")
    _add_account_id_flag(lb_monitor_groups_delete)
    lb_monitor_groups_delete.add_argument("--monitor-group-id", required=True, help="Monitor group id")
    _add_query_flags(lb_monitor_groups_delete)
    _add_out_flags(lb_monitor_groups_delete)
    lb_monitor_groups_delete.set_defaults(func=load_balancers_cmd.cmd_load_balancers_monitor_groups_delete, write_capable=True)
    lb_monitor_groups_references = lb_monitor_groups_sub.add_parser("references", help="List references for one monitor group (sensitive; file-only)")
    _add_account_id_flag(lb_monitor_groups_references)
    lb_monitor_groups_references.add_argument("--monitor-group-id", required=True, help="Monitor group id")
    _add_query_flags(lb_monitor_groups_references)
    _add_out_flags(lb_monitor_groups_references)
    lb_monitor_groups_references.set_defaults(func=load_balancers_cmd.cmd_load_balancers_monitor_groups_references, write_capable=False)

    lb_regions = load_balancers_sub.add_parser("regions", help="Regions (account-scoped)")
    lb_regions_sub = lb_regions.add_subparsers(dest="load_balancers_regions_cmd", required=True, parser_class=_ToolArgumentParser)
    lb_regions_list = lb_regions_sub.add_parser("list", help="List regions (sensitive; file-only)")
    _add_account_id_flag(lb_regions_list)
    _add_query_flags(lb_regions_list)
    _add_out_flags(lb_regions_list)
    lb_regions_list.set_defaults(func=load_balancers_cmd.cmd_load_balancers_regions_list, write_capable=False)
    lb_regions_get = lb_regions_sub.add_parser("get", help="Get one region (sensitive; file-only)")
    _add_account_id_flag(lb_regions_get)
    lb_regions_get.add_argument("--region-id", required=True, help="Region id")
    _add_query_flags(lb_regions_get)
    _add_out_flags(lb_regions_get)
    lb_regions_get.set_defaults(func=load_balancers_cmd.cmd_load_balancers_regions_get, write_capable=False)

    lb_search = load_balancers_sub.add_parser("search", help="Search load balancing resources (sensitive; file-only)")
    _add_account_id_flag(lb_search)
    _add_query_flags(lb_search)
    _add_out_flags(lb_search)
    lb_search.set_defaults(func=load_balancers_cmd.cmd_load_balancers_search, write_capable=False)

    lb_preview_result = load_balancers_sub.add_parser("preview-result", help="Preview result lookup (sensitive; file-only)")
    lb_preview_result_sub = lb_preview_result.add_subparsers(
        dest="load_balancers_preview_result_cmd", required=True, parser_class=_ToolArgumentParser
    )
    lb_preview_result_get = lb_preview_result_sub.add_parser("get", help="Get a preview result by id (sensitive; file-only)")
    _add_account_id_flag(lb_preview_result_get)
    lb_preview_result_get.add_argument("--preview-id", required=True, help="Preview id")
    _add_query_flags(lb_preview_result_get)
    _add_out_flags(lb_preview_result_get)
    lb_preview_result_get.set_defaults(func=load_balancers_cmd.cmd_load_balancers_preview_result_get, write_capable=False)

    waf = sub.add_parser("waf", help="Rulesets/WAF inventory (read-first)")
    waf_sub = waf.add_subparsers(dest="waf_cmd", required=True, parser_class=_ToolArgumentParser)

    waf_rulesets = waf_sub.add_parser("rulesets", help="Rulesets (zone/account)")
    waf_rulesets_sub = waf_rulesets.add_subparsers(dest="waf_rulesets_cmd", required=True, parser_class=_ToolArgumentParser)
    waf_rulesets_list = waf_rulesets_sub.add_parser("list", help="List rulesets")
    waf_rulesets_list.add_argument("--zone-id", default=None, help="Zone id")
    waf_rulesets_list.add_argument("--account-id", default=None, help="Account id")
    waf_rulesets_list.set_defaults(func=waf_cmd.cmd_waf_rulesets_list, write_capable=False)
    waf_rulesets_get = waf_rulesets_sub.add_parser("get", help="Get one ruleset")
    waf_rulesets_get.add_argument("--zone-id", default=None, help="Zone id")
    waf_rulesets_get.add_argument("--account-id", default=None, help="Account id")
    waf_rulesets_get.add_argument("--ruleset-id", required=True, help="Ruleset id")
    waf_rulesets_get.set_defaults(func=waf_cmd.cmd_waf_rulesets_get, write_capable=False)
    waf_rulesets_entrypoint_get = waf_rulesets_sub.add_parser("entrypoint-get", help="Get entrypoint ruleset for a phase (zone)")
    waf_rulesets_entrypoint_get.add_argument("--zone-id", required=True, help="Zone id")
    waf_rulesets_entrypoint_get.add_argument("--ruleset-phase", required=True, help="Ruleset phase (e.g. http_request_firewall_custom)")
    waf_rulesets_entrypoint_get.set_defaults(func=waf_cmd.cmd_waf_rulesets_entrypoint_get, write_capable=False)
    waf_rulesets_entrypoint_update = waf_rulesets_sub.add_parser(
        "entrypoint-update", help="Update an entrypoint ruleset for a phase (zone/account; write)"
    )
    waf_rulesets_entrypoint_update.add_argument("--zone-id", default=None, help="Zone id")
    waf_rulesets_entrypoint_update.add_argument("--account-id", default=None, help="Account id")
    waf_rulesets_entrypoint_update.add_argument("--ruleset-phase", required=True, help="Ruleset phase (e.g. http_request_firewall_custom)")
    waf_rulesets_entrypoint_update.add_argument("--body-json-file", required=True, help="JSON body file")
    waf_rulesets_entrypoint_update.set_defaults(func=waf_cmd.cmd_waf_rulesets_entrypoint_update, write_capable=True)
    waf_rulesets_versions_list = waf_rulesets_sub.add_parser("versions-list", help="List ruleset versions (zone)")
    waf_rulesets_versions_list.add_argument("--zone-id", required=True, help="Zone id")
    waf_rulesets_versions_list.add_argument("--ruleset-id", required=True, help="Ruleset id")
    waf_rulesets_versions_list.set_defaults(func=waf_cmd.cmd_waf_rulesets_versions_list, write_capable=False)

    waf_firewall = waf_sub.add_parser("firewall", help="Firewall (access rules)")
    waf_firewall_sub = waf_firewall.add_subparsers(dest="waf_firewall_cmd", required=True, parser_class=_ToolArgumentParser)
    waf_access_rules = waf_firewall_sub.add_parser("access-rules", help="Access rules (zone/account/user)")
    waf_access_rules_sub = waf_access_rules.add_subparsers(dest="waf_access_rules_cmd", required=True, parser_class=_ToolArgumentParser)
    waf_access_rules_list = waf_access_rules_sub.add_parser("list", help="List access rules")
    waf_access_rules_list.add_argument("--zone-id", default=None, help="Zone id")
    waf_access_rules_list.add_argument("--account-id", default=None, help="Account id")
    waf_access_rules_list.add_argument("--user", action="store_true", help="Use user scope")
    waf_access_rules_list.set_defaults(func=waf_cmd.cmd_waf_firewall_access_rules_list, write_capable=False)
    waf_access_rules_get = waf_access_rules_sub.add_parser("get", help="Get one access rule")
    waf_access_rules_get.add_argument("--zone-id", default=None, help="Zone id")
    waf_access_rules_get.add_argument("--account-id", default=None, help="Account id")
    waf_access_rules_get.add_argument("--user", action="store_true", help="Use user scope")
    waf_access_rules_get.add_argument("--rule-id", required=True, help="Access rule id")
    waf_access_rules_get.set_defaults(func=waf_cmd.cmd_waf_firewall_access_rules_get, write_capable=False)

    waf_rate_limits = waf_sub.add_parser("rate-limits", help="Rate limits (zone)")
    waf_rate_limits_sub = waf_rate_limits.add_subparsers(dest="waf_rate_limits_cmd", required=True, parser_class=_ToolArgumentParser)
    waf_rate_limits_list = waf_rate_limits_sub.add_parser("list", help="List rate limits")
    waf_rate_limits_list.add_argument("--zone-id", required=True, help="Zone id")
    waf_rate_limits_list.set_defaults(func=waf_cmd.cmd_waf_rate_limits_list, write_capable=False)
    waf_rate_limits_get = waf_rate_limits_sub.add_parser("get", help="Get one rate limit")
    waf_rate_limits_get.add_argument("--zone-id", required=True, help="Zone id")
    waf_rate_limits_get.add_argument("--rate-limit-id", required=True, help="Rate limit id")
    waf_rate_limits_get.set_defaults(func=waf_cmd.cmd_waf_rate_limits_get, write_capable=False)

    waf_snippets = waf_sub.add_parser("snippets", help="Snippets (zone)")
    waf_snippets_sub = waf_snippets.add_subparsers(dest="waf_snippets_cmd", required=True, parser_class=_ToolArgumentParser)
    waf_snippets_list = waf_snippets_sub.add_parser("list", help="List snippets")
    waf_snippets_list.add_argument("--zone-id", required=True, help="Zone id")
    waf_snippets_list.set_defaults(func=waf_cmd.cmd_waf_snippets_list, write_capable=False)
    waf_snippets_get = waf_snippets_sub.add_parser("get", help="Get one snippet (metadata)")
    waf_snippets_get.add_argument("--zone-id", required=True, help="Zone id")
    waf_snippets_get.add_argument("--snippet-name", required=True, help="Snippet name")
    waf_snippets_get.set_defaults(func=waf_cmd.cmd_waf_snippets_get, write_capable=False)
    waf_snippets_content = waf_snippets_sub.add_parser("content", help="Snippet content (sensitive read; file-only)")
    waf_snippets_content_sub = waf_snippets_content.add_subparsers(dest="waf_snippets_content_cmd", required=True, parser_class=_ToolArgumentParser)
    waf_snippets_content_get = waf_snippets_content_sub.add_parser("get", help="Get snippet content (writes to file)")
    waf_snippets_content_get.add_argument("--zone-id", required=True, help="Zone id")
    waf_snippets_content_get.add_argument("--snippet-name", required=True, help="Snippet name")
    waf_snippets_content_get.add_argument("--out", default=None, help="Output file path under --project-dir (required; never printed)")
    waf_snippets_content_get.add_argument("--overwrite", action="store_true", help="Allow overwriting --out")
    waf_snippets_content_get.set_defaults(func=waf_cmd.cmd_waf_snippets_content_get, write_capable=True)

    waf_page_rules = waf_sub.add_parser("page-rules", help="Page rules (zone)")
    waf_page_rules_sub = waf_page_rules.add_subparsers(dest="waf_page_rules_cmd", required=True, parser_class=_ToolArgumentParser)
    waf_page_rules_list = waf_page_rules_sub.add_parser("list", help="List page rules")
    waf_page_rules_list.add_argument("--zone-id", required=True, help="Zone id")
    waf_page_rules_list.set_defaults(func=waf_cmd.cmd_waf_page_rules_list, write_capable=False)
    waf_page_rules_get = waf_page_rules_sub.add_parser("get", help="Get one page rule")
    waf_page_rules_get.add_argument("--zone-id", required=True, help="Zone id")
    waf_page_rules_get.add_argument("--pagerule-id", required=True, help="Page rule id")
    waf_page_rules_get.set_defaults(func=waf_cmd.cmd_waf_page_rules_get, write_capable=False)

    waf_managed_transforms = waf_sub.add_parser("managed-transforms", help="Managed transforms (/managed_headers)")
    waf_managed_transforms_sub = waf_managed_transforms.add_subparsers(
        dest="waf_managed_transforms_cmd", required=True, parser_class=_ToolArgumentParser
    )
    waf_managed_transforms_get = waf_managed_transforms_sub.add_parser("get", help="Get managed transforms")
    waf_managed_transforms_get.add_argument("--zone-id", required=True, help="Zone id")
    waf_managed_transforms_get.set_defaults(func=waf_cmd.cmd_waf_managed_transforms_get, write_capable=False)
    waf_managed_transforms_update = waf_managed_transforms_sub.add_parser(
        "update", help="Update managed transforms (write; plan-first)"
    )
    waf_managed_transforms_update.add_argument("--zone-id", required=True, help="Zone id")
    waf_managed_transforms_update.add_argument("--body-json-file", required=True, help="JSON request body file")
    waf_managed_transforms_update.set_defaults(func=waf_cmd.cmd_waf_managed_transforms_update, write_capable=True)

    operations = sub.add_parser("operations", help="Explicit per-operation commands (derived from the pinned allowlist ledgers)")
    ops_sub = operations.add_subparsers(dest="operations_area", required=True, parser_class=_ToolArgumentParser)

    ops_list = ops_sub.add_parser("list", help="Search allowlisted operations")
    ops_list.add_argument("--contains", default=None, help="Substring filter (op_key/operation id/path/summary/tags)")
    ops_list.add_argument("--tag", default=None, help="Tag filter (substring)")
    ops_list.add_argument("--method", default=None, help="Method filter (GET/POST/PUT/PATCH/DELETE)")
    ops_list.add_argument("--area", default=None, help="Area filter (exact match; derived from ledgers)")
    ops_list.add_argument("--limit", type=int, default=200, help="Max operations to return (default: 200)")
    ops_list.add_argument("--include-deprecated", action="store_true", help="Include deprecated operations")
    ops_list.add_argument("--include-sensitive", action="store_true", help="Include sensitive operations (tokens/content/values)")
    ops_list.set_defaults(func=operations_cmd.cmd_operations_list, write_capable=False)

    ops_show = ops_sub.add_parser("show", help="Show one allowlisted operation")
    ops_show.add_argument("--area", required=True, help="Area name")
    ops_show.add_argument("--op", required=True, help="Operation key (op_key)")
    ops_show.set_defaults(func=operations_cmd.cmd_operations_show, write_capable=False)

    def _add_operation_call_args(op_p: argparse.ArgumentParser) -> None:
        op_p.add_argument("--path-param", action="append", default=[], help="Path param key=value (repeatable)")
        op_p.add_argument("--query", action="append", default=[], help="Query param key=value (repeatable)")
        op_p.add_argument("--body-json-file", default=None, help="JSON request body file (no secrets printed)")
        op_p.add_argument("--body-bytes-file", default=None, help="Raw bytes request body file (no secrets printed)")
        op_p.add_argument("--multipart-spec-file", default=None, help="Multipart spec JSON file (fields + file parts)")
        op_p.add_argument("--content-type", default=None, help="Override Content-Type header (advanced)")
        op_p.add_argument("--out", default=None, help="Write sensitive output (tokens/content/values) to this file under --project-dir")
        op_p.add_argument("--overwrite", action="store_true", help="Allow overwriting --out")

    # Explicit per-operation subcommands, generated deterministically from the allowlist index.
    by_area: dict[str, list] = {}
    for c in load_allowlisted_operation_commands():
        by_area.setdefault(c.area, []).append(c)

    for area in sorted(by_area.keys()):
        area_parser = ops_sub.add_parser(area, help=f"Allowlisted operations: {area}")
        area_sub = area_parser.add_subparsers(dest="op_key", required=True, parser_class=_ToolArgumentParser)
        for c in sorted(by_area[area], key=lambda x: (x.op_key, x.method, x.path_template)):
            op_help = str(c.summary or "").strip() or f"{c.method} {c.path_template}"
            if str(c.sensitivity) != "none":
                op_help = argparse.SUPPRESS
            op_p = area_sub.add_parser(c.op_key, help=op_help)
            _add_operation_call_args(op_p)
            op_p.set_defaults(
                func=openapi_runner_cmd.cmd_openapi_call,
                write_capable=True,
                operation_id=c.operation_id,
                method=c.method,
                path=c.path_template,
            )

    pages = sub.add_parser("pages", help="Cloudflare Pages deploy utilities")
    pages_sub = pages.add_subparsers(dest="pages_cmd", required=True, parser_class=_ToolArgumentParser)
    pages_deploy = pages_sub.add_parser("deploy", help="Deploy a static directory to a Pages project (plan-first; sensitive output).")
    pages_deploy.add_argument("--apply", dest="pages_apply", action="store_true", help="Apply changes (default is dry-run)")
    pages_deploy.add_argument("--yes", dest="pages_yes", action="store_true", help="Additional confirmation for deployment writes")
    pages_deploy.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    pages_deploy.add_argument("--project-name", required=True, help="Pages project name")
    pages_deploy.add_argument("--source-dir", required=True, help="Local directory containing the built static assets")
    pages_deploy.add_argument("--production-branch", default="main", help="Production branch to use if the Pages project must be created during apply (default: main)")
    pages_deploy.add_argument("--branch", default=None, help="Optional Pages branch name (use a non-production branch for preview deployments)")
    pages_deploy.add_argument("--skip-caching", action="store_true", help="Upload all files instead of checking the Pages asset cache first")
    pages_deploy.add_argument("--out", default=None, help="Output file path (relative to --project-dir)")
    pages_deploy.add_argument("--overwrite", action="store_true", help="Allow overwriting the --out file")
    pages_deploy.set_defaults(func=pages_cmd.cmd_pages_deploy, write_capable=True)

    jobs = sub.add_parser("jobs", help="Batch runner (CSV; safe-by-default)")
    jobs_sub = jobs.add_subparsers(dest="jobs_cmd", required=True, parser_class=_ToolArgumentParser)
    jobs_run = jobs_sub.add_parser("run", help="Run a CSV batch (dry-run by default)")
    jobs_run.add_argument("--file", required=True, help="CSV file path")
    jobs_run.add_argument(
        "--include-results",
        action="store_true",
        help="Include full JSON results for non-sensitive steps in the output receipt (can be large).",
    )
    jobs_run.set_defaults(func=jobs_cmd.cmd_jobs_run, write_capable=True)

    zero_trust = sub.add_parser("zero-trust", help="Zero Trust inventory (read-only)")
    zero_trust_sub = zero_trust.add_subparsers(dest="zero_trust_cmd", required=True, parser_class=_ToolArgumentParser)

    zt_org = zero_trust_sub.add_parser("org", help="Zero Trust organization")
    zt_org_sub = zt_org.add_subparsers(dest="zt_org_cmd", required=True, parser_class=_ToolArgumentParser)
    zt_org_get = zt_org_sub.add_parser("get", help="Get Zero Trust organization")
    zt_org_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    zt_org_get.set_defaults(func=zero_trust_cmd.cmd_zero_trust_org_get, write_capable=False)

    zt_gateway = zero_trust_sub.add_parser("gateway", help="Zero Trust Gateway")
    zt_gateway_sub = zt_gateway.add_subparsers(dest="zt_gateway_cmd", required=True, parser_class=_ToolArgumentParser)

    zt_gateway_account = zt_gateway_sub.add_parser("account", help="Gateway account settings")
    zt_gateway_account_sub = zt_gateway_account.add_subparsers(
        dest="zt_gateway_account_cmd", required=True, parser_class=_ToolArgumentParser
    )
    zt_gateway_account_get = zt_gateway_account_sub.add_parser("get", help="Get Gateway account information")
    zt_gateway_account_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    zt_gateway_account_get.set_defaults(func=zero_trust_cmd.cmd_zero_trust_gateway_account_get, write_capable=False)

    zt_gateway_config = zt_gateway_sub.add_parser("configuration", help="Gateway configuration")
    zt_gateway_config_sub = zt_gateway_config.add_subparsers(
        dest="zt_gateway_configuration_cmd", required=True, parser_class=_ToolArgumentParser
    )
    zt_gateway_config_get = zt_gateway_config_sub.add_parser("get", help="Get Gateway configuration")
    zt_gateway_config_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    zt_gateway_config_get.set_defaults(func=zero_trust_cmd.cmd_zero_trust_gateway_configuration_get, write_capable=False)

    zt_gateway_logging = zt_gateway_sub.add_parser("logging", help="Gateway logging settings")
    zt_gateway_logging_sub = zt_gateway_logging.add_subparsers(dest="zt_gateway_logging_cmd", required=True, parser_class=_ToolArgumentParser)
    zt_gateway_logging_get = zt_gateway_logging_sub.add_parser("get", help="Get Gateway logging settings")
    zt_gateway_logging_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    zt_gateway_logging_get.set_defaults(func=zero_trust_cmd.cmd_zero_trust_gateway_logging_get, write_capable=False)

    zt_gateway_rules = zt_gateway_sub.add_parser("rules", help="Gateway rules")
    zt_gateway_rules_sub = zt_gateway_rules.add_subparsers(dest="zt_gateway_rules_cmd", required=True, parser_class=_ToolArgumentParser)
    zt_gateway_rules_list = zt_gateway_rules_sub.add_parser("list", help="List Gateway rules")
    zt_gateway_rules_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    zt_gateway_rules_list.set_defaults(func=zero_trust_cmd.cmd_zero_trust_gateway_rules_list, write_capable=False)
    zt_gateway_rules_get = zt_gateway_rules_sub.add_parser("get", help="Get one Gateway rule")
    zt_gateway_rules_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    zt_gateway_rules_get.add_argument("--rule-id", required=True, help="Rule id")
    zt_gateway_rules_get.set_defaults(func=zero_trust_cmd.cmd_zero_trust_gateway_rules_get, write_capable=False)

    zt_gateway_lists = zt_gateway_sub.add_parser("lists", help="Gateway lists")
    zt_gateway_lists_sub = zt_gateway_lists.add_subparsers(dest="zt_gateway_lists_cmd", required=True, parser_class=_ToolArgumentParser)
    zt_gateway_lists_list = zt_gateway_lists_sub.add_parser("list", help="List Gateway lists")
    zt_gateway_lists_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    zt_gateway_lists_list.set_defaults(func=zero_trust_cmd.cmd_zero_trust_gateway_lists_list, write_capable=False)
    zt_gateway_lists_get = zt_gateway_lists_sub.add_parser("get", help="Get one Gateway list")
    zt_gateway_lists_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    zt_gateway_lists_get.add_argument("--list-id", required=True, help="List id")
    zt_gateway_lists_get.set_defaults(func=zero_trust_cmd.cmd_zero_trust_gateway_lists_get, write_capable=False)
    zt_gateway_lists_items = zt_gateway_lists_sub.add_parser("items", help="Gateway list items")
    zt_gateway_lists_items_sub = zt_gateway_lists_items.add_subparsers(
        dest="zt_gateway_lists_items_cmd", required=True, parser_class=_ToolArgumentParser
    )
    zt_gateway_lists_items_list = zt_gateway_lists_items_sub.add_parser("list", help="List items for a Gateway list")
    zt_gateway_lists_items_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    zt_gateway_lists_items_list.add_argument("--list-id", required=True, help="List id")
    zt_gateway_lists_items_list.set_defaults(func=zero_trust_cmd.cmd_zero_trust_gateway_lists_items_list, write_capable=False)

    zt_devices = zero_trust_sub.add_parser("devices", help="Devices inventory")
    zt_devices_sub = zt_devices.add_subparsers(dest="zt_devices_cmd", required=True, parser_class=_ToolArgumentParser)
    zt_devices_list = zt_devices_sub.add_parser("list", help="List devices")
    zt_devices_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    zt_devices_list.set_defaults(func=zero_trust_cmd.cmd_zero_trust_devices_list, write_capable=False)
    zt_devices_get = zt_devices_sub.add_parser("get", help="Get one device")
    zt_devices_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    zt_devices_get.add_argument("--device-id", required=True, help="Device id")
    zt_devices_get.set_defaults(func=zero_trust_cmd.cmd_zero_trust_devices_get, write_capable=False)

    zt_access = zero_trust_sub.add_parser("access", help="Access inventory")
    zt_access_sub = zt_access.add_subparsers(dest="zt_access_cmd", required=True, parser_class=_ToolArgumentParser)

    zt_access_apps = zt_access_sub.add_parser("apps", help="Access applications")
    zt_access_apps_sub = zt_access_apps.add_subparsers(dest="zt_access_apps_cmd", required=True, parser_class=_ToolArgumentParser)
    zt_access_apps_list = zt_access_apps_sub.add_parser("list", help="List Access applications")
    zt_access_apps_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    zt_access_apps_list.add_argument("--name", default=None, help="Optional name filter")
    zt_access_apps_list.add_argument("--domain", default=None, help="Optional domain filter")
    zt_access_apps_list.add_argument("--aud", default=None, help="Optional aud filter")
    zt_access_apps_list.add_argument("--target-attributes", dest="target_attributes", default=None, help="Optional target attributes filter")
    zt_access_apps_list.add_argument("--search", default=None, help="Optional search string")
    zt_access_apps_list.add_argument("--exact", action="store_true", help="Exact match (when supported by the API)")
    zt_access_apps_list.set_defaults(func=zero_trust_cmd.cmd_zero_trust_access_apps_list, write_capable=False)
    zt_access_apps_resolve = zt_access_apps_sub.add_parser("resolve", help="Resolve one Access app by exact name/domain/aud")
    zt_access_apps_resolve.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    zt_access_apps_resolve.add_argument("--name", default=None, help="Exact app name")
    zt_access_apps_resolve.add_argument("--domain", default=None, help="Exact app domain")
    zt_access_apps_resolve.add_argument("--aud", default=None, help="Exact app aud")
    zt_access_apps_resolve.add_argument("--exact", action="store_true", help="Exact match (when supported by the API)")
    zt_access_apps_resolve.set_defaults(func=zero_trust_cmd.cmd_zero_trust_access_apps_resolve, write_capable=False)
    zt_access_apps_get = zt_access_apps_sub.add_parser("get", help="Get one Access application")
    zt_access_apps_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    zt_access_apps_get.add_argument("--app-id", required=True, help="App id")
    zt_access_apps_get.set_defaults(func=zero_trust_cmd.cmd_zero_trust_access_apps_get, write_capable=False)

    zt_access_policies = zt_access_sub.add_parser("policies", help="Access policies (app-scoped)")
    zt_access_policies_sub = zt_access_policies.add_subparsers(dest="zt_access_policies_cmd", required=True, parser_class=_ToolArgumentParser)
    zt_access_policies_list = zt_access_policies_sub.add_parser("list", help="List Access app policies")
    zt_access_policies_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    zt_access_policies_list.add_argument("--app-id", required=True, help="App id")
    zt_access_policies_list.set_defaults(func=zero_trust_cmd.cmd_zero_trust_access_policies_list, write_capable=False)
    zt_access_policies_get = zt_access_policies_sub.add_parser("get", help="Get one Access policy")
    zt_access_policies_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    zt_access_policies_get.add_argument("--app-id", required=True, help="App id")
    zt_access_policies_get.add_argument("--policy-id", required=True, help="Policy id")
    zt_access_policies_get.set_defaults(func=zero_trust_cmd.cmd_zero_trust_access_policies_get, write_capable=False)

    tunnels = sub.add_parser("tunnels", help="Cloudflare Tunnels (read-only helpers)")
    tunnels_sub = tunnels.add_subparsers(dest="tunnels_cmd", required=True, parser_class=_ToolArgumentParser)
    tunnels_list = tunnels_sub.add_parser("list", help="List tunnels (account-scoped)")
    tunnels_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    tunnels_list.add_argument("--name", default=None, help="Optional exact name filter (client-side)")
    tunnels_list.add_argument("--status", default=None, help="Optional status filter (client-side)")
    tunnels_list.set_defaults(func=tunnels_cmd.cmd_tunnels_list, write_capable=False)
    tunnels_resolve = tunnels_sub.add_parser("resolve", help="Resolve a tunnel id by exact name")
    tunnels_resolve.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    tunnels_resolve.add_argument("--name", required=True, help="Exact tunnel name to resolve")
    tunnels_resolve.set_defaults(func=tunnels_cmd.cmd_tunnels_resolve, write_capable=False)
    tunnels_config = tunnels_sub.add_parser("config", help="Tunnel configuration")
    tunnels_config_sub = tunnels_config.add_subparsers(dest="tunnels_config_cmd", required=True, parser_class=_ToolArgumentParser)
    tunnels_config_get = tunnels_config_sub.add_parser("get", help="Get tunnel ingress configuration")
    tunnels_config_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    tunnels_config_get.add_argument("--tunnel-id", required=True, help="Tunnel id")
    tunnels_config_get.set_defaults(func=tunnels_cmd.cmd_tunnels_config_get, write_capable=False)

    workers = sub.add_parser("workers", help="Workers platform (read-only + safe writes)")
    workers_sub = workers.add_subparsers(dest="workers_cmd", required=True, parser_class=_ToolArgumentParser)

    scripts = workers_sub.add_parser("scripts", help="Workers scripts (metadata + apply-gated content downloads)")
    scripts_sub = scripts.add_subparsers(dest="scripts_cmd", required=True, parser_class=_ToolArgumentParser)
    scripts_list = scripts_sub.add_parser("list", help="List scripts")
    scripts_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    scripts_list.add_argument("--tags", default=None, help="Optional tags filter")
    scripts_list.set_defaults(func=workers_cmd.cmd_workers_scripts_list, write_capable=False)
    scripts_search = scripts_sub.add_parser("search", help="Search scripts")
    scripts_search.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    scripts_search.add_argument("--name", default=None, help="Optional name filter")
    scripts_search.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    scripts_search.add_argument("--per-page", type=int, default=50, help="Page size (default: 50)")
    scripts_search.set_defaults(func=workers_cmd.cmd_workers_scripts_search, write_capable=False)
    scripts_get = scripts_sub.add_parser("get", help="Get script settings (metadata only)")
    scripts_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    scripts_get.add_argument("--script-name", required=True, help="Script name")
    scripts_get.set_defaults(func=workers_cmd.cmd_workers_scripts_get, write_capable=False)
    scripts_download = scripts_sub.add_parser("download", help="Download script (sensitive read; writes to file)")
    scripts_download.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    scripts_download.add_argument("--script-name", required=True, help="Script name")
    scripts_download.add_argument("--out", required=True, help="Output file path (relative to --project-dir)")
    scripts_download.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing file")
    scripts_download.set_defaults(func=workers_sensitive_cmd.cmd_workers_scripts_download, write_capable=True)
    scripts_content = scripts_sub.add_parser("content", help="Script content (sensitive read; writes to file)")
    scripts_content_sub = scripts_content.add_subparsers(dest="scripts_content_cmd", required=True, parser_class=_ToolArgumentParser)
    scripts_content_get = scripts_content_sub.add_parser("get", help="Get script content (writes to file)")
    scripts_content_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    scripts_content_get.add_argument("--script-name", required=True, help="Script name")
    scripts_content_get.add_argument("--out", required=True, help="Output file path (relative to --project-dir)")
    scripts_content_get.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing file")
    scripts_content_get.set_defaults(func=workers_sensitive_cmd.cmd_workers_scripts_content_get, write_capable=True)

    scripts_schedules = scripts_sub.add_parser("schedules", help="Script schedules (metadata only)")
    scripts_schedules_sub = scripts_schedules.add_subparsers(
        dest="scripts_schedules_cmd", required=True, parser_class=_ToolArgumentParser
    )
    scripts_schedules_get = scripts_schedules_sub.add_parser("get", help="Get cron triggers")
    scripts_schedules_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    scripts_schedules_get.add_argument("--script-name", required=True, help="Script name")
    scripts_schedules_get.set_defaults(func=workers_cmd.cmd_workers_scripts_schedules_get, write_capable=False)

    scripts_script_settings = scripts_sub.add_parser("script-settings", help="Script settings (metadata only)")
    scripts_script_settings_sub = scripts_script_settings.add_subparsers(
        dest="scripts_script_settings_cmd", required=True, parser_class=_ToolArgumentParser
    )
    scripts_script_settings_get = scripts_script_settings_sub.add_parser("get", help="Get script settings")
    scripts_script_settings_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    scripts_script_settings_get.add_argument("--script-name", required=True, help="Script name")
    scripts_script_settings_get.set_defaults(func=workers_cmd.cmd_workers_scripts_script_settings_get, write_capable=False)

    workers_observability = workers_sub.add_parser("observability", help="Workers script observability (toggle; plan-first)")
    workers_observability_sub = workers_observability.add_subparsers(
        dest="workers_observability_cmd", required=True, parser_class=_ToolArgumentParser
    )
    workers_observability_status = workers_observability_sub.add_parser(
        "status", help="Show current observability settings for one script"
    )
    workers_observability_status.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    workers_observability_status.add_argument("--script-name", required=True, help="Script name")
    workers_observability_status.set_defaults(func=workers_write_cmd.cmd_workers_observability_status, write_capable=False)
    workers_observability_enable = workers_observability_sub.add_parser(
        "enable", help="Enable script observability (dry-run by default; apply requires --apply --yes)"
    )
    workers_observability_enable.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    workers_observability_enable.add_argument("--script-name", required=True, help="Script name")
    workers_observability_enable.add_argument(
        "--head-sampling-rate",
        dest="head_sampling_rate",
        type=float,
        default=None,
        help="Optional sampling rate from 0 to 1 (1 = 100%%, 0.1 = 10%%). If omitted, the tool leaves the current rate unchanged.",
    )
    workers_observability_enable.set_defaults(func=workers_write_cmd.cmd_workers_observability_enable, write_capable=True)
    workers_observability_disable = workers_observability_sub.add_parser(
        "disable", help="Disable script observability (dry-run by default; apply requires --apply --yes)"
    )
    workers_observability_disable.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    workers_observability_disable.add_argument("--script-name", required=True, help="Script name")
    workers_observability_disable.set_defaults(func=workers_write_cmd.cmd_workers_observability_disable, write_capable=True)

    scripts_usage_model = scripts_sub.add_parser("usage-model", help="Script usage model (metadata only)")
    scripts_usage_model_sub = scripts_usage_model.add_subparsers(
        dest="scripts_usage_model_cmd", required=True, parser_class=_ToolArgumentParser
    )
    scripts_usage_model_get = scripts_usage_model_sub.add_parser("get", help="Get usage model")
    scripts_usage_model_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    scripts_usage_model_get.add_argument("--script-name", required=True, help="Script name")
    scripts_usage_model_get.set_defaults(func=workers_cmd.cmd_workers_scripts_usage_model_get, write_capable=False)

    scripts_subdomain = scripts_sub.add_parser("subdomain", help="Script subdomain (metadata only)")
    scripts_subdomain_sub = scripts_subdomain.add_subparsers(
        dest="scripts_subdomain_cmd", required=True, parser_class=_ToolArgumentParser
    )
    scripts_subdomain_get = scripts_subdomain_sub.add_parser("get", help="Get script subdomain")
    scripts_subdomain_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    scripts_subdomain_get.add_argument("--script-name", required=True, help="Script name")
    scripts_subdomain_get.set_defaults(func=workers_cmd.cmd_workers_scripts_subdomain_get, write_capable=False)

    scripts_secrets = scripts_sub.add_parser("secrets", help="Script secrets (metadata only; never values)")
    scripts_secrets_sub = scripts_secrets.add_subparsers(
        dest="scripts_secrets_cmd", required=True, parser_class=_ToolArgumentParser
    )
    scripts_secrets_list = scripts_secrets_sub.add_parser("list", help="List secret bindings")
    scripts_secrets_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    scripts_secrets_list.add_argument("--script-name", required=True, help="Script name")
    scripts_secrets_list.set_defaults(func=workers_cmd.cmd_workers_scripts_secrets_list, write_capable=False)
    scripts_secrets_get = scripts_secrets_sub.add_parser("get", help="Get one secret binding")
    scripts_secrets_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    scripts_secrets_get.add_argument("--script-name", required=True, help="Script name")
    scripts_secrets_get.add_argument("--secret-name", required=True, help="Secret name")
    scripts_secrets_get.set_defaults(func=workers_cmd.cmd_workers_scripts_secrets_get, write_capable=False)

    account_settings = workers_sub.add_parser("account-settings", help="Worker account settings (metadata only)")
    account_settings_sub = account_settings.add_subparsers(dest="account_settings_cmd", required=True, parser_class=_ToolArgumentParser)
    account_settings_get = account_settings_sub.add_parser("get", help="Get account settings")
    account_settings_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    account_settings_get.set_defaults(func=workers_cmd.cmd_workers_account_settings_get, write_capable=False)

    placement = workers_sub.add_parser("placement", help="Worker placement regions (metadata only)")
    placement_sub = placement.add_subparsers(dest="placement_cmd", required=True, parser_class=_ToolArgumentParser)
    placement_regions = placement_sub.add_parser("regions", help="Placement regions")
    placement_regions_sub = placement_regions.add_subparsers(dest="placement_regions_cmd", required=True, parser_class=_ToolArgumentParser)
    placement_regions_list = placement_regions_sub.add_parser("list", help="List regions")
    placement_regions_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    placement_regions_list.set_defaults(func=workers_cmd.cmd_workers_placement_regions_list, write_capable=False)

    platforms = workers_sub.add_parser("platforms", help="Workers for Platforms inventory (read-only)")
    platforms_sub = platforms.add_subparsers(dest="platforms_cmd", required=True, parser_class=_ToolArgumentParser)
    platforms_list = platforms_sub.add_parser("list", help="List platform workers")
    platforms_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    platforms_list.set_defaults(func=workers_cmd.cmd_workers_platforms_list, write_capable=False)
    platforms_get = platforms_sub.add_parser("get", help="Get one platform worker")
    platforms_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    platforms_get.add_argument("--worker-id", required=True, help="Worker id")
    platforms_get.set_defaults(func=workers_cmd.cmd_workers_platforms_get, write_capable=False)

    services = workers_sub.add_parser("services", help="Workers services (read-only)")
    services_sub = services.add_subparsers(dest="services_cmd", required=True, parser_class=_ToolArgumentParser)
    services_env = services_sub.add_parser("env", help="Service environments (read-only)")
    services_env_sub = services_env.add_subparsers(dest="services_env_cmd", required=True, parser_class=_ToolArgumentParser)
    services_env_settings = services_env_sub.add_parser("settings", help="Environment settings (metadata only)")
    services_env_settings_sub = services_env_settings.add_subparsers(
        dest="services_env_settings_cmd", required=True, parser_class=_ToolArgumentParser
    )
    services_env_settings_get = services_env_settings_sub.add_parser("get", help="Get environment settings")
    services_env_settings_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    services_env_settings_get.add_argument("--service-name", required=True, help="Service name")
    services_env_settings_get.add_argument("--environment-name", required=True, help="Environment name")
    services_env_settings_get.set_defaults(func=workers_cmd.cmd_workers_services_env_settings_get, write_capable=False)

    routes = workers_sub.add_parser("routes", help="Worker routes (zone-scoped)")
    routes_sub = routes.add_subparsers(dest="routes_cmd", required=True, parser_class=_ToolArgumentParser)
    routes_list = routes_sub.add_parser("list", help="List routes")
    routes_list.add_argument("--zone-id", required=True, help="Zone id")
    routes_list.set_defaults(func=workers_cmd.cmd_workers_routes_list, write_capable=False)
    routes_get = routes_sub.add_parser("get", help="Get one route")
    routes_get.add_argument("--zone-id", required=True, help="Zone id")
    routes_get.add_argument("--route-id", required=True, help="Route id")
    routes_get.set_defaults(func=workers_cmd.cmd_workers_routes_get, write_capable=False)
    routes_ensure = routes_sub.add_parser("ensure", help="Ensure a route exists for pattern -> script mapping (write)")
    routes_ensure.add_argument("--zone-id", required=True, help="Zone id")
    routes_ensure.add_argument("--pattern", required=True, help="Route pattern (e.g. example.com/*)")
    routes_ensure.add_argument("--script-name", required=True, help="Worker script name")
    routes_ensure.set_defaults(func=workers_write_cmd.cmd_workers_routes_ensure, write_capable=True)
    routes_absent = routes_sub.add_parser("ensure-absent", help="Ensure no route exists for a pattern (write)")
    routes_absent.add_argument("--zone-id", required=True, help="Zone id")
    routes_absent.add_argument("--pattern", required=True, help="Route pattern (e.g. example.com/*)")
    routes_absent.set_defaults(func=workers_write_cmd.cmd_workers_routes_ensure_absent, write_capable=True)

    subdomain = workers_sub.add_parser("subdomain", help="Workers subdomain")
    subdomain_sub = subdomain.add_subparsers(dest="subdomain_cmd", required=True, parser_class=_ToolArgumentParser)
    subdomain_get = subdomain_sub.add_parser("get", help="Get account subdomain")
    subdomain_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    subdomain_get.set_defaults(func=workers_cmd.cmd_workers_subdomain_get, write_capable=False)
    subdomain_ensure = subdomain_sub.add_parser("ensure", help="Ensure Workers subdomain is set (write)")
    subdomain_ensure.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    subdomain_ensure.add_argument("--subdomain", required=True, help="Subdomain name to set")
    subdomain_ensure.set_defaults(func=workers_write_cmd.cmd_workers_subdomain_ensure, write_capable=True)
    subdomain_absent = subdomain_sub.add_parser("ensure-absent", help="Ensure Workers subdomain is not set (write)")
    subdomain_absent.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    subdomain_absent.set_defaults(func=workers_write_cmd.cmd_workers_subdomain_ensure_absent, write_capable=True)

    domains = workers_sub.add_parser("domains", help="Workers domains")
    domains_sub = domains.add_subparsers(dest="domains_cmd", required=True, parser_class=_ToolArgumentParser)
    domains_list = domains_sub.add_parser("list", help="List domains")
    domains_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    domains_list.set_defaults(func=workers_cmd.cmd_workers_domains_list, write_capable=False)
    domains_get = domains_sub.add_parser("get", help="Get one domain")
    domains_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    domains_get.add_argument("--domain-id", required=True, help="Domain id")
    domains_get.set_defaults(func=workers_cmd.cmd_workers_domains_get, write_capable=False)
    domains_attach = domains_sub.add_parser("attach", help="Attach a domain to a Workers service (write)")
    domains_attach.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    domains_attach.add_argument("--zone-id", required=True, help="Zone id that owns the hostname")
    domains_attach.add_argument("--hostname", required=True, help="Hostname to attach (e.g. api.example.com)")
    domains_attach.add_argument("--service", required=True, help="Workers service name")
    domains_attach.add_argument("--environment", default=None, help="Optional environment name")
    domains_attach.set_defaults(func=workers_write_cmd.cmd_workers_domains_attach, write_capable=True)
    domains_detach = domains_sub.add_parser("detach", help="Detach a Workers domain by id (write)")
    domains_detach.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    domains_detach.add_argument("--domain-id", required=True, help="Domain id")
    domains_detach.set_defaults(func=workers_write_cmd.cmd_workers_domains_detach, write_capable=True)

    dispatch = workers_sub.add_parser("dispatch", help="Workers Dispatch")
    dispatch_sub = dispatch.add_subparsers(dest="dispatch_cmd", required=True, parser_class=_ToolArgumentParser)
    dispatch_ns = dispatch_sub.add_parser("namespaces", help="Dispatch namespaces")
    dispatch_ns_sub = dispatch_ns.add_subparsers(dest="dispatch_ns_cmd", required=True, parser_class=_ToolArgumentParser)
    dispatch_ns_list = dispatch_ns_sub.add_parser("list", help="List namespaces")
    dispatch_ns_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    dispatch_ns_list.set_defaults(func=workers_cmd.cmd_workers_dispatch_namespaces_list, write_capable=False)
    dispatch_ns_get = dispatch_ns_sub.add_parser("get", help="Get one namespace")
    dispatch_ns_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    dispatch_ns_get.add_argument("--dispatch-namespace", required=True, help="Dispatch namespace name")
    dispatch_ns_get.set_defaults(func=workers_cmd.cmd_workers_dispatch_namespaces_get, write_capable=False)

    dispatch_scripts = dispatch_sub.add_parser("scripts", help="Dispatch scripts (metadata only)")
    dispatch_scripts_sub = dispatch_scripts.add_subparsers(dest="dispatch_scripts_cmd", required=True, parser_class=_ToolArgumentParser)
    dispatch_scripts_list = dispatch_scripts_sub.add_parser("list", help="List scripts in a namespace")
    dispatch_scripts_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    dispatch_scripts_list.add_argument("--dispatch-namespace", required=True, help="Dispatch namespace name")
    dispatch_scripts_list.set_defaults(func=workers_cmd.cmd_workers_dispatch_scripts_list, write_capable=False)
    dispatch_scripts_get = dispatch_scripts_sub.add_parser("get", help="Get script settings (metadata only)")
    dispatch_scripts_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    dispatch_scripts_get.add_argument("--dispatch-namespace", required=True, help="Dispatch namespace name")
    dispatch_scripts_get.add_argument("--script-name", required=True, help="Script name")
    dispatch_scripts_get.set_defaults(func=workers_cmd.cmd_workers_dispatch_scripts_get, write_capable=False)

    dispatch_scripts_bindings = dispatch_scripts_sub.add_parser("bindings", help="Script bindings (metadata only)")
    dispatch_scripts_bindings_sub = dispatch_scripts_bindings.add_subparsers(
        dest="dispatch_scripts_bindings_cmd", required=True, parser_class=_ToolArgumentParser
    )
    dispatch_scripts_bindings_list = dispatch_scripts_bindings_sub.add_parser("list", help="List bindings")
    dispatch_scripts_bindings_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    dispatch_scripts_bindings_list.add_argument("--dispatch-namespace", required=True, help="Dispatch namespace name")
    dispatch_scripts_bindings_list.add_argument("--script-name", required=True, help="Script name")
    dispatch_scripts_bindings_list.set_defaults(func=workers_cmd.cmd_workers_dispatch_scripts_bindings_list, write_capable=False)

    dispatch_scripts_tags = dispatch_scripts_sub.add_parser("tags", help="Script tags (metadata only)")
    dispatch_scripts_tags_sub = dispatch_scripts_tags.add_subparsers(
        dest="dispatch_scripts_tags_cmd", required=True, parser_class=_ToolArgumentParser
    )
    dispatch_scripts_tags_list = dispatch_scripts_tags_sub.add_parser("list", help="List tags")
    dispatch_scripts_tags_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    dispatch_scripts_tags_list.add_argument("--dispatch-namespace", required=True, help="Dispatch namespace name")
    dispatch_scripts_tags_list.add_argument("--script-name", required=True, help="Script name")
    dispatch_scripts_tags_list.set_defaults(func=workers_cmd.cmd_workers_dispatch_scripts_tags_list, write_capable=False)

    dispatch_scripts_secrets = dispatch_scripts_sub.add_parser("secrets", help="Script secrets (metadata only; never values)")
    dispatch_scripts_secrets_sub = dispatch_scripts_secrets.add_subparsers(
        dest="dispatch_scripts_secrets_cmd", required=True, parser_class=_ToolArgumentParser
    )
    dispatch_scripts_secrets_list = dispatch_scripts_secrets_sub.add_parser("list", help="List secret bindings")
    dispatch_scripts_secrets_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    dispatch_scripts_secrets_list.add_argument("--dispatch-namespace", required=True, help="Dispatch namespace name")
    dispatch_scripts_secrets_list.add_argument("--script-name", required=True, help="Script name")
    dispatch_scripts_secrets_list.set_defaults(func=workers_cmd.cmd_workers_dispatch_scripts_secrets_list, write_capable=False)
    dispatch_scripts_secrets_get = dispatch_scripts_secrets_sub.add_parser("get", help="Get one secret binding")
    dispatch_scripts_secrets_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    dispatch_scripts_secrets_get.add_argument("--dispatch-namespace", required=True, help="Dispatch namespace name")
    dispatch_scripts_secrets_get.add_argument("--script-name", required=True, help="Script name")
    dispatch_scripts_secrets_get.add_argument("--secret-name", required=True, help="Secret name")
    dispatch_scripts_secrets_get.set_defaults(func=workers_cmd.cmd_workers_dispatch_scripts_secrets_get, write_capable=False)

    builds = workers_sub.add_parser("builds", help="Workers builds (read-only)")
    builds_sub = builds.add_subparsers(dest="builds_cmd", required=True, parser_class=_ToolArgumentParser)
    builds_list = builds_sub.add_parser("list", help="List builds by external script id")
    builds_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    builds_list.add_argument("--external-script-id", required=True, help="External script id")
    builds_list.set_defaults(func=workers_cmd.cmd_workers_builds_list, write_capable=False)
    builds_triggers = builds_sub.add_parser("triggers", help="Build triggers")
    builds_triggers_sub = builds_triggers.add_subparsers(dest="builds_triggers_cmd", required=True, parser_class=_ToolArgumentParser)
    builds_triggers_list = builds_triggers_sub.add_parser("list", help="List triggers by external script id")
    builds_triggers_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    builds_triggers_list.add_argument("--external-script-id", required=True, help="External script id")
    builds_triggers_list.set_defaults(func=workers_cmd.cmd_workers_builds_triggers_list, write_capable=False)

    pipelines = workers_sub.add_parser("pipelines", help="Workers pipelines (read-only)")
    pipelines_sub = pipelines.add_subparsers(dest="pipelines_cmd", required=True, parser_class=_ToolArgumentParser)
    pipelines_list = pipelines_sub.add_parser("list", help="List pipelines (v1)")
    pipelines_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    pipelines_list.set_defaults(func=workers_cmd.cmd_workers_pipelines_list, write_capable=False)
    pipelines_get = pipelines_sub.add_parser("get", help="Get one pipeline (v1)")
    pipelines_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    pipelines_get.add_argument("--pipeline-id", required=True, help="Pipeline id")
    pipelines_get.set_defaults(func=workers_cmd.cmd_workers_pipelines_get, write_capable=False)

    pipelines_sinks = pipelines_sub.add_parser("sinks", help="Pipeline sinks (v1)")
    pipelines_sinks_sub = pipelines_sinks.add_subparsers(dest="pipelines_sinks_cmd", required=True, parser_class=_ToolArgumentParser)
    pipelines_sinks_list = pipelines_sinks_sub.add_parser("list", help="List sinks")
    pipelines_sinks_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    pipelines_sinks_list.set_defaults(func=workers_cmd.cmd_workers_pipelines_sinks_list, write_capable=False)
    pipelines_sinks_get = pipelines_sinks_sub.add_parser("get", help="Get one sink")
    pipelines_sinks_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    pipelines_sinks_get.add_argument("--sink-id", required=True, help="Sink id")
    pipelines_sinks_get.set_defaults(func=workers_cmd.cmd_workers_pipelines_sinks_get, write_capable=False)

    pipelines_streams = pipelines_sub.add_parser("streams", help="Pipeline streams (v1)")
    pipelines_streams_sub = pipelines_streams.add_subparsers(dest="pipelines_streams_cmd", required=True, parser_class=_ToolArgumentParser)
    pipelines_streams_list = pipelines_streams_sub.add_parser("list", help="List streams")
    pipelines_streams_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    pipelines_streams_list.set_defaults(func=workers_cmd.cmd_workers_pipelines_streams_list, write_capable=False)
    pipelines_streams_get = pipelines_streams_sub.add_parser("get", help="Get one stream")
    pipelines_streams_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    pipelines_streams_get.add_argument("--stream-id", required=True, help="Stream id")
    pipelines_streams_get.set_defaults(func=workers_cmd.cmd_workers_pipelines_streams_get, write_capable=False)

    pipelines_legacy = pipelines_sub.add_parser("legacy", help="Legacy (deprecated) pipelines endpoints")
    pipelines_legacy_sub = pipelines_legacy.add_subparsers(dest="pipelines_legacy_cmd", required=True, parser_class=_ToolArgumentParser)
    pipelines_legacy_list = pipelines_legacy_sub.add_parser("list", help="List legacy pipelines")
    pipelines_legacy_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    pipelines_legacy_list.set_defaults(func=workers_cmd.cmd_workers_pipelines_legacy_list, write_capable=False)
    pipelines_legacy_get = pipelines_legacy_sub.add_parser("get", help="Get one legacy pipeline")
    pipelines_legacy_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    pipelines_legacy_get.add_argument("--pipeline-name", required=True, help="Pipeline name")
    pipelines_legacy_get.set_defaults(func=workers_cmd.cmd_workers_pipelines_legacy_get, write_capable=False)

    kv = workers_sub.add_parser("kv", help="Workers KV (metadata + apply-gated value reads)")
    kv_sub = kv.add_subparsers(dest="kv_cmd", required=True, parser_class=_ToolArgumentParser)
    kv_ns = kv_sub.add_parser("namespaces", help="KV namespaces")
    kv_ns_sub = kv_ns.add_subparsers(dest="kv_ns_cmd", required=True, parser_class=_ToolArgumentParser)
    kv_ns_list = kv_ns_sub.add_parser("list", help="List namespaces")
    kv_ns_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    kv_ns_list.set_defaults(func=workers_cmd.cmd_workers_kv_namespaces_list, write_capable=False)
    kv_ns_get = kv_ns_sub.add_parser("get", help="Get a namespace")
    kv_ns_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    kv_ns_get.add_argument("--namespace-id", required=True, help="Namespace id")
    kv_ns_get.set_defaults(func=workers_cmd.cmd_workers_kv_namespaces_get, write_capable=False)

    kv_keys = kv_sub.add_parser("keys", help="KV keys (never values)")
    kv_keys_sub = kv_keys.add_subparsers(dest="kv_keys_cmd", required=True, parser_class=_ToolArgumentParser)
    kv_keys_list = kv_keys_sub.add_parser("list", help="List keys")
    kv_keys_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    kv_keys_list.add_argument("--namespace-id", required=True, help="Namespace id")
    kv_keys_list.add_argument("--limit", type=int, default=1000, help="Max keys per page (default: 1000)")
    kv_keys_list.add_argument("--prefix", default=None, help="Optional prefix filter")
    kv_keys_list.add_argument("--cursor", default=None, help="Cursor for pagination (from previous result_info)")
    kv_keys_list.add_argument("--all", action="store_true", help="Fetch all pages (capped; safe)")
    kv_keys_list.add_argument("--max-rows", type=int, default=5000, help="Max rows when using --all (default: 5000)")
    kv_keys_list.set_defaults(func=workers_cmd.cmd_workers_kv_keys_list, write_capable=False)
    kv_keys_meta = kv_keys_sub.add_parser("metadata-get", help="Get key metadata (never the value)")
    kv_keys_meta.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    kv_keys_meta.add_argument("--namespace-id", required=True, help="Namespace id")
    kv_keys_meta.add_argument("--key-name", required=True, help="Key name")
    kv_keys_meta.set_defaults(func=workers_cmd.cmd_workers_kv_keys_metadata_get, write_capable=False)

    kv_values = kv_sub.add_parser("values", help="KV values (sensitive; file output only)")
    kv_values_sub = kv_values.add_subparsers(dest="kv_values_cmd", required=True, parser_class=_ToolArgumentParser)
    kv_values_get = kv_values_sub.add_parser("get", help="Get one KV value (writes to file)")
    kv_values_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    kv_values_get.add_argument("--namespace-id", required=True, help="Namespace id")
    kv_values_get.add_argument("--key-name", required=True, help="Key name")
    kv_values_get.add_argument("--out", required=True, help="Output file path (relative to --project-dir)")
    kv_values_get.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing file")
    kv_values_get.set_defaults(func=workers_sensitive_cmd.cmd_workers_kv_values_get, write_capable=True)

    versions = workers_sub.add_parser("versions", help="Workers script versions")
    versions_sub = versions.add_subparsers(dest="versions_cmd", required=True, parser_class=_ToolArgumentParser)
    versions_list = versions_sub.add_parser("list", help="List versions")
    versions_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    versions_list.add_argument("--script-name", required=True, help="Script name")
    versions_list.set_defaults(func=workers_cmd.cmd_workers_versions_list, write_capable=False)
    versions_get = versions_sub.add_parser("get", help="Get one version")
    versions_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    versions_get.add_argument("--script-name", required=True, help="Script name")
    versions_get.add_argument("--version-id", required=True, help="Version id")
    versions_get.set_defaults(func=workers_cmd.cmd_workers_versions_get, write_capable=False)

    deployments = workers_sub.add_parser("deployments", help="Workers deployments")
    deployments_sub = deployments.add_subparsers(dest="deployments_cmd", required=True, parser_class=_ToolArgumentParser)
    deployments_list = deployments_sub.add_parser("list", help="List deployments")
    deployments_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    deployments_list.add_argument("--script-name", required=True, help="Script name")
    deployments_list.set_defaults(func=workers_cmd.cmd_workers_deployments_list, write_capable=False)
    deployments_get = deployments_sub.add_parser("get", help="Get one deployment")
    deployments_get.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    deployments_get.add_argument("--script-name", required=True, help="Script name")
    deployments_get.add_argument("--deployment-id", required=True, help="Deployment id")
    deployments_get.set_defaults(func=workers_cmd.cmd_workers_deployments_get, write_capable=False)

    logs = workers_sub.add_parser("logs", help="Workers stored logs/events (Telemetry API; file-only)")
    logs_sub = logs.add_subparsers(dest="logs_cmd", required=True, parser_class=_ToolArgumentParser)

    logs_keys = logs_sub.add_parser("keys", help="List telemetry keys (file-only; dry-run by default)")
    logs_keys.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    logs_keys.add_argument("--from", dest="from_ts", default=None, help="Unix-ms or RFC3339 (default: last 24h)")
    logs_keys.add_argument("--to", dest="to_ts", default=None, help="Unix-ms or RFC3339 (default: now)")
    logs_keys.add_argument("--limit", type=int, default=None, help="Optional limit")
    logs_keys.add_argument("--dataset", action="append", default=[], help="Optional dataset name (repeatable)")
    logs_keys.add_argument("--key-needle", dest="key_needle", default=None, help="Substring search within key names")
    logs_keys.add_argument("--needle", default=None, help="Substring search within events (broad)")
    logs_keys.add_argument("--out", required=True, help="Output file path under --project-dir")
    logs_keys.add_argument("--overwrite", action="store_true", help="Allow overwriting --out")
    logs_keys.set_defaults(func=workers_logs_cmd.cmd_workers_logs_keys, write_capable=True)

    logs_values = logs_sub.add_parser("values", help="List telemetry values for a key (file-only; dry-run by default)")
    logs_values.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    logs_values.add_argument("--from", dest="from_ts", default=None, help="Unix-ms or RFC3339 (default: last 24h)")
    logs_values.add_argument("--to", dest="to_ts", default=None, help="Unix-ms or RFC3339 (default: now)")
    logs_values.add_argument("--limit", type=int, default=None, help="Optional limit")
    logs_values.add_argument("--dataset", action="append", default=[], help="Optional dataset name (repeatable)")
    logs_values.add_argument("--key", required=True, help="Telemetry key to list values for")
    logs_values.add_argument("--type", required=True, choices=("string", "number", "boolean"), help="Value type")
    logs_values.add_argument("--needle", default=None, help="Substring search within values")
    logs_values.add_argument("--out", required=True, help="Output file path under --project-dir")
    logs_values.add_argument("--overwrite", action="store_true", help="Allow overwriting --out")
    logs_values.set_defaults(func=workers_logs_cmd.cmd_workers_logs_values, write_capable=True)

    logs_search = logs_sub.add_parser("search", help="Search stored logs/events by Error ID (file-only; dry-run by default)")
    logs_search.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    logs_search.add_argument("--error-id", required=True, help="UI Error ID / request id (x-request-id) to search for")
    logs_search.add_argument("--request-id-key", dest="request_id_key", default=None, help="Override request-id key (advanced)")
    logs_search.add_argument("--script-name", default=None, help="Optional script name constraint (best-effort)")
    logs_search.add_argument("--from", dest="from_ts", default=None, help="Unix-ms or RFC3339 (default: last 24h)")
    logs_search.add_argument("--to", dest="to_ts", default=None, help="Unix-ms or RFC3339 (default: now)")
    logs_search.add_argument("--limit", type=int, default=None, help="Optional limit (max 2000)")
    logs_search.add_argument("--dataset", action="append", default=[], help="Optional dataset name (repeatable)")
    logs_search.add_argument("--out", required=True, help="Output file path under --project-dir")
    logs_search.add_argument("--overwrite", action="store_true", help="Allow overwriting --out")
    logs_search.set_defaults(func=workers_logs_cmd.cmd_workers_logs_search, write_capable=True)

    tails = workers_sub.add_parser("tails", help="Workers tails (list + streaming)")
    tails_sub = tails.add_subparsers(dest="tails_cmd", required=True, parser_class=_ToolArgumentParser)
    tails_list = tails_sub.add_parser("list", help="List tails (GET only)")
    tails_list.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    tails_list.add_argument("--script-name", required=True, help="Script name")
    tails_list.set_defaults(func=workers_cmd.cmd_workers_tails_list, write_capable=False)
    tails_stream = tails_sub.add_parser(
        "stream", help="Stream tail logs to a file (PII-risk; file-only). Dry-run by default."
    )
    tails_stream.add_argument("--account-id", default=None, help="Account id (or use accounts set-default)")
    tails_stream.add_argument("--script-name", required=True, help="Script name")
    tails_stream.add_argument("--duration-s", dest="duration_s", type=int, default=60, help="Stream duration in seconds (default: 60)")
    tails_stream.add_argument("--out", required=True, help="Output file path under --project-dir")
    tails_stream.add_argument("--overwrite", action="store_true", help="Allow overwriting --out")
    tails_stream.set_defaults(func=workers_tails_stream_cmd.cmd_workers_tails_stream, write_capable=True)

    _PARSER_CACHE = p
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

def _redact_sensitive_argv(argv: list[str]) -> list[str]:
    """
    Redact sensitive CLI argument values from command strings written to stdout/audit logs/run index.

    This does not affect the actual parsed values (only the logged/printed command string).
    """
    redacted: list[str] = []
    i = 0
    while i < len(argv):
        tok = str(argv[i])
        if tok == "--email":
            redacted.append(tok)
            if i + 1 < len(argv):
                redacted.append("<REDACTED_EMAIL>")
                i += 2
                continue
            i += 1
            continue
        if tok.startswith("--email="):
            redacted.append("--email=<REDACTED_EMAIL>")
            i += 1
            continue
        redacted.append(tok)
        i += 1
    return redacted


def main(argv: list[str]) -> int:
    parser = build_parser()
    out = Output(mode=_output_mode_from_argv(argv))
    redaction_secrets: list[str] = []
    try:
        args = parser.parse_args(argv)
    except ValidationError as e:
        out.emit({"ok": False, "error": redact_secrets(str(e), redaction_secrets), "error_type": type(e).__name__})
        return 1
    except SystemExit as e:
        # `--help` and similar argparse exits. For parse errors, we raise ValidationError instead.
        try:
            return int(e.code or 0)
        except Exception:
            return 0
    if getattr(args, "cmd", None) == "pages":
        if getattr(args, "pages_apply", False):
            args.apply = True
        if getattr(args, "pages_yes", False):
            args.yes = True
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
            payload = {"ok": True, "tool": "cloudflare-api-tool", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"cloudflare-api-tool {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        audit_argv = _redact_sensitive_argv(argv)
        command_str = "cloudflare-api-tool " + " ".join(audit_argv)
        audit.bind_context(
            {
                "tool": "cloudflare-api-tool",
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
        if str(getattr(args, "cmd", "") or "") in {"runs", "onboarding", "config"}:
            ctx = {
                "cfg": None,
                "out": out,
                "audit": audit,
                "redaction_secrets": redaction_secrets,
                "tool": "cloudflare-api-tool",
                "tool_version": __version__,
                "command_str": command_str,
                "project_cfg": project_cfg,
                "project_dir": project_dir,
                "env_file": str(args.env_file),
                "timeout_s": None,
                "connect_timeout_s": None,
                "read_timeout_s": None,
                "timeout_profile": None,
                "progress": bool(args.progress),
                "cache_ttl_s": float(args.cache_ttl_s),
                "no_cache": bool(args.no_cache),
                "parallel": int(args.parallel),
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
            blocked_before_state_reason = _live_apply_before_state_block_reason(args)
            if blocked_before_state_reason:
                raise SafetyError(blocked_before_state_reason)
            rc = int(args.func(args, ctx))
            return rc

        cfg = load_config(args.env_file)
        redaction_secrets.clear()
        if cfg.token:
            redaction_secrets.append(cfg.token)
        env_fingerprint = f"{cfg.base_url}|{cfg.token_fingerprint}"

        # Timeout selection:
        # - Env file can set connect/read timeouts.
        # - --timeout-s overrides both (back-compat).
        # - --connect-timeout-s / --read-timeout-s override individually.
        # - Some Cloudflare surfaces are vendor-slow (Zero Trust); apply the slow profile unless the user overrides.
        auto_profile = "slow" if str(getattr(args, "cmd", "") or "") in {"zero-trust"} else "default"
        timeout_profile = str(args.timeout_profile or auto_profile)
        connect_timeout_s = float(cfg.connect_timeout_s)
        read_timeout_s = float(cfg.read_timeout_s)
        if timeout_profile == "slow":
            connect_timeout_s = max(connect_timeout_s, 10.0)
            read_timeout_s = max(read_timeout_s, 240.0)
        if args.timeout_s is not None:
            connect_timeout_s = float(args.timeout_s)
            read_timeout_s = float(args.timeout_s)
        if args.connect_timeout_s is not None:
            connect_timeout_s = float(args.connect_timeout_s)
        if args.read_timeout_s is not None:
            read_timeout_s = float(args.read_timeout_s)

        cache = None
        if not bool(args.no_cache) and float(args.cache_ttl_s) > 0:
            try:
                cache = ShortTtlCache(
                    cache_dir=cache_dir_for_env_file(str(args.env_file)),
                    fingerprint=env_fingerprint,
                    ttl_s=float(args.cache_ttl_s),
                )
            except Exception:
                cache = None

        cf = CloudflareClient(
            base_url=cfg.base_url,
            token=cfg.token,
            connect_timeout_s=connect_timeout_s,
            read_timeout_s=read_timeout_s,
            verbose=bool(args.verbose),
            progress=bool(args.progress),
            cache=cache,
            user_agent=f"cloudflare-api-tool/{__version__}",
        )
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "redaction_secrets": redaction_secrets,
            "tool": "cloudflare-api-tool",
            "tool_version": __version__,
            "command_str": command_str,
            "cf": cf,
            "project_cfg": project_cfg,
            "project_dir": project_dir,
            "env_file": str(args.env_file),
            "env_fingerprint": env_fingerprint,
            "timeout_s": None if args.timeout_s is None else float(args.timeout_s),
            "connect_timeout_s": connect_timeout_s,
            "read_timeout_s": read_timeout_s,
            "timeout_profile": timeout_profile,
            "progress": bool(args.progress),
            "cache_ttl_s": float(args.cache_ttl_s),
            "no_cache": bool(args.no_cache),
            "parallel": int(args.parallel),
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
                "tool": "cloudflare-api-tool",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "ack_no_snapshot": bool(args.ack_no_snapshot),
                "env_fingerprint": env_fingerprint,
                "run_id": run_ctx.run_id,
            }
        )
        blocked_before_state_reason = _live_apply_before_state_block_reason(args)
        if blocked_before_state_reason:
            raise SafetyError(blocked_before_state_reason)
        rc = int(args.func(args, ctx))

        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="cloudflare-api-tool",
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
        msg = redact_secrets(str(e), redaction_secrets)
        audit.write("refused", {"reason": msg})
        out.emit({"ok": True, "refused": True, "reasons": [msg], "refusal_type": "SafetyError"})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="cloudflare-api-tool",
            version=__version__,
            command=command_str if "command_str" in locals() else ("cloudflare-api-tool " + " ".join(_redact_sensitive_argv(argv))),
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 0
    except ToolError as e:
        msg = redact_secrets(str(e), redaction_secrets)
        audit.write("error", {"error": msg, "error_type": type(e).__name__})
        out.emit({"ok": False, "error": msg, "error_type": type(e).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="cloudflare-api-tool",
            version=__version__,
            command=command_str if "command_str" in locals() else ("cloudflare-api-tool " + " ".join(_redact_sensitive_argv(argv))),
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
        msg = redact_secrets(str(e), redaction_secrets)
        audit.write("error", {"error": msg, "error_type": type(e).__name__})
        out.emit({"ok": False, "error": msg, "error_type": type(e).__name__})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="cloudflare-api-tool",
            version=__version__,
            command=command_str if "command_str" in locals() else ("cloudflare-api-tool " + " ".join(_redact_sensitive_argv(argv))),
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
