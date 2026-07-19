from __future__ import annotations

import hashlib
import json
from typing import Any

from .config import Config
from .errors import SafetyError
from .redaction import redact

_EFFECT_RISKS = {"spend", "outbound_contact", "bulk"}
_ACK_BY_RISK = {
    "outbound_contact": "ack_contact",
    "spend": "ack_spend",
    "bulk": "ack_bulk",
    "destructive": "ack_destructive",
    "auth_or_permission": "ack_auth",
    "identity_or_compliance": "ack_identity",
    "production_change": "ack_production",
    "preview": "ack_preview",
}


def _stable_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _explicit_target_count(input_obj: dict[str, Any], *, bulk: bool) -> int | None:
    counts: list[int] = []
    target_keys = {"to", "recipient", "recipients", "addresses"}
    bulk_keys = {"items", "phonenumbers", "profiles", "queuesids"}

    def inspect(value: Any) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                normalized = str(key).lower().replace("_", "")
                if normalized in target_keys or (bulk and normalized in bulk_keys):
                    counts.append(len(nested) if isinstance(nested, list) else 1)
                if bulk and normalized == "updaterequest" and isinstance(nested, str):
                    try:
                        parsed = json.loads(nested)
                    except json.JSONDecodeError:
                        parsed = None
                    if isinstance(parsed, list):
                        counts.append(len(parsed))
                inspect(nested)
        elif isinstance(value, list):
            for item in value:
                inspect(item)

    inspect(input_obj.get("body"))
    return max(counts) if counts else None


def classify_risks(operation: dict[str, Any], input_obj: dict[str, Any]) -> list[str]:
    risks = set(operation.get("risk_flags", []))
    if operation.get("classification", {}).get("preview"):
        risks.add("preview")
    body = input_obj.get("body") if isinstance(input_obj, dict) else None
    if isinstance(body, dict):
        for key, value in body.items():
            lowered = str(key).lower()
            if lowered in {"to", "recipients", "recipient", "identities", "addresses"}:
                if isinstance(value, list) and len(value) > 1 and "bulk" not in risks:
                    raise SafetyError("Refused: one command may contact only one explicit target")
            if lowered in {"status", "state"} and str(value).lower() in {
                "closed",
                "cancelled",
                "canceled",
                "released",
                "deleted",
            }:
                risks.add("destructive")
        dynamic_contact = False
        dynamic_bulk = False

        def inspect(value: Any, parent_key: str = "") -> None:
            nonlocal dynamic_contact, dynamic_bulk
            if isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    normalized = str(nested_key).lower().replace("_", "")
                    if normalized in {"to", "recipient", "recipients", "addresses"}:
                        dynamic_contact = True
                        if isinstance(nested_value, list) and len(nested_value) > 1:
                            dynamic_bulk = True
                    action = str(nested_value).upper().replace("-", "_")
                    if normalized in {"type", "action", "channel"} and action in {
                        "SEND_MESSAGE",
                        "SEND_AND_WAIT_FOR_REPLY",
                        "MAKE_OUTGOING_CALL_V1",
                        "MAKE_OUTGOING_CALL_V2",
                        "CONNECT_CALL_TO",
                        "SMS",
                        "MMS",
                        "RCS",
                        "WHATSAPP",
                        "VOICE",
                    }:
                        dynamic_contact = True
                    inspect(nested_value, normalized)
            elif isinstance(value, list):
                if parent_key in {"to", "recipient", "recipients", "addresses"} and len(value) > 1:
                    dynamic_bulk = True
                for item in value:
                    inspect(item, parent_key)
            elif isinstance(value, str) and value.lstrip().startswith(("{", "[")):
                try:
                    decoded = json.loads(value)
                except json.JSONDecodeError:
                    return
                inspect(decoded, parent_key)

        inspect(body)
        if dynamic_contact:
            risks.update({"outbound_contact", "spend"})
        if dynamic_bulk:
            risks.add("bulk")
    return sorted(risks)


def is_effectful(operation: dict[str, Any], input_obj: dict[str, Any]) -> bool:
    risks = set(classify_risks(operation, input_obj))
    return "write" in risks or bool(risks & _EFFECT_RISKS)


def required_acknowledgements(operation: dict[str, Any], input_obj: dict[str, Any]) -> list[str]:
    risks = classify_risks(operation, input_obj)
    if not is_effectful(operation, input_obj):
        return []
    required = {_ACK_BY_RISK[risk] for risk in risks if risk in _ACK_BY_RISK}
    if "write" in risks:
        if operation.get("snapshot_required") is True:
            required.add("snapshot_in")
        elif str(operation.get("snapshot_strategy", "")).startswith("no_snapshot"):
            required.add("ack_no_snapshot")
        else:
            required.add("snapshot_in_or_ack_no_snapshot")
    return sorted(required)


