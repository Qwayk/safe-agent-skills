from __future__ import annotations

import hashlib
import ipaddress
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse

from .auth import build_auth, route_server
from .config import Config
from .errors import SafetyError, ToolError, ValidationError
from .http import HttpResult, send_request
from .redaction import REDACTED, create_protected_json, file_receipt, redact, write_protected_json
from .safety import (
    build_plan,
    enforce_approvals,
    is_effectful,
    provider_status_summary,
    verify_plan,
)

_SCIM_READ_COMMAND = "iam-organizations.fetch-organization-user"
_SCIM_PATCH_COMMAND = "iam-organizations.patch-organization-user"
_PORTING_READ_COMMAND = "numbers-v1.fetch-porting-webhook-configuration-fetch"
_PORTING_WRITE_COMMAND = "numbers-v1.create-porting-webhook-configuration"
_SNAPSHOT_READ_COMMANDS = {_SCIM_READ_COMMAND, _PORTING_READ_COMMAND}


@dataclass(frozen=True)
class PreparedRequest:
    method: str
    url: str
    public_host: str
    headers: dict[str, str]
    auth: tuple[str, str] | None
    query: list[tuple[str, Any]]
    form: dict[str, Any] | None
    json_body: Any | None
    content_type: str | None
    auth_summary: dict[str, Any]
    auth_warnings: tuple[str, ...]


def _schema_for_request(operation: dict[str, Any], content_type: str) -> dict[str, Any]:
    request = operation.get("request") or {}
    entry = request.get("schemas", {}).get(content_type, {})
    return entry.get("resolved_schema") or entry.get("schema") or {}


def _allowed_parameter_names(operation: dict[str, Any], location: str) -> set[str]:
    return {str(item["name"]) for item in operation.get("parameters", []) if item.get("in") == location}


def _parameter_schema(parameter: dict[str, Any]) -> dict[str, Any]:
    resolved = parameter.get("resolved_schema")
    if isinstance(resolved, dict):
        return resolved
    schema = parameter.get("schema")
    return schema if isinstance(schema, dict) else {}


def _auto_path_value(operation: dict[str, Any], name: str, cfg: Config) -> str | None:
    if name == "AccountSid":
        return cfg.account_sid
    if operation.get("command") == "api-v2010.fetch-account" and name == "Sid":
        return cfg.account_sid
    return None


def _merge_all_of(schema: dict[str, Any]) -> dict[str, Any]:
    if "allOf" not in schema:
        return schema
    merged = {key: value for key, value in schema.items() if key != "allOf"}
    properties = dict(merged.get("properties") or {})
    required = set(merged.get("required") or [])
    for member in schema.get("allOf") or []:
        if not isinstance(member, dict):
            continue
        resolved = _merge_all_of(member)
        properties.update(resolved.get("properties") or {})
        required.update(resolved.get("required") or [])
        for key, value in resolved.items():
            if key not in {"properties", "required"} and key not in merged:
                merged[key] = value
    if properties:
        merged["properties"] = properties
    if required:
        merged["required"] = sorted(required)
    return merged


