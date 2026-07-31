from __future__ import annotations

import hashlib
import json
import time
from typing import Any

from .errors import SafetyError, ValidationError
from .json_files import read_json_file, write_json_file
from .operations import OPERATIONS, OperationSpec, get_operation
from .redaction import redact_object

PLAN_SCHEMA_VERSION = "1.0"
PLAN_TOOL = "namebright-safe-cli"
PLAN_DEFAULT_VERSION = "0.1.0"

_PURCHASE_STATUS_KEYS = {
    "status",
    "availableforregistration",
    "available_for_registration",
}
_PURCHASE_PRICE_KEYS = (
    "unit_price",
    "promotion_price",
    "quoted_unit_price",
    "quoted_total_price",
)
_PURCHASE_WARNINGS = (
    "NameBright charges the account's funded balance.",
    "NameBright purchases are non-refundable.",
    "Approval is limited to the exact domain and duration in this plan.",
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

    if spec.family == "purchase" and spec.command in {"purchase register", "purchase renew"}:
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
    if not isinstance(payload, dict):
        return False

    raw_status = payload.get("AvailableForRegistration")
    if raw_status is not None:
        return _is_available_status_value(raw_status)

    for key, value in payload.items():
        if _normalize_key(key) in {"status", "availability", "registrationstatus"}:
            text = str(value).strip().lower()
            if text in {"available", "ready", "ok"}:
                return True
            if text in {"unavailable", "notavailable", "inactive", "blocked", "false", "0", "not ready", "disabled"}:
                return False
    return False


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


def _quote_from_availability(payload: dict[str, Any], *, years: int | None = None) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None

    status = payload.get("Status")
    if not isinstance(status, str):
        for key in _PURCHASE_STATUS_KEYS:
            if key in payload:
                status = "Available" if _is_available_for_registration(payload) else "Unavailable"
                break

    if status is None:
        return None

    if not isinstance(status, str):
        status = str(status)

    price_obj = payload.get("UnitPrice")
    if price_obj is None:
        price_blob = payload.get("Price")
        if isinstance(price_blob, dict):
            price_obj = price_blob.get("UnitPrice")

    unit_price = price_obj
    promotion_price = payload.get("PromotionPrice")
    promotion_obj = payload.get("Promotion")
    if isinstance(promotion_obj, dict):
        promotion_price = promotion_obj.get("PromotionPrice", promotion_price)
    if promotion_price is None and isinstance(payload.get("Prices"), dict):
        price_blob = payload.get("Prices")
        if isinstance(price_blob, dict):
            promotion_price = price_blob.get("PromotionPrice", promotion_price)
            if unit_price is None:
                unit_price = price_blob.get("UnitPrice", unit_price)
    if unit_price is None and isinstance(payload.get("Prices"), dict):
        unit_price = payload.get("Prices", {}).get("UnitPrice", unit_price)

    quote: dict[str, Any] = {"status": status}

    if unit_price is not None:
        quote["unit_price"] = unit_price
    if promotion_price is not None:
        quote["promotion_price"] = promotion_price

    quoted_unit = promotion_price if promotion_price is not None else unit_price
    if quoted_unit is not None:
        quote["quoted_unit_price"] = quoted_unit
        if isinstance(years, int) and years > 0:
            try:
                quote["quoted_total_price"] = float(quoted_unit) * years
            except (TypeError, ValueError):
                quote["quoted_total_price"] = quoted_unit

    return quote


def _fingerprint(plan_body: dict[str, Any]) -> str:
    body = dict(plan_body)
    body.pop("fingerprint", None)
    blob = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _secret_fields_for_operation(spec: OperationSpec) -> tuple[str, ...]:
    return tuple(sorted(field.api_name for field in spec.fields if field.source == "cli" and field.kind == "secret_file"))


def _snapshot_records_for_create(
    spec: OperationSpec,
    *,
    values: dict[str, Any],
    client: Any,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    snapshots: list[dict[str, Any]] = []
    quote_info: dict[str, Any] | None = None

    for ref in spec.snapshot_commands:
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

        if snapshot_spec.family == "purchase" and snapshot_spec.command == "purchase availability" and snapshot.get("ok"):
            payload = snapshot.get("payload")
            if isinstance(payload, dict):
                if spec.family == "purchase" and spec.command == "purchase register" and not _is_available_for_registration(payload):
                    raise SafetyError("Refused: domain not available for registration")
                current_quote = _quote_from_availability(
                    payload,
                    years=values.get("Years") if isinstance(values.get("Years"), int) else None,
                )
                if current_quote is not None:
                    if quote_info is None:
                        quote_info = dict(current_quote)
                    else:
                        quote_info.update(current_quote)

    if quote_info is not None:
        quote_info = dict(quote_info)
    if quote_info is not None:
        quote_info["domain"] = values.get("DomainName")
        quote_info["years"] = values.get("Years")

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
    for ref in spec.snapshot_commands:
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
                allow_fail=not strict_purchase_recheck,
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
        "values": _contact_display_values(spec, values),
        "target": _build_target_from_values(values),
        "risk": spec.risk,
        "required_acknowledgements": list(_required_acknowledgements(spec)),
        "flags": {
            "no_snapshot": bool(spec.no_snapshot),
            "external_message": bool(spec.external_message),
        },
        "verification_refs": list(spec.verify_commands),
        "snapshot_refs": list(spec.snapshot_commands),
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
    if spec.family == "purchase":
        warnings.extend(_PURCHASE_WARNINGS)
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
        raise ValidationError("Plan file missing schema_version")
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
    if spec.family != "purchase" or spec.command not in {"purchase register", "purchase renew"}:
        return

    plan_quote = plan.get("purchase_quote")
    if not isinstance(plan_quote, dict):
        return

    availability_snapshot = next((s for s in snapshots if s.get("op") == "purchase:purchase availability"), None)
    if availability_snapshot is None or not isinstance(availability_snapshot.get("payload"), dict):
        raise SafetyError("Refused: cannot re-read purchase availability")

    current_quote = _quote_from_availability(
        availability_snapshot["payload"],
        years=normalized.get("Years") if isinstance(normalized.get("Years"), int) else None,
    )
    if current_quote is None:
        raise SafetyError("Refused: cannot re-read purchase availability")

    if "status" in plan_quote and str(current_quote.get("status", "")).strip().lower() != str(plan_quote.get("status")).strip().lower():
        raise SafetyError("Refused: purchase availability status drift")

    for key in _PURCHASE_PRICE_KEYS:
        if key not in plan_quote:
            continue
        if current_quote.get(key) != plan_quote.get(key):
            raise SafetyError(f"Refused: purchase quoted {key} drift")


def create_plan(
    spec: OperationSpec,
    values: dict[str, Any],
    *,
    plan_out: str,
    client: Any,
    tool_version: str = PLAN_DEFAULT_VERSION,
) -> dict[str, Any]:
    if not _is_known_write_operation(spec):
        raise ValidationError("Refused: unknown or non-write operation for planning")

    normalized = _canonical_values(spec, values)
    plan = _build_plan_for_operation(spec=spec, values=normalized, client=client, plan_out=plan_out, tool_version=tool_version)
    plan["fingerprint"] = _fingerprint(plan)
    write_json_file(plan_out, plan)
    return plan


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
) -> dict[str, Any]:
    if not _is_known_write_operation(spec):
        raise ValidationError("Refused: unknown or non-write operation for apply")
    if not yes:
        raise SafetyError("Refused: apply requires --yes")
    if not receipt_out:
        raise ValidationError("Missing receipt_out")

    if not plan_in:
        raise ValidationError("Missing plan_in")

    plan = read_json_file(plan_in)

    normalized = _canonical_values(spec, values)
    _validate_plan_identity(spec=spec, values=normalized, plan=plan, tool_version=tool_version)
    _validate_acknowledgements(spec, acknowledgements=acknowledgements)

    secret_map = _validate_secret_inputs(spec, secret_values=secret_values)

    requested_target = _build_target_from_values(normalized)
    if requested_target is not None or plan.get("target") is not None:
        if requested_target != plan.get("target"):
            raise ValidationError("Refused: target mismatch")

    strict_purchase = spec.family == "purchase" and spec.command in {"purchase register", "purchase renew"}
    pre_snapshots = _snapshot_records_for_apply(
        spec,
        values=normalized,
        client=client,
        strict_purchase_recheck=strict_purchase,
    )
    _validate_snapshot_drift(plan=plan, snapshots=pre_snapshots)
    _validate_purchase_drift(spec=spec, normalized=normalized, plan=plan, snapshots=pre_snapshots)

    write_values = dict(normalized)
    write_values.update(secret_map)
    write_response = _extract_payload(client.execute_operation(spec, values=write_values))

    verification_results = _run_verify(client=client, spec=spec, values=normalized)

    receipt: dict[str, Any] = {
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
        "plan_fingerprint": plan.get("fingerprint"),
        "applied": True,
        "write": {
            "ok": True,
            "response": redact_object(write_response, redact_pii=True) if isinstance(write_response, (dict, list)) else None,
        },
        "verification": {
            "ok": all(item.get("ok") for item in verification_results),
            "results": verification_results,
        },
        "snapshot_before": pre_snapshots,
        "rollback_supported": False,
    }

    write_json_file(receipt_out, receipt)
    return receipt