def build_plan(
    operation: dict[str, Any],
    input_obj: dict[str, Any],
    cfg: Config,
    inventory_hash: str,
    tool_version: str,
    *,
    snapshot_command: str | None = None,
    snapshot_receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    risks = classify_risks(operation, input_obj)
    target_count = _explicit_target_count(input_obj, bulk="bulk" in risks)
    if "bulk" in risks:
        if target_count is None:
            raise SafetyError("Refused: bulk input must contain an explicit target list")
        if target_count < 1 or target_count > 25:
            raise SafetyError("Refused: bulk work must contain between 1 and 25 targets")
    input_hash = _stable_hash(input_obj)
    binding = {
        "command": operation["command"],
        "env_fingerprint": cfg.fingerprint,
        "input_sha256": input_hash,
        "inventory_sha256": inventory_hash,
        "snapshot_sha256": snapshot_receipt.get("sha256") if snapshot_receipt else None,
        "target_count": target_count,
        "tool_version": tool_version,
    }
    plan_id = _stable_hash(binding)
    pii_fields = {item["field"] for item in operation.get("pii_fields", [])}
    return {
        "schema_version": 1,
        "tool": "qwayk-twilio-safe-agent-cli",
        "plan_id": plan_id,
        "binding": binding,
        "operation": {
            "command": operation["command"],
            "method": operation["method"],
            "server": operation["server"],
            "path": operation["path"],
            "account_fingerprint": cfg.fingerprint,
            "region": cfg.region or "us1",
            "edge": cfg.edge or "automatic",
        },
        "target_preview": redact(
            input_obj,
            pii_fields=pii_fields,
            secret_values=cfg.redaction_values(),
        ),
        "input_sha256": input_hash,
        "risks": risks,
        "expected_effect": _expected_effect(risks, operation),
        "target_count": target_count,
        "snapshot": {
            "strategy": operation.get("snapshot_strategy"),
            "read_command": snapshot_command,
            "file": (
                {
                    "name": str(snapshot_receipt.get("path", "")).rsplit("/", 1)[-1],
                    "sha256": snapshot_receipt.get("sha256"),
                    "bytes": snapshot_receipt.get("bytes"),
                    "protected_mode": snapshot_receipt.get("protected_mode"),
                }
                if snapshot_receipt
                else None
            ),
            "warning": (
                "A protected before-state file is bound to this plan."
                if snapshot_receipt
                else "No provider snapshot is available for this action."
                if str(operation.get("snapshot_strategy", "")).startswith("no_snapshot")
                and "write" in risks
                else "This effectful read does not change provider state, so no snapshot is needed."
                if "write" not in risks
                else "Save the current state with the paired read command or acknowledge that no snapshot was supplied."
            ),
        },
        "verification_strategy": operation.get("verification_strategy"),
        "required_acknowledgements": required_acknowledgements(operation, input_obj),
    }


def verify_plan(
    plan: dict[str, Any],
    operation: dict[str, Any],
    input_obj: dict[str, Any],
    cfg: Config,
    inventory_hash: str,
    tool_version: str,
    *,
    snapshot_command: str | None = None,
    snapshot_receipt: dict[str, Any] | None = None,
) -> None:
    expected = build_plan(
        operation,
        input_obj,
        cfg,
        inventory_hash,
        tool_version,
        snapshot_command=snapshot_command,
        snapshot_receipt=snapshot_receipt,
    )
    if plan != expected:
        raise SafetyError("Refused: the reviewed plan does not match this command, account, input, inventory, or tool version")


def enforce_approvals(
    plan: dict[str, Any],
    acknowledgements: dict[str, bool],
    *,
    apply: bool,
    yes: bool,
    snapshot_in: str | None,
    target_count: int | None,
) -> None:
    if not apply or not yes:
        raise SafetyError("Refused: live apply requires both --apply and --yes")
    missing: list[str] = []
    for requirement in plan.get("required_acknowledgements", []):
        if requirement == "snapshot_in":
            if not snapshot_in:
                missing.append("--snapshot-in")
        elif requirement == "snapshot_in_or_ack_no_snapshot":
            if not snapshot_in and not acknowledgements.get("ack_no_snapshot", False):
                missing.append("--snapshot-in or --ack-no-snapshot")
        elif not acknowledgements.get(requirement, False):
            missing.append("--" + requirement.replace("_", "-"))
    if "bulk" in plan.get("risks", []):
        if target_count is None or target_count < 1 or target_count > 25:
            missing.append("--target-count between 1 and 25")
        bound_target_count = plan.get("target_count")
        if bound_target_count is not None and target_count != bound_target_count:
            missing.append(f"--target-count exactly {bound_target_count} to match the reviewed input")
    if missing:
        raise SafetyError("Refused: missing required approval: " + ", ".join(sorted(set(missing))))


def provider_status_summary(value: Any) -> dict[str, Any]:
    status: str | None = None
    if isinstance(value, dict):
        for key in ("status", "Status", "state", "State"):
            if value.get(key) is not None:
                status = str(value[key]).lower()
                break
    return {
        "provider_status": status or "not_reported",
        "accepted": status in {"accepted", "queued", "scheduled", "sending", "sent", "delivered", "completed"},
        "delivered": status in {"delivered", "read"},
        "completed": status == "completed",
        "note": (
            "Twilio reported delivery."
            if status in {"delivered", "read"}
            else "Twilio did not report delivery; accepted, queued, sent, and completed are kept distinct."
        ),
    }


def _expected_effect(risks: list[str], operation: dict[str, Any]) -> str:
    if operation.get("expected_effect"):
        return str(operation["expected_effect"])
    if "outbound_contact" in risks:
        return "May contact a real person or route a communication."
    if "destructive" in risks:
        return "May delete, release, cancel, or close a Twilio resource."
    if "spend" in risks:
        return "May create Twilio usage or cost."
    if "write" in risks:
        return "May change live Twilio account state."
    return "Reads Twilio state without changing it."