def _validate_schema_value(
    value: Any,
    schema: dict[str, Any],
    *,
    location: str,
    fail_closed_object: bool,
) -> None:
    if value is None and schema.get("nullable"):
        return
    json_string_contract = schema.get("x-qwayk-json-string")
    if isinstance(json_string_contract, dict):
        if not isinstance(value, str):
            raise ValidationError(f"{location} must be a JSON string")
        max_bytes = json_string_contract.get("max_bytes")
        if max_bytes is not None and len(value.encode("utf-8")) > int(max_bytes):
            raise ValidationError(f"{location} must be no more than {int(max_bytes)} bytes")
        try:
            decoded = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            raise ValidationError(f"{location} must contain valid JSON") from None
        decoded_schema = json_string_contract.get("schema")
        if not isinstance(decoded_schema, dict):
            raise ValidationError(f"{location} has an invalid bundled JSON-string contract")
        _validate_schema_value(
            decoded,
            decoded_schema,
            location=location,
            fail_closed_object=False,
        )

    if isinstance(schema.get("oneOf"), list):
        failures: list[str] = []
        for variant in schema["oneOf"]:
            try:
                _validate_schema_value(
                    value,
                    _merge_all_of(variant),
                    location=location,
                    fail_closed_object=fail_closed_object,
                )
                return
            except ValidationError as exc:
                failures.append(str(exc))
        raise ValidationError(f"{location} does not match any pinned request schema") from None

    if isinstance(schema.get("anyOf"), list):
        for variant in schema["anyOf"]:
            try:
                _validate_schema_value(
                    value,
                    _merge_all_of(variant),
                    location=location,
                    fail_closed_object=(
                        False
                        if isinstance(variant, dict)
                        and variant.get("x-qwayk-condition-only") is True
                        else fail_closed_object
                    ),
                )
                break
            except ValidationError:
                continue
        else:
            raise ValidationError(f"{location} does not match any pinned request schema") from None

    schema = _merge_all_of(schema)
    expected_type = schema.get("type")
    documented_flexible = schema.get("x-qwayk-documented-flexible-json") is True
    if expected_type == "object" or "properties" in schema or "required" in schema:
        if not isinstance(value, dict):
            raise ValidationError(f"{location} must be a JSON object")
        if schema.get("minProperties") is not None and len(value) < int(schema["minProperties"]):
            raise ValidationError(f"{location} has fewer properties than the documented minimum")
        if schema.get("maxProperties") is not None and len(value) > int(schema["maxProperties"]):
            raise ValidationError(f"{location} has more properties than the documented maximum")
        properties = schema.get("properties") or {}
        missing = [name for name in schema.get("required", []) if value.get(name) in (None, "")]
        if missing:
            raise ValidationError(f"Missing required {location} fields: " + ", ".join(sorted(missing)))
        read_only = {name for name, item in properties.items() if item.get("readOnly") is True}
        supplied_read_only = set(value) & read_only
        if supplied_read_only:
            raise ValidationError(
                f"Read-only {location} fields are not allowed: " + ", ".join(sorted(supplied_read_only))
            )
        unknown = set(value) - set(properties)
        additional = schema.get("additionalProperties")
        condition_only = schema.get("x-qwayk-condition-only") is True
        if unknown and not documented_flexible and not condition_only and (
            fail_closed_object or additional is False or additional is None
        ):
            raise ValidationError(f"Unknown {location} fields: " + ", ".join(sorted(unknown)))
        for name, item in value.items():
            child_schema = properties.get(name)
            if child_schema is None and isinstance(additional, dict):
                child_schema = additional
            if isinstance(child_schema, dict):
                _validate_schema_value(
                    item,
                    child_schema,
                    location=f"{location}.{name}",
                    fail_closed_object=False,
                )
    elif expected_type == "array":
        if not isinstance(value, list):
            raise ValidationError(f"{location} must be a JSON array")
        if schema.get("minItems") is not None and len(value) < int(schema["minItems"]):
            raise ValidationError(f"{location} has fewer items than the pinned minimum")
        if schema.get("maxItems") is not None and len(value) > int(schema["maxItems"]):
            raise ValidationError(f"{location} has more items than the pinned maximum")
        if schema.get("uniqueItems") is True:
            canonical = [
                json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                for item in value
            ]
            if len(canonical) != len(set(canonical)):
                raise ValidationError(f"{location} contains duplicate items")
        unique_by = schema.get("x-qwayk-unique-by")
        if isinstance(unique_by, str):
            values = [item.get(unique_by) for item in value if isinstance(item, dict)]
            if len(values) != len(value) or len(values) != len(set(values)):
                raise ValidationError(f"{location} contains duplicate or invalid {unique_by} values")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                _validate_schema_value(
                    item,
                    item_schema,
                    location=f"{location}[{index}]",
                    fail_closed_object=False,
                )
    elif expected_type == "string" and not isinstance(value, str):
        raise ValidationError(f"{location} must be a string")
    elif expected_type == "boolean" and not isinstance(value, bool):
        raise ValidationError(f"{location} must be a boolean")
    elif expected_type == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
        raise ValidationError(f"{location} must be an integer")
    elif expected_type == "number" and (not isinstance(value, (int, float)) or isinstance(value, bool)):
        raise ValidationError(f"{location} must be a number")
    if "enum" in schema and value not in schema["enum"]:
        raise ValidationError(f"{location} must be one of the pinned enum values")
    if isinstance(value, str):
        if schema.get("minLength") is not None and len(value) < int(schema["minLength"]):
            raise ValidationError(f"{location} is shorter than the pinned minimum")
        if schema.get("maxLength") is not None and len(value) > int(schema["maxLength"]):
            raise ValidationError(f"{location} is longer than the pinned maximum")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.fullmatch(pattern, value) is None:
            raise ValidationError(f"{location} does not match the pinned format")
        if schema.get("x-qwayk-https-url") is True:
            _validate_https_url(value, location=location)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if schema.get("minimum") is not None and value < schema["minimum"]:
            raise ValidationError(f"{location} is below the pinned minimum")
        if schema.get("maximum") is not None and value > schema["maximum"]:
            raise ValidationError(f"{location} is above the pinned maximum")


