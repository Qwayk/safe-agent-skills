from __future__ import annotations

import contextlib
import hashlib
import hmac
import json
import secrets
import time
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .errors import ProviderStatusError, SafetyError, ToolError, ValidationError
from .json_files import read_json_file, write_json_file
from .operations import OPERATIONS, OperationSpec, get_operation
from .redaction import redact_object

PLAN_SCHEMA_VERSION = "2.0"
PLAN_TOOL = "namebright-safe-cli"
PLAN_DEFAULT_VERSION = "0.1.0"

_PURCHASE_COMMANDS = {"purchase register", "purchase renew"}
_PRICE_UNAVAILABLE = "NameBright did not give a usable price for this purchase. Check and complete it in NameBright checkout."
_PURCHASE_WARNINGS = (
    "NameBright charges the account's funded balance.",
    "NameBright purchases are non-refundable.",
    "Review the price, domain, and years together. NameBright sets the final charge.",
)

_SCALAR_MESSAGE_FIELDS = {
    "Email",
    "EmailAddress",
    "PhoneNumber",
    "PhoneNumberVerificationMethod",
    "DomainName",
    "domain",
}

_CONTACT_VERIFY_COMMANDS = {
    "contacts update-administrative": "contacts get-administrative",
    "contacts update-all": "contacts get-all",
    "contacts update-registrant": "contacts get-registrant",
    "contacts update-technical": "contacts get-technical",
}


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _build_target_from_values(values: dict[str, Any]) -> dict[str, str] | None:
    if "DomainName" in values:
        return {"kind": "DomainName", "value": str(values["DomainName"])}
    if "domain" in values:
        return {"kind": "domain", "value": str(values["domain"])}
    return None


def _canonicalize_scalar(value: Any, field: Any) -> Any:
    if isinstance(value, str):
        value = value.strip()
    if field.kind == "int":
        try:
            value = int(value)
        except (TypeError, ValueError) as e:
            raise ValidationError(f"{field.api_name} must be an integer") from e
        if field.positive and value <= 0:
            raise ValidationError(f"{field.api_name} must be a positive integer")
        return value

    if field.kind == "bool":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "1", "yes", "y"}:
                return True
            if lowered in {"false", "0", "no", "n"}:
                return False
            raise ValidationError(f"{field.api_name} must be boolean-like")
        raise ValidationError(f"{field.api_name} must be boolean")

    return value


