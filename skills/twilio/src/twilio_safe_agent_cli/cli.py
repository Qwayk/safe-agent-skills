from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any, cast

from . import __version__
from .auth import build_auth
from .config import Config, load_config
from .errors import SafetyError, ToolError, ValidationError
from .local_contracts import (
    agent_connect_contract,
    generate_conversation_relay,
    validate_conversation_relay,
    validate_conversation_relay_message,
    validate_twilio_signature,
)
from .output import Output
from .redaction import redact
from .registry import CatalogRegistry, load_registry
from .runtime import execute_operation, execute_read

TOOL_NAME = "qwayk-twilio-safe-agent-cli"
_ACK_FLAGS = (
    "ack_contact",
    "ack_spend",
    "ack_bulk",
    "ack_destructive",
    "ack_auth",
    "ack_identity",
    "ack_production",
    "ack_preview",
    "ack_no_snapshot",
)


class _ToolArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def _output_mode(argv: list[str]) -> str:
    try:
        index = argv.index("--output")
    except ValueError:
        return "json"
    if index + 1 < len(argv) and argv[index + 1] in {"json", "text"}:
        return argv[index + 1]
    return "json"


def _read_input(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    source = Path(path).expanduser()
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise ValidationError(f"Could not read input JSON: {type(exc).__name__}") from None
    if not isinstance(value, dict):
        raise ValidationError("Input JSON must contain one object")
    return value


def _add_operation_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input-json", help="Path to a command-specific JSON input object")
    parser.add_argument(
        "--sensitive-out",
        help="Protected file for sensitive provider output or a command-required snapshot",
    )
    parser.add_argument("--apply", action="store_true", help="Apply a reviewed plan")
    parser.add_argument("--yes", action="store_true", help="Confirm the reviewed live change")
    parser.add_argument("--plan-out", help="Write the dry-run plan to a mode-600 JSON file")
    parser.add_argument("--plan-in", help="Reviewed plan JSON required for live apply")
    parser.add_argument("--receipt-out", help="Write the apply receipt to a mode-600 JSON file")
    parser.add_argument(
        "--snapshot-in",
        help="Protected current-state snapshot bound to the reviewed plan",
    )
    parser.add_argument("--target-count", type=int, help="Explicit bulk target count; hard-capped at 25")
    for name in _ACK_FLAGS:
        parser.add_argument(
            "--" + name.replace("_", "-"),
            dest=name,
            action="store_true",
            help="Explicit acknowledgement required by the generated safety classification",
        )


def build_parser(registry: CatalogRegistry | None = None) -> argparse.ArgumentParser:
    registry = registry or load_registry()
    parser = _ToolArgumentParser(prog=TOOL_NAME)
    parser.add_argument("--version", action="store_true", help="Print the tool version")
    parser.add_argument("--env-file", default=".env", help="Twilio credential env file")
    parser.add_argument("--output", choices=("json", "text"), default="json")
    parser.add_argument("--verbose", action="store_true", help="Print method, host, and status to stderr")
    parser.add_argument("--debug", action="store_true", help="Show a local traceback after a safe error")

    top = parser.add_subparsers(dest="command_group", parser_class=_ToolArgumentParser)

    inventory = top.add_parser("inventory", help="Inspect the pinned callable boundary")
    inventory_sub = inventory.add_subparsers(
        dest="inventory_command", required=True, parser_class=_ToolArgumentParser
    )
    inventory_sub.add_parser("summary", help="Show pinned coverage counts")
    inventory_show = inventory_sub.add_parser("show", help="Show one fixed command's safe input contract")
    inventory_show.add_argument("--command", required=True, help="Fixed command name, such as api-v2010.create-message")

    onboarding = top.add_parser("onboarding", help="Show or create a local Twilio env template")
    onboarding.add_argument("--write-env", action="store_true", help="Create the env file at mode 600")

    auth = top.add_parser("auth", help="Validate configured Twilio authentication")
    auth_sub = auth.add_subparsers(dest="auth_command", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Validate local auth without making a request")
    auth_check.add_argument(
        "--live",
        action="store_true",
        help="Run the safe api-v2010 fetch-account request after local validation",
    )
    auth_check.add_argument("--sensitive-out", help="Protected local file for the full account result")

    twiml = top.add_parser("twiml", help="Validate or generate bounded ConversationRelay XML")
    twiml_sub = twiml.add_subparsers(dest="local_command", required=True, parser_class=_ToolArgumentParser)
    for name in ("conversation-relay-generate", "conversation-relay-validate"):
        command = twiml_sub.add_parser(name)
        command.add_argument("--input-json", required=True, help="Path to the local contract input JSON")
    websocket = top.add_parser("websocket", help="Validate ConversationRelay WebSocket messages")
    websocket_sub = websocket.add_subparsers(dest="local_command", required=True, parser_class=_ToolArgumentParser)
    message = websocket_sub.add_parser("conversation-relay-message-validate")
    message.add_argument("--input-json", required=True, help="Path to the local contract input JSON")
    webhook = top.add_parser("webhook", help="Validate Twilio webhook signatures locally")
    webhook_sub = webhook.add_subparsers(dest="local_command", required=True, parser_class=_ToolArgumentParser)
    signature = webhook_sub.add_parser("twilio-signature-validate")
    signature.add_argument("--input-json", required=True, help="Path to the local contract input JSON")
    agent_connect = top.add_parser("agent-connect", help="Inspect the local Agent Connect metadata contract")
    agent_connect_sub = agent_connect.add_subparsers(dest="local_command", required=True, parser_class=_ToolArgumentParser)
    agent_connect_sub.add_parser("contract")

    for spec_id, operations in sorted(registry.by_spec.items()):
        spec = top.add_parser(spec_id, help=f"Fixed commands from {spec_id}")
        operation_parsers = spec.add_subparsers(
            dest="operation_name", required=True, parser_class=_ToolArgumentParser
        )
        for operation in operations:
            operation_name = operation["command"].split(".", 1)[1]
            command = operation_parsers.add_parser(
                operation_name,
                help=operation.get("summary") or operation["operation_id"],
            )
            _add_operation_options(command)
            command.set_defaults(operation_command=operation["command"])
    return parser


def _onboarding(args: argparse.Namespace, out: Output) -> int:
    destination = Path(args.env_file).expanduser()
    template = (
        "TWILIO_ACCOUNT_SID=\n"
        "TWILIO_API_KEY_SID=\n"
        "TWILIO_API_KEY_SECRET=\n"
        "# TWILIO_AUTH_TOKEN=\n"
        "# TWILIO_OAUTH_ACCESS_TOKEN=\n"
        "# TWILIO_REGION=\n"
        "# TWILIO_EDGE=\n"
        "TWILIO_TIMEOUT_S=30\n"
    )
    created = False
    if args.write_env:
        if destination.exists():
            raise ValidationError(f"Refused to overwrite existing env file: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        raw_fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        fd = os.fdopen(raw_fd, "w", encoding="utf-8")
        try:
            fd.write(template)
        finally:
            fd.close()
        destination.chmod(0o600)
        created = True
    out.emit(
        {
            "ok": True,
            "created": created,
            "env_file": str(destination),
            "required": [
                "TWILIO_ACCOUNT_SID",
                "TWILIO_API_KEY_SID",
                "TWILIO_API_KEY_SECRET",
            ],
            "next": f"Fill {destination}, then run: {TOOL_NAME} --env-file {destination} auth check",
        }
    )
    return 0


def _auth_check(
    args: argparse.Namespace,
    out: Output,
    registry: CatalogRegistry,
    cfg: Config,
) -> int:
    operation = registry.get("api-v2010.fetch-account")
    if operation is None:
        raise ValidationError("Pinned fetch-account command is unavailable")
    auth = build_auth(operation, cfg, {})
    if args.live:
        out.emit(
            execute_read(
                operation,
                {},
                cfg,
                sensitive_out=args.sensitive_out,
                verbose=bool(args.verbose),
            )
        )
    else:
        out.emit(
            {
                "ok": True,
                "configured": True,
                "live_request": False,
                "auth": auth.public_summary,
                "warnings": list(auth.warnings),
                "account_fingerprint": cfg.fingerprint,
                "region": cfg.region or "us1",
                "edge": cfg.edge or "automatic",
            }
        )
    return 0


def _run_generated(
    args: argparse.Namespace,
    out: Output,
    registry: CatalogRegistry,
    cfg: Config,
) -> int:
    operation = registry.get(args.operation_command)
    if operation is None:
        raise ValidationError("The fixed Twilio command is not in the pinned catalog")
    input_obj = _read_input(args.input_json)
    acknowledgements = {name: bool(getattr(args, name, False)) for name in _ACK_FLAGS}
    result = execute_operation(
        operation,
        input_obj,
        cfg,
        registry=registry,
        tool_version=__version__,
        apply=bool(args.apply),
        yes=bool(args.yes),
        plan_out=args.plan_out,
        plan_in=args.plan_in,
        receipt_out=args.receipt_out,
        snapshot_in=args.snapshot_in,
        acknowledgements=acknowledgements,
        target_count=args.target_count,
        sensitive_out=args.sensitive_out,
        verbose=bool(args.verbose),
    )
    out.emit(result)
    return 0


def _load_operation_config(operation: dict[str, Any], env_file: str) -> Config:
    requirements = operation.get("security", {}).get("requirements", [])
    scheme_names = {name for alternative in requirements for name in alternative}
    if not requirements:
        return load_config(env_file, require_account=False, require_credentials=False)
    if "oAuth2ClientCredentials" in scheme_names:
        return load_config(env_file, require_account=False, require_credentials=False)
    return load_config(env_file)


def _run_local_contract(argv: list[str], out: Output) -> int | None:
    """Handle credential-free local contracts without requiring the provider catalog."""
    groups = {"twiml", "websocket", "webhook", "agent-connect"}
    skip_value = False
    group = None
    for item in argv:
        if skip_value:
            skip_value = False
            continue
        if item in {"--output", "--env-file"}:
            skip_value = True
            continue
        if not item.startswith("-"):
            group = item if item in groups else None
            break
    if group is None:
        return None
    empty = CatalogRegistry(data={"operations": []}, inventory_hash="local-contracts")
    parser = build_parser(empty)
    args = parser.parse_args(argv)
    input_obj = _read_input(cast(str | None, getattr(args, "input_json", None)))
    if args.local_command == "conversation-relay-generate":
        out.emit(generate_conversation_relay(input_obj))
    elif args.local_command == "conversation-relay-validate":
        out.emit(validate_conversation_relay(cast(str, input_obj.get("xml"))))
    elif args.local_command == "conversation-relay-message-validate":
        out.emit(validate_conversation_relay_message(input_obj))
    elif args.local_command == "twilio-signature-validate":
        out.emit(validate_twilio_signature(input_obj))
    else:
        out.emit(agent_connect_contract(input_obj))
    return 0


def main(argv: list[str]) -> int:
    out = Output(mode=_output_mode(argv))
    cfg: Config | None = None
    debug = "--debug" in argv
    try:
        local_result = _run_local_contract(argv, out)
        if local_result is not None:
            return local_result
        registry = load_registry()
        parser = build_parser(registry)
        args = parser.parse_args(argv)
        if args.version:
            out.emit({"ok": True, "tool": TOOL_NAME, "version": __version__})
            return 0
        if not args.command_group:
            parser.error("Missing command. Use --help to see available commands.")
        if args.command_group == "inventory":
            if args.inventory_command == "show":
                out.emit(registry.describe(args.command))
            else:
                out.emit({"ok": True, **registry.summary()})
            return 0
        if args.command_group == "onboarding":
            return _onboarding(args, out)
        if args.command_group == "auth":
            cfg = load_config(args.env_file)
            return _auth_check(args, out, registry, cfg)
        operation = registry.get(args.operation_command)
        if operation is None:
            raise ValidationError("The fixed Twilio command is not in the pinned catalog")
        cfg = _load_operation_config(operation, args.env_file)
        return _run_generated(args, out, registry, cfg)
    except KeyboardInterrupt:
        out.emit({"ok": False, "error": "Interrupted", "error_type": "KeyboardInterrupt"})
        return 130
    except SafetyError as exc:
        safe_error = redact(str(exc), secret_values=cfg.redaction_values() if cfg else ())
        out.emit(
            {
                "ok": True,
                "refused": True,
                "reasons": [safe_error],
                "refusal_type": "SafetyError",
            }
        )
        return 0
    except (ToolError, ValueError, OSError) as exc:
        safe_error = redact(str(exc), secret_values=cfg.redaction_values() if cfg else ())
        out.emit({"ok": False, "error": safe_error, "error_type": type(exc).__name__})
        if debug:
            safe_traceback = redact(
                traceback.format_exc(),
                secret_values=cfg.redaction_values() if cfg else (),
            )
            print(safe_traceback, file=sys.stderr, end="" if safe_traceback.endswith("\n") else "\n")
        return 1