def _validate_https_url(value: str, *, location: str) -> None:
    if any(character.isspace() for character in value):
        raise ValidationError(f"{location} must be a valid absolute HTTPS URL")
    try:
        parsed = urlparse(value)
        port = parsed.port
    except ValueError:
        raise ValidationError(f"{location} must be a valid absolute HTTPS URL") from None
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or (port is not None and not 1 <= port <= 65535)
    ):
        raise ValidationError(f"{location} must be a secure absolute HTTPS URL")
    hostname = parsed.hostname.rstrip(".").lower()
    if hostname == "localhost" or hostname.endswith((".localhost", ".local")):
        raise ValidationError(f"{location} must use a public HTTPS host")
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        try:
            ascii_hostname = hostname.encode("idna").decode("ascii")
        except UnicodeError:
            raise ValidationError(f"{location} must use a valid public HTTPS host") from None
        if len(ascii_hostname) > 253 or "." not in ascii_hostname:
            raise ValidationError(f"{location} must use a valid public HTTPS host") from None
        label_pattern = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
        if any(label_pattern.fullmatch(label) is None for label in ascii_hostname.split(".")):
            raise ValidationError(f"{location} must use a valid public HTTPS host") from None
        return
    if not address.is_global:
        raise ValidationError(f"{location} must use a public HTTPS host")


def _validate_operation_invariants(operation: dict[str, Any], body: dict[str, Any]) -> None:
    if operation.get("command") != "iam-organizations.patch-organization-user":
        return
    operations = body.get("Operations")
    if not isinstance(operations, list):
        return
    by_path = {item.get("path"): item.get("value") for item in operations if isinstance(item, dict)}
    username = by_path.get("userName")
    primary_email = by_path.get("emails[primary eq true].value")
    if (username is None) != (primary_email is None):
        raise ValidationError(
            "SCIM userName and primary email changes must be supplied together"
        )
    if username is not None and username != primary_email:
        raise ValidationError("SCIM userName and primary email changes must be equal")


