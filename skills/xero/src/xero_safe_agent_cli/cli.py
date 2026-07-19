from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .auth import (
    TokenStore,
    begin_pkce,
    client_credentials_token,
    exchange_pkce,
    refresh_pkce,
)
from .config import Config, load_config
from .errors import SafetyError, ToolError, ValidationError
from .http import HttpClient
from .json_files import read_json_file
from .output import Output
from .redaction import safe_error
from .registry import CatalogRegistry, load_registry
from .runtime import ExecutionOptions, XeroRuntime
from .state import write_private_bytes
from .tenants import TenantStore

ENV_TEMPLATE = """# Local OAuth 2.0 Authorization Code with PKCE (recommended)
XERO_CLIENT_ID=
XERO_REDIRECT_URI=http://localhost:8765/callback

# Protected local state. Keep this out of shared folders and Git.
XERO_STATE_DIR=.state
XERO_TIMEOUT_S=30

# Optional paid, single-organisation Custom Connection.
XERO_CUSTOM_CLIENT_ID=
XERO_CUSTOM_CLIENT_SECRET=

# Optional non-tenanted Xero App Store API credentials.
XERO_APP_STORE_CLIENT_ID=
XERO_APP_STORE_CLIENT_SECRET=
"""


class _ToolArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def _add_fixed_command(
    subparsers: argparse._SubParsersAction[Any],
    command: str,
    operation: dict[str, Any],
) -> None:
    parser = subparsers.add_parser(
        command,
        help=str(operation.get("summary") or f"{operation['method']} {operation['path']}"),
    )
    parser.add_argument(
        "--input",
        default=None,
        help="JSON object with only path, query, headers, body, file_path, and media_type fields",
    )
    parser.set_defaults(handler="fixed", command=command)


