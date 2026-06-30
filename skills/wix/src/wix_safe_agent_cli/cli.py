from __future__ import annotations

import argparse
import ast
import importlib
import json
import sys
import time
from functools import lru_cache
from pathlib import Path

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import ai_credits as ai_credits_cmd
from .commands import auth as auth_cmd
from .commands import b2b_site_transfer as b2b_site_transfer_cmd
from .commands import bi_event as bi_event_cmd
from .commands import balances as balances_cmd
from .commands import benefit_items as benefit_items_cmd
from .commands import brands_v3 as brands_v3_cmd
from .commands import catalog_versioning as catalog_versioning_cmd
from .commands import categories as categories_cmd
from .commands import partner_profiles as partner_profiles_cmd
from .commands import viewer as viewer_cmd
from .commands import app_instance as app_instance_cmd
from .commands import app_installation as app_installation_cmd
from .commands import app_installations as app_installations_cmd
from .commands import bookings_reader_v2 as bookings_reader_v2_cmd
from .commands import bookings_attendance as bookings_attendance_cmd
from .commands import bookings_external_calendars_v2 as bookings_external_calendars_v2_cmd
from .commands import bookings_policies as bookings_policies_cmd
from .commands import bookings_policy_snapshots as bookings_policy_snapshots_cmd
from .commands import bookings_resource_types_v2 as bookings_resource_types_v2_cmd
from .commands import bookings_resources_v2 as bookings_resources_v2_cmd
from .commands import bookings_service_options_v1 as bookings_service_options_v1_cmd
from .commands import bookings_services_v2 as bookings_services_v2_cmd
from .commands import bookings_staff_members as bookings_staff_members_cmd
from .commands import bookings_time_slots_v2 as bookings_time_slots_v2_cmd
from .commands import bookings_waitlist as bookings_waitlist_cmd
from .commands import bookings_writer_v2 as bookings_writer_v2_cmd
from .commands import custom_embeds as custom_embeds_cmd
from .commands import customizations_v3 as customizations_v3_cmd
from .commands import coupons as coupons_cmd
from .commands import donation_campaigns as donation_campaigns_cmd
from .commands import embedded_scripts as embedded_scripts_cmd
from .commands import editor_deep_link as editor_deep_link_cmd
from .commands import email_campaigns as email_campaigns_cmd
from .commands import events_categories as events_categories_cmd
from .commands import events_forms as events_forms_cmd
from .commands import events_guests as events_guests_cmd
from .commands import events_orders as events_orders_cmd
from .commands import events_policies_v2 as events_policies_v2_cmd
from .commands import events_ticket_reservations as events_ticket_reservations_cmd
from .commands import events_tickets as events_tickets_cmd
from .commands import events_schedule_items as events_schedule_items_cmd
from .commands import events_rsvps_v2 as events_rsvps_v2_cmd
from .commands import events_staff_members as events_staff_members_cmd
from .commands import events_v3 as events_v3_cmd
from .commands import events_ticket_definitions_v3 as events_ticket_definitions_v3_cmd
from .commands import events_settings as events_settings_cmd
from .commands import gift_cards as gift_cards_cmd
from .commands import pricing_plans as pricing_plans_cmd
from .commands import read_only_variants_v3 as read_only_variants_v3_cmd
from .commands import restaurants_item_labels as restaurants_item_labels_cmd
from .commands import restaurants_item_modifier_groups as restaurants_item_modifier_groups_cmd
from .commands import restaurants_item_modifiers as restaurants_item_modifiers_cmd
from .commands import restaurants_item_variants as restaurants_item_variants_cmd
from .commands import restaurants_items as restaurants_items_cmd
from .commands import restaurants_menus as restaurants_menus_cmd
from .commands import restaurants_online_order_availability_exceptions as restaurants_online_order_availability_exceptions_cmd
from .commands import restaurants_online_order_fulfillment_methods as restaurants_online_order_fulfillment_methods_cmd
from .commands import restaurants_online_order_operation_groups as restaurants_online_order_operation_groups_cmd
from .commands import restaurants_online_order_operations as restaurants_online_order_operations_cmd
from .commands import restaurants_online_order_menu_ordering_settings as restaurants_online_order_menu_ordering_settings_cmd
from .commands import restaurants_online_order_notification_recipients as restaurants_online_order_notification_recipients_cmd
from .commands import restaurants_online_order_service_fees as restaurants_online_order_service_fees_cmd
from .commands import restaurants_reservation_locations as restaurants_reservation_locations_cmd
from .commands import restaurants_reservations as restaurants_reservations_cmd
from .commands import restaurants_sections as restaurants_sections_cmd
from .commands import ribbons_v3 as ribbons_v3_cmd
from .commands import stores_inventory_items_v3 as stores_inventory_items_v3_cmd
from .commands import stores_info_sections_v3 as stores_info_sections_v3_cmd
from .commands import stores_locations_v3 as stores_locations_v3_cmd
from .commands import stores_products_v3 as stores_products_v3_cmd
from .commands import market_listing as market_listing_cmd
from .commands import secrets as secrets_cmd
from .commands import marketing_consent as marketing_consent_cmd
from .commands import multilingual_locales as multilingual_locales_cmd
from .commands import multilingual_locale_settings as multilingual_locale_settings_cmd
from .commands import multilingual_translation_schemas as multilingual_translation_schemas_cmd
from .commands import multilingual_translation_contents as multilingual_translation_contents_cmd
from .commands import multilingual_translation_published_contents as multilingual_translation_published_contents_cmd
from .commands import multilingual_machine_translation as multilingual_machine_translation_cmd
from .commands import multilingual_machine_translation_credit_data as multilingual_machine_translation_credit_data_cmd
from .commands import online_programs_instructor_v2 as online_programs_instructor_v2_cmd
from .commands import online_programs_programs as online_programs_programs_cmd
from .commands import sender_emails as sender_emails_cmd
from .commands import sender_details as sender_details_cmd
from .commands import sending_domains as sending_domains_cmd
from .commands import app_permissions as app_permissions_cmd
from .commands import analytics_data as analytics_data_cmd
from .commands import analytics_semantic_models as analytics_semantic_models_cmd
from .commands import async_jobs as async_jobs_cmd
from .commands import branches as branches_cmd
from .commands import calendar_schedules_v3 as calendar_schedules_v3_cmd
from .commands import site_plugins as site_plugins_cmd
from .commands import site_search as site_search_cmd
from .commands import contributors as contributors_cmd
from .commands import form_submissions as form_submissions_cmd
from .commands import domain_dns as domain_dns_cmd
from .commands import dns_propagation as dns_propagation_cmd
from .commands import domains as domains_cmd
from .commands import connected_domains as connected_domains_cmd
from .commands import data_collections as data_collections_cmd
from .commands import data_extension_schemas as data_extension_schemas_cmd
from .commands import data_folders as data_folders_cmd
from .commands import data_indexes as data_indexes_cmd
from .commands import data_permissions as data_permissions_cmd
from .commands import data_sharing as data_sharing_cmd
from .commands import data_items as data_items_cmd
from .commands import locations as locations_cmd
from .commands import contact_labels as contact_labels_cmd
from .commands import tags as tags_cmd
from .commands import site_actions as site_actions_cmd
from .commands import site_properties as site_properties_cmd
from .commands import site_urls as site_urls_cmd
from .commands import contacts as contacts_cmd
from .commands import accounts as accounts_cmd
from .commands import notifications as notifications_cmd
from .commands import order_billing as order_billing_cmd
from .commands import orders as orders_cmd
from .commands import payments as payments_cmd
from .commands import members as members_cmd
from .commands import files as files_cmd
from .commands import media_folders as media_folders_cmd
from .commands import sites as sites_cmd
from .commands import site_folders as site_folders_cmd
from .commands import projects as projects_cmd
from .commands import resellers as resellers_cmd
from .commands import loyalty_rewards as loyalty_rewards_cmd
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

    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def _find_subparsers(parser: argparse.ArgumentParser) -> argparse._SubParsersAction | None:
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action
    return None


@lru_cache(maxsize=None)
def _parser_argument_dests(module_name: str) -> frozenset[str]:
    module_path = Path(__file__).resolve().parent / "commands" / f"{module_name}.py"
    if not module_path.exists():
        return frozenset()
    try:
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return frozenset()

    dests: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "getattr":
            if (
                len(node.args) >= 2
                and isinstance(node.args[0], ast.Name)
                and node.args[0].id == "args"
                and isinstance(node.args[1], ast.Constant)
                and isinstance(node.args[1].value, str)
            ):
                dests.add(node.args[1].value)
        elif (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "args"
            and not node.attr.startswith("_")
        ):
            dests.add(node.attr)
        elif isinstance(node, ast.keyword) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            value = node.value.value
            if node.arg in {"attr", "field"} and (value.endswith("-json") or value.endswith("-id")):
                dests.add(value.replace("-", "_"))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value
            if value.endswith("-json") or value.endswith("-id"):
                dests.add(value.replace("-", "_"))
    return frozenset(dests)


def _add_backfill_args(parser: argparse.ArgumentParser, module_name: str) -> None:
    for dest in sorted(_parser_argument_dests(module_name)):
        if dest in {"func", "write_capable"}:
            continue
        flag = "--" + dest.replace("_", "-")
        if any(flag in action.option_strings for action in parser._actions):
            continue
        parser.add_argument(flag, dest=dest, nargs="?", const=True)


def _inventory_path() -> Path:
    return Path(__file__).resolve().parents[2] / "docs" / "official_inventory.json"


@lru_cache(maxsize=1)
def _implemented_inventory_commands() -> tuple[tuple[str, str, str | None, tuple[str, ...]], ...]:
    path = _inventory_path()
    if not path.exists():
        return ()
    try:
        inventory = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ()

    commands: list[tuple[str, str, str | None, tuple[str, ...]]] = []
    for family in inventory.get("families", []):
        for op in family.get("operations", []):
            flags = tuple(op.get("flags", []))
            if "implemented" not in flags:
                continue
            planned = op.get("planned_command")
            if not isinstance(planned, str) or not planned.startswith("wix-safe-agent-cli "):
                continue
            parts = planned.split()[1:]
            if len(parts) != 2:
                continue
            commands.append((parts[0], parts[1], op.get("http_method"), flags))
    return tuple(commands)


def _backfill_func(module: object, module_name: str, command_name: str):
    command_token = command_name.replace("-", "_")
    candidates = [f"cmd_{module_name}_{command_token}"]
    for prefix in ("list_", "get_", "query_", "search_", "count_"):
        if command_token.startswith(prefix):
            candidates.append(f"cmd_{module_name}_{prefix[:-1]}")
    for name in candidates:
        func = getattr(module, name, None)
        if func is not None:
            return func
    return None


def _backfill_write_capable(http_method: str | None, flags: tuple[str, ...], command_name: str) -> bool:
    flag_set = set(flags)
    if "plan-first-write" in flag_set or "ack-irreversible" in flag_set or "requires-ack-irreversible" in flag_set:
        return True
    read_prefixes = (
        "get",
        "list",
        "query",
        "search",
        "count",
        "check",
        "validate",
        "preview",
        "calculate",
    )
    if command_name.startswith("generate-") and command_name != "generate-summary":
        return True
    if command_name == "generate-summary":
        return False
    if command_name == "convert-from" or command_name == "convert-to":
        return False
    if command_name.startswith(read_prefixes):
        return False
    return http_method not in {None, "GET"}


def _register_inventory_backfill_commands(sub: argparse._SubParsersAction) -> None:
    module_cache: dict[str, object | None] = {}
    for family_name, command_name, http_method, flags in _implemented_inventory_commands():
        module_name = family_name.replace("-", "_")
        if module_name not in module_cache:
            try:
                module_cache[module_name] = importlib.import_module(f"{__package__}.commands.{module_name}")
            except ImportError:
                module_cache[module_name] = None
        module = module_cache[module_name]
        if module is None:
            continue

        func = _backfill_func(module, module_name, command_name)
        if func is None:
            continue

        if family_name in sub.choices:
            family_parser = sub.choices[family_name]
        else:
            family_parser = sub.add_parser(family_name, help=f"{family_name} commands")
        family_sub = _find_subparsers(family_parser)
        if family_sub is None:
            family_sub = family_parser.add_subparsers(
                dest=f"{module_name}_cmd",
                required=True,
                parser_class=_ToolArgumentParser,
            )
        if command_name in family_sub.choices:
            continue

        command_parser = family_sub.add_parser(command_name, help=f"{family_name} {command_name}")
        _add_backfill_args(command_parser, module_name)
        write_capable = _backfill_write_capable(http_method, flags, command_name)
        command_parser.set_defaults(func=func, write_capable=write_capable)


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
    p = _ToolArgumentParser(prog="wix-safe-agent-cli")
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

    token = auth_sub.add_parser("token", help="OAuth token helpers")
    token_sub = token.add_subparsers(dest="token_cmd", required=True, parser_class=_ToolArgumentParser)
    token_set = token_sub.add_parser("set", help="Store token JSON under .state/token.json")
    token_set.add_argument("--file", required=True, help="Token JSON file path (input)")
    token_set.set_defaults(func=auth_cmd.cmd_auth_token_set, write_capable=True)
    token_create = token_sub.add_parser("create", help="Create and store a Wix access token")
    token_create.set_defaults(func=auth_cmd.cmd_auth_token_create, write_capable=True)
    token_request = token_sub.add_parser(
        "request",
        help="Request and store a legacy custom-auth Wix access token",
    )
    token_request.add_argument("--code", required=True, help="Authorization code from the Wix install redirect")
    token_request.set_defaults(func=auth_cmd.cmd_auth_token_request, write_capable=True)
    token_refresh = token_sub.add_parser(
        "refresh",
        help="Refresh and store a Wix access token from a legacy refresh token",
    )
    token_refresh.add_argument(
        "--refresh-token",
        default=None,
        help="Optional legacy refresh token. Uses the local .state/token.json refresh_token when omitted.",
    )
    token_refresh.set_defaults(func=auth_cmd.cmd_auth_token_refresh, write_capable=True)
    token_inspect = token_sub.add_parser("inspect", help="Inspect token claims with Wix token-info")
    token_inspect.add_argument("--token", default=None, help="Optional token to inspect. Uses WIX_ACCESS_TOKEN or stored token when empty.")
    token_inspect.set_defaults(func=auth_cmd.cmd_auth_token_inspect, write_capable=False)
    token_status = token_sub.add_parser("status", help="Show token status (never prints token values)")
    token_status.set_defaults(func=auth_cmd.cmd_auth_token_status, write_capable=False)

    contacts = sub.add_parser("contacts", help="Read-only contacts methods")
    contacts_sub = contacts.add_subparsers(dest="contacts_cmd", required=True, parser_class=_ToolArgumentParser)
    contacts_list = contacts_sub.add_parser("list", help="List contacts")
    contacts_list.add_argument("--limit", type=int, default=None, help="Maximum contacts to return")
    contacts_list.add_argument("--offset", type=int, default=None, help="Number to skip in current sort order")
    contacts_list.add_argument("--sort-json", dest="sort_json", help="JSON list/object for sort fields")
    contacts_list.add_argument("--fields-json", dest="fields_json", help="JSON array of projected fields")
    contacts_list.add_argument("--fieldsets-json", dest="fieldsets_json", help="JSON array of fieldsets")
    contacts_list.set_defaults(func=contacts_cmd.cmd_contacts_list, write_capable=False)

    contacts_get = contacts_sub.add_parser("get", help="Get one contact")
    contacts_get.add_argument("--contact-id", required=True, help="Contact ID")
    contacts_get.add_argument("--fields-json", dest="fields_json", help="JSON array of projected fields")
    contacts_get.add_argument("--fieldsets-json", dest="fieldsets_json", help="JSON array of fieldsets")
    contacts_get.set_defaults(func=contacts_cmd.cmd_contacts_get, write_capable=False)

    contacts_query = contacts_sub.add_parser("query", help="Query contacts with Wix query options")
    contacts_query.add_argument("--query-json", dest="query_json", help="JSON object for full request query payload")
    contacts_query.add_argument("--filter-json", dest="filter_json", help="JSON query filter")
    contacts_query.add_argument("--sort-json", dest="sort_json", help="JSON sort object/list")
    contacts_query.add_argument("--search", dest="search", help="Exact text search")
    contacts_query.add_argument("--fields-json", dest="fields_json", help="JSON array of projected fields")
    contacts_query.add_argument("--limit", type=int, default=None, help="Max contacts to return")
    contacts_query.add_argument("--offset", type=int, default=None, help="Number to skip in current sort order")
    contacts_query.set_defaults(func=contacts_cmd.cmd_contacts_query, write_capable=False)

    loyalty_rewards = sub.add_parser("loyalty-rewards", help="Read and manage Wix Loyalty rewards")
    loyalty_rewards_sub = loyalty_rewards.add_subparsers(
        dest="loyalty_rewards_cmd", required=True, parser_class=_ToolArgumentParser
    )

    loyalty_rewards_list = loyalty_rewards_sub.add_parser("list", help="List Loyalty rewards")
    loyalty_rewards_list.add_argument(
        "--params-json",
        default="{}",
        help="Optional query parameters JSON object or @file",
    )
    loyalty_rewards_list.set_defaults(func=loyalty_rewards_cmd.cmd_loyalty_rewards_list, write_capable=False)

    loyalty_rewards_get = loyalty_rewards_sub.add_parser("get", help="Get one Loyalty reward")
    loyalty_rewards_get.add_argument("--reward-id", required=True, help="Reward ID")
    loyalty_rewards_get.set_defaults(func=loyalty_rewards_cmd.cmd_loyalty_rewards_get, write_capable=False)

    loyalty_rewards_query = loyalty_rewards_sub.add_parser("query", help="Query Loyalty rewards")
    loyalty_rewards_query.add_argument(
        "--query-json",
        default="{}",
        help="Official query body or @file",
    )
    loyalty_rewards_query.set_defaults(func=loyalty_rewards_cmd.cmd_loyalty_rewards_query, write_capable=False)

    loyalty_rewards_create = loyalty_rewards_sub.add_parser("create", help="Create one Loyalty reward")
    loyalty_rewards_create.add_argument(
        "--reward-json",
        required=True,
        help="Official create body with reward object or @file",
    )
    loyalty_rewards_create.set_defaults(func=loyalty_rewards_cmd.cmd_loyalty_rewards_create, write_capable=True)

    loyalty_rewards_update = loyalty_rewards_sub.add_parser("update", help="Update one Loyalty reward")
    loyalty_rewards_update.add_argument(
        "--reward-json",
        required=True,
        help="Official update body with reward object (including reward.id) or @file",
    )
    loyalty_rewards_update.set_defaults(func=loyalty_rewards_cmd.cmd_loyalty_rewards_update, write_capable=True)

    loyalty_rewards_delete = loyalty_rewards_sub.add_parser("delete", help="Delete one Loyalty reward")
    loyalty_rewards_delete.add_argument("--reward-id", required=True, help="Reward ID")
    loyalty_rewards_delete.set_defaults(func=loyalty_rewards_cmd.cmd_loyalty_rewards_delete, write_capable=True)

    loyalty_rewards_bulk_create = loyalty_rewards_sub.add_parser(
        "bulk-create", help="Create multiple Loyalty rewards"
    )
    loyalty_rewards_bulk_create.add_argument(
        "--rewards-json",
        required=True,
        help="Official bulk create body with rewards array or @file",
    )
    loyalty_rewards_bulk_create.set_defaults(
        func=loyalty_rewards_cmd.cmd_loyalty_rewards_bulk_create,
        write_capable=True,
    )

    contact_labels = sub.add_parser("contact-labels", help="Read/write CRM contact labels")
    contact_labels_sub = contact_labels.add_subparsers(dest="contact_labels_cmd", required=True, parser_class=_ToolArgumentParser)

    contact_labels_query = contact_labels_sub.add_parser("query", help="Query contact labels")
    contact_labels_query.add_argument("--query-json", required=True, help="JSON query payload")
    contact_labels_query.set_defaults(func=contact_labels_cmd.cmd_contact_labels_query, write_capable=False)

    contact_labels_list = contact_labels_sub.add_parser("list", help="List contact labels")
    contact_labels_list.set_defaults(func=contact_labels_cmd.cmd_contact_labels_list, write_capable=False)

    contact_labels_find_or_create = contact_labels_sub.add_parser("find-or-create", help="Find a label by name or create one")
    contact_labels_find_or_create.add_argument("--label-json", required=True, help="JSON label payload with displayName and optional fields")
    contact_labels_find_or_create.set_defaults(
        func=contact_labels_cmd.cmd_contact_labels_find_or_create, write_capable=True
    )

    contact_labels_get = contact_labels_sub.add_parser("get", help="Get one label by key")
    contact_labels_get.add_argument("--key", required=True, help="Label key")
    contact_labels_get.set_defaults(func=contact_labels_cmd.cmd_contact_labels_get, write_capable=False)

    contact_labels_update = contact_labels_sub.add_parser("update", help="Update one label by key")
    contact_labels_update.add_argument("--key", required=True, help="Label key")
    contact_labels_update.add_argument("--label-json", required=True, help="JSON label payload with fields to update")
    contact_labels_update.set_defaults(func=contact_labels_cmd.cmd_contact_labels_update, write_capable=True)

    contact_labels_delete = contact_labels_sub.add_parser("delete", help="Delete one label by key")
    contact_labels_delete.add_argument("--key", required=True, help="Label key")
    contact_labels_delete.set_defaults(func=contact_labels_cmd.cmd_contact_labels_delete, write_capable=True)

    data_collections = sub.add_parser("data-collections", help="CMS collection schema methods")
    data_collections_sub = data_collections.add_subparsers(
        dest="data_collections_cmd", required=True, parser_class=_ToolArgumentParser
    )
    data_collections_list = data_collections_sub.add_parser("list", help="List CMS data collections")
    data_collections_list.add_argument("--fields-json", dest="fields_json", help="JSON array of projected fields")
    data_collections_list.add_argument("--limit", type=int, default=None, help="Max collections to return")
    data_collections_list.add_argument("--offset", type=int, default=None, help="Collections to skip in current sort order")
    data_collections_list.add_argument("--sort-field-name", default=None, help="Field name to sort by")
    data_collections_list.add_argument("--sort-order", default=None, choices=("ASC", "DESC"), help="Sort order (ASC or DESC)")
    data_collections_list.add_argument(
        "--consistent-read",
        action="store_true",
        help="Read from primary DB for latest results",
    )
    data_collections_list.set_defaults(func=data_collections_cmd.cmd_data_collections_list, write_capable=False)

    data_collections_get = data_collections_sub.add_parser("get", help="Get one CMS data collection")
    data_collections_get.add_argument("--data-collection-id", required=True, help="ID of the collection")
    data_collections_get.add_argument("--fields-json", dest="fields_json", help="JSON array of projected fields")
    data_collections_get.add_argument(
        "--consistent-read",
        action="store_true",
        help="Read from primary DB for latest results",
    )
    data_collections_get.set_defaults(func=data_collections_cmd.cmd_data_collections_get, write_capable=False)

    data_sharing = sub.add_parser("data-sharing", help="CMS data sharing policy and connection methods")
    data_sharing_sub = data_sharing.add_subparsers(
        dest="data_sharing_cmd", required=True, parser_class=_ToolArgumentParser
    )
    data_sharing_list_policies = data_sharing_sub.add_parser("list-policies", help="List data sharing policies")
    data_sharing_list_policies.add_argument(
        "--data-collection-ids-json",
        default=None,
        help="Optional JSON array of data collection IDs to filter policies",
    )
    data_sharing_list_policies.set_defaults(
        func=data_sharing_cmd.cmd_data_sharing_list_policies, write_capable=False
    )
    data_sharing_get_policy = data_sharing_sub.add_parser("get-policy", help="Get one data sharing policy")
    data_sharing_get_policy.add_argument("--policy-id", required=True, help="Data sharing policy ID")
    data_sharing_get_policy.set_defaults(func=data_sharing_cmd.cmd_data_sharing_get_policy, write_capable=False)
    data_sharing_list_shared = data_sharing_sub.add_parser(
        "list-shared-collections", help="List shared data collections"
    )
    data_sharing_list_shared.add_argument(
        "--shared-with-current-site",
        action="store_true",
        default=None,
        help="Filter to collections shared with the current site",
    )
    data_sharing_list_shared.set_defaults(
        func=data_sharing_cmd.cmd_data_sharing_list_shared_collections, write_capable=False
    )
    data_sharing_create_policy = data_sharing_sub.add_parser("create-policy", help="Create a data sharing policy")
    data_sharing_create_policy.add_argument(
        "--policy-json",
        required=True,
        help="JSON policy object or full request body with dataSharingPolicy",
    )
    data_sharing_create_policy.set_defaults(
        func=data_sharing_cmd.cmd_data_sharing_create_policy, write_capable=True
    )
    data_sharing_update_policy = data_sharing_sub.add_parser("update-policy", help="Update a data sharing policy filter")
    data_sharing_update_policy.add_argument("--policy-id", required=True, help="Data sharing policy ID")
    data_sharing_update_policy.add_argument(
        "--policy-json",
        required=True,
        help="JSON policy object or full request body with dataSharingPolicy",
    )
    data_sharing_update_policy.set_defaults(
        func=data_sharing_cmd.cmd_data_sharing_update_policy, write_capable=True
    )
    data_sharing_delete_policy = data_sharing_sub.add_parser("delete-policy", help="Delete a data sharing policy")
    data_sharing_delete_policy.add_argument("--policy-id", required=True, help="Data sharing policy ID")
    data_sharing_delete_policy.set_defaults(
        func=data_sharing_cmd.cmd_data_sharing_delete_policy, write_capable=True
    )
    data_sharing_connect = data_sharing_sub.add_parser("connect", help="Connect to a shared data collection")
    data_sharing_connect.add_argument(
        "--connection-json",
        required=True,
        help="JSON request body, including namespace",
    )
    data_sharing_connect.set_defaults(func=data_sharing_cmd.cmd_data_sharing_connect, write_capable=True)
    data_sharing_disconnect = data_sharing_sub.add_parser("disconnect", help="Disconnect from a shared data collection")
    data_sharing_disconnect.add_argument(
        "--connection-json",
        required=True,
        help="JSON request body, including namespace",
    )
    data_sharing_disconnect.set_defaults(func=data_sharing_cmd.cmd_data_sharing_disconnect, write_capable=True)

    data_collections_delete = data_collections_sub.add_parser("delete", help="Delete one CMS data collection")
    data_collections_delete.add_argument("--data-collection-id", required=True, help="ID of the collection to delete")
    data_collections_delete.set_defaults(func=data_collections_cmd.cmd_data_collections_delete, write_capable=True)

    data_collections_create = data_collections_sub.add_parser("create", help="Create one CMS data collection")
    data_collections_create.add_argument("--collection-id", required=True, help="ID of the new collection")
    data_collections_create.add_argument("--display-name", default=None, help="Display name of the collection")
    data_collections_create.add_argument("--display-field", default=None, help="Display field for this collection")
    data_collections_create.add_argument(
        "--field-json",
        required=True,
        action="append",
        dest="field_json",
        help="Repeatable JSON object or @file with key/type and optional displayName",
    )
    data_collections_create.add_argument("--permission-insert", default="ADMIN", help="Permission for inserts (default: ADMIN)")
    data_collections_create.add_argument("--permission-update", default="ADMIN", help="Permission for updates (default: ADMIN)")
    data_collections_create.add_argument("--permission-remove", default="ADMIN", help="Permission for removes (default: ADMIN)")
    data_collections_create.add_argument("--permission-read", default="ADMIN", help="Permission for reads (default: ADMIN)")
    data_collections_create.set_defaults(func=data_collections_cmd.cmd_data_collections_create, write_capable=True)

    data_collections_update = data_collections_sub.add_parser("update", help="Update one CMS data collection")
    data_collections_update.add_argument("--data-collection-id", required=True, help="ID of the collection to update")
    data_collections_update.add_argument("--display-name", default=None, help="Display name override")
    data_collections_update.add_argument("--display-field", default=None, help="Display field override")
    data_collections_update.add_argument(
        "--field-json",
        action="append",
        dest="field_json",
        help="Repeatable JSON object or @file with key/type and optional displayName",
    )
    data_collections_update.add_argument("--permission-insert", default=None, help="Permission for inserts")
    data_collections_update.add_argument("--permission-update", default=None, help="Permission for updates")
    data_collections_update.add_argument("--permission-remove", default=None, help="Permission for removes")
    data_collections_update.add_argument("--permission-read", default=None, help="Permission for reads")
    data_collections_update.set_defaults(func=data_collections_cmd.cmd_data_collections_update, write_capable=True)

    data_collections_patch = data_collections_sub.add_parser("patch", help="Patch one CMS data collection")
    data_collections_patch.add_argument("--data-collection-id", required=True, help="ID of the collection to patch")
    data_collections_patch.add_argument("--display-name", default=None, help="Display name override")
    data_collections_patch.add_argument("--display-field", default=None, help="Display field override")
    data_collections_patch.add_argument("--permission-insert", default=None, help="Permission for inserts")
    data_collections_patch.add_argument("--permission-update", default=None, help="Permission for updates")
    data_collections_patch.add_argument("--permission-remove", default=None, help="Permission for removes")
    data_collections_patch.add_argument("--permission-read", default=None, help="Permission for reads")
    data_collections_patch.set_defaults(func=data_collections_cmd.cmd_data_collections_patch, write_capable=True)

    data_collections_create_field = data_collections_sub.add_parser("create-field", help="Create one CMS data collection field")
    data_collections_create_field.add_argument("--data-collection-id", required=True, help="ID of the collection")
    data_collections_create_field.add_argument(
        "--field-json",
        required=True,
        dest="field_json",
        help="JSON object or @file with key/type and optional field attributes",
    )
    data_collections_create_field.set_defaults(func=data_collections_cmd.cmd_data_collections_create_field, write_capable=True)

    data_collections_update_field = data_collections_sub.add_parser("update-field", help="Replace one CMS data collection field")
    data_collections_update_field.add_argument("--data-collection-id", required=True, help="ID of the collection")
    data_collections_update_field.add_argument(
        "--field-json",
        required=True,
        dest="field_json",
        help="JSON object or @file with key/type and optional field attributes",
    )
    data_collections_update_field.set_defaults(func=data_collections_cmd.cmd_data_collections_update_field, write_capable=True)

    data_collections_patch_field = data_collections_sub.add_parser("patch-field", help="Patch one CMS data collection field")
    data_collections_patch_field.add_argument("--data-collection-id", required=True, help="ID of the collection")
    data_collections_patch_field.add_argument(
        "--field-json",
        required=True,
        dest="field_json",
        help="JSON object or @file with key and patch attributes",
    )
    data_collections_patch_field.set_defaults(func=data_collections_cmd.cmd_data_collections_patch_field, write_capable=True)

    data_collections_delete_field = data_collections_sub.add_parser("delete-field", help="Delete one CMS data collection field")
    data_collections_delete_field.add_argument("--data-collection-id", required=True, help="ID of the collection")
    data_collections_delete_field.add_argument("--field-key", required=True, help="Field key to delete")
    data_collections_delete_field.set_defaults(func=data_collections_cmd.cmd_data_collections_delete_field, write_capable=True)

    data_collections_add_plugin = data_collections_sub.add_parser("add-plugin", help="Add one CMS collection plugin")
    data_collections_add_plugin.add_argument("--data-collection-id", required=True, help="ID of the collection")
    data_collections_add_plugin.add_argument(
        "--plugin-json",
        required=True,
        dest="plugin_json",
        help="JSON object or @file describing plugin config",
    )
    data_collections_add_plugin.set_defaults(func=data_collections_cmd.cmd_data_collections_add_plugin, write_capable=True)

    data_collections_delete_plugin = data_collections_sub.add_parser("delete-plugin", help="Delete one CMS collection plugin")
    data_collections_delete_plugin.add_argument("--data-collection-id", required=True, help="ID of the collection")
    data_collections_delete_plugin.add_argument("--plugin-type", required=True, help="Plugin type to remove")
    data_collections_delete_plugin.set_defaults(
        func=data_collections_cmd.cmd_data_collections_delete_plugin,
        write_capable=True,
    )

    data_extension_schemas = sub.add_parser("data-extension-schemas", help="Data extension schema methods")
    data_extension_schemas_sub = data_extension_schemas.add_subparsers(
        dest="data_extension_schemas_cmd", required=True, parser_class=_ToolArgumentParser
    )
    data_extension_schemas_list = data_extension_schemas_sub.add_parser("list", help="List data extension schemas for one FQDN")
    data_extension_schemas_list.add_argument("--fqdn", required=True, help="FQDN for the Wix object to extend")
    data_extension_schemas_list.add_argument("--namespaces-json", dest="namespaces_json", help="JSON array of namespaces to filter")
    data_extension_schemas_list.add_argument("--fields-json", dest="fields_json", help="JSON array of projected fields")
    data_extension_schemas_list.add_argument(
        "--extension-points-json",
        dest="extension_points_json",
        help="JSON array of extension points to filter",
    )
    data_extension_schemas_list.set_defaults(
        func=data_extension_schemas_cmd.cmd_data_extension_schemas_list,
        write_capable=False,
    )

    data_extension_schemas_create = data_extension_schemas_sub.add_parser("create", help="Create one user-defined data extension schema")
    data_extension_schemas_create.add_argument(
        "--data-extension-schema-json",
        required=True,
        dest="data_extension_schema_json",
        help="JSON object or @file describing the schema",
    )
    data_extension_schemas_create.set_defaults(
        func=data_extension_schemas_cmd.cmd_data_extension_schemas_create,
        write_capable=True,
    )

    data_extension_schemas_update = data_extension_schemas_sub.add_parser("update", help="Update one user-defined data extension schema")
    data_extension_schemas_update.add_argument(
        "--data-extension-schema-json",
        required=True,
        dest="data_extension_schema_json",
        help="JSON object or @file describing the schema",
    )
    data_extension_schemas_update.set_defaults(
        func=data_extension_schemas_cmd.cmd_data_extension_schemas_update,
        write_capable=True,
    )

    data_extension_schemas_delete = data_extension_schemas_sub.add_parser(
        "delete-user-defined-fields",
        help="Archive user-defined fields from one data extension schema",
    )
    data_extension_schemas_delete.add_argument(
        "--data-extension-schema-id",
        required=True,
        dest="data_extension_schema_id",
        help="Data extension schema ID",
    )
    data_extension_schemas_delete.add_argument("--fqdn", required=True, help="FQDN for the Wix object to extend")
    data_extension_schemas_delete.add_argument(
        "--fields-to-delete-json",
        required=True,
        dest="fields_to_delete_json",
        help="JSON array of user-defined field paths to archive",
    )
    data_extension_schemas_delete.set_defaults(
        func=data_extension_schemas_cmd.cmd_data_extension_schemas_delete_user_defined_fields,
        write_capable=True,
    )

    data_indexes = sub.add_parser("data-indexes", help="CMS index management methods")
    data_indexes_sub = data_indexes.add_subparsers(dest="data_indexes_cmd", required=True, parser_class=_ToolArgumentParser)

    data_indexes_list = data_indexes_sub.add_parser("list", help="List CMS data collection indexes")
    data_indexes_list.add_argument("--data-collection-id", required=True, help="ID of the collection")
    data_indexes_list.add_argument("--limit", type=int, default=None, help="Max indexes to return")
    data_indexes_list.add_argument("--offset", type=int, default=None, help="Indexes to skip in current sort order")
    data_indexes_list.set_defaults(func=data_indexes_cmd.cmd_data_indexes_list, write_capable=False)

    data_indexes_create = data_indexes_sub.add_parser("create", help="Create one CMS data collection index")
    data_indexes_create.add_argument("--data-collection-id", required=True, help="ID of the collection")
    data_indexes_create.add_argument(
        "--index-json",
        required=True,
        dest="index_json",
        help="JSON object or @file with index name and fields",
    )
    data_indexes_create.set_defaults(func=data_indexes_cmd.cmd_data_indexes_create, write_capable=True)

    data_indexes_drop = data_indexes_sub.add_parser("drop", help="Drop one CMS data collection index")
    data_indexes_drop.add_argument("--data-collection-id", required=True, help="ID of the collection")
    data_indexes_drop.add_argument("--index-name", required=True, help="Index name")
    data_indexes_drop.set_defaults(func=data_indexes_cmd.cmd_data_indexes_drop, write_capable=True)

    data_folders = sub.add_parser("data-folders", help="CMS collection folder methods")
    data_folders_sub = data_folders.add_subparsers(dest="data_folders_cmd", required=True, parser_class=_ToolArgumentParser)

    data_folders_get = data_folders_sub.add_parser("get", help="Get one CMS collection folder or the root folder")
    data_folders_get.add_argument("--folder-id", default=None, help="Folder ID; omit to get the root folder")
    data_folders_get.set_defaults(func=data_folders_cmd.cmd_data_folders_get, write_capable=False)

    data_folders_create = data_folders_sub.add_parser("create", help="Create one CMS collection folder")
    data_folders_create.add_argument("--name", required=True, help="Folder name")
    data_folders_create.add_argument("--description", default=None, help="Folder description")
    data_folders_create.set_defaults(func=data_folders_cmd.cmd_data_folders_create, write_capable=True)

    data_folders_update = data_folders_sub.add_parser("update", help="Update one CMS collection folder")
    data_folders_update.add_argument("--folder-id", required=True, help="Folder ID")
    data_folders_update.add_argument("--name", default=None, help="Updated folder name")
    data_folders_update.add_argument("--description", default=None, help="Updated folder description")
    data_folders_update.set_defaults(func=data_folders_cmd.cmd_data_folders_update, write_capable=True)

    data_folders_delete = data_folders_sub.add_parser("delete", help="Delete one CMS collection folder")
    data_folders_delete.add_argument("--folder-id", required=True, help="Folder ID")
    data_folders_delete.set_defaults(func=data_folders_cmd.cmd_data_folders_delete, write_capable=True)

    data_folders_create_ref = data_folders_sub.add_parser(
        "create-collection-reference",
        help="Put one data collection into a CMS folder",
    )
    data_folders_create_ref.add_argument("--collection-name", required=True, help="Collection display name")
    data_folders_create_ref.add_argument("--folder-id", default=None, help="Folder ID; omit for the root folder")
    data_folders_create_ref.set_defaults(
        func=data_folders_cmd.cmd_data_folders_create_collection_reference,
        write_capable=True,
    )

    data_folders_get_refs = data_folders_sub.add_parser(
        "get-collection-references",
        help="Get all folder references for one data collection",
    )
    data_folders_get_refs.add_argument("--collection-name", required=True, help="Collection display name")
    data_folders_get_refs.set_defaults(
        func=data_folders_cmd.cmd_data_folders_get_collection_references,
        write_capable=False,
    )

    data_folders_delete_ref = data_folders_sub.add_parser(
        "delete-collection-reference",
        help="Delete one CMS collection-folder reference",
    )
    data_folders_delete_ref.add_argument("--collection-name", required=True, help="Collection display name")
    data_folders_delete_ref.add_argument("--folder-id", default=None, help="Folder ID; omit for the root folder")
    data_folders_delete_ref.set_defaults(
        func=data_folders_cmd.cmd_data_folders_delete_collection_reference,
        write_capable=True,
    )

    data_permissions = sub.add_parser("data-permissions", help="CMS collection permission methods")
    data_permissions_sub = data_permissions.add_subparsers(
        dest="data_permissions_cmd", required=True, parser_class=_ToolArgumentParser
    )
    data_permissions_get = data_permissions_sub.add_parser("get", help="Get collection permissions")
    data_permissions_get.add_argument("--data-collection-id", required=True, help="Collection ID")
    data_permissions_get.set_defaults(func=data_permissions_cmd.cmd_data_permissions_get, write_capable=False)

    data_permissions_get_my = data_permissions_sub.add_parser("get-my", help="Get the current caller's effective permissions")
    data_permissions_get_my.add_argument("--data-collection-id", required=True, help="Collection ID")
    data_permissions_get_my.set_defaults(func=data_permissions_cmd.cmd_data_permissions_get_my, write_capable=False)

    data_permissions_update = data_permissions_sub.add_parser("update", help="Update collection-level permissions")
    data_permissions_update.add_argument("--data-collection-id", required=True, help="Collection ID")
    data_permissions_update.add_argument("--item-read", required=True, help="Collection read access level")
    data_permissions_update.add_argument("--item-insert", required=True, help="Collection insert access level")
    data_permissions_update.add_argument("--item-update", required=True, help="Collection update access level")
    data_permissions_update.add_argument("--item-remove", required=True, help="Collection remove access level")
    data_permissions_update.set_defaults(func=data_permissions_cmd.cmd_data_permissions_update, write_capable=True)

    data_permissions_add_special = data_permissions_sub.add_parser("add-special", help="Add special permissions for one user or role")
    data_permissions_add_special.add_argument("--data-collection-id", required=True, help="Collection ID")
    data_permissions_add_special.add_argument("--user-id", default=None, help="Wix user ID for special permissions")
    data_permissions_add_special.add_argument("--policy-id", default=None, help="Wix role policy ID for special permissions")
    data_permissions_add_special.add_argument("--item-read", required=True, help="Special read access")
    data_permissions_add_special.add_argument("--item-insert", required=True, help="Special insert access")
    data_permissions_add_special.add_argument("--item-update", required=True, help="Special update access")
    data_permissions_add_special.add_argument("--item-remove", required=True, help="Special remove access")
    data_permissions_add_special.set_defaults(func=data_permissions_cmd.cmd_data_permissions_add_special, write_capable=True)

    data_permissions_update_special = data_permissions_sub.add_parser("update-special", help="Update special permissions for one user or role")
    data_permissions_update_special.add_argument("--data-collection-id", required=True, help="Collection ID for readback verification")
    data_permissions_update_special.add_argument("--special-permissions-id", required=True, help="Special permissions ID")
    data_permissions_update_special.add_argument("--user-id", default=None, help="Wix user ID for special permissions")
    data_permissions_update_special.add_argument("--policy-id", default=None, help="Wix role policy ID for special permissions")
    data_permissions_update_special.add_argument("--item-read", required=True, help="Special read access")
    data_permissions_update_special.add_argument("--item-insert", required=True, help="Special insert access")
    data_permissions_update_special.add_argument("--item-update", required=True, help="Special update access")
    data_permissions_update_special.add_argument("--item-remove", required=True, help="Special remove access")
    data_permissions_update_special.set_defaults(func=data_permissions_cmd.cmd_data_permissions_update_special, write_capable=True)

    data_permissions_remove_special = data_permissions_sub.add_parser("remove-special", help="Remove special permissions")
    data_permissions_remove_special.add_argument("--data-collection-id", required=True, help="Collection ID for readback verification")
    data_permissions_remove_special.add_argument("--special-permissions-id", required=True, help="Special permissions ID")
    data_permissions_remove_special.set_defaults(func=data_permissions_cmd.cmd_data_permissions_remove_special, write_capable=True)

    members = sub.add_parser("members", help="Read-only member methods")
    members_sub = members.add_subparsers(dest="members_cmd", required=True, parser_class=_ToolArgumentParser)

    members_list = members_sub.add_parser("list", help="List members")
    members_list.add_argument("--limit", type=int, default=None, help="Maximum members to return")
    members_list.add_argument("--offset", type=int, default=None, help="Number to skip in current sort order")
    members_list.add_argument("--sort-json", dest="sort_json", help="JSON list/object for sort fields")
    members_list.add_argument("--fieldsets-json", dest="fieldsets_json", help="JSON array of fieldsets")
    members_list.set_defaults(func=members_cmd.cmd_members_list, write_capable=False)

    members_get = members_sub.add_parser("get", help="Get one member")
    members_get.add_argument("--member-id", required=True, help="Member ID")
    members_get.add_argument("--fieldsets-json", dest="fieldsets_json", help="JSON array of fieldsets")
    members_get.set_defaults(func=members_cmd.cmd_members_get, write_capable=False)

    members_query = members_sub.add_parser("query", help="Query members with Wix query payload")
    members_query.add_argument("--query-json", dest="query_json", help="JSON query object or full request payload")
    members_query.add_argument("--fieldsets-json", dest="fieldsets_json", help="JSON array of fieldsets")
    members_query.set_defaults(func=members_cmd.cmd_members_query, write_capable=False)

    notifications = sub.add_parser("notifications", help="Send Wix notifications")
    notifications_sub = notifications.add_subparsers(dest="notifications_cmd", required=True, parser_class=_ToolArgumentParser)
    notifications_notify = notifications_sub.add_parser("notify", help="Send one notification")
    notifications_notify.add_argument("--notification-template-id", required=True, help="Wix notification template ID")
    notifications_notify.add_argument(
        "--dynamic-values-json",
        dest="dynamic_values_json",
        default=None,
        help="JSON map of placeholder -> {text: string}; pass with @file for file input",
    )
    notifications_notify.add_argument(
        "--notify-json",
        dest="notify_json",
        default=None,
        help="Optional full request body JSON override for /notifications/v3/notify",
    )
    notifications_notify.set_defaults(func=notifications_cmd.cmd_notifications_notify, write_capable=True)

    accounts = sub.add_parser("accounts", help="Account-level account methods")
    accounts_sub = accounts.add_subparsers(dest="accounts_cmd", required=True, parser_class=_ToolArgumentParser)
    accounts_get = accounts_sub.add_parser("get", help="Get one account")
    accounts_get.add_argument("--account-id", required=True, help="Account ID (GUID)")
    accounts_get.set_defaults(func=accounts_cmd.cmd_accounts_get, write_capable=False)

    accounts_list_child_accounts = accounts_sub.add_parser(
        "list-child-accounts",
        help="List child accounts for the current account",
    )
    accounts_list_child_accounts.add_argument("--limit", type=int, default=None, help="Results limit (0-50)")
    accounts_list_child_accounts.add_argument("--offset", type=int, default=None, help="Results offset (0 or greater)")
    accounts_list_child_accounts.set_defaults(func=accounts_cmd.cmd_accounts_list_child_accounts, write_capable=False)

    contributors = sub.add_parser("contributors", help="Site contributor methods")
    contributors_sub = contributors.add_subparsers(dest="contributors_cmd", required=True, parser_class=_ToolArgumentParser)
    contributors_query = contributors_sub.add_parser("query", help="Query contributors for the current site context")
    contributors_query.add_argument(
        "--policy-ids-json",
        dest="policy_ids_json",
        help="Optional JSON array of role policy IDs to filter by",
    )
    contributors_query.set_defaults(func=contributors_cmd.cmd_contributors_query, write_capable=False)
    contributors_remove = contributors_sub.add_parser("remove", help="Remove a contributor from the current site context")
    contributors_remove.add_argument("--account-id", required=True, help="Contributor account ID to remove")
    contributors_remove.add_argument("--site-id", required=True, help="Wix site ID for deterministic contributor targeting")
    contributors_remove.set_defaults(func=contributors_cmd.cmd_contributors_remove, write_capable=True)
    contributors_change_role = contributors_sub.add_parser(
        "change-role",
        help="Replace all roles for one contributor on the current site context",
    )
    contributors_change_role.add_argument("--account-id", required=True, help="Contributor account ID to update")
    contributors_change_role.add_argument("--site-id", required=True, help="Wix site ID for deterministic targeting")
    contributors_change_role.add_argument(
        "--role-ids-json",
        required=True,
        dest="role_ids_json",
        help="JSON array of role GUIDs to assign",
    )
    contributors_change_role.set_defaults(func=contributors_cmd.cmd_contributors_change_role, write_capable=True)
    contributors_change_contributor_location = contributors_sub.add_parser(
        "change-contributor-location",
        help="Replace all locations for one contributor on the current site context",
    )
    contributors_change_contributor_location.add_argument(
        "--account-id", required=True, help="Contributor account ID to update"
    )
    contributors_change_contributor_location.add_argument(
        "--site-id", required=True, help="Wix site ID for deterministic targeting"
    )
    contributors_change_contributor_location.add_argument(
        "--location-ids-json",
        required=True,
        dest="location_ids_json",
        help="JSON array of location GUIDs to assign",
    )
    contributors_change_contributor_location.set_defaults(
        func=contributors_cmd.cmd_contributors_change_contributor_location,
        write_capable=True,
    )

    locations = sub.add_parser("locations", help="Read/write Wix location methods")
    locations_sub = locations.add_subparsers(dest="locations_cmd", required=True, parser_class=_ToolArgumentParser)

    locations_list = locations_sub.add_parser("list", help="List locations")
    locations_list.add_argument("--include-archived", action="store_true", help="Include archived locations")
    locations_list.add_argument("--authorized-only", action="store_true", help="Only include authorized locations")
    locations_list.add_argument("--limit", type=int, default=None, help="Max locations to return")
    locations_list.add_argument("--offset", type=int, default=None, help="Locations to skip in current sort order")
    locations_list.add_argument("--sort-field", default=None, help="Field to sort by")
    locations_list.add_argument("--sort-order", default=None, choices=("ASC", "DESC"), help="Sort order")
    locations_list.set_defaults(func=locations_cmd.cmd_locations_list, write_capable=False)

    locations_query = locations_sub.add_parser("query", help="Query locations")
    locations_query.add_argument("--query-json", required=True, dest="query_json", help="JSON object or full request payload")
    locations_query.add_argument("--authorized-only", action="store_true", help="Only include authorized locations")
    locations_query.set_defaults(func=locations_cmd.cmd_locations_query, write_capable=False)

    locations_get = locations_sub.add_parser("get", help="Get one location by id")
    locations_get.add_argument("--location-id", required=True, help="Location ID")
    locations_get.set_defaults(func=locations_cmd.cmd_locations_get, write_capable=False)

    locations_create = locations_sub.add_parser("create", help="Create one location")
    locations_create.add_argument("--location-json", required=True, help="JSON location payload")
    locations_create.set_defaults(func=locations_cmd.cmd_locations_create, write_capable=True)

    locations_update = locations_sub.add_parser("update", help="Update one location by id (full object)")
    locations_update.add_argument("--location-id", required=True, help="Location ID")
    locations_update.add_argument("--location-json", required=True, help="JSON location payload")
    locations_update.set_defaults(func=locations_cmd.cmd_locations_update, write_capable=True)

    locations_archive = locations_sub.add_parser("archive", help="Archive one location")
    locations_archive.add_argument("--location-id", required=True, help="Location ID")
    locations_archive.set_defaults(func=locations_cmd.cmd_locations_archive, write_capable=True)

    locations_set_default = locations_sub.add_parser("set-default", help="Set one location as default")
    locations_set_default.add_argument("--location-id", required=True, help="Location ID")
    locations_set_default.set_defaults(func=locations_cmd.cmd_locations_set_default, write_capable=True)

    tags = sub.add_parser("tags", help="Read/write Wix tags methods")
    tags_sub = tags.add_subparsers(dest="tags_cmd", required=True, parser_class=_ToolArgumentParser)

    tags_list = tags_sub.add_parser("list", help="List tags for one FQDN")
    tags_list.add_argument("--fqdn", required=True, help="Fully Qualified Domain Name, such as wix.ecom.v1.order")
    tags_list.set_defaults(func=tags_cmd.cmd_tags_list, write_capable=False)

    tags_get = tags_sub.add_parser("get", help="Get one tag by id")
    tags_get.add_argument("--tag-id", required=True, help="Tag ID")
    tags_get.set_defaults(func=tags_cmd.cmd_tags_get, write_capable=False)

    tags_create = tags_sub.add_parser("create", help="Create one tag")
    tags_create.add_argument("--tag-json", required=True, help="JSON tag payload with fqdn and name")
    tags_create.set_defaults(func=tags_cmd.cmd_tags_create, write_capable=True)

    tags_update = tags_sub.add_parser("update", help="Update one tag by id")
    tags_update.add_argument("--tag-id", required=True, help="Tag ID")
    tags_update.add_argument("--tag-json", required=True, help="JSON tag payload with revision and name")
    tags_update.set_defaults(func=tags_cmd.cmd_tags_update, write_capable=True)

    tags_delete = tags_sub.add_parser("delete", help="Delete one tag by id")
    tags_delete.add_argument("--tag-id", required=True, help="Tag ID")
    tags_delete.set_defaults(func=tags_cmd.cmd_tags_delete, write_capable=True)

    app_installations = sub.add_parser("app-installations", help="Read-only app installation methods")
    app_installations_sub = app_installations.add_subparsers(
        dest="app_installations_cmd", required=True, parser_class=_ToolArgumentParser
    )
    app_installations_query = app_installations_sub.add_parser("query", help="Query app installations")
    app_installations_query.add_argument("--query-json", dest="query_json", help="JSON query options payload")
    app_installations_query.add_argument("--filter-json", dest="filter_json", help="JSON filter object")
    app_installations_query.add_argument("--sort-json", dest="sort_json", help="JSON sort object/list")
    app_installations_query.add_argument("--fields-json", dest="fields_json", help="JSON array of projected fields")
    app_installations_query.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    app_installations_query.add_argument("--limit", type=int, default=None, help="Max installations to return")
    app_installations_query.set_defaults(func=app_installations_cmd.cmd_app_installations_query, write_capable=False)

    app_installations_search = app_installations_sub.add_parser("search", help="Search app installations")
    app_installations_search.add_argument("--search", default=None, help="Free-text search expression")
    app_installations_search.add_argument("--search-json", dest="search_json", help="JSON request override for search payload")
    app_installations_search.add_argument("--fields-json", dest="fields_json", help="JSON array of projected fields")
    app_installations_search.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    app_installations_search.add_argument("--limit", type=int, default=None, help="Max installations to return")
    app_installations_search.set_defaults(func=app_installations_cmd.cmd_app_installations_search, write_capable=False)

    app_instance = sub.add_parser("app-instance", help="Read-only app instance methods")
    app_instance_sub = app_instance.add_subparsers(dest="app_instance_cmd", required=True, parser_class=_ToolArgumentParser)
    app_instance_get = app_instance_sub.add_parser("get", help="Get app instance state")
    app_instance_get.set_defaults(func=app_instance_cmd.cmd_app_instance_get, write_capable=False)

    app_installation = sub.add_parser("app-installation", help="App installation methods")
    app_installation_sub = app_installation.add_subparsers(
        dest="app_installation_cmd", required=True, parser_class=_ToolArgumentParser
    )
    app_installation_get_installed = app_installation_sub.add_parser("get-installed", help="List installed apps")
    app_installation_get_installed.set_defaults(
        func=app_installation_cmd.cmd_app_installation_get_installed,
        write_capable=False,
    )

    app_installation_is_permitted = app_installation_sub.add_parser("is-permitted", help="Check whether an install is permitted")
    app_installation_is_permitted.add_argument(
        "--request-json",
        required=True,
        help="JSON object or @file with the is-permitted request body",
    )
    app_installation_is_permitted.set_defaults(
        func=app_installation_cmd.cmd_app_installation_is_permitted,
        write_capable=False,
    )

    app_installation_install = app_installation_sub.add_parser("install", help="Install one app")
    app_installation_install.add_argument("--tenant-json", required=True, help="JSON tenant object or @file")
    app_installation_install.add_argument("--app-def-id", required=True, help="App definition ID")
    app_installation_install.add_argument(
        "--enabled",
        choices=("true", "false"),
        default="true",
        help="Whether the installed app is enabled (default: true)",
    )
    app_installation_install.add_argument("--version", default=None, help="Optional app version")
    app_installation_install.set_defaults(func=app_installation_cmd.cmd_app_installation_install, write_capable=True)

    app_installation_install_from_share_url = app_installation_sub.add_parser(
        "install-from-share-url",
        help="Install one app from a share URL",
    )
    app_installation_install_from_share_url.add_argument("--tenant-json", required=True, help="JSON tenant object or @file")
    app_installation_install_from_share_url.add_argument("--share-url-id", required=True, help="Share URL ID")
    app_installation_install_from_share_url.add_argument("--dev-override-id", default=None, help="Optional dev override ID")
    app_installation_install_from_share_url.set_defaults(
        func=app_installation_cmd.cmd_app_installation_install_from_share_url,
        write_capable=True,
    )

    app_installation_uninstall = app_installation_sub.add_parser("uninstall", help="Uninstall one app")
    app_installation_uninstall.add_argument("--tenant-json", required=True, help="JSON tenant object or @file")
    app_installation_uninstall.add_argument("--app-def-id", required=True, help="App definition ID")
    app_installation_uninstall.set_defaults(func=app_installation_cmd.cmd_app_installation_uninstall, write_capable=True)

    app_installation_bulk_install = app_installation_sub.add_parser("bulk-install", help="Install multiple apps")
    app_installation_bulk_install.add_argument("--tenant-json", required=True, help="JSON tenant object or @file")
    app_installation_bulk_install.add_argument(
        "--app-instances-json",
        required=True,
        help="JSON array or @file with app installation objects",
    )
    app_installation_bulk_install.set_defaults(func=app_installation_cmd.cmd_app_installation_bulk_install, write_capable=True)

    app_installation_bulk_uninstall = app_installation_sub.add_parser("bulk-uninstall", help="Uninstall multiple apps")
    app_installation_bulk_uninstall.add_argument("--tenant-json", required=True, help="JSON tenant object or @file")
    app_installation_bulk_uninstall.add_argument(
        "--app-def-ids-json",
        required=True,
        help="JSON array or @file with app definition IDs",
    )
    app_installation_bulk_uninstall.set_defaults(
        func=app_installation_cmd.cmd_app_installation_bulk_uninstall,
        write_capable=True,
    )

    bi_event = sub.add_parser("bi-event", help="Send BI events")
    bi_event_sub = bi_event.add_subparsers(dest="bi_event_cmd", required=True, parser_class=_ToolArgumentParser)
    bi_event_send = bi_event_sub.add_parser("send", help="Send one BI event")
    bi_event_send.add_argument("--event-name", required=True, help="BI event name")
    bi_event_send.add_argument(
        "--event-data-json",
        default=None,
        help="Optional JSON object or @file with BI event data",
    )
    bi_event_send.set_defaults(func=bi_event_cmd.cmd_bi_event_send, write_capable=True)

    embedded_scripts = sub.add_parser("embedded-scripts", help="Embedded script methods")
    embedded_scripts_sub = embedded_scripts.add_subparsers(
        dest="embedded_scripts_cmd", required=True, parser_class=_ToolArgumentParser
    )
    embedded_scripts_get = embedded_scripts_sub.add_parser(
        "get",
        help="Get the current embedded script state for this app",
    )
    embedded_scripts_get.add_argument("--component-id", default=None, help="Optional embedded script component ID")
    embedded_scripts_get.set_defaults(func=embedded_scripts_cmd.cmd_embedded_scripts_get, write_capable=False)
    embedded_scripts_embed = embedded_scripts_sub.add_parser(
        "embed",
        help="Create or update one embedded script",
    )
    embedded_scripts_embed.add_argument("--component-id", default=None, help="Optional embedded script component ID")
    embedded_scripts_embed.add_argument(
        "--disabled",
        type=str.lower,
        default="false",
        choices=("true", "false"),
        help="Disable the script when true. Default false.",
    )
    embedded_scripts_embed.add_argument(
        "--parameters-json",
        dest="parameters_json",
        default=None,
        help="Optional JSON object of dynamic parameter string pairs",
    )
    embedded_scripts_embed.set_defaults(func=embedded_scripts_cmd.cmd_embedded_scripts_embed, write_capable=True)

    custom_embeds = sub.add_parser("custom-embeds", help="Read/write custom embed methods")
    custom_embeds_sub = custom_embeds.add_subparsers(
        dest="custom_embeds_cmd", required=True, parser_class=_ToolArgumentParser
    )
    custom_embeds_list = custom_embeds_sub.add_parser("list", help="List custom embeds")
    custom_embeds_list.add_argument("--limit", type=int, default=None, help="Max embeds to return, up to 100")
    custom_embeds_list.add_argument("--offset", type=int, default=None, help="Embeds to skip in current sort order")
    custom_embeds_list.set_defaults(func=custom_embeds_cmd.cmd_custom_embeds_list, write_capable=False)

    custom_embeds_get = custom_embeds_sub.add_parser("get", help="Get one custom embed by id")
    custom_embeds_get.add_argument("--custom-embed-id", required=True, help="Custom embed ID")
    custom_embeds_get.set_defaults(func=custom_embeds_cmd.cmd_custom_embeds_get, write_capable=False)

    custom_embeds_create = custom_embeds_sub.add_parser("create", help="Create one custom embed")
    custom_embeds_create.add_argument(
        "--custom-embed-json",
        required=True,
        dest="custom_embed_json",
        help="JSON customEmbed object with name, position, and embedData",
    )
    custom_embeds_create.set_defaults(func=custom_embeds_cmd.cmd_custom_embeds_create, write_capable=True)

    custom_embeds_update = custom_embeds_sub.add_parser("update", help="Update one custom embed by id")
    custom_embeds_update.add_argument("--custom-embed-id", required=True, help="Custom embed ID")
    custom_embeds_update.add_argument(
        "--custom-embed-json",
        required=True,
        dest="custom_embed_json",
        help="JSON customEmbed object with the current revision and any fields to update",
    )
    custom_embeds_update.set_defaults(func=custom_embeds_cmd.cmd_custom_embeds_update, write_capable=True)

    custom_embeds_delete = custom_embeds_sub.add_parser("delete", help="Delete one custom embed by id")
    custom_embeds_delete.add_argument("--custom-embed-id", required=True, help="Custom embed ID")
    custom_embeds_delete.set_defaults(func=custom_embeds_cmd.cmd_custom_embeds_delete, write_capable=True)

    secrets = sub.add_parser("secrets", help="Read and manage site secrets")
    secrets_sub = secrets.add_subparsers(dest="secrets_cmd", required=True, parser_class=_ToolArgumentParser)

    secrets_list = secrets_sub.add_parser("list", help="List secret metadata")
    secrets_list.set_defaults(func=secrets_cmd.cmd_secrets_list, write_capable=False)

    secrets_get_value = secrets_sub.add_parser("get-value", help="Get one secret value by name")
    secrets_get_value.add_argument("--name", required=True, help="Secret name")
    secrets_get_value.set_defaults(func=secrets_cmd.cmd_secrets_get_value, write_capable=False)

    secrets_create = secrets_sub.add_parser("create", help="Create one secret")
    secrets_create.add_argument(
        "--secret-json",
        dest="secret_json",
        required=True,
        help="JSON object or @file with secret name, value, and optional description",
    )
    secrets_create.set_defaults(func=secrets_cmd.cmd_secrets_create, write_capable=True)

    secrets_patch = secrets_sub.add_parser("patch", help="Patch one secret by id")
    secrets_patch.add_argument("--secret-id", required=True, dest="secret_id", help="Secret ID")
    secrets_patch.add_argument(
        "--secret-json",
        dest="secret_json",
        required=True,
        help="JSON object or @file with one or more of name, description, and value",
    )
    secrets_patch.set_defaults(func=secrets_cmd.cmd_secrets_patch, write_capable=True)

    secrets_delete = secrets_sub.add_parser("delete", help="Delete one secret by id")
    secrets_delete.add_argument("--secret-id", required=True, dest="secret_id", help="Secret ID")
    secrets_delete.set_defaults(func=secrets_cmd.cmd_secrets_delete, write_capable=True)

    marketing_consent = sub.add_parser("marketing-consent", help="Read and manage marketing consent records")
    marketing_consent_sub = marketing_consent.add_subparsers(
        dest="marketing_consent_cmd", required=True, parser_class=_ToolArgumentParser
    )

    marketing_consent_get = marketing_consent_sub.add_parser("get", help="Get one marketing consent by id")
    marketing_consent_get.add_argument(
        "--marketing-consent-id",
        required=True,
        dest="marketing_consent_id",
        help="Marketing consent ID",
    )
    marketing_consent_get.set_defaults(func=marketing_consent_cmd.cmd_marketing_consent_get, write_capable=False)

    marketing_consent_query = marketing_consent_sub.add_parser("query", help="Query marketing consents")
    marketing_consent_query.add_argument(
        "--query-json",
        dest="query_json",
        required=True,
        help="JSON object or @file with a CursorQuery payload",
    )
    marketing_consent_query.set_defaults(func=marketing_consent_cmd.cmd_marketing_consent_query, write_capable=False)

    marketing_consent_get_by_identifier = marketing_consent_sub.add_parser(
        "get-by-identifier",
        help="Get one marketing consent by type and communication details",
    )
    marketing_consent_get_by_identifier.add_argument(
        "--type",
        required=True,
        choices=("EMAIL", "PHONE"),
        help="Communication channel",
    )
    marketing_consent_get_by_identifier.add_argument("--email", default=None, help="Email address")
    marketing_consent_get_by_identifier.add_argument("--phone", default=None, help="Phone number in E.164 format")
    marketing_consent_get_by_identifier.add_argument(
        "--link-language",
        dest="link_language",
        default=None,
        help="Optional page language for the page link",
    )
    marketing_consent_get_by_identifier.set_defaults(
        func=marketing_consent_cmd.cmd_marketing_consent_get_by_identifier,
        write_capable=False,
    )

    marketing_consent_create = marketing_consent_sub.add_parser("create", help="Create one marketing consent")
    marketing_consent_create.add_argument(
        "--marketing-consent-json",
        dest="marketing_consent_json",
        required=True,
        help="JSON object or @file with a MarketingConsent payload",
    )
    marketing_consent_create.set_defaults(func=marketing_consent_cmd.cmd_marketing_consent_create, write_capable=True)

    marketing_consent_upsert = marketing_consent_sub.add_parser("upsert", help="Create or update one marketing consent")
    marketing_consent_upsert.add_argument(
        "--marketing-consent-json",
        dest="marketing_consent_json",
        required=True,
        help="JSON object or @file with a MarketingConsent payload",
    )
    marketing_consent_upsert.set_defaults(func=marketing_consent_cmd.cmd_marketing_consent_upsert, write_capable=True)

    marketing_consent_update = marketing_consent_sub.add_parser("update", help="Update one marketing consent")
    marketing_consent_update.add_argument(
        "--marketing-consent-json",
        dest="marketing_consent_json",
        required=True,
        help="JSON object or @file with a MarketingConsent payload including id",
    )
    marketing_consent_update.add_argument(
        "--mask-json",
        dest="mask_json",
        required=True,
        help="JSON object or @file with mask.paths entries to update",
    )
    marketing_consent_update.set_defaults(func=marketing_consent_cmd.cmd_marketing_consent_update, write_capable=True)

    marketing_consent_delete = marketing_consent_sub.add_parser("delete", help="Delete one marketing consent by id")
    marketing_consent_delete.add_argument(
        "--marketing-consent-id",
        required=True,
        dest="marketing_consent_id",
        help="Marketing consent ID",
    )
    marketing_consent_delete.set_defaults(func=marketing_consent_cmd.cmd_marketing_consent_delete, write_capable=True)

    marketing_consent_bulk_upsert = marketing_consent_sub.add_parser(
        "bulk-upsert",
        help="Create or update multiple marketing consents",
    )
    marketing_consent_bulk_upsert.add_argument(
        "--marketing-consents-json",
        dest="marketing_consents_json",
        required=True,
        help="JSON array or @file, or an object with info[] marketing consent entries",
    )
    marketing_consent_bulk_upsert.set_defaults(
        func=marketing_consent_cmd.cmd_marketing_consent_bulk_upsert,
        write_capable=True,
    )

    marketing_consent_remove = marketing_consent_sub.add_parser("remove", help="Cancel one marketing consent")
    marketing_consent_remove.add_argument("--type", required=True, choices=("EMAIL", "PHONE"), help="Communication channel")
    marketing_consent_remove.add_argument("--email", default=None, help="Email address")
    marketing_consent_remove.add_argument("--phone", default=None, help="Phone number in E.164 format")
    marketing_consent_remove.add_argument(
        "--last-revoke-activity-json",
        dest="last_revoke_activity_json",
        required=True,
        help="JSON object or @file with lastRevokeActivity",
    )
    marketing_consent_remove.set_defaults(func=marketing_consent_cmd.cmd_marketing_consent_remove, write_capable=True)

    sender_emails = sub.add_parser("sender-emails", help="Read and manage sender email addresses")
    sender_emails_sub = sender_emails.add_subparsers(
        dest="sender_emails_cmd", required=True, parser_class=_ToolArgumentParser
    )

    sender_emails_list = sender_emails_sub.add_parser("list", help="List sender emails")
    sender_emails_list.add_argument("--email-address", dest="email_address", default=None, help="Optional exact email address filter")
    sender_emails_list.add_argument("--limit", type=int, default=None, help="Max results to return, up to 100")
    sender_emails_list.add_argument("--cursor", default=None, help="Cursor from a prior sender-emails list response")
    sender_emails_list.set_defaults(func=sender_emails_cmd.cmd_sender_emails_list, write_capable=False)

    sender_emails_get = sender_emails_sub.add_parser("get", help="Get one sender email by id")
    sender_emails_get.add_argument("--sender-email-id", required=True, dest="sender_email_id", help="Sender email ID")
    sender_emails_get.set_defaults(func=sender_emails_cmd.cmd_sender_emails_get, write_capable=False)

    sender_emails_create = sender_emails_sub.add_parser("create", help="Create one sender email")
    sender_emails_create.add_argument(
        "--sender-email-json",
        dest="sender_email_json",
        required=True,
        help="JSON object or @file with senderEmail.emailAddress and optional extendedFields",
    )
    sender_emails_create.set_defaults(func=sender_emails_cmd.cmd_sender_emails_create, write_capable=True)

    sender_emails_delete = sender_emails_sub.add_parser("delete", help="Delete one sender email by id")
    sender_emails_delete.add_argument("--sender-email-id", required=True, dest="sender_email_id", help="Sender email ID")
    sender_emails_delete.set_defaults(func=sender_emails_cmd.cmd_sender_emails_delete, write_capable=True)

    sender_emails_get_or_create = sender_emails_sub.add_parser(
        "get-or-create",
        help="Get one sender email by address or create it if it does not exist",
    )
    sender_emails_get_or_create.add_argument(
        "--email-address",
        required=True,
        dest="email_address",
        help="Sender email address",
    )
    sender_emails_get_or_create.set_defaults(func=sender_emails_cmd.cmd_sender_emails_get_or_create, write_capable=True)

    sender_emails_send_verification_code = sender_emails_sub.add_parser(
        "send-verification-code",
        help="Send a verification code to one sender email inbox",
    )
    sender_emails_send_verification_code.add_argument(
        "--sender-email-id",
        required=True,
        dest="sender_email_id",
        help="Sender email ID",
    )
    sender_emails_send_verification_code.set_defaults(
        func=sender_emails_cmd.cmd_sender_emails_send_verification_code,
        write_capable=True,
    )

    sender_emails_verify = sender_emails_sub.add_parser("verify", help="Verify one sender email with a code")
    sender_emails_verify.add_argument("--sender-email-id", required=True, dest="sender_email_id", help="Sender email ID")
    sender_emails_verify.add_argument(
        "--verification-code",
        required=True,
        dest="verification_code",
        help="Verification code received in the inbox",
    )
    sender_emails_verify.set_defaults(func=sender_emails_cmd.cmd_sender_emails_verify, write_capable=True)

    sender_details = sub.add_parser("sender-details", help="Read and manage sender details")
    sender_details_sub = sender_details.add_subparsers(
        dest="sender_details_cmd", required=True, parser_class=_ToolArgumentParser
    )

    sender_details_list = sender_details_sub.add_parser("list", help="List sender details")
    sender_details_list.add_argument("--limit", type=int, default=None, help="Max results to return, up to 100")
    sender_details_list.add_argument("--cursor", default=None, help="Cursor from a prior sender-details list response")
    sender_details_list.set_defaults(func=sender_details_cmd.cmd_sender_details_list, write_capable=False)

    sender_details_get = sender_details_sub.add_parser("get", help="Get one sender details record by id")
    sender_details_get.add_argument(
        "--sender-details-id",
        required=True,
        dest="sender_details_id",
        help="Sender details ID",
    )
    sender_details_get.set_defaults(func=sender_details_cmd.cmd_sender_details_get, write_capable=False)

    sender_details_create = sender_details_sub.add_parser("create", help="Create one sender details record")
    sender_details_create.add_argument(
        "--sender-details-json",
        dest="sender_details_json",
        required=True,
        help="JSON object or @file with senderDetails.fromName, senderDetails.fromEmailAddress, and optional extendedFields",
    )
    sender_details_create.set_defaults(func=sender_details_cmd.cmd_sender_details_create, write_capable=True)

    sender_details_update = sender_details_sub.add_parser("update", help="Update one sender details record by id")
    sender_details_update.add_argument(
        "--sender-details-id",
        required=True,
        dest="sender_details_id",
        help="Sender details ID",
    )
    sender_details_update.add_argument(
        "--sender-details-json",
        dest="sender_details_json",
        required=True,
        help="JSON object or @file with one or more senderDetails fields to update",
    )
    sender_details_update.set_defaults(func=sender_details_cmd.cmd_sender_details_update, write_capable=True)

    sender_details_delete = sender_details_sub.add_parser("delete", help="Delete one sender details record by id")
    sender_details_delete.add_argument(
        "--sender-details-id",
        required=True,
        dest="sender_details_id",
        help="Sender details ID",
    )
    sender_details_delete.set_defaults(func=sender_details_cmd.cmd_sender_details_delete, write_capable=True)

    sender_details_get_default = sender_details_sub.add_parser("get-default", help="Get the default sender details")
    sender_details_get_default.set_defaults(func=sender_details_cmd.cmd_sender_details_get_default, write_capable=False)

    sender_details_mark_default = sender_details_sub.add_parser(
        "mark-default",
        help="Mark one sender details record as the default sender",
    )
    sender_details_mark_default.add_argument(
        "--sender-details-id",
        required=True,
        dest="sender_details_id",
        help="Sender details ID",
    )
    sender_details_mark_default.set_defaults(func=sender_details_cmd.cmd_sender_details_mark_default, write_capable=True)

    sending_domains = sub.add_parser("sending-domains", help="Read and authenticate sending domains")
    sending_domains_sub = sending_domains.add_subparsers(
        dest="sending_domains_cmd", required=True, parser_class=_ToolArgumentParser
    )

    sending_domains_get = sending_domains_sub.add_parser("get", help="Get one sending domain by id")
    sending_domains_get.add_argument(
        "--sending-domain-id",
        required=True,
        dest="sending_domain_id",
        help="Sending domain ID",
    )
    sending_domains_get.set_defaults(func=sending_domains_cmd.cmd_sending_domains_get, write_capable=False)

    sending_domains_query = sending_domains_sub.add_parser(
        "query",
        help="Query sending domains with a required domain or id filter",
    )
    sending_domains_query.add_argument("--domain", default=None, help="Exact domain filter, for example example.com")
    sending_domains_query.add_argument(
        "--sending-domain-id",
        dest="sending_domain_id",
        default=None,
        help="Exact sending domain ID filter",
    )
    sending_domains_query.add_argument(
        "--query-json",
        dest="query_json",
        default=None,
        help="Full query JSON object or @file. Use instead of the shorthand domain/id flags when needed.",
    )
    sending_domains_query.set_defaults(func=sending_domains_cmd.cmd_sending_domains_query, write_capable=False)

    sending_domains_authenticate = sending_domains_sub.add_parser(
        "authenticate",
        help="Authenticate one sending domain after DNS records are added and propagated",
    )
    sending_domains_authenticate.add_argument(
        "--sending-domain-id",
        required=True,
        dest="sending_domain_id",
        help="Sending domain ID",
    )
    sending_domains_authenticate.set_defaults(
        func=sending_domains_cmd.cmd_sending_domains_authenticate,
        write_capable=True,
    )

    email_campaigns = sub.add_parser("email-campaigns", help="Read and manage Wix email marketing campaign data")
    email_campaigns_sub = email_campaigns.add_subparsers(
        dest="email_campaigns_cmd", required=True, parser_class=_ToolArgumentParser
    )

    email_campaigns_list = email_campaigns_sub.add_parser("list", help="List email campaigns")
    email_campaigns_list.add_argument(
        "--include-statistics",
        action="store_true",
        help="Include publishingData.statistics in returned campaigns",
    )
    email_campaigns_list.add_argument(
        "--statuses-json",
        dest="statuses_json",
        default=None,
        help='JSON array of campaign statuses, for example ["ACTIVE"]',
    )
    email_campaigns_list.add_argument(
        "--visibility-statuses-json",
        dest="visibility_statuses_json",
        default=None,
        help='JSON array of visibility statuses, for example ["DRAFT"]',
    )
    email_campaigns_list.add_argument("--limit", type=int, default=None, help="Max campaigns to return")
    email_campaigns_list.add_argument("--offset", type=int, default=None, help="Campaigns to skip")
    email_campaigns_list.set_defaults(func=email_campaigns_cmd.cmd_email_campaigns_list, write_capable=False)

    email_campaigns_get = email_campaigns_sub.add_parser("get", help="Get one email campaign by id")
    email_campaigns_get.add_argument("--campaign-id", required=True, dest="campaign_id", help="Campaign ID")
    email_campaigns_get.add_argument(
        "--include-statistics",
        action="store_true",
        help="Include publishingData.statistics in the returned campaign",
    )
    email_campaigns_get.set_defaults(func=email_campaigns_cmd.cmd_email_campaigns_get, write_capable=False)

    email_campaigns_get_audience = email_campaigns_sub.add_parser(
        "get-audience",
        help="Get the full audience for one paused campaign",
    )
    email_campaigns_get_audience.add_argument("--campaign-id", required=True, dest="campaign_id", help="Campaign ID")
    email_campaigns_get_audience.set_defaults(func=email_campaigns_cmd.cmd_email_campaigns_get_audience, write_capable=False)

    email_campaigns_list_statistics = email_campaigns_sub.add_parser(
        "list-statistics",
        help="List statistics for up to 100 campaigns",
    )
    email_campaigns_list_statistics.add_argument(
        "--campaign-ids-json",
        required=True,
        dest="campaign_ids_json",
        help="JSON array of campaign IDs, max 100",
    )
    email_campaigns_list_statistics.set_defaults(
        func=email_campaigns_cmd.cmd_email_campaigns_list_statistics,
        write_capable=False,
    )

    email_campaigns_list_recipients = email_campaigns_sub.add_parser(
        "list-recipients",
        help="List recipients for one campaign and one activity type",
    )
    email_campaigns_list_recipients.add_argument("--campaign-id", required=True, dest="campaign_id", help="Campaign ID")
    email_campaigns_list_recipients.add_argument(
        "--activity",
        required=True,
        help="Recipient activity: DELIVERED, OPENED, CLICKED, BOUNCED, NOT_SENT, SENT, or NOT_OPENED",
    )
    email_campaigns_list_recipients.add_argument("--limit", type=int, default=None, help="Max recipients to return, up to 1000")
    email_campaigns_list_recipients.add_argument("--cursor", default=None, help="Cursor from a prior recipients response")
    email_campaigns_list_recipients.set_defaults(
        func=email_campaigns_cmd.cmd_email_campaigns_list_recipients,
        write_capable=False,
    )

    email_campaigns_pause = email_campaigns_sub.add_parser(
        "pause-scheduling",
        help="Pause a scheduled campaign",
    )
    email_campaigns_pause.add_argument("--campaign-id", required=True, dest="campaign_id", help="Campaign ID")
    email_campaigns_pause.set_defaults(func=email_campaigns_cmd.cmd_email_campaigns_pause_scheduling, write_capable=True)

    email_campaigns_reschedule = email_campaigns_sub.add_parser(
        "reschedule",
        help="Change the send time for a scheduled campaign",
    )
    email_campaigns_reschedule.add_argument("--campaign-id", required=True, dest="campaign_id", help="Campaign ID")
    email_campaigns_reschedule.add_argument("--send-at", required=True, dest="send_at", help="New RFC 3339 send time")
    email_campaigns_reschedule.set_defaults(func=email_campaigns_cmd.cmd_email_campaigns_reschedule, write_capable=True)

    email_campaigns_send_test = email_campaigns_sub.add_parser(
        "send-test",
        help="Send a test email for one campaign",
    )
    email_campaigns_send_test.add_argument("--campaign-id", required=True, dest="campaign_id", help="Campaign ID")
    email_campaigns_send_test.add_argument(
        "--send-test-json",
        dest="send_test_json",
        required=True,
        help="JSON object or @file with toEmailAddress and optional emailSubject",
    )
    email_campaigns_send_test.set_defaults(func=email_campaigns_cmd.cmd_email_campaigns_send_test, write_capable=True)

    email_campaigns_publish = email_campaigns_sub.add_parser(
        "publish",
        help="Publish one campaign",
    )
    email_campaigns_publish.add_argument("--campaign-id", required=True, dest="campaign_id", help="Campaign ID")
    email_campaigns_publish.add_argument(
        "--publish-json",
        dest="publish_json",
        default=None,
        help=(
            "JSON object or @file with optional emailDistributionOptions; omit it to publish the landing page only"
        ),
    )
    email_campaigns_publish.set_defaults(func=email_campaigns_cmd.cmd_email_campaigns_publish, write_capable=True)

    email_campaigns_reuse = email_campaigns_sub.add_parser(
        "reuse",
        help="Create a new campaign copy from one campaign",
    )
    email_campaigns_reuse.add_argument("--campaign-id", required=True, dest="campaign_id", help="Campaign ID")
    email_campaigns_reuse.set_defaults(func=email_campaigns_cmd.cmd_email_campaigns_reuse, write_capable=True)

    email_campaigns_delete = email_campaigns_sub.add_parser(
        "delete",
        help="Delete one campaign permanently",
    )
    email_campaigns_delete.add_argument("--campaign-id", required=True, dest="campaign_id", help="Campaign ID")
    email_campaigns_delete.set_defaults(func=email_campaigns_cmd.cmd_email_campaigns_delete, write_capable=True)

    email_campaigns_identify_sender = email_campaigns_sub.add_parser(
        "identify-sender-address",
        help='Check whether one email address will be used as the "from" address',
    )
    email_campaigns_identify_sender.add_argument(
        "--email-address",
        required=True,
        dest="email_address",
        help="Email address to check",
    )
    email_campaigns_identify_sender.set_defaults(
        func=email_campaigns_cmd.cmd_email_campaigns_identify_sender_address,
        write_capable=False,
    )

    campaign_validation = sub.add_parser(
        "campaign-validation",
        help="Read-only email campaign validation helpers",
    )
    campaign_validation_sub = campaign_validation.add_subparsers(
        dest="campaign_validation_cmd", required=True, parser_class=_ToolArgumentParser
    )

    campaign_validation_validate_link = campaign_validation_sub.add_parser(
        "validate-link",
        help="Validate one link for campaign abuse-rule compliance",
    )
    campaign_validation_validate_link.add_argument("--url", required=True, help="URL to validate")
    campaign_validation_validate_link.set_defaults(
        func=email_campaigns_cmd.cmd_campaign_validation_validate_link,
        write_capable=False,
    )

    campaign_validation_validate_html_links = campaign_validation_sub.add_parser(
        "validate-html-links",
        help="Validate links extracted from one HTML block",
    )
    campaign_validation_validate_html_links.add_argument(
        "--html",
        required=True,
        help="HTML string or @file path containing HTML to validate",
    )
    campaign_validation_validate_html_links.set_defaults(
        func=email_campaigns_cmd.cmd_campaign_validation_validate_html_links,
        write_capable=False,
    )

    orders = sub.add_parser("orders", help="Read and manage Wix eCommerce orders")
    orders_sub = orders.add_subparsers(dest="orders_cmd", required=True, parser_class=_ToolArgumentParser)

    orders_search = orders_sub.add_parser("search", help="Search orders")
    orders_search.add_argument(
        "--search-json",
        dest="search_json",
        default=None,
        help="Optional JSON search object or full official search request body",
    )
    orders_search.set_defaults(func=orders_cmd.cmd_orders_search, write_capable=False)

    orders_get = orders_sub.add_parser("get", help="Get one order by id")
    orders_get.add_argument("--order-id", required=True, dest="order_id", help="Order ID")
    orders_get.set_defaults(func=orders_cmd.cmd_orders_get, write_capable=False)

    orders_create = orders_sub.add_parser("create", help="Create one manual or external-system order")
    orders_create.add_argument(
        "--order-json",
        dest="order_json",
        required=True,
        help="JSON order object, full create body, or @file",
    )
    orders_create.set_defaults(func=orders_cmd.cmd_orders_create, write_capable=True)

    orders_update = orders_sub.add_parser("update", help="Update one order")
    orders_update.add_argument("--order-id", required=True, dest="order_id", help="Order ID")
    orders_update.add_argument(
        "--order-json",
        dest="order_json",
        required=True,
        help="JSON order patch object, full update body, or @file",
    )
    orders_update.set_defaults(func=orders_cmd.cmd_orders_update, write_capable=True)

    orders_cancel = orders_sub.add_parser("cancel", help="Cancel one order")
    orders_cancel.add_argument("--order-id", required=True, dest="order_id", help="Order ID")
    orders_cancel.add_argument(
        "--cancel-json",
        dest="cancel_json",
        default=None,
        help="Optional JSON body or @file with sendOrderCanceledEmail, customMessage, or restockAllItems",
    )
    orders_cancel.set_defaults(func=orders_cmd.cmd_orders_cancel, write_capable=True)

    orders_bulk_update = orders_sub.add_parser("bulk-update", help="Update up to 100 orders in one reviewed-plan request")
    orders_bulk_update.add_argument(
        "--orders-json",
        dest="orders_json",
        required=True,
        help="JSON array, JSON object, or @file with the official bulk update body",
    )
    orders_bulk_update.set_defaults(func=orders_cmd.cmd_orders_bulk_update, write_capable=True)

    bookings_policies = sub.add_parser(
        "bookings-policies",
        help="Read and manage Wix Bookings booking policies",
    )
    bookings_policies_sub = bookings_policies.add_subparsers(
        dest="bookings_policies_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    bookings_policies_get = bookings_policies_sub.add_parser("get", help="Get one booking policy")
    bookings_policies_get.add_argument("--booking-policy-id", required=True, help="Booking policy ID")
    bookings_policies_get.set_defaults(func=bookings_policies_cmd.cmd_bookings_policies_get, write_capable=False)

    bookings_policies_query = bookings_policies_sub.add_parser("query", help="Query booking policies")
    bookings_policies_query.add_argument("--query-json", dest="query_json", default=None, help="Optional official query JSON object or @file")
    bookings_policies_query.set_defaults(func=bookings_policies_cmd.cmd_bookings_policies_query, write_capable=False)

    bookings_policies_count = bookings_policies_sub.add_parser("count", help="Count booking policies")
    bookings_policies_count.add_argument("--filter-json", dest="filter_json", default=None, help="Optional official filter JSON object or @file")
    bookings_policies_count.set_defaults(func=bookings_policies_cmd.cmd_bookings_policies_count, write_capable=False)

    bookings_policies_strictest = bookings_policies_sub.add_parser("strictest", help="Get the strictest combined booking policy")
    bookings_policies_strictest.add_argument("--request-json", dest="request_json", required=True, help="Official strictest policy request JSON object or @file")
    bookings_policies_strictest.set_defaults(func=bookings_policies_cmd.cmd_bookings_policies_strictest, write_capable=False)

    bookings_policies_create = bookings_policies_sub.add_parser("create", help="Create one booking policy")
    bookings_policies_create.add_argument("--policy-json", dest="policy_json", required=True, help="Official bookingPolicy JSON object/body or @file")
    bookings_policies_create.set_defaults(func=bookings_policies_cmd.cmd_bookings_policies_create, write_capable=True)

    bookings_policies_update = bookings_policies_sub.add_parser("update", help="Update one booking policy")
    bookings_policies_update.add_argument("--booking-policy-id", required=True, help="Booking policy ID")
    bookings_policies_update.add_argument("--policy-json", dest="policy_json", required=True, help="Official bookingPolicy JSON object/body or @file")
    bookings_policies_update.set_defaults(func=bookings_policies_cmd.cmd_bookings_policies_update, write_capable=True)

    bookings_policies_delete = bookings_policies_sub.add_parser("delete", help="Delete one booking policy")
    bookings_policies_delete.add_argument("--booking-policy-id", required=True, help="Booking policy ID")
    bookings_policies_delete.set_defaults(func=bookings_policies_cmd.cmd_bookings_policies_delete, write_capable=True)

    bookings_policies_set_default = bookings_policies_sub.add_parser("set-default", help="Set one booking policy as the site default")
    bookings_policies_set_default.add_argument("--booking-policy-id", required=True, help="Booking policy ID")
    bookings_policies_set_default.set_defaults(func=bookings_policies_cmd.cmd_bookings_policies_set_default, write_capable=True)

    bookings_policy_snapshots = sub.add_parser(
        "bookings-policy-snapshots",
        help="Read Wix Bookings policy snapshots",
    )
    bookings_policy_snapshots_sub = bookings_policy_snapshots.add_subparsers(
        dest="bookings_policy_snapshots_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    bookings_policy_snapshots_list = bookings_policy_snapshots_sub.add_parser(
        "list",
        help="List booking policy snapshots by booking IDs",
    )
    bookings_policy_snapshots_list.add_argument(
        "--booking-ids",
        required=True,
        help="Comma-separated booking IDs to fetch policy snapshots for",
    )
    bookings_policy_snapshots_list.set_defaults(
        func=bookings_policy_snapshots_cmd.cmd_bookings_policy_snapshots_list,
        write_capable=False,
    )

    bookings_attendance = sub.add_parser(
        "bookings-attendance",
        help="Read and manage Wix Bookings attendance",
    )
    bookings_attendance_sub = bookings_attendance.add_subparsers(
        dest="bookings_attendance_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    bookings_attendance_get = bookings_attendance_sub.add_parser("get", help="Get one attendance record")
    bookings_attendance_get.add_argument("--attendance-id", required=True, help="Attendance ID")
    bookings_attendance_get.set_defaults(func=bookings_attendance_cmd.cmd_bookings_attendance_get, write_capable=False)

    bookings_attendance_query = bookings_attendance_sub.add_parser("query", help="Query attendance records")
    bookings_attendance_query.add_argument("--query-json", dest="query_json", default=None, help="Optional official query JSON object or @file")
    bookings_attendance_query.set_defaults(func=bookings_attendance_cmd.cmd_bookings_attendance_query, write_capable=False)

    bookings_attendance_count = bookings_attendance_sub.add_parser("count", help="Count attendance records for the calling member")
    bookings_attendance_count.add_argument("--filter-json", dest="filter_json", default=None, help="Optional official filter JSON object or @file")
    bookings_attendance_count.set_defaults(func=bookings_attendance_cmd.cmd_bookings_attendance_count, write_capable=False)

    bookings_attendance_set = bookings_attendance_sub.add_parser("set", help="Set or update one attendance record")
    bookings_attendance_set.add_argument("--attendance-json", dest="attendance_json", required=True, help="Official attendance request JSON object or @file")
    bookings_attendance_set.set_defaults(func=bookings_attendance_cmd.cmd_bookings_attendance_set, write_capable=True)

    bookings_attendance_bulk_set = bookings_attendance_sub.add_parser("bulk-set", help="Set or update multiple attendance records")
    bookings_attendance_bulk_set.add_argument("--attendance-json", dest="attendance_json", required=True, help="Official bulk attendance request JSON object or @file")
    bookings_attendance_bulk_set.set_defaults(func=bookings_attendance_cmd.cmd_bookings_attendance_bulk_set, write_capable=True)

    bookings_attendance_delete = bookings_attendance_sub.add_parser("delete", help="Delete one attendance record")
    bookings_attendance_delete.add_argument("--attendance-id", required=True, help="Attendance ID")
    bookings_attendance_delete.set_defaults(func=bookings_attendance_cmd.cmd_bookings_attendance_delete, write_capable=True)

    bookings_attendance_bulk_delete = bookings_attendance_sub.add_parser("bulk-delete", help="Delete multiple attendance records")
    bookings_attendance_bulk_delete.add_argument("--attendance-json", dest="attendance_json", required=True, help="Official bulk delete attendance request JSON object or @file")
    bookings_attendance_bulk_delete.set_defaults(func=bookings_attendance_cmd.cmd_bookings_attendance_bulk_delete, write_capable=True)

    bookings_waitlist = sub.add_parser(
        "bookings-waitlist",
        help="Read and manage Wix Bookings waitlists",
    )
    bookings_waitlist_sub = bookings_waitlist.add_subparsers(
        dest="bookings_waitlist_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    bookings_waitlist_list = bookings_waitlist_sub.add_parser("list", help="List waitlisted entries for waiting resources")
    bookings_waitlist_list.add_argument(
        "--waiting-resources",
        required=True,
        help="Comma-separated session GUIDs with active waitlists",
    )
    bookings_waitlist_list.set_defaults(func=bookings_waitlist_cmd.cmd_bookings_waitlist_list, write_capable=False)

    for command_name, handler, help_text in (
        ("register", bookings_waitlist_cmd.cmd_bookings_waitlist_register, "Register a site member to a waitlist"),
        ("leave", bookings_waitlist_cmd.cmd_bookings_waitlist_leave, "Remove a registration from a waitlist"),
        ("book", bookings_waitlist_cmd.cmd_bookings_waitlist_book, "Book a waitlisted member into the session"),
    ):
        parser = bookings_waitlist_sub.add_parser(command_name, help=help_text)
        parser.add_argument("--request-json", dest="request_json", required=True, help="Official waitlist request JSON object or @file")
        parser.add_argument(
            "--ack-event-session",
            action="store_true",
            help="Confirm the target waiting resource is a session with type = EVENT",
        )
        parser.set_defaults(func=handler, write_capable=True)

    calendar_schedules_v3 = sub.add_parser(
        "calendar-schedules-v3",
        help="Read and manage Wix Calendar Schedules V3",
    )
    calendar_schedules_v3_sub = calendar_schedules_v3.add_subparsers(
        dest="calendar_schedules_v3_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    calendar_schedules_v3_get = calendar_schedules_v3_sub.add_parser("get", help="Get one calendar schedule")
    calendar_schedules_v3_get.add_argument("--schedule-id", required=True, help="Schedule ID")
    calendar_schedules_v3_get.set_defaults(func=calendar_schedules_v3_cmd.cmd_calendar_schedules_v3_get, write_capable=False)

    calendar_schedules_v3_query = calendar_schedules_v3_sub.add_parser("query", help="Query calendar schedules")
    calendar_schedules_v3_query.add_argument("--query-json", dest="query_json", default=None, help="Optional official query JSON object or @file")
    calendar_schedules_v3_query.set_defaults(func=calendar_schedules_v3_cmd.cmd_calendar_schedules_v3_query, write_capable=False)

    calendar_schedules_v3_create = calendar_schedules_v3_sub.add_parser("create", help="Create one calendar schedule")
    calendar_schedules_v3_create.add_argument("--schedule-json", dest="schedule_json", required=True, help="Official schedule JSON object/body or @file")
    calendar_schedules_v3_create.set_defaults(func=calendar_schedules_v3_cmd.cmd_calendar_schedules_v3_create, write_capable=True)

    calendar_schedules_v3_update = calendar_schedules_v3_sub.add_parser("update", help="Update one calendar schedule")
    calendar_schedules_v3_update.add_argument("--schedule-id", required=True, help="Schedule ID")
    calendar_schedules_v3_update.add_argument("--schedule-json", dest="schedule_json", required=True, help="Official schedule JSON object/body or @file")
    calendar_schedules_v3_update.set_defaults(func=calendar_schedules_v3_cmd.cmd_calendar_schedules_v3_update, write_capable=True)

    calendar_schedules_v3_cancel = calendar_schedules_v3_sub.add_parser("cancel", help="Cancel one calendar schedule")
    calendar_schedules_v3_cancel.add_argument("--schedule-id", required=True, help="Schedule ID")
    calendar_schedules_v3_cancel.add_argument("--request-json", dest="request_json", default=None, help="Optional official cancel request JSON object or @file")
    calendar_schedules_v3_cancel.set_defaults(func=calendar_schedules_v3_cmd.cmd_calendar_schedules_v3_cancel, write_capable=True)

    bookings_external_calendars_v2 = sub.add_parser(
        "bookings-external-calendars-v2",
        help="Read and manage Wix Bookings External Calendars V2",
    )
    bookings_external_calendars_v2_sub = bookings_external_calendars_v2.add_subparsers(
        dest="bookings_external_calendars_v2_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    bookings_external_calendars_v2_list_providers = bookings_external_calendars_v2_sub.add_parser("list-providers", help="List supported external calendar providers")
    bookings_external_calendars_v2_list_providers.set_defaults(
        func=bookings_external_calendars_v2_cmd.cmd_bookings_external_calendars_v2_list_providers,
        write_capable=False,
    )

    bookings_external_calendars_v2_connect_credentials = bookings_external_calendars_v2_sub.add_parser("connect-by-credentials", help="Connect an external calendar account using credentials")
    bookings_external_calendars_v2_connect_credentials.add_argument("--request-json", dest="request_json", required=True, help="Official connect request JSON object or @file")
    bookings_external_calendars_v2_connect_credentials.add_argument(
        "--ack-external-credentials",
        action="store_true",
        help="Confirm the request submits an external calendar account password to Wix",
    )
    bookings_external_calendars_v2_connect_credentials.set_defaults(
        func=bookings_external_calendars_v2_cmd.cmd_bookings_external_calendars_v2_connect_by_credentials,
        write_capable=True,
    )

    bookings_external_calendars_v2_connect_oauth = bookings_external_calendars_v2_sub.add_parser("connect-by-oauth", help="Start an external calendar OAuth connection")
    bookings_external_calendars_v2_connect_oauth.add_argument("--request-json", dest="request_json", required=True, help="Official OAuth connect request JSON object or @file")
    bookings_external_calendars_v2_connect_oauth.set_defaults(
        func=bookings_external_calendars_v2_cmd.cmd_bookings_external_calendars_v2_connect_by_oauth,
        write_capable=True,
    )

    bookings_external_calendars_v2_list_connections = bookings_external_calendars_v2_sub.add_parser("list-connections", help="List external calendar connections")
    bookings_external_calendars_v2_list_connections.add_argument("--query-json", dest="query_json", default=None, help="Optional official query parameter JSON object or @file")
    bookings_external_calendars_v2_list_connections.set_defaults(
        func=bookings_external_calendars_v2_cmd.cmd_bookings_external_calendars_v2_list_connections,
        write_capable=False,
    )

    bookings_external_calendars_v2_get_connection = bookings_external_calendars_v2_sub.add_parser("get-connection", help="Get one external calendar connection")
    bookings_external_calendars_v2_get_connection.add_argument("--connection-id", required=True, help="Connection ID")
    bookings_external_calendars_v2_get_connection.set_defaults(
        func=bookings_external_calendars_v2_cmd.cmd_bookings_external_calendars_v2_get_connection,
        write_capable=False,
    )

    bookings_external_calendars_v2_update_sync_config = bookings_external_calendars_v2_sub.add_parser("update-sync-config", help="Update external calendar sync settings")
    bookings_external_calendars_v2_update_sync_config.add_argument("--connection-id", required=True, help="Connection ID")
    bookings_external_calendars_v2_update_sync_config.add_argument("--request-json", dest="request_json", required=True, help="Official sync config request JSON object or @file")
    bookings_external_calendars_v2_update_sync_config.set_defaults(
        func=bookings_external_calendars_v2_cmd.cmd_bookings_external_calendars_v2_update_sync_config,
        write_capable=True,
    )

    bookings_external_calendars_v2_list_calendars = bookings_external_calendars_v2_sub.add_parser("list-calendars", help="List external calendars for a connection")
    bookings_external_calendars_v2_list_calendars.add_argument("--connection-id", required=True, help="Connection ID")
    bookings_external_calendars_v2_list_calendars.set_defaults(
        func=bookings_external_calendars_v2_cmd.cmd_bookings_external_calendars_v2_list_calendars,
        write_capable=False,
    )

    bookings_external_calendars_v2_list_events = bookings_external_calendars_v2_sub.add_parser("list-events", help="List external calendar events")
    bookings_external_calendars_v2_list_events.add_argument("--query-json", dest="query_json", default=None, help="Optional official query parameter JSON object or @file")
    bookings_external_calendars_v2_list_events.add_argument("--from", dest="from_", default=None, help="Start date/time for event filtering")
    bookings_external_calendars_v2_list_events.add_argument("--to", dest="to", default=None, help="End date/time for event filtering")
    bookings_external_calendars_v2_list_events.add_argument("--cursor", dest="cursor", default=None, help="Cursor for cursorPaging.cursor")
    bookings_external_calendars_v2_list_events.add_argument("--limit", dest="limit", type=int, default=None, help="Cursor page limit")
    bookings_external_calendars_v2_list_events.add_argument("--schedule-ids", dest="schedule_ids", default=None, help="Comma-separated schedule IDs")
    bookings_external_calendars_v2_list_events.add_argument("--user-ids", dest="user_ids", default=None, help="Comma-separated user IDs")
    bookings_external_calendars_v2_list_events.add_argument("--fieldsets", dest="fieldsets", default=None, help="Official fieldsets value, for example OWN_PI")
    bookings_external_calendars_v2_list_events.add_argument("--partial-failure", dest="partial_failure", action="store_true", help="Allow partial success when one provider fails")
    bookings_external_calendars_v2_list_events.set_defaults(
        func=bookings_external_calendars_v2_cmd.cmd_bookings_external_calendars_v2_list_events,
        write_capable=False,
    )

    bookings_external_calendars_v2_disconnect = bookings_external_calendars_v2_sub.add_parser("disconnect", help="Disconnect an external calendar connection")
    bookings_external_calendars_v2_disconnect.add_argument("--connection-id", required=True, help="Connection ID")
    bookings_external_calendars_v2_disconnect.set_defaults(
        func=bookings_external_calendars_v2_cmd.cmd_bookings_external_calendars_v2_disconnect,
        write_capable=True,
    )

    bookings_service_options_v1 = sub.add_parser(
        "bookings-service-options-v1",
        help="Read and manage Wix Bookings Service Options and Variants",
    )
    bookings_service_options_v1_sub = bookings_service_options_v1.add_subparsers(
        dest="bookings_service_options_v1_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    bookings_service_options_v1_get = bookings_service_options_v1_sub.add_parser("get", help="Get one service options and variants object")
    bookings_service_options_v1_get.add_argument("--service-options-id", required=True, help="Service options and variants ID")
    bookings_service_options_v1_get.set_defaults(func=bookings_service_options_v1_cmd.cmd_bookings_service_options_v1_get, write_capable=False)

    bookings_service_options_v1_get_by_service_id = bookings_service_options_v1_sub.add_parser("get-by-service-id", help="Get service options and variants by service ID")
    bookings_service_options_v1_get_by_service_id.add_argument("--service-id", required=True, help="Service ID")
    bookings_service_options_v1_get_by_service_id.set_defaults(func=bookings_service_options_v1_cmd.cmd_bookings_service_options_v1_get_by_service_id, write_capable=False)

    bookings_service_options_v1_query = bookings_service_options_v1_sub.add_parser("query", help="Query service options and variants")
    bookings_service_options_v1_query.add_argument("--query-json", dest="query_json", default=None, help="Optional official query JSON object or @file")
    bookings_service_options_v1_query.set_defaults(func=bookings_service_options_v1_cmd.cmd_bookings_service_options_v1_query, write_capable=False)

    bookings_service_options_v1_create = bookings_service_options_v1_sub.add_parser("create", help="Create service options and variants")
    bookings_service_options_v1_create.add_argument("--options-json", dest="options_json", required=True, help="Official serviceOptionsAndVariants JSON object/body or @file")
    bookings_service_options_v1_create.set_defaults(func=bookings_service_options_v1_cmd.cmd_bookings_service_options_v1_create, write_capable=True)

    bookings_service_options_v1_update = bookings_service_options_v1_sub.add_parser("update", help="Update service options and variants")
    bookings_service_options_v1_update.add_argument("--service-options-id", required=True, help="Service options and variants ID")
    bookings_service_options_v1_update.add_argument("--options-json", dest="options_json", required=True, help="Official serviceOptionsAndVariants JSON object/body or @file")
    bookings_service_options_v1_update.set_defaults(func=bookings_service_options_v1_cmd.cmd_bookings_service_options_v1_update, write_capable=True)

    bookings_service_options_v1_delete = bookings_service_options_v1_sub.add_parser("delete", help="Delete service options and variants")
    bookings_service_options_v1_delete.add_argument("--service-options-id", required=True, help="Service options and variants ID")
    bookings_service_options_v1_delete.set_defaults(func=bookings_service_options_v1_cmd.cmd_bookings_service_options_v1_delete, write_capable=True)

    bookings_service_options_v1_clone = bookings_service_options_v1_sub.add_parser("clone", help="Clone service options and variants")
    bookings_service_options_v1_clone.add_argument("--clone-from-id", required=True, help="Source service options and variants ID")
    bookings_service_options_v1_clone.add_argument("--request-json", dest="request_json", required=True, help="Official clone request JSON object or @file")
    bookings_service_options_v1_clone.set_defaults(func=bookings_service_options_v1_cmd.cmd_bookings_service_options_v1_clone, write_capable=True)

    bookings_writer_v2 = sub.add_parser(
        "bookings-writer-v2",
        help="Manage Wix Bookings Writer V2 methods",
    )
    bookings_writer_v2_sub = bookings_writer_v2.add_subparsers(
        dest="bookings_writer_v2_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    bookings_writer_v2_get_multi = bookings_writer_v2_sub.add_parser("get-multi-service", help="Get one multi-service booking")
    bookings_writer_v2_get_multi.add_argument("--multi-service-booking-id", required=True, help="Multi-service booking ID")
    bookings_writer_v2_get_multi.set_defaults(func=bookings_writer_v2_cmd.cmd_bookings_writer_v2_get_multi_service, write_capable=False)

    for command_name, handler, help_text in (
        ("bulk-calculate-allowed-actions", bookings_writer_v2_cmd.cmd_bookings_writer_v2_bulk_calculate_allowed_actions, "Calculate allowed actions for bookings"),
        ("bulk-get-multi-service-allowed-actions", bookings_writer_v2_cmd.cmd_bookings_writer_v2_bulk_get_multi_service_allowed_actions, "Get allowed actions for multi-service bookings"),
    ):
        parser = bookings_writer_v2_sub.add_parser(command_name, help=help_text)
        parser.add_argument("--request-json", dest="request_json", required=True, help="Official request JSON object or @file")
        parser.set_defaults(func=handler, write_capable=False)

    bookings_writer_v2_multi_availability = bookings_writer_v2_sub.add_parser("get-multi-service-availability", help="Get multi-service booking availability")
    bookings_writer_v2_multi_availability.add_argument("--multi-service-booking-id", required=True, help="Multi-service booking ID")
    bookings_writer_v2_multi_availability.add_argument("--request-json", dest="request_json", required=True, help="Official request JSON object or @file")
    bookings_writer_v2_multi_availability.set_defaults(func=bookings_writer_v2_cmd.cmd_bookings_writer_v2_get_multi_service_availability, write_capable=False)

    bookings_writer_v2_token = bookings_writer_v2_sub.add_parser("get-anonymous-action-token", help="Get an anonymous action token for a booking")
    bookings_writer_v2_token.add_argument("--booking-id", required=True, help="Booking ID")
    bookings_writer_v2_token.set_defaults(func=bookings_writer_v2_cmd.cmd_bookings_writer_v2_get_anonymous_action_token, write_capable=False)

    for command_name, handler, help_text in (
        ("get-anonymous", bookings_writer_v2_cmd.cmd_bookings_writer_v2_get_anonymous, "Get a booking with an anonymous token"),
        ("get-service-anonymous", bookings_writer_v2_cmd.cmd_bookings_writer_v2_get_service_anonymous, "Get the service for an anonymous booking token"),
    ):
        parser = bookings_writer_v2_sub.add_parser(command_name, help=help_text)
        parser.add_argument("--token", required=True, help="Anonymous booking action token")
        parser.set_defaults(func=handler, write_capable=False)

    bookings_writer_v2_create = bookings_writer_v2_sub.add_parser("create", help="Create one booking")
    bookings_writer_v2_create.add_argument("--booking-json", dest="booking_json", required=True, help="Official booking body JSON or @file")
    bookings_writer_v2_create.set_defaults(func=bookings_writer_v2_cmd.cmd_bookings_writer_v2_create, write_capable=True)

    bookings_writer_v2_bulk_create = bookings_writer_v2_sub.add_parser("bulk-create", help="Create up to 12 bookings")
    bookings_writer_v2_bulk_create.add_argument("--bookings-json", dest="bookings_json", required=True, help="Official bulk create body JSON or @file")
    bookings_writer_v2_bulk_create.set_defaults(func=bookings_writer_v2_cmd.cmd_bookings_writer_v2_bulk_create, write_capable=True)

    bookings_writer_v2_create_multi = bookings_writer_v2_sub.add_parser("create-multi-service", help="Create one multi-service booking")
    bookings_writer_v2_create_multi.add_argument("--multi-service-booking-json", dest="multi_service_booking_json", required=True, help="Official multiServiceBooking JSON object/body or @file")
    bookings_writer_v2_create_multi.set_defaults(func=bookings_writer_v2_cmd.cmd_bookings_writer_v2_create_multi_service, write_capable=True)

    for command_name, handler, help_text in (
        ("bulk-confirm-or-decline", bookings_writer_v2_cmd.cmd_bookings_writer_v2_bulk_confirm_or_decline, "Bulk confirm or decline bookings"),
        ("add-to-multi-service", bookings_writer_v2_cmd.cmd_bookings_writer_v2_add_to_multi_service, "Add bookings to a multi-service booking"),
        ("remove-from-multi-service", bookings_writer_v2_cmd.cmd_bookings_writer_v2_remove_from_multi_service, "Remove bookings from a multi-service booking"),
    ):
        parser = bookings_writer_v2_sub.add_parser(command_name, help=help_text)
        parser.add_argument("--request-json", dest="request_json", required=True, help="Official request JSON object or @file")
        parser.set_defaults(func=handler, write_capable=True)

    for command_name, handler, help_text in (
        ("confirm-or-decline", bookings_writer_v2_cmd.cmd_bookings_writer_v2_confirm_or_decline, "Confirm or decline one booking"),
        ("confirm", bookings_writer_v2_cmd.cmd_bookings_writer_v2_confirm, "Confirm one booking"),
        ("decline", bookings_writer_v2_cmd.cmd_bookings_writer_v2_decline, "Decline one booking"),
        ("cancel", bookings_writer_v2_cmd.cmd_bookings_writer_v2_cancel, "Cancel one booking"),
        ("reschedule", bookings_writer_v2_cmd.cmd_bookings_writer_v2_reschedule, "Reschedule one booking"),
        ("mark-pending", bookings_writer_v2_cmd.cmd_bookings_writer_v2_mark_pending, "Mark one booking as pending"),
        ("set-submission-id", bookings_writer_v2_cmd.cmd_bookings_writer_v2_set_submission_id, "Set one booking form submission ID"),
        ("update-extended-fields", bookings_writer_v2_cmd.cmd_bookings_writer_v2_update_extended_fields, "Update one booking's extended fields"),
        ("update-participants", bookings_writer_v2_cmd.cmd_bookings_writer_v2_update_participants, "Update one booking's participant count"),
    ):
        parser = bookings_writer_v2_sub.add_parser(command_name, help=help_text)
        parser.add_argument("--booking-id", required=True, help="Booking ID")
        parser.add_argument("--request-json", dest="request_json", required=True, help="Official request JSON object or @file")
        parser.set_defaults(func=handler, write_capable=True)

    for command_name, handler, help_text in (
        ("cancel-multi-service", bookings_writer_v2_cmd.cmd_bookings_writer_v2_cancel_multi_service, "Cancel one multi-service booking"),
        ("confirm-multi-service", bookings_writer_v2_cmd.cmd_bookings_writer_v2_confirm_multi_service, "Confirm one multi-service booking"),
        ("decline-multi-service", bookings_writer_v2_cmd.cmd_bookings_writer_v2_decline_multi_service, "Decline one multi-service booking"),
        ("reschedule-multi-service", bookings_writer_v2_cmd.cmd_bookings_writer_v2_reschedule_multi_service, "Reschedule one multi-service booking"),
        ("mark-multi-service-pending", bookings_writer_v2_cmd.cmd_bookings_writer_v2_mark_multi_service_pending, "Mark one multi-service booking as pending"),
    ):
        parser = bookings_writer_v2_sub.add_parser(command_name, help=help_text)
        parser.add_argument("--multi-service-booking-id", required=True, help="Multi-service booking ID")
        parser.add_argument("--request-json", dest="request_json", required=True, help="Official request JSON object or @file")
        parser.set_defaults(func=handler, write_capable=True)

    for command_name, handler, help_text in (
        ("cancel-anonymous", bookings_writer_v2_cmd.cmd_bookings_writer_v2_cancel_anonymous, "Cancel a booking with an anonymous token"),
        ("reschedule-anonymous", bookings_writer_v2_cmd.cmd_bookings_writer_v2_reschedule_anonymous, "Reschedule a booking with an anonymous token"),
    ):
        parser = bookings_writer_v2_sub.add_parser(command_name, help=help_text)
        parser.add_argument("--token", required=True, help="Anonymous booking action token")
        parser.add_argument("--request-json", dest="request_json", required=True, help="Official request JSON object or @file")
        parser.set_defaults(func=handler, write_capable=True)

    bookings_services_v2 = sub.add_parser(
        "bookings-services-v2",
        help="Manage Wix Bookings Services V2 methods",
    )
    bookings_services_v2_sub = bookings_services_v2.add_subparsers(
        dest="bookings_services_v2_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    bookings_services_v2_get = bookings_services_v2_sub.add_parser("get", help="Get one Bookings service")
    bookings_services_v2_get.add_argument("--service-id", required=True, help="Bookings service ID")
    bookings_services_v2_get.set_defaults(func=bookings_services_v2_cmd.cmd_bookings_services_v2_get, write_capable=False)

    bookings_services_v2_query = bookings_services_v2_sub.add_parser("query", help="Query Bookings services")
    bookings_services_v2_query.add_argument("--query-json", dest="query_json", default=None, help="Optional official query JSON object or @file")
    bookings_services_v2_query.set_defaults(func=bookings_services_v2_cmd.cmd_bookings_services_v2_query, write_capable=False)

    bookings_services_v2_search = bookings_services_v2_sub.add_parser("search", help="Search Bookings services")
    bookings_services_v2_search.add_argument("--search-json", dest="search_json", default=None, help="Optional official search JSON object or @file")
    bookings_services_v2_search.set_defaults(func=bookings_services_v2_cmd.cmd_bookings_services_v2_search, write_capable=False)

    bookings_services_v2_count = bookings_services_v2_sub.add_parser("count", help="Count Bookings services")
    bookings_services_v2_count.add_argument("--filter-json", dest="filter_json", default=None, help="Optional official filter JSON object or @file")
    bookings_services_v2_count.set_defaults(func=bookings_services_v2_cmd.cmd_bookings_services_v2_count, write_capable=False)

    bookings_services_v2_create = bookings_services_v2_sub.add_parser("create", help="Create one Bookings service")
    bookings_services_v2_create.add_argument("--service-json", dest="service_json", required=True, help="Official service JSON object or @file")
    bookings_services_v2_create.set_defaults(func=bookings_services_v2_cmd.cmd_bookings_services_v2_create, write_capable=True)

    bookings_services_v2_update = bookings_services_v2_sub.add_parser("update", help="Update one Bookings service")
    bookings_services_v2_update.add_argument("--service-id", required=True, help="Bookings service ID")
    bookings_services_v2_update.add_argument("--service-json", dest="service_json", required=True, help="Official service JSON object or @file")
    bookings_services_v2_update.set_defaults(func=bookings_services_v2_cmd.cmd_bookings_services_v2_update, write_capable=True)

    bookings_services_v2_delete = bookings_services_v2_sub.add_parser("delete", help="Delete one Bookings service")
    bookings_services_v2_delete.add_argument("--service-id", required=True, help="Bookings service ID")
    bookings_services_v2_delete.set_defaults(func=bookings_services_v2_cmd.cmd_bookings_services_v2_delete, write_capable=True)

    for command_name, handler, help_text in (
        ("bulk-create", bookings_services_v2_cmd.cmd_bookings_services_v2_bulk_create, "Bulk create Bookings services"),
        ("bulk-update", bookings_services_v2_cmd.cmd_bookings_services_v2_bulk_update, "Bulk update Bookings services"),
    ):
        parser = bookings_services_v2_sub.add_parser(command_name, help=help_text)
        parser.add_argument("--services-json", dest="services_json", required=True, help="Official services array/body JSON or @file")
        parser.set_defaults(func=handler, write_capable=True)

    for command_name, handler, help_text in (
        ("bulk-update-by-filter", bookings_services_v2_cmd.cmd_bookings_services_v2_bulk_update_by_filter, "Bulk update services by filter"),
        ("bulk-delete", bookings_services_v2_cmd.cmd_bookings_services_v2_bulk_delete, "Bulk delete services"),
        ("bulk-delete-by-filter", bookings_services_v2_cmd.cmd_bookings_services_v2_bulk_delete_by_filter, "Bulk delete services by filter"),
        ("clone", bookings_services_v2_cmd.cmd_bookings_services_v2_clone, "Clone a Bookings service"),
        ("create-add-on-group", bookings_services_v2_cmd.cmd_bookings_services_v2_create_add_on_group, "Create a Bookings service add-on group"),
        ("delete-add-on-group", bookings_services_v2_cmd.cmd_bookings_services_v2_delete_add_on_group, "Delete a Bookings service add-on group"),
        ("set-add-ons-for-group", bookings_services_v2_cmd.cmd_bookings_services_v2_set_add_ons_for_group, "Set add-ons for a Bookings service add-on group"),
        ("update-add-on-group", bookings_services_v2_cmd.cmd_bookings_services_v2_update_add_on_group, "Update a Bookings service add-on group"),
    ):
        parser = bookings_services_v2_sub.add_parser(command_name, help=help_text)
        parser.add_argument("--request-json", dest="request_json", required=True, help="Official request JSON object or @file")
        parser.set_defaults(func=handler, write_capable=True)

    for command_name, handler, help_text in (
        ("set-service-locations", bookings_services_v2_cmd.cmd_bookings_services_v2_set_service_locations, "Replace locations for one service"),
        ("enable-pricing-plans", bookings_services_v2_cmd.cmd_bookings_services_v2_enable_pricing_plans, "Enable pricing plans for one service"),
        ("disable-pricing-plans", bookings_services_v2_cmd.cmd_bookings_services_v2_disable_pricing_plans, "Disable pricing plans for one service"),
        ("set-custom-slug", bookings_services_v2_cmd.cmd_bookings_services_v2_set_custom_slug, "Set the custom slug for one service"),
    ):
        parser = bookings_services_v2_sub.add_parser(command_name, help=help_text)
        parser.add_argument("--service-id", required=True, help="Bookings service ID")
        parser.add_argument("--request-json", dest="request_json", required=True, help="Official request JSON object or @file")
        parser.set_defaults(func=handler, write_capable=True)

    for command_name, handler, help_text in (
        ("query-policies", bookings_services_v2_cmd.cmd_bookings_services_v2_query_policies, "Query Bookings policies"),
        ("query-locations", bookings_services_v2_cmd.cmd_bookings_services_v2_query_locations, "Query Bookings service locations"),
        ("query-categories", bookings_services_v2_cmd.cmd_bookings_services_v2_query_categories, "Query Bookings service categories"),
        ("validate-slug", bookings_services_v2_cmd.cmd_bookings_services_v2_validate_slug, "Validate a Bookings service slug"),
        (
            "list-add-on-groups-by-service-id",
            bookings_services_v2_cmd.cmd_bookings_services_v2_list_add_on_groups_by_service_id,
            "List add-on groups for a Bookings service",
        ),
    ):
        parser = bookings_services_v2_sub.add_parser(command_name, help=help_text)
        parser.add_argument("--request-json", dest="request_json", default=None, help="Optional official request JSON object or @file")
        parser.set_defaults(func=handler, write_capable=False)

    bookings_resources_v2 = sub.add_parser(
        "bookings-resources-v2",
        help="Manage Wix Bookings Resources V2 methods",
    )
    bookings_resources_v2_sub = bookings_resources_v2.add_subparsers(
        dest="bookings_resources_v2_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    bookings_resources_v2_get = bookings_resources_v2_sub.add_parser("get", help="Get one Bookings resource")
    bookings_resources_v2_get.add_argument("--resource-id", required=True, help="Bookings resource ID")
    bookings_resources_v2_get.set_defaults(func=bookings_resources_v2_cmd.cmd_bookings_resources_v2_get, write_capable=False)

    bookings_resources_v2_query = bookings_resources_v2_sub.add_parser("query", help="Query Bookings resources")
    bookings_resources_v2_query.add_argument("--query-json", dest="query_json", default=None, help="Optional official query JSON object or @file")
    bookings_resources_v2_query.set_defaults(func=bookings_resources_v2_cmd.cmd_bookings_resources_v2_query, write_capable=False)

    bookings_resources_v2_search = bookings_resources_v2_sub.add_parser("search", help="Search Bookings resources")
    bookings_resources_v2_search.add_argument("--search-json", dest="search_json", default=None, help="Optional official search JSON object or @file")
    bookings_resources_v2_search.set_defaults(func=bookings_resources_v2_cmd.cmd_bookings_resources_v2_search, write_capable=False)

    bookings_resources_v2_count = bookings_resources_v2_sub.add_parser("count", help="Count Bookings resources")
    bookings_resources_v2_count.add_argument("--filter-json", dest="filter_json", default=None, help="Optional official filter JSON object or @file")
    bookings_resources_v2_count.set_defaults(func=bookings_resources_v2_cmd.cmd_bookings_resources_v2_count, write_capable=False)

    bookings_resources_v2_create = bookings_resources_v2_sub.add_parser("create", help="Create one Bookings resource")
    bookings_resources_v2_create.add_argument("--resource-json", dest="resource_json", required=True, help="Official resource JSON object or @file")
    bookings_resources_v2_create.set_defaults(func=bookings_resources_v2_cmd.cmd_bookings_resources_v2_create, write_capable=True)

    bookings_resources_v2_update = bookings_resources_v2_sub.add_parser("update", help="Update one Bookings resource")
    bookings_resources_v2_update.add_argument("--resource-id", required=True, help="Bookings resource ID")
    bookings_resources_v2_update.add_argument("--resource-json", dest="resource_json", required=True, help="Official resource JSON object or @file")
    bookings_resources_v2_update.set_defaults(func=bookings_resources_v2_cmd.cmd_bookings_resources_v2_update, write_capable=True)

    bookings_resources_v2_delete = bookings_resources_v2_sub.add_parser("delete", help="Delete one Bookings resource")
    bookings_resources_v2_delete.add_argument("--resource-id", required=True, help="Bookings resource ID")
    bookings_resources_v2_delete.set_defaults(func=bookings_resources_v2_cmd.cmd_bookings_resources_v2_delete, write_capable=True)

    for command_name, handler, help_text in (
        ("bulk-create", bookings_resources_v2_cmd.cmd_bookings_resources_v2_bulk_create, "Bulk create Bookings resources"),
        ("bulk-update", bookings_resources_v2_cmd.cmd_bookings_resources_v2_bulk_update, "Bulk update Bookings resources"),
    ):
        parser = bookings_resources_v2_sub.add_parser(command_name, help=help_text)
        parser.add_argument("--resources-json", dest="resources_json", required=True, help="Official resources array/body JSON or @file")
        parser.set_defaults(func=handler, write_capable=True)

    bookings_resources_v2_bulk_delete = bookings_resources_v2_sub.add_parser("bulk-delete", help="Bulk delete Bookings resources")
    bookings_resources_v2_bulk_delete.add_argument("--ids-json", dest="ids_json", required=True, help="Official ids array/body JSON or @file")
    bookings_resources_v2_bulk_delete.set_defaults(func=bookings_resources_v2_cmd.cmd_bookings_resources_v2_bulk_delete, write_capable=True)

    bookings_resource_types_v2 = sub.add_parser(
        "bookings-resource-types-v2",
        help="Manage Wix Bookings Resource Types V2 methods",
    )
    bookings_resource_types_v2_sub = bookings_resource_types_v2.add_subparsers(
        dest="bookings_resource_types_v2_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    bookings_resource_types_v2_get = bookings_resource_types_v2_sub.add_parser("get", help="Get one Bookings resource type")
    bookings_resource_types_v2_get.add_argument("--resource-type-id", required=True, help="Bookings resource type ID")
    bookings_resource_types_v2_get.set_defaults(func=bookings_resource_types_v2_cmd.cmd_bookings_resource_types_v2_get, write_capable=False)

    bookings_resource_types_v2_query = bookings_resource_types_v2_sub.add_parser("query", help="Query Bookings resource types")
    bookings_resource_types_v2_query.add_argument("--query-json", dest="query_json", default=None, help="Optional official query JSON object or @file")
    bookings_resource_types_v2_query.set_defaults(func=bookings_resource_types_v2_cmd.cmd_bookings_resource_types_v2_query, write_capable=False)

    bookings_resource_types_v2_count = bookings_resource_types_v2_sub.add_parser("count", help="Count Bookings resource types")
    bookings_resource_types_v2_count.add_argument("--filter-json", dest="filter_json", default=None, help="Optional official filter JSON object or @file")
    bookings_resource_types_v2_count.set_defaults(func=bookings_resource_types_v2_cmd.cmd_bookings_resource_types_v2_count, write_capable=False)

    bookings_resource_types_v2_create = bookings_resource_types_v2_sub.add_parser("create", help="Create one Bookings resource type")
    bookings_resource_types_v2_create.add_argument("--resource-type-json", dest="resource_type_json", required=True, help="Official resourceType JSON object or @file")
    bookings_resource_types_v2_create.set_defaults(func=bookings_resource_types_v2_cmd.cmd_bookings_resource_types_v2_create, write_capable=True)

    bookings_resource_types_v2_update = bookings_resource_types_v2_sub.add_parser("update", help="Update one Bookings resource type")
    bookings_resource_types_v2_update.add_argument("--resource-type-id", required=True, help="Bookings resource type ID")
    bookings_resource_types_v2_update.add_argument("--resource-type-json", dest="resource_type_json", required=True, help="Official resourceType JSON object or @file")
    bookings_resource_types_v2_update.set_defaults(func=bookings_resource_types_v2_cmd.cmd_bookings_resource_types_v2_update, write_capable=True)

    bookings_resource_types_v2_delete = bookings_resource_types_v2_sub.add_parser("delete", help="Delete one Bookings resource type")
    bookings_resource_types_v2_delete.add_argument("--resource-type-id", required=True, help="Bookings resource type ID")
    bookings_resource_types_v2_delete.set_defaults(func=bookings_resource_types_v2_cmd.cmd_bookings_resource_types_v2_delete, write_capable=True)

    bookings_staff_members = sub.add_parser(
        "bookings-staff-members",
        help="Manage Wix Bookings Staff Members methods",
    )
    bookings_staff_members_sub = bookings_staff_members.add_subparsers(
        dest="bookings_staff_members_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    for command_name, handler, help_text in (
        ("get", bookings_staff_members_cmd.cmd_bookings_staff_members_get, "Get one Bookings staff member"),
        ("get-deleted", bookings_staff_members_cmd.cmd_bookings_staff_members_get_deleted, "Get one deleted Bookings staff member"),
    ):
        parser = bookings_staff_members_sub.add_parser(command_name, help=help_text)
        parser.add_argument("--staff-member-id", required=True, help="Bookings staff member ID")
        parser.add_argument("--field", action="append", default=[], help="Optional official field enum, repeatable")
        parser.set_defaults(func=handler, write_capable=False)

    bookings_staff_members_query = bookings_staff_members_sub.add_parser("query", help="Query Bookings staff members")
    bookings_staff_members_query.add_argument("--query-json", dest="query_json", default=None, help="Optional official query JSON object/body or @file")
    bookings_staff_members_query.set_defaults(func=bookings_staff_members_cmd.cmd_bookings_staff_members_query, write_capable=False)

    bookings_staff_members_search = bookings_staff_members_sub.add_parser("search", help="Search Bookings staff members")
    bookings_staff_members_search.add_argument("--search-json", dest="search_json", required=True, help="Official search JSON object/body or @file")
    bookings_staff_members_search.set_defaults(func=bookings_staff_members_cmd.cmd_bookings_staff_members_search, write_capable=False)

    bookings_staff_members_count = bookings_staff_members_sub.add_parser("count", help="Count Bookings staff members")
    bookings_staff_members_count.add_argument("--filter-json", dest="filter_json", default=None, help="Optional official filter JSON object or @file")
    bookings_staff_members_count.set_defaults(func=bookings_staff_members_cmd.cmd_bookings_staff_members_count, write_capable=False)

    bookings_staff_members_list_deleted = bookings_staff_members_sub.add_parser("list-deleted", help="List deleted Bookings staff members")
    bookings_staff_members_list_deleted.add_argument("--field", action="append", default=[], help="Optional official field enum, repeatable")
    bookings_staff_members_list_deleted.add_argument("--limit", type=int, default=None, help="Optional official paging.limit")
    bookings_staff_members_list_deleted.add_argument("--cursor", default=None, help="Optional official paging.cursor")
    bookings_staff_members_list_deleted.set_defaults(func=bookings_staff_members_cmd.cmd_bookings_staff_members_list_deleted, write_capable=False)

    bookings_staff_members_create = bookings_staff_members_sub.add_parser("create", help="Create one Bookings staff member")
    bookings_staff_members_create.add_argument("--staff-member-json", dest="staff_member_json", required=True, help="Official staffMember JSON object or @file")
    bookings_staff_members_create.set_defaults(func=bookings_staff_members_cmd.cmd_bookings_staff_members_create, write_capable=True)

    bookings_staff_members_update = bookings_staff_members_sub.add_parser("update", help="Update one Bookings staff member")
    bookings_staff_members_update.add_argument("--staff-member-id", required=True, help="Bookings staff member ID")
    bookings_staff_members_update.add_argument("--staff-member-json", dest="staff_member_json", required=True, help="Official staffMember JSON object or @file")
    bookings_staff_members_update.set_defaults(func=bookings_staff_members_cmd.cmd_bookings_staff_members_update, write_capable=True)

    for command_name, handler, help_text in (
        ("delete", bookings_staff_members_cmd.cmd_bookings_staff_members_delete, "Delete one Bookings staff member"),
        ("remove-from-trash", bookings_staff_members_cmd.cmd_bookings_staff_members_remove_from_trash, "Permanently remove a deleted Bookings staff member"),
    ):
        parser = bookings_staff_members_sub.add_parser(command_name, help=help_text)
        parser.add_argument("--staff-member-id", required=True, help="Bookings staff member ID")
        parser.set_defaults(func=handler, write_capable=True)

    bookings_staff_members_assign_schedule = bookings_staff_members_sub.add_parser(
        "assign-working-hours-schedule",
        help="Assign a working-hours schedule to a Bookings staff member",
    )
    bookings_staff_members_assign_schedule.add_argument("--staff-member-id", required=True, help="Bookings staff member ID")
    bookings_staff_members_assign_schedule.add_argument("--schedule-id", required=True, help="Calendar schedule ID")
    bookings_staff_members_assign_schedule.add_argument("--field", action="append", default=[], help="Optional official field enum, repeatable")
    bookings_staff_members_assign_schedule.set_defaults(
        func=bookings_staff_members_cmd.cmd_bookings_staff_members_assign_working_hours_schedule,
        write_capable=True,
    )

    bookings_staff_members_bulk_tags = bookings_staff_members_sub.add_parser("bulk-update-tags", help="Bulk update Bookings staff member tags by IDs")
    bookings_staff_members_bulk_tags.add_argument("--tags-json", dest="tags_json", required=True, help="Official bulk tag update body or @file")
    bookings_staff_members_bulk_tags.set_defaults(func=bookings_staff_members_cmd.cmd_bookings_staff_members_bulk_update_tags, write_capable=True)

    bookings_staff_members_bulk_tags_filter = bookings_staff_members_sub.add_parser(
        "bulk-update-tags-by-filter",
        help="Bulk update Bookings staff member tags by filter",
    )
    bookings_staff_members_bulk_tags_filter.add_argument(
        "--tags-filter-json",
        dest="tags_filter_json",
        required=True,
        help="Official bulk tag filter update body or @file",
    )
    bookings_staff_members_bulk_tags_filter.set_defaults(
        func=bookings_staff_members_cmd.cmd_bookings_staff_members_bulk_update_tags_by_filter,
        write_capable=True,
    )

    bookings_staff_members_connect = bookings_staff_members_sub.add_parser("connect-to-user", help="Connect a Bookings staff member to a Wix user")
    bookings_staff_members_connect.add_argument("--staff-member-id", required=True, help="Bookings staff member ID")
    bookings_staff_members_connect.add_argument("--connect-json", dest="connect_json", default=None, help="Optional official connect body or @file")
    bookings_staff_members_connect.set_defaults(func=bookings_staff_members_cmd.cmd_bookings_staff_members_connect_to_user, write_capable=True)

    bookings_staff_members_disconnect = bookings_staff_members_sub.add_parser(
        "disconnect-from-user",
        help="Disconnect a Bookings staff member from a Wix user",
    )
    bookings_staff_members_disconnect.add_argument("--staff-member-id", required=True, help="Bookings staff member ID")
    bookings_staff_members_disconnect.add_argument("--disconnect-json", dest="disconnect_json", default=None, help="Optional official disconnect body or @file")
    bookings_staff_members_disconnect.set_defaults(func=bookings_staff_members_cmd.cmd_bookings_staff_members_disconnect_from_user, write_capable=True)

    bookings_time_slots_v2 = sub.add_parser(
        "bookings-time-slots-v2",
        help="Read Wix Bookings appointment availability methods",
    )
    bookings_time_slots_v2_sub = bookings_time_slots_v2.add_subparsers(
        dest="bookings_time_slots_v2_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    bookings_time_slots_v2_list_availability = bookings_time_slots_v2_sub.add_parser(
        "list-availability",
        help="List available appointment time slots",
    )
    bookings_time_slots_v2_list_availability.add_argument(
        "--list-availability-json",
        dest="list_availability_json",
        required=True,
        help="Official list-availability JSON request body or @file",
    )
    bookings_time_slots_v2_list_availability.set_defaults(
        func=bookings_time_slots_v2_cmd.cmd_bookings_time_slots_v2_list_availability,
        write_capable=False,
    )

    bookings_time_slots_v2_get_availability = bookings_time_slots_v2_sub.add_parser(
        "get-availability",
        help="Get detailed appointment time-slot availability",
    )
    bookings_time_slots_v2_get_availability.add_argument(
        "--get-availability-json",
        dest="get_availability_json",
        required=True,
        help="Official get-availability JSON request body or @file",
    )
    bookings_time_slots_v2_get_availability.set_defaults(
        func=bookings_time_slots_v2_cmd.cmd_bookings_time_slots_v2_get_availability,
        write_capable=False,
    )

    bookings_time_slots_v2_list_event = bookings_time_slots_v2_sub.add_parser(
        "list-event",
        help="List available class event time slots",
    )
    bookings_time_slots_v2_list_event.add_argument(
        "--list-event-json",
        dest="list_event_json",
        required=True,
        help="Official list-event JSON request body or @file",
    )
    bookings_time_slots_v2_list_event.set_defaults(
        func=bookings_time_slots_v2_cmd.cmd_bookings_time_slots_v2_list_event,
        write_capable=False,
    )

    bookings_time_slots_v2_get_event = bookings_time_slots_v2_sub.add_parser(
        "get-event",
        help="Get detailed class event time-slot availability",
    )
    bookings_time_slots_v2_get_event.add_argument(
        "--event-id",
        required=True,
        help="Bookings event time-slot ID",
    )
    bookings_time_slots_v2_get_event.set_defaults(
        func=bookings_time_slots_v2_cmd.cmd_bookings_time_slots_v2_get_event,
        write_capable=False,
    )

    bookings_time_slots_v2_list_multi_service = bookings_time_slots_v2_sub.add_parser(
        "list-multi-service",
        help="List available multi-service appointment time slots",
    )
    bookings_time_slots_v2_list_multi_service.add_argument(
        "--list-multi-service-json",
        dest="list_multi_service_json",
        required=True,
        help="Official list-multi-service JSON request body or @file",
    )
    bookings_time_slots_v2_list_multi_service.set_defaults(
        func=bookings_time_slots_v2_cmd.cmd_bookings_time_slots_v2_list_multi_service,
        write_capable=False,
    )

    bookings_time_slots_v2_get_multi_service = bookings_time_slots_v2_sub.add_parser(
        "get-multi-service",
        help="Get detailed multi-service appointment time-slot availability",
    )
    bookings_time_slots_v2_get_multi_service.add_argument(
        "--get-multi-service-json",
        dest="get_multi_service_json",
        required=True,
        help="Official get-multi-service JSON request body or @file",
    )
    bookings_time_slots_v2_get_multi_service.set_defaults(
        func=bookings_time_slots_v2_cmd.cmd_bookings_time_slots_v2_get_multi_service,
        write_capable=False,
    )

    bookings_reader_v2 = sub.add_parser(
        "bookings-reader-v2",
        help="Read Wix Bookings extended booking methods",
    )
    bookings_reader_v2_sub = bookings_reader_v2.add_subparsers(
        dest="bookings_reader_v2_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    bookings_reader_v2_query = bookings_reader_v2_sub.add_parser(
        "query-extended-bookings",
        help="Query extended bookings",
    )
    bookings_reader_v2_query.add_argument(
        "--query-json",
        dest="query_extended_bookings_json",
        required=True,
        help="Official query-extended-bookings JSON request body or @file",
    )
    bookings_reader_v2_query.set_defaults(
        func=bookings_reader_v2_cmd.cmd_bookings_reader_v2_query_extended_bookings,
        write_capable=False,
    )

    bookings_reader_v2_count = bookings_reader_v2_sub.add_parser(
        "count-extended-bookings",
        help="Count extended bookings",
    )
    bookings_reader_v2_count.add_argument(
        "--filter-json",
        dest="filter_json",
        default=None,
        help="Optional official filter JSON request body or @file",
    )
    bookings_reader_v2_count.set_defaults(
        func=bookings_reader_v2_cmd.cmd_bookings_reader_v2_count_extended_bookings,
        write_capable=False,
    )

    stores_products_v3 = sub.add_parser("stores-products-v3", help="Read and manage Wix Stores Catalog V3 products")
    stores_products_v3_sub = stores_products_v3.add_subparsers(
        dest="stores_products_v3_cmd", required=True, parser_class=_ToolArgumentParser
    )

    stores_products_v3_get = stores_products_v3_sub.add_parser("get", help="Get one Catalog V3 product by id")
    stores_products_v3_get.add_argument("--product-id", required=True, dest="product_id", help="Product ID")
    stores_products_v3_get.set_defaults(func=stores_products_v3_cmd.cmd_stores_products_v3_get, write_capable=False)

    stores_products_v3_get_by_slug = stores_products_v3_sub.add_parser(
        "get-by-slug",
        help="Get one Catalog V3 product by slug",
    )
    stores_products_v3_get_by_slug.add_argument("--slug", required=True, help="Product slug")
    stores_products_v3_get_by_slug.set_defaults(
        func=stores_products_v3_cmd.cmd_stores_products_v3_get_by_slug,
        write_capable=False,
    )

    stores_products_v3_get_all_products_category = stores_products_v3_sub.add_parser(
        "get-all-products-category",
        help='Get the Catalog V3 "All Products" category id',
    )
    stores_products_v3_get_all_products_category.set_defaults(
        func=stores_products_v3_cmd.cmd_stores_products_v3_get_all_products_category,
        write_capable=False,
    )

    stores_products_v3_query = stores_products_v3_sub.add_parser("query", help="Query Catalog V3 products")
    stores_products_v3_query.add_argument(
        "--query-json",
        dest="query_json",
        default=None,
        help="Optional JSON query object or full official query body",
    )
    stores_products_v3_query.set_defaults(
        func=stores_products_v3_cmd.cmd_stores_products_v3_query,
        write_capable=False,
    )

    stores_products_v3_search = stores_products_v3_sub.add_parser("search", help="Search Catalog V3 products")
    stores_products_v3_search.add_argument(
        "--search-json",
        dest="search_json",
        default=None,
        help="Optional JSON search object or full official search body",
    )
    stores_products_v3_search.set_defaults(
        func=stores_products_v3_cmd.cmd_stores_products_v3_search,
        write_capable=False,
    )

    stores_products_v3_count = stores_products_v3_sub.add_parser("count", help="Count Catalog V3 products")
    stores_products_v3_count.add_argument(
        "--filter-json",
        dest="filter_json",
        default=None,
        help="Optional JSON filter object or full official count body",
    )
    stores_products_v3_count.set_defaults(
        func=stores_products_v3_cmd.cmd_stores_products_v3_count,
        write_capable=False,
    )

    stores_products_v3_create = stores_products_v3_sub.add_parser("create", help="Create one Catalog V3 product")
    stores_products_v3_create.add_argument(
        "--product-json",
        dest="product_json",
        required=True,
        help="JSON product object, full create body, or @file",
    )
    stores_products_v3_create.set_defaults(
        func=stores_products_v3_cmd.cmd_stores_products_v3_create,
        write_capable=True,
    )

    stores_products_v3_update = stores_products_v3_sub.add_parser("update", help="Update one Catalog V3 product")
    stores_products_v3_update.add_argument("--product-id", required=True, dest="product_id", help="Product ID")
    stores_products_v3_update.add_argument(
        "--product-json",
        dest="product_json",
        required=True,
        help="JSON product object, full update body, or @file. Must include the current revision.",
    )
    stores_products_v3_update.set_defaults(
        func=stores_products_v3_cmd.cmd_stores_products_v3_update,
        write_capable=True,
    )

    stores_products_v3_delete = stores_products_v3_sub.add_parser("delete", help="Delete one Catalog V3 product")
    stores_products_v3_delete.add_argument("--product-id", required=True, dest="product_id", help="Product ID")
    stores_products_v3_delete.set_defaults(
        func=stores_products_v3_cmd.cmd_stores_products_v3_delete,
        write_capable=True,
    )

    stores_products_v3_bulk_create = stores_products_v3_sub.add_parser(
        "bulk-create",
        help="Create multiple Catalog V3 products",
    )
    stores_products_v3_bulk_create.add_argument(
        "--products-json",
        dest="products_json",
        required=True,
        help="JSON products array/body or @file",
    )
    stores_products_v3_bulk_create.set_defaults(
        func=stores_products_v3_cmd.cmd_stores_products_v3_bulk_create,
        write_capable=True,
    )

    stores_products_v3_bulk_delete = stores_products_v3_sub.add_parser(
        "bulk-delete",
        help="Delete multiple Catalog V3 products",
    )
    stores_products_v3_bulk_delete.add_argument(
        "--request-json",
        dest="request_json",
        required=True,
        help="Official bulk delete request body JSON or @file",
    )
    stores_products_v3_bulk_delete.set_defaults(
        func=stores_products_v3_cmd.cmd_stores_products_v3_bulk_delete,
        write_capable=True,
    )

    stores_products_v3_bulk_update = stores_products_v3_sub.add_parser(
        "bulk-update",
        help="Update multiple Catalog V3 products",
    )
    stores_products_v3_bulk_update.add_argument(
        "--products-json",
        dest="products_json",
        required=True,
        help="JSON products array/body with revisions or @file",
    )
    stores_products_v3_bulk_update.set_defaults(
        func=stores_products_v3_cmd.cmd_stores_products_v3_bulk_update,
        write_capable=True,
    )

    stores_products_v3_create_with_inventory = stores_products_v3_sub.add_parser(
        "create-with-inventory",
        help="Create one Catalog V3 product with inventory",
    )
    stores_products_v3_create_with_inventory.add_argument(
        "--product-json",
        dest="product_json",
        required=True,
        help="JSON product-with-inventory object/body or @file",
    )
    stores_products_v3_create_with_inventory.set_defaults(
        func=stores_products_v3_cmd.cmd_stores_products_v3_create_with_inventory,
        write_capable=True,
    )

    stores_products_v3_update_with_inventory = stores_products_v3_sub.add_parser(
        "update-with-inventory",
        help="Update one Catalog V3 product with inventory",
    )
    stores_products_v3_update_with_inventory.add_argument("--product-id", required=True, dest="product_id", help="Product ID")
    stores_products_v3_update_with_inventory.add_argument(
        "--product-json",
        dest="product_json",
        required=True,
        help="JSON product-with-inventory object/body with revision or @file",
    )
    stores_products_v3_update_with_inventory.set_defaults(
        func=stores_products_v3_cmd.cmd_stores_products_v3_update_with_inventory,
        write_capable=True,
    )

    stores_products_v3_bulk_create_with_inventory = stores_products_v3_sub.add_parser(
        "bulk-create-with-inventory",
        help="Create multiple Catalog V3 products with inventory",
    )
    stores_products_v3_bulk_create_with_inventory.add_argument(
        "--products-json",
        dest="products_json",
        required=True,
        help="JSON products-with-inventory array/body or @file",
    )
    stores_products_v3_bulk_create_with_inventory.set_defaults(
        func=stores_products_v3_cmd.cmd_stores_products_v3_bulk_create_with_inventory,
        write_capable=True,
    )

    stores_products_v3_bulk_update_with_inventory = stores_products_v3_sub.add_parser(
        "bulk-update-with-inventory",
        help="Update multiple Catalog V3 products with inventory",
    )
    stores_products_v3_bulk_update_with_inventory.add_argument(
        "--products-json",
        dest="products_json",
        required=True,
        help="JSON products-with-inventory array/body with revisions or @file",
    )
    stores_products_v3_bulk_update_with_inventory.set_defaults(
        func=stores_products_v3_cmd.cmd_stores_products_v3_bulk_update_with_inventory,
        write_capable=True,
    )

    for command_name, help_text, func in [
        (
            "bulk-add-info-sections",
            "Add info sections to multiple Catalog V3 products",
            stores_products_v3_cmd.cmd_stores_products_v3_bulk_add_info_sections,
        ),
        (
            "bulk-add-info-sections-by-filter",
            "Add info sections to Catalog V3 products by filter",
            stores_products_v3_cmd.cmd_stores_products_v3_bulk_add_info_sections_by_filter,
        ),
        (
            "bulk-add-to-categories-by-filter",
            "Add Catalog V3 products to categories by filter",
            stores_products_v3_cmd.cmd_stores_products_v3_bulk_add_to_categories_by_filter,
        ),
        (
            "bulk-adjust-variants-by-filter",
            "Adjust Catalog V3 product variants by filter",
            stores_products_v3_cmd.cmd_stores_products_v3_bulk_adjust_variants_by_filter,
        ),
        (
            "bulk-delete-by-filter",
            "Delete Catalog V3 products by filter",
            stores_products_v3_cmd.cmd_stores_products_v3_bulk_delete_by_filter,
        ),
        (
            "bulk-remove-info-sections",
            "Remove info sections from multiple Catalog V3 products",
            stores_products_v3_cmd.cmd_stores_products_v3_bulk_remove_info_sections,
        ),
        (
            "bulk-remove-info-sections-by-filter",
            "Remove info sections from Catalog V3 products by filter",
            stores_products_v3_cmd.cmd_stores_products_v3_bulk_remove_info_sections_by_filter,
        ),
        (
            "bulk-remove-from-categories-by-filter",
            "Remove Catalog V3 products from categories by filter",
            stores_products_v3_cmd.cmd_stores_products_v3_bulk_remove_from_categories_by_filter,
        ),
        (
            "bulk-update-variants-by-filter",
            "Update Catalog V3 product variants by filter",
            stores_products_v3_cmd.cmd_stores_products_v3_bulk_update_variants_by_filter,
        ),
        (
            "bulk-update-by-filter",
            "Update Catalog V3 products by filter",
            stores_products_v3_cmd.cmd_stores_products_v3_bulk_update_by_filter,
        ),
    ]:
        request_parser = stores_products_v3_sub.add_parser(command_name, help=help_text)
        request_parser.add_argument(
            "--request-json",
            dest="request_json",
            required=True,
            help="Official request body JSON or @file",
        )
        request_parser.set_defaults(func=func, write_capable=True)

    read_only_variants_v3 = sub.add_parser(
        "read-only-variants-v3",
        help="Query and search Wix Stores Catalog V3 variants as primary entities",
    )
    read_only_variants_v3_sub = read_only_variants_v3.add_subparsers(
        dest="read_only_variants_v3_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    read_only_variants_v3_query = read_only_variants_v3_sub.add_parser(
        "query",
        help="Query Catalog V3 variants with structured filters",
    )
    read_only_variants_v3_query.add_argument(
        "--query-json",
        dest="query_json",
        default=None,
        help="Optional JSON query object or full official query body",
    )
    read_only_variants_v3_query.set_defaults(
        func=read_only_variants_v3_cmd.cmd_read_only_variants_v3_query,
        write_capable=False,
    )

    read_only_variants_v3_search = read_only_variants_v3_sub.add_parser(
        "search",
        help="Search Catalog V3 variants with free-text and aggregations",
    )
    read_only_variants_v3_search.add_argument(
        "--search-json",
        dest="search_json",
        default=None,
        help="Optional JSON search object or full official search body",
    )
    read_only_variants_v3_search.set_defaults(
        func=read_only_variants_v3_cmd.cmd_read_only_variants_v3_search,
        write_capable=False,
    )

    brands_v3 = sub.add_parser("brands-v3", help="Read and manage Wix Stores Catalog V3 brands")
    brands_v3_sub = brands_v3.add_subparsers(
        dest="brands_v3_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    brands_v3_get = brands_v3_sub.add_parser("get", help="Get one Catalog V3 brand by id")
    brands_v3_get.add_argument("--brand-id", required=True, dest="brand_id", help="Brand ID")
    brands_v3_get.set_defaults(func=brands_v3_cmd.cmd_brands_v3_get, write_capable=False)

    brands_v3_query = brands_v3_sub.add_parser("query", help="Query Catalog V3 brands")
    brands_v3_query.add_argument(
        "--query-json",
        dest="query_json",
        default=None,
        help="Optional JSON query object or full official query body",
    )
    brands_v3_query.set_defaults(func=brands_v3_cmd.cmd_brands_v3_query, write_capable=False)

    brands_v3_create = brands_v3_sub.add_parser("create", help="Create one Catalog V3 brand")
    brands_v3_create.add_argument("--brand-json", required=True, dest="brand_json", help="Brand JSON object or @file")
    brands_v3_create.set_defaults(func=brands_v3_cmd.cmd_brands_v3_create, write_capable=True)

    brands_v3_update = brands_v3_sub.add_parser("update", help="Update one Catalog V3 brand")
    brands_v3_update.add_argument("--brand-id", required=True, dest="brand_id", help="Brand ID")
    brands_v3_update.add_argument(
        "--brand-json",
        required=True,
        dest="brand_json",
        help="Brand JSON object with current revision or @file",
    )
    brands_v3_update.set_defaults(func=brands_v3_cmd.cmd_brands_v3_update, write_capable=True)

    brands_v3_delete = brands_v3_sub.add_parser("delete", help="Delete one Catalog V3 brand")
    brands_v3_delete.add_argument("--brand-id", required=True, dest="brand_id", help="Brand ID")
    brands_v3_delete.set_defaults(func=brands_v3_cmd.cmd_brands_v3_delete, write_capable=True)

    brands_v3_bulk_create = brands_v3_sub.add_parser("bulk-create", help="Create multiple Catalog V3 brands")
    brands_v3_bulk_create.add_argument(
        "--brands-json",
        required=True,
        dest="brands_json",
        help="Brands array, official body object, or @file",
    )
    brands_v3_bulk_create.set_defaults(func=brands_v3_cmd.cmd_brands_v3_bulk_create, write_capable=True)

    brands_v3_bulk_delete = brands_v3_sub.add_parser("bulk-delete", help="Delete multiple Catalog V3 brands")
    brands_v3_bulk_delete.add_argument(
        "--brand-ids-json",
        required=True,
        dest="brand_ids_json",
        help="Brand IDs JSON array or @file",
    )
    brands_v3_bulk_delete.set_defaults(func=brands_v3_cmd.cmd_brands_v3_bulk_delete, write_capable=True)

    brands_v3_bulk_update = brands_v3_sub.add_parser("bulk-update", help="Update multiple Catalog V3 brands")
    brands_v3_bulk_update.add_argument(
        "--brands-json",
        required=True,
        dest="brands_json",
        help="Brands array with current revisions, official body object, or @file",
    )
    brands_v3_bulk_update.set_defaults(func=brands_v3_cmd.cmd_brands_v3_bulk_update, write_capable=True)

    brands_v3_get_or_create = brands_v3_sub.add_parser(
        "get-or-create",
        help="Get one Catalog V3 brand by name or create it",
    )
    brands_v3_get_or_create.add_argument("--brand-name", required=True, dest="brand_name", help="Brand name")
    brands_v3_get_or_create.set_defaults(func=brands_v3_cmd.cmd_brands_v3_get_or_create, write_capable=True)

    brands_v3_bulk_get_or_create = brands_v3_sub.add_parser(
        "bulk-get-or-create",
        help="Get or create multiple Catalog V3 brands by name",
    )
    brands_v3_bulk_get_or_create.add_argument(
        "--brand-names-json",
        required=True,
        dest="brand_names_json",
        help="Brand names JSON array, official body object, or @file",
    )
    brands_v3_bulk_get_or_create.set_defaults(
        func=brands_v3_cmd.cmd_brands_v3_bulk_get_or_create,
        write_capable=True,
    )

    ribbons_v3 = sub.add_parser("ribbons-v3", help="Read and manage Wix Stores Catalog V3 ribbons")
    ribbons_v3_sub = ribbons_v3.add_subparsers(
        dest="ribbons_v3_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    ribbons_v3_get = ribbons_v3_sub.add_parser("get", help="Get one Catalog V3 ribbon by id")
    ribbons_v3_get.add_argument("--ribbon-id", required=True, dest="ribbon_id", help="Ribbon ID")
    ribbons_v3_get.set_defaults(func=ribbons_v3_cmd.cmd_ribbons_v3_get, write_capable=False)

    ribbons_v3_query = ribbons_v3_sub.add_parser("query", help="Query Catalog V3 ribbons")
    ribbons_v3_query.add_argument(
        "--query-json",
        dest="query_json",
        default=None,
        help="Optional JSON query object or full official query body",
    )
    ribbons_v3_query.set_defaults(func=ribbons_v3_cmd.cmd_ribbons_v3_query, write_capable=False)

    ribbons_v3_create = ribbons_v3_sub.add_parser("create", help="Create one Catalog V3 ribbon")
    ribbons_v3_create.add_argument("--ribbon-json", required=True, dest="ribbon_json", help="Ribbon JSON object or @file")
    ribbons_v3_create.set_defaults(func=ribbons_v3_cmd.cmd_ribbons_v3_create, write_capable=True)

    ribbons_v3_update = ribbons_v3_sub.add_parser("update", help="Update one Catalog V3 ribbon")
    ribbons_v3_update.add_argument("--ribbon-id", required=True, dest="ribbon_id", help="Ribbon ID")
    ribbons_v3_update.add_argument("--ribbon-json", required=True, dest="ribbon_json", help="Ribbon JSON object with current revision or @file")
    ribbons_v3_update.set_defaults(func=ribbons_v3_cmd.cmd_ribbons_v3_update, write_capable=True)

    ribbons_v3_delete = ribbons_v3_sub.add_parser("delete", help="Delete one Catalog V3 ribbon")
    ribbons_v3_delete.add_argument("--ribbon-id", required=True, dest="ribbon_id", help="Ribbon ID")
    ribbons_v3_delete.set_defaults(func=ribbons_v3_cmd.cmd_ribbons_v3_delete, write_capable=True)

    ribbons_v3_bulk_create = ribbons_v3_sub.add_parser("bulk-create", help="Create multiple Catalog V3 ribbons")
    ribbons_v3_bulk_create.add_argument("--ribbons-json", required=True, dest="ribbons_json", help="Ribbons array/body JSON or @file")
    ribbons_v3_bulk_create.set_defaults(func=ribbons_v3_cmd.cmd_ribbons_v3_bulk_create, write_capable=True)

    ribbons_v3_bulk_delete = ribbons_v3_sub.add_parser("bulk-delete", help="Delete multiple Catalog V3 ribbons")
    ribbons_v3_bulk_delete.add_argument("--ribbon-ids-json", required=True, dest="ribbon_ids_json", help="Ribbon IDs JSON array or @file")
    ribbons_v3_bulk_delete.set_defaults(func=ribbons_v3_cmd.cmd_ribbons_v3_bulk_delete, write_capable=True)

    ribbons_v3_bulk_update = ribbons_v3_sub.add_parser("bulk-update", help="Update multiple Catalog V3 ribbons")
    ribbons_v3_bulk_update.add_argument("--ribbons-json", required=True, dest="ribbons_json", help="Ribbons array/body JSON with current revisions or @file")
    ribbons_v3_bulk_update.set_defaults(func=ribbons_v3_cmd.cmd_ribbons_v3_bulk_update, write_capable=True)

    ribbons_v3_get_or_create = ribbons_v3_sub.add_parser("get-or-create", help="Get or create one Catalog V3 ribbon by name")
    ribbons_v3_get_or_create.add_argument("--ribbon-name", required=True, dest="ribbon_name", help="Ribbon name")
    ribbons_v3_get_or_create.set_defaults(func=ribbons_v3_cmd.cmd_ribbons_v3_get_or_create, write_capable=True)

    ribbons_v3_bulk_get_or_create = ribbons_v3_sub.add_parser(
        "bulk-get-or-create",
        help="Get or create multiple Catalog V3 ribbons by name",
    )
    ribbons_v3_bulk_get_or_create.add_argument(
        "--ribbon-names-json",
        required=True,
        dest="ribbon_names_json",
        help="Ribbon names JSON array or @file",
    )
    ribbons_v3_bulk_get_or_create.set_defaults(
        func=ribbons_v3_cmd.cmd_ribbons_v3_bulk_get_or_create,
        write_capable=True,
    )

    stores_info_sections_v3 = sub.add_parser(
        "stores-info-sections-v3",
        help="Read and manage Wix Stores Catalog V3 info sections",
    )
    stores_info_sections_v3_sub = stores_info_sections_v3.add_subparsers(
        dest="stores_info_sections_v3_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    stores_info_sections_v3_get = stores_info_sections_v3_sub.add_parser(
        "get",
        help="Get one Catalog V3 info section by id",
    )
    stores_info_sections_v3_get.add_argument(
        "--info-section-id",
        required=True,
        dest="info_section_id",
        help="Info section ID",
    )
    stores_info_sections_v3_get.set_defaults(
        func=stores_info_sections_v3_cmd.cmd_stores_info_sections_v3_get,
        write_capable=False,
    )

    stores_info_sections_v3_query = stores_info_sections_v3_sub.add_parser(
        "query",
        help="Query Catalog V3 info sections",
    )
    stores_info_sections_v3_query.add_argument(
        "--query-json",
        dest="query_json",
        default=None,
        help="Optional JSON query object or full official query body",
    )
    stores_info_sections_v3_query.set_defaults(
        func=stores_info_sections_v3_cmd.cmd_stores_info_sections_v3_query,
        write_capable=False,
    )

    stores_info_sections_v3_create = stores_info_sections_v3_sub.add_parser(
        "create",
        help="Create one Catalog V3 info section",
    )
    stores_info_sections_v3_create.add_argument(
        "--info-section-json",
        dest="info_section_json",
        required=True,
        help="JSON infoSection object, full create body, or @file",
    )
    stores_info_sections_v3_create.set_defaults(
        func=stores_info_sections_v3_cmd.cmd_stores_info_sections_v3_create,
        write_capable=True,
    )

    stores_info_sections_v3_update = stores_info_sections_v3_sub.add_parser(
        "update",
        help="Update one Catalog V3 info section",
    )
    stores_info_sections_v3_update.add_argument(
        "--info-section-id",
        required=True,
        dest="info_section_id",
        help="Info section ID",
    )
    stores_info_sections_v3_update.add_argument(
        "--info-section-json",
        dest="info_section_json",
        required=True,
        help="JSON infoSection object, full update body, or @file. Must include the current revision.",
    )
    stores_info_sections_v3_update.set_defaults(
        func=stores_info_sections_v3_cmd.cmd_stores_info_sections_v3_update,
        write_capable=True,
    )

    stores_info_sections_v3_delete = stores_info_sections_v3_sub.add_parser(
        "delete",
        help="Delete one Catalog V3 info section",
    )
    stores_info_sections_v3_delete.add_argument(
        "--info-section-id",
        required=True,
        dest="info_section_id",
        help="Info section ID",
    )
    stores_info_sections_v3_delete.set_defaults(
        func=stores_info_sections_v3_cmd.cmd_stores_info_sections_v3_delete,
        write_capable=True,
    )

    stores_info_sections_v3_bulk_create = stores_info_sections_v3_sub.add_parser(
        "bulk-create",
        help="Create multiple Catalog V3 info sections",
    )
    stores_info_sections_v3_bulk_create.add_argument(
        "--info-sections-json",
        dest="info_sections_json",
        required=True,
        help="JSON infoSections array/body or @file",
    )
    stores_info_sections_v3_bulk_create.set_defaults(
        func=stores_info_sections_v3_cmd.cmd_stores_info_sections_v3_bulk_create,
        write_capable=True,
    )

    stores_info_sections_v3_bulk_delete = stores_info_sections_v3_sub.add_parser(
        "bulk-delete",
        help="Delete multiple Catalog V3 info sections",
    )
    stores_info_sections_v3_bulk_delete.add_argument(
        "--info-section-ids-json",
        dest="info_section_ids_json",
        required=True,
        help="JSON infoSectionIds array/body or @file",
    )
    stores_info_sections_v3_bulk_delete.set_defaults(
        func=stores_info_sections_v3_cmd.cmd_stores_info_sections_v3_bulk_delete,
        write_capable=True,
    )

    stores_info_sections_v3_bulk_update = stores_info_sections_v3_sub.add_parser(
        "bulk-update",
        help="Update multiple Catalog V3 info sections",
    )
    stores_info_sections_v3_bulk_update.add_argument(
        "--info-sections-json",
        dest="info_sections_json",
        required=True,
        help="JSON infoSections array/body or @file. Each info section must include the current revision.",
    )
    stores_info_sections_v3_bulk_update.set_defaults(
        func=stores_info_sections_v3_cmd.cmd_stores_info_sections_v3_bulk_update,
        write_capable=True,
    )

    stores_info_sections_v3_get_or_create = stores_info_sections_v3_sub.add_parser(
        "get-or-create",
        help="Get or create one Catalog V3 info section by id or uniqueName",
    )
    stores_info_sections_v3_get_or_create.add_argument(
        "--info-section-json",
        dest="info_section_json",
        required=True,
        help="JSON infoSection object, full get-or-create body, or @file",
    )
    stores_info_sections_v3_get_or_create.set_defaults(
        func=stores_info_sections_v3_cmd.cmd_stores_info_sections_v3_get_or_create,
        write_capable=True,
    )

    stores_info_sections_v3_bulk_get_or_create = stores_info_sections_v3_sub.add_parser(
        "bulk-get-or-create",
        help="Get or create multiple Catalog V3 info sections by id or uniqueName",
    )
    stores_info_sections_v3_bulk_get_or_create.add_argument(
        "--info-sections-json",
        dest="info_sections_json",
        required=True,
        help="JSON infoSections array/body or @file",
    )
    stores_info_sections_v3_bulk_get_or_create.set_defaults(
        func=stores_info_sections_v3_cmd.cmd_stores_info_sections_v3_bulk_get_or_create,
        write_capable=True,
    )

    customizations_v3 = sub.add_parser("customizations-v3", help="Read and manage Wix Stores Catalog V3 customizations")
    customizations_v3_sub = customizations_v3.add_subparsers(
        dest="customizations_v3_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    customizations_v3_get = customizations_v3_sub.add_parser("get", help="Get one Catalog V3 customization by id")
    customizations_v3_get.add_argument(
        "--customization-id",
        required=True,
        dest="customization_id",
        help="Customization ID",
    )
    customizations_v3_get.set_defaults(func=customizations_v3_cmd.cmd_customizations_v3_get, write_capable=False)

    customizations_v3_query = customizations_v3_sub.add_parser("query", help="Query Catalog V3 customizations")
    customizations_v3_query.add_argument(
        "--query-json",
        dest="query_json",
        default=None,
        help="Optional JSON query object or full official query body",
    )
    customizations_v3_query.set_defaults(func=customizations_v3_cmd.cmd_customizations_v3_query, write_capable=False)

    customizations_v3_create = customizations_v3_sub.add_parser("create", help="Create one Catalog V3 customization")
    customizations_v3_create.add_argument(
        "--customization-json",
        required=True,
        dest="customization_json",
        help="Customization JSON object or @file",
    )
    customizations_v3_create.set_defaults(func=customizations_v3_cmd.cmd_customizations_v3_create, write_capable=True)

    customizations_v3_update = customizations_v3_sub.add_parser("update", help="Update one Catalog V3 customization")
    customizations_v3_update.add_argument(
        "--customization-id",
        required=True,
        dest="customization_id",
        help="Customization ID",
    )
    customizations_v3_update.add_argument(
        "--customization-json",
        required=True,
        dest="customization_json",
        help="Customization JSON object with current revision or @file",
    )
    customizations_v3_update.set_defaults(func=customizations_v3_cmd.cmd_customizations_v3_update, write_capable=True)

    customizations_v3_delete = customizations_v3_sub.add_parser("delete", help="Delete one Catalog V3 customization")
    customizations_v3_delete.add_argument(
        "--customization-id",
        required=True,
        dest="customization_id",
        help="Customization ID",
    )
    customizations_v3_delete.set_defaults(func=customizations_v3_cmd.cmd_customizations_v3_delete, write_capable=True)

    customizations_v3_bulk_create = customizations_v3_sub.add_parser("bulk-create", help="Create multiple Catalog V3 customizations")
    customizations_v3_bulk_create.add_argument(
        "--customizations-json",
        required=True,
        dest="customizations_json",
        help="Customizations array/body JSON or @file",
    )
    customizations_v3_bulk_create.set_defaults(
        func=customizations_v3_cmd.cmd_customizations_v3_bulk_create,
        write_capable=True,
    )

    customizations_v3_bulk_update = customizations_v3_sub.add_parser("bulk-update", help="Update multiple Catalog V3 customizations")
    customizations_v3_bulk_update.add_argument(
        "--customizations-json",
        required=True,
        dest="customizations_json",
        help="Customizations array/body JSON with current revisions or @file",
    )
    customizations_v3_bulk_update.set_defaults(
        func=customizations_v3_cmd.cmd_customizations_v3_bulk_update,
        write_capable=True,
    )

    customizations_v3_add_choices = customizations_v3_sub.add_parser("add-choices", help="Add choices to one Catalog V3 customization")
    customizations_v3_add_choices.add_argument(
        "--customization-id",
        required=True,
        dest="customization_id",
        help="Customization ID",
    )
    customizations_v3_add_choices.add_argument(
        "--choices-json",
        required=True,
        dest="choices_json",
        help="Choices array/body JSON or @file",
    )
    customizations_v3_add_choices.set_defaults(
        func=customizations_v3_cmd.cmd_customizations_v3_add_choices,
        write_capable=True,
    )

    customizations_v3_bulk_add_choices = customizations_v3_sub.add_parser(
        "bulk-add-choices",
        help="Add choices to multiple Catalog V3 customizations",
    )
    customizations_v3_bulk_add_choices.add_argument(
        "--customizations-json",
        required=True,
        dest="customizations_json",
        help="Bulk customization choices body JSON or @file",
    )
    customizations_v3_bulk_add_choices.set_defaults(
        func=customizations_v3_cmd.cmd_customizations_v3_bulk_add_choices,
        write_capable=True,
    )

    customizations_v3_remove_choices = customizations_v3_sub.add_parser(
        "remove-choices",
        help="Remove choices from one Catalog V3 customization",
    )
    customizations_v3_remove_choices.add_argument(
        "--customization-id",
        required=True,
        dest="customization_id",
        help="Customization ID",
    )
    customizations_v3_remove_choices.add_argument(
        "--choices-json",
        required=True,
        dest="choices_json",
        help="Choices array/body JSON or @file",
    )
    customizations_v3_remove_choices.set_defaults(
        func=customizations_v3_cmd.cmd_customizations_v3_remove_choices,
        write_capable=True,
    )

    customizations_v3_set_choices = customizations_v3_sub.add_parser(
        "set-choices",
        help="Replace choices for one Catalog V3 customization",
    )
    customizations_v3_set_choices.add_argument(
        "--customization-id",
        required=True,
        dest="customization_id",
        help="Customization ID",
    )
    customizations_v3_set_choices.add_argument(
        "--choices-json",
        required=True,
        dest="choices_json",
        help="Choices array/body JSON or @file",
    )
    customizations_v3_set_choices.set_defaults(
        func=customizations_v3_cmd.cmd_customizations_v3_set_choices,
        write_capable=True,
    )

    categories = sub.add_parser("categories", help="Read and manage Wix Stores Catalog V3 categories")
    categories_sub = categories.add_subparsers(
        dest="categories_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    categories_get = categories_sub.add_parser("get", help="Get one category by id")
    categories_get.add_argument("--category-id", required=True, dest="category_id", help="Category ID")
    categories_get.add_argument(
        "--tree-reference-json",
        dest="tree_reference_json",
        default=None,
        help="Optional JSON treeReference override or @file",
    )
    categories_get.set_defaults(func=categories_cmd.cmd_categories_get, write_capable=False)

    categories_get_by_slug = categories_sub.add_parser("get-by-slug", help="Get one category by slug")
    categories_get_by_slug.add_argument("--slug", required=True, dest="slug", help="Category slug")
    categories_get_by_slug.add_argument(
        "--tree-reference-json",
        dest="tree_reference_json",
        default=None,
        help="Optional JSON treeReference override or @file",
    )
    categories_get_by_slug.set_defaults(func=categories_cmd.cmd_categories_get_by_slug, write_capable=False)

    categories_query = categories_sub.add_parser("query", help="Query categories")
    categories_query.add_argument(
        "--query-json",
        dest="query_json",
        default=None,
        help="Optional JSON query object or full official query body",
    )
    categories_query.set_defaults(func=categories_cmd.cmd_categories_query, write_capable=False)

    categories_search = categories_sub.add_parser("search", help="Search categories")
    categories_search.add_argument(
        "--search-json",
        dest="search_json",
        default=None,
        help="Optional JSON search object or full official search body",
    )
    categories_search.set_defaults(func=categories_cmd.cmd_categories_search, write_capable=False)

    categories_count = categories_sub.add_parser("count", help="Count categories")
    categories_count.add_argument(
        "--filter-json",
        dest="filter_json",
        default=None,
        help="Optional JSON filter object or full official count body",
    )
    categories_count.set_defaults(func=categories_cmd.cmd_categories_count, write_capable=False)

    categories_create = categories_sub.add_parser("create", help="Create one category")
    categories_create.add_argument(
        "--category-json",
        dest="category_json",
        required=True,
        help="JSON category object, full create body, or @file",
    )
    categories_create.set_defaults(func=categories_cmd.cmd_categories_create, write_capable=True)

    categories_update = categories_sub.add_parser("update", help="Update one category")
    categories_update.add_argument("--category-id", required=True, dest="category_id", help="Category ID")
    categories_update.add_argument(
        "--category-json",
        dest="category_json",
        required=True,
        help="JSON category object with revision, full update body, or @file",
    )
    categories_update.set_defaults(func=categories_cmd.cmd_categories_update, write_capable=True)

    categories_delete = categories_sub.add_parser("delete", help="Delete one category")
    categories_delete.add_argument("--category-id", required=True, dest="category_id", help="Category ID")
    categories_delete.set_defaults(func=categories_cmd.cmd_categories_delete, write_capable=True)

    categories_bulk_update = categories_sub.add_parser("bulk-update", help="Update multiple categories")
    categories_bulk_update.add_argument(
        "--categories-json",
        dest="categories_json",
        required=True,
        help="JSON categories array/body with revisions or @file",
    )
    categories_bulk_update.set_defaults(func=categories_cmd.cmd_categories_bulk_update, write_capable=True)

    categories_update_visibility = categories_sub.add_parser(
        "update-visibility",
        help="Update category visibility",
    )
    categories_update_visibility.add_argument(
        "--request-json",
        dest="request_json",
        required=True,
        help="Official visibility request body JSON or @file",
    )
    categories_update_visibility.set_defaults(
        func=categories_cmd.cmd_categories_update_visibility,
        write_capable=True,
    )

    categories_bulk_show = categories_sub.add_parser("bulk-show", help="Show multiple categories")
    categories_bulk_show.add_argument(
        "--request-json",
        dest="request_json",
        required=True,
        help="Official bulk show request body JSON or @file",
    )
    categories_bulk_show.set_defaults(func=categories_cmd.cmd_categories_bulk_show, write_capable=True)

    categories_bulk_add_items_to_category = categories_sub.add_parser(
        "bulk-add-items-to-category",
        help="Add multiple items to one category",
    )
    categories_bulk_add_items_to_category.add_argument(
        "--category-id",
        required=True,
        dest="category_id",
        help="Category ID",
    )
    categories_bulk_add_items_to_category.add_argument(
        "--request-json",
        dest="request_json",
        required=True,
        help="Official bulk add items request body JSON or @file",
    )
    categories_bulk_add_items_to_category.set_defaults(
        func=categories_cmd.cmd_categories_bulk_add_items_to_category,
        write_capable=True,
    )

    categories_bulk_add_item_to_categories = categories_sub.add_parser(
        "bulk-add-item-to-categories",
        help="Add one item to multiple categories",
    )
    categories_bulk_add_item_to_categories.add_argument(
        "--request-json",
        dest="request_json",
        required=True,
        help="Official bulk add item request body JSON or @file",
    )
    categories_bulk_add_item_to_categories.set_defaults(
        func=categories_cmd.cmd_categories_bulk_add_item_to_categories,
        write_capable=True,
    )

    categories_bulk_remove_items_from_category = categories_sub.add_parser(
        "bulk-remove-items-from-category",
        help="Remove multiple items from one category",
    )
    categories_bulk_remove_items_from_category.add_argument(
        "--category-id",
        required=True,
        dest="category_id",
        help="Category ID",
    )
    categories_bulk_remove_items_from_category.add_argument(
        "--request-json",
        dest="request_json",
        required=True,
        help="Official bulk remove items request body JSON or @file",
    )
    categories_bulk_remove_items_from_category.set_defaults(
        func=categories_cmd.cmd_categories_bulk_remove_items_from_category,
        write_capable=True,
    )

    categories_bulk_remove_item_from_categories = categories_sub.add_parser(
        "bulk-remove-item-from-categories",
        help="Remove one item from multiple categories",
    )
    categories_bulk_remove_item_from_categories.add_argument(
        "--request-json",
        dest="request_json",
        required=True,
        help="Official bulk remove item request body JSON or @file",
    )
    categories_bulk_remove_item_from_categories.set_defaults(
        func=categories_cmd.cmd_categories_bulk_remove_item_from_categories,
        write_capable=True,
    )

    categories_move = categories_sub.add_parser("move", help="Move one category")
    categories_move.add_argument("--category-id", required=True, dest="category_id", help="Category ID")
    categories_move.add_argument(
        "--request-json",
        dest="request_json",
        required=True,
        help="Official move category request body JSON or @file",
    )
    categories_move.set_defaults(func=categories_cmd.cmd_categories_move, write_capable=True)

    categories_set_arranged_items = categories_sub.add_parser(
        "set-arranged-items",
        help="Set arranged items for one category",
    )
    categories_set_arranged_items.add_argument(
        "--category-id",
        required=True,
        dest="category_id",
        help="Category ID",
    )
    categories_set_arranged_items.add_argument(
        "--request-json",
        dest="request_json",
        required=True,
        help="Official set arranged items request body JSON or @file",
    )
    categories_set_arranged_items.set_defaults(
        func=categories_cmd.cmd_categories_set_arranged_items,
        write_capable=True,
    )

    categories_list_trees = categories_sub.add_parser("list-trees", help="List available category trees")
    categories_list_trees.add_argument(
        "--tree-reference-json",
        dest="tree_reference_json",
        default=None,
        help="Optional JSON treeReference override or @file",
    )
    categories_list_trees.set_defaults(func=categories_cmd.cmd_categories_list_trees, write_capable=False)

    categories_get_arranged_items = categories_sub.add_parser(
        "get-arranged-items",
        help="Get arranged items for one category",
    )
    categories_get_arranged_items.add_argument(
        "--category-id",
        required=True,
        dest="category_id",
        help="Category ID",
    )
    categories_get_arranged_items.add_argument(
        "--tree-reference-json",
        dest="tree_reference_json",
        default=None,
        help="Optional JSON treeReference override or @file",
    )
    categories_get_arranged_items.set_defaults(
        func=categories_cmd.cmd_categories_get_arranged_items,
        write_capable=False,
    )

    categories_list_categories_for_item = categories_sub.add_parser(
        "list-categories-for-item",
        help="List categories for one item",
    )
    categories_list_categories_for_item.add_argument(
        "--request-json",
        dest="request_json",
        default=None,
        help="Optional JSON request body or @file",
    )
    categories_list_categories_for_item.set_defaults(
        func=categories_cmd.cmd_categories_list_categories_for_item,
        write_capable=False,
    )

    categories_list_categories_for_items = categories_sub.add_parser(
        "list-categories-for-items",
        help="List categories for multiple items",
    )
    categories_list_categories_for_items.add_argument(
        "--request-json",
        dest="request_json",
        default=None,
        help="Optional JSON request body or @file",
    )
    categories_list_categories_for_items.set_defaults(
        func=categories_cmd.cmd_categories_list_categories_for_items,
        write_capable=False,
    )

    categories_list_items_in_category = categories_sub.add_parser(
        "list-items-in-category",
        help="List items in one category",
    )
    categories_list_items_in_category.add_argument(
        "--category-id",
        required=True,
        dest="category_id",
        help="Category ID",
    )
    categories_list_items_in_category.add_argument(
        "--request-json",
        dest="request_json",
        default=None,
        help="Optional JSON request body or @file",
    )
    categories_list_items_in_category.set_defaults(
        func=categories_cmd.cmd_categories_list_items_in_category,
        write_capable=False,
    )

    stores_inventory_items_v3 = sub.add_parser(
        "stores-inventory-items-v3",
        help="Read and manage Wix Stores Catalog V3 inventory items",
    )
    stores_inventory_items_v3_sub = stores_inventory_items_v3.add_subparsers(
        dest="stores_inventory_items_v3_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    stores_inventory_items_v3_get = stores_inventory_items_v3_sub.add_parser(
        "get",
        help="Get one Catalog V3 inventory item by id",
    )
    stores_inventory_items_v3_get.add_argument(
        "--inventory-item-id",
        required=True,
        dest="inventory_item_id",
        help="Inventory item ID",
    )
    stores_inventory_items_v3_get.set_defaults(
        func=stores_inventory_items_v3_cmd.cmd_stores_inventory_items_v3_get,
        write_capable=False,
    )

    stores_inventory_items_v3_query = stores_inventory_items_v3_sub.add_parser(
        "query",
        help="Query Catalog V3 inventory items",
    )
    stores_inventory_items_v3_query.add_argument(
        "--query-json",
        dest="query_json",
        default=None,
        help="Optional JSON query object or full official query body",
    )
    stores_inventory_items_v3_query.set_defaults(
        func=stores_inventory_items_v3_cmd.cmd_stores_inventory_items_v3_query,
        write_capable=False,
    )

    stores_inventory_items_v3_search = stores_inventory_items_v3_sub.add_parser(
        "search",
        help="Search Catalog V3 inventory items",
    )
    stores_inventory_items_v3_search.add_argument(
        "--search-json",
        dest="search_json",
        default=None,
        help="Optional JSON search object or full official search body",
    )
    stores_inventory_items_v3_search.set_defaults(
        func=stores_inventory_items_v3_cmd.cmd_stores_inventory_items_v3_search,
        write_capable=False,
    )

    stores_inventory_items_v3_create = stores_inventory_items_v3_sub.add_parser(
        "create",
        help="Create one Catalog V3 inventory item",
    )
    stores_inventory_items_v3_create.add_argument(
        "--inventory-item-json",
        dest="inventory_item_json",
        required=True,
        help="JSON inventoryItem object, full create body, or @file",
    )
    stores_inventory_items_v3_create.set_defaults(
        func=stores_inventory_items_v3_cmd.cmd_stores_inventory_items_v3_create,
        write_capable=True,
    )

    stores_inventory_items_v3_update = stores_inventory_items_v3_sub.add_parser(
        "update",
        help="Update one Catalog V3 inventory item",
    )
    stores_inventory_items_v3_update.add_argument(
        "--inventory-item-id",
        required=True,
        dest="inventory_item_id",
        help="Inventory item ID",
    )
    stores_inventory_items_v3_update.add_argument(
        "--inventory-item-json",
        dest="inventory_item_json",
        required=True,
        help="JSON inventoryItem object, full update body, or @file. Must include the current revision.",
    )
    stores_inventory_items_v3_update.set_defaults(
        func=stores_inventory_items_v3_cmd.cmd_stores_inventory_items_v3_update,
        write_capable=True,
    )

    stores_inventory_items_v3_delete = stores_inventory_items_v3_sub.add_parser(
        "delete",
        help="Delete one Catalog V3 inventory item",
    )
    stores_inventory_items_v3_delete.add_argument(
        "--inventory-item-id",
        required=True,
        dest="inventory_item_id",
        help="Inventory item ID",
    )
    stores_inventory_items_v3_delete.set_defaults(
        func=stores_inventory_items_v3_cmd.cmd_stores_inventory_items_v3_delete,
        write_capable=True,
    )

    stores_locations_v3 = sub.add_parser(
        "stores-locations-v3",
        help="Read Wix Stores Catalog V3 inventory locations",
    )
    stores_locations_v3_sub = stores_locations_v3.add_subparsers(
        dest="stores_locations_v3_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    stores_locations_v3_get = stores_locations_v3_sub.add_parser(
        "get",
        help="Get one Stores Catalog V3 location by id",
    )
    stores_locations_v3_get.add_argument(
        "--stores-location-id",
        required=True,
        dest="stores_location_id",
        help="Stores location ID",
    )
    stores_locations_v3_get.set_defaults(
        func=stores_locations_v3_cmd.cmd_stores_locations_v3_get,
        write_capable=False,
    )

    stores_locations_v3_query = stores_locations_v3_sub.add_parser(
        "query",
        help="Query Stores Catalog V3 locations",
    )
    stores_locations_v3_query.add_argument(
        "--query-json",
        dest="query_json",
        default=None,
        help="Optional JSON query object or full official query body",
    )
    stores_locations_v3_query.set_defaults(
        func=stores_locations_v3_cmd.cmd_stores_locations_v3_query,
        write_capable=False,
    )

    catalog_versioning = sub.add_parser(
        "catalog-versioning",
        help="Read the Wix Stores catalog version for the current site",
    )
    catalog_versioning_sub = catalog_versioning.add_subparsers(
        dest="catalog_versioning_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    catalog_versioning_get = catalog_versioning_sub.add_parser(
        "get",
        help="Get the current Wix Stores catalog version",
    )
    catalog_versioning_get.set_defaults(
        func=catalog_versioning_cmd.cmd_catalog_versioning_get,
        write_capable=False,
    )

    order_billing = sub.add_parser("order-billing", help="Preview and process Wix order refunds")
    order_billing_sub = order_billing.add_subparsers(
        dest="order_billing_cmd", required=True, parser_class=_ToolArgumentParser
    )

    order_billing_get_refundability = order_billing_sub.add_parser(
        "get-order-refundability",
        help="Get refundability details for one order",
    )
    order_billing_get_refundability.add_argument(
        "--order-id",
        required=True,
        dest="order_id",
        help="Order ID",
    )
    order_billing_get_refundability.set_defaults(
        func=order_billing_cmd.cmd_order_billing_get_order_refundability,
        write_capable=False,
    )

    order_billing_calculate_refund = order_billing_sub.add_parser(
        "calculate-refund",
        help="Preview refund totals for one order",
    )
    order_billing_calculate_refund.add_argument(
        "--order-id",
        required=True,
        dest="order_id",
        help="Order ID",
    )
    order_billing_calculate_refund.add_argument(
        "--refund-items-json",
        required=True,
        dest="refund_items_json",
        help="JSON object or @file with refundItems",
    )
    order_billing_calculate_refund.set_defaults(
        func=order_billing_cmd.cmd_order_billing_calculate_refund,
        write_capable=False,
    )

    order_billing_refund_payments = order_billing_sub.add_parser(
        "refund-payments",
        help="Refund payments for one order through the reviewed-plan flow",
    )
    order_billing_refund_payments.add_argument(
        "--order-id",
        required=True,
        dest="order_id",
        help="Order ID",
    )
    order_billing_refund_payments.add_argument(
        "--payment-refunds-json",
        required=True,
        dest="payment_refunds_json",
        help="JSON array or @file with paymentRefunds entries",
    )
    order_billing_refund_payments.add_argument(
        "--refund-items-json",
        dest="refund_items_json",
        default=None,
        help="Optional JSON object or @file with refundItems",
    )
    order_billing_refund_payments.add_argument(
        "--side-effects-json",
        dest="side_effects_json",
        default=None,
        help="Optional JSON object or @file with sideEffects such as restock or notifications",
    )
    order_billing_refund_payments.set_defaults(
        func=order_billing_cmd.cmd_order_billing_refund_payments,
        write_capable=True,
    )

    order_billing_authorize_charge = order_billing_sub.add_parser(
        "authorize-charge-with-saved-payment-method",
        help="Authorize one saved-payment-method charge for an order through the reviewed-plan flow",
    )
    order_billing_authorize_charge.add_argument(
        "--order-id",
        required=True,
        dest="order_id",
        help="Order ID",
    )
    order_billing_authorize_charge.add_argument(
        "--amount-json",
        required=True,
        dest="amount_json",
        help='JSON object or @file with amount, for example \'{"amount":"1"}\'',
    )
    order_billing_authorize_charge.add_argument(
        "--currency",
        required=True,
        help="Currency code such as USD",
    )
    order_billing_authorize_charge.add_argument(
        "--delayed-capture-settings-json",
        dest="delayed_capture_settings_json",
        default=None,
        help="Optional JSON object or @file with delayedCaptureSettings",
    )
    order_billing_authorize_charge.set_defaults(
        func=order_billing_cmd.cmd_order_billing_authorize_charge_with_saved_payment_method,
        write_capable=True,
    )

    order_billing_capture_authorized = order_billing_sub.add_parser(
        "capture-authorized-payments",
        help="Capture authorized order payments through the reviewed-plan flow",
    )
    order_billing_capture_authorized.add_argument(
        "--order-id",
        required=True,
        dest="order_id",
        help="Order ID",
    )
    order_billing_capture_authorized.add_argument(
        "--payments-json",
        required=True,
        dest="payments_json",
        help='JSON array or @file with payments entries such as [{"paymentId":"...","amount":{"amount":"1"}}]',
    )
    order_billing_capture_authorized.set_defaults(
        func=order_billing_cmd.cmd_order_billing_capture_authorized_payments,
        write_capable=True,
    )

    order_billing_void_authorized = order_billing_sub.add_parser(
        "void-authorized-payments",
        help="Void authorized order payments through the reviewed-plan flow",
    )
    order_billing_void_authorized.add_argument(
        "--order-id",
        required=True,
        dest="order_id",
        help="Order ID",
    )
    order_billing_void_authorized.add_argument(
        "--payment-ids-json",
        required=True,
        dest="payment_ids_json",
        help='JSON array or @file with payment IDs such as ["payment-1"]',
    )
    order_billing_void_authorized.set_defaults(
        func=order_billing_cmd.cmd_order_billing_void_authorized_payments,
        write_capable=True,
    )

    order_billing_generate_receipts = order_billing_sub.add_parser(
        "generate-receipts",
        help="Generate payment receipts for an order through the reviewed-plan flow",
    )
    order_billing_generate_receipts.add_argument(
        "--order-id",
        required=True,
        dest="order_id",
        help="Order ID",
    )
    order_billing_generate_receipts.add_argument(
        "--payment-ids-json",
        required=True,
        dest="payment_ids_json",
        help='JSON array or @file with payment IDs such as ["payment-1"]',
    )
    order_billing_generate_receipts.set_defaults(
        func=order_billing_cmd.cmd_order_billing_generate_receipts,
        write_capable=True,
    )

    order_billing_redeem_gift_card = order_billing_sub.add_parser(
        "redeem-gift-card",
        help="Redeem one gift card against an order through the reviewed-plan flow",
    )
    order_billing_redeem_gift_card.add_argument(
        "--order-id",
        required=True,
        dest="order_id",
        help="Order ID",
    )
    order_billing_redeem_gift_card.add_argument(
        "--gift-card-code",
        required=True,
        dest="gift_card_code",
        help="Gift card code",
    )
    order_billing_redeem_gift_card.add_argument(
        "--amount-json",
        required=True,
        dest="amount_json",
        help='JSON object or @file with amount, for example \'{"amount":"20"}\'',
    )
    order_billing_redeem_gift_card.add_argument(
        "--currency",
        required=True,
        help="Currency code such as USD",
    )
    order_billing_redeem_gift_card.set_defaults(
        func=order_billing_cmd.cmd_order_billing_redeem_gift_card,
        write_capable=True,
    )

    coupons = sub.add_parser("coupons", help="Read and manage Wix coupons")
    coupons_sub = coupons.add_subparsers(dest="coupons_cmd", required=True, parser_class=_ToolArgumentParser)

    coupons_get = coupons_sub.add_parser("get", help="Get one coupon by id")
    coupons_get.add_argument("--coupon-id", required=True, dest="coupon_id", help="Coupon ID")
    coupons_get.set_defaults(func=coupons_cmd.cmd_coupons_get, write_capable=False)

    coupons_query = coupons_sub.add_parser("query", help="Query coupons")
    coupons_query.add_argument("--query-json", dest="query_json", default=None, help="Optional JSON query body")
    coupons_query.set_defaults(func=coupons_cmd.cmd_coupons_query, write_capable=False)

    coupons_create = coupons_sub.add_parser("create", help="Create one coupon")
    coupons_create.add_argument(
        "--coupon-json",
        dest="coupon_json",
        required=True,
        help="JSON object or @file with the official coupon body",
    )
    coupons_create.set_defaults(func=coupons_cmd.cmd_coupons_create, write_capable=True)

    coupons_update = coupons_sub.add_parser("update", help="Update one coupon")
    coupons_update.add_argument("--coupon-id", required=True, dest="coupon_id", help="Coupon ID")
    coupons_update.add_argument(
        "--coupon-json",
        dest="coupon_json",
        required=True,
        help="JSON object or @file with the official coupon patch body",
    )
    coupons_update.set_defaults(func=coupons_cmd.cmd_coupons_update, write_capable=True)

    coupons_delete = coupons_sub.add_parser("delete", help="Delete one coupon")
    coupons_delete.add_argument("--coupon-id", required=True, dest="coupon_id", help="Coupon ID")
    coupons_delete.set_defaults(func=coupons_cmd.cmd_coupons_delete, write_capable=True)

    coupons_bulk_create = coupons_sub.add_parser("bulk-create", help="Create multiple coupons")
    coupons_bulk_create.add_argument(
        "--coupons-json",
        dest="coupons_json",
        required=True,
        help="JSON array, JSON object, or @file with the official bulk-create body",
    )
    coupons_bulk_create.set_defaults(func=coupons_cmd.cmd_coupons_bulk_create, write_capable=True)

    coupons_bulk_delete = coupons_sub.add_parser("bulk-delete", help="Delete multiple coupons")
    coupons_bulk_delete.add_argument(
        "--coupon-ids-json",
        dest="coupon_ids_json",
        required=True,
        help="JSON array, JSON object, or @file with coupon ids for bulk delete",
    )
    coupons_bulk_delete.set_defaults(func=coupons_cmd.cmd_coupons_bulk_delete, write_capable=True)

    benefit_items = sub.add_parser("benefit-items", help="Read and manage Wix benefit items")
    benefit_items_sub = benefit_items.add_subparsers(
        dest="benefit_items_cmd", required=True, parser_class=_ToolArgumentParser
    )

    benefit_items_get = benefit_items_sub.add_parser("get", help="Get one benefit item by id")
    benefit_items_get.add_argument("--item-id", required=True, dest="item_id", help="Benefit item ID")
    benefit_items_get.set_defaults(func=benefit_items_cmd.cmd_benefit_items_get, write_capable=False)

    benefit_items_list = benefit_items_sub.add_parser("list", help="List benefit items")
    benefit_items_list.set_defaults(func=benefit_items_cmd.cmd_benefit_items_list, write_capable=False)

    benefit_items_query = benefit_items_sub.add_parser("query", help="Query benefit items")
    benefit_items_query.add_argument("--query-json", dest="query_json", default=None, help="Optional JSON query body")
    benefit_items_query.set_defaults(func=benefit_items_cmd.cmd_benefit_items_query, write_capable=False)

    benefit_items_count = benefit_items_sub.add_parser("count", help="Count benefit items")
    benefit_items_count.add_argument(
        "--filter-json",
        dest="filter_json",
        default=None,
        help="Optional JSON filter body or full official count body",
    )
    benefit_items_count.set_defaults(func=benefit_items_cmd.cmd_benefit_items_count, write_capable=False)

    benefit_items_create = benefit_items_sub.add_parser("create", help="Create one benefit item")
    benefit_items_create.add_argument(
        "--item-json",
        dest="item_json",
        required=True,
        help="Item JSON object, full create body, or @file",
    )
    benefit_items_create.set_defaults(func=benefit_items_cmd.cmd_benefit_items_create, write_capable=True)

    benefit_items_update = benefit_items_sub.add_parser("update", help="Update one benefit item")
    benefit_items_update.add_argument("--item-id", required=True, dest="item_id", help="Benefit item ID")
    benefit_items_update.add_argument(
        "--item-json",
        dest="item_json",
        required=True,
        help="Item patch JSON object, full update body, or @file",
    )
    benefit_items_update.set_defaults(func=benefit_items_cmd.cmd_benefit_items_update, write_capable=True)

    benefit_items_delete = benefit_items_sub.add_parser("delete", help="Delete one benefit item")
    benefit_items_delete.add_argument("--item-id", required=True, dest="item_id", help="Benefit item ID")
    benefit_items_delete.set_defaults(func=benefit_items_cmd.cmd_benefit_items_delete, write_capable=True)

    benefit_items_bulk_create = benefit_items_sub.add_parser("bulk-create", help="Create multiple benefit items")
    benefit_items_bulk_create.add_argument(
        "--items-json",
        dest="items_json",
        required=True,
        help="JSON array, JSON object, or @file with the official bulk-create body",
    )
    benefit_items_bulk_create.set_defaults(func=benefit_items_cmd.cmd_benefit_items_bulk_create, write_capable=True)

    benefit_items_bulk_update = benefit_items_sub.add_parser("bulk-update", help="Update multiple benefit items")
    benefit_items_bulk_update.add_argument(
        "--items-json",
        dest="items_json",
        required=True,
        help="JSON array, JSON object, or @file with the official bulk-update body",
    )
    benefit_items_bulk_update.set_defaults(func=benefit_items_cmd.cmd_benefit_items_bulk_update, write_capable=True)

    benefit_items_bulk_delete = benefit_items_sub.add_parser("bulk-delete", help="Delete multiple benefit items")
    benefit_items_bulk_delete.add_argument(
        "--item-ids-json",
        dest="item_ids_json",
        required=True,
        help="JSON array, JSON object, or @file with item ids for bulk delete",
    )
    benefit_items_bulk_delete.set_defaults(func=benefit_items_cmd.cmd_benefit_items_bulk_delete, write_capable=True)

    benefit_items_bulk_delete_by_filter = benefit_items_sub.add_parser(
        "bulk-delete-by-filter", help="Delete benefit items by filter"
    )
    benefit_items_bulk_delete_by_filter.add_argument(
        "--filter-json",
        dest="filter_json",
        required=True,
        help="JSON filter object, full official body, or @file for delete-by-filter",
    )
    benefit_items_bulk_delete_by_filter.set_defaults(
        func=benefit_items_cmd.cmd_benefit_items_bulk_delete_by_filter,
        write_capable=True,
    )

    balances = sub.add_parser("balances", help="Read and manage Wix benefit balances")
    balances_sub = balances.add_subparsers(dest="balances_cmd", required=True, parser_class=_ToolArgumentParser)

    balances_get = balances_sub.add_parser("get", help="Get one balance by pool id")
    balances_get.add_argument("--pool-id", required=True, dest="pool_id", help="Pool ID")
    balances_get.set_defaults(func=balances_cmd.cmd_balances_get, write_capable=False)

    balances_list = balances_sub.add_parser("list", help="List balances")
    balances_list.set_defaults(func=balances_cmd.cmd_balances_list, write_capable=False)

    balances_query = balances_sub.add_parser("query", help="Query balances")
    balances_query.add_argument("--query-json", dest="query_json", default=None, help="Optional JSON query body")
    balances_query.set_defaults(func=balances_cmd.cmd_balances_query, write_capable=False)

    balances_change = balances_sub.add_parser("change", help="Change one balance by pool id")
    balances_change.add_argument("--pool-id", required=True, dest="pool_id", help="Pool ID")
    balances_change.add_argument(
        "--change-json",
        dest="change_json",
        required=True,
        help="JSON object or @file with the balance change payload",
    )
    balances_change.set_defaults(func=balances_cmd.cmd_balances_change, write_capable=True)

    balances_revert_change = balances_sub.add_parser(
        "revert-change",
        help="Revert one prior balance change transaction",
    )
    balances_revert_change.add_argument(
        "--transaction-id",
        required=True,
        dest="transaction_id",
        help="Balance change transaction ID",
    )
    balances_revert_change.set_defaults(func=balances_cmd.cmd_balances_revert_change, write_capable=True)

    gift_cards = sub.add_parser("gift-cards", help="Read and manage Wix gift cards")
    gift_cards_sub = gift_cards.add_subparsers(dest="gift_cards_cmd", required=True, parser_class=_ToolArgumentParser)

    gift_cards_get = gift_cards_sub.add_parser("get", help="Get one gift card by id")
    gift_cards_get.add_argument("--gift-card-id", required=True, dest="gift_card_id", help="Gift card ID")
    gift_cards_get.set_defaults(func=gift_cards_cmd.cmd_gift_cards_get, write_capable=False)

    gift_cards_query = gift_cards_sub.add_parser("query", help="Query gift cards")
    gift_cards_query.add_argument("--query-json", dest="query_json", default=None, help="Optional JSON query body")
    gift_cards_query.set_defaults(func=gift_cards_cmd.cmd_gift_cards_query, write_capable=False)

    gift_cards_search = gift_cards_sub.add_parser("search", help="Search gift cards")
    gift_cards_search.add_argument("--search-json", dest="search_json", default=None, help="Optional JSON search body")
    gift_cards_search.set_defaults(func=gift_cards_cmd.cmd_gift_cards_search, write_capable=False)

    gift_cards_count = gift_cards_sub.add_parser("count", help="Count gift cards")
    gift_cards_count.add_argument("--filter-json", dest="filter_json", default=None, help="Optional JSON filter body")
    gift_cards_count.set_defaults(func=gift_cards_cmd.cmd_gift_cards_count, write_capable=False)

    gift_cards_create = gift_cards_sub.add_parser("create", help="Create one gift card")
    gift_cards_create.add_argument(
        "--gift-card-json",
        dest="gift_card_json",
        required=True,
        help="Gift card JSON object or full create request JSON",
    )
    gift_cards_create.set_defaults(func=gift_cards_cmd.cmd_gift_cards_create, write_capable=True)

    gift_cards_disable = gift_cards_sub.add_parser("disable", help="Disable one gift card")
    gift_cards_disable.add_argument("--gift-card-id", required=True, dest="gift_card_id", help="Gift card ID")
    gift_cards_disable.set_defaults(func=gift_cards_cmd.cmd_gift_cards_disable, write_capable=True)

    gift_cards_send_email = gift_cards_sub.add_parser("send-email", help="Send one gift card email")
    gift_cards_send_email.add_argument("--gift-card-id", required=True, dest="gift_card_id", help="Gift card ID")
    gift_cards_send_email.add_argument(
        "--recipient-email",
        dest="recipient_email",
        default=None,
        help="Optional recipient email override for delivery",
    )
    gift_cards_send_email.set_defaults(func=gift_cards_cmd.cmd_gift_cards_send_email, write_capable=True)

    donation_campaigns = sub.add_parser("donation-campaigns", help="Read and manage Wix donation campaigns")
    donation_campaigns_sub = donation_campaigns.add_subparsers(
        dest="donation_campaigns_cmd", required=True, parser_class=_ToolArgumentParser
    )

    donation_campaigns_get = donation_campaigns_sub.add_parser("get", help="Get one donation campaign by id")
    donation_campaigns_get.add_argument(
        "--donation-campaign-id",
        required=True,
        dest="donation_campaign_id",
        help="Donation campaign ID",
    )
    donation_campaigns_get.set_defaults(
        func=donation_campaigns_cmd.cmd_donation_campaigns_get,
        write_capable=False,
    )

    donation_campaigns_get_metrics = donation_campaigns_sub.add_parser(
        "get-metrics",
        help="Get metrics for one donation campaign",
    )
    donation_campaigns_get_metrics.add_argument(
        "--donation-campaign-id",
        required=True,
        dest="donation_campaign_id",
        help="Donation campaign ID",
    )
    donation_campaigns_get_metrics.set_defaults(
        func=donation_campaigns_cmd.cmd_donation_campaigns_get_metrics,
        write_capable=False,
    )

    donation_campaigns_query = donation_campaigns_sub.add_parser("query", help="Query donation campaigns")
    donation_campaigns_query.add_argument(
        "--query-json",
        dest="query_json",
        default=None,
        help="Optional JSON query body",
    )
    donation_campaigns_query.set_defaults(
        func=donation_campaigns_cmd.cmd_donation_campaigns_query,
        write_capable=False,
    )

    donation_campaigns_create = donation_campaigns_sub.add_parser("create", help="Create one donation campaign")
    donation_campaigns_create.add_argument(
        "--donation-campaign-json",
        required=True,
        dest="donation_campaign_json",
        help="Donation campaign JSON object or full create request JSON",
    )
    donation_campaigns_create.set_defaults(
        func=donation_campaigns_cmd.cmd_donation_campaigns_create,
        write_capable=True,
    )

    donation_campaigns_update = donation_campaigns_sub.add_parser("update", help="Update one donation campaign")
    donation_campaigns_update.add_argument(
        "--donation-campaign-id",
        required=True,
        dest="donation_campaign_id",
        help="Donation campaign ID",
    )
    donation_campaigns_update.add_argument(
        "--donation-campaign-json",
        required=True,
        dest="donation_campaign_json",
        help="Donation campaign JSON object or full update request JSON",
    )
    donation_campaigns_update.set_defaults(
        func=donation_campaigns_cmd.cmd_donation_campaigns_update,
        write_capable=True,
    )

    donation_campaigns_bulk_create = donation_campaigns_sub.add_parser(
        "bulk-create",
        help="Create multiple donation campaigns",
    )
    donation_campaigns_bulk_create.add_argument(
        "--donation-campaigns-json",
        required=True,
        dest="donation_campaigns_json",
        help="Donation campaigns JSON array/object or @file",
    )
    donation_campaigns_bulk_create.set_defaults(
        func=donation_campaigns_cmd.cmd_donation_campaigns_bulk_create,
        write_capable=True,
    )

    donation_campaigns_bulk_update = donation_campaigns_sub.add_parser(
        "bulk-update",
        help="Update multiple donation campaigns",
    )
    donation_campaigns_bulk_update.add_argument(
        "--donation-campaigns-json",
        required=True,
        dest="donation_campaigns_json",
        help="Donation campaigns JSON array/object or @file",
    )
    donation_campaigns_bulk_update.set_defaults(
        func=donation_campaigns_cmd.cmd_donation_campaigns_bulk_update,
        write_capable=True,
    )

    donation_campaigns_bulk_update_tags = donation_campaigns_sub.add_parser(
        "bulk-update-tags",
        help="Update tags for specific donation campaigns",
    )
    donation_campaigns_bulk_update_tags.add_argument(
        "--update-tags-json",
        required=True,
        dest="update_tags_json",
        help="Donation campaign tag update JSON object or @file",
    )
    donation_campaigns_bulk_update_tags.set_defaults(
        func=donation_campaigns_cmd.cmd_donation_campaigns_bulk_update_tags,
        write_capable=True,
    )

    donation_campaigns_bulk_update_tags_by_filter = donation_campaigns_sub.add_parser(
        "bulk-update-tags-by-filter",
        help="Update tags for donation campaigns selected by filter",
    )
    donation_campaigns_bulk_update_tags_by_filter.add_argument(
        "--update-tags-json",
        required=True,
        dest="update_tags_json",
        help="Donation campaign filtered tag update JSON object or @file",
    )
    donation_campaigns_bulk_update_tags_by_filter.set_defaults(
        func=donation_campaigns_cmd.cmd_donation_campaigns_bulk_update_tags_by_filter,
        write_capable=True,
    )

    pricing_plans = sub.add_parser("pricing-plans", help="Read and manage Wix pricing plans")
    pricing_plans_sub = pricing_plans.add_subparsers(
        dest="pricing_plans_cmd", required=True, parser_class=_ToolArgumentParser
    )

    pricing_plans_get = pricing_plans_sub.add_parser("get", help="Get one pricing plan by id")
    pricing_plans_get.add_argument("--plan-id", required=True, dest="plan_id", help="Pricing plan ID")
    pricing_plans_get.set_defaults(func=pricing_plans_cmd.cmd_pricing_plans_get, write_capable=False)

    pricing_plans_query = pricing_plans_sub.add_parser("query", help="Query pricing plans")
    pricing_plans_query.add_argument("--query-json", dest="query_json", default=None, help="Optional JSON query body")
    pricing_plans_query.set_defaults(func=pricing_plans_cmd.cmd_pricing_plans_query, write_capable=False)

    pricing_plans_search = pricing_plans_sub.add_parser("search", help="Search pricing plans")
    pricing_plans_search.add_argument("--search-json", dest="search_json", default=None, help="Optional JSON search body")
    pricing_plans_search.set_defaults(func=pricing_plans_cmd.cmd_pricing_plans_search, write_capable=False)

    pricing_plans_count = pricing_plans_sub.add_parser("count", help="Count pricing plans")
    pricing_plans_count.add_argument(
        "--filter-json",
        dest="filter_json",
        default=None,
        help="Optional JSON filter object or full count body",
    )
    pricing_plans_count.set_defaults(func=pricing_plans_cmd.cmd_pricing_plans_count, write_capable=False)

    pricing_plans_create = pricing_plans_sub.add_parser("create", help="Create one pricing plan")
    pricing_plans_create.add_argument(
        "--pricing-plan-json",
        dest="pricing_plan_json",
        required=True,
        help="JSON object or @file with the official pricing plan body",
    )
    pricing_plans_create.set_defaults(func=pricing_plans_cmd.cmd_pricing_plans_create, write_capable=True)

    pricing_plans_update = pricing_plans_sub.add_parser("update", help="Update one pricing plan")
    pricing_plans_update.add_argument("--plan-id", required=True, dest="plan_id", help="Pricing plan ID")
    pricing_plans_update.add_argument(
        "--pricing-plan-json",
        dest="pricing_plan_json",
        required=True,
        help="JSON object or @file with the official pricing plan patch body",
    )
    pricing_plans_update.set_defaults(func=pricing_plans_cmd.cmd_pricing_plans_update, write_capable=True)

    pricing_plans_delete = pricing_plans_sub.add_parser("delete", help="Delete one pricing plan")
    pricing_plans_delete.add_argument("--plan-id", required=True, dest="plan_id", help="Pricing plan ID")
    pricing_plans_delete.set_defaults(func=pricing_plans_cmd.cmd_pricing_plans_delete, write_capable=True)

    pricing_plans_bulk_update = pricing_plans_sub.add_parser(
        "bulk-update",
        help="Bulk update up to 100 pricing plans in one reviewed-plan request",
    )
    pricing_plans_bulk_update.add_argument(
        "--bulk-update-json",
        dest="bulk_update_json",
        required=True,
        help="JSON object or @file with the official bulk update body or a raw plans array",
    )
    pricing_plans_bulk_update.set_defaults(func=pricing_plans_cmd.cmd_pricing_plans_bulk_update, write_capable=True)

    market_listing = sub.add_parser("market-listing", help="Read-only Wix App Market listing search")
    market_listing_sub = market_listing.add_subparsers(dest="market_listing_cmd", required=True, parser_class=_ToolArgumentParser)
    market_listing_search = market_listing_sub.add_parser(
        "search",
        help="Search published app listings by keyword or app name",
    )
    market_listing_search.add_argument("--search-term", required=True, dest="search_term", help="Keyword or app name")
    market_listing_search.add_argument("--language-code", default=None, dest="language_code", help="Optional language code")
    market_listing_search.add_argument("--limit", type=int, default=None, help="Max results per page, up to 50")
    market_listing_search.set_defaults(func=market_listing_cmd.cmd_market_listing_search, write_capable=False)

    editor_deep_link = sub.add_parser("editor-deep-link", help="Generate editor deep links for legacy custom elements")
    editor_deep_link_sub = editor_deep_link.add_subparsers(
        dest="editor_deep_link_cmd", required=True, parser_class=_ToolArgumentParser
    )
    editor_deep_link_create = editor_deep_link_sub.add_parser(
        "create",
        help="Create an editor deep link",
    )
    editor_deep_link_create.add_argument(
        "--custom-params-json",
        dest="custom_params_json",
        default=None,
        help="Optional JSON object of custom parameter key/value pairs",
    )
    editor_deep_link_create.set_defaults(func=editor_deep_link_cmd.cmd_editor_deep_link_create, write_capable=False)

    events_settings = sub.add_parser("events-settings", help="Read and manage Wix Events settings")
    events_settings_sub = events_settings.add_subparsers(
        dest="events_settings_cmd", required=True, parser_class=_ToolArgumentParser
    )
    events_settings_get = events_settings_sub.add_parser("get", help="Get Wix Events settings")
    events_settings_get.set_defaults(func=events_settings_cmd.cmd_events_settings_get, write_capable=False)
    events_settings_update = events_settings_sub.add_parser("update", help="Update Wix Events settings")
    events_settings_update.add_argument("--events-settings-id", required=True, help="Events Settings ID")
    events_settings_update.add_argument("--settings-json", required=True, help="JSON update body or @file")
    events_settings_update.set_defaults(func=events_settings_cmd.cmd_events_settings_update, write_capable=True)

    events_v3 = sub.add_parser("events-v3", help="Read and manage Wix Events V3 events")
    events_v3_sub = events_v3.add_subparsers(dest="events_v3_cmd", required=True, parser_class=_ToolArgumentParser)
    events_v3_create = events_v3_sub.add_parser("create", help="Create one event")
    events_v3_create.add_argument("--event-json", required=True, help="JSON create body or @file")
    events_v3_create.set_defaults(func=events_v3_cmd.cmd_events_v3_create, write_capable=True)
    events_v3_get = events_v3_sub.add_parser("get", help="Get one event")
    events_v3_get.add_argument("--event-id", required=True, help="Event ID")
    events_v3_get.set_defaults(func=events_v3_cmd.cmd_events_v3_get, write_capable=False)
    events_v3_update = events_v3_sub.add_parser("update", help="Update one event")
    events_v3_update.add_argument("--event-id", required=True, help="Event ID")
    events_v3_update.add_argument("--event-json", required=True, help="JSON update body or @file")
    events_v3_update.set_defaults(func=events_v3_cmd.cmd_events_v3_update, write_capable=True)
    events_v3_delete = events_v3_sub.add_parser("delete", help="Delete one event")
    events_v3_delete.add_argument("--event-id", required=True, help="Event ID")
    events_v3_delete.set_defaults(func=events_v3_cmd.cmd_events_v3_delete, write_capable=True)
    events_v3_query = events_v3_sub.add_parser("query", help="Query events")
    events_v3_query.add_argument("--query-json", required=True, help="JSON query body or @file")
    events_v3_query.set_defaults(func=events_v3_cmd.cmd_events_v3_query, write_capable=False)
    events_v3_bulk_cancel = events_v3_sub.add_parser("bulk-cancel-by-filter", help="Cancel events by filter")
    events_v3_bulk_cancel.add_argument("--filter-json", required=True, help="JSON filter body or @file")
    events_v3_bulk_cancel.set_defaults(func=events_v3_cmd.cmd_events_v3_bulk_cancel_by_filter, write_capable=True)
    events_v3_bulk_delete = events_v3_sub.add_parser("bulk-delete-by-filter", help="Delete events by filter")
    events_v3_bulk_delete.add_argument("--filter-json", required=True, help="JSON filter body or @file")
    events_v3_bulk_delete.set_defaults(func=events_v3_cmd.cmd_events_v3_bulk_delete_by_filter, write_capable=True)
    events_v3_cancel = events_v3_sub.add_parser("cancel", help="Cancel one event")
    events_v3_cancel.add_argument("--event-id", required=True, help="Event ID")
    events_v3_cancel.add_argument("--request-json", default="{}", help="Optional JSON cancel body or @file")
    events_v3_cancel.set_defaults(func=events_v3_cmd.cmd_events_v3_cancel, write_capable=True)
    events_v3_clone = events_v3_sub.add_parser("clone", help="Clone one event")
    events_v3_clone.add_argument("--event-id", required=True, help="Event ID")
    events_v3_clone.add_argument("--request-json", default="{}", help="Optional JSON clone body or @file")
    events_v3_clone.set_defaults(func=events_v3_cmd.cmd_events_v3_clone, write_capable=True)
    events_v3_count = events_v3_sub.add_parser("count-by-status", help="Count events by status")
    events_v3_count.add_argument("--query-json", default="{}", help="Optional JSON query body or @file")
    events_v3_count.set_defaults(func=events_v3_cmd.cmd_events_v3_count_by_status, write_capable=False)
    events_v3_get_by_slug = events_v3_sub.add_parser("get-by-slug", help="Get one event by slug")
    events_v3_get_by_slug.add_argument("--slug", required=True, help="Event slug")
    events_v3_get_by_slug.set_defaults(func=events_v3_cmd.cmd_events_v3_get_by_slug, write_capable=False)
    events_v3_list_by_category = events_v3_sub.add_parser("list-by-category", help="List events in one category")
    events_v3_list_by_category.add_argument("--category-id", required=True, help="Event category ID")
    events_v3_list_by_category.set_defaults(func=events_v3_cmd.cmd_events_v3_list_by_category, write_capable=False)
    events_v3_publish_draft = events_v3_sub.add_parser("publish-draft", help="Publish one draft event")
    events_v3_publish_draft.add_argument("--event-id", required=True, help="Event ID")
    events_v3_publish_draft.add_argument("--request-json", default="{}", help="Optional JSON publish body or @file")
    events_v3_publish_draft.set_defaults(func=events_v3_cmd.cmd_events_v3_publish_draft, write_capable=True)

    events_ticket_definitions_v3 = sub.add_parser(
        "events-ticket-definitions-v3",
        help="Read and manage Wix Events ticket definitions",
    )
    events_ticket_definitions_v3_sub = events_ticket_definitions_v3.add_subparsers(
        dest="events_ticket_definitions_v3_cmd", required=True, parser_class=_ToolArgumentParser
    )
    events_ticket_definitions_v3_create = events_ticket_definitions_v3_sub.add_parser("create", help="Create one ticket definition")
    events_ticket_definitions_v3_create.add_argument(
        "--ticket-definition-json",
        dest="ticket_definition_json",
        required=True,
        help="JSON ticketDefinition body or @file",
    )
    events_ticket_definitions_v3_create.set_defaults(
        func=events_ticket_definitions_v3_cmd.cmd_events_ticket_definitions_v3_create,
        write_capable=True,
    )

    events_ticket_definitions_v3_get = events_ticket_definitions_v3_sub.add_parser("get", help="Get one ticket definition")
    events_ticket_definitions_v3_get.add_argument("--ticket-definition-id", required=True, dest="ticket_definition_id", help="Ticket definition ID")
    events_ticket_definitions_v3_get.set_defaults(func=events_ticket_definitions_v3_cmd.cmd_events_ticket_definitions_v3_get, write_capable=False)

    events_ticket_definitions_v3_update = events_ticket_definitions_v3_sub.add_parser("update", help="Update one ticket definition")
    events_ticket_definitions_v3_update.add_argument(
        "--ticket-definition-id",
        required=True,
        dest="ticket_definition_id",
        help="Ticket definition ID",
    )
    events_ticket_definitions_v3_update.add_argument(
        "--ticket-definition-json",
        required=True,
        dest="ticket_definition_json",
        help="JSON ticketDefinition body or @file",
    )
    events_ticket_definitions_v3_update.set_defaults(
        func=events_ticket_definitions_v3_cmd.cmd_events_ticket_definitions_v3_update,
        write_capable=True,
    )

    events_ticket_definitions_v3_delete = events_ticket_definitions_v3_sub.add_parser("delete", help="Delete one ticket definition")
    events_ticket_definitions_v3_delete.add_argument(
        "--ticket-definition-id",
        required=True,
        dest="ticket_definition_id",
        help="Ticket definition ID",
    )
    events_ticket_definitions_v3_delete.set_defaults(
        func=events_ticket_definitions_v3_cmd.cmd_events_ticket_definitions_v3_delete,
        write_capable=True,
    )

    events_ticket_definitions_v3_query = events_ticket_definitions_v3_sub.add_parser("query", help="Query ticket definitions")
    events_ticket_definitions_v3_query.add_argument(
        "--query-json",
        dest="query_json",
        default="{}",
        help="Optional JSON query body or @file",
    )
    events_ticket_definitions_v3_query.set_defaults(func=events_ticket_definitions_v3_cmd.cmd_events_ticket_definitions_v3_query, write_capable=False)

    events_ticket_definitions_v3_bulk_delete_by_filter = events_ticket_definitions_v3_sub.add_parser(
        "bulk-delete-by-filter",
        help="Delete ticket definitions by filter",
    )
    events_ticket_definitions_v3_bulk_delete_by_filter.add_argument(
        "--filter-json",
        dest="filter_json",
        required=True,
        help="JSON filter body or @file",
    )
    events_ticket_definitions_v3_bulk_delete_by_filter.set_defaults(
        func=events_ticket_definitions_v3_cmd.cmd_events_ticket_definitions_v3_bulk_delete_by_filter,
        write_capable=True,
    )

    events_ticket_definitions_v3_change_currency = events_ticket_definitions_v3_sub.add_parser(
        "change-currency",
        help="Change ticket definition currency",
    )
    events_ticket_definitions_v3_change_currency.add_argument(
        "--request-json",
        required=True,
        dest="request_json",
        help="JSON currency change request or @file",
    )
    events_ticket_definitions_v3_change_currency.set_defaults(
        func=events_ticket_definitions_v3_cmd.cmd_events_ticket_definitions_v3_change_currency,
        write_capable=True,
    )

    events_ticket_definitions_v3_count = events_ticket_definitions_v3_sub.add_parser("count", help="Count ticket definitions")
    events_ticket_definitions_v3_count.add_argument(
        "--filter-json",
        dest="filter_json",
        default="{}",
        help="Optional JSON filter body or @file",
    )
    events_ticket_definitions_v3_count.set_defaults(func=events_ticket_definitions_v3_cmd.cmd_events_ticket_definitions_v3_count, write_capable=False)

    events_ticket_definitions_v3_reorder = events_ticket_definitions_v3_sub.add_parser("reorder", help="Reorder ticket definitions")
    events_ticket_definitions_v3_reorder.add_argument(
        "--request-json",
        required=True,
        dest="request_json",
        help="JSON reorder request or @file",
    )
    events_ticket_definitions_v3_reorder.set_defaults(
        func=events_ticket_definitions_v3_cmd.cmd_events_ticket_definitions_v3_reorder,
        write_capable=True,
    )

    events_categories = sub.add_parser("events-categories", help="Read and manage Wix Events categories")
    events_categories_sub = events_categories.add_subparsers(
        dest="events_categories_cmd", required=True, parser_class=_ToolArgumentParser
    )
    events_categories_create = events_categories_sub.add_parser("create", help="Create one event category")
    events_categories_create.add_argument("--category-json", required=True, dest="category_json", help="JSON category body or @file")
    events_categories_create.set_defaults(func=events_categories_cmd.cmd_events_categories_create, write_capable=True)

    events_categories_bulk_create = events_categories_sub.add_parser("bulk-create", help="Create event categories in bulk")
    events_categories_bulk_create.add_argument("--categories-json", required=True, dest="categories_json", help="JSON bulk create body or @file")
    events_categories_bulk_create.set_defaults(func=events_categories_cmd.cmd_events_categories_bulk_create, write_capable=True)

    events_categories_update = events_categories_sub.add_parser("update", help="Update one event category")
    events_categories_update.add_argument("--category-id", required=True, dest="category_id", help="Event category ID")
    events_categories_update.add_argument("--category-json", required=True, dest="category_json", help="JSON category body or @file")
    events_categories_update.set_defaults(func=events_categories_cmd.cmd_events_categories_update, write_capable=True)

    events_categories_delete = events_categories_sub.add_parser("delete", help="Delete one event category")
    events_categories_delete.add_argument("--category-id", required=True, dest="category_id", help="Event category ID")
    events_categories_delete.set_defaults(func=events_categories_cmd.cmd_events_categories_delete, write_capable=True)

    events_categories_query = events_categories_sub.add_parser("query", help="Query event categories")
    events_categories_query.add_argument("--query-json", default="{}", dest="query_json", help="Optional JSON query body or @file")
    events_categories_query.set_defaults(func=events_categories_cmd.cmd_events_categories_query, write_capable=False)

    events_categories_assign_events = events_categories_sub.add_parser("assign-events", help="Assign events to one category")
    events_categories_assign_events.add_argument("--category-id", required=True, dest="category_id", help="Event category ID")
    events_categories_assign_events.add_argument("--events-json", required=True, dest="events_json", help="JSON assign events body or @file")
    events_categories_assign_events.set_defaults(func=events_categories_cmd.cmd_events_categories_assign_events, write_capable=True)

    events_categories_unassign_events = events_categories_sub.add_parser("unassign-events", help="Unassign events from one category")
    events_categories_unassign_events.add_argument("--category-id", required=True, dest="category_id", help="Event category ID")
    events_categories_unassign_events.add_argument("--event-ids", required=True, dest="event_ids", help="Comma-separated event IDs")
    events_categories_unassign_events.set_defaults(func=events_categories_cmd.cmd_events_categories_unassign_events, write_capable=True)

    events_categories_bulk_assign_events = events_categories_sub.add_parser("bulk-assign-events", help="Assign events to categories in bulk")
    events_categories_bulk_assign_events.add_argument("--request-json", required=True, dest="request_json", help="JSON bulk assign request or @file")
    events_categories_bulk_assign_events.set_defaults(func=events_categories_cmd.cmd_events_categories_bulk_assign_events, write_capable=True)

    events_categories_bulk_unassign_events = events_categories_sub.add_parser(
        "bulk-unassign-events",
        help="Unassign events from categories in bulk",
    )
    events_categories_bulk_unassign_events.add_argument("--category-ids", required=True, dest="category_ids", help="Comma-separated category IDs")
    events_categories_bulk_unassign_events.add_argument("--event-ids", required=True, dest="event_ids", help="Comma-separated event IDs")
    events_categories_bulk_unassign_events.set_defaults(func=events_categories_cmd.cmd_events_categories_bulk_unassign_events, write_capable=True)

    events_categories_get = events_categories_sub.add_parser("get", help="Get one event category")
    events_categories_get.add_argument("--category-id", required=True, dest="category_id", help="Event category ID")
    events_categories_get.set_defaults(func=events_categories_cmd.cmd_events_categories_get, write_capable=False)

    events_categories_reorder_events = events_categories_sub.add_parser("reorder-events", help="Reorder events in one category")
    events_categories_reorder_events.add_argument("--category-id", required=True, dest="category_id", help="Event category ID")
    events_categories_reorder_events.add_argument("--request-json", required=True, dest="request_json", help="JSON reorder request or @file")
    events_categories_reorder_events.set_defaults(func=events_categories_cmd.cmd_events_categories_reorder_events, write_capable=True)

    events_schedule_items = sub.add_parser("events-schedule-items", help="Read and manage Wix Events schedule items")
    events_schedule_items_sub = events_schedule_items.add_subparsers(
        dest="events_schedule_items_cmd", required=True, parser_class=_ToolArgumentParser
    )
    events_schedule_items_get = events_schedule_items_sub.add_parser("get", help="Get one schedule item")
    events_schedule_items_get.add_argument("--item-id", required=True, dest="item_id", help="Schedule item ID")
    events_schedule_items_get.set_defaults(func=events_schedule_items_cmd.cmd_events_schedule_items_get, write_capable=False)

    events_schedule_items_query = events_schedule_items_sub.add_parser("query", help="Query schedule items")
    events_schedule_items_query.add_argument("--query-json", default="{}", dest="query_json", help="Optional JSON query body or @file")
    events_schedule_items_query.set_defaults(func=events_schedule_items_cmd.cmd_events_schedule_items_query, write_capable=False)

    events_schedule_items_add = events_schedule_items_sub.add_parser("add", help="Add a draft schedule item")
    events_schedule_items_add.add_argument("--schedule-item-json", required=True, dest="schedule_item_json", help="JSON schedule item body or @file")
    events_schedule_items_add.set_defaults(func=events_schedule_items_cmd.cmd_events_schedule_items_add, write_capable=True)

    events_schedule_items_create_bookmark = events_schedule_items_sub.add_parser("create-bookmark", help="Bookmark one schedule item")
    events_schedule_items_create_bookmark.add_argument("--item-id", required=True, dest="item_id", help="Schedule item ID")
    events_schedule_items_create_bookmark.set_defaults(func=events_schedule_items_cmd.cmd_events_schedule_items_create_bookmark, write_capable=True)

    events_schedule_items_delete_bookmark = events_schedule_items_sub.add_parser("delete-bookmark", help="Remove one schedule item bookmark")
    events_schedule_items_delete_bookmark.add_argument("--item-id", required=True, dest="item_id", help="Schedule item ID")
    events_schedule_items_delete_bookmark.set_defaults(func=events_schedule_items_cmd.cmd_events_schedule_items_delete_bookmark, write_capable=True)

    events_schedule_items_delete = events_schedule_items_sub.add_parser("delete", help="Delete a draft schedule item")
    events_schedule_items_delete.add_argument("--request-json", required=True, dest="request_json", help="JSON delete request body or @file")
    events_schedule_items_delete.set_defaults(func=events_schedule_items_cmd.cmd_events_schedule_items_delete, write_capable=True)

    events_schedule_items_discard_draft = events_schedule_items_sub.add_parser("discard-draft", help="Discard all draft schedule changes")
    events_schedule_items_discard_draft.add_argument("--request-json", required=True, dest="request_json", help="JSON discard request body or @file")
    events_schedule_items_discard_draft.set_defaults(func=events_schedule_items_cmd.cmd_events_schedule_items_discard_draft, write_capable=True)

    events_schedule_items_list_bookmarks = events_schedule_items_sub.add_parser("list-bookmarks", help="List schedule bookmarks for the current member")
    events_schedule_items_list_bookmarks.add_argument("--params-json", default=None, dest="params_json", help="Optional query parameters JSON object or @file")
    events_schedule_items_list_bookmarks.set_defaults(func=events_schedule_items_cmd.cmd_events_schedule_items_list_bookmarks, write_capable=False)

    events_schedule_items_list = events_schedule_items_sub.add_parser("list", help="List schedule items")
    events_schedule_items_list.add_argument("--params-json", default=None, dest="params_json", help="Optional query parameters JSON object or @file")
    events_schedule_items_list.set_defaults(func=events_schedule_items_cmd.cmd_events_schedule_items_list, write_capable=False)

    events_schedule_items_publish_draft = events_schedule_items_sub.add_parser("publish-draft", help="Publish a draft schedule")
    events_schedule_items_publish_draft.add_argument("--request-json", required=True, dest="request_json", help="JSON publish request body or @file")
    events_schedule_items_publish_draft.set_defaults(func=events_schedule_items_cmd.cmd_events_schedule_items_publish_draft, write_capable=True)

    events_schedule_items_reschedule_draft = events_schedule_items_sub.add_parser("reschedule-draft", help="Reschedule draft schedule items")
    events_schedule_items_reschedule_draft.add_argument("--request-json", required=True, dest="request_json", help="JSON reschedule request body or @file")
    events_schedule_items_reschedule_draft.set_defaults(func=events_schedule_items_cmd.cmd_events_schedule_items_reschedule_draft, write_capable=True)

    events_schedule_items_update = events_schedule_items_sub.add_parser("update", help="Update a draft schedule item")
    events_schedule_items_update.add_argument("--item-id", required=True, dest="item_id", help="Schedule item ID")
    events_schedule_items_update.add_argument("--schedule-item-json", required=True, dest="schedule_item_json", help="JSON schedule item body or @file")
    events_schedule_items_update.set_defaults(func=events_schedule_items_cmd.cmd_events_schedule_items_update, write_capable=True)

    events_policies_v2 = sub.add_parser("events-policies-v2", help="Read and manage Wix Events policies")
    events_policies_v2_sub = events_policies_v2.add_subparsers(
        dest="events_policies_v2_cmd", required=True, parser_class=_ToolArgumentParser
    )
    events_policies_v2_create = events_policies_v2_sub.add_parser("create", help="Create one event policy")
    events_policies_v2_create.add_argument("--policy-json", required=True, dest="policy_json", help="JSON policy body or @file")
    events_policies_v2_create.set_defaults(func=events_policies_v2_cmd.cmd_events_policies_v2_create, write_capable=True)

    events_policies_v2_get = events_policies_v2_sub.add_parser("get", help="Get one event policy")
    events_policies_v2_get.add_argument("--policy-id", required=True, dest="policy_id", help="Event policy ID")
    events_policies_v2_get.set_defaults(func=events_policies_v2_cmd.cmd_events_policies_v2_get, write_capable=False)

    events_policies_v2_update = events_policies_v2_sub.add_parser("update", help="Update one event policy")
    events_policies_v2_update.add_argument("--policy-id", required=True, dest="policy_id", help="Event policy ID")
    events_policies_v2_update.add_argument("--policy-json", required=True, dest="policy_json", help="JSON policy body or @file")
    events_policies_v2_update.set_defaults(func=events_policies_v2_cmd.cmd_events_policies_v2_update, write_capable=True)

    events_policies_v2_delete = events_policies_v2_sub.add_parser("delete", help="Delete one event policy permanently")
    events_policies_v2_delete.add_argument("--policy-id", required=True, dest="policy_id", help="Event policy ID")
    events_policies_v2_delete.set_defaults(func=events_policies_v2_cmd.cmd_events_policies_v2_delete, write_capable=True)

    events_policies_v2_query = events_policies_v2_sub.add_parser("query", help="Query event policies")
    events_policies_v2_query.add_argument("--query-json", default="{}", dest="query_json", help="Optional JSON query body or @file")
    events_policies_v2_query.set_defaults(func=events_policies_v2_cmd.cmd_events_policies_v2_query, write_capable=False)

    events_policies_v2_reorder = events_policies_v2_sub.add_parser("reorder", help="Reorder event policies")
    events_policies_v2_reorder.add_argument("--request-json", required=True, dest="request_json", help="JSON reorder request or @file")
    events_policies_v2_reorder.set_defaults(func=events_policies_v2_cmd.cmd_events_policies_v2_reorder, write_capable=True)

    events_staff_members = sub.add_parser("events-staff-members", help="Read and manage Wix Events staff members")
    events_staff_members_sub = events_staff_members.add_subparsers(
        dest="events_staff_members_cmd", required=True, parser_class=_ToolArgumentParser
    )
    events_staff_members_create = events_staff_members_sub.add_parser("create", help="Create one event staff member")
    events_staff_members_create.add_argument("--staff-member-json", required=True, dest="staff_member_json", help="JSON staff member body or @file")
    events_staff_members_create.set_defaults(func=events_staff_members_cmd.cmd_events_staff_members_create, write_capable=True)

    events_staff_members_get = events_staff_members_sub.add_parser("get", help="Get one event staff member")
    events_staff_members_get.add_argument("--staff-member-id", required=True, dest="staff_member_id", help="Event staff member ID")
    events_staff_members_get.set_defaults(func=events_staff_members_cmd.cmd_events_staff_members_get, write_capable=False)

    events_staff_members_update = events_staff_members_sub.add_parser("update", help="Update one event staff member")
    events_staff_members_update.add_argument("--staff-member-id", required=True, dest="staff_member_id", help="Event staff member ID")
    events_staff_members_update.add_argument("--staff-member-json", required=True, dest="staff_member_json", help="JSON staff member body or @file")
    events_staff_members_update.set_defaults(func=events_staff_members_cmd.cmd_events_staff_members_update, write_capable=True)

    events_staff_members_delete = events_staff_members_sub.add_parser("delete", help="Delete one event staff member permanently")
    events_staff_members_delete.add_argument("--staff-member-id", required=True, dest="staff_member_id", help="Event staff member ID")
    events_staff_members_delete.set_defaults(func=events_staff_members_cmd.cmd_events_staff_members_delete, write_capable=True)

    events_staff_members_query = events_staff_members_sub.add_parser("query", help="Query event staff members")
    events_staff_members_query.add_argument("--query-json", default="{}", dest="query_json", help="Optional JSON query body or @file")
    events_staff_members_query.set_defaults(func=events_staff_members_cmd.cmd_events_staff_members_query, write_capable=False)

    events_guests = sub.add_parser("events-guests", help="Query Wix Events guest records")
    events_guests_sub = events_guests.add_subparsers(dest="events_guests_cmd", required=True, parser_class=_ToolArgumentParser)
    events_guests_query = events_guests_sub.add_parser("query", help="Query event guests")
    events_guests_query.add_argument("--query-json", default="{}", dest="query_json", help="Optional JSON query body or @file")
    events_guests_query.set_defaults(func=events_guests_cmd.cmd_events_guests_query, write_capable=False)

    events_rsvps_v2 = sub.add_parser("events-rsvps-v2", help="Read and manage Wix Events RSVP V2 records")
    events_rsvps_v2_sub = events_rsvps_v2.add_subparsers(dest="events_rsvps_v2_cmd", required=True, parser_class=_ToolArgumentParser)

    events_rsvps_v2_create = events_rsvps_v2_sub.add_parser("create", help="Create one RSVP")
    events_rsvps_v2_create.add_argument("--rsvp-json", required=True, dest="rsvp_json", help="JSON RSVP body or @file")
    events_rsvps_v2_create.set_defaults(func=events_rsvps_v2_cmd.cmd_events_rsvps_v2_create, write_capable=True)

    events_rsvps_v2_get = events_rsvps_v2_sub.add_parser("get", help="Get one RSVP")
    events_rsvps_v2_get.add_argument("--rsvp-id", required=True, dest="rsvp_id", help="RSVP ID")
    events_rsvps_v2_get.set_defaults(func=events_rsvps_v2_cmd.cmd_events_rsvps_v2_get, write_capable=False)

    events_rsvps_v2_update = events_rsvps_v2_sub.add_parser("update", help="Update one RSVP")
    events_rsvps_v2_update.add_argument("--rsvp-id", required=True, dest="rsvp_id", help="RSVP ID")
    events_rsvps_v2_update.add_argument("--rsvp-json", required=True, dest="rsvp_json", help="JSON RSVP body with revision or @file")
    events_rsvps_v2_update.set_defaults(func=events_rsvps_v2_cmd.cmd_events_rsvps_v2_update, write_capable=True)

    events_rsvps_v2_delete = events_rsvps_v2_sub.add_parser("delete", help="Delete one RSVP")
    events_rsvps_v2_delete.add_argument("--rsvp-id", required=True, dest="rsvp_id", help="RSVP ID")
    events_rsvps_v2_delete.set_defaults(func=events_rsvps_v2_cmd.cmd_events_rsvps_v2_delete, write_capable=True)

    events_rsvps_v2_query = events_rsvps_v2_sub.add_parser("query", help="Query RSVPs")
    events_rsvps_v2_query.add_argument("--query-json", default="{}", dest="query_json", help="Optional JSON query body or @file")
    events_rsvps_v2_query.set_defaults(func=events_rsvps_v2_cmd.cmd_events_rsvps_v2_query, write_capable=False)

    events_rsvps_v2_search = events_rsvps_v2_sub.add_parser("search", help="Search RSVPs")
    events_rsvps_v2_search.add_argument("--search-json", required=True, dest="search_json", help="JSON search body or @file")
    events_rsvps_v2_search.set_defaults(func=events_rsvps_v2_cmd.cmd_events_rsvps_v2_search, write_capable=False)

    events_rsvps_v2_bulk_update = events_rsvps_v2_sub.add_parser("bulk-update", help="Update multiple RSVPs")
    events_rsvps_v2_bulk_update.add_argument("--rsvps-json", required=True, dest="rsvps_json", help="JSON bulk update body with revisions or @file")
    events_rsvps_v2_bulk_update.set_defaults(func=events_rsvps_v2_cmd.cmd_events_rsvps_v2_bulk_update, write_capable=True)

    events_rsvps_v2_bulk_delete_by_filter = events_rsvps_v2_sub.add_parser("bulk-delete-by-filter", help="Delete RSVPs by filter")
    events_rsvps_v2_bulk_delete_by_filter.add_argument("--filter-json", required=True, dest="filter_json", help="JSON filter body or @file")
    events_rsvps_v2_bulk_delete_by_filter.set_defaults(func=events_rsvps_v2_cmd.cmd_events_rsvps_v2_bulk_delete_by_filter, write_capable=True)

    events_rsvps_v2_check_in = events_rsvps_v2_sub.add_parser("check-in", help="Check in RSVP guests")
    events_rsvps_v2_check_in.add_argument("--rsvp-id", required=True, dest="rsvp_id", help="RSVP ID")
    events_rsvps_v2_check_in.add_argument("--request-json", default="{}", dest="request_json", help="Optional check-in body or @file")
    events_rsvps_v2_check_in.set_defaults(func=events_rsvps_v2_cmd.cmd_events_rsvps_v2_check_in, write_capable=True)

    events_rsvps_v2_cancel_check_in = events_rsvps_v2_sub.add_parser("cancel-check-in", help="Cancel RSVP guest check-in")
    events_rsvps_v2_cancel_check_in.add_argument("--rsvp-id", required=True, dest="rsvp_id", help="RSVP ID")
    events_rsvps_v2_cancel_check_in.add_argument("--request-json", default="{}", dest="request_json", help="Optional cancel check-in body or @file")
    events_rsvps_v2_cancel_check_in.set_defaults(func=events_rsvps_v2_cmd.cmd_events_rsvps_v2_cancel_check_in, write_capable=True)

    events_rsvps_v2_count = events_rsvps_v2_sub.add_parser("count", help="Count RSVPs")
    events_rsvps_v2_count.add_argument("--count-json", default="{}", dest="count_json", help="Optional count body or @file")
    events_rsvps_v2_count.set_defaults(func=events_rsvps_v2_cmd.cmd_events_rsvps_v2_count, write_capable=False)

    events_rsvps_v2_list_summary = events_rsvps_v2_sub.add_parser("list-summary", help="List RSVP summaries by event ID")
    events_rsvps_v2_list_summary.add_argument("--event-id", required=True, action="append", dest="event_id", help="Event ID; repeat for up to 100 events")
    events_rsvps_v2_list_summary.set_defaults(func=events_rsvps_v2_cmd.cmd_events_rsvps_v2_list_summary, write_capable=False)

    events_ticket_reservations = sub.add_parser("events-ticket-reservations", help="Read and manage Wix Events ticket reservations")
    events_ticket_reservations_sub = events_ticket_reservations.add_subparsers(dest="events_ticket_reservations_cmd", required=True, parser_class=_ToolArgumentParser)

    events_ticket_reservations_create = events_ticket_reservations_sub.add_parser("create", help="Create one ticket reservation")
    events_ticket_reservations_create.add_argument("--reservation-json", required=True, dest="reservation_json", help="JSON ticketReservation body or @file")
    events_ticket_reservations_create.set_defaults(func=events_ticket_reservations_cmd.cmd_events_ticket_reservations_create, write_capable=True)

    events_ticket_reservations_get = events_ticket_reservations_sub.add_parser("get", help="Get one ticket reservation")
    events_ticket_reservations_get.add_argument("--ticket-reservation-id", required=True, dest="ticket_reservation_id", help="Ticket reservation ID")
    events_ticket_reservations_get.set_defaults(func=events_ticket_reservations_cmd.cmd_events_ticket_reservations_get, write_capable=False)

    events_ticket_reservations_delete = events_ticket_reservations_sub.add_parser("delete", help="Delete one ticket reservation permanently")
    events_ticket_reservations_delete.add_argument("--ticket-reservation-id", required=True, dest="ticket_reservation_id", help="Ticket reservation ID")
    events_ticket_reservations_delete.set_defaults(func=events_ticket_reservations_cmd.cmd_events_ticket_reservations_delete, write_capable=True)

    events_ticket_reservations_bulk_update_tags = events_ticket_reservations_sub.add_parser("bulk-update-tags", help="Update tags for known ticket reservations")
    events_ticket_reservations_bulk_update_tags.add_argument("--tags-json", required=True, dest="tags_json", help="JSON tag update body with ids or @file")
    events_ticket_reservations_bulk_update_tags.set_defaults(func=events_ticket_reservations_cmd.cmd_events_ticket_reservations_bulk_update_tags, write_capable=True)

    events_ticket_reservations_bulk_update_tags_by_filter = events_ticket_reservations_sub.add_parser("bulk-update-tags-by-filter", help="Update ticket reservation tags by filter")
    events_ticket_reservations_bulk_update_tags_by_filter.add_argument("--filter-json", required=True, dest="filter_json", help="JSON filter/tag update body or @file")
    events_ticket_reservations_bulk_update_tags_by_filter.set_defaults(func=events_ticket_reservations_cmd.cmd_events_ticket_reservations_bulk_update_tags_by_filter, write_capable=True)

    events_ticket_reservations_cancel = events_ticket_reservations_sub.add_parser("cancel", help="Cancel one ticket reservation")
    events_ticket_reservations_cancel.add_argument("--ticket-reservation-id", required=True, dest="ticket_reservation_id", help="Ticket reservation ID")
    events_ticket_reservations_cancel.set_defaults(func=events_ticket_reservations_cmd.cmd_events_ticket_reservations_cancel, write_capable=True)

    events_tickets = sub.add_parser("events-tickets", help="Read and manage Wix Events tickets")
    events_tickets_sub = events_tickets.add_subparsers(dest="events_tickets_cmd", required=True, parser_class=_ToolArgumentParser)

    events_tickets_get = events_tickets_sub.add_parser("get", help="Get one event ticket")
    events_tickets_get.add_argument("--ticket-number", required=True, dest="ticket_number", help="Ticket number")
    events_tickets_get.set_defaults(func=events_tickets_cmd.cmd_events_tickets_get, write_capable=False)

    events_tickets_list = events_tickets_sub.add_parser("list", help="List event tickets")
    events_tickets_list.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    events_tickets_list.set_defaults(func=events_tickets_cmd.cmd_events_tickets_list, write_capable=False)

    events_tickets_update = events_tickets_sub.add_parser("update", help="Update one event ticket")
    events_tickets_update.add_argument("--ticket-number", required=True, dest="ticket_number", help="Ticket number")
    events_tickets_update.add_argument("--ticket-json", required=True, dest="ticket_json", help="JSON ticket body or @file")
    events_tickets_update.set_defaults(func=events_tickets_cmd.cmd_events_tickets_update, write_capable=True)

    events_tickets_bulk_update = events_tickets_sub.add_parser("bulk-update", help="Bulk update event tickets")
    events_tickets_bulk_update.add_argument("--tickets-json", required=True, dest="tickets_json", help="JSON bulk ticket update body or @file")
    events_tickets_bulk_update.set_defaults(func=events_tickets_cmd.cmd_events_tickets_bulk_update, write_capable=True)

    events_tickets_check_in = events_tickets_sub.add_parser("check-in", help="Check in event tickets")
    events_tickets_check_in.add_argument("--request-json", required=True, dest="request_json", help="JSON check-in body or @file")
    events_tickets_check_in.set_defaults(func=events_tickets_cmd.cmd_events_tickets_check_in, write_capable=True)

    events_tickets_delete_check_in = events_tickets_sub.add_parser("delete-check-in", help="Delete event ticket check-ins")
    events_tickets_delete_check_in.add_argument("--request-json", required=True, dest="request_json", help="JSON check-in delete body or @file")
    events_tickets_delete_check_in.set_defaults(func=events_tickets_cmd.cmd_events_tickets_delete_check_in, write_capable=True)

    events_orders = sub.add_parser("events-orders", help="Read and manage Wix Events orders and checkout")
    events_orders_sub = events_orders.add_subparsers(dest="events_orders_cmd", required=True, parser_class=_ToolArgumentParser)

    events_orders_list = events_orders_sub.add_parser("list", help="List event orders")
    events_orders_list.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    events_orders_list.set_defaults(func=events_orders_cmd.cmd_events_orders_list, write_capable=False)

    events_orders_get = events_orders_sub.add_parser("get", help="Get one event order")
    events_orders_get.add_argument("--event-id", required=True, dest="event_id", help="Event ID")
    events_orders_get.add_argument("--order-number", required=True, dest="order_number", help="Order number")
    events_orders_get.set_defaults(func=events_orders_cmd.cmd_events_orders_get, write_capable=False)

    events_orders_update = events_orders_sub.add_parser("update", help="Update one event order")
    events_orders_update.add_argument("--event-id", required=True, dest="event_id", help="Event ID")
    events_orders_update.add_argument("--order-number", required=True, dest="order_number", help="Order number")
    events_orders_update.add_argument("--order-json", required=True, dest="order_json", help="JSON order update body or @file")
    events_orders_update.set_defaults(func=events_orders_cmd.cmd_events_orders_update, write_capable=True)

    events_orders_bulk_update = events_orders_sub.add_parser("bulk-update", help="Bulk update event orders")
    events_orders_bulk_update.add_argument("--event-id", required=True, dest="event_id", help="Event ID")
    events_orders_bulk_update.add_argument("--orders-json", required=True, dest="orders_json", help="JSON bulk order update body or @file")
    events_orders_bulk_update.set_defaults(func=events_orders_cmd.cmd_events_orders_bulk_update, write_capable=True)

    events_orders_confirm = events_orders_sub.add_parser("confirm", help="Confirm event orders")
    events_orders_confirm.add_argument("--event-id", required=True, dest="event_id", help="Event ID")
    events_orders_confirm.add_argument("--request-json", required=True, dest="request_json", help="JSON confirm order body or @file")
    events_orders_confirm.set_defaults(func=events_orders_cmd.cmd_events_orders_confirm, write_capable=True)

    events_orders_get_summary = events_orders_sub.add_parser("get-summary", help="Get event order summary")
    events_orders_get_summary.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    events_orders_get_summary.set_defaults(func=events_orders_cmd.cmd_events_orders_get_summary, write_capable=False)

    events_orders_get_checkout_options = events_orders_sub.add_parser("get-checkout-options", help="Get event checkout options")
    events_orders_get_checkout_options.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    events_orders_get_checkout_options.set_defaults(func=events_orders_cmd.cmd_events_orders_get_checkout_options, write_capable=False)

    events_orders_list_available_tickets = events_orders_sub.add_parser("list-available-tickets", help="List available checkout tickets")
    events_orders_list_available_tickets.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    events_orders_list_available_tickets.set_defaults(func=events_orders_cmd.cmd_events_orders_list_available_tickets, write_capable=False)

    events_orders_query_available_tickets = events_orders_sub.add_parser("query-available-tickets", help="Query available checkout tickets")
    events_orders_query_available_tickets.add_argument("--query-json", default="{}", dest="query_json", help="JSON query body or @file")
    events_orders_query_available_tickets.set_defaults(func=events_orders_cmd.cmd_events_orders_query_available_tickets, write_capable=False)

    events_orders_create_reservation = events_orders_sub.add_parser("create-reservation", help="Create a deprecated checkout reservation")
    events_orders_create_reservation.add_argument("--reservation-json", required=True, dest="reservation_json", help="JSON reservation body or @file")
    events_orders_create_reservation.set_defaults(func=events_orders_cmd.cmd_events_orders_create_reservation, write_capable=True)

    events_orders_cancel_reservation = events_orders_sub.add_parser("cancel-reservation", help="Cancel a deprecated checkout reservation")
    events_orders_cancel_reservation.add_argument("--reservation-id", required=True, dest="reservation_id", help="Reservation ID")
    events_orders_cancel_reservation.set_defaults(func=events_orders_cmd.cmd_events_orders_cancel_reservation, write_capable=True)

    events_orders_checkout = events_orders_sub.add_parser("checkout", help="Checkout reserved event tickets")
    events_orders_checkout.add_argument("--checkout-json", required=True, dest="checkout_json", help="JSON checkout body or @file")
    events_orders_checkout.set_defaults(func=events_orders_cmd.cmd_events_orders_checkout, write_capable=True)

    events_orders_update_checkout = events_orders_sub.add_parser("update-checkout", help="Update event checkout")
    events_orders_update_checkout.add_argument("--order-number", required=True, dest="order_number", help="Order number")
    events_orders_update_checkout.add_argument("--checkout-json", required=True, dest="checkout_json", help="JSON checkout update body or @file")
    events_orders_update_checkout.set_defaults(func=events_orders_cmd.cmd_events_orders_update_checkout, write_capable=True)

    events_orders_get_invoice = events_orders_sub.add_parser("get-invoice", help="Get checkout invoice preview")
    events_orders_get_invoice.add_argument("--reservation-id", required=True, dest="reservation_id", help="Reservation ID")
    events_orders_get_invoice.add_argument("--invoice-json", default="{}", dest="invoice_json", help="Optional invoice request JSON or @file")
    events_orders_get_invoice.set_defaults(func=events_orders_cmd.cmd_events_orders_get_invoice, write_capable=False)

    events_forms = sub.add_parser("events-forms", help="Read and manage Wix Events registration forms")
    events_forms_sub = events_forms.add_subparsers(dest="events_forms_cmd", required=True, parser_class=_ToolArgumentParser)

    events_forms_get_form = events_forms_sub.add_parser("get-form", help="Get one event registration form")
    events_forms_get_form.add_argument("--event-id", required=True, dest="event_id", help="Event ID")
    events_forms_get_form.set_defaults(func=events_forms_cmd.cmd_events_forms_get_form, write_capable=False)

    events_forms_discard_draft = events_forms_sub.add_parser("discard-draft", help="Discard deprecated event form draft changes")
    events_forms_discard_draft.add_argument("--event-id", required=True, dest="event_id", help="Event ID")
    events_forms_discard_draft.set_defaults(func=events_forms_cmd.cmd_events_forms_discard_draft, write_capable=True)

    events_forms_add_control = events_forms_sub.add_parser("add-control", help="Add one registration form control")
    events_forms_add_control.add_argument("--event-id", required=True, dest="event_id", help="Event ID")
    events_forms_add_control.add_argument("--control-json", required=True, dest="control_json", help="JSON control body or @file")
    events_forms_add_control.set_defaults(func=events_forms_cmd.cmd_events_forms_add_control, write_capable=True)

    events_forms_update_control = events_forms_sub.add_parser("update-control", help="Update one registration form control")
    events_forms_update_control.add_argument("--event-id", required=True, dest="event_id", help="Event ID")
    events_forms_update_control.add_argument("--control-id", required=True, dest="control_id", help="Control ID")
    events_forms_update_control.add_argument("--control-json", required=True, dest="control_json", help="JSON control body or @file")
    events_forms_update_control.set_defaults(func=events_forms_cmd.cmd_events_forms_update_control, write_capable=True)

    events_forms_delete_control = events_forms_sub.add_parser("delete-control", help="Delete one registration form control")
    events_forms_delete_control.add_argument("--event-id", required=True, dest="event_id", help="Event ID")
    events_forms_delete_control.add_argument("--control-id", required=True, dest="control_id", help="Control ID")
    events_forms_delete_control.set_defaults(func=events_forms_cmd.cmd_events_forms_delete_control, write_capable=True)

    events_forms_update_messages = events_forms_sub.add_parser("update-messages", help="Update registration form messages")
    events_forms_update_messages.add_argument("--event-id", required=True, dest="event_id", help="Event ID")
    events_forms_update_messages.add_argument("--messages-json", required=True, dest="messages_json", help="JSON messages body or @file")
    events_forms_update_messages.set_defaults(func=events_forms_cmd.cmd_events_forms_update_messages, write_capable=True)

    events_forms_publish_draft = events_forms_sub.add_parser("publish-draft", help="Publish a deprecated event form draft")
    events_forms_publish_draft.add_argument("--event-id", required=True, dest="event_id", help="Event ID")
    events_forms_publish_draft.set_defaults(func=events_forms_cmd.cmd_events_forms_publish_draft, write_capable=True)

    restaurants_menus = sub.add_parser("restaurants-menus", help="Read and manage Wix Restaurants menus")
    restaurants_menus_sub = restaurants_menus.add_subparsers(dest="restaurants_menus_cmd", required=True, parser_class=_ToolArgumentParser)

    restaurants_menus_list = restaurants_menus_sub.add_parser("list", help="List restaurant menus")
    restaurants_menus_list.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    restaurants_menus_list.set_defaults(func=restaurants_menus_cmd.cmd_restaurants_menus_list, write_capable=False)

    restaurants_menus_get = restaurants_menus_sub.add_parser("get", help="Get one restaurant menu")
    restaurants_menus_get.add_argument("--menu-id", required=True, dest="menu_id", help="Menu ID")
    restaurants_menus_get.set_defaults(func=restaurants_menus_cmd.cmd_restaurants_menus_get, write_capable=False)

    restaurants_menus_query = restaurants_menus_sub.add_parser("query", help="Query restaurant menus")
    restaurants_menus_query.add_argument("--query-json", default="{}", dest="query_json", help="JSON query body or @file")
    restaurants_menus_query.set_defaults(func=restaurants_menus_cmd.cmd_restaurants_menus_query, write_capable=False)

    restaurants_menus_create = restaurants_menus_sub.add_parser("create", help="Create one restaurant menu")
    restaurants_menus_create.add_argument("--menu-json", required=True, dest="menu_json", help="JSON create body or @file")
    restaurants_menus_create.set_defaults(func=restaurants_menus_cmd.cmd_restaurants_menus_create, write_capable=True)

    restaurants_menus_update = restaurants_menus_sub.add_parser("update", help="Update one restaurant menu")
    restaurants_menus_update.add_argument("--menu-id", required=True, dest="menu_id", help="Menu ID")
    restaurants_menus_update.add_argument("--menu-json", required=True, dest="menu_json", help="JSON update body with menu.revision or @file")
    restaurants_menus_update.set_defaults(func=restaurants_menus_cmd.cmd_restaurants_menus_update, write_capable=True)

    restaurants_menus_delete = restaurants_menus_sub.add_parser("delete", help="Delete one restaurant menu")
    restaurants_menus_delete.add_argument("--menu-id", required=True, dest="menu_id", help="Menu ID")
    restaurants_menus_delete.set_defaults(func=restaurants_menus_cmd.cmd_restaurants_menus_delete, write_capable=True)

    restaurants_menus_bulk_create = restaurants_menus_sub.add_parser("bulk-create", help="Create restaurant menus in bulk")
    restaurants_menus_bulk_create.add_argument("--menus-json", required=True, dest="menus_json", help="JSON bulk create body or @file")
    restaurants_menus_bulk_create.set_defaults(func=restaurants_menus_cmd.cmd_restaurants_menus_bulk_create, write_capable=True)

    restaurants_menus_bulk_update = restaurants_menus_sub.add_parser("bulk-update", help="Update restaurant menus in bulk")
    restaurants_menus_bulk_update.add_argument("--menus-json", required=True, dest="menus_json", help="JSON bulk update body with menu revisions or @file")
    restaurants_menus_bulk_update.set_defaults(func=restaurants_menus_cmd.cmd_restaurants_menus_bulk_update, write_capable=True)

    restaurants_menus_duplicate = restaurants_menus_sub.add_parser("duplicate", help="Duplicate one restaurant menu")
    restaurants_menus_duplicate.add_argument("--menu-id", required=True, dest="menu_id", help="Menu ID")
    restaurants_menus_duplicate.add_argument("--options-json", default="{}", dest="options_json", help="Optional duplicate options JSON or @file")
    restaurants_menus_duplicate.set_defaults(func=restaurants_menus_cmd.cmd_restaurants_menus_duplicate, write_capable=True)

    restaurants_menus_update_extended_fields = restaurants_menus_sub.add_parser(
        "update-extended-fields",
        help="Update one restaurant menu's extended fields",
    )
    restaurants_menus_update_extended_fields.add_argument("--menu-id", required=True, dest="menu_id", help="Menu ID")
    restaurants_menus_update_extended_fields.add_argument(
        "--extended-fields-json",
        required=True,
        dest="extended_fields_json",
        help="JSON extended fields update body or @file",
    )
    restaurants_menus_update_extended_fields.set_defaults(func=restaurants_menus_cmd.cmd_restaurants_menus_update_extended_fields, write_capable=True)

    restaurants_sections = sub.add_parser("restaurants-sections", help="Read and manage Wix Restaurants menu sections")
    restaurants_sections_sub = restaurants_sections.add_subparsers(dest="restaurants_sections_cmd", required=True, parser_class=_ToolArgumentParser)

    restaurants_sections_list = restaurants_sections_sub.add_parser("list", help="List restaurant menu sections")
    restaurants_sections_list.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    restaurants_sections_list.set_defaults(func=restaurants_sections_cmd.cmd_restaurants_sections_list, write_capable=False)

    restaurants_sections_get = restaurants_sections_sub.add_parser("get", help="Get one restaurant menu section")
    restaurants_sections_get.add_argument("--section-id", required=True, dest="section_id", help="Section ID")
    restaurants_sections_get.set_defaults(func=restaurants_sections_cmd.cmd_restaurants_sections_get, write_capable=False)

    restaurants_sections_query = restaurants_sections_sub.add_parser("query", help="Query restaurant menu sections")
    restaurants_sections_query.add_argument("--query-json", default="{}", dest="query_json", help="JSON query body or @file")
    restaurants_sections_query.set_defaults(func=restaurants_sections_cmd.cmd_restaurants_sections_query, write_capable=False)

    restaurants_sections_create = restaurants_sections_sub.add_parser("create", help="Create one restaurant menu section")
    restaurants_sections_create.add_argument("--section-json", required=True, dest="section_json", help="JSON create body or @file")
    restaurants_sections_create.set_defaults(func=restaurants_sections_cmd.cmd_restaurants_sections_create, write_capable=True)

    restaurants_sections_update = restaurants_sections_sub.add_parser("update", help="Update one restaurant menu section")
    restaurants_sections_update.add_argument("--section-id", required=True, dest="section_id", help="Section ID")
    restaurants_sections_update.add_argument("--section-json", required=True, dest="section_json", help="JSON update body with section.revision or @file")
    restaurants_sections_update.set_defaults(func=restaurants_sections_cmd.cmd_restaurants_sections_update, write_capable=True)

    restaurants_sections_delete = restaurants_sections_sub.add_parser("delete", help="Delete one restaurant menu section")
    restaurants_sections_delete.add_argument("--section-id", required=True, dest="section_id", help="Section ID")
    restaurants_sections_delete.set_defaults(func=restaurants_sections_cmd.cmd_restaurants_sections_delete, write_capable=True)

    restaurants_sections_bulk_create = restaurants_sections_sub.add_parser("bulk-create", help="Create restaurant menu sections in bulk")
    restaurants_sections_bulk_create.add_argument("--sections-json", required=True, dest="sections_json", help="JSON bulk create body or @file")
    restaurants_sections_bulk_create.set_defaults(func=restaurants_sections_cmd.cmd_restaurants_sections_bulk_create, write_capable=True)

    restaurants_sections_bulk_delete = restaurants_sections_sub.add_parser("bulk-delete", help="Delete restaurant menu sections in bulk")
    restaurants_sections_bulk_delete.add_argument("--sections-json", required=True, dest="sections_json", help="JSON bulk delete body or @file")
    restaurants_sections_bulk_delete.set_defaults(func=restaurants_sections_cmd.cmd_restaurants_sections_bulk_delete, write_capable=True)

    restaurants_sections_bulk_update = restaurants_sections_sub.add_parser("bulk-update", help="Update restaurant menu sections in bulk")
    restaurants_sections_bulk_update.add_argument("--sections-json", required=True, dest="sections_json", help="JSON bulk update body with section revisions or @file")
    restaurants_sections_bulk_update.set_defaults(func=restaurants_sections_cmd.cmd_restaurants_sections_bulk_update, write_capable=True)

    restaurants_sections_duplicate = restaurants_sections_sub.add_parser("duplicate", help="Duplicate one restaurant menu section")
    restaurants_sections_duplicate.add_argument("--section-id", required=True, dest="section_id", help="Section ID")
    restaurants_sections_duplicate.add_argument("--options-json", default="{}", dest="options_json", help="Optional duplicate options JSON or @file")
    restaurants_sections_duplicate.set_defaults(func=restaurants_sections_cmd.cmd_restaurants_sections_duplicate, write_capable=True)

    restaurants_items = sub.add_parser("restaurants-items", help="Read and manage Wix Restaurants menu items")
    restaurants_items_sub = restaurants_items.add_subparsers(dest="restaurants_items_cmd", required=True, parser_class=_ToolArgumentParser)

    restaurants_items_list = restaurants_items_sub.add_parser("list", help="List restaurant menu items")
    restaurants_items_list.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    restaurants_items_list.set_defaults(func=restaurants_items_cmd.cmd_restaurants_items_list, write_capable=False)

    restaurants_items_get = restaurants_items_sub.add_parser("get", help="Get one restaurant menu item")
    restaurants_items_get.add_argument("--item-id", required=True, dest="item_id", help="Item ID")
    restaurants_items_get.set_defaults(func=restaurants_items_cmd.cmd_restaurants_items_get, write_capable=False)

    restaurants_items_query = restaurants_items_sub.add_parser("query", help="Query restaurant menu items")
    restaurants_items_query.add_argument("--query-json", default="{}", dest="query_json", help="JSON query body or @file")
    restaurants_items_query.set_defaults(func=restaurants_items_cmd.cmd_restaurants_items_query, write_capable=False)

    restaurants_items_search = restaurants_items_sub.add_parser("search", help="Search restaurant menu items")
    restaurants_items_search.add_argument("--search-json", default="{}", dest="search_json", help="JSON search body or @file")
    restaurants_items_search.set_defaults(func=restaurants_items_cmd.cmd_restaurants_items_search, write_capable=False)

    restaurants_items_count = restaurants_items_sub.add_parser("count", help="Count restaurant menu items")
    restaurants_items_count.add_argument("--filter-json", default="{}", dest="filter_json", help="JSON count body or @file")
    restaurants_items_count.set_defaults(func=restaurants_items_cmd.cmd_restaurants_items_count, write_capable=False)

    restaurants_items_create = restaurants_items_sub.add_parser("create", help="Create one restaurant menu item")
    restaurants_items_create.add_argument("--item-json", required=True, dest="item_json", help="JSON create body or @file")
    restaurants_items_create.set_defaults(func=restaurants_items_cmd.cmd_restaurants_items_create, write_capable=True)

    restaurants_items_update = restaurants_items_sub.add_parser("update", help="Update one restaurant menu item")
    restaurants_items_update.add_argument("--item-id", required=True, dest="item_id", help="Item ID")
    restaurants_items_update.add_argument("--item-json", required=True, dest="item_json", help="JSON update body with item.revision or @file")
    restaurants_items_update.set_defaults(func=restaurants_items_cmd.cmd_restaurants_items_update, write_capable=True)

    restaurants_items_delete = restaurants_items_sub.add_parser("delete", help="Delete one restaurant menu item")
    restaurants_items_delete.add_argument("--item-id", required=True, dest="item_id", help="Item ID")
    restaurants_items_delete.set_defaults(func=restaurants_items_cmd.cmd_restaurants_items_delete, write_capable=True)

    restaurants_items_bulk_create = restaurants_items_sub.add_parser("bulk-create", help="Create restaurant menu items in bulk")
    restaurants_items_bulk_create.add_argument("--items-json", required=True, dest="items_json", help="JSON bulk create body or @file")
    restaurants_items_bulk_create.set_defaults(func=restaurants_items_cmd.cmd_restaurants_items_bulk_create, write_capable=True)

    restaurants_items_bulk_delete = restaurants_items_sub.add_parser("bulk-delete", help="Delete restaurant menu items in bulk")
    restaurants_items_bulk_delete.add_argument("--items-json", required=True, dest="items_json", help="JSON bulk delete body or @file")
    restaurants_items_bulk_delete.set_defaults(func=restaurants_items_cmd.cmd_restaurants_items_bulk_delete, write_capable=True)

    restaurants_items_bulk_update = restaurants_items_sub.add_parser("bulk-update", help="Update restaurant menu items in bulk")
    restaurants_items_bulk_update.add_argument("--items-json", required=True, dest="items_json", help="JSON bulk update body with item revisions or @file")
    restaurants_items_bulk_update.set_defaults(func=restaurants_items_cmd.cmd_restaurants_items_bulk_update, write_capable=True)

    restaurants_item_labels = sub.add_parser("restaurants-item-labels", help="Read and manage Wix Restaurants item labels")
    restaurants_item_labels_sub = restaurants_item_labels.add_subparsers(
        dest="restaurants_item_labels_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    restaurants_item_labels_list = restaurants_item_labels_sub.add_parser("list", help="List restaurant item labels")
    restaurants_item_labels_list.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    restaurants_item_labels_list.set_defaults(func=restaurants_item_labels_cmd.cmd_restaurants_item_labels_list, write_capable=False)

    restaurants_item_labels_get = restaurants_item_labels_sub.add_parser("get", help="Get one restaurant item label")
    restaurants_item_labels_get.add_argument("--label-id", required=True, dest="label_id", help="Label ID")
    restaurants_item_labels_get.set_defaults(func=restaurants_item_labels_cmd.cmd_restaurants_item_labels_get, write_capable=False)

    restaurants_item_labels_query = restaurants_item_labels_sub.add_parser("query", help="Query restaurant item labels")
    restaurants_item_labels_query.add_argument("--query-json", default="{}", dest="query_json", help="JSON query body or @file")
    restaurants_item_labels_query.set_defaults(func=restaurants_item_labels_cmd.cmd_restaurants_item_labels_query, write_capable=False)

    restaurants_item_labels_create = restaurants_item_labels_sub.add_parser("create", help="Create one restaurant item label")
    restaurants_item_labels_create.add_argument("--label-json", required=True, dest="label_json", help="JSON create body or @file")
    restaurants_item_labels_create.set_defaults(func=restaurants_item_labels_cmd.cmd_restaurants_item_labels_create, write_capable=True)

    restaurants_item_labels_update = restaurants_item_labels_sub.add_parser("update", help="Update one restaurant item label")
    restaurants_item_labels_update.add_argument("--label-id", required=True, dest="label_id", help="Label ID")
    restaurants_item_labels_update.add_argument("--label-json", required=True, dest="label_json", help="JSON update body with label.revision or @file")
    restaurants_item_labels_update.set_defaults(func=restaurants_item_labels_cmd.cmd_restaurants_item_labels_update, write_capable=True)

    restaurants_item_labels_delete = restaurants_item_labels_sub.add_parser("delete", help="Delete one restaurant item label")
    restaurants_item_labels_delete.add_argument("--label-id", required=True, dest="label_id", help="Label ID")
    restaurants_item_labels_delete.set_defaults(func=restaurants_item_labels_cmd.cmd_restaurants_item_labels_delete, write_capable=True)

    restaurants_item_variants = sub.add_parser("restaurants-item-variants", help="Read and manage Wix Restaurants item variants")
    restaurants_item_variants_sub = restaurants_item_variants.add_subparsers(
        dest="restaurants_item_variants_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    restaurants_item_variants_list = restaurants_item_variants_sub.add_parser("list", help="List restaurant item variants")
    restaurants_item_variants_list.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    restaurants_item_variants_list.set_defaults(func=restaurants_item_variants_cmd.cmd_restaurants_item_variants_list, write_capable=False)

    restaurants_item_variants_get = restaurants_item_variants_sub.add_parser("get", help="Get one restaurant item variant")
    restaurants_item_variants_get.add_argument("--variant-id", required=True, dest="variant_id", help="Variant ID")
    restaurants_item_variants_get.set_defaults(func=restaurants_item_variants_cmd.cmd_restaurants_item_variants_get, write_capable=False)

    restaurants_item_variants_query = restaurants_item_variants_sub.add_parser("query", help="Query restaurant item variants")
    restaurants_item_variants_query.add_argument("--query-json", default="{}", dest="query_json", help="JSON query body or @file")
    restaurants_item_variants_query.set_defaults(func=restaurants_item_variants_cmd.cmd_restaurants_item_variants_query, write_capable=False)

    restaurants_item_variants_count = restaurants_item_variants_sub.add_parser("count", help="Count restaurant item variants")
    restaurants_item_variants_count.add_argument("--filter-json", default="{}", dest="filter_json", help="JSON count body or @file")
    restaurants_item_variants_count.set_defaults(func=restaurants_item_variants_cmd.cmd_restaurants_item_variants_count, write_capable=False)

    restaurants_item_variants_create = restaurants_item_variants_sub.add_parser("create", help="Create one restaurant item variant")
    restaurants_item_variants_create.add_argument("--variant-json", required=True, dest="variant_json", help="JSON create body or @file")
    restaurants_item_variants_create.set_defaults(func=restaurants_item_variants_cmd.cmd_restaurants_item_variants_create, write_capable=True)

    restaurants_item_variants_update = restaurants_item_variants_sub.add_parser("update", help="Update one restaurant item variant")
    restaurants_item_variants_update.add_argument("--variant-id", required=True, dest="variant_id", help="Variant ID")
    restaurants_item_variants_update.add_argument("--variant-json", required=True, dest="variant_json", help="JSON update body with variant.revision or @file")
    restaurants_item_variants_update.set_defaults(func=restaurants_item_variants_cmd.cmd_restaurants_item_variants_update, write_capable=True)

    restaurants_item_variants_delete = restaurants_item_variants_sub.add_parser("delete", help="Delete one restaurant item variant")
    restaurants_item_variants_delete.add_argument("--variant-id", required=True, dest="variant_id", help="Variant ID")
    restaurants_item_variants_delete.set_defaults(func=restaurants_item_variants_cmd.cmd_restaurants_item_variants_delete, write_capable=True)

    restaurants_item_variants_bulk_create = restaurants_item_variants_sub.add_parser("bulk-create", help="Create restaurant item variants in bulk")
    restaurants_item_variants_bulk_create.add_argument("--variants-json", required=True, dest="variants_json", help="JSON bulk create body or @file")
    restaurants_item_variants_bulk_create.set_defaults(func=restaurants_item_variants_cmd.cmd_restaurants_item_variants_bulk_create, write_capable=True)

    restaurants_item_variants_bulk_delete = restaurants_item_variants_sub.add_parser("bulk-delete", help="Delete restaurant item variants in bulk")
    restaurants_item_variants_bulk_delete.add_argument("--variants-json", required=True, dest="variants_json", help="JSON bulk delete body or @file")
    restaurants_item_variants_bulk_delete.set_defaults(func=restaurants_item_variants_cmd.cmd_restaurants_item_variants_bulk_delete, write_capable=True)

    restaurants_item_variants_bulk_update = restaurants_item_variants_sub.add_parser("bulk-update", help="Update restaurant item variants in bulk")
    restaurants_item_variants_bulk_update.add_argument("--variants-json", required=True, dest="variants_json", help="JSON bulk update body with variant revisions or @file")
    restaurants_item_variants_bulk_update.set_defaults(func=restaurants_item_variants_cmd.cmd_restaurants_item_variants_bulk_update, write_capable=True)

    restaurants_item_modifiers = sub.add_parser("restaurants-item-modifiers", help="Read and manage Wix Restaurants item modifiers")
    restaurants_item_modifiers_sub = restaurants_item_modifiers.add_subparsers(
        dest="restaurants_item_modifiers_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    restaurants_item_modifiers_list = restaurants_item_modifiers_sub.add_parser("list", help="List restaurant item modifiers")
    restaurants_item_modifiers_list.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    restaurants_item_modifiers_list.set_defaults(func=restaurants_item_modifiers_cmd.cmd_restaurants_item_modifiers_list, write_capable=False)

    restaurants_item_modifiers_get = restaurants_item_modifiers_sub.add_parser("get", help="Get one restaurant item modifier")
    restaurants_item_modifiers_get.add_argument("--modifier-id", required=True, dest="modifier_id", help="Modifier ID")
    restaurants_item_modifiers_get.set_defaults(func=restaurants_item_modifiers_cmd.cmd_restaurants_item_modifiers_get, write_capable=False)

    restaurants_item_modifiers_query = restaurants_item_modifiers_sub.add_parser("query", help="Query restaurant item modifiers")
    restaurants_item_modifiers_query.add_argument("--query-json", default="{}", dest="query_json", help="JSON query body or @file")
    restaurants_item_modifiers_query.set_defaults(func=restaurants_item_modifiers_cmd.cmd_restaurants_item_modifiers_query, write_capable=False)

    restaurants_item_modifiers_count = restaurants_item_modifiers_sub.add_parser("count", help="Count restaurant item modifiers")
    restaurants_item_modifiers_count.add_argument("--filter-json", default="{}", dest="filter_json", help="JSON count body or @file")
    restaurants_item_modifiers_count.set_defaults(func=restaurants_item_modifiers_cmd.cmd_restaurants_item_modifiers_count, write_capable=False)

    restaurants_item_modifiers_create = restaurants_item_modifiers_sub.add_parser("create", help="Create one restaurant item modifier")
    restaurants_item_modifiers_create.add_argument("--modifier-json", required=True, dest="modifier_json", help="JSON create body or @file")
    restaurants_item_modifiers_create.set_defaults(func=restaurants_item_modifiers_cmd.cmd_restaurants_item_modifiers_create, write_capable=True)

    restaurants_item_modifiers_update = restaurants_item_modifiers_sub.add_parser("update", help="Update one restaurant item modifier")
    restaurants_item_modifiers_update.add_argument("--modifier-id", required=True, dest="modifier_id", help="Modifier ID")
    restaurants_item_modifiers_update.add_argument("--modifier-json", required=True, dest="modifier_json", help="JSON update body with modifier.revision or @file")
    restaurants_item_modifiers_update.set_defaults(func=restaurants_item_modifiers_cmd.cmd_restaurants_item_modifiers_update, write_capable=True)

    restaurants_item_modifiers_delete = restaurants_item_modifiers_sub.add_parser("delete", help="Delete one restaurant item modifier")
    restaurants_item_modifiers_delete.add_argument("--modifier-id", required=True, dest="modifier_id", help="Modifier ID")
    restaurants_item_modifiers_delete.set_defaults(func=restaurants_item_modifiers_cmd.cmd_restaurants_item_modifiers_delete, write_capable=True)

    restaurants_item_modifiers_bulk_create = restaurants_item_modifiers_sub.add_parser("bulk-create", help="Create restaurant item modifiers in bulk")
    restaurants_item_modifiers_bulk_create.add_argument("--modifiers-json", required=True, dest="modifiers_json", help="JSON bulk create body or @file")
    restaurants_item_modifiers_bulk_create.set_defaults(func=restaurants_item_modifiers_cmd.cmd_restaurants_item_modifiers_bulk_create, write_capable=True)

    restaurants_item_modifiers_bulk_delete = restaurants_item_modifiers_sub.add_parser("bulk-delete", help="Delete restaurant item modifiers in bulk")
    restaurants_item_modifiers_bulk_delete.add_argument("--modifiers-json", required=True, dest="modifiers_json", help="JSON bulk delete body or @file")
    restaurants_item_modifiers_bulk_delete.set_defaults(func=restaurants_item_modifiers_cmd.cmd_restaurants_item_modifiers_bulk_delete, write_capable=True)

    restaurants_item_modifiers_bulk_update = restaurants_item_modifiers_sub.add_parser("bulk-update", help="Update restaurant item modifiers in bulk")
    restaurants_item_modifiers_bulk_update.add_argument("--modifiers-json", required=True, dest="modifiers_json", help="JSON bulk update body with modifier revisions or @file")
    restaurants_item_modifiers_bulk_update.set_defaults(func=restaurants_item_modifiers_cmd.cmd_restaurants_item_modifiers_bulk_update, write_capable=True)

    restaurants_item_modifier_groups = sub.add_parser("restaurants-item-modifier-groups", help="Read and manage Wix Restaurants item modifier groups")
    restaurants_item_modifier_groups_sub = restaurants_item_modifier_groups.add_subparsers(
        dest="restaurants_item_modifier_groups_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    restaurants_item_modifier_groups_list = restaurants_item_modifier_groups_sub.add_parser("list", help="List restaurant item modifier groups")
    restaurants_item_modifier_groups_list.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    restaurants_item_modifier_groups_list.set_defaults(func=restaurants_item_modifier_groups_cmd.cmd_restaurants_item_modifier_groups_list, write_capable=False)

    restaurants_item_modifier_groups_get = restaurants_item_modifier_groups_sub.add_parser("get", help="Get one restaurant item modifier group")
    restaurants_item_modifier_groups_get.add_argument("--modifier-group-id", required=True, dest="modifier_group_id", help="Modifier group ID")
    restaurants_item_modifier_groups_get.set_defaults(func=restaurants_item_modifier_groups_cmd.cmd_restaurants_item_modifier_groups_get, write_capable=False)

    restaurants_item_modifier_groups_query = restaurants_item_modifier_groups_sub.add_parser("query", help="Query restaurant item modifier groups")
    restaurants_item_modifier_groups_query.add_argument("--query-json", default="{}", dest="query_json", help="JSON query body or @file")
    restaurants_item_modifier_groups_query.set_defaults(func=restaurants_item_modifier_groups_cmd.cmd_restaurants_item_modifier_groups_query, write_capable=False)

    restaurants_item_modifier_groups_count = restaurants_item_modifier_groups_sub.add_parser("count", help="Count restaurant item modifier groups")
    restaurants_item_modifier_groups_count.add_argument("--filter-json", default="{}", dest="filter_json", help="JSON count body or @file")
    restaurants_item_modifier_groups_count.set_defaults(func=restaurants_item_modifier_groups_cmd.cmd_restaurants_item_modifier_groups_count, write_capable=False)

    restaurants_item_modifier_groups_create = restaurants_item_modifier_groups_sub.add_parser("create", help="Create one restaurant item modifier group")
    restaurants_item_modifier_groups_create.add_argument("--modifier-group-json", required=True, dest="modifier_group_json", help="JSON create body or @file")
    restaurants_item_modifier_groups_create.set_defaults(func=restaurants_item_modifier_groups_cmd.cmd_restaurants_item_modifier_groups_create, write_capable=True)

    restaurants_item_modifier_groups_update = restaurants_item_modifier_groups_sub.add_parser("update", help="Update one restaurant item modifier group")
    restaurants_item_modifier_groups_update.add_argument("--modifier-group-id", required=True, dest="modifier_group_id", help="Modifier group ID")
    restaurants_item_modifier_groups_update.add_argument("--modifier-group-json", required=True, dest="modifier_group_json", help="JSON update body with modifierGroup.revision or @file")
    restaurants_item_modifier_groups_update.set_defaults(func=restaurants_item_modifier_groups_cmd.cmd_restaurants_item_modifier_groups_update, write_capable=True)

    restaurants_item_modifier_groups_delete = restaurants_item_modifier_groups_sub.add_parser("delete", help="Delete one restaurant item modifier group")
    restaurants_item_modifier_groups_delete.add_argument("--modifier-group-id", required=True, dest="modifier_group_id", help="Modifier group ID")
    restaurants_item_modifier_groups_delete.set_defaults(func=restaurants_item_modifier_groups_cmd.cmd_restaurants_item_modifier_groups_delete, write_capable=True)

    restaurants_item_modifier_groups_bulk_create = restaurants_item_modifier_groups_sub.add_parser("bulk-create", help="Create restaurant item modifier groups in bulk")
    restaurants_item_modifier_groups_bulk_create.add_argument("--modifier-groups-json", required=True, dest="modifier_groups_json", help="JSON bulk create body or @file")
    restaurants_item_modifier_groups_bulk_create.set_defaults(func=restaurants_item_modifier_groups_cmd.cmd_restaurants_item_modifier_groups_bulk_create, write_capable=True)

    restaurants_item_modifier_groups_bulk_update = restaurants_item_modifier_groups_sub.add_parser("bulk-update", help="Update restaurant item modifier groups in bulk")
    restaurants_item_modifier_groups_bulk_update.add_argument("--modifier-groups-json", required=True, dest="modifier_groups_json", help="JSON bulk update body with modifier group revisions or @file")
    restaurants_item_modifier_groups_bulk_update.set_defaults(func=restaurants_item_modifier_groups_cmd.cmd_restaurants_item_modifier_groups_bulk_update, write_capable=True)

    restaurants_online_order_operation_groups = sub.add_parser("restaurants-online-order-operation-groups", help="Read and manage Wix Restaurants Online Orders operation groups")
    restaurants_online_order_operation_groups_sub = restaurants_online_order_operation_groups.add_subparsers(
        dest="restaurants_online_order_operation_groups_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    restaurants_online_order_operation_groups_get = restaurants_online_order_operation_groups_sub.add_parser("get", help="Get one restaurant online order operation group")
    restaurants_online_order_operation_groups_get.add_argument("--operation-group-id", required=True, dest="operation_group_id", help="Operation group ID")
    restaurants_online_order_operation_groups_get.set_defaults(func=restaurants_online_order_operation_groups_cmd.cmd_restaurants_online_order_operation_groups_get, write_capable=False)

    restaurants_online_order_operation_groups_query = restaurants_online_order_operation_groups_sub.add_parser("query", help="Query restaurant online order operation groups")
    restaurants_online_order_operation_groups_query.add_argument("--query-json", default="{}", dest="query_json", help="JSON query body or @file")
    restaurants_online_order_operation_groups_query.set_defaults(func=restaurants_online_order_operation_groups_cmd.cmd_restaurants_online_order_operation_groups_query, write_capable=False)

    restaurants_online_order_operation_groups_create = restaurants_online_order_operation_groups_sub.add_parser("create", help="Create one restaurant online order operation group")
    restaurants_online_order_operation_groups_create.add_argument("--operation-group-json", required=True, dest="operation_group_json", help="JSON create body or @file")
    restaurants_online_order_operation_groups_create.set_defaults(func=restaurants_online_order_operation_groups_cmd.cmd_restaurants_online_order_operation_groups_create, write_capable=True)

    restaurants_online_order_operation_groups_update = restaurants_online_order_operation_groups_sub.add_parser("update", help="Update one restaurant online order operation group")
    restaurants_online_order_operation_groups_update.add_argument("--operation-group-id", required=True, dest="operation_group_id", help="Operation group ID")
    restaurants_online_order_operation_groups_update.add_argument("--operation-group-json", required=True, dest="operation_group_json", help="JSON update body with operationGroup.revision or @file")
    restaurants_online_order_operation_groups_update.set_defaults(func=restaurants_online_order_operation_groups_cmd.cmd_restaurants_online_order_operation_groups_update, write_capable=True)

    restaurants_online_order_operation_groups_delete = restaurants_online_order_operation_groups_sub.add_parser("delete", help="Delete one restaurant online order operation group")
    restaurants_online_order_operation_groups_delete.add_argument("--operation-group-id", required=True, dest="operation_group_id", help="Operation group ID")
    restaurants_online_order_operation_groups_delete.set_defaults(func=restaurants_online_order_operation_groups_cmd.cmd_restaurants_online_order_operation_groups_delete, write_capable=True)

    restaurants_online_order_operation_groups_bulk_create = restaurants_online_order_operation_groups_sub.add_parser("bulk-create", help="Create restaurant online order operation groups in bulk")
    restaurants_online_order_operation_groups_bulk_create.add_argument("--operation-groups-json", required=True, dest="operation_groups_json", help="JSON bulk create body or @file")
    restaurants_online_order_operation_groups_bulk_create.set_defaults(func=restaurants_online_order_operation_groups_cmd.cmd_restaurants_online_order_operation_groups_bulk_create, write_capable=True)

    restaurants_online_order_operation_groups_bulk_delete = restaurants_online_order_operation_groups_sub.add_parser("bulk-delete", help="Delete restaurant online order operation groups in bulk")
    restaurants_online_order_operation_groups_bulk_delete.add_argument("--operation-groups-json", required=True, dest="operation_groups_json", help="JSON bulk delete body or @file")
    restaurants_online_order_operation_groups_bulk_delete.set_defaults(func=restaurants_online_order_operation_groups_cmd.cmd_restaurants_online_order_operation_groups_bulk_delete, write_capable=True)

    restaurants_online_order_operation_groups_bulk_update = restaurants_online_order_operation_groups_sub.add_parser("bulk-update", help="Update restaurant online order operation groups in bulk")
    restaurants_online_order_operation_groups_bulk_update.add_argument("--operation-groups-json", required=True, dest="operation_groups_json", help="JSON bulk update body with operation group revisions or @file")
    restaurants_online_order_operation_groups_bulk_update.set_defaults(func=restaurants_online_order_operation_groups_cmd.cmd_restaurants_online_order_operation_groups_bulk_update, write_capable=True)

    restaurants_online_order_operation_groups_bulk_update_tags = restaurants_online_order_operation_groups_sub.add_parser("bulk-update-tags", help="Update tags on restaurant online order operation groups")
    restaurants_online_order_operation_groups_bulk_update_tags.add_argument("--tags-json", required=True, dest="tags_json", help="JSON tags body with ids and assign/unassign arrays or @file")
    restaurants_online_order_operation_groups_bulk_update_tags.set_defaults(func=restaurants_online_order_operation_groups_cmd.cmd_restaurants_online_order_operation_groups_bulk_update_tags, write_capable=True)

    restaurants_online_order_operation_groups_bulk_update_tags_by_filter = restaurants_online_order_operation_groups_sub.add_parser("bulk-update-tags-by-filter", help="Update tags on restaurant online order operation groups by filter")
    restaurants_online_order_operation_groups_bulk_update_tags_by_filter.add_argument("--filter-json", required=True, dest="filter_json", help="JSON filter tags body or @file")
    restaurants_online_order_operation_groups_bulk_update_tags_by_filter.set_defaults(func=restaurants_online_order_operation_groups_cmd.cmd_restaurants_online_order_operation_groups_bulk_update_tags_by_filter, write_capable=True)

    restaurants_online_order_operations = sub.add_parser("restaurants-online-order-operations", help="Read and manage Wix Restaurants Online Orders operations")
    restaurants_online_order_operations_sub = restaurants_online_order_operations.add_subparsers(
        dest="restaurants_online_order_operations_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    restaurants_online_order_operations_get = restaurants_online_order_operations_sub.add_parser("get", help="Get one restaurant online order operation")
    restaurants_online_order_operations_get.add_argument("--operation-id", required=True, dest="operation_id", help="Operation ID")
    restaurants_online_order_operations_get.set_defaults(func=restaurants_online_order_operations_cmd.cmd_restaurants_online_order_operations_get, write_capable=False)

    restaurants_online_order_operations_list = restaurants_online_order_operations_sub.add_parser("list", help="List restaurant online order operations")
    restaurants_online_order_operations_list.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    restaurants_online_order_operations_list.set_defaults(func=restaurants_online_order_operations_cmd.cmd_restaurants_online_order_operations_list, write_capable=False)

    restaurants_online_order_operations_query = restaurants_online_order_operations_sub.add_parser("query", help="Query restaurant online order operations")
    restaurants_online_order_operations_query.add_argument("--query-json", default="{}", dest="query_json", help="JSON query body or @file")
    restaurants_online_order_operations_query.set_defaults(func=restaurants_online_order_operations_cmd.cmd_restaurants_online_order_operations_query, write_capable=False)

    restaurants_online_order_operations_first_slot_by_fulfillment = restaurants_online_order_operations_sub.add_parser("first-available-time-slot-per-fulfillment-type", help="Calculate the first available time slot per fulfillment type")
    restaurants_online_order_operations_first_slot_by_fulfillment.add_argument("--operation-id", required=True, dest="operation_id", help="Operation ID")
    restaurants_online_order_operations_first_slot_by_fulfillment.add_argument("--params-json", default="{}", dest="params_json", help="Optional calculation query params JSON or @file")
    restaurants_online_order_operations_first_slot_by_fulfillment.set_defaults(func=restaurants_online_order_operations_cmd.cmd_restaurants_online_order_operations_first_available_time_slot_per_fulfillment_type, write_capable=False)

    restaurants_online_order_operations_first_slots_by_operation = restaurants_online_order_operations_sub.add_parser("first-available-time-slots-per-operation", help="Calculate first available time slots per operation")
    restaurants_online_order_operations_first_slots_by_operation.add_argument("--operations-json", required=True, dest="operations_json", help="JSON calculation body or @file")
    restaurants_online_order_operations_first_slots_by_operation.set_defaults(func=restaurants_online_order_operations_cmd.cmd_restaurants_online_order_operations_first_available_time_slots_per_operation, write_capable=False)

    restaurants_online_order_operations_first_slots_by_menu = restaurants_online_order_operations_sub.add_parser("first-available-time-slots-per-menu", help="Calculate first available time slots per menu")
    restaurants_online_order_operations_first_slots_by_menu.add_argument("--operation-id", required=True, dest="operation_id", help="Operation ID")
    restaurants_online_order_operations_first_slots_by_menu.add_argument("--params-json", default="{}", dest="params_json", help="Optional calculation query params JSON or @file")
    restaurants_online_order_operations_first_slots_by_menu.set_defaults(func=restaurants_online_order_operations_cmd.cmd_restaurants_online_order_operations_first_available_time_slots_per_menu, write_capable=False)

    restaurants_online_order_operations_available_slots = restaurants_online_order_operations_sub.add_parser("available-time-slots-for-date", help="Calculate available time slots for a date")
    restaurants_online_order_operations_available_slots.add_argument("--operation-id", required=True, dest="operation_id", help="Operation ID")
    restaurants_online_order_operations_available_slots.add_argument("--params-json", default="{}", dest="params_json", help="Optional calculation query params JSON or @file")
    restaurants_online_order_operations_available_slots.set_defaults(func=restaurants_online_order_operations_cmd.cmd_restaurants_online_order_operations_available_time_slots_for_date, write_capable=False)

    restaurants_online_order_operations_available_dates = restaurants_online_order_operations_sub.add_parser("available-dates-in-range", help="Calculate available dates in a range")
    restaurants_online_order_operations_available_dates.add_argument("--operation-id", required=True, dest="operation_id", help="Operation ID")
    restaurants_online_order_operations_available_dates.add_argument("--params-json", default="{}", dest="params_json", help="Optional calculation query params JSON or @file")
    restaurants_online_order_operations_available_dates.set_defaults(func=restaurants_online_order_operations_cmd.cmd_restaurants_online_order_operations_available_dates_in_range, write_capable=False)

    restaurants_online_order_operations_validate_address = restaurants_online_order_operations_sub.add_parser("validate-address", help="Validate an address for one operation")
    restaurants_online_order_operations_validate_address.add_argument("--operation-id", required=True, dest="operation_id", help="Operation ID")
    restaurants_online_order_operations_validate_address.add_argument("--params-json", default="{}", dest="params_json", help="Optional validation query params JSON or @file")
    restaurants_online_order_operations_validate_address.set_defaults(func=restaurants_online_order_operations_cmd.cmd_restaurants_online_order_operations_validate_address, write_capable=False)

    restaurants_online_order_operations_update = restaurants_online_order_operations_sub.add_parser("update", help="Update one restaurant online order operation")
    restaurants_online_order_operations_update.add_argument("--operation-id", required=True, dest="operation_id", help="Operation ID")
    restaurants_online_order_operations_update.add_argument("--operation-json", required=True, dest="operation_json", help="JSON update body with operation.revision or @file")
    restaurants_online_order_operations_update.set_defaults(func=restaurants_online_order_operations_cmd.cmd_restaurants_online_order_operations_update, write_capable=True)

    restaurants_online_order_operations_delete = restaurants_online_order_operations_sub.add_parser("delete", help="Delete one restaurant online order operation")
    restaurants_online_order_operations_delete.add_argument("--operation-id", required=True, dest="operation_id", help="Operation ID")
    restaurants_online_order_operations_delete.set_defaults(func=restaurants_online_order_operations_cmd.cmd_restaurants_online_order_operations_delete, write_capable=True)

    restaurants_online_order_operations_bulk_update_tags = restaurants_online_order_operations_sub.add_parser("bulk-update-tags", help="Update tags on restaurant online order operations")
    restaurants_online_order_operations_bulk_update_tags.add_argument("--tags-json", required=True, dest="tags_json", help="JSON tags body with ids/operationIds and assignTags/unassignTags arrays or @file")
    restaurants_online_order_operations_bulk_update_tags.set_defaults(func=restaurants_online_order_operations_cmd.cmd_restaurants_online_order_operations_bulk_update_tags, write_capable=True)

    restaurants_online_order_operations_bulk_update_tags_by_filter = restaurants_online_order_operations_sub.add_parser("bulk-update-tags-by-filter", help="Update tags on restaurant online order operations by filter")
    restaurants_online_order_operations_bulk_update_tags_by_filter.add_argument("--filter-json", required=True, dest="filter_json", help="JSON filter tags body or @file")
    restaurants_online_order_operations_bulk_update_tags_by_filter.set_defaults(func=restaurants_online_order_operations_cmd.cmd_restaurants_online_order_operations_bulk_update_tags_by_filter, write_capable=True)

    restaurants_online_order_menu_ordering_settings = sub.add_parser(
        "restaurants-online-order-menu-ordering-settings",
        help="Read and manage Wix Restaurants Online Orders menu-ordering settings",
    )
    restaurants_online_order_menu_ordering_settings_sub = restaurants_online_order_menu_ordering_settings.add_subparsers(
        dest="restaurants_online_order_menu_ordering_settings_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    restaurants_online_order_menu_ordering_settings_get = restaurants_online_order_menu_ordering_settings_sub.add_parser(
        "get",
        help="Get one menu-ordering settings object",
    )
    restaurants_online_order_menu_ordering_settings_get.add_argument(
        "--menu-ordering-settings-id",
        required=True,
        dest="menu_ordering_settings_id",
        help="Menu ordering settings ID",
    )
    restaurants_online_order_menu_ordering_settings_get.set_defaults(
        func=restaurants_online_order_menu_ordering_settings_cmd.cmd_restaurants_online_order_menu_ordering_settings_get,
        write_capable=False,
    )

    restaurants_online_order_menu_ordering_settings_query = restaurants_online_order_menu_ordering_settings_sub.add_parser(
        "query",
        help="Query restaurant menu-ordering settings",
    )
    restaurants_online_order_menu_ordering_settings_query.add_argument(
        "--query-json",
        default="{}",
        dest="query_json",
        help="JSON query body or @file",
    )
    restaurants_online_order_menu_ordering_settings_query.set_defaults(
        func=restaurants_online_order_menu_ordering_settings_cmd.cmd_restaurants_online_order_menu_ordering_settings_query,
        write_capable=False,
    )

    restaurants_online_order_menu_ordering_settings_list_menus_availability_status = restaurants_online_order_menu_ordering_settings_sub.add_parser(
        "list-menus-availability-status",
        help="List restaurant menu availability status",
    )
    restaurants_online_order_menu_ordering_settings_list_menus_availability_status.set_defaults(
        func=restaurants_online_order_menu_ordering_settings_cmd.cmd_restaurants_online_order_menu_ordering_settings_list_menus_availability_status,
        write_capable=False,
    )

    restaurants_online_order_menu_ordering_settings_update = restaurants_online_order_menu_ordering_settings_sub.add_parser(
        "update",
        help="Update one restaurant menu-ordering settings object",
    )
    restaurants_online_order_menu_ordering_settings_update.add_argument(
        "--menu-ordering-settings-id",
        required=True,
        dest="menu_ordering_settings_id",
        help="Menu ordering settings ID",
    )
    restaurants_online_order_menu_ordering_settings_update.add_argument(
        "--menu-ordering-settings-json",
        required=True,
        dest="menu_ordering_settings_json",
        help="JSON update body with menuOrderingSettings.revision or @file",
    )
    restaurants_online_order_menu_ordering_settings_update.set_defaults(
        func=restaurants_online_order_menu_ordering_settings_cmd.cmd_restaurants_online_order_menu_ordering_settings_update,
        write_capable=True,
    )

    restaurants_online_order_menu_ordering_settings_bulk_update = restaurants_online_order_menu_ordering_settings_sub.add_parser(
        "bulk-update",
        help="Update restaurant menu-ordering settings in bulk",
    )
    restaurants_online_order_menu_ordering_settings_bulk_update.add_argument(
        "--menu-ordering-settings-json",
        required=True,
        dest="menu_ordering_settings_json",
        help="JSON bulk update body with menuOrderingSettings and revisions or @file",
    )
    restaurants_online_order_menu_ordering_settings_bulk_update.set_defaults(
        func=restaurants_online_order_menu_ordering_settings_cmd.cmd_restaurants_online_order_menu_ordering_settings_bulk_update,
        write_capable=True,
    )

    restaurants_online_order_menu_ordering_settings_bulk_update_tags = restaurants_online_order_menu_ordering_settings_sub.add_parser(
        "bulk-update-tags",
        help="Update tags on restaurant menu-ordering settings",
    )
    restaurants_online_order_menu_ordering_settings_bulk_update_tags.add_argument(
        "--tags-json",
        required=True,
        dest="tags_json",
        help="JSON tags body with ids/menuOrderingSettingsIds and assignTags/unassignTags arrays or @file",
    )
    restaurants_online_order_menu_ordering_settings_bulk_update_tags.set_defaults(
        func=restaurants_online_order_menu_ordering_settings_cmd.cmd_restaurants_online_order_menu_ordering_settings_bulk_update_tags,
        write_capable=True,
    )

    restaurants_online_order_menu_ordering_settings_bulk_update_tags_by_filter = restaurants_online_order_menu_ordering_settings_sub.add_parser(
        "bulk-update-tags-by-filter",
        help="Update tags on restaurant menu-ordering settings by filter",
    )
    restaurants_online_order_menu_ordering_settings_bulk_update_tags_by_filter.add_argument(
        "--filter-json",
        required=True,
        dest="filter_json",
        help="JSON filter tags body or @file",
    )
    restaurants_online_order_menu_ordering_settings_bulk_update_tags_by_filter.set_defaults(
        func=restaurants_online_order_menu_ordering_settings_cmd.cmd_restaurants_online_order_menu_ordering_settings_bulk_update_tags_by_filter,
        write_capable=True,
    )

    restaurants_online_order_menu_ordering_settings_update_extended_fields = restaurants_online_order_menu_ordering_settings_sub.add_parser(
        "update-extended-fields",
        help="Update extended fields for one restaurant menu-ordering settings object",
    )
    restaurants_online_order_menu_ordering_settings_update_extended_fields.add_argument(
        "--menu-ordering-settings-id",
        required=True,
        dest="menu_ordering_settings_id",
        help="Menu ordering settings ID",
    )
    restaurants_online_order_menu_ordering_settings_update_extended_fields.add_argument(
        "--extended-fields-json",
        required=True,
        dest="extended_fields_json",
        help="JSON update extended fields body or @file",
    )
    restaurants_online_order_menu_ordering_settings_update_extended_fields.set_defaults(
        func=restaurants_online_order_menu_ordering_settings_cmd.cmd_restaurants_online_order_menu_ordering_settings_update_extended_fields,
        write_capable=True,
    )

    restaurants_online_order_menu_ordering_settings_upsert_by_menu_id = restaurants_online_order_menu_ordering_settings_sub.add_parser(
        "upsert-by-menu-id",
        help="Upsert restaurant menu-ordering settings by menu ID",
    )
    restaurants_online_order_menu_ordering_settings_upsert_by_menu_id.add_argument(
        "--menu-id",
        required=True,
        dest="menu_id",
        help="Menu ID",
    )
    restaurants_online_order_menu_ordering_settings_upsert_by_menu_id.add_argument(
        "--upsert-json",
        required=True,
        dest="upsert_json",
        help="JSON upsert body or @file",
    )
    restaurants_online_order_menu_ordering_settings_upsert_by_menu_id.set_defaults(
        func=restaurants_online_order_menu_ordering_settings_cmd.cmd_restaurants_online_order_menu_ordering_settings_upsert_by_menu_id,
        write_capable=True,
    )

    restaurants_online_order_fulfillment_methods = sub.add_parser(
        "restaurants-online-order-fulfillment-methods",
        help="Read and manage Wix Restaurants Online Orders fulfillment methods",
    )
    restaurants_online_order_fulfillment_methods_sub = restaurants_online_order_fulfillment_methods.add_subparsers(
        dest="restaurants_online_order_fulfillment_methods_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    restaurants_online_order_fulfillment_methods_list = restaurants_online_order_fulfillment_methods_sub.add_parser("list", help="List restaurant fulfillment methods")
    restaurants_online_order_fulfillment_methods_list.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    restaurants_online_order_fulfillment_methods_list.set_defaults(func=restaurants_online_order_fulfillment_methods_cmd.cmd_restaurants_online_order_fulfillment_methods_list, write_capable=False)

    restaurants_online_order_fulfillment_methods_get = restaurants_online_order_fulfillment_methods_sub.add_parser("get", help="Get one restaurant fulfillment method")
    restaurants_online_order_fulfillment_methods_get.add_argument("--fulfillment-method-id", required=True, dest="fulfillment_method_id", help="Fulfillment method ID")
    restaurants_online_order_fulfillment_methods_get.set_defaults(func=restaurants_online_order_fulfillment_methods_cmd.cmd_restaurants_online_order_fulfillment_methods_get, write_capable=False)

    restaurants_online_order_fulfillment_methods_query = restaurants_online_order_fulfillment_methods_sub.add_parser("query", help="Query restaurant fulfillment methods")
    restaurants_online_order_fulfillment_methods_query.add_argument("--query-json", default="{}", dest="query_json", help="JSON query body or @file")
    restaurants_online_order_fulfillment_methods_query.set_defaults(func=restaurants_online_order_fulfillment_methods_cmd.cmd_restaurants_online_order_fulfillment_methods_query, write_capable=False)

    restaurants_online_order_fulfillment_methods_list_available_for_address = restaurants_online_order_fulfillment_methods_sub.add_parser("list-available-for-address", help="List available fulfillment methods for an address")
    restaurants_online_order_fulfillment_methods_list_available_for_address.add_argument("--address-json", required=True, dest="address_json", help="JSON address body or @file")
    restaurants_online_order_fulfillment_methods_list_available_for_address.set_defaults(func=restaurants_online_order_fulfillment_methods_cmd.cmd_restaurants_online_order_fulfillment_methods_list_available_for_address, write_capable=False)

    restaurants_online_order_fulfillment_methods_get_accumulated_availability = restaurants_online_order_fulfillment_methods_sub.add_parser("get-accumulated-availability", help="Get accumulated fulfillment methods availability")
    restaurants_online_order_fulfillment_methods_get_accumulated_availability.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    restaurants_online_order_fulfillment_methods_get_accumulated_availability.set_defaults(func=restaurants_online_order_fulfillment_methods_cmd.cmd_restaurants_online_order_fulfillment_methods_get_accumulated_availability, write_capable=False)

    restaurants_online_order_fulfillment_methods_get_combined_availability = restaurants_online_order_fulfillment_methods_sub.add_parser("get-combined-availability", help="Get combined fulfillment method availability (deprecated by Wix)")
    restaurants_online_order_fulfillment_methods_get_combined_availability.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    restaurants_online_order_fulfillment_methods_get_combined_availability.set_defaults(func=restaurants_online_order_fulfillment_methods_cmd.cmd_restaurants_online_order_fulfillment_methods_get_combined_availability, write_capable=False)

    restaurants_online_order_fulfillment_methods_get_aggregated_availability = restaurants_online_order_fulfillment_methods_sub.add_parser("get-aggregated-availability", help="Get aggregated fulfillment method availability")
    restaurants_online_order_fulfillment_methods_get_aggregated_availability.add_argument("--availability-json", required=True, dest="availability_json", help="JSON availability body or @file")
    restaurants_online_order_fulfillment_methods_get_aggregated_availability.set_defaults(func=restaurants_online_order_fulfillment_methods_cmd.cmd_restaurants_online_order_fulfillment_methods_get_aggregated_availability, write_capable=False)

    restaurants_online_order_fulfillment_methods_create = restaurants_online_order_fulfillment_methods_sub.add_parser("create", help="Create one restaurant fulfillment method")
    restaurants_online_order_fulfillment_methods_create.add_argument("--fulfillment-method-json", required=True, dest="fulfillment_method_json", help="JSON create body or @file")
    restaurants_online_order_fulfillment_methods_create.set_defaults(func=restaurants_online_order_fulfillment_methods_cmd.cmd_restaurants_online_order_fulfillment_methods_create, write_capable=True)

    restaurants_online_order_fulfillment_methods_bulk_create = restaurants_online_order_fulfillment_methods_sub.add_parser("bulk-create", help="Create restaurant fulfillment methods in bulk")
    restaurants_online_order_fulfillment_methods_bulk_create.add_argument("--fulfillment-methods-json", required=True, dest="fulfillment_methods_json", help="JSON bulk create body or @file")
    restaurants_online_order_fulfillment_methods_bulk_create.set_defaults(func=restaurants_online_order_fulfillment_methods_cmd.cmd_restaurants_online_order_fulfillment_methods_bulk_create, write_capable=True)

    restaurants_online_order_fulfillment_methods_update = restaurants_online_order_fulfillment_methods_sub.add_parser("update", help="Update one restaurant fulfillment method")
    restaurants_online_order_fulfillment_methods_update.add_argument("--fulfillment-method-id", required=True, dest="fulfillment_method_id", help="Fulfillment method ID")
    restaurants_online_order_fulfillment_methods_update.add_argument("--fulfillment-method-json", required=True, dest="fulfillment_method_json", help="JSON update body with fulfillmentMethod.revision or @file")
    restaurants_online_order_fulfillment_methods_update.set_defaults(func=restaurants_online_order_fulfillment_methods_cmd.cmd_restaurants_online_order_fulfillment_methods_update, write_capable=True)

    restaurants_online_order_fulfillment_methods_delete = restaurants_online_order_fulfillment_methods_sub.add_parser("delete", help="Delete one restaurant fulfillment method")
    restaurants_online_order_fulfillment_methods_delete.add_argument("--fulfillment-method-id", required=True, dest="fulfillment_method_id", help="Fulfillment method ID")
    restaurants_online_order_fulfillment_methods_delete.set_defaults(func=restaurants_online_order_fulfillment_methods_cmd.cmd_restaurants_online_order_fulfillment_methods_delete, write_capable=True)

    restaurants_online_order_fulfillment_methods_bulk_update_tags = restaurants_online_order_fulfillment_methods_sub.add_parser("bulk-update-tags", help="Update tags on restaurant fulfillment methods")
    restaurants_online_order_fulfillment_methods_bulk_update_tags.add_argument("--tags-json", required=True, dest="tags_json", help="JSON tags body with ids/fulfillmentMethodIds and assignTags/unassignTags arrays or @file")
    restaurants_online_order_fulfillment_methods_bulk_update_tags.set_defaults(func=restaurants_online_order_fulfillment_methods_cmd.cmd_restaurants_online_order_fulfillment_methods_bulk_update_tags, write_capable=True)

    restaurants_online_order_fulfillment_methods_bulk_update_tags_by_filter = restaurants_online_order_fulfillment_methods_sub.add_parser("bulk-update-tags-by-filter", help="Update tags on restaurant fulfillment methods by filter")
    restaurants_online_order_fulfillment_methods_bulk_update_tags_by_filter.add_argument("--filter-json", required=True, dest="filter_json", help="JSON filter tags body or @file")
    restaurants_online_order_fulfillment_methods_bulk_update_tags_by_filter.set_defaults(func=restaurants_online_order_fulfillment_methods_cmd.cmd_restaurants_online_order_fulfillment_methods_bulk_update_tags_by_filter, write_capable=True)

    restaurants_online_order_availability_exceptions = sub.add_parser("restaurants-online-order-availability-exceptions", help="Read and manage Wix Restaurants Online Orders availability exceptions")
    restaurants_online_order_availability_exceptions_sub = restaurants_online_order_availability_exceptions.add_subparsers(dest="restaurants_online_order_availability_exceptions_cmd", required=True, parser_class=_ToolArgumentParser)

    restaurants_online_order_availability_exceptions_get = restaurants_online_order_availability_exceptions_sub.add_parser("get", help="Get one restaurant availability exception")
    restaurants_online_order_availability_exceptions_get.add_argument("--availability-exception-id", required=True, dest="availability_exception_id", help="Availability exception ID")
    restaurants_online_order_availability_exceptions_get.set_defaults(func=restaurants_online_order_availability_exceptions_cmd.cmd_restaurants_online_order_availability_exceptions_get, write_capable=False)

    restaurants_online_order_availability_exceptions_query = restaurants_online_order_availability_exceptions_sub.add_parser("query", help="Query restaurant availability exceptions")
    restaurants_online_order_availability_exceptions_query.add_argument("--query-json", default="{}", dest="query_json", help="JSON query body or @file")
    restaurants_online_order_availability_exceptions_query.set_defaults(func=restaurants_online_order_availability_exceptions_cmd.cmd_restaurants_online_order_availability_exceptions_query, write_capable=False)

    restaurants_online_order_availability_exceptions_create = restaurants_online_order_availability_exceptions_sub.add_parser("create", help="Create one restaurant availability exception")
    restaurants_online_order_availability_exceptions_create.add_argument("--availability-exception-json", required=True, dest="availability_exception_json", help="JSON create body or @file")
    restaurants_online_order_availability_exceptions_create.set_defaults(func=restaurants_online_order_availability_exceptions_cmd.cmd_restaurants_online_order_availability_exceptions_create, write_capable=True)

    restaurants_online_order_availability_exceptions_bulk_create = restaurants_online_order_availability_exceptions_sub.add_parser("bulk-create", help="Create restaurant availability exceptions in bulk")
    restaurants_online_order_availability_exceptions_bulk_create.add_argument("--availability-exceptions-json", required=True, dest="availability_exceptions_json", help="JSON bulk create body or @file")
    restaurants_online_order_availability_exceptions_bulk_create.set_defaults(func=restaurants_online_order_availability_exceptions_cmd.cmd_restaurants_online_order_availability_exceptions_bulk_create, write_capable=True)

    restaurants_online_order_availability_exceptions_update = restaurants_online_order_availability_exceptions_sub.add_parser("update", help="Update one restaurant availability exception")
    restaurants_online_order_availability_exceptions_update.add_argument("--availability-exception-id", required=True, dest="availability_exception_id", help="Availability exception ID")
    restaurants_online_order_availability_exceptions_update.add_argument("--availability-exception-json", required=True, dest="availability_exception_json", help="JSON update body with availabilityException.revision or @file")
    restaurants_online_order_availability_exceptions_update.set_defaults(func=restaurants_online_order_availability_exceptions_cmd.cmd_restaurants_online_order_availability_exceptions_update, write_capable=True)

    restaurants_online_order_availability_exceptions_bulk_update = restaurants_online_order_availability_exceptions_sub.add_parser("bulk-update", help="Update restaurant availability exceptions in bulk")
    restaurants_online_order_availability_exceptions_bulk_update.add_argument("--availability-exceptions-json", required=True, dest="availability_exceptions_json", help="JSON bulk update body with availabilityExceptions revisions or @file")
    restaurants_online_order_availability_exceptions_bulk_update.set_defaults(func=restaurants_online_order_availability_exceptions_cmd.cmd_restaurants_online_order_availability_exceptions_bulk_update, write_capable=True)

    restaurants_online_order_availability_exceptions_delete = restaurants_online_order_availability_exceptions_sub.add_parser("delete", help="Delete one restaurant availability exception")
    restaurants_online_order_availability_exceptions_delete.add_argument("--availability-exception-id", required=True, dest="availability_exception_id", help="Availability exception ID")
    restaurants_online_order_availability_exceptions_delete.set_defaults(func=restaurants_online_order_availability_exceptions_cmd.cmd_restaurants_online_order_availability_exceptions_delete, write_capable=True)

    restaurants_online_order_availability_exceptions_bulk_update_tags = restaurants_online_order_availability_exceptions_sub.add_parser("bulk-update-tags", help="Update tags on restaurant availability exceptions")
    restaurants_online_order_availability_exceptions_bulk_update_tags.add_argument("--tags-json", required=True, dest="tags_json", help="JSON tags body with ids/availabilityExceptionIds and assignTags/unassignTags arrays or @file")
    restaurants_online_order_availability_exceptions_bulk_update_tags.set_defaults(func=restaurants_online_order_availability_exceptions_cmd.cmd_restaurants_online_order_availability_exceptions_bulk_update_tags, write_capable=True)

    restaurants_online_order_availability_exceptions_bulk_update_tags_by_filter = restaurants_online_order_availability_exceptions_sub.add_parser("bulk-update-tags-by-filter", help="Update tags on restaurant availability exceptions by filter")
    restaurants_online_order_availability_exceptions_bulk_update_tags_by_filter.add_argument("--filter-json", required=True, dest="filter_json", help="JSON filter tags body or @file")
    restaurants_online_order_availability_exceptions_bulk_update_tags_by_filter.set_defaults(func=restaurants_online_order_availability_exceptions_cmd.cmd_restaurants_online_order_availability_exceptions_bulk_update_tags_by_filter, write_capable=True)

    restaurants_online_order_service_fees = sub.add_parser("restaurants-online-order-service-fees", help="Read and manage Wix Restaurants Online Orders service fee rules")
    restaurants_online_order_service_fees_sub = restaurants_online_order_service_fees.add_subparsers(dest="restaurants_online_order_service_fees_cmd", required=True, parser_class=_ToolArgumentParser)

    restaurants_online_order_service_fees_calculate = restaurants_online_order_service_fees_sub.add_parser("calculate", help="Calculate service fees for an order")
    restaurants_online_order_service_fees_calculate.add_argument("--order-json", required=True, dest="order_json", help="JSON order body or @file")
    restaurants_online_order_service_fees_calculate.set_defaults(func=restaurants_online_order_service_fees_cmd.cmd_restaurants_online_order_service_fees_calculate, write_capable=False)

    restaurants_online_order_service_fees_list = restaurants_online_order_service_fees_sub.add_parser("list", help="List service fee rules")
    restaurants_online_order_service_fees_list.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    restaurants_online_order_service_fees_list.set_defaults(func=restaurants_online_order_service_fees_cmd.cmd_restaurants_online_order_service_fees_list, write_capable=False)

    restaurants_online_order_service_fees_get = restaurants_online_order_service_fees_sub.add_parser("get", help="Get one service fee rule")
    restaurants_online_order_service_fees_get.add_argument("--rule-id", required=True, dest="rule_id", help="Rule ID")
    restaurants_online_order_service_fees_get.set_defaults(func=restaurants_online_order_service_fees_cmd.cmd_restaurants_online_order_service_fees_get, write_capable=False)

    restaurants_online_order_service_fees_query = restaurants_online_order_service_fees_sub.add_parser("query", help="Query service fee rules")
    restaurants_online_order_service_fees_query.add_argument("--query-json", default="{}", dest="query_json", help="JSON query body or @file")
    restaurants_online_order_service_fees_query.set_defaults(func=restaurants_online_order_service_fees_cmd.cmd_restaurants_online_order_service_fees_query, write_capable=False)

    restaurants_online_order_service_fees_create = restaurants_online_order_service_fees_sub.add_parser("create", help="Create one service fee rule")
    restaurants_online_order_service_fees_create.add_argument("--rule-json", required=True, dest="rule_json", help="JSON rule create body or @file")
    restaurants_online_order_service_fees_create.set_defaults(func=restaurants_online_order_service_fees_cmd.cmd_restaurants_online_order_service_fees_create, write_capable=True)

    restaurants_online_order_service_fees_bulk_create = restaurants_online_order_service_fees_sub.add_parser("bulk-create", help="Create service fee rules in bulk")
    restaurants_online_order_service_fees_bulk_create.add_argument("--rules-json", required=True, dest="rules_json", help="JSON bulk create body or @file")
    restaurants_online_order_service_fees_bulk_create.set_defaults(func=restaurants_online_order_service_fees_cmd.cmd_restaurants_online_order_service_fees_bulk_create, write_capable=True)

    restaurants_online_order_service_fees_update = restaurants_online_order_service_fees_sub.add_parser("update", help="Update one service fee rule")
    restaurants_online_order_service_fees_update.add_argument("--rule-id", required=True, dest="rule_id", help="Rule ID")
    restaurants_online_order_service_fees_update.add_argument("--rule-json", required=True, dest="rule_json", help="JSON rule update body with rule.revision or @file")
    restaurants_online_order_service_fees_update.set_defaults(func=restaurants_online_order_service_fees_cmd.cmd_restaurants_online_order_service_fees_update, write_capable=True)

    restaurants_online_order_service_fees_bulk_update = restaurants_online_order_service_fees_sub.add_parser("bulk-update", help="Update service fee rules in bulk")
    restaurants_online_order_service_fees_bulk_update.add_argument("--rules-json", required=True, dest="rules_json", help="JSON bulk update body with rules revisions or @file")
    restaurants_online_order_service_fees_bulk_update.set_defaults(func=restaurants_online_order_service_fees_cmd.cmd_restaurants_online_order_service_fees_bulk_update, write_capable=True)

    restaurants_online_order_service_fees_delete = restaurants_online_order_service_fees_sub.add_parser("delete", help="Delete one service fee rule")
    restaurants_online_order_service_fees_delete.add_argument("--rule-id", required=True, dest="rule_id", help="Rule ID")
    restaurants_online_order_service_fees_delete.set_defaults(func=restaurants_online_order_service_fees_cmd.cmd_restaurants_online_order_service_fees_delete, write_capable=True)

    restaurants_online_order_service_fees_bulk_delete = restaurants_online_order_service_fees_sub.add_parser("bulk-delete", help="Delete service fee rules in bulk")
    restaurants_online_order_service_fees_bulk_delete.add_argument("--rules-json", required=True, dest="rules_json", help="JSON bulk delete body or @file")
    restaurants_online_order_service_fees_bulk_delete.set_defaults(func=restaurants_online_order_service_fees_cmd.cmd_restaurants_online_order_service_fees_bulk_delete, write_capable=True)

    restaurants_online_order_service_fees_bulk_update_tags = restaurants_online_order_service_fees_sub.add_parser("bulk-update-tags", help="Update tags on service fee rules")
    restaurants_online_order_service_fees_bulk_update_tags.add_argument("--tags-json", required=True, dest="tags_json", help="JSON tags body with ids/ruleIds and assignTags/unassignTags arrays or @file")
    restaurants_online_order_service_fees_bulk_update_tags.set_defaults(func=restaurants_online_order_service_fees_cmd.cmd_restaurants_online_order_service_fees_bulk_update_tags, write_capable=True)

    restaurants_online_order_service_fees_bulk_update_tags_by_filter = restaurants_online_order_service_fees_sub.add_parser("bulk-update-tags-by-filter", help="Update tags on service fee rules by filter")
    restaurants_online_order_service_fees_bulk_update_tags_by_filter.add_argument("--filter-json", required=True, dest="filter_json", help="JSON filter tags body or @file")
    restaurants_online_order_service_fees_bulk_update_tags_by_filter.set_defaults(func=restaurants_online_order_service_fees_cmd.cmd_restaurants_online_order_service_fees_bulk_update_tags_by_filter, write_capable=True)

    restaurants_online_order_notification_recipients = sub.add_parser("restaurants-online-order-notification-recipients", help="Read and manage Wix Restaurants Online Orders notification recipients")
    restaurants_online_order_notification_recipients_sub = restaurants_online_order_notification_recipients.add_subparsers(dest="restaurants_online_order_notification_recipients_cmd", required=True, parser_class=_ToolArgumentParser)

    restaurants_online_order_notification_recipients_get = restaurants_online_order_notification_recipients_sub.add_parser("get", help="Get one restaurant notification recipient")
    restaurants_online_order_notification_recipients_get.add_argument("--recipient-id", required=True, dest="recipient_id", help="Recipient ID")
    restaurants_online_order_notification_recipients_get.set_defaults(func=restaurants_online_order_notification_recipients_cmd.cmd_restaurants_online_order_notification_recipients_get, write_capable=False)

    restaurants_online_order_notification_recipients_query = restaurants_online_order_notification_recipients_sub.add_parser("query", help="Query restaurant notification recipients")
    restaurants_online_order_notification_recipients_query.add_argument("--query-json", default="{}", dest="query_json", help="JSON query body or @file")
    restaurants_online_order_notification_recipients_query.set_defaults(func=restaurants_online_order_notification_recipients_cmd.cmd_restaurants_online_order_notification_recipients_query, write_capable=False)

    restaurants_online_order_notification_recipients_create = restaurants_online_order_notification_recipients_sub.add_parser("create", help="Create one restaurant notification recipient")
    restaurants_online_order_notification_recipients_create.add_argument("--recipient-json", required=True, dest="recipient_json", help="JSON recipient create body or @file")
    restaurants_online_order_notification_recipients_create.set_defaults(func=restaurants_online_order_notification_recipients_cmd.cmd_restaurants_online_order_notification_recipients_create, write_capable=True)

    restaurants_online_order_notification_recipients_bulk_create = restaurants_online_order_notification_recipients_sub.add_parser("bulk-create", help="Create restaurant notification recipients in bulk")
    restaurants_online_order_notification_recipients_bulk_create.add_argument("--recipients-json", required=True, dest="recipients_json", help="JSON bulk create body or @file")
    restaurants_online_order_notification_recipients_bulk_create.set_defaults(func=restaurants_online_order_notification_recipients_cmd.cmd_restaurants_online_order_notification_recipients_bulk_create, write_capable=True)

    restaurants_online_order_notification_recipients_update = restaurants_online_order_notification_recipients_sub.add_parser("update", help="Update one restaurant notification recipient")
    restaurants_online_order_notification_recipients_update.add_argument("--recipient-id", required=True, dest="recipient_id", help="Recipient ID")
    restaurants_online_order_notification_recipients_update.add_argument("--recipient-json", required=True, dest="recipient_json", help="JSON recipient update body with recipient.revision or @file")
    restaurants_online_order_notification_recipients_update.set_defaults(func=restaurants_online_order_notification_recipients_cmd.cmd_restaurants_online_order_notification_recipients_update, write_capable=True)

    restaurants_online_order_notification_recipients_bulk_update = restaurants_online_order_notification_recipients_sub.add_parser("bulk-update", help="Update restaurant notification recipients in bulk")
    restaurants_online_order_notification_recipients_bulk_update.add_argument("--recipients-json", required=True, dest="recipients_json", help="JSON bulk update body with recipients revisions or @file")
    restaurants_online_order_notification_recipients_bulk_update.set_defaults(func=restaurants_online_order_notification_recipients_cmd.cmd_restaurants_online_order_notification_recipients_bulk_update, write_capable=True)

    restaurants_online_order_notification_recipients_delete = restaurants_online_order_notification_recipients_sub.add_parser("delete", help="Delete one restaurant notification recipient")
    restaurants_online_order_notification_recipients_delete.add_argument("--recipient-id", required=True, dest="recipient_id", help="Recipient ID")
    restaurants_online_order_notification_recipients_delete.set_defaults(func=restaurants_online_order_notification_recipients_cmd.cmd_restaurants_online_order_notification_recipients_delete, write_capable=True)

    restaurants_online_order_notification_recipients_bulk_delete = restaurants_online_order_notification_recipients_sub.add_parser("bulk-delete", help="Delete restaurant notification recipients in bulk")
    restaurants_online_order_notification_recipients_bulk_delete.add_argument("--recipients-json", required=True, dest="recipients_json", help="JSON bulk delete body or @file")
    restaurants_online_order_notification_recipients_bulk_delete.set_defaults(func=restaurants_online_order_notification_recipients_cmd.cmd_restaurants_online_order_notification_recipients_bulk_delete, write_capable=True)

    restaurants_online_order_notification_recipients_bulk_update_tags = restaurants_online_order_notification_recipients_sub.add_parser("bulk-update-tags", help="Update tags on restaurant notification recipients")
    restaurants_online_order_notification_recipients_bulk_update_tags.add_argument("--tags-json", required=True, dest="tags_json", help="JSON tags body with ids/recipientIds and assignTags/unassignTags arrays or @file")
    restaurants_online_order_notification_recipients_bulk_update_tags.set_defaults(func=restaurants_online_order_notification_recipients_cmd.cmd_restaurants_online_order_notification_recipients_bulk_update_tags, write_capable=True)

    restaurants_online_order_notification_recipients_bulk_update_tags_by_filter = restaurants_online_order_notification_recipients_sub.add_parser("bulk-update-tags-by-filter", help="Update tags on restaurant notification recipients by filter")
    restaurants_online_order_notification_recipients_bulk_update_tags_by_filter.add_argument("--filter-json", required=True, dest="filter_json", help="JSON filter tags body or @file")
    restaurants_online_order_notification_recipients_bulk_update_tags_by_filter.set_defaults(func=restaurants_online_order_notification_recipients_cmd.cmd_restaurants_online_order_notification_recipients_bulk_update_tags_by_filter, write_capable=True)

    restaurants_reservations = sub.add_parser("restaurants-reservations", help="Read and manage Wix Restaurants Reservations")
    restaurants_reservations_sub = restaurants_reservations.add_subparsers(dest="restaurants_reservations_cmd", required=True, parser_class=_ToolArgumentParser)

    restaurants_reservations_create = restaurants_reservations_sub.add_parser("create", help="Create one restaurant reservation")
    restaurants_reservations_create.add_argument("--reservation-json", required=True, dest="reservation_json", help="JSON reservation create body or @file")
    restaurants_reservations_create.set_defaults(func=restaurants_reservations_cmd.cmd_restaurants_reservations_create, write_capable=True)

    restaurants_reservations_get = restaurants_reservations_sub.add_parser("get", help="Get one restaurant reservation")
    restaurants_reservations_get.add_argument("--reservation-id", required=True, dest="reservation_id", help="Reservation ID")
    restaurants_reservations_get.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON, including fieldsets, or @file")
    restaurants_reservations_get.set_defaults(func=restaurants_reservations_cmd.cmd_restaurants_reservations_get, write_capable=False)

    restaurants_reservations_update = restaurants_reservations_sub.add_parser("update", help="Update one restaurant reservation")
    restaurants_reservations_update.add_argument("--reservation-id", required=True, dest="reservation_id", help="Reservation ID")
    restaurants_reservations_update.add_argument("--reservation-json", required=True, dest="reservation_json", help="JSON reservation update body with reservation.revision or @file")
    restaurants_reservations_update.set_defaults(func=restaurants_reservations_cmd.cmd_restaurants_reservations_update, write_capable=True)

    restaurants_reservations_delete = restaurants_reservations_sub.add_parser("delete", help="Delete one held restaurant reservation")
    restaurants_reservations_delete.add_argument("--reservation-id", required=True, dest="reservation_id", help="Reservation ID")
    restaurants_reservations_delete.set_defaults(func=restaurants_reservations_cmd.cmd_restaurants_reservations_delete, write_capable=True)

    restaurants_reservations_query = restaurants_reservations_sub.add_parser("query", help="Query restaurant reservations")
    restaurants_reservations_query.add_argument("--query-json", default="{}", dest="query_json", help="JSON query body or @file")
    restaurants_reservations_query.set_defaults(func=restaurants_reservations_cmd.cmd_restaurants_reservations_query, write_capable=False)

    restaurants_reservations_list = restaurants_reservations_sub.add_parser("list", help="List restaurant reservations")
    restaurants_reservations_list.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    restaurants_reservations_list.set_defaults(func=restaurants_reservations_cmd.cmd_restaurants_reservations_list, write_capable=False)

    restaurants_reservations_search = restaurants_reservations_sub.add_parser("search", help="Search restaurant reservations")
    restaurants_reservations_search.add_argument("--search-json", default="{}", dest="search_json", help="JSON search body or @file")
    restaurants_reservations_search.set_defaults(func=restaurants_reservations_cmd.cmd_restaurants_reservations_search, write_capable=False)

    restaurants_reservations_bulk_archive = restaurants_reservations_sub.add_parser("bulk-archive", help="Archive restaurant reservations in bulk")
    restaurants_reservations_bulk_archive.add_argument("--reservations-json", required=True, dest="reservations_json", help="JSON bulk archive body or @file")
    restaurants_reservations_bulk_archive.set_defaults(func=restaurants_reservations_cmd.cmd_restaurants_reservations_bulk_archive, write_capable=True)

    restaurants_reservations_bulk_unarchive = restaurants_reservations_sub.add_parser("bulk-unarchive", help="Unarchive restaurant reservations in bulk")
    restaurants_reservations_bulk_unarchive.add_argument("--reservations-json", required=True, dest="reservations_json", help="JSON bulk unarchive body or @file")
    restaurants_reservations_bulk_unarchive.set_defaults(func=restaurants_reservations_cmd.cmd_restaurants_reservations_bulk_unarchive, write_capable=True)

    restaurants_reservations_cancel = restaurants_reservations_sub.add_parser("cancel", help="Cancel one restaurant reservation")
    restaurants_reservations_cancel.add_argument("--reservation-id", required=True, dest="reservation_id", help="Reservation ID")
    restaurants_reservations_cancel.add_argument("--request-json", default="{}", dest="request_json", help="Optional cancel body JSON or @file")
    restaurants_reservations_cancel.set_defaults(func=restaurants_reservations_cmd.cmd_restaurants_reservations_cancel, write_capable=True)

    restaurants_reservations_create_held = restaurants_reservations_sub.add_parser("create-held", help="Create one held restaurant reservation")
    restaurants_reservations_create_held.add_argument("--reservation-json", required=True, dest="reservation_json", help="JSON held reservation body or @file")
    restaurants_reservations_create_held.set_defaults(func=restaurants_reservations_cmd.cmd_restaurants_reservations_create_held, write_capable=True)

    restaurants_reservations_reserve = restaurants_reservations_sub.add_parser("reserve", help="Reserve one held restaurant reservation")
    restaurants_reservations_reserve.add_argument("--reservation-id", required=True, dest="reservation_id", help="Reservation ID")
    restaurants_reservations_reserve.add_argument("--request-json", default="{}", dest="request_json", help="Optional reserve body JSON or @file")
    restaurants_reservations_reserve.set_defaults(func=restaurants_reservations_cmd.cmd_restaurants_reservations_reserve, write_capable=True)

    restaurants_reservation_locations = sub.add_parser("restaurants-reservation-locations", help="Read and update Wix Restaurants Reservation Locations")
    restaurants_reservation_locations_sub = restaurants_reservation_locations.add_subparsers(dest="restaurants_reservation_locations_cmd", required=True, parser_class=_ToolArgumentParser)

    restaurants_reservation_locations_get = restaurants_reservation_locations_sub.add_parser("get", help="Get one restaurant reservation location")
    restaurants_reservation_locations_get.add_argument("--reservation-location-id", required=True, dest="reservation_location_id", help="Reservation location ID")
    restaurants_reservation_locations_get.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    restaurants_reservation_locations_get.set_defaults(func=restaurants_reservation_locations_cmd.cmd_restaurants_reservation_locations_get, write_capable=False)

    restaurants_reservation_locations_update = restaurants_reservation_locations_sub.add_parser("update", help="Update one restaurant reservation location")
    restaurants_reservation_locations_update.add_argument("--reservation-location-id", required=True, dest="reservation_location_id", help="Reservation location ID")
    restaurants_reservation_locations_update.add_argument("--reservation-location-json", required=True, dest="reservation_location_json", help="JSON reservation location update body with reservationLocation.revision or @file")
    restaurants_reservation_locations_update.set_defaults(func=restaurants_reservation_locations_cmd.cmd_restaurants_reservation_locations_update, write_capable=True)

    restaurants_reservation_locations_query = restaurants_reservation_locations_sub.add_parser("query", help="Query restaurant reservation locations")
    restaurants_reservation_locations_query.add_argument("--query-json", default="{}", dest="query_json", help="JSON query body or @file")
    restaurants_reservation_locations_query.set_defaults(func=restaurants_reservation_locations_cmd.cmd_restaurants_reservation_locations_query, write_capable=False)

    restaurants_reservation_locations_list = restaurants_reservation_locations_sub.add_parser("list", help="List restaurant reservation locations")
    restaurants_reservation_locations_list.add_argument("--params-json", default="{}", dest="params_json", help="Optional query params JSON or @file")
    restaurants_reservation_locations_list.set_defaults(func=restaurants_reservation_locations_cmd.cmd_restaurants_reservation_locations_list, write_capable=False)

    site_plugins = sub.add_parser("site-plugins", help="Read-only site plugin status methods")
    site_plugins_sub = site_plugins.add_subparsers(dest="site_plugins_cmd", required=True, parser_class=_ToolArgumentParser)
    site_plugins_get_placement_status = site_plugins_sub.add_parser(
        "get-placement-status",
        help="Get the current placement status for this app's site plugins",
    )
    site_plugins_get_placement_status.set_defaults(
        func=site_plugins_cmd.cmd_site_plugins_get_placement_status,
        write_capable=False,
    )

    app_permissions = sub.add_parser("app-permissions", help="Read and write Wix app permission grants")
    app_permissions_sub = app_permissions.add_subparsers(dest="app_permissions_cmd", required=True, parser_class=_ToolArgumentParser)

    app_permissions_list = app_permissions_sub.add_parser("list", help="List app permissions for one app")
    app_permissions_list.add_argument("--app-id", required=True, help="Wix app ID")
    app_permissions_list.add_argument(
        "--consistent",
        default=None,
        help="Read from primary DB for latest results: true or false",
    )
    app_permissions_list.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    app_permissions_list.add_argument("--limit", type=int, default=None, help="Max permissions to return")
    app_permissions_list.set_defaults(func=app_permissions_cmd.cmd_app_permissions_list, write_capable=False)

    app_permissions_create = app_permissions_sub.add_parser("create", help="Create one app permission grant")
    app_permissions_create.add_argument(
        "--app-permission-json",
        default=None,
        help="JSON payload for appPermission with appId and permission.permissionId",
    )
    app_permissions_create.add_argument("--app-id", default=None, help="Wix app ID (use without --app-permission-json)")
    app_permissions_create.add_argument(
        "--permission-id",
        default=None,
        help="Permission ID (use without --app-permission-json)",
    )
    app_permissions_create.set_defaults(func=app_permissions_cmd.cmd_app_permissions_create, write_capable=True)

    app_permissions_delete = app_permissions_sub.add_parser("delete", help="Delete one app permission grant")
    app_permissions_delete.add_argument("--app-id", required=True, help="Wix app ID")
    app_permissions_delete.add_argument("--permission-id", required=True, help="Permission ID")
    app_permissions_delete.set_defaults(func=app_permissions_cmd.cmd_app_permissions_delete, write_capable=True)

    ai_credits = sub.add_parser("ai-credits", help="Read-only account-level AI credit balance methods")
    ai_credits_sub = ai_credits.add_subparsers(dest="ai_credits_cmd", required=True, parser_class=_ToolArgumentParser)
    ai_credits_get_balance = ai_credits_sub.add_parser("get-balance", help="Get the current AI credit balance")
    ai_credits_get_balance.set_defaults(func=ai_credits_cmd.cmd_ai_credits_get_balance, write_capable=False)

    analytics_data = sub.add_parser("analytics-data", help="Read-only site analytics data methods")
    analytics_data_sub = analytics_data.add_subparsers(
        dest="analytics_data_cmd", required=True, parser_class=_ToolArgumentParser
    )
    analytics_data_get = analytics_data_sub.add_parser(
        "get", help="Get analytics data by date range and measurement types"
    )
    analytics_data_get.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD")
    analytics_data_get.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD")
    analytics_data_get.add_argument(
        "--measurement-types-json", dest="measurement_types_json", required=True, help="JSON array of measurement types"
    )
    analytics_data_get.add_argument("--time-zone", default=None, help="Optional time zone")
    analytics_data_get.set_defaults(func=analytics_data_cmd.cmd_analytics_data_get, write_capable=False)

    analytics_semantic_models = sub.add_parser(
        "analytics-semantic-models",
        help="Read-only Wix Analytics Semantic Models methods",
    )
    analytics_semantic_models_sub = analytics_semantic_models.add_subparsers(
        dest="analytics_semantic_models_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    analytics_semantic_models_list = analytics_semantic_models_sub.add_parser(
        "list",
        help="List available analytics semantic models",
    )
    analytics_semantic_models_list.set_defaults(
        func=analytics_semantic_models_cmd.cmd_analytics_semantic_models_list,
        write_capable=False,
    )
    analytics_semantic_models_get = analytics_semantic_models_sub.add_parser(
        "get",
        help="Get one analytics semantic model by ID",
    )
    analytics_semantic_models_get.add_argument(
        "--semantic-model-id",
        required=True,
        help="Semantic model ID from list or docs-backed discovery",
    )
    analytics_semantic_models_get.set_defaults(
        func=analytics_semantic_models_cmd.cmd_analytics_semantic_models_get,
        write_capable=False,
    )
    analytics_semantic_models_query = analytics_semantic_models_sub.add_parser(
        "query",
        help="Query semantic model data with an official query JSON object",
    )
    analytics_semantic_models_query.add_argument(
        "--query-json",
        dest="query_json",
        required=True,
        help="Official semantic model query JSON object or @file",
    )
    analytics_semantic_models_query.set_defaults(
        func=analytics_semantic_models_cmd.cmd_analytics_semantic_models_query,
        write_capable=False,
    )

    async_jobs = sub.add_parser("async-jobs", help="Read-only Wix Async Job methods")
    async_jobs_sub = async_jobs.add_subparsers(
        dest="async_jobs_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    async_jobs_get = async_jobs_sub.add_parser(
        "get",
        help="Get one async job by ID",
    )
    async_jobs_get.add_argument("--job-id", required=True, help="Async job ID")
    async_jobs_get.set_defaults(func=async_jobs_cmd.cmd_async_jobs_get, write_capable=False)
    async_jobs_list_items = async_jobs_sub.add_parser(
        "list-items",
        help="List the items for one async job",
    )
    async_jobs_list_items.add_argument("--job-id", required=True, help="Async job ID")
    async_jobs_list_items.set_defaults(func=async_jobs_cmd.cmd_async_jobs_list_items, write_capable=False)

    payments = sub.add_parser("payments", help="Read-only Wix Payments methods")
    payments_sub = payments.add_subparsers(
        dest="payments_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    payments_transactions_list = payments_sub.add_parser(
        "transactions-list",
        help="List payment transactions with official Wix query filters",
    )
    payments_transactions_list.add_argument("--from-created", default=None, help="Only transactions created after this ISO timestamp")
    payments_transactions_list.add_argument("--to-created", default=None, help="Only transactions created before this ISO timestamp")
    payments_transactions_list.add_argument("--limit", type=int, default=None, help="Maximum transactions to retrieve, up to 1000")
    payments_transactions_list.add_argument("--offset", type=int, default=None, help="Result offset")
    payments_transactions_list.add_argument("--order", choices=["date:asc", "date:desc"], default=None, help="Sort by created date")
    payments_transactions_list.add_argument("--status", action="append", default=None, help="Transaction status filter; repeat for more than one")
    payments_transactions_list.add_argument("--payment-method", default=None, help="Transaction payment method filter")
    payments_transactions_list.add_argument("--payment-provider", default=None, help="Transaction payment provider filter")
    payments_transactions_list.add_argument("--currency", default=None, help="Deprecated Wix currency filter")
    payments_transactions_list.add_argument("--from-updated", default=None, help="Only transactions updated after this ISO timestamp")
    payments_transactions_list.add_argument("--to-updated", default=None, help="Only transactions updated before this ISO timestamp")
    payments_transactions_list.add_argument("--app-id", default=None, help="Deprecated Wix app ID filter")
    payments_transactions_list.add_argument("--include-refunds", action="store_true", default=None, help="Include refunds in transaction objects")
    payments_transactions_list.add_argument("--ignore-totals", action="store_true", default=None, help="Omit pagination total when Wix supports it")
    payments_transactions_list.set_defaults(func=payments_cmd.cmd_payments_transactions_list, write_capable=False)

    branches = sub.add_parser("branches", help="Read-only Wix Branches methods")
    branches_sub = branches.add_subparsers(
        dest="branches_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    branches_get_default = branches_sub.add_parser(
        "get-default",
        help="Get the default branch",
    )
    branches_get_default.set_defaults(func=branches_cmd.cmd_branches_get_default, write_capable=False)
    branches_get = branches_sub.add_parser(
        "get",
        help="Get one branch by ID",
    )
    branches_get.add_argument("--branch-id", required=True, help="Branch ID")
    branches_get.set_defaults(func=branches_cmd.cmd_branches_get, write_capable=False)
    branches_query = branches_sub.add_parser(
        "query",
        help="Query branches with an official query JSON object",
    )
    branches_query.add_argument(
        "--query-json",
        dest="query_json",
        required=True,
        help="Official branches query JSON object or @file",
    )
    branches_query.set_defaults(func=branches_cmd.cmd_branches_query, write_capable=False)

    site_search = sub.add_parser("site-search", help="Read-only Wix Site Search methods")
    site_search_sub = site_search.add_subparsers(dest="site_search_cmd", required=True, parser_class=_ToolArgumentParser)
    site_search_search = site_search_sub.add_parser(
        "search",
        help="Search one official Wix Site Search document type with an explicit search JSON object",
    )
    site_search_search.add_argument(
        "--document-type",
        required=True,
        help="One of BLOG_POSTS, BOOKING_SERVICES, EVENTS, FORUM_CONTENT, ONLINE_PROGRAMS, PROGALLERY_ITEM, STORES_PRODUCTS",
    )
    site_search_search.add_argument("--search-json", required=True, dest="search_json", help="Official search JSON object")
    site_search_search.add_argument("--language", default=None, help="Optional language code")
    site_search_search.set_defaults(func=site_search_cmd.cmd_site_search_search, write_capable=False)

    domains = sub.add_parser("domains", help="Read-only domain-search methods")
    domains_sub = domains.add_subparsers(dest="domains_cmd", required=True, parser_class=_ToolArgumentParser)

    domains_check_availability = domains_sub.add_parser("check-availability", help="Check one domain for availability")
    domains_check_availability.add_argument("--domain", required=True, help="Full domain to check (must include a TLD)")
    domains_check_availability.set_defaults(func=domains_cmd.cmd_domains_check_availability, write_capable=False)

    domains_suggest = domains_sub.add_parser("suggest", help="Get domain suggestions from an input query")
    domains_suggest.add_argument("--query", required=True, help="Search query for suggestions")
    domains_suggest.add_argument("--tlds-json", dest="tlds_json", help="JSON array of TLD values (max 10, no leading dots)")
    domains_suggest.add_argument("--paging-limit", type=int, default=None, help="Results limit (1-20)")
    domains_suggest.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    domains_suggest.add_argument("--max-length", type=int, default=None, help="Max domain length (3-63)")
    domains_suggest.set_defaults(func=domains_cmd.cmd_domains_suggest, write_capable=False)

    domain_dns = sub.add_parser("domain-dns", help="DNS zone read and write methods")
    domain_dns_sub = domain_dns.add_subparsers(dest="domain_dns_cmd", required=True, parser_class=_ToolArgumentParser)

    domain_dns_get_zone = domain_dns_sub.add_parser("get-zone", help="Get one DNS zone")
    domain_dns_get_zone.add_argument("--domain-name", required=True, help="Hostname with TLD (root domain or subdomain)")
    domain_dns_get_zone.set_defaults(func=domain_dns_cmd.cmd_domain_dns_get_zone, write_capable=False)

    domain_dns_preview_zone = domain_dns_sub.add_parser("preview-zone", help="Preview one DNS zone")
    domain_dns_preview_zone.add_argument("--domain-name", required=True, help="Hostname with TLD (root domain or subdomain)")
    domain_dns_preview_zone.set_defaults(func=domain_dns_cmd.cmd_domain_dns_preview_zone, write_capable=False)

    domain_dns_create_zone = domain_dns_sub.add_parser(
        "create-zone",
        help="Create one DNS zone from an official dnsZone JSON object",
    )
    domain_dns_create_zone.add_argument(
        "--dns-zone-json",
        required=True,
        help="JSON object for the official dnsZone request body",
    )
    domain_dns_create_zone.set_defaults(func=domain_dns_cmd.cmd_domain_dns_create_zone, write_capable=True)

    domain_dns_update_zone = domain_dns_sub.add_parser(
        "update-zone",
        help="Update one DNS zone with additions, deletions, or dnssecEnabled",
    )
    domain_dns_update_zone.add_argument("--domain-name", required=True, help="Hostname with TLD (root domain or subdomain)")
    domain_dns_update_zone.add_argument("--additions-json", help="JSON array of DNS record objects to add")
    domain_dns_update_zone.add_argument("--deletions-json", help="JSON array of DNS record objects to remove")
    domain_dns_update_zone.add_argument("--dnssec-enabled", help="Optional true/false value for dnssecEnabled")
    domain_dns_update_zone.set_defaults(func=domain_dns_cmd.cmd_domain_dns_update_zone, write_capable=True)

    domain_dns_delete_zone = domain_dns_sub.add_parser("delete-zone", help="Delete one DNS zone")
    domain_dns_delete_zone.add_argument("--domain-name", required=True, help="Hostname with TLD (root domain or subdomain)")
    domain_dns_delete_zone.set_defaults(func=domain_dns_cmd.cmd_domain_dns_delete_zone, write_capable=True)

    dns_propagation = sub.add_parser("dns-propagation", help="DNS propagation status methods")
    dns_propagation_sub = dns_propagation.add_subparsers(
        dest="dns_propagation_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    dns_propagation_get = dns_propagation_sub.add_parser("get", help="Get DNS propagation for one domain")
    dns_propagation_get.add_argument(
        "--dns-propagation-id",
        required=True,
        help="DNS propagation ID from Wix docs. In practice this is the domain name including the TLD.",
    )
    dns_propagation_get.set_defaults(func=dns_propagation_cmd.cmd_dns_propagation_get, write_capable=False)

    connected_domains = sub.add_parser("connected-domains", help="Connected domain read and write methods")
    connected_domains_sub = connected_domains.add_subparsers(dest="connected_domains_cmd", required=True, parser_class=_ToolArgumentParser)

    connected_domains_list = connected_domains_sub.add_parser("list", help="List connected domains")
    connected_domains_list.add_argument("--limit", type=int, default=None, help="Results limit (1-100)")
    connected_domains_list.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    connected_domains_list.set_defaults(func=connected_domains_cmd.cmd_connected_domains_list, write_capable=False)

    connected_domains_get = connected_domains_sub.add_parser("get", help="Get one connected domain")
    connected_domains_get.add_argument("--connected-domain-id", required=True, help="Connected domain ID (must include a TLD)")
    connected_domains_get.set_defaults(func=connected_domains_cmd.cmd_connected_domains_get, write_capable=False)

    connected_domains_get_setup_info = connected_domains_sub.add_parser(
        "get-setup-info",
        help="Get setup info for one connected domain",
    )
    connected_domains_get_setup_info.add_argument(
        "--connected-domain-id", required=True, help="Connected domain ID (must include a TLD)"
    )
    connected_domains_get_setup_info.set_defaults(
        func=connected_domains_cmd.cmd_connected_domains_get_setup_info, write_capable=False
    )

    connected_domains_create = connected_domains_sub.add_parser("create", help="Create one connected domain")
    connected_domains_create.add_argument("--domain", required=True, help="External domain to connect (must include a TLD)")
    connected_domains_create.add_argument("--site-id", required=True, help="Target Wix site ID for this tool's deterministic create flow")
    connected_domains_create.add_argument(
        "--connection-type",
        choices=("POINTING", "NAMESERVERS", "HIDDEN"),
        default=None,
        help="Optional connection type",
    )
    connected_domains_create.add_argument(
        "--assignment-type",
        choices=("PRIMARY", "REDIRECT"),
        default=None,
        help="Optional domain assignment type",
    )
    connected_domains_create.add_argument(
        "--suppress-notifications",
        action="store_true",
        help="Suppress standard Wix connected-domain email notifications",
    )
    connected_domains_create.set_defaults(func=connected_domains_cmd.cmd_connected_domains_create, write_capable=True)

    connected_domains_delete = connected_domains_sub.add_parser("delete", help="Delete one connected domain")
    connected_domains_delete.add_argument(
        "--connected-domain-id", required=True, help="Connected domain ID (must include a TLD)"
    )
    connected_domains_delete.set_defaults(func=connected_domains_cmd.cmd_connected_domains_delete, write_capable=True)

    files = sub.add_parser("files", help="Read and manage Media Manager files")
    files_sub = files.add_subparsers(dest="files_cmd", required=True, parser_class=_ToolArgumentParser)
    files_list = files_sub.add_parser("list", help="List media files")
    files_list.add_argument("--parent-folder-id", default=None, help="Parent folder ID (default: media-root)")
    files_list.add_argument("--media-types-json", dest="media_types_json", help="JSON array of media types")
    files_list.add_argument(
        "--private",
        type=str.lower,
        choices=("true", "false"),
        help="Whether to return only private or only public files",
    )
    files_list.add_argument("--sort-json", dest="sort_json", help="JSON object/list for sort fields")
    files_list.set_defaults(func=files_cmd.cmd_files_list, write_capable=False)

    files_get = files_sub.add_parser("get", help="Get one media file by id or URL")
    files_get.add_argument("--file-id", required=True, help="File ID or Wix media URL")
    files_get.set_defaults(func=files_cmd.cmd_files_get, write_capable=False)

    files_batch_get = files_sub.add_parser("batch-get", help="Get multiple media files by id or URL")
    files_batch_get.add_argument("--file-ids-json", required=True, dest="file_ids_json", help="JSON array of file IDs or URLs (max 100)")
    files_batch_get.set_defaults(func=files_cmd.cmd_files_batch_get, write_capable=False)

    files_search = files_sub.add_parser("search", help="Search media files")
    files_search.add_argument("--search", default=None, help="Free-text search across display name, MIME type, and labels")
    files_search.add_argument("--media-types-json", dest="media_types_json", help="JSON array of media types")
    files_search.add_argument(
        "--private",
        type=str.lower,
        choices=("true", "false"),
        help="Whether to return only private or only public files",
    )
    files_search.add_argument("--root-folder", default="MEDIA_ROOT", help="Root folder for search")
    files_search.add_argument("--sort-json", dest="sort_json", help="JSON object for sort fields")
    files_search.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    files_search.add_argument("--limit", type=int, default=None, help="Max files to return")
    files_search.set_defaults(func=files_cmd.cmd_files_search, write_capable=False)

    files_query = files_sub.add_parser("query", help="Query media files with Wix query payload")
    files_query.add_argument("--query-json", required=False, dest="query_json", help="JSON payload for file query")
    files_query.set_defaults(func=files_cmd.cmd_files_query, write_capable=False)

    files_list_deleted = files_sub.add_parser("list-deleted", help="List files in the Media Manager trash bin")
    files_list_deleted.add_argument("--parent-folder-id", default="media-root", help="Parent folder ID in the trash bin (default: media-root)")
    files_list_deleted.add_argument("--media-types-json", dest="media_types_json", help="JSON array of media types")
    files_list_deleted.add_argument(
        "--private",
        type=str.lower,
        choices=("true", "false"),
        help="Whether to return only private or only public files",
    )
    files_list_deleted.add_argument("--sort-json", dest="sort_json", help="JSON object/list for sort fields")
    files_list_deleted.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    files_list_deleted.set_defaults(func=files_cmd.cmd_files_list_deleted, write_capable=False)

    files_update = files_sub.add_parser("update", help="Update one media file descriptor")
    files_update.add_argument("--file-id", required=True, help="File ID or Wix media URL")
    files_update.add_argument(
        "--file-json",
        required=True,
        dest="file_json",
        help="JSON object with the official update-file-descriptor fields",
    )
    files_update.set_defaults(func=files_cmd.cmd_files_update, write_capable=True)

    files_bulk_delete = files_sub.add_parser("bulk-delete", help="Delete up to 1000 media files")
    files_bulk_delete.add_argument(
        "--file-ids-json",
        required=True,
        dest="file_ids_json",
        help="JSON array of file IDs or Wix media URLs (max 1000)",
    )
    files_bulk_delete.add_argument(
        "--permanent",
        type=str.lower,
        default="false",
        choices=("true", "false"),
        help="If true, delete files permanently",
    )
    files_bulk_delete.set_defaults(func=files_cmd.cmd_files_bulk_delete, write_capable=True)

    files_bulk_restore = files_sub.add_parser("bulk-restore", help="Restore deleted media files")
    files_bulk_restore.add_argument(
        "--file-ids-json",
        required=True,
        dest="file_ids_json",
        help="JSON array of file IDs or Wix media URLs (max 1000)",
    )
    files_bulk_restore.set_defaults(func=files_cmd.cmd_files_bulk_restore, write_capable=True)

    files_generate_upload_url = files_sub.add_parser(
        "generate-upload-url", help="Generate one Media Manager upload URL"
    )
    files_generate_upload_url.add_argument(
        "--upload-json",
        required=True,
        dest="upload_json",
        help="JSON object for the official generate-upload-url request",
    )
    files_generate_upload_url.set_defaults(func=files_cmd.cmd_files_generate_upload_url, write_capable=False)

    files_generate_resumable_upload_url = files_sub.add_parser(
        "generate-resumable-upload-url", help="Generate one resumable Media Manager upload URL"
    )
    files_generate_resumable_upload_url.add_argument(
        "--upload-json",
        required=True,
        dest="upload_json",
        help="JSON object for the official generate-resumable-upload-url request",
    )
    files_generate_resumable_upload_url.set_defaults(
        func=files_cmd.cmd_files_generate_resumable_upload_url, write_capable=False
    )

    files_import = files_sub.add_parser("import", help="Import one external file into Media Manager")
    files_import.add_argument(
        "--import-json",
        required=True,
        dest="import_json",
        help="JSON object for the official import-file request",
    )
    files_import.set_defaults(func=files_cmd.cmd_files_import, write_capable=True)

    files_generate_download_url = files_sub.add_parser(
        "generate-download-url", help="Generate one Media Manager file download URL"
    )
    files_generate_download_url.add_argument(
        "--download-json",
        required=True,
        dest="download_json",
        help="JSON object for the official generate-file-download-url request",
    )
    files_generate_download_url.set_defaults(func=files_cmd.cmd_files_generate_download_url, write_capable=False)

    form_submissions = sub.add_parser("form-submissions", help="Wix form submission methods")
    form_submissions_sub = form_submissions.add_subparsers(
        dest="form_submissions_cmd", required=True, parser_class=_ToolArgumentParser
    )
    form_submissions_get_submission = form_submissions_sub.add_parser("get-submission", help="Get one form submission")
    form_submissions_get_submission.add_argument("--submission-id", required=True, help="Submission ID")
    form_submissions_get_submission.set_defaults(
        func=form_submissions_cmd.cmd_form_submissions_get_submission, write_capable=False
    )

    form_submissions_query_submissions_by_namespace = form_submissions_sub.add_parser(
        "query-submissions-by-namespace", help="Query submissions by namespace"
    )
    form_submissions_query_submissions_by_namespace.add_argument(
        "--query-json",
        required=True,
        dest="query_json",
        help="JSON query payload (must include namespace in query scope)",
    )
    form_submissions_query_submissions_by_namespace.add_argument(
        "--only-your-own",
        default=None,
        type=str.lower,
        choices=("true", "false"),
        help="Filter to current user's own submissions",
    )
    form_submissions_query_submissions_by_namespace.set_defaults(
        func=form_submissions_cmd.cmd_form_submissions_query_submissions_by_namespace, write_capable=False
    )

    form_submissions_count_submissions = form_submissions_sub.add_parser("count-submissions", help="Count form submissions")
    form_submissions_count_submissions.add_argument(
        "--form-ids-json",
        required=True,
        dest="form_ids_json",
        help="JSON array of form IDs (1-100)",
    )
    form_submissions_count_submissions.add_argument(
        "--namespace", required=True, help="Submission namespace (required)"
    )
    form_submissions_count_submissions.add_argument(
        "--statuses-json",
        dest="statuses_json",
        help="Optional JSON array of status strings (max 4)",
    )
    form_submissions_count_submissions.set_defaults(func=form_submissions_cmd.cmd_form_submissions_count_submissions, write_capable=False)

    form_submissions_get_media_upload_url = form_submissions_sub.add_parser(
        "get-media-upload-url", help="Get form submission media upload URL"
    )
    form_submissions_get_media_upload_url.add_argument("--form-id", required=True, help="Wix form ID")
    form_submissions_get_media_upload_url.add_argument("--filename", required=True, help="Original file name")
    form_submissions_get_media_upload_url.add_argument("--mime-type", required=True, help="File MIME type")
    form_submissions_get_media_upload_url.set_defaults(
        func=form_submissions_cmd.cmd_form_submissions_get_media_upload_url, write_capable=False
    )

    form_submissions_create_submission = form_submissions_sub.add_parser(
        "create-submission", help="Create a form submission"
    )
    form_submissions_create_submission.add_argument(
        "--submission-json",
        required=True,
        dest="submission_json",
        help="JSON object for the submission body",
    )
    form_submissions_create_submission.set_defaults(
        func=form_submissions_cmd.cmd_form_submissions_create_submission, write_capable=True
    )

    form_submissions_update_submission = form_submissions_sub.add_parser(
        "update-submission", help="Update a form submission"
    )
    form_submissions_update_submission.add_argument(
        "--submission-json",
        required=True,
        dest="submission_json",
        help="JSON object for the full submission body including id, formId, and revision",
    )
    form_submissions_update_submission.set_defaults(
        func=form_submissions_cmd.cmd_form_submissions_update_submission, write_capable=True
    )

    form_submissions_delete_submission = form_submissions_sub.add_parser(
        "delete-submission", help="Delete a form submission"
    )
    form_submissions_delete_submission.add_argument("--submission-id", required=True, help="Submission ID")
    form_submissions_delete_submission.add_argument(
        "--permanent",
        default=None,
        type=str.lower,
        choices=("true", "false"),
        help="Permanently delete and bypass the trash bin",
    )
    form_submissions_delete_submission.add_argument(
        "--preserve-files",
        default=None,
        type=str.lower,
        choices=("true", "false"),
        help="Preserve files associated with the submission",
    )
    form_submissions_delete_submission.set_defaults(
        func=form_submissions_cmd.cmd_form_submissions_delete_submission, write_capable=True
    )

    form_submissions_confirm_submission = form_submissions_sub.add_parser(
        "confirm-submission", help="Confirm a pending form submission"
    )
    form_submissions_confirm_submission.add_argument("--submission-id", required=True, help="Submission ID")
    form_submissions_confirm_submission.set_defaults(
        func=form_submissions_cmd.cmd_form_submissions_confirm_submission, write_capable=True
    )

    form_submissions_bulk_mark_submissions_as_seen = form_submissions_sub.add_parser(
        "bulk-mark-submissions-as-seen", help="Mark submissions as seen"
    )
    form_submissions_bulk_mark_submissions_as_seen.add_argument("--form-id", required=True, help="Wix form ID")
    form_submissions_bulk_mark_submissions_as_seen.add_argument(
        "--ids-json",
        dest="ids_json",
        help="Optional JSON array of submission IDs to mark as seen (max 100)",
    )
    form_submissions_bulk_mark_submissions_as_seen.add_argument(
        "--all-unseen",
        action="store_true",
        help="Allow the empty ids case and mark all unseen submissions for the form",
    )
    form_submissions_bulk_mark_submissions_as_seen.set_defaults(
        func=form_submissions_cmd.cmd_form_submissions_bulk_mark_submissions_as_seen,
        write_capable=True,
    )

    media_folders = sub.add_parser("media-folders", help="Read and write media folder methods")
    media_folders_sub = media_folders.add_subparsers(dest="media_folders_cmd", required=True, parser_class=_ToolArgumentParser)

    media_folders_list = media_folders_sub.add_parser("list", help="List media folders")
    media_folders_list.add_argument("--parent-folder-id", default=None, help="Parent folder ID")
    media_folders_list.add_argument("--cursor", default=None, help="Paging cursor")
    media_folders_list.add_argument("--limit", type=int, default=None, help="Max folders to return")
    media_folders_list.add_argument("--sort-json", dest="sort_json", help="JSON object/list for sort fields")
    media_folders_list.set_defaults(func=media_folders_cmd.cmd_media_folders_list, write_capable=False)

    media_folders_get = media_folders_sub.add_parser("get", help="Get one media folder")
    media_folders_get.add_argument("--folder-id", required=True, help="Folder ID")
    media_folders_get.set_defaults(func=media_folders_cmd.cmd_media_folders_get, write_capable=False)

    media_folders_search = media_folders_sub.add_parser("search", help="Search media folders")
    media_folders_search.add_argument("--search", default=None, help="Search term")
    media_folders_search.add_argument("--root-folder", default="MEDIA_ROOT", help="Root folder enum value")
    media_folders_search.add_argument("--cursor", default=None, help="Paging cursor")
    media_folders_search.add_argument("--limit", type=int, default=None, help="Max folders to return")
    media_folders_search.add_argument("--sort-json", dest="sort_json", help="JSON object for sort fields")
    media_folders_search.set_defaults(func=media_folders_cmd.cmd_media_folders_search, write_capable=False)

    media_folders_query = media_folders_sub.add_parser("query", help="Query media folders")
    media_folders_query.add_argument("--query-json", dest="query_json", help="JSON payload for folder query")
    media_folders_query.add_argument("--sort-json", dest="sort_json", help="JSON sort object/list")
    media_folders_query.add_argument("--limit", type=int, default=None, help="Max folders to return")
    media_folders_query.add_argument("--offset", type=int, default=None, help="Folders to skip in current sort order")
    media_folders_query.set_defaults(func=media_folders_cmd.cmd_media_folders_query, write_capable=False)

    media_folders_list_deleted = media_folders_sub.add_parser("list-deleted", help="List folders in media trash")
    media_folders_list_deleted.add_argument("--parent-folder-id", default=None, help="Trash parent folder ID")
    media_folders_list_deleted.add_argument("--cursor", default=None, help="Paging cursor")
    media_folders_list_deleted.add_argument("--limit", type=int, default=None, help="Max folders to return")
    media_folders_list_deleted.add_argument("--sort-json", dest="sort_json", help="JSON object/list for sort fields")
    media_folders_list_deleted.set_defaults(func=media_folders_cmd.cmd_media_folders_list_deleted, write_capable=False)

    media_folders_create = media_folders_sub.add_parser("create", help="Create one media folder")
    media_folders_create.add_argument("--display-name", required=True, help="Folder display name")
    media_folders_create.add_argument("--parent-folder-id", default=None, help="Optional parent folder ID")
    media_folders_create.set_defaults(func=media_folders_cmd.cmd_media_folders_create, write_capable=True)

    media_folders_update = media_folders_sub.add_parser("update", help="Update a media folder")
    media_folders_update.add_argument("--folder-id", required=True, help="Folder ID")
    media_folders_update.add_argument("--display-name", default=None, help="Optional folder display name")
    media_folders_update.add_argument("--parent-folder-id", default=None, help="Optional parent folder ID")
    media_folders_update.set_defaults(func=media_folders_cmd.cmd_media_folders_update, write_capable=True)

    media_folders_bulk_delete = media_folders_sub.add_parser("bulk-delete", help="Delete up to 100 folders")
    media_folders_bulk_delete.add_argument(
        "--folder-ids-json",
        required=True,
        dest="folder_ids_json",
        help="JSON array of folder IDs (max 100)",
    )
    media_folders_bulk_delete.add_argument(
        "--permanent",
        type=str.lower,
        default="false",
        choices=("true", "false"),
        help="If true, delete folders permanently",
    )
    media_folders_bulk_delete.set_defaults(func=media_folders_cmd.cmd_media_folders_bulk_delete, write_capable=True)

    media_folders_bulk_restore = media_folders_sub.add_parser("bulk-restore", help="Restore deleted folders")
    media_folders_bulk_restore.add_argument(
        "--folder-ids-json",
        required=True,
        dest="folder_ids_json",
        help="JSON array of folder IDs (max 100)",
    )
    media_folders_bulk_restore.set_defaults(func=media_folders_cmd.cmd_media_folders_bulk_restore, write_capable=True)

    media_folders_generate_download_url = media_folders_sub.add_parser(
        "generate-download-url",
        help="Generate a download URL for one folder",
    )
    media_folders_generate_download_url.add_argument("--folder-id", required=True, help="Folder ID")
    media_folders_generate_download_url.set_defaults(
        func=media_folders_cmd.cmd_media_folders_generate_download_url,
        write_capable=False,
    )

    sites = sub.add_parser("sites", help="Read-only account-level site methods")
    sites_sub = sites.add_subparsers(dest="sites_cmd", required=True, parser_class=_ToolArgumentParser)

    sites_query = sites_sub.add_parser("query", help="Query sites with account-level auth")
    sites_query.add_argument("--query-json", dest="query_json", help="JSON query object or full request payload")
    sites_query.add_argument("--filter-json", dest="filter_json", help="JSON filter object")
    sites_query.add_argument("--sort-json", dest="sort_json", help="JSON sort object/list")
    sites_query.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    sites_query.add_argument("--limit", type=int, default=None, help="Max sites to return (1-100)")
    sites_query.set_defaults(func=sites_cmd.cmd_sites_query, write_capable=False)

    sites_count = sites_sub.add_parser("count", help="Count sites with account-level filters")
    sites_count.add_argument("--query-json", dest="query_json", help="JSON request with filter object")
    sites_count.add_argument("--filter-json", dest="filter_json", help="JSON filter object")
    sites_count.set_defaults(func=sites_cmd.cmd_sites_count, write_capable=False)

    projects = sub.add_parser("projects", help="Account-level project methods")
    projects_sub = projects.add_subparsers(dest="projects_cmd", required=True, parser_class=_ToolArgumentParser)

    projects_create = projects_sub.add_parser("create-project", help="Create one Wix project")
    projects_create.add_argument("--type", required=True, help="Project type; WIX only in this slice")
    projects_create.add_argument("--name", default=None, help="Project display name (required in this slice)")
    projects_create.add_argument("--template-id", default=None, help="Optional template ID")
    projects_create.add_argument("--folder-id", default=None, help="Optional folder ID")
    projects_create.add_argument("--apps-json", dest="apps_json", help="JSON array of objects with appDefId")
    projects_create.set_defaults(func=projects_cmd.cmd_projects_create_project, write_capable=True)

    b2b_transfer = sub.add_parser("b2b-site-transfer", help="Account-level B2B site transfer methods")
    b2b_transfer_sub = b2b_transfer.add_subparsers(dest="b2b_site_transfer_cmd", required=True, parser_class=_ToolArgumentParser)
    b2b_transfer_transfer = b2b_transfer_sub.add_parser("transfer", help="Transfer one site to the target account in wix-account-id")
    b2b_transfer_transfer.add_argument("--site-transfer-json", required=True, dest="site_transfer_json", help="JSON siteTransfer object, {siteTransfer:{...}}, or @file")
    b2b_transfer_transfer.set_defaults(func=b2b_site_transfer_cmd.cmd_b2b_site_transfer_transfer, write_capable=True)

    partner_profiles = sub.add_parser("partner-profiles", help="Account-level Partner Profile V1 methods")
    partner_profiles_sub = partner_profiles.add_subparsers(dest="partner_profiles_cmd", required=True, parser_class=_ToolArgumentParser)
    partner_profiles_create = partner_profiles_sub.add_parser("create", help="Create the current partner profile")
    partner_profiles_create.add_argument("--profile-json", required=True, dest="profile_json", help="JSON partnerProfile object, {partnerProfile:{...}}, or @file")
    partner_profiles_create.set_defaults(func=partner_profiles_cmd.cmd_partner_profiles_create, write_capable=True)
    partner_profiles_update = partner_profiles_sub.add_parser("update", help="Update the current partner profile")
    partner_profiles_update.add_argument("--profile-json", required=True, dest="profile_json", help="JSON partnerProfile object with revision, {partnerProfile:{...}}, or @file")
    partner_profiles_update.set_defaults(func=partner_profiles_cmd.cmd_partner_profiles_update, write_capable=True)
    partner_profiles_delete = partner_profiles_sub.add_parser("delete", help="Delete the current partner profile")
    partner_profiles_delete.set_defaults(func=partner_profiles_cmd.cmd_partner_profiles_delete, write_capable=True)
    partner_profiles_get_current = partner_profiles_sub.add_parser("get-current", help="Get the current partner profile")
    partner_profiles_get_current.set_defaults(func=partner_profiles_cmd.cmd_partner_profiles_get_current, write_capable=False)
    partner_profiles_get_public = partner_profiles_sub.add_parser("get-public", help="Get one public partner profile")
    partner_profiles_get_public.add_argument("--partner-id", required=True, help="Partner profile ID")
    partner_profiles_get_public.set_defaults(func=partner_profiles_cmd.cmd_partner_profiles_get_public, write_capable=False)
    partner_profiles_find_public_by_slug = partner_profiles_sub.add_parser("find-public-by-slug", help="Find one public partner profile by slug")
    partner_profiles_find_public_by_slug.add_argument("--slug", required=True, help="Public partner profile slug")
    partner_profiles_find_public_by_slug.set_defaults(func=partner_profiles_cmd.cmd_partner_profiles_find_public_by_slug, write_capable=False)

    viewer_cache = sub.add_parser("viewer-cache", help="Viewer cache methods")
    viewer_cache_sub = viewer_cache.add_subparsers(dest="viewer_cache_cmd", required=True, parser_class=_ToolArgumentParser)
    viewer_cache_invalidate = viewer_cache_sub.add_parser("invalidate", help="Invalidate tagged web method/router cache entries")
    viewer_cache_invalidate.add_argument("--invalidation-methods-json", required=True, dest="invalidation_methods_json", help="JSON array of {tag} objects, up to 100, or @file")
    viewer_cache_invalidate.set_defaults(func=viewer_cmd.cmd_viewer_cache_invalidate, write_capable=True)

    viewer_seo_tags = sub.add_parser("viewer-seo-tags", help="Viewer SEO tag resolution methods")
    viewer_seo_tags_sub = viewer_seo_tags.add_subparsers(dest="viewer_seo_tags_cmd", required=True, parser_class=_ToolArgumentParser)
    viewer_seo_tags_item = viewer_seo_tags_sub.add_parser("resolve-item", help="Resolve SEO tags for one item")
    viewer_seo_tags_item.add_argument("--page-url", required=True, help="Full canonical item page URL")
    viewer_seo_tags_item.add_argument("--slug", required=True, help="Item slug")
    viewer_seo_tags_item.add_argument("--item-type", required=True, help="Item type")
    viewer_seo_tags_item.add_argument("--seo-data-json", dest="seo_data_json", help="Optional SEO data JSON object or @file")
    viewer_seo_tags_item.set_defaults(func=viewer_cmd.cmd_viewer_seo_tags_resolve_item, write_capable=False)
    viewer_seo_tags_static = viewer_seo_tags_sub.add_parser("resolve-static", help="Resolve SEO tags for one static page")
    viewer_seo_tags_static.add_argument("--page-url", required=True, help="Full canonical static page URL")
    viewer_seo_tags_static.add_argument("--page-name", required=True, help="Static page name")
    viewer_seo_tags_static.add_argument("--seo-data-json", dest="seo_data_json", help="Optional SEO data JSON object or @file")
    viewer_seo_tags_static.set_defaults(func=viewer_cmd.cmd_viewer_seo_tags_resolve_static, write_capable=False)

    resellers = sub.add_parser("resellers", help="Account-level reseller package and product instance methods")
    resellers_sub = resellers.add_subparsers(dest="resellers_cmd", required=True, parser_class=_ToolArgumentParser)

    resellers_get = resellers_sub.add_parser("get", help="Get one reseller package")
    resellers_get.add_argument("--package-id", required=True, help="Package ID")
    resellers_get.set_defaults(func=resellers_cmd.cmd_resellers_get, write_capable=False)

    resellers_query = resellers_sub.add_parser("query", help="Query reseller packages")
    resellers_query.add_argument("--query-json", dest="query_json", help="JSON query object or full request payload")
    resellers_query.add_argument("--filter-json", dest="filter_json", help="JSON filter object")
    resellers_query.add_argument("--sort-json", dest="sort_json", help="JSON sort object/list")
    resellers_query.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    resellers_query.add_argument("--limit", type=int, default=None, help="Max packages to return (1-100)")
    resellers_query.set_defaults(func=resellers_cmd.cmd_resellers_query, write_capable=False)

    resellers_create_package = resellers_sub.add_parser("create-package", help="Create a reseller package")
    resellers_create_package.add_argument("--body-json", required=True, dest="body_json", help="JSON request body or @file")
    resellers_create_package.set_defaults(func=resellers_cmd.cmd_resellers_create_package, write_capable=True)

    resellers_adjust = resellers_sub.add_parser(
        "adjust-product-instance",
        help="Adjust one reseller product instance",
    )
    resellers_adjust.add_argument("--instance-id", required=True, help="Product instance ID")
    resellers_adjust.add_argument("--body-json", required=True, dest="body_json", help="JSON request body or @file")
    resellers_adjust.set_defaults(func=resellers_cmd.cmd_resellers_adjust_product_instance, write_capable=True)

    resellers_assign = resellers_sub.add_parser(
        "assign-product-instance",
        help="Assign one reseller product instance to a site",
    )
    resellers_assign.add_argument("--instance-id", required=True, help="Product instance ID")
    resellers_assign.add_argument("--site-id", required=True, help="Site ID")
    resellers_assign.set_defaults(func=resellers_cmd.cmd_resellers_assign_product_instance, write_capable=True)

    resellers_unassign = resellers_sub.add_parser(
        "unassign-product-instance",
        help="Unassign one reseller product instance from its site",
    )
    resellers_unassign.add_argument("--instance-id", required=True, help="Product instance ID")
    resellers_unassign.set_defaults(func=resellers_cmd.cmd_resellers_unassign_product_instance, write_capable=True)

    resellers_update_external_id = resellers_sub.add_parser(
        "update-package-external-id",
        help="Update a reseller package external ID",
    )
    resellers_update_external_id.add_argument("--package-id", required=True, help="Package ID")
    resellers_update_external_id.add_argument("--external-id", required=True, help="External ID, max 100 chars")
    resellers_update_external_id.set_defaults(
        func=resellers_cmd.cmd_resellers_update_package_external_id,
        write_capable=True,
    )

    resellers_cancel_package = resellers_sub.add_parser("cancel-package", help="Cancel one reseller package")
    resellers_cancel_package.add_argument("--package-id", required=True, help="Package ID")
    resellers_cancel_package.set_defaults(func=resellers_cmd.cmd_resellers_cancel_package, write_capable=True)

    resellers_cancel_instance = resellers_sub.add_parser(
        "cancel-product-instance",
        help="Cancel one reseller product instance",
    )
    resellers_cancel_instance.add_argument("--instance-id", required=True, help="Product instance ID")
    resellers_cancel_instance.set_defaults(func=resellers_cmd.cmd_resellers_cancel_product_instance, write_capable=True)

    multilingual_locale_settings = sub.add_parser(
        "multilingual-locale-settings",
        help="Wix Multilingual locale settings methods",
    )
    multilingual_locale_settings_sub = multilingual_locale_settings.add_subparsers(
        dest="multilingual_locale_settings_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    multilingual_locale_settings_get = multilingual_locale_settings_sub.add_parser(
        "get",
        help="Get locale settings",
    )
    multilingual_locale_settings_get.set_defaults(
        func=multilingual_locale_settings_cmd.cmd_multilingual_locale_settings_get,
        write_capable=False,
    )

    multilingual_locale_settings_set_mode = multilingual_locale_settings_sub.add_parser(
        "set-mode",
        help="Enable or disable multilingual mode",
    )
    multilingual_locale_settings_set_mode.add_argument(
        "--enabled",
        required=True,
        choices=("true", "false"),
        help="Whether multilingual mode is enabled",
    )
    multilingual_locale_settings_set_mode.set_defaults(
        func=multilingual_locale_settings_cmd.cmd_multilingual_locale_settings_set_mode,
        write_capable=True,
    )

    multilingual_locale_settings_update = multilingual_locale_settings_sub.add_parser(
        "update",
        help="Update locale settings",
    )
    multilingual_locale_settings_update.add_argument(
        "--locale-settings-json",
        required=True,
        dest="locale_settings_json",
        help="JSON localeSettings object or @file; revision is required",
    )
    multilingual_locale_settings_update.set_defaults(
        func=multilingual_locale_settings_cmd.cmd_multilingual_locale_settings_update,
        write_capable=True,
    )

    multilingual_locales = sub.add_parser("multilingual-locales", help="Wix Multilingual locale methods")
    multilingual_locales_sub = multilingual_locales.add_subparsers(
        dest="multilingual_locales_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    multilingual_locales_create = multilingual_locales_sub.add_parser("create", help="Create one secondary locale")
    multilingual_locales_create.add_argument("--locale-json", required=True, dest="locale_json", help="JSON locale object or @file")
    multilingual_locales_create.set_defaults(func=multilingual_locales_cmd.cmd_multilingual_locales_create, write_capable=True)

    multilingual_locales_get = multilingual_locales_sub.add_parser("get", help="Get one locale")
    multilingual_locales_get.add_argument("--locale-id", required=True, help="Locale ID, such as en-US")
    multilingual_locales_get.set_defaults(func=multilingual_locales_cmd.cmd_multilingual_locales_get, write_capable=False)

    multilingual_locales_update = multilingual_locales_sub.add_parser("update", help="Update one locale")
    multilingual_locales_update.add_argument("--locale-json", required=True, dest="locale_json", help="JSON locale object with id and revision or @file")
    multilingual_locales_update.set_defaults(func=multilingual_locales_cmd.cmd_multilingual_locales_update, write_capable=True)

    multilingual_locales_delete = multilingual_locales_sub.add_parser("delete", help="Delete one secondary locale")
    multilingual_locales_delete.add_argument("--locale-id", required=True, help="Locale ID, such as fr-FR")
    multilingual_locales_delete.set_defaults(func=multilingual_locales_cmd.cmd_multilingual_locales_delete, write_capable=True)

    multilingual_locales_query = multilingual_locales_sub.add_parser("query", help="Query site locales")
    multilingual_locales_query.add_argument("--query-json", dest="query_json", help="JSON query object or full request payload")
    multilingual_locales_query.add_argument("--filter-json", dest="filter_json", help="JSON filter object")
    multilingual_locales_query.add_argument("--sort-json", dest="sort_json", help="JSON sort object/list")
    multilingual_locales_query.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    multilingual_locales_query.add_argument("--limit", type=int, default=None, help="Max locales to return (1-100)")
    multilingual_locales_query.set_defaults(func=multilingual_locales_cmd.cmd_multilingual_locales_query, write_capable=False)

    multilingual_locales_bulk_create = multilingual_locales_sub.add_parser("bulk-create", help="Create multiple secondary locales")
    multilingual_locales_bulk_create.add_argument("--locales-json", required=True, dest="locales_json", help="JSON array of locale objects or @file")
    multilingual_locales_bulk_create.add_argument("--return-entity", choices=("true", "false"), default=None, help="Whether Wix should return created locale entities")
    multilingual_locales_bulk_create.set_defaults(func=multilingual_locales_cmd.cmd_multilingual_locales_bulk_create, write_capable=True)

    multilingual_locales_bulk_delete = multilingual_locales_sub.add_parser("bulk-delete", help="Delete multiple secondary locales")
    multilingual_locales_bulk_delete.add_argument("--locale-ids-json", required=True, dest="locale_ids_json", help="JSON array of locale IDs or @file")
    multilingual_locales_bulk_delete.set_defaults(func=multilingual_locales_cmd.cmd_multilingual_locales_bulk_delete, write_capable=True)

    multilingual_locales_bulk_update = multilingual_locales_sub.add_parser("bulk-update", help="Update multiple locales")
    multilingual_locales_bulk_update.add_argument("--locales-json", required=True, dest="locales_json", help="JSON array of {locale:{id,revision,...}} objects or @file")
    multilingual_locales_bulk_update.set_defaults(func=multilingual_locales_cmd.cmd_multilingual_locales_bulk_update, write_capable=True)

    multilingual_locales_change_primary = multilingual_locales_sub.add_parser("create-new-primary", help="Create and assign a new primary locale")
    multilingual_locales_change_primary.add_argument("--primary-locale-json", required=True, dest="primary_locale_json", help="JSON primaryLocale object or @file")
    multilingual_locales_change_primary.set_defaults(func=multilingual_locales_cmd.cmd_multilingual_locales_create_new_primary, write_capable=True)

    multilingual_locales_primary_status = multilingual_locales_sub.add_parser("get-new-primary-status", help="Get new primary locale change status")
    multilingual_locales_primary_status.add_argument("--token", required=True, help="Token returned by create-new-primary")
    multilingual_locales_primary_status.set_defaults(func=multilingual_locales_cmd.cmd_multilingual_locales_get_new_primary_status, write_capable=False)

    multilingual_locales_supported = multilingual_locales_sub.add_parser("list-supported", help="List Wix-supported locales")
    multilingual_locales_supported.add_argument("--language-code", default=None, help="Optional language code filter")
    multilingual_locales_supported.add_argument("--include-all-locales", choices=("true", "false"), default=None)
    multilingual_locales_supported.add_argument("--include-region-options", choices=("true", "false"), default=None)
    multilingual_locales_supported.set_defaults(func=multilingual_locales_cmd.cmd_multilingual_locales_list_supported, write_capable=False)

    multilingual_locales_set_visitor_primary = multilingual_locales_sub.add_parser("set-visitor-primary", help="Set visitor primary locale")
    multilingual_locales_set_visitor_primary.add_argument("--locale-id", required=True, help="Visible locale ID")
    multilingual_locales_set_visitor_primary.set_defaults(func=multilingual_locales_cmd.cmd_multilingual_locales_set_visitor_primary, write_capable=True)

    multilingual_translation_schemas = sub.add_parser(
        "multilingual-translation-schemas",
        help="Wix Multilingual translation schema methods",
    )
    multilingual_translation_schemas_sub = multilingual_translation_schemas.add_subparsers(
        dest="multilingual_translation_schemas_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    mts_create = multilingual_translation_schemas_sub.add_parser("create", help="Create one translation schema")
    mts_create.add_argument("--schema-json", required=True, dest="schema_json", help="JSON schema object or @file")
    mts_create.set_defaults(func=multilingual_translation_schemas_cmd.cmd_multilingual_translation_schemas_create, write_capable=True)

    mts_get = multilingual_translation_schemas_sub.add_parser("get", help="Get one translation schema by ID")
    mts_get.add_argument("--schema-id", required=True, help="Translation schema ID")
    mts_get.set_defaults(func=multilingual_translation_schemas_cmd.cmd_multilingual_translation_schemas_get, write_capable=False)

    mts_update = multilingual_translation_schemas_sub.add_parser("update", help="Update one translation schema")
    mts_update.add_argument("--schema-json", required=True, dest="schema_json", help="JSON schema object with id and revision or @file")
    mts_update.set_defaults(func=multilingual_translation_schemas_cmd.cmd_multilingual_translation_schemas_update, write_capable=True)

    mts_delete = multilingual_translation_schemas_sub.add_parser("delete", help="Delete one translation schema")
    mts_delete.add_argument("--schema-id", required=True, help="Translation schema ID")
    mts_delete.set_defaults(func=multilingual_translation_schemas_cmd.cmd_multilingual_translation_schemas_delete, write_capable=True)

    mts_query = multilingual_translation_schemas_sub.add_parser("query", help="Query translation schemas")
    mts_query.add_argument("--query-json", dest="query_json", help="JSON query object or full request payload")
    mts_query.add_argument("--filter-json", dest="filter_json", help="JSON filter object")
    mts_query.add_argument("--sort-json", dest="sort_json", help="JSON sort object/list")
    mts_query.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    mts_query.add_argument("--limit", type=int, default=None, help="Max schemas to return (1-100)")
    mts_query.set_defaults(func=multilingual_translation_schemas_cmd.cmd_multilingual_translation_schemas_query, write_capable=False)

    mts_list_site = multilingual_translation_schemas_sub.add_parser("list-site", help="List all site translation schemas")
    mts_list_site.add_argument("--app-id", default=None, help="Optional app ID filter")
    mts_list_site.add_argument("--entity-type", default=None, help="Optional entity type filter")
    mts_list_site.add_argument("--scope", choices=("GLOBAL", "SITE"), default=None, help="Optional schema scope filter")
    mts_list_site.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    mts_list_site.add_argument("--limit", type=int, default=None, help="Max schemas to return (0-100)")
    mts_list_site.set_defaults(func=multilingual_translation_schemas_cmd.cmd_multilingual_translation_schemas_list_site, write_capable=False)

    mts_get_by_key = multilingual_translation_schemas_sub.add_parser("get-by-key", help="Get a translation schema by app/entity/scope key")
    mts_get_by_key.add_argument("--app-id", required=True, help="App ID from the schema key")
    mts_get_by_key.add_argument("--entity-type", required=True, help="Entity type from the schema key")
    mts_get_by_key.add_argument("--scope", required=True, choices=("GLOBAL", "SITE"), help="Schema scope")
    mts_get_by_key.set_defaults(func=multilingual_translation_schemas_cmd.cmd_multilingual_translation_schemas_get_by_key, write_capable=False)

    mtc = sub.add_parser("multilingual-translation-contents", help="Wix Multilingual translation content methods")
    mtc_sub = mtc.add_subparsers(
        dest="multilingual_translation_contents_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    mtc_create = mtc_sub.add_parser("create", help="Create one translation content item")
    mtc_create.add_argument("--content-json", required=True, dest="content_json", help="JSON content object or @file")
    mtc_create.set_defaults(func=multilingual_translation_contents_cmd.cmd_multilingual_translation_contents_create, write_capable=True)

    mtc_get = mtc_sub.add_parser("get", help="Get one translation content item")
    mtc_get.add_argument("--content-id", required=True, help="Translation content ID")
    mtc_get.set_defaults(func=multilingual_translation_contents_cmd.cmd_multilingual_translation_contents_get, write_capable=False)

    mtc_update = mtc_sub.add_parser("update", help="Update one translation content item by ID")
    mtc_update.add_argument("--content-json", required=True, dest="content_json", help="JSON content object with id and schemaId or @file")
    mtc_update.add_argument("--force-fields-timestamp-update", choices=("true", "false"), default=None)
    mtc_update.set_defaults(func=multilingual_translation_contents_cmd.cmd_multilingual_translation_contents_update, write_capable=True)

    mtc_delete = mtc_sub.add_parser("delete", help="Delete one translation content item")
    mtc_delete.add_argument("--content-id", required=True, help="Translation content ID")
    mtc_delete.set_defaults(func=multilingual_translation_contents_cmd.cmd_multilingual_translation_contents_delete, write_capable=True)

    mtc_query = mtc_sub.add_parser("query", help="Query translation content")
    mtc_query.add_argument("--query-json", dest="query_json", help="JSON query object or full request payload")
    mtc_query.add_argument("--filter-json", dest="filter_json", help="JSON filter object")
    mtc_query.add_argument("--sort-json", dest="sort_json", help="JSON sort object/list")
    mtc_query.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    mtc_query.add_argument("--limit", type=int, default=None, help="Max content items to return (1-100)")
    mtc_query.set_defaults(func=multilingual_translation_contents_cmd.cmd_multilingual_translation_contents_query, write_capable=False)

    mtc_search = mtc_sub.add_parser("search", help="Search translation content")
    mtc_search.add_argument("--search-json", dest="search_json", help="JSON search object or full request payload")
    mtc_search.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    mtc_search.add_argument("--limit", type=int, default=None, help="Max content items to return (1-100)")
    mtc_search.set_defaults(func=multilingual_translation_contents_cmd.cmd_multilingual_translation_contents_search, write_capable=False)

    mtc_bulk_create = mtc_sub.add_parser("bulk-create", help="Create multiple translation content items")
    mtc_bulk_create.add_argument("--contents-json", required=True, dest="contents_json", help="JSON array of content objects or @file")
    mtc_bulk_create.add_argument("--return-entity", choices=("true", "false"), default=None)
    mtc_bulk_create.set_defaults(func=multilingual_translation_contents_cmd.cmd_multilingual_translation_contents_bulk_create, write_capable=True)

    mtc_bulk_delete = mtc_sub.add_parser("bulk-delete", help="Delete multiple translation content items")
    mtc_bulk_delete.add_argument("--content-ids-json", required=True, dest="content_ids_json", help="JSON array of content IDs or @file")
    mtc_bulk_delete.set_defaults(func=multilingual_translation_contents_cmd.cmd_multilingual_translation_contents_bulk_delete, write_capable=True)

    mtc_bulk_update = mtc_sub.add_parser("bulk-update", help="Update multiple translation content items by ID")
    mtc_bulk_update.add_argument("--contents-json", required=True, dest="contents_json", help="JSON array of {content:{id,schemaId,...}} objects or @file")
    mtc_bulk_update.add_argument("--force-fields-timestamp-update", choices=("true", "false"), default=None)
    mtc_bulk_update.add_argument("--return-entity", choices=("true", "false"), default=None)
    mtc_bulk_update.set_defaults(func=multilingual_translation_contents_cmd.cmd_multilingual_translation_contents_bulk_update, write_capable=True)

    mtc_update_by_key = mtc_sub.add_parser("update-by-key", help="Update one translation content item by schema/entity/locale key")
    mtc_update_by_key.add_argument("--content-json", required=True, dest="content_json", help="JSON content object with schemaId, entityId, and locale or @file")
    mtc_update_by_key.add_argument("--force-fields-timestamp-update", choices=("true", "false"), default=None)
    mtc_update_by_key.set_defaults(func=multilingual_translation_contents_cmd.cmd_multilingual_translation_contents_update_by_key, write_capable=True)

    mtc_bulk_update_by_key = mtc_sub.add_parser("bulk-update-by-key", help="Update multiple translation content items by schema/entity/locale key")
    mtc_bulk_update_by_key.add_argument("--contents-json", required=True, dest="contents_json", help="JSON array of {content:{schemaId,entityId,locale,...}} objects or @file")
    mtc_bulk_update_by_key.add_argument("--force-fields-timestamp-update", choices=("true", "false"), default=None)
    mtc_bulk_update_by_key.add_argument("--return-entity", choices=("true", "false"), default=None)
    mtc_bulk_update_by_key.set_defaults(func=multilingual_translation_contents_cmd.cmd_multilingual_translation_contents_bulk_update_by_key, write_capable=True)

    mtpc = sub.add_parser(
        "multilingual-translation-published-contents",
        help="Wix Multilingual published translation content methods",
    )
    mtpc_sub = mtpc.add_subparsers(
        dest="multilingual_translation_published_contents_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )

    mtpc_query = mtpc_sub.add_parser("query", help="Query published translation content")
    mtpc_query.add_argument("--query-json", dest="query_json", help="JSON query object or full request payload")
    mtpc_query.add_argument("--filter-json", dest="filter_json", help="JSON filter object with schemaKey.appId/entityType/scope")
    mtpc_query.add_argument("--sort-json", dest="sort_json", help="JSON sort object/list")
    mtpc_query.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    mtpc_query.add_argument("--limit", type=int, default=None, help="Max published content items to return (1-100)")
    mtpc_query.set_defaults(func=multilingual_translation_published_contents_cmd.cmd_multilingual_translation_published_contents_query, write_capable=False)

    mmt = sub.add_parser("multilingual-machine-translation", help="Wix Multilingual machine translation methods")
    mmt_sub = mmt.add_subparsers(
        dest="multilingual_machine_translation_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    mmt_translate = mmt_sub.add_parser("translate", help="Machine translate one content unit")
    mmt_translate.add_argument("--source-language", required=True, help="Source supported language code")
    mmt_translate.add_argument("--target-language", required=True, help="Target supported language code")
    mmt_translate.add_argument("--content-json", required=True, dest="content_json", help="TranslatableContent object or @file")
    mmt_translate.set_defaults(func=multilingual_machine_translation_cmd.cmd_multilingual_machine_translation_translate, write_capable=True)

    mmt_bulk = mmt_sub.add_parser("bulk-translate", help="Machine translate up to 1,000 content units")
    mmt_bulk.add_argument("--source-language", required=True, help="Source supported language code")
    mmt_bulk.add_argument("--target-language", required=True, help="Target supported language code")
    mmt_bulk.add_argument("--contents-json", required=True, dest="contents_json", help="JSON array of TranslatableContent objects or @file")
    mmt_bulk.set_defaults(func=multilingual_machine_translation_cmd.cmd_multilingual_machine_translation_bulk_translate, write_capable=True)

    mmtcd = sub.add_parser("multilingual-machine-translation-credit-data", help="Wix Multilingual machine translation credit data methods")
    mmtcd_sub = mmtcd.add_subparsers(
        dest="multilingual_machine_translation_credit_data_cmd",
        required=True,
        parser_class=_ToolArgumentParser,
    )
    mmtcd_get = mmtcd_sub.add_parser("get", help="Get site word credit data")
    mmtcd_get.set_defaults(func=multilingual_machine_translation_credit_data_cmd.cmd_multilingual_machine_translation_credit_data_get, write_capable=False)

    mmtcd_check = mmtcd_sub.add_parser("check-sufficient", help="Check whether a word count has enough credits")
    mmtcd_check.add_argument("--word-count", required=True, type=int, help="Number of words to translate")
    mmtcd_check.set_defaults(func=multilingual_machine_translation_credit_data_cmd.cmd_multilingual_machine_translation_credit_data_check_sufficient, write_capable=False)

    opp = sub.add_parser("online-programs-programs", help="Wix Online Programs Programs methods")
    opp_sub = opp.add_subparsers(dest="online_programs_programs_cmd", required=True, parser_class=_ToolArgumentParser)
    opp_create = opp_sub.add_parser("create", help="Create a draft program")
    opp_create.add_argument("--program-json", required=True, dest="program_json", help="Program object, {program:{...}}, or @file")
    opp_create.set_defaults(func=online_programs_programs_cmd.cmd_online_programs_programs_create, write_capable=True)
    opp_get = opp_sub.add_parser("get", help="Get one program")
    opp_get.add_argument("--program-id", required=True, help="Program GUID")
    opp_get.set_defaults(func=online_programs_programs_cmd.cmd_online_programs_programs_get, write_capable=False)
    opp_update = opp_sub.add_parser("update", help="Update selected program fields")
    opp_update.add_argument("--program-json", required=True, dest="program_json", help="Program object with id and revision, {program:{...}}, or @file")
    opp_update.set_defaults(func=online_programs_programs_cmd.cmd_online_programs_programs_update, write_capable=True)
    opp_delete = opp_sub.add_parser("delete", help="Delete one program")
    opp_delete.add_argument("--program-id", required=True, help="Program GUID")
    opp_delete.set_defaults(func=online_programs_programs_cmd.cmd_online_programs_programs_delete, write_capable=True)
    opp_query = opp_sub.add_parser("query", help="Query programs")
    opp_query.add_argument("--query-json", dest="query_json", default="{}", help="Query object, {query:{...}}, or @file")
    opp_query.set_defaults(func=online_programs_programs_cmd.cmd_online_programs_programs_query, write_capable=False)
    opp_search = opp_sub.add_parser("search", help="Search programs")
    opp_search.add_argument("--search-json", dest="search_json", default="{}", help="Search object, {search:{...}}, or @file")
    opp_search.set_defaults(func=online_programs_programs_cmd.cmd_online_programs_programs_search, write_capable=False)
    opp_count = opp_sub.add_parser("count", help="Count programs")
    opp_count.add_argument("--filter-json", dest="filter_json", default="{}", help="Filter object, {filter:{...}}, or @file")
    opp_count.set_defaults(func=online_programs_programs_cmd.cmd_online_programs_programs_count, write_capable=False)
    opp_bulk_update = opp_sub.add_parser("bulk-update", help="Update up to 100 programs")
    opp_bulk_update.add_argument("--programs-json", required=True, dest="programs_json", help="JSON array of {program:{id,revision,...}} objects or @file")
    opp_bulk_update.add_argument("--return-entity", choices=("true", "false"), default=None)
    opp_bulk_update.set_defaults(func=online_programs_programs_cmd.cmd_online_programs_programs_bulk_update, write_capable=True)
    for name, func, help_text, write_capable in [
        ("archive", online_programs_programs_cmd.cmd_online_programs_programs_archive, "Archive one program", True),
        ("duplicate", online_programs_programs_cmd.cmd_online_programs_programs_duplicate, "Duplicate one program as a draft", True),
        ("end", online_programs_programs_cmd.cmd_online_programs_programs_end, "End one published program", True),
        ("publish", online_programs_programs_cmd.cmd_online_programs_programs_publish, "Publish one draft program", True),
    ]:
        parser = opp_sub.add_parser(name, help=help_text)
        parser.add_argument("--program-id", required=True, help="Program GUID")
        parser.set_defaults(func=func, write_capable=write_capable)
    opp_samples = opp_sub.add_parser("list-samples", help="List sample programs")
    opp_samples.set_defaults(func=online_programs_programs_cmd.cmd_online_programs_programs_list_samples, write_capable=False)

    opi = sub.add_parser("online-programs-instructor-v2", help="Wix Online Programs Instructor V2 methods")
    opi_sub = opi.add_subparsers(dest="online_programs_instructor_v2_cmd", required=True, parser_class=_ToolArgumentParser)
    opi_create = opi_sub.add_parser("create", help="Create one instructor")
    opi_create.add_argument("--instructor-json", required=True, dest="instructor_json", help="Instructor object, {instructor:{...}}, or @file")
    opi_create.add_argument("--action-id", default=None, help="Optional BI trace action ID")
    opi_create.set_defaults(func=online_programs_instructor_v2_cmd.cmd_online_programs_instructor_v2_create, write_capable=True)
    opi_update = opi_sub.add_parser("update", help="Update one instructor")
    opi_update.add_argument("--instructor-json", required=True, dest="instructor_json", help="Instructor object with id, {instructor:{...}}, or @file")
    opi_update.add_argument("--action-id", default=None, help="Optional BI trace action ID")
    opi_update.set_defaults(func=online_programs_instructor_v2_cmd.cmd_online_programs_instructor_v2_update, write_capable=True)
    opi_query = opi_sub.add_parser("query", help="Query instructors")
    opi_query.add_argument("--query-json", dest="query_json", default="{}", help="Query object, {query:{...}}, or @file")
    opi_query.set_defaults(func=online_programs_instructor_v2_cmd.cmd_online_programs_instructor_v2_query, write_capable=False)
    opi_assign = opi_sub.add_parser("assign", help="Assign an instructor to one program")
    opi_assign.add_argument("--instructor-id", required=True, help="Instructor GUID")
    opi_assign.add_argument("--program-id", required=True, help="Program GUID")
    opi_assign.add_argument("--action-id", default=None, help="Optional BI trace action ID")
    opi_assign.set_defaults(func=online_programs_instructor_v2_cmd.cmd_online_programs_instructor_v2_assign, write_capable=True)
    opi_change = opi_sub.add_parser("change-program-instructors", help="Assign or unassign instructors for one program")
    opi_change.add_argument("--assignment-json", required=True, dest="assignment_json", help="JSON body with programId and assignInstructorIds/unassignInstructorIds or @file")
    opi_change.add_argument("--action-id", default=None, help="Optional BI trace action ID")
    opi_change.set_defaults(func=online_programs_instructor_v2_cmd.cmd_online_programs_instructor_v2_change_program_instructors, write_capable=True)
    opi_invite = opi_sub.add_parser("invite", help="Invite an instructor by email")
    opi_invite.add_argument("--email", required=True, help="Instructor email address")
    opi_invite.set_defaults(func=online_programs_instructor_v2_cmd.cmd_online_programs_instructor_v2_invite, write_capable=True)
    opi_list = opi_sub.add_parser("list", help="List instructors")
    opi_list.add_argument("--list-json", dest="list_json", default="{}", help="List body with paging/programIdsFilter or @file")
    opi_list.set_defaults(func=online_programs_instructor_v2_cmd.cmd_online_programs_instructor_v2_list, write_capable=False)
    opi_unassign = opi_sub.add_parser("unassign", help="Unassign an instructor from one program")
    opi_unassign.add_argument("--instructor-id", required=True, help="Instructor GUID")
    opi_unassign.add_argument("--program-id", required=True, help="Program GUID")
    opi_unassign.add_argument("--action-id", default=None, help="Optional BI trace action ID")
    opi_unassign.set_defaults(func=online_programs_instructor_v2_cmd.cmd_online_programs_instructor_v2_unassign, write_capable=True)

    site_folders = sub.add_parser("site-folders", help="Account-level site folder methods")
    site_folders_sub = site_folders.add_subparsers(
        dest="site_folders_cmd", required=True, parser_class=_ToolArgumentParser
    )

    site_folders_query = site_folders_sub.add_parser("query", help="Query site folders")
    site_folders_query.add_argument("--query-json", dest="query_json", help="JSON query payload")
    site_folders_query.add_argument("--filter-json", dest="filter_json", help="JSON filter object")
    site_folders_query.add_argument("--sort-json", dest="sort_json", help="JSON sort array of {fieldName, order}")
    site_folders_query.add_argument("--limit", type=int, default=None, help="Max folders to return (default: 1000, max: 1000)")
    site_folders_query.add_argument("--offset", type=int, default=None, help="Folders to skip in current sort order")
    site_folders_query.set_defaults(func=site_folders_cmd.cmd_site_folders_query, write_capable=False)

    site_folders_get = site_folders_sub.add_parser("get-folder-by-site", help="Get folder for one site")
    site_folders_get.add_argument("--site-id", required=True, help="Site ID")
    site_folders_get.set_defaults(func=site_folders_cmd.cmd_site_folders_get_folder_by_site, write_capable=False)

    site_folders_create = site_folders_sub.add_parser("create", help="Create one folder")
    site_folders_create.add_argument("--name", required=True, help="Folder name")
    site_folders_create.add_argument("--parent-id", default=None, help="Optional parent folder ID")
    site_folders_create.set_defaults(func=site_folders_cmd.cmd_site_folders_create, write_capable=True)

    site_folders_update = site_folders_sub.add_parser("update", help="Rename one folder")
    site_folders_update.add_argument("--folder-id", required=True, help="Folder ID")
    site_folders_update.add_argument("--name", required=True, help="New folder name")
    site_folders_update.set_defaults(func=site_folders_cmd.cmd_site_folders_update, write_capable=True)

    site_folders_delete = site_folders_sub.add_parser("delete", help="Delete one folder")
    site_folders_delete.add_argument("--folder-id", required=True, help="Folder ID")
    site_folders_delete.set_defaults(func=site_folders_cmd.cmd_site_folders_delete, write_capable=True)

    site_folders_move_sites = site_folders_sub.add_parser("move-sites", help="Move sites between folders")
    site_folders_move_sites.add_argument("--site-ids-json", required=True, dest="site_ids_json", help="JSON array of site IDs")
    site_folders_move_sites_target = site_folders_move_sites.add_mutually_exclusive_group(required=True)
    site_folders_move_sites_target.add_argument("--target-folder-id", default=None, dest="target_folder_id", help="Target folder ID")
    site_folders_move_sites_target.add_argument("--to-root", action="store_true", help="Move sites to root folder")
    site_folders_move_sites.set_defaults(func=site_folders_cmd.cmd_site_folders_move_sites, write_capable=True)

    site_folders_move_folders = site_folders_sub.add_parser("move-folders", help="Move folders to another folder")
    site_folders_move_folders.add_argument("--folder-ids-json", required=True, dest="folder_ids_json", help="JSON array of folder IDs")
    site_folders_move_folders_target = site_folders_move_folders.add_mutually_exclusive_group(required=True)
    site_folders_move_folders_target.add_argument("--target-folder-id", default=None, dest="target_folder_id", help="Target folder ID")
    site_folders_move_folders_target.add_argument("--to-root", action="store_true", help="Move folders to root level")
    site_folders_move_folders.set_defaults(func=site_folders_cmd.cmd_site_folders_move_folders, write_capable=True)

    site_actions = sub.add_parser("site-actions", help="Account-level write actions for sites")
    site_actions_sub = site_actions.add_subparsers(dest="site_actions_cmd", required=True, parser_class=_ToolArgumentParser)

    site_actions_bulk_delete = site_actions_sub.add_parser("bulk-delete", help="Move up to 20 sites to trash")
    site_actions_bulk_delete.add_argument(
        "--site-ids-json",
        required=True,
        dest="site_ids_json",
        help='JSON array of site IDs (max 20) to delete in one request',
    )
    site_actions_bulk_delete.set_defaults(func=site_actions_cmd.cmd_site_actions_bulk_delete, write_capable=True)

    site_actions_publish = site_actions_sub.add_parser("publish", help="Publish one site")
    site_actions_publish.add_argument("--site-id", required=True, help="Target site ID")
    site_actions_publish.set_defaults(func=site_actions_cmd.cmd_site_actions_publish, write_capable=True)

    site_actions_duplicate = site_actions_sub.add_parser("duplicate", help="Duplicate a site")
    site_actions_duplicate.add_argument("--source-site-id", required=True, help="Source site ID to duplicate")
    site_actions_duplicate.add_argument("--site-display-name", required=True, help="Display name for duplicated site")
    site_actions_duplicate.set_defaults(func=site_actions_cmd.cmd_site_actions_duplicate, write_capable=True)

    site_properties = sub.add_parser("site-properties", help="Read or write site property objects")
    site_properties_sub = site_properties.add_subparsers(
        dest="site_properties_cmd", required=True, parser_class=_ToolArgumentParser
    )

    site_properties_get = site_properties_sub.add_parser("get", help="Get site properties")
    site_properties_get.add_argument("--field-path", action="append", dest="field_path", help="Repeatable property path to return")
    site_properties_get.set_defaults(func=site_properties_cmd.cmd_site_properties_get, write_capable=False)

    site_properties_update_contact = site_properties_sub.add_parser(
        "update-business-contact",
        help="Update business-contact properties",
    )
    site_properties_update_contact.add_argument("--contact-json", required=True, help="Business contact JSON object")
    site_properties_update_contact.set_defaults(
        func=site_properties_cmd.cmd_site_properties_update_business_contact,
        write_capable=True,
    )

    site_properties_update_profile = site_properties_sub.add_parser(
        "update-business-profile",
        help="Update business profile",
    )
    site_properties_update_profile.add_argument("--profile-json", required=True, help="Business profile JSON object")
    site_properties_update_profile.set_defaults(
        func=site_properties_cmd.cmd_site_properties_update_business_profile,
        write_capable=True,
    )

    site_properties_update_schedule = site_properties_sub.add_parser(
        "update-business-schedule",
        help="Overwrite business schedule",
    )
    site_properties_update_schedule.add_argument("--schedule-json", required=True, help="Business schedule JSON object")
    site_properties_update_schedule.set_defaults(
        func=site_properties_cmd.cmd_site_properties_update_business_schedule,
        write_capable=True,
    )

    site_properties_update_consent = site_properties_sub.add_parser(
        "update-consent-policy",
        help="Update consent policy",
    )
    site_properties_update_consent.add_argument("--consent-json", required=True, help="Consent policy JSON object")
    site_properties_update_consent.set_defaults(
        func=site_properties_cmd.cmd_site_properties_update_consent_policy,
        write_capable=True,
    )

    site_urls = sub.add_parser("site-urls", help="Read-only site url lookup")
    site_urls_sub = site_urls.add_subparsers(dest="site_urls_cmd", required=True, parser_class=_ToolArgumentParser)
    site_urls_editor = site_urls_sub.add_parser("get-editor-urls", help="Get editor URLs")
    site_urls_editor.set_defaults(func=site_urls_cmd.cmd_site_urls_get_editor_urls, write_capable=False)

    site_urls_published = site_urls_sub.add_parser(
        "list-published-site-urls",
        help="Get published site URLs",
    )
    site_urls_published.set_defaults(func=site_urls_cmd.cmd_site_urls_list_published_site_urls, write_capable=False)

    data_items = sub.add_parser("data-items", help="CMS data item methods")
    data_items_sub = data_items.add_subparsers(dest="data_items_cmd", required=True, parser_class=_ToolArgumentParser)
    data_items_get = data_items_sub.add_parser("get", help="Get one data item from a collection")
    data_items_get.add_argument("--data-item-id", required=True, help="ID of the data item to retrieve")
    data_items_get.add_argument("--data-collection-id", required=True, help="ID of the collection the item belongs to")
    data_items_get.add_argument("--consistent-read", action="store_true", help="Read from primary DB for latest results")
    data_items_get.add_argument("--language", default=None, help="BCP 47 language tag for translated result text")
    data_items_get.add_argument("--fields-json", dest="fields_json", help="JSON array of projected fields")
    data_items_get.add_argument("--include-references-json", dest="include_references_json", help="Include reference fields as full items")
    data_items_get.set_defaults(func=data_items_cmd.cmd_data_items_get, write_capable=False)

    data_items_query = data_items_sub.add_parser("query", help="Query data items")
    data_items_query.add_argument("--data-collection-id", required=True, help="ID of the collection to query")
    data_items_query.add_argument("--query-json", dest="query_json", help="JSON query object or full request payload")
    data_items_query.add_argument("--filter-json", dest="filter_json", help="JSON filter object")
    data_items_query.add_argument("--sort-json", dest="sort_json", help="JSON sort object or array")
    data_items_query.add_argument("--fields-json", dest="fields_json", help="JSON array of projected fields")
    data_items_query.add_argument("--include-references-json", dest="include_references_json", help="JSON object/array for reference include options")
    data_items_query.add_argument("--include-field-groups-json", dest="include_field_groups_json", help="JSON array of field group names")
    data_items_query.add_argument("--language", default=None, help="BCP 47 language tag for translated result text")
    data_items_query.add_argument("--limit", type=int, default=None, help="Page size (for offset paging)")
    data_items_query.add_argument("--offset", type=int, default=None, help="Items to skip (offset paging)")
    data_items_query.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    data_items_query.add_argument("--return-total-count", action="store_true", help="Return total in pagingMetadata when using offset paging")
    data_items_query.add_argument("--consistent-read", action="store_true", help="Read from primary DB for latest results")
    data_items_query.set_defaults(func=data_items_cmd.cmd_data_items_query, write_capable=False)

    data_items_aggregate = data_items_sub.add_parser("aggregate", help="Run an aggregate query on data items")
    data_items_aggregate.add_argument("--data-collection-id", required=True, help="ID of the collection to aggregate")
    data_items_aggregate.add_argument("--aggregation-json", required=True, dest="aggregation_json", help="JSON object for aggregation")
    data_items_aggregate.add_argument("--initial-filter-json", dest="initial_filter_json", help="JSON filter object applied before aggregation")
    data_items_aggregate.add_argument("--final-filter-json", dest="final_filter_json", help="JSON filter object applied after aggregation")
    data_items_aggregate.add_argument("--sort-json", dest="sort_json", help="JSON sort object or array")
    data_items_aggregate.add_argument("--app-options-json", dest="app_options_json", help="JSON object for appOptions")
    data_items_aggregate.add_argument("--language", default=None, help="BCP 47 language tag for translated result text")
    data_items_aggregate.add_argument("--limit", type=int, default=None, help="Page size (for offset paging)")
    data_items_aggregate.add_argument("--offset", type=int, default=None, help="Items to skip (offset paging)")
    data_items_aggregate.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    data_items_aggregate.add_argument("--return-total-count", action="store_true", help="Return total in pagingMetadata when using offset paging")
    data_items_aggregate.add_argument("--consistent-read", action="store_true", help="Read from primary DB for latest results")
    data_items_aggregate.add_argument("--include-draft-items", action="store_true", help="Include draft items")
    data_items_aggregate.set_defaults(func=data_items_cmd.cmd_data_items_aggregate, write_capable=False)

    data_items_aggregate_pipeline = data_items_sub.add_parser(
        "aggregate-pipeline",
        help="Run an aggregate pipeline over data items",
    )
    data_items_aggregate_pipeline.add_argument("--data-collection-id", required=True, help="ID of the collection to aggregate")
    data_items_aggregate_pipeline.add_argument("--pipeline-json", required=True, dest="pipeline_json", help="JSON object for aggregate pipeline")
    data_items_aggregate_pipeline.add_argument("--app-options-json", dest="app_options_json", help="JSON object for appOptions")
    data_items_aggregate_pipeline.add_argument("--language", default=None, help="BCP 47 language tag for translated result text")
    data_items_aggregate_pipeline.add_argument("--return-total-count", action="store_true", help="Return total in pagingMetadata when using offset paging")
    data_items_aggregate_pipeline.add_argument("--consistent-read", action="store_true", help="Read from primary DB for latest results")
    data_items_aggregate_pipeline.add_argument("--include-draft-items", action="store_true", help="Include draft items")
    data_items_aggregate_pipeline.set_defaults(func=data_items_cmd.cmd_data_items_aggregate_pipeline, write_capable=False)

    data_items_distinct = data_items_sub.add_parser("distinct", help="Get distinct values for a field in a collection")
    data_items_distinct.add_argument("--data-collection-id", required=True, help="ID of the collection to query")
    data_items_distinct.add_argument("--field-name", required=True, dest="field_name", help="Field to return distinct values for")
    data_items_distinct.add_argument("--filter-json", dest="filter_json", help="JSON filter object")
    data_items_distinct.add_argument("--order", default=None, choices=("ASC", "DESC"), help="Sort order (ASC or DESC)")
    data_items_distinct.add_argument("--language", default=None, help="BCP 47 language tag for translated result text")
    data_items_distinct.add_argument("--limit", type=int, default=None, help="Page size (for offset paging)")
    data_items_distinct.add_argument("--offset", type=int, default=None, help="Items to skip (offset paging)")
    data_items_distinct.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    data_items_distinct.add_argument("--return-total-count", action="store_true", help="Return total in pagingMetadata when using offset paging")
    data_items_distinct.add_argument("--consistent-read", action="store_true", help="Read from primary DB for latest results")
    data_items_distinct.add_argument("--include-draft-items", action="store_true", help="Include draft items")
    data_items_distinct.set_defaults(func=data_items_cmd.cmd_data_items_distinct, write_capable=False)

    data_items_search = data_items_sub.add_parser("search", help="Search data items")
    data_items_search.add_argument("--data-collection-id", required=True, help="ID of the collection to search")
    data_items_search.add_argument("--search-json", required=True, dest="search_json", help="JSON search request payload")
    data_items_search.add_argument("--include-references-json", dest="include_references_json", help="JSON object/array for reference include options")
    data_items_search.add_argument("--referenced-item-options-json", dest="referenced_item_options_json", help="JSON object/array for referenced item options")
    data_items_search.add_argument("--include-draft-items", action="store_true", help="Include draft items")
    data_items_search.set_defaults(func=data_items_cmd.cmd_data_items_search, write_capable=False)

    data_items_query_referenced = data_items_sub.add_parser("query-referenced", help="Query items that reference a source item")
    data_items_query_referenced.add_argument("--data-collection-id", required=True, help="ID of the source collection")
    data_items_query_referenced.add_argument(
        "--referring-item-field-name",
        required=True,
        help="Field name on the source item that stores references",
    )
    data_items_query_referenced.add_argument("--referring-item-id", required=True, help="ID of the referring item")
    data_items_query_referenced.add_argument("--fields-json", dest="fields_json", help="JSON array of projected fields")
    data_items_query_referenced.add_argument("--language", default=None, help="BCP 47 language tag for translated result text")
    data_items_query_referenced.add_argument("--order", default=None, choices=("ASC", "DESC"), help="Sort order (ASC or DESC)")
    data_items_query_referenced.add_argument("--limit", type=int, default=None, help="Page size")
    data_items_query_referenced.add_argument("--offset", type=int, default=None, help="Items to skip (offset paging)")
    data_items_query_referenced.add_argument("--cursor", default=None, help="Paging cursor from prior response")
    data_items_query_referenced.add_argument("--return-total-count", action="store_true", help="Return total in pagingMetadata")
    data_items_query_referenced.add_argument("--consistent-read", action="store_true", help="Read from primary DB for latest results")
    data_items_query_referenced.add_argument("--include-draft-items", action="store_true", help="Include draft items from publish plugin data")
    data_items_query_referenced.add_argument("--include-hidden-products", action="store_true", help="Include hidden products from app options")
    data_items_query_referenced.add_argument("--include-variants", action="store_true", help="Include variants from app options")
    data_items_query_referenced.set_defaults(func=data_items_cmd.cmd_data_items_query_referenced, write_capable=False)

    data_items_is_referenced = data_items_sub.add_parser("is-referenced", help="Check if an item is referenced")
    data_items_is_referenced.add_argument("--data-collection-id", required=True, help="ID of the source collection")
    data_items_is_referenced.add_argument(
        "--referring-item-field-name",
        required=True,
        help="Field name on the source item that stores references",
    )
    data_items_is_referenced.add_argument("--referring-item-id", required=True, help="ID of the referring item")
    data_items_is_referenced.add_argument("--referenced-item-id", required=True, help="ID of the item to check")
    data_items_is_referenced.add_argument("--consistent-read", action="store_true", help="Read from primary DB for latest results")
    data_items_is_referenced.set_defaults(func=data_items_cmd.cmd_data_items_is_referenced, write_capable=False)

    data_items_insert_reference = data_items_sub.add_parser("insert-reference", help="Insert one data item reference")
    data_items_insert_reference.add_argument("--data-collection-id", required=True, help="ID of the collection containing the referring item")
    data_items_insert_reference.add_argument(
        "--referring-item-field-name",
        required=True,
        help="Field name on the source item that stores references",
    )
    data_items_insert_reference.add_argument("--referring-item-id", required=True, help="ID of the referring item")
    data_items_insert_reference.add_argument("--referenced-item-id", required=True, help="ID of the referenced item")
    data_items_insert_reference.add_argument("--consistent-read", action="store_true", help="Read from primary DB for preflight and verification")
    data_items_insert_reference.set_defaults(func=data_items_cmd.cmd_data_items_insert_reference, write_capable=True)

    data_items_remove_reference = data_items_sub.add_parser("remove-reference", help="Remove one data item reference")
    data_items_remove_reference.add_argument("--data-collection-id", required=True, help="ID of the collection containing the referring item")
    data_items_remove_reference.add_argument(
        "--referring-item-field-name",
        required=True,
        help="Field name on the source item that stores references",
    )
    data_items_remove_reference.add_argument("--referring-item-id", required=True, help="ID of the referring item")
    data_items_remove_reference.add_argument("--referenced-item-id", required=True, help="ID of the referenced item")
    data_items_remove_reference.add_argument("--consistent-read", action="store_true", help="Read from primary DB for preflight and verification")
    data_items_remove_reference.set_defaults(func=data_items_cmd.cmd_data_items_remove_reference, write_capable=True)

    data_items_replace_references = data_items_sub.add_parser("replace-references", help="Replace all references on one field")
    data_items_replace_references.add_argument("--data-collection-id", required=True, help="ID of the collection containing the referring item")
    data_items_replace_references.add_argument(
        "--referring-item-field-name",
        required=True,
        help="Field name on the source item that stores references",
    )
    data_items_replace_references.add_argument("--referring-item-id", required=True, help="ID of the referring item")
    data_items_replace_references.add_argument(
        "--new-referenced-item-ids-json",
        required=True,
        dest="new_referenced_item_ids_json",
        help="JSON array of referenced item IDs (can be empty)",
    )
    data_items_replace_references.add_argument("--consistent-read", action="store_true", help="Read from primary DB for preflight and verification")
    data_items_replace_references.set_defaults(func=data_items_cmd.cmd_data_items_replace_references, write_capable=True)

    data_items_count = data_items_sub.add_parser("count", help="Count data items")
    data_items_count.add_argument("--data-collection-id", required=True, help="ID of the collection to count")
    data_items_count.add_argument("--query-json", dest="query_json", help="JSON query/filter payload")
    data_items_count.add_argument("--filter-json", dest="filter_json", help="JSON filter object")
    data_items_count.add_argument("--language", default=None, help="BCP 47 language tag for translated result text")
    data_items_count.add_argument("--consistent-read", action="store_true", help="Read from primary DB for latest results")
    data_items_count.set_defaults(func=data_items_cmd.cmd_data_items_count, write_capable=False)

    data_items_save = data_items_sub.add_parser("save", help="Insert or update one CMS data item")
    data_items_save.add_argument("--data-collection-id", required=True, help="ID of the collection for the saved item")
    data_items_save.add_argument("--data-item-json", required=True, dest="data_item_json", help="JSON object for the saved data item")
    data_items_save.add_argument("--app-options-json", default=None, dest="app_options_json", help="JSON object for appOptions")
    data_items_save.add_argument("--include-draft-items", action="store_true", help="Include draft items in the save")
    data_items_save.set_defaults(func=data_items_cmd.cmd_data_items_save, write_capable=True)

    data_items_truncate = data_items_sub.add_parser("truncate", help="Remove all CMS data items from one collection")
    data_items_truncate.add_argument("--data-collection-id", required=True, help="ID of the collection to truncate")
    data_items_truncate.set_defaults(func=data_items_cmd.cmd_data_items_truncate, write_capable=True)

    data_items_bulk_remove = data_items_sub.add_parser("bulk-remove", help="Remove up to 1000 CMS data items in one request")
    data_items_bulk_remove.add_argument("--data-collection-id", required=True, help="ID of the collection containing the items")
    data_items_bulk_remove.add_argument(
        "--data-item-ids-json",
        required=True,
        dest="data_item_ids_json",
        help="JSON array of data item IDs (max 1000)",
    )
    data_items_bulk_remove.add_argument("--condition-json", dest="condition_json", help="Optional condition object")
    data_items_bulk_remove.add_argument("--app-options-json", default=None, dest="app_options_json", help="JSON object for appOptions")
    data_items_bulk_remove.add_argument("--include-draft-items", action="store_true", help="Include draft items in the remove")
    data_items_bulk_remove.set_defaults(func=data_items_cmd.cmd_data_items_bulk_remove, write_capable=True)

    data_items_bulk_save = data_items_sub.add_parser("bulk-save", help="Insert or update up to 1000 CMS data items in one request")
    data_items_bulk_save.add_argument("--data-collection-id", required=True, help="ID of the collection for the saved items")
    data_items_bulk_save.add_argument(
        "--data-items-json",
        required=True,
        dest="data_items_json",
        help="JSON array of data item objects (max 1000)",
    )
    data_items_bulk_save.add_argument("--app-options-json", default=None, dest="app_options_json", help="JSON object for appOptions")
    data_items_bulk_save.add_argument("--include-draft-items", action="store_true", help="Include draft items in the save")
    data_items_bulk_save.add_argument("--return-entity", action="store_true", help="Ask Wix to return saved entities")
    data_items_bulk_save.set_defaults(func=data_items_cmd.cmd_data_items_bulk_save, write_capable=True)

    data_items_bulk_update = data_items_sub.add_parser("bulk-update", help="Replace up to 1000 CMS data items in one request")
    data_items_bulk_update.add_argument("--data-collection-id", required=True, help="ID of the collection containing the items")
    data_items_bulk_update.add_argument(
        "--data-items-json",
        required=True,
        dest="data_items_json",
        help="JSON array of full replacement data item objects (max 1000; each item must include id)",
    )
    data_items_bulk_update.add_argument("--condition-json", dest="condition_json", help="Optional condition object")
    data_items_bulk_update.add_argument("--app-options-json", default=None, dest="app_options_json", help="JSON object for appOptions")
    data_items_bulk_update.add_argument("--include-draft-items", action="store_true", help="Include draft items in the update")
    data_items_bulk_update.add_argument("--return-entity", action="store_true", help="Ask Wix to return updated entities")
    data_items_bulk_update.set_defaults(func=data_items_cmd.cmd_data_items_bulk_update, write_capable=True)

    data_items_bulk_insert_references = data_items_sub.add_parser("bulk-insert-references", help="Insert up to 1000 CMS data item references")
    data_items_bulk_insert_references.add_argument("--data-collection-id", required=True, help="ID of the collection containing the referring items")
    data_items_bulk_insert_references.add_argument(
        "--data-item-references-json",
        required=True,
        dest="data_item_references_json",
        help="JSON array of reference objects with referringItemFieldName, referringItemId, and referencedItemId",
    )
    data_items_bulk_insert_references.add_argument("--return-entity", action="store_true", help="Ask Wix to return inserted references")
    data_items_bulk_insert_references.set_defaults(func=data_items_cmd.cmd_data_items_bulk_insert_references, write_capable=True)

    data_items_bulk_remove_references = data_items_sub.add_parser("bulk-remove-references", help="Remove up to 1000 CMS data item references")
    data_items_bulk_remove_references.add_argument("--data-collection-id", required=True, help="ID of the collection containing the referring items")
    data_items_bulk_remove_references.add_argument(
        "--data-item-references-json",
        required=True,
        dest="data_item_references_json",
        help="JSON array of reference objects with referringItemFieldName, referringItemId, and referencedItemId",
    )
    data_items_bulk_remove_references.set_defaults(func=data_items_cmd.cmd_data_items_bulk_remove_references, write_capable=True)

    data_items_insert = data_items_sub.add_parser("insert", help="Insert one CMS data item")
    data_items_insert.add_argument("--data-collection-id", required=True, help="ID of the collection for the new item")
    data_items_insert.add_argument("--data-item-json", required=True, dest="data_item_json", help="JSON object for the new data item")
    data_items_insert.add_argument("--language", default=None, help="BCP 47 language tag for translated result text")
    data_items_insert.set_defaults(func=data_items_cmd.cmd_data_items_insert, write_capable=True)

    data_items_bulk_insert = data_items_sub.add_parser("bulk-insert", help="Insert up to 1000 CMS data items in one request")
    data_items_bulk_insert.add_argument("--data-collection-id", required=True, help="ID of the collection for the new items")
    data_items_bulk_insert.add_argument(
        "--data-items-json",
        required=True,
        dest="data_items_json",
        help="JSON array of data item objects (max 1000)",
    )
    data_items_bulk_insert.add_argument("--app-options-json", default=None, dest="app_options_json", help="JSON object for appOptions")
    data_items_bulk_insert.add_argument("--return-entity", action="store_true", help="Ask Wix to return inserted entities")
    data_items_bulk_insert.set_defaults(func=data_items_cmd.cmd_data_items_bulk_insert, write_capable=True)

    data_items_bulk_patch = data_items_sub.add_parser("bulk-patch", help="Patch up to 100 CMS data items in one request")
    data_items_bulk_patch.add_argument("--data-collection-id", required=True, help="ID of the collection containing the items")
    data_items_bulk_patch.add_argument(
        "--patches-json",
        required=True,
        dest="patches_json",
        help="JSON array of patch objects (max 100)",
    )
    data_items_bulk_patch.add_argument("--condition-json", dest="condition_json", help="Optional condition object")
    data_items_bulk_patch.set_defaults(func=data_items_cmd.cmd_data_items_bulk_patch, write_capable=True)

    data_items_update = data_items_sub.add_parser("update", help="Replace one CMS data item")
    data_items_update.add_argument("--data-collection-id", required=True, help="ID of the collection the item belongs to")
    data_items_update.add_argument("--data-item-id", required=True, help="ID of the item to replace")
    data_items_update.add_argument("--data-item-json", required=True, dest="data_item_json", help="JSON object for the replacement item")
    data_items_update.add_argument("--condition-json", dest="condition_json", help="Optional condition object")
    data_items_update.add_argument("--language", default=None, help="BCP 47 language tag for translated result text")
    data_items_update.set_defaults(func=data_items_cmd.cmd_data_items_update, write_capable=True)

    data_items_patch = data_items_sub.add_parser("patch", help="Patch one CMS data item")
    data_items_patch.add_argument("--data-collection-id", required=True, help="ID of the collection the item belongs to")
    data_items_patch.add_argument("--data-item-id", required=True, help="ID of the item to patch")
    data_items_patch.add_argument("--patch-json", required=True, dest="patch_json", help="JSON patch object")
    data_items_patch.add_argument("--condition-json", dest="condition_json", help="Optional condition object")
    data_items_patch.add_argument("--language", default=None, help="BCP 47 language tag for translated result text")
    data_items_patch.set_defaults(func=data_items_cmd.cmd_data_items_patch, write_capable=True)

    data_items_remove = data_items_sub.add_parser("remove", help="Remove one CMS data item")
    data_items_remove.add_argument("--data-collection-id", required=True, help="ID of the collection the item belongs to")
    data_items_remove.add_argument("--data-item-id", required=True, help="ID of the item to remove")
    data_items_remove.add_argument("--condition-json", dest="condition_json", help="Optional condition object")
    data_items_remove.add_argument("--language", default=None, help="BCP 47 language tag for translated result text")
    data_items_remove.set_defaults(func=data_items_cmd.cmd_data_items_remove, write_capable=True)

    _register_inventory_backfill_commands(sub)
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
            payload = {"ok": True, "tool": "wix-safe-agent-cli", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"wix-safe-agent-cli {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        command_str = "wix-safe-agent-cli " + " ".join(argv)
        audit.bind_context(
            {
                "tool": "wix-safe-agent-cli",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
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
                "tool": "wix-safe-agent-cli",
                "tool_version": __version__,
                "command_str": command_str,
                "project_cfg": project_cfg,
                "project_dir": project_dir,
                "env_file": str(args.env_file),
                "timeout_s": None,
                "verbose": bool(args.verbose),
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "plan_out": args.plan_out,
                "plan_in": args.plan_in,
                "receipt_out": args.receipt_out,
                "ack_irreversible": bool(args.ack_irreversible),
                "enforce_reviewed_plan": True,
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
            "tool": "wix-safe-agent-cli",
            "tool_version": __version__,
            "command_str": command_str,
            "project_cfg": project_cfg,
            "project_dir": project_dir,
            "env_file": str(args.env_file),
            "timeout_s": timeout_s,
            "verbose": bool(args.verbose),
            "apply": bool(args.apply),
            "yes": bool(args.yes),
            "plan_out": args.plan_out,
            "plan_in": args.plan_in,
            "receipt_out": args.receipt_out,
            "ack_irreversible": bool(args.ack_irreversible),
            "enforce_reviewed_plan": True,
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
                "tool": "wix-safe-agent-cli",
                "version": __version__,
                "command": command_str,
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "env_fingerprint": cfg.base_url,
                "run_id": run_ctx.run_id,
            }
        )
        rc = int(args.func(args, ctx))

        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="wix-safe-agent-cli",
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
            tool="wix-safe-agent-cli",
            version=__version__,
            command="wix-safe-agent-cli " + " ".join(argv),
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
            tool="wix-safe-agent-cli",
            version=__version__,
            command="wix-safe-agent-cli " + " ".join(argv),
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
            tool="wix-safe-agent-cli",
            version=__version__,
            command="wix-safe-agent-cli " + " ".join(argv),
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