def _serialize_form_body(body: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    """Serialize documented structured form fields the way Twilio's form API expects them."""

    merged = _merge_all_of(schema)
    properties = merged.get("properties") or {}
    serialized: dict[str, Any] = {}
    for name, value in body.items():
        field_schema = properties.get(name) if isinstance(properties, dict) else None
        if not isinstance(field_schema, dict) or "x-qwayk-json-string" in field_schema:
            serialized[name] = value
            continue
        if field_schema.get("type") == "object" and isinstance(value, dict):
            serialized[name] = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
            continue
        item_schema = field_schema.get("items")
        if (
            field_schema.get("type") == "array"
            and isinstance(value, list)
            and isinstance(item_schema, dict)
            and (item_schema.get("type") == "object" or "properties" in item_schema)
        ):
            serialized[name] = [
                json.dumps(item, ensure_ascii=False, separators=(",", ":"))
                for item in value
            ]
            continue
        serialized[name] = value
    return serialized


def prepare_request(operation: dict[str, Any], input_obj: dict[str, Any], cfg: Config) -> PreparedRequest:
    if not isinstance(input_obj, dict):
        raise ValidationError("Input JSON must contain one object")
    unknown_sections = set(input_obj) - {"path", "query", "headers", "body", "content_type"}
    if unknown_sections:
        raise ValidationError("Unknown input sections: " + ", ".join(sorted(unknown_sections)))
    path_values = dict(input_obj.get("path") or {})
    query_values = dict(input_obj.get("query") or {})
    header_values = dict(input_obj.get("headers") or {})
    body = input_obj.get("body")
    if not all(isinstance(value, dict) for value in (path_values, query_values, header_values)):
        raise ValidationError("path, query, and headers must be JSON objects")

    for location, supplied in (("path", path_values), ("query", query_values), ("header", header_values)):
        unknown = set(supplied) - _allowed_parameter_names(operation, location)
        if unknown:
            raise ValidationError(
                f"Unknown {location} parameters for {operation['command']}: " + ", ".join(sorted(unknown))
            )

    path = str(operation["path"])
    for parameter in operation.get("parameters", []):
        if parameter.get("in") != "path":
            continue
        name = str(parameter["name"])
        value = path_values.get(name)
        if value in (None, ""):
            value = _auto_path_value(operation, name, cfg)
        if value in (None, ""):
            raise ValidationError(f"Missing required path parameter: {name}")
        _validate_schema_value(
            value,
            _parameter_schema(parameter),
            location=f"path.{name}",
            fail_closed_object=True,
        )
        path = path.replace("{" + name + "}", quote(str(value), safe=""))
    if re.search(r"\{[^}]+\}", path):
        raise ValidationError("Unresolved path parameter in fixed Twilio command")

    query: list[tuple[str, Any]] = []
    for parameter in operation.get("parameters", []):
        if parameter.get("in") != "query":
            continue
        name = str(parameter["name"])
        value = query_values.get(name)
        if value in (None, "") and name == "AccountSid":
            value = cfg.account_sid
        if value in (None, ""):
            if parameter.get("required"):
                raise ValidationError(f"Missing required query parameter: {name}")
            continue
        _validate_schema_value(
            value,
            _parameter_schema(parameter),
            location=f"query.{name}",
            fail_closed_object=True,
        )
        if isinstance(value, list) and parameter.get("explode") is False:
            query.append((name, ",".join(str(item) for item in value)))
        elif isinstance(value, list):
            query.extend((name, item) for item in value)
        else:
            query.append((name, value))

    for parameter in operation.get("parameters", []):
        if parameter.get("in") != "header":
            continue
        name = str(parameter["name"])
        value = header_values.get(name)
        if value in (None, "") and parameter.get("required"):
            raise ValidationError(f"Missing required header parameter: {name}")
        if value not in (None, ""):
            _validate_schema_value(
                value,
                _parameter_schema(parameter),
                location=f"headers.{name}",
                fail_closed_object=True,
            )

    request_meta = operation.get("request")
    content_type: str | None = None
    form: dict[str, Any] | None = None
    json_body: Any | None = None
    if request_meta is None:
        if body not in (None, {}):
            raise ValidationError(f"{operation['command']} does not accept a request body")
    else:
        media_types = list(request_meta.get("media_types", []))
        requested_type = input_obj.get("content_type")
        if requested_type is not None and requested_type not in media_types:
            raise ValidationError("content_type must be one of the media types fixed by this command")
        content_type = str(
            requested_type
            or ("application/x-www-form-urlencoded" if "application/x-www-form-urlencoded" in media_types else media_types[0])
        )
        schema = _schema_for_request(operation, content_type)
        if body is None:
            body = {}
        if not isinstance(body, dict):
            raise ValidationError("Request body must be a JSON object")
        if isinstance(schema, dict) and schema:
            _validate_schema_value(body, schema, location="body", fail_closed_object=True)
            _validate_operation_invariants(operation, body)
        elif body:
            raise ValidationError("The pinned request schema does not expose safe body fields")
        if content_type == "application/x-www-form-urlencoded":
            form = _serialize_form_body(body, schema)
        else:
            json_body = body
            header_values.setdefault("Content-Type", content_type)

    auth_result = build_auth(operation, cfg, header_values)
    server = route_server(str(operation["server"]), cfg)
    url = f"{server.rstrip('/')}/{path.lstrip('/')}"
    return PreparedRequest(
        method=str(operation["method"]),
        url=url,
        public_host=urlparse(server).hostname or "twilio.com",
        headers=auth_result.headers,
        auth=auth_result.basic,
        query=query,
        form=form,
        json_body=json_body,
        content_type=content_type,
        auth_summary=auth_result.public_summary,
        auth_warnings=auth_result.warnings,
    )


def _pii_fields(operation: dict[str, Any]) -> set[str]:
    return {str(item["field"]) for item in operation.get("pii_fields", [])}


def _safe_result(operation: dict[str, Any], result: HttpResult, cfg: Config) -> dict[str, Any]:
    if operation.get("command") == _SCIM_READ_COMMAND:
        version = (
            result.data.get("meta", {}).get("version")
            if isinstance(result.data, dict) and isinstance(result.data.get("meta"), dict)
            else None
        )
        data: Any = {
            "meta": {"version": version if isinstance(version, str) else REDACTED},
            "user": REDACTED,
        }
    elif operation.get("command") == _PORTING_READ_COMMAND:
        data = {"configuration": REDACTED}
    else:
        data = redact(
            result.data,
            pii_fields=_pii_fields(operation),
            secret_values=cfg.redaction_values(),
        )
    return {
        "ok": 200 <= result.status_code < 300,
        "command": operation["command"],
        "http_status": result.status_code,
        "data": data,
        "status": provider_status_summary(result.data),
        "live_verification": "performed_against_provider",
    }


def _compatible_read_input(
    input_obj: dict[str, Any],
    read_operation: dict[str, Any],
) -> dict[str, Any]:
    allowed = {
        (str(item.get("in")), str(item.get("name")))
        for item in read_operation.get("parameters", [])
    }
    output: dict[str, Any] = {}
    for section, location in (("path", "path"), ("query", "query"), ("headers", "header")):
        supplied = input_obj.get(section)
        if not isinstance(supplied, dict):
            continue
        kept = {name: value for name, value in supplied.items() if (location, str(name)) in allowed}
        if kept:
            output[section] = kept
    return output


def _raise_for_failure(operation: dict[str, Any], result: HttpResult, cfg: Config) -> None:
    if 200 <= result.status_code < 300:
        return
    if operation.get("command") in {
        _SCIM_READ_COMMAND,
        _SCIM_PATCH_COMMAND,
        _PORTING_READ_COMMAND,
        _PORTING_WRITE_COMMAND,
    }:
        safe: Any = {"provider_error": REDACTED}
    else:
        safe = redact(
            result.data,
            pii_fields=_pii_fields(operation),
            secret_values=cfg.redaction_values(),
        )
    raise ToolError(f"Twilio request failed with HTTP {result.status_code}: {json.dumps(safe, ensure_ascii=False)}")


def execute_read(
    operation: dict[str, Any],
    input_obj: dict[str, Any],
    cfg: Config,
    *,
    session: Any | None = None,
    sensitive_out: str | Path | None = None,
    verbose: bool = False,
) -> dict[str, Any]:
    request = prepare_request(operation, input_obj, cfg)
    result = send_request(
        request,
        session=session,
        timeout_s=cfg.timeout_s,
        retry_safe=operation.get("method") == "GET" and not is_effectful(operation, input_obj),
        verbose=verbose,
    )
    _raise_for_failure(operation, result, cfg)
    output = _safe_result(operation, result, cfg)
    if sensitive_out:
        protected_data = result.data
        if operation.get("command") == _SCIM_READ_COMMAND:
            version = (
                result.data.get("meta", {}).get("version")
                if isinstance(result.data, dict) and isinstance(result.data.get("meta"), dict)
                else None
            )
            if not isinstance(version, str) or not version:
                raise SafetyError("Refused: SCIM user snapshot has no resource meta.version")
            protected_data = {
                "meta": {"version": version},
                "user": REDACTED,
            }
        if operation.get("command") in _SNAPSHOT_READ_COMMANDS:
            protected_data = _snapshot_envelope(
                operation,
                input_obj,
                cfg,
                protected_data,
            )
        write_protected_json(sensitive_out, protected_data)
        receipt = file_receipt(sensitive_out)
        receipt["path"] = Path(str(sensitive_out)).name
        output["protected_result"] = receipt
    return output


def execute_operation(
    operation: dict[str, Any],
    input_obj: dict[str, Any],
    cfg: Config,
    *,
    registry: Any,
    tool_version: str,
    apply: bool,
    yes: bool,
    plan_out: str | None,
    plan_in: str | None,
    receipt_out: str | None,
    snapshot_in: str | None,
    acknowledgements: dict[str, bool],
    target_count: int | None,
    sensitive_out: str | None,
    session: Any | None = None,
    verbose: bool = False,
) -> dict[str, Any]:
    if not is_effectful(operation, input_obj):
        return execute_read(
            operation,
            input_obj,
            cfg,
            session=session,
            sensitive_out=sensitive_out,
            verbose=verbose,
        )

    request = prepare_request(operation, input_obj, cfg)
    paired = registry.paired_read(operation)
    snapshot_receipt: dict[str, Any] | None = None
    snapshot_data: dict[str, Any] | None = None
    if snapshot_in:
        snapshot_receipt = file_receipt(snapshot_in)
        if snapshot_receipt["protected_mode"] != "0o600":
            raise SafetyError("Refused: --snapshot-in must be a mode-600 protected file")
        try:
            loaded_snapshot = json.loads(Path(snapshot_in).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raise SafetyError("Refused: --snapshot-in must contain valid protected JSON") from None
        if not isinstance(loaded_snapshot, dict):
            raise SafetyError("Refused: --snapshot-in must contain one snapshot object")
        snapshot_data = loaded_snapshot
    if operation.get("snapshot_required") is True and snapshot_receipt is None:
        raise SafetyError("Refused: this command requires --snapshot-in from its paired GET")
    if operation.get("snapshot_required") is True:
        if paired is None or snapshot_data is None:
            raise SafetyError("Refused: this command requires a provable paired GET snapshot")
        _verify_snapshot_binding(
            snapshot_data,
            paired,
            _compatible_read_input(input_obj, paired),
            cfg,
        )
    if operation.get("command") == _SCIM_PATCH_COMMAND:
        try:
            assert snapshot_data is not None
            snapshot_version = snapshot_data["provider_state"]["meta"]["version"]
        except (TypeError, KeyError):
            raise SafetyError(
                "Refused: SCIM snapshot must contain the paired GET meta.version"
            ) from None
        supplied_version = (input_obj.get("headers") or {}).get("If-Match")
        if supplied_version != snapshot_version:
            raise SafetyError(
                "Refused: If-Match must equal the current meta.version in --snapshot-in"
            )
    plan = build_plan(
        operation,
        input_obj,
        cfg,
        registry.inventory_hash,
        tool_version,
        snapshot_command=paired.get("command") if paired else None,
        snapshot_receipt=snapshot_receipt,
    )
    if not apply:
        if plan_out:
            write_protected_json(plan_out, plan)
        return {"ok": True, "dry_run": True, "plan": plan, "plan_saved": bool(plan_out)}
    if not plan_in:
        raise SafetyError("Refused: live apply requires --plan-in from a prior dry-run")
    if not receipt_out:
        raise SafetyError("Refused: live apply requires --receipt-out for a protected receipt")
    plan_receipt = file_receipt(plan_in)
    if plan_receipt["protected_mode"] != "0o600":
        raise SafetyError("Refused: --plan-in must be a mode-600 protected file")
    reviewed_plan = json.loads(Path(plan_in).read_text(encoding="utf-8"))
    verify_plan(
        reviewed_plan,
        operation,
        input_obj,
        cfg,
        registry.inventory_hash,
        tool_version,
        snapshot_command=paired.get("command") if paired else None,
        snapshot_receipt=snapshot_receipt,
    )
    enforce_approvals(
        reviewed_plan,
        acknowledgements,
        apply=apply,
        yes=yes,
        snapshot_in=snapshot_in,
        target_count=target_count,
    )
    snapshot_summary = (
        {
            "name": Path(str(snapshot_in)).name,
            "sha256": snapshot_receipt["sha256"],
            "bytes": snapshot_receipt["bytes"],
        }
        if snapshot_receipt
        else None
    )
    receipt_base = {
        "schema_version": 1,
        "tool": "qwayk-twilio-safe-agent-cli",
        "plan_id": reviewed_plan["plan_id"],
        "command": operation["command"],
        "account_fingerprint": cfg.fingerprint,
        "snapshot": snapshot_summary,
    }
    preflight_receipt = {
        **receipt_base,
        "attempt": {
            "status": "uncertain",
            "provider_response_received": False,
            "note": (
                "This preflight receipt is replaced after the provider attempt. If it remains, "
                "check provider state before retrying."
            ),
        },
        "http_status": None,
        "provider_status": provider_status_summary({}),
        "verification": {
            "strategy": operation.get("verification_strategy"),
            "performed": False,
            "result": "not_started",
        },
        "response": None,
    }
    create_protected_json(receipt_out, preflight_receipt)
    try:
        result = send_request(
            request,
            session=session,
            timeout_s=cfg.timeout_s,
            retry_safe=False,
            verbose=verbose,
        )
    except Exception as exc:  # noqa: BLE001
        uncertain_receipt = {
            **preflight_receipt,
            "attempt": {
                "status": "uncertain",
                "provider_response_received": False,
                "error_type": type(exc).__name__,
                "note": "No provider response was received. Check provider state before retrying.",
            },
            "verification": {
                "strategy": operation.get("verification_strategy"),
                "performed": False,
                "result": "not_possible_without_provider_response",
            },
        }
        write_protected_json(receipt_out, uncertain_receipt)
        raise ToolError(
            "Twilio write attempt ended without a provider response "
            f"({type(exc).__name__}); check the protected receipt before retrying"
        ) from None

    if operation.get("command") == _SCIM_PATCH_COMMAND:
        version = (
            result.data.get("meta", {}).get("version")
            if isinstance(result.data, dict) and isinstance(result.data.get("meta"), dict)
            else None
        )
        safe_response: Any = {
            "meta": {"version": version if isinstance(version, str) else REDACTED},
            "user": REDACTED,
        }
    elif (
        operation.get("command") == _PORTING_WRITE_COMMAND
        and not 200 <= result.status_code < 300
    ):
        safe_response = {"provider_error": REDACTED}
    else:
        safe_response = redact(
            result.data,
            pii_fields=_pii_fields(operation),
            secret_values=cfg.redaction_values(),
        )
    if not 200 <= result.status_code < 300:
        failed_receipt = {
            **receipt_base,
            "attempt": {
                "status": "failed",
                "provider_response_received": True,
                "note": "Twilio returned a non-success HTTP response.",
            },
            "http_status": result.status_code,
            "provider_status": provider_status_summary(result.data),
            "verification": {
                "strategy": operation.get("verification_strategy"),
                "performed": False,
                "result": "provider_rejected_or_failed",
            },
            "response": safe_response,
        }
        write_protected_json(receipt_out, failed_receipt)
        _raise_for_failure(operation, result, cfg)

    verification: dict[str, Any] = {
        "strategy": operation.get("verification_strategy"),
        "performed": False,
        "result": "provider_response_only",
    }
    if paired and operation.get("snapshot_strategy") in {"fetch_before_change", "fetch_before_delete"}:
        try:
            verify_request = prepare_request(paired, _compatible_read_input(input_obj, paired), cfg)
            verify_result = send_request(
                verify_request,
                session=session,
                timeout_s=cfg.timeout_s,
                retry_safe=True,
                verbose=verbose,
            )
            verification = {
                "strategy": operation.get("verification_strategy"),
                "performed": True,
                "http_status": verify_result.status_code,
                "result": (
                    "confirmed_absent"
                    if operation.get("method") == "DELETE" and verify_result.status_code == 404
                    else "refetched" if 200 <= verify_result.status_code < 300 else "not_confirmed"
                ),
            }
        except Exception as exc:  # noqa: BLE001
            verification = {
                "strategy": operation.get("verification_strategy"),
                "performed": False,
                "result": "verification_failed",
                "error_type": type(exc).__name__,
            }

    receipt = {
        **receipt_base,
        "attempt": {
            "status": "succeeded",
            "provider_response_received": True,
            "note": "Twilio returned a successful HTTP response.",
        },
        "http_status": result.status_code,
        "provider_status": provider_status_summary(result.data),
        "verification": verification,
        "response": safe_response,
    }
    write_protected_json(receipt_out, receipt)
    return {"ok": True, "applied": True, "receipt": receipt, "receipt_saved": True}


def _canonical_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _snapshot_envelope(
    read_operation: dict[str, Any],
    input_obj: dict[str, Any],
    cfg: Config,
    provider_state: Any,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "snapshot_binding": {
            "read_command": read_operation["command"],
            "account_fingerprint": cfg.fingerprint,
            "input_sha256": _canonical_hash(input_obj),
        },
        "provider_state": provider_state,
    }


def _verify_snapshot_binding(
    snapshot: dict[str, Any],
    paired_read: dict[str, Any],
    read_input: dict[str, Any],
    cfg: Config,
) -> None:
    binding = snapshot.get("snapshot_binding")
    if not isinstance(binding, dict):
        raise SafetyError("Refused: snapshot has no paired GET provenance")
    expected = {
        "read_command": paired_read["command"],
        "account_fingerprint": cfg.fingerprint,
        "input_sha256": _canonical_hash(read_input),
    }
    if binding != expected:
        raise SafetyError("Refused: snapshot does not match the paired GET, account, or target")
    if "provider_state" not in snapshot:
        raise SafetyError("Refused: snapshot has no paired GET provider state")