def build_parser(registry: CatalogRegistry | None = None) -> argparse.ArgumentParser:
    registry = registry or load_registry()
    parser = _ToolArgumentParser(prog="qwayk-xero-safe-agent-cli")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    parser.add_argument("--env-file", default=".env", help="Local env file path")
    parser.add_argument("--output", choices=("json", "text"), default="json")
    parser.add_argument(
        "--auth-profile",
        choices=("pkce", "custom"),
        default="pkce",
        help="Use local PKCE by default or the optional paid single-organisation Custom Connection",
    )
    parser.add_argument("--verbose", action="store_true", help="Write safe HTTP timing to stderr")
    parser.add_argument("--apply", action="store_true", help="Apply an already reviewed saved plan")
    parser.add_argument("--plan-out", default=None, help="Protected output path for a new write plan")
    parser.add_argument("--plan-in", default=None, help="Reviewed write plan to apply")
    parser.add_argument("--receipt-out", default=None, help="Protected output path for the apply receipt")
    parser.add_argument("--protected-output", default=None, help="Protected local file for a full read response")
    parser.add_argument("--approve", action="store_true", help="Approve the exact saved write plan")
    parser.add_argument(
        "--approve-high-risk",
        action="store_true",
        help="Extra approval for financial, payroll, bank, file, auth, billing, tax, legal, employment, destructive, or bulk effects",
    )
    parser.add_argument(
        "--ack-no-snapshot",
        action="store_true",
        help="Acknowledge that the reviewed plan has no reliable before-state",
    )
    parser.add_argument(
        "--allow-deprecated-scope",
        action="store_true",
        help="Allow a command that still requires a deprecated broad Accounting scope",
    )
    parser.add_argument("--idempotency-key", default=None, help="Explicit Xero idempotency key when the operation documents support")
    sub = parser.add_subparsers(
        dest="command",
        required=False,
        parser_class=_ToolArgumentParser,
    )

    inventory = sub.add_parser("inventory", help="Inspect the fixed Xero command boundary")
    inventory_sub = inventory.add_subparsers(dest="inventory_command", required=True)
    inventory_sub.add_parser("summary").set_defaults(handler="inventory_summary")
    inventory_list = inventory_sub.add_parser("list")
    inventory_list.add_argument("--spec", default=None)
    inventory_list.add_argument("--limit", type=int, default=50)
    inventory_list.set_defaults(handler="inventory_list")
    inventory_show = inventory_sub.add_parser("show")
    inventory_show.add_argument("--command", required=True, dest="fixed_command")
    inventory_show.set_defaults(handler="inventory_show")

    onboarding = sub.add_parser("onboarding", help="Prepare local placeholder configuration")
    onboarding.add_argument("--no-write-env", action="store_true")
    onboarding.set_defaults(handler="onboarding")

    auth = sub.add_parser("auth", help="OAuth and token helpers")
    auth_sub = auth.add_subparsers(dest="auth_command", required=True)
    auth_status = auth_sub.add_parser("status")
    auth_status.add_argument("--profile", choices=("pkce", "custom", "app-store"), default="pkce")
    auth_status.set_defaults(handler="auth_status")
    auth_start = auth_sub.add_parser("start")
    auth_start.add_argument("--command", action="append", dest="commands", required=True)
    auth_start.add_argument("--no-offline", action="store_true")
    auth_start.set_defaults(handler="auth_start")
    auth_exchange = auth_sub.add_parser("exchange")
    auth_exchange.add_argument("--code-file", required=True)
    auth_exchange.add_argument("--state", required=True)
    auth_exchange.set_defaults(handler="auth_exchange")
    auth_sub.add_parser("refresh").set_defaults(handler="auth_refresh")
    credentials = auth_sub.add_parser("client-credentials")
    credentials.add_argument("--profile", choices=("custom", "app-store"), required=True)
    credentials.add_argument("--scope", action="append", dest="scopes", required=True)
    credentials.set_defaults(handler="auth_client_credentials")

    tenant = sub.add_parser("tenant", help="Discover and select the exact Xero tenant")
    tenant_sub = tenant.add_subparsers(dest="tenant_command", required=True)
    tenant_sub.add_parser("list").set_defaults(handler="tenant_list")
    tenant_select = tenant_sub.add_parser("select")
    tenant_select.add_argument("--tenant-id", required=True)
    tenant_select.add_argument(
        "--region", choices=("AU", "NZ", "UK", "US", "GLOBAL"), required=True
    )
    tenant_select.set_defaults(handler="tenant_select")
    tenant_custom = tenant_sub.add_parser(
        "custom-discover",
        help="Discover the one organisation bound to a paid Custom Connection",
    )
    tenant_custom.set_defaults(handler="tenant_custom_discover")
    tenant_show = tenant_sub.add_parser("show")
    tenant_show.add_argument("--profile", choices=("pkce", "custom"), default="pkce")
    tenant_show.set_defaults(handler="tenant_show")

    for command, operation in sorted(registry.commands.items()):
        _add_fixed_command(sub, command, operation)
    return parser


def _output_mode(argv: list[str]) -> str:
    try:
        index = argv.index("--output")
        return argv[index + 1] if index + 1 < len(argv) else "json"
    except ValueError:
        return "json"


def _transport(config: Config, verbose: bool) -> HttpClient:
    return HttpClient(
        timeout_s=config.timeout_s,
        verbose=verbose,
        user_agent=f"qwayk-xero-safe-agent-cli/{__version__}",
    )


def _token_store(config: Config, profile: str) -> TokenStore:
    if profile == "custom":
        return TokenStore(config.custom_token_path)
    if profile == "app-store":
        return TokenStore(config.app_store_token_path)
    return TokenStore(config.pkce_token_path)