def _canonical_values(spec: OperationSpec, values: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(values, dict):
        raise ValidationError("values must be a mapping")

    cli_fields = [f for f in spec.fields if f.source == "cli"]
    if not cli_fields:
        return {}

    provided = {str(k): v for k, v in values.items()}
    allowed = {f.api_name for f in cli_fields}
    unknown = set(provided) - allowed
    if unknown:
        raise ValidationError(f"Unknown values for {spec.family}:{spec.command}: {', '.join(sorted(unknown))}")

    out: dict[str, Any] = {}

    for field in cli_fields:
        if field.kind == "secret_file":
            if field.api_name in provided:
                raise ValidationError(f"Secret value for {field.api_name} must be provided in secret_values")
            continue

        if field.api_name in provided:
            raw = provided[field.api_name]
        elif field.default is not None:
            raw = field.default
        elif field.required:
            raise ValidationError(f"Missing required value for {field.api_name}")
        else:
            continue

        if raw is None:
            if field.required:
                raise ValidationError(f"Missing required value for {field.api_name}")
            continue

        if isinstance(raw, (list, dict, tuple)):
            raise ValidationError(f"{field.api_name} must be scalar")

        normalized = _canonicalize_scalar(raw, field)

        if field.choices and str(normalized) not in {str(c) for c in field.choices}:
            raise ValidationError(f"{field.api_name} must be one of: {', '.join(field.choices)}")

        out[field.api_name] = normalized

    if spec.external_message:
        for name in _SCALAR_MESSAGE_FIELDS:
            if name not in out:
                continue
            if isinstance(out[name], (list, dict, tuple)):
                raise ValidationError(f"External message field {name} must be scalar")

    if spec.command in _PURCHASE_COMMANDS:
        if "DomainName" not in out:
            raise ValidationError("Refused: purchase operations require DomainName")
        years = out.get("Years")
        if years is None:
            raise ValidationError("Refused: purchase operations require Years")
        if not isinstance(years, int) or years <= 0:
            raise ValidationError("Years must be a positive integer")

    if "DomainName" in out and "domain" in out and str(out["DomainName"]) != str(out["domain"]):
        raise ValidationError("DomainName and domain values must match")

    return out


def _operation_ref_key(operation_ref: str) -> tuple[str, str]:
    if ":" not in operation_ref:
        raise ValidationError(f"Invalid operation ref: {operation_ref}")
    family, _, command = operation_ref.partition(":")
    if not family or not command:
        raise ValidationError(f"Invalid operation ref: {operation_ref}")
    return family, command


def _lookup_operation_ref(operation_ref: str) -> OperationSpec:
    family, command = _operation_ref_key(operation_ref)
    operation = get_operation(family, command)
    if operation is None:
        raise ValidationError(f"Unknown operation ref: {operation_ref}")
    return operation


def _required_acknowledgements(spec: OperationSpec) -> tuple[str, ...]:
    required = list(spec.required_acks)
    if spec.no_snapshot:
        required.append("ack_no_snapshot")
    if spec.external_message:
        required.append("ack_external_message")
    return tuple(sorted(set(required)))


def _is_known_write_operation(spec: OperationSpec) -> bool:
    return any(op is spec for op in OPERATIONS) and bool(spec.write_capable)


def _extract_payload(response: Any) -> dict[str, Any] | list[Any] | None:
    if response is None:
        return None
    if isinstance(response, (dict, list)):
        return response
    payload = getattr(response, "payload", None)
    if isinstance(payload, (dict, list)):
        return payload
    return None


def _canonical_sha256(value: Any) -> str:
    blob = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _contact_display_values(
    spec: OperationSpec,
    values: dict[str, Any],
) -> dict[str, Any]:
    if spec.family != "contacts":
        return dict(values)
    redacted = redact_object(values, redact_pii=True)
    return redacted if isinstance(redacted, dict) else {}


def _contact_expected_fields(
    spec: OperationSpec,
    values: dict[str, Any],
) -> dict[str, Any]:
    return {
        field.api_name: values[field.api_name]
        for field in spec.fields
        if field.location == "body"
        and field.source == "cli"
        and field.api_name in values
    }


def _project_snapshot_values(source_spec: OperationSpec, values: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for field in source_spec.fields:
        if field.source != "cli":
            continue
        if field.api_name in values:
            out[field.api_name] = values[field.api_name]
            continue
        if field.api_name == "domain" and "DomainName" in values:
            out[field.api_name] = values["DomainName"]
        if field.api_name == "DomainName" and "domain" in values:
            out[field.api_name] = values["domain"]

    for field in source_spec.fields:
        if field.location in {"path", "query"} and field.source == "cli" and field.required and field.api_name not in out:
            raise ValidationError(f"Missing required {source_spec.family}:{source_spec.command} value for {field.api_name}")

    return out


def _normalize_key(name: str) -> str:
    return str(name).lower().replace("-", "").replace("_", "").replace(" ", "")


def _is_available_status_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    return text in {"true", "1", "yes", "y", "available"}


def _is_available_for_registration(payload: dict[str, Any]) -> bool:
    values = _normalized_keys(payload)
    raw_status = values.get("availableforregistration")
    if raw_status is not None:
        return _is_available_status_value(raw_status)
    return _availability_status(values) in {"available", "availableforregistration", "ready", "ok"}


def _normalized_keys(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    return {_normalize_key(key): value for key, value in payload.items()}


def _availability_status(values: dict[str, Any]) -> str:
    for key in ("status", "availability", "registrationstatus"):
        if values.get(key) is not None:
            return _normalize_key(str(values[key]).strip())
    if "availableforregistration" in values:
        return "available" if _is_available_status_value(values["availableforregistration"]) else "unavailable"
    return ""


def _run_read(
    *,
    client: Any,
    operation_ref: str,
    values: dict[str, Any],
    allow_fail: bool,
    context: str,
) -> dict[str, Any]:
    spec = _lookup_operation_ref(operation_ref)
    try:
        response = client.execute_operation(spec, values=values)
        payload = _extract_payload(response)
    except Exception:
        if allow_fail:
            return {
                "op": f"{spec.family}:{spec.command}",
                "ok": False,
                "note": "snapshot_unavailable",
                "payload": None,
            }
        raise SafetyError(f"Refused: {context} for {operation_ref}") from None

    if not isinstance(payload, (dict, list)):
        if allow_fail:
            return {
                "op": f"{spec.family}:{spec.command}",
                "ok": False,
                "note": "snapshot_unavailable",
                "payload": None,
            }
        raise SafetyError(f"Refused: {context} for {operation_ref}")

    snapshot: dict[str, Any] = {
        "op": f"{spec.family}:{spec.command}",
        "ok": True,
        "payload": redact_object(payload, redact_pii=True),
    }
    if spec.family == "contacts":
        snapshot_sha256 = getattr(response, "snapshot_sha256", None)
        if not isinstance(snapshot_sha256, str) or len(snapshot_sha256) != 64:
            if allow_fail:
                return {
                    "op": f"{spec.family}:{spec.command}",
                    "ok": False,
                    "note": "raw_snapshot_digest_unavailable",
                    "payload": None,
                }
            raise SafetyError(f"Refused: {context} digest unavailable for {operation_ref}")
        snapshot["raw_snapshot_sha256"] = snapshot_sha256
    return snapshot


def _run_verify(*, client: Any, spec: OperationSpec, values: dict[str, Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for operation_ref in spec.verify_commands:
        verify_spec = _lookup_operation_ref(operation_ref)
        try:
            mapped = _project_snapshot_values(verify_spec, values)
        except ValidationError:
            results.append({"op": f"{verify_spec.family}:{verify_spec.command}", "ok": False, "payload": None, "note": "verification_inputs_missing"})
            continue
        try:
            response = client.execute_operation(verify_spec, values=mapped)
            payload = _extract_payload(response)
        except Exception:
            results.append({"op": f"{verify_spec.family}:{verify_spec.command}", "ok": False, "payload": None, "note": "verification_error"})
            continue

        if not isinstance(payload, (dict, list)):
            results.append(
                {
                    "op": f"{verify_spec.family}:{verify_spec.command}",
                    "ok": False,
                    "payload": None,
                    "note": "verification_invalid_payload",
                }
            )
            continue

        result: dict[str, Any] = {
            "op": f"{verify_spec.family}:{verify_spec.command}",
            "ok": True,
            "payload": redact_object(payload, redact_pii=True),
        }
        if (
            spec.family == "contacts"
            and verify_spec.family == "contacts"
            and _CONTACT_VERIFY_COMMANDS.get(spec.command) == verify_spec.command
        ):
            expected_fields = _contact_expected_fields(spec, values)
            compare = getattr(response, "compare_contact_fields", None)
            comparison = compare(expected_fields) if callable(compare) else None
            if isinstance(comparison, dict):
                matched = sorted(str(name) for name in comparison.get("matched", []))
                mismatched = sorted(
                    str(name) for name in comparison.get("mismatched", [])
                )
                unavailable = sorted(
                    str(name) for name in comparison.get("unavailable", [])
                )
                result["field_matches"] = matched
                result["field_mismatches"] = mismatched
                result["field_unavailable"] = unavailable
                result["ok"] = not mismatched and not unavailable
        results.append(result)
    return results


def _price(value: Any) -> Decimal | None:
    try:
        amount = Decimal(str(value))
    except InvalidOperation:
        return None
    if not amount.is_finite() or amount < 0:
        return None
    return amount


def _quote_from_availability(
    payload: dict[str, Any], *, years: int, domain: str, for_registration: bool,
) -> dict[str, Any] | None:
    values = _normalized_keys(payload)
    status = _availability_status(values)
    accepted = (
        _is_available_for_registration(payload)
        if for_registration
        else status in {"availableforrenewal", "available", "ready", "ok"}
    )
    if not accepted:
        return None
    for key in ("domainname", "domain"):
        if key in values and str(values[key]).rstrip(".").casefold() != domain.rstrip(".").casefold():
            return None

    price_fields = _normalized_keys(values.get("prices") or values.get("price"))
    promotion_fields = _normalized_keys(values.get("promotion"))
    unit = _price(values.get("unitprice", price_fields.get("unitprice")))
    if unit is None:
        return None
    promotion = _price(
        promotion_fields.get("promotionprice", values.get("promotionprice", price_fields.get("promotionprice")))
    )
    quoted_unit = unit
    if years == 1 and promotion is not None and 0 < promotion < unit:
        quoted_unit = promotion

    quote: dict[str, Any] = {
        "status": status or "availableforregistration",
        "unit_price": format(unit.normalize(), "f"),
        "quoted_unit_price": format(quoted_unit.normalize(), "f"),
        "quoted_total_price": format((quoted_unit * years).normalize(), "f"),
        "domain": domain,
        "years": years,
    }
    if promotion is not None and promotion > 0:
        quote["promotion_price"] = format(promotion.normalize(), "f")
    return quote


def _fingerprint(plan_body: dict[str, Any]) -> str:
    body = {key: value for key, value in plan_body.items() if key not in {"fingerprint", "plan_signature"}}
    return _canonical_sha256(body)


def _receipt_directory(settings_file: str | None, plan_path: Path) -> Path:
    folder = Path(settings_file).expanduser().resolve().parent if settings_file else plan_path.resolve().parent
    state = folder / ".state"
    receipts = state / "receipts"
    if state.is_symlink() or receipts.is_symlink():
        raise SafetyError("Choose a settings folder with a local .state/receipts directory.")
    return receipts


def _protect_plan_output(path: Path, *, settings_file: str | None, receipts: Path) -> None:
    if path.resolve().is_relative_to(receipts):
        raise SafetyError("Choose a plan path outside the receipt folder.")
    if settings_file:
        settings = Path(settings_file).expanduser()
        if path.resolve() == settings.resolve() or (path.exists() and settings.exists() and path.samefile(settings)):
            raise SafetyError("Choose a plan path separate from the settings file.")


def _secret_fields_for_operation(spec: OperationSpec) -> tuple[str, ...]:
    return tuple(sorted(field.api_name for field in spec.fields if field.source == "cli" and field.kind == "secret_file"))


def _snapshot_refs(spec: OperationSpec) -> tuple[str, ...]:
    if spec.family in {"inbound-push", "outbound-push"}:
        completed = f"{spec.family}:{spec.family} list-completed"
        return tuple(dict.fromkeys((*spec.snapshot_commands, completed)))
    return spec.snapshot_commands


def _snapshot_payload(records: list[dict[str, Any]], op: str) -> Any:
    return next((record["payload"] for record in records if record["op"] == op and record["ok"]), None)


def _push_records(payload: Any, domain: str, action: str) -> set[str] | None:
    if not isinstance(payload, list):
        return None
    found = set()
    for item in payload:
        fields = _normalized_keys(item)
        name = item if isinstance(item, str) else fields.get("domain", fields.get("domainname"))
        actual = _normalize_key(str(fields.get("pushaction", "")))
        if not isinstance(name, str) or name.rstrip(".").casefold() != domain:
            continue
        if actual == action or (action == "requested" and isinstance(item, str)):
            found.add(_canonical_sha256(item))
    return found


def _verify_push(
    client: Any, spec: OperationSpec, values: dict[str, Any], snapshots: list[dict[str, Any]],
) -> dict[str, Any]:
    domain = values["domain"].rstrip(".").casefold()
    _, verb = spec.command.split(" ", 1)
    action = "declined" if verb.startswith(("decline-", "cancel-")) else "accepted"
    results = []
    for suffix, expected, status in (("completed", action, action), ("pending", "requested", "pending")):
        if suffix == "pending" and not verb.startswith(("initiate-", "force-")):
            continue
        ref = f"{spec.family}:{spec.family} list-{suffix}"
        previous = _push_records(_snapshot_payload(snapshots, ref), domain, expected)
        result = _run_read(client=client, operation_ref=ref, values={}, allow_fail=True, context="verification")
        current = _push_records(result["payload"], domain, expected)
        matched = previous is not None and current is not None and bool(current - previous)
        results.append({"op": ref, "ok": matched, "state": status if matched else "unconfirmed"})
        if matched:
            return {"ok": True, "state": status, "results": results}
    return {"ok": False, "state": "unconfirmed", "results": results}


def _expiry(payload: Any) -> date | None:
    value = str(_normalized_keys(payload).get("expirationdate", ""))
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _verify_purchase(
    client: Any, spec: OperationSpec, values: dict[str, Any], snapshots: list[dict[str, Any]],
) -> dict[str, Any]:
    domain = values["DomainName"]
    ref = "domains:domains get"
    result = _run_read(client=client, operation_ref=ref, values={"domain": domain}, allow_fail=True, context="verification")
    payload = _normalized_keys(result["payload"])
    advanced = True
    if spec.command == "purchase renew":
        before = _expiry(_snapshot_payload(snapshots, ref))
        after = _expiry(result["payload"])
        advanced = before is not None and after is not None and after > before
    matched = (
        result["ok"] and isinstance(payload.get("domainname"), str)
        and payload["domainname"].rstrip(".").casefold() == domain.rstrip(".").casefold()
        and advanced
    )
    result["ok"] = matched
    return {"ok": matched, "results": [result]}


def _check_order(client: Any, number: str) -> dict[str, Any]:
    ref = "orders:orders get"
    result = _run_read(
        client=client,
        operation_ref=ref,
        values={"customerOrderNumber": number},
        allow_fail=True,
        context="order lookup",
    )
    order = _normalized_keys(result["payload"])
    order_id = order.get("orderid")
    result["ok"] = type(order_id) is int and order_id > 0 and isinstance(order.get("orderitems"), list)
    return result


def _snapshot_records_for_create(
    spec: OperationSpec,
    *,
    values: dict[str, Any],
    client: Any,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    snapshots: list[dict[str, Any]] = []
    quote_info: dict[str, Any] | None = None

    for ref in _snapshot_refs(spec):
        snapshot_spec = _lookup_operation_ref(ref)
        try:
            mapped_values = _project_snapshot_values(snapshot_spec, values)
        except ValidationError:
            snapshots.append({
                "op": ref,
                "ok": False,
                "note": "snapshot_unavailable",
                "payload": None,
            })
            continue

        snapshot = _run_read(
            client=client,
            operation_ref=ref,
            values=mapped_values,
            allow_fail=True,
            context="snapshot",
        )
        snapshots.append(snapshot)
        if snapshot_spec.family == "contacts" and not snapshot.get("ok"):
            raise SafetyError(
                f"Refused: contact snapshot digest unavailable for {ref}"
            )

        if spec.command in _PURCHASE_COMMANDS and snapshot_spec.command == "purchase availability" and snapshot.get("ok"):
            payload = snapshot.get("payload")
            if isinstance(payload, dict):
                if spec.family == "purchase" and spec.command == "purchase register" and not _is_available_for_registration(payload):
                    raise SafetyError("Refused: domain not available for registration")
                quote_info = _quote_from_availability(
                    payload, years=values["Years"], domain=values["DomainName"],
                    for_registration=spec.command == "purchase register",
                )

    return snapshots, quote_info


def _validate_snapshot_drift(plan: dict[str, Any], snapshots: list[dict[str, Any]]) -> None:
    saved_by_op = {}
    for snapshot in plan.get("snapshots", []):
        if not isinstance(snapshot, dict):
            continue
        if not snapshot.get("ok"):
            continue
        op = snapshot.get("op")
        if isinstance(op, str):
            saved_by_op[op] = snapshot

    current_by_op = {
        snapshot.get("op"): snapshot
        for snapshot in snapshots
        if isinstance(snapshot, dict) and isinstance(snapshot.get("op"), str)
    }

    for op, saved in saved_by_op.items():
        snapshot = current_by_op.get(op)
        if not isinstance(snapshot, dict) or not snapshot.get("ok"):
            if saved.get("raw_snapshot_sha256") is not None:
                raise SafetyError(f"Refused: snapshot drift for {op}")
            continue
        saved_digest = saved.get("raw_snapshot_sha256")
        current_digest = snapshot.get("raw_snapshot_sha256")
        if saved_digest is not None or current_digest is not None:
            if (
                not isinstance(saved_digest, str)
                or not isinstance(current_digest, str)
                or saved_digest != current_digest
            ):
                raise SafetyError(f"Refused: snapshot drift for {op}")
            continue
        if saved.get("payload") != snapshot.get("payload"):
            raise SafetyError(f"Refused: snapshot drift for {op}")


def _snapshot_records_for_apply(
    spec: OperationSpec,
    *,
    values: dict[str, Any],
    client: Any,
    strict_purchase_recheck: bool,
) -> list[dict[str, Any]]:
    snapshots: list[dict[str, Any]] = []
    for ref in _snapshot_refs(spec):
        snapshot_spec = _lookup_operation_ref(ref)
        if strict_purchase_recheck:
            mapped_values = _project_snapshot_values(snapshot_spec, values)
        else:
            try:
                mapped_values = _project_snapshot_values(snapshot_spec, values)
            except ValidationError:
                snapshots.append({
                    "op": ref,
                    "ok": False,
                    "note": "snapshot_unavailable",
                    "payload": None,
                })
                continue

        snapshots.append(
            _run_read(
                client=client,
                operation_ref=ref,
                values=mapped_values,
                allow_fail=not strict_purchase_recheck or snapshot_spec.command == "purchase availability",
                context="pre-apply snapshot",
            )
        )
    return snapshots


def _build_plan_for_operation(
    *,
    spec: OperationSpec,
    values: dict[str, Any],
    client: Any,
    plan_out: str,
    tool_version: str,
) -> dict[str, Any]:
    if not plan_out:
        raise ValidationError("Missing plan_out")

    snapshots, quote_info = _snapshot_records_for_create(spec, values=values, client=client)

    plan: dict[str, Any] = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "tool": PLAN_TOOL,
        "tool_version": tool_version,
        "operation": {
            "family": spec.family,
            "command": spec.command,
            "method": spec.method,
            "path": spec.path,
        },
        "generated_at_utc": _utc_now(),
        "plan_id": secrets.token_hex(16),
        "values": _contact_display_values(spec, values),
        "target": _build_target_from_values(values),
        "risk": spec.risk,
        "required_acknowledgements": list(_required_acknowledgements(spec)),
        "flags": {
            "no_snapshot": bool(spec.no_snapshot),
            "external_message": bool(spec.external_message),
        },
        "verification_refs": list(spec.verify_commands),
        "snapshot_refs": list(_snapshot_refs(spec)),
        "snapshots": snapshots,
        "secret_field_names": _secret_fields_for_operation(spec),
    }

    if quote_info is not None:
        plan["purchase_quote"] = quote_info
    if spec.family == "contacts":
        plan["contact_values_sha256"] = _canonical_sha256(values)

    warnings: list[str] = []
    if spec.no_snapshot:
        warnings.append(
            "Readable before-state is included when available, but it is not a reliable restore path."
        )
    if spec.command in _PURCHASE_COMMANDS:
        warnings.extend(_PURCHASE_WARNINGS)
        if quote_info is None:
            warnings.append(_PRICE_UNAVAILABLE)
    if spec.command.startswith("outbound-push force-"):
        warnings.append("NameBright listed this command in July. Its current API guide omits it.")
    if warnings:
        plan["warnings"] = warnings

    return plan


def _validate_plan_identity(
    *,
    spec: OperationSpec,
    values: dict[str, Any],
    plan: dict[str, Any],
    tool_version: str,
) -> None:
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")

    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise SafetyError("This plan is from an older version. Save and review a new plan.")
    if plan.get("tool") != PLAN_TOOL:
        raise ValidationError("Plan file has wrong tool")
    if plan.get("tool_version") != tool_version:
        raise ValidationError("Plan file has unsupported tool version")

    expected = _fingerprint(plan)
    if plan.get("fingerprint") != expected:
        raise SafetyError("Refused: plan fingerprint mismatch")

    plan_op = plan.get("operation")
    if not isinstance(plan_op, dict):
        raise ValidationError("Plan file missing operation")

    for key in ("family", "command", "method", "path"):
        if plan_op.get(key) != getattr(spec, key):
            raise ValidationError("Refused: plan target does not match requested operation")

    if spec.family == "contacts":
        if plan.get("values") != _contact_display_values(spec, values):
            raise ValidationError("Refused: plan values do not match requested values")
        if plan.get("contact_values_sha256") != _canonical_sha256(values):
            raise ValidationError("Refused: plan contact values do not match requested values")
    elif plan.get("values") != values:
        raise ValidationError("Refused: plan values do not match requested values")

    requested_target = _build_target_from_values(values)
    plan_target = plan.get("target")
    if requested_target is not None or plan_target is not None:
        if requested_target != plan_target:
            raise ValidationError("Refused: plan target does not match requested target")


def _validate_acknowledgements(spec: OperationSpec, *, acknowledgements: dict[str, bool] | None) -> None:
    required = set(_required_acknowledgements(spec))
    provided = acknowledgements or {}
    for required_ack in sorted(required):
        if not bool(provided.get(required_ack)):
            raise SafetyError(f"Refused: missing required acknowledgement: {required_ack}")


def _validate_secret_inputs(spec: OperationSpec, secret_values: dict[str, Any] | None) -> dict[str, str]:
    required = set(_secret_fields_for_operation(spec))
    provided = secret_values or {}

    if not isinstance(provided, dict):
        raise ValidationError("secret_values must be a mapping")

    provided_names = {str(k) for k in provided}

    if set(provided_names) != required:
        missing = sorted(required - provided_names)
        extra = sorted(provided_names - required)
        if missing:
            raise ValidationError("Refused: missing required secret fields: " + ", ".join(missing))
        raise ValidationError("Refused: extra secret fields: " + ", ".join(extra))

    normalized: dict[str, str] = {}
    for key, value in provided.items():
        sval = str(value)
        if isinstance(value, (list, dict, tuple)):
            raise ValidationError(f"Refused: secret value for {key} must be scalar")
        normalized[str(key)] = sval

    return normalized


def _validate_purchase_drift(spec: OperationSpec, normalized: dict[str, Any], plan: dict[str, Any], snapshots: list[dict[str, Any]]) -> None:
    if spec.command not in _PURCHASE_COMMANDS:
        return
    saved = plan.get("purchase_quote")
    if not isinstance(saved, dict):
        raise SafetyError(_PRICE_UNAVAILABLE)
    availability = _snapshot_payload(snapshots, "purchase:purchase availability")
    current = _quote_from_availability(
        _normalized_keys(availability), years=normalized["Years"], domain=normalized["DomainName"],
        for_registration=spec.command == "purchase register",
    )
    if current is None:
        raise SafetyError(_PRICE_UNAVAILABLE)
    if current != saved:
        raise SafetyError("NameBright changed the availability or price. Save and review a new plan.")


def create_plan(
    spec: OperationSpec,
    values: dict[str, Any],
    *,
    plan_out: str,
    client: Any,
    tool_version: str = PLAN_DEFAULT_VERSION,
    settings_file: str | None = None,
) -> dict[str, Any]:
    if not _is_known_write_operation(spec):
        raise ValidationError("Refused: unknown or non-write operation for planning")
    if not plan_out:
        raise ValidationError("Missing plan_out")

    path = Path(plan_out).expanduser()
    receipt_dir = _receipt_directory(settings_file, path)
    _protect_plan_output(path, settings_file=settings_file, receipts=receipt_dir)
    normalized = _canonical_values(spec, values)
    plan = _build_plan_for_operation(spec=spec, values=normalized, client=client, plan_out=plan_out, tool_version=tool_version)
    plan["fingerprint"] = _fingerprint(plan)
    plan["plan_signature"] = client.sign_plan(plan["fingerprint"], str(receipt_dir))
    write_json_file(path, plan)
    return plan


def _reserve_receipts(directory: Path, custom: Path, canonical: Path, receipt: dict[str, Any]) -> None:
    if canonical.exists() or canonical.is_symlink():
        raise SafetyError(f"This plan already has an attempt receipt at {canonical}. Check NameBright before making a new plan.")
    if custom.is_relative_to(directory) or custom.exists() or custom.is_symlink():
        raise SafetyError("Choose a new receipt file separate from the settings, plan, and saved receipts.")

    custom_reserved = False
    try:
        directory.parent.mkdir(mode=0o700, exist_ok=True)
        directory.mkdir(mode=0o700, exist_ok=True)
        write_json_file(custom, receipt, exclusive=True)
        custom_reserved = True
        write_json_file(canonical, receipt, exclusive=True)
    except OSError as exc:
        if custom_reserved:
            with contextlib.suppress(OSError):
                custom.unlink()
        if canonical.exists():
            raise SafetyError(f"This plan already has an attempt receipt at {canonical}. Check NameBright before making a new plan.") from exc
        raise SafetyError("Could not save the starting receipt. Choose a writable new receipt path.") from exc


def _save_receipts(canonical: Path, custom: Path, receipt: dict[str, Any]) -> bool:
    try:
        write_json_file(canonical, receipt)
        write_json_file(custom, receipt)
    except OSError:
        receipt["receipt_written"] = False
        receipt["next_step"] = "The final receipt could not be saved. Check NameBright before making a new plan."
        return False
    return True


def apply_plan(
    spec: OperationSpec,
    values: dict[str, Any],
    *,
    plan_in: str,
    receipt_out: str,
    client: Any,
    yes: bool,
    acknowledgements: dict[str, bool] | None,
    secret_values: dict[str, str] | None,
    tool_version: str = PLAN_DEFAULT_VERSION,
    settings_file: str | None = None,
) -> dict[str, Any]:
    if not _is_known_write_operation(spec):
        raise ValidationError("Refused: unknown or non-write operation for apply")
    if not yes:
        raise SafetyError("Refused: apply requires --yes")
    if not receipt_out or not plan_in:
        raise ValidationError("Apply needs a saved plan and a new receipt path.")

    plan_path = Path(plan_in).expanduser()
    plan = read_json_file(plan_path)
    normalized = _canonical_values(spec, values)
    _validate_plan_identity(spec=spec, values=normalized, plan=plan, tool_version=tool_version)
    _validate_acknowledgements(spec, acknowledgements=acknowledgements)
    secret_map = _validate_secret_inputs(spec, secret_values=secret_values)

    directory = _receipt_directory(settings_file, plan_path)
    expected = client.sign_plan(plan["fingerprint"], str(directory))
    saved_signature = plan.get("plan_signature")
    if not isinstance(saved_signature, str) or not hmac.compare_digest(saved_signature.encode(), expected.encode()):
        raise SafetyError("Use the same NameBright credentials and settings folder, or save and review a new plan.")
    custom = Path(receipt_out).expanduser()
    if custom.is_symlink() or custom.resolve() == plan_path.resolve():
        raise SafetyError("Choose a new receipt file separate from the settings, plan, and saved receipts.")
    custom = custom.resolve()
    canonical = directory / f"{plan['fingerprint']}.receipt.json"
    if canonical.exists() or canonical.is_symlink():
        raise SafetyError(f"This plan already has an attempt receipt at {canonical}. Check NameBright before making a new plan.")
    if custom.exists() or custom.is_relative_to(directory):
        raise SafetyError("Choose a new receipt file separate from the settings, plan, and saved receipts.")
    if settings_file and custom == Path(settings_file).expanduser().resolve():
        raise SafetyError("Choose a new receipt file separate from the settings, plan, and saved receipts.")

    purchase = spec.command in _PURCHASE_COMMANDS
    if purchase and not isinstance(plan.get("purchase_quote"), dict):
        raise SafetyError(_PRICE_UNAVAILABLE)
    snapshots = _snapshot_records_for_apply(
        spec, values=normalized, client=client, strict_purchase_recheck=purchase,
    )
    _validate_purchase_drift(spec, normalized, plan, snapshots)
    _validate_snapshot_drift(plan=plan, snapshots=snapshots)

    receipt: dict[str, Any] = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "tool": PLAN_TOOL,
        "tool_version": tool_version,
        "operation": plan["operation"],
        "generated_at_utc": _utc_now(),
        "plan_fingerprint": plan["fingerprint"],
        "applied": False,
        "outcome": "unknown",
        "write": {"ok": False, "status": None, "response": None},
        "verification": {"ok": False, "results": []},
        "snapshot_before": snapshots,
        "receipt_written": True,
        "rollback_supported": False,
        "next_step": "Check NameBright before making a new plan. This request may have gone through.",
    }
    _reserve_receipts(directory, custom, canonical, receipt)

    try:
        response = client.execute_operation(spec, values={**normalized, **secret_map})
    except ProviderStatusError as exc:
        receipt["write"]["status"] = exc.status
        if 300 <= exc.status < 500 and exc.status not in {408, 409}:
            receipt["outcome"] = "rejected"
            receipt["next_step"] = "Check the reply from NameBright and save a new plan before trying again."
        _save_receipts(canonical, custom, receipt)
        return receipt
    except (RuntimeError, ToolError):
        _save_receipts(canonical, custom, receipt)
        return receipt

    status = response.status
    payload = _extract_payload(response)
    receipt["write"] = {
        "ok": True, "status": status,
        "response": redact_object(payload, secret_values=tuple(secret_map.values()), redact_pii=True),
    }
    if status == 202:
        receipt["outcome"] = "paid_pending" if purchase else "pending"
        receipt["next_step"] = "Check the order or current state in NameBright before trying again."
        number = _normalized_keys(payload).get("customerordernumber")
        if purchase and isinstance(number, str) and number.strip():
            receipt["order_number"] = number
            if not _save_receipts(canonical, custom, receipt):
                return receipt
            order = _check_order(client, number)
            receipt["verification"] = {"ok": order["ok"], "results": [order]}
            if order["ok"]:
                receipt.update(outcome="accepted", applied=True)
                receipt.pop("next_step")
        _save_receipts(canonical, custom, receipt)
        return receipt

    receipt.update(outcome="accepted", applied=True)
    receipt.pop("next_step")
    if purchase:
        receipt["verification"] = _verify_purchase(client, spec, normalized, snapshots)
    elif spec.family in {"inbound-push", "outbound-push"}:
        receipt["verification"] = _verify_push(client, spec, normalized, snapshots)
    else:
        results = _run_verify(client=client, spec=spec, values=normalized)
        receipt["verification"] = {"ok": bool(results) and all(item.get("ok") for item in results), "results": results}

    if not receipt["verification"]["ok"]:
        receipt["next_step"] = "NameBright accepted the request. Check the result there before making a new plan."
    _save_receipts(canonical, custom, receipt)
    return receipt
