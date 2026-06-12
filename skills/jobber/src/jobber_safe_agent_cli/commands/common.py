from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from ..errors import ValidationError
from ..json_files import read_json_file
from ..schema_registry import OperationField


def parse_payload_argument(*, args_json: str | None, args_file: str | None) -> dict[str, Any]:
    if args_json and args_file:
        raise ValidationError("Use only one of --args-json or --args-file")

    if args_file:
        obj = read_json_file(args_file)
    elif args_json:
        try:
            obj = json.loads(args_json)
        except Exception:
            raise ValidationError("Invalid JSON in --args-json") from None
    else:
        return {}

    if not isinstance(obj, dict):
        raise ValidationError("Arguments payload must be a JSON object")
    return obj


def parse_selection(*, selection: str | None, selection_file: str | None) -> str | None:
    if selection and selection_file:
        raise ValidationError("Use only one of --selection and --selection-file")
    if selection_file:
        p = Path(selection_file)
        if not p.exists():
            raise ValidationError(f"Selection file not found: {p}")
        selection = p.read_text(encoding="utf-8")
    if selection:
        return str(selection).strip() or None
    return None


def format_graphql_arg_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def build_graphql_selection(type_name: str, user_selection: str | None) -> str | None:
    if user_selection:
        s = user_selection.strip()
        if s:
            return s if s.startswith("{") and s.endswith("}") else f"{{ {s} }}"
        return None

    scalar_or_enum = {"SCALAR", "ENUM"}
    if type_name in scalar_or_enum:
        return None
    return "{ __typename }"


def filter_allowed_args(*, spec: OperationField, raw_args: dict[str, Any]) -> dict[str, Any]:
    allowed = {arg.name for arg in spec.args if arg.name}
    out: dict[str, Any] = {}
    for key, value in raw_args.items():
        if key not in allowed:
            raise ValidationError(f"Unknown argument '{key}' for operation '{spec.name}'")
        out[key] = value
    return out


def build_operation_document(*, operation: str, args: dict[str, Any], selection: str | None, operation_type: str) -> str:
    arg_parts: list[str] = []
    for key in sorted(args):
        arg_parts.append(f"{key}: {format_graphql_arg_value(args[key])}")
    arg_text = ("(" + ", ".join(arg_parts) + ")") if arg_parts else ""
    if selection is None:
        selection_text = ""
    elif selection:
        selection_text = " " + selection.strip()
    else:
        selection_text = ""
    return f"{operation_type} {{ {operation}{arg_text}{selection_text} }}"


def args_hash(args: dict[str, Any]) -> str:
    payload = json.dumps(args, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def text_hash(value: str | None) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()


_NO_SNAPSHOT_RISK_PREFIXES = ("delete", "destroy", "remove", "cancel", "archive")
_NO_SNAPSHOT_RISK_SUFFIXES = ("delete", "destroy", "remove", "cancel", "archive")
_NO_SNAPSHOT_RISK_TOKENS = (
    "send",
    "spend",
    "auth",
    "permission",
    "payment",
    "pay",
    "refund",
    "capture",
    "charge",
    "billing",
    "invoicepay",
    "payout",
    "cardonfile",
    "transfer",
    "purchase",
    "approve",
    "publish",
    "activate",
    "deactivate",
    "merge",
    "import",
    "revert",
    "bulk",
    "connect",
    "disconnect",
    "token",
    "session",
    "ownership",
)
_IRREVERSIBLE_RISK_PREFIXES = ("delete", "destroy", "remove", "cancel", "archive", "disconnect")
_IRREVERSIBLE_RISK_SUFFIXES = ("delete", "destroy", "remove", "cancel", "archive", "disconnect")
_IRREVERSIBLE_RISK_TOKENS = (
    "send",
    "pay",
    "payment",
    "refund",
    "capture",
    "charge",
    "transfer",
    "purchase",
    "publish",
    "merge",
)


def _normalize_mutation_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(name).lower())


def mutation_requires_no_snapshot(name: str) -> bool:
    lowered = _normalize_mutation_name(name)
    return (
        lowered.startswith(_NO_SNAPSHOT_RISK_PREFIXES)
        or lowered.endswith(_NO_SNAPSHOT_RISK_SUFFIXES)
        or any(token in lowered for token in _NO_SNAPSHOT_RISK_TOKENS)
    )


def mutation_requires_ack_irreversible(name: str) -> bool:
    lowered = _normalize_mutation_name(name)
    return (
        lowered.startswith(_IRREVERSIBLE_RISK_PREFIXES)
        or lowered.endswith(_IRREVERSIBLE_RISK_SUFFIXES)
        or any(token in lowered for token in _IRREVERSIBLE_RISK_TOKENS)
    )


def mutation_snapshot_plan_fields() -> dict[str, Any]:
    return {
        "snapshot_status": "No snapshot available",
        "recovery_notes": "No useful before-state was saved. Recovery may be manual or impossible.",
        "recovery": {
            "status": "manual_or_impossible",
            "notes": "No useful before-state was saved. Recovery may be manual or impossible.",
        },
    }