def _connections(config: Config, *, verbose: bool) -> list[dict[str, Any]]:
    token = TokenStore(config.pkce_token_path).read()
    response = _transport(config, verbose).request(
        "GET",
        "https://api.xero.com/Connections",
        headers={"Authorization": "Bearer " + str(token["access_token"]), "Accept": "application/json"},
        retries=2,
    )
    if response.status >= 400:
        raise ValidationError(f"Xero Connections returned HTTP {response.status}")
    try:
        payload = json.loads(response.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValidationError("Xero Connections returned invalid JSON") from None
    if not isinstance(payload, list):
        raise ValidationError("Xero Connections did not return a list")
    return [item for item in payload if isinstance(item, dict)]


def _custom_organisation(config: Config, *, verbose: bool) -> tuple[dict[str, Any], str]:
    token = TokenStore(config.custom_token_path).read()
    response = _transport(config, verbose).request(
        "GET",
        "https://api.xero.com/api.xro/2.0/Organisation",
        headers={"Authorization": "Bearer " + str(token["access_token"]), "Accept": "application/json"},
        retries=2,
    )
    if response.status >= 400:
        raise ValidationError(f"Xero Organisation returned HTTP {response.status}")
    try:
        payload = json.loads(response.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValidationError("Xero Organisation returned invalid JSON") from None
    organisations = payload.get("Organisations") if isinstance(payload, dict) else None
    if not isinstance(organisations, list) or len(organisations) != 1:
        raise ValidationError(
            "Custom Connection Organisation response must contain exactly one organisation"
        )
    organisation = organisations[0]
    if not isinstance(organisation, dict):
        raise ValidationError("Custom Connection Organisation entry is invalid")
    return organisation, str(token["credential_fingerprint"])


def _onboarding(config: Config, *, no_write_env: bool) -> dict[str, Any]:
    created = False
    if not config.env_file.exists() and not no_write_env:
        write_private_bytes(config.env_file, ENV_TEMPLATE.encode("utf-8"))
        created = True
    return {
        "ok": True,
        "env_file": str(config.env_file),
        "created_placeholder_env": created,
        "next": [
            "Add only your Xero client ID and exact redirect URI to the local env file.",
            "Run auth start with the fixed commands you want so the tool can request minimum scopes.",
            "Run tenant list and tenant select before any tenanted command.",
        ],
    }


def _fixed_runtime(
    config: Config,
    registry: CatalogRegistry,
    operation: dict[str, Any],
    *,
    auth_profile: str,
    verbose: bool,
) -> XeroRuntime:
    profile = "app-store" if operation.get("auth_flow") == "client_credentials" else auth_profile
    tenant_path = config.custom_tenant_path if profile == "custom" else config.tenant_path
    return XeroRuntime(
        registry,
        _transport(config, verbose),
        _token_store(config, profile),
        TenantStore(tenant_path),
        auth_profile=profile,
    )


def _handle(args: argparse.Namespace, registry: CatalogRegistry, config: Config) -> dict[str, Any]:
    handler = getattr(args, "handler", None)
    if handler == "inventory_summary":
        return {"ok": True, **registry.summary()}
    if handler == "inventory_list":
        rows = [
            registry.describe(command)
            for command in sorted(registry.commands)
            if args.spec is None or command.startswith(str(args.spec) + ".")
        ][: max(0, args.limit)]
        return {"ok": True, "count": len(rows), "commands": rows}
    if handler == "inventory_show":
        return registry.describe(args.fixed_command)
    if handler == "onboarding":
        return _onboarding(config, no_write_env=bool(args.no_write_env))
    if handler == "auth_status":
        return {"ok": True, "profile": args.profile, "token": _token_store(config, args.profile).status()}
    if handler == "auth_start":
        scopes = registry.minimum_scopes(args.commands, offline=not args.no_offline)
        return begin_pkce(
            client_id=config.client_id,
            redirect_uri=config.redirect_uri,
            scopes=scopes,
            state_dir=config.pkce_state_path.parent,
        )
    if handler == "auth_exchange":
        return exchange_pkce(
            transport=_transport(config, args.verbose),
            state_path=config.pkce_state_path,
            code_file=args.code_file,
            returned_state=args.state,
            token_store=TokenStore(config.pkce_token_path),
        )
    if handler == "auth_refresh":
        return refresh_pkce(
            transport=_transport(config, args.verbose),
            client_id=config.client_id,
            token_store=TokenStore(config.pkce_token_path),
        )
    if handler == "auth_client_credentials":
        requested_scopes = set(args.scopes)
        allowed_scopes = registry.client_credentials_scopes(args.profile)
        unsupported_scopes = sorted(requested_scopes - allowed_scopes)
        if unsupported_scopes:
            raise ValidationError(
                f"Scope(s) not allowed for {args.profile} client credentials: "
                + ", ".join(unsupported_scopes)
            )
        if args.profile == "custom":
            client_id = config.custom_client_id or ""
            secret = config.custom_client_secret or ""
        else:
            client_id = config.app_store_client_id or ""
            secret = config.app_store_client_secret or ""
        return client_credentials_token(
            transport=_transport(config, args.verbose),
            client_id=client_id,
            client_secret=secret,
            scopes=sorted(requested_scopes),
            token_store=_token_store(config, args.profile),
        )
    if handler == "tenant_list":
        connections = _connections(config, verbose=args.verbose)
        safe = [
            {
                "id": item.get("id"),
                "tenant_id": item.get("tenantId"),
                "tenant_name": item.get("tenantName"),
                "tenant_type": item.get("tenantType"),
            }
            for item in connections
        ]
        return {"ok": True, "count": len(safe), "connections": safe, "selected": None}
    if handler == "tenant_select":
        connections = _connections(config, verbose=args.verbose)
        selected = TenantStore(config.tenant_path).select(
            connections,
            tenant_id=args.tenant_id,
            region=args.region,
        )
        return {"ok": True, "selected": selected}
    if handler == "tenant_custom_discover":
        organisation, credential_fingerprint = _custom_organisation(
            config, verbose=args.verbose
        )
        selected = TenantStore(config.custom_tenant_path).select_custom(
            organisation,
            credential_fingerprint=credential_fingerprint,
        )
        return {"ok": True, "profile": "custom", "selected": selected}
    if handler == "tenant_show":
        path = config.custom_tenant_path if args.profile == "custom" else config.tenant_path
        return {"ok": True, "profile": args.profile, "selected": TenantStore(path).read()}
    if handler == "fixed":
        operation = registry.get(args.command)
        assert operation is not None
        input_data: dict[str, Any] = {}
        if args.input:
            loaded = read_json_file(args.input)
            if not isinstance(loaded, dict):
                raise ValidationError("Fixed command input file must contain one JSON object")
            input_data = loaded
        runtime = _fixed_runtime(
            config,
            registry,
            operation,
            auth_profile=args.auth_profile,
            verbose=args.verbose,
        )
        return runtime.execute(
            args.command,
            input_data,
            ExecutionOptions(
                apply=bool(args.apply),
                plan_out=Path(args.plan_out) if args.plan_out else None,
                plan_in=Path(args.plan_in) if args.plan_in else None,
                receipt_out=Path(args.receipt_out) if args.receipt_out else None,
                protected_output=Path(args.protected_output) if args.protected_output else None,
                approve=bool(args.approve),
                approve_high_risk=bool(args.approve_high_risk),
                ack_no_snapshot=bool(args.ack_no_snapshot),
                allow_deprecated_scope=bool(args.allow_deprecated_scope),
                idempotency_key=args.idempotency_key,
            ),
        )
    raise ValidationError("Missing command. Use --help to see the fixed Xero commands.")


def main(argv: list[str] | None = None) -> int:
    values = list(sys.argv[1:] if argv is None else argv)
    output = Output(mode=_output_mode(values))
    try:
        registry = load_registry()
        parser = build_parser(registry)
        args = parser.parse_args(values)
        if args.version:
            output.emit({"ok": True, "tool": "qwayk-xero-safe-agent-cli", "version": __version__})
            return 0
        config = load_config(args.env_file)
        result = _handle(args, registry, config)
        output.emit(result)
        return 0 if result.get("ok") else 1
    except (ToolError, ValueError, OSError, RuntimeError) as exc:
        output.emit(
            {
                "ok": False,
                "error": safe_error(str(exc)),
                "error_type": type(exc).__name__,
            }
        )
        return 2 if isinstance(exc, (SafetyError, ValidationError)) else 1
