from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import secrets
import stat
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from importlib.resources import files as resource_files
from pathlib import Path
from typing import Any, cast
from urllib.parse import quote

from jsonschema import Draft202012Validator

from . import __version__
from .config import Config, load_config
from .errors import AuthError, ProviderError, SafetyError, ToolError, ValidationError
from .http import RequestsTransport, Transport, TransportResponse
from .output import Output
from .privacy import collect_sensitive_values, is_sensitive_key, sanitize, scrub_text
from .secure_files import (
    AtomicFileReservation,
    atomic_write_text,
    create_private_bytes_if_absent,
    ensure_private_directory,
    file_paths_alias,
    reserve_atomic_file,
)

INVENTORY_RESOURCE = "resources/operation_inventory.json"
SPEC_RESOURCE = "resources/porkbun-openapi-v3.9.json"
PLAN_SIGNING_KEY_PATH = Path(".state/plan-signing.key")
PLAN_SIGNING_KEY_BYTES = 32
PLAN_SIGNATURE_PREFIX = "hmac-sha256:"


class _ToolArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


@dataclass(frozen=True)
class OperationMeta:
    family_slug: str
    operation_id: str
    kebab_operation_id: str
    command: str
    method: str
    path: str
    auth: str
    write: bool
    destructive: bool
    billable: bool
    terms_required: bool
    secret_bearing_result: bool
    native_dry_run: bool
    snapshot_plan: dict[str, Any]
    parameters: list[dict[str, Any]]


@dataclass(frozen=True)
class TransportMeta:
    request_id: str | None
    api_version: str | None
    rate_limits: dict[str, str]
    retry_after: str | None


def _to_dashed(name: str) -> str:
    out = ""
    for char in name:
        if char == "_":
            out += "-"
        elif char.isupper():
            if out:
                out += "-"
            out += char.lower()
        else:
            out += char
    return out


def _iso_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _redact(obj: Any) -> Any:
    return sanitize(obj)


def _sensitive_values_from_argv(argv: list[str]) -> set[str]:
    values: set[str] = set()
    for index, item in enumerate(argv):
        if not item.startswith("--") or index + 1 >= len(argv):
            continue
        if is_sensitive_key(item):
            values.add(str(argv[index + 1]))
        if item == "--input":
            candidate = Path(argv[index + 1])
            try:
                payload = json.loads(candidate.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                continue
            values.update(collect_sensitive_values(payload))
    return {value for value in values if value}


def _request_sensitive_values(
    cfg: Config,
    path_params: dict[str, Any],
    query_params: dict[str, Any],
    payload: dict[str, Any],
) -> set[str]:
    values = {cfg.api_key, cfg.secret_api_key}
    values.update(collect_sensitive_values(path_params))
    values.update(collect_sensitive_values(query_params))
    values.update(collect_sensitive_values(payload))
    return {value for value in values if value}


def _canonical_plan(plan: dict[str, Any], *, for_hash: bool) -> str:
    excluded = {"plan_signature"}
    if for_hash:
        excluded.add("plan_hash")
    return json.dumps(
        {key: value for key, value in plan.items() if key not in excluded},
        sort_keys=True,
    )


def _load_plan_signing_key(*, create: bool) -> bytes:
    ensure_private_directory(PLAN_SIGNING_KEY_PATH.parent)
    if create:
        create_private_bytes_if_absent(
            PLAN_SIGNING_KEY_PATH,
            secrets.token_bytes(PLAN_SIGNING_KEY_BYTES),
            private_parent=True,
            allow_plan_signing_key=True,
        )
    elif not PLAN_SIGNING_KEY_PATH.exists():
        raise SafetyError("Plan signing key is missing")

    if PLAN_SIGNING_KEY_PATH.is_symlink() or not PLAN_SIGNING_KEY_PATH.is_file():
        raise SafetyError("Plan signing key is invalid")
    mode = stat.S_IMODE(PLAN_SIGNING_KEY_PATH.stat().st_mode)
    if mode != 0o600:
        raise SafetyError("Plan signing key must use owner-only mode 0600")
    try:
        key = PLAN_SIGNING_KEY_PATH.read_bytes()
    except OSError as exc:
        raise SafetyError("Plan signing key cannot be read") from exc
    if len(key) != PLAN_SIGNING_KEY_BYTES:
        raise SafetyError("Plan signing key is invalid")
    return key


def _sign_plan(plan: dict[str, Any], key: bytes) -> None:
    plan["plan_hash"] = _sha256_text(_canonical_plan(plan, for_hash=True))
    signature = hmac.new(
        key,
        _canonical_plan(plan, for_hash=False).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    plan["plan_signature"] = PLAN_SIGNATURE_PREFIX + signature


def _verify_plan_signature(plan: dict[str, Any]) -> None:
    signature = plan.get("plan_signature")
    if not isinstance(signature, str) or not re.fullmatch(
        rf"{re.escape(PLAN_SIGNATURE_PREFIX)}[0-9a-f]{{64}}",
        signature,
    ):
        raise SafetyError("Plan signature is missing or invalid")
    key = _load_plan_signing_key(create=False)
    expected = PLAN_SIGNATURE_PREFIX + hmac.new(
        key,
        _canonical_plan(plan, for_hash=False).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise SafetyError("Plan signature is invalid; plan contents were changed")

    plan_hash = plan.get("plan_hash")
    if not isinstance(plan_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", plan_hash):
        raise SafetyError("Plan hash is missing or invalid")
    if not hmac.compare_digest(plan_hash, _sha256_text(_canonical_plan(plan, for_hash=True))):
        raise SafetyError("Plan hash is invalid")


def _load_resource_json(relative_path: str) -> dict[str, Any]:
    path = resource_files("qwayk_porkbun_safe_agent_cli") / relative_path
    return json.loads(path.read_text(encoding="utf-8"))


_SPEC_DOC = _load_resource_json(SPEC_RESOURCE)


def _build_operation_map() -> dict[str, OperationMeta]:
    inventory = _load_resource_json(INVENTORY_RESOURCE)
    out: dict[str, OperationMeta] = {}
    for op in inventory["operations"]:
        out[op["operation_id"]] = OperationMeta(
            family_slug=op["family_slug"],
            operation_id=op["operation_id"],
            kebab_operation_id=op["kebab_operation_id"],
            command=op["command"],
            method=op["method"].upper(),
            path=op["path"],
            auth=op.get("auth", "public"),
            write=bool(op.get("write")),
            destructive=bool(op.get("destructive")),
            billable=bool(op.get("billable")),
            terms_required=bool(op.get("terms_required")),
            secret_bearing_result=bool(op.get("secret_bearing_result")),
            native_dry_run=bool(op.get("native_dry_run")),
            snapshot_plan=op.get("snapshot_plan", {}),
            parameters=list(op.get("parameters", [])),
        )
    if len(out) != 66:
        raise RuntimeError("Inventory must contain exactly 66 operations")
    return out


def _spec_by_operation() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for path, path_item in (_SPEC_DOC.get("paths") or {}).items():
        if not isinstance(path_item, dict):
            continue
        for method_name, op_obj in path_item.items():
            if not isinstance(op_obj, dict):
                continue
            operation_id = str(op_obj.get("operationId") or "").strip()
            if not operation_id:
                continue
            out[operation_id] = {
                "operation": op_obj,
                "method": str(method_name).upper(),
                "path": str(path),
            }
    return out


_OPERATION_MAP: dict[str, OperationMeta] = _build_operation_map()
_SPEC_BY_OPERATION: dict[str, dict[str, Any]] = _spec_by_operation()


def _operation_has_request_body(operation: OperationMeta) -> bool:
    spec_entry = _SPEC_BY_OPERATION.get(operation.operation_id, {})
    if not isinstance(spec_entry, dict):
        return False
    op_obj = spec_entry.get("operation", {})
    if not isinstance(op_obj, dict):
        return False
    return isinstance(op_obj.get("requestBody"), dict)


def _resource_inventory() -> dict[str, Any]:
    return _load_resource_json(INVENTORY_RESOURCE)


def _find_operation_by_command(command: str) -> OperationMeta:
    for op in _OPERATION_MAP.values():
        if op.command == command:
            return op
    raise KeyError(command)


def _resolve_request_schema(operation: OperationMeta) -> dict[str, Any] | None:
    spec_entry = _SPEC_BY_OPERATION.get(operation.operation_id, {})
    spec_obj = spec_entry.get("operation", {}) if isinstance(spec_entry, dict) else {}
    request_body = spec_obj.get("requestBody")
    if not isinstance(request_body, dict):
        return None
    content = request_body.get("content")
    if not isinstance(content, dict):
        return None
    entry = content.get("application/json")
    if not isinstance(entry, dict):
        return None
    schema = entry.get("schema")
    if not isinstance(schema, dict):
        return None
    schema_copy = _resolve_request_schema_with_refs(deepcopy(schema))
    if not isinstance(schema_copy, dict):
        return None

    if "properties" in schema_copy and isinstance(schema_copy["properties"], dict):
        for forbidden in {"apikey", "secretapikey"}:
            schema_copy["properties"].pop(forbidden, None)
    if "required" in schema_copy and isinstance(schema_copy["required"], list):
        schema_copy["required"] = [
            x
            for x in schema_copy["required"]
            if x not in {"apikey", "secretapikey"}
        ]

    if operation.native_dry_run and isinstance(schema_copy, dict) and schema_copy.get("type") == "object":
        properties = schema_copy.setdefault("properties", {})
        if isinstance(properties, dict):
            properties.setdefault("dryRun", {"type": "boolean"})

    if operation.operation_id == "domainCreate":
        req = schema_copy.get("required")
        if not isinstance(req, list):
            req = []
        if "agreeToTerms" not in req:
            req.append("agreeToTerms")
        schema_copy["required"] = req

    return schema_copy


def _resolve_request_schema_with_refs(schema: Any, seen: list[str] | None = None) -> Any:
    if seen is None:
        seen = []

    if isinstance(schema, list):
        return [_resolve_request_schema_with_refs(item, seen) for item in schema]

    if not isinstance(schema, dict):
        return schema

    if "$ref" in schema:
        ref = str(schema["$ref"])
        if ref in seen:
            return {}
        target = _resolve_schema_ref(ref)
        if target is None:
            return {}
        seen.append(ref)
        return _resolve_request_schema_with_refs(target, seen)

    if "allOf" in schema:
        merged: dict[str, Any] = {}
        for entry in schema.get("allOf") or []:
            resolved = _resolve_request_schema_with_refs(entry, seen)
            if isinstance(resolved, dict):
                merged = _merge_schemas(merged, resolved)

        for key, value in schema.items():
            if key == "allOf":
                continue
            if key in merged:
                continue
            merged[key] = _resolve_request_schema_with_refs(value, seen)
        return merged

    out: dict[str, Any] = {}
    for key, value in schema.items():
        if isinstance(value, (dict, list)):
            out[key] = _resolve_request_schema_with_refs(value, seen)
        else:
            out[key] = value
    return out


def _resolve_schema_ref(ref: str) -> dict[str, Any] | None:
    if not ref.startswith("#/components/schemas/"):
        return None
    name = ref.rsplit("/", 1)[-1]
    node = _SPEC_DOC.get("components", {}).get("schemas", {}).get(name)
    if isinstance(node, dict):
        return deepcopy(node)
    return None


def _merge_schemas(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(left)

    for key, value in right.items():
        if key == "properties":
            props = merged.get("properties")
            current = props.copy() if isinstance(props, dict) else {}
            if isinstance(value, dict):
                current.update(value)
            merged["properties"] = current
            continue

        if key == "required":
            existing = merged.get("required")
            if not isinstance(existing, list):
                existing = []
            required: list[str] = []
            for field in list(existing) + list(value or []):
                if field not in required:
                    required.append(str(field))
            merged["required"] = required
            continue

        if key == "allOf":
            continue

        merged[key] = deepcopy(value) if isinstance(value, (dict, list)) else value

    return merged


def _normalize_param_type(value: Any, schema: dict[str, Any]) -> Any:
    t = str(schema.get("type") or "string").lower()
    if value is None:
        return value
    if t == "integer":
        try:
            return int(value)
        except Exception as exc:  # noqa: BLE001
            raise ValidationError(f"Invalid integer value for query/path parameter: {value}") from exc
    if t == "number":
        try:
            return float(value)
        except Exception as exc:  # noqa: BLE001
            raise ValidationError(f"Invalid number value for query/path parameter: {value}") from exc
    if t == "boolean":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on"}:
                return True
            if normalized in {"0", "false", "no", "off"}:
                return False
        raise ValidationError(f"Invalid boolean value for query/path parameter: {value}")
    return str(value)


def _coerce_input_payload(raw: str | None) -> dict[str, Any]:
    if raw is None:
        return {}
    candidate = Path(raw)
    if not candidate.exists():
        raise ValidationError("--input must be a JSON file path")
    try:
        payload = json.loads(candidate.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise ValidationError(f"Invalid JSON in --input file: {candidate}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValidationError("--input must be a JSON object")
    return payload


def _validate_parameters(operation: OperationMeta, raw: dict[str, Any]) -> None:
    props: dict[str, Any] = {}
    required: list[str] = []
    for param in operation.parameters:
        if param.get("in") not in {"path", "query"}:
            continue
        name = str(param.get("name") or "").strip()
        if not name:
            continue
        props[name] = param.get("schema") if isinstance(param.get("schema"), dict) else {"type": "string"}
        if param.get("required"):
            required.append(name)

    if not props:
        return

    validator = Draft202012Validator(
        {"type": "object", "properties": props, "required": required, "additionalProperties": False}
    )
    for error in sorted(validator.iter_errors(raw), key=lambda e: str(e)):
        raise ValidationError(str(error))


def _validate_body(operation: OperationMeta, payload: dict[str, Any]) -> dict[str, Any]:
    schema = _resolve_request_schema(operation)
    if not isinstance(schema, dict):
        return payload

    if not isinstance(payload, dict):
        raise ValidationError("--input must be an object")

    validator = Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(payload), key=lambda e: str(e)):
        raise ValidationError(str(error))

    if operation.operation_id == "domainCreate" and str(payload.get("agreeToTerms")) not in {"yes", "1"}:
        raise ValidationError("domainCreate requires agreeToTerms set to 'yes' or '1'")

    if "apikey" in payload or "secretapikey" in payload:
        raise ValidationError("apikey and secretapikey cannot be sent in --input")

    return payload


def _derive_operation_args(
    operation: OperationMeta,
    parsed_path: dict[str, Any],
    parsed_query: dict[str, Any],
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    p_params: dict[str, Any] = {}
    q_params: dict[str, Any] = {}

    for item in operation.parameters:
        if item.get("in") not in {"path", "query"}:
            continue
        name = str(item.get("name") or "").strip()
        if not name:
            continue
        source = parsed_path.get(name)
        if source is None:
            source = parsed_query.get(name)
        if source is None:
            source = payload.get(name)
        if source is None:
            if item.get("required"):
                raise SafetyError(f"Missing required mapped argument: {name}")
            continue
        converted = _normalize_param_type(source, item.get("schema") or {"type": "string"})
        if item.get("in") == "path":
            p_params[name] = converted
        else:
            q_params[name] = converted

    return p_params, q_params


def _split_path_query(operation: OperationMeta, namespace: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    values = vars(namespace)
    q_params: dict[str, Any] = {}
    p_params: dict[str, Any] = {}
    for item in operation.parameters:
        if item.get("in") not in {"path", "query"}:
            continue
        name = str(item.get("name") or "").strip()
        if not name:
            continue
        dest = _to_dashed(name).replace("-", "_")
        value = values.get(dest)
        if value is None:
            continue
        converted = _normalize_param_type(value, item.get("schema") or {"type": "string"})
        if item.get("in") == "path":
            p_params[name] = converted
        else:
            q_params[name] = converted
    return p_params, q_params


def _render_url(operation: OperationMeta, path_params: dict[str, Any]) -> str:
    target = operation.path
    for key, value in path_params.items():
        target = target.replace("{" + key + "}", quote(str(value), safe=""))
    return target


def _safe_headers(
    cfg: Config,
    operation: OperationMeta | None = None,
    *,
    force_auth: bool = False,
) -> dict[str, str]:
    headers = {"User-Agent": "qwayk-porkbun-safe-agent-cli"}
    if operation is None:
        return headers
    if operation.auth != "api-key-headers" and not force_auth:
        return headers
    if cfg.api_key and cfg.secret_api_key:
        headers["X-API-Key"] = cfg.api_key
        headers["X-Secret-API-Key"] = cfg.secret_api_key
    return headers


def _collect_transport_meta(response: TransportResponse) -> TransportMeta:
    rate_limits = {
        k: v
        for k, v in response.headers.items()
        if k.lower().startswith("x-ratelimit") or "limit" in k.lower()
    }
    retry_after = response.headers.get("retry-after")
    request_id = response.headers.get("x-request-id") or response.headers.get("request-id")
    api_version = response.headers.get("x-api-version")
    return TransportMeta(
        request_id=request_id,
        api_version=api_version,
        rate_limits=rate_limits,
        retry_after=retry_after,
    )


def _parse_json_response(response: TransportResponse) -> Any:
    text = response.body.decode("utf-8", errors="replace")
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        return {"raw": text}


def _plan_path(args: argparse.Namespace, operation: OperationMeta, operation_input: dict[str, Any]) -> str:
    if getattr(args, "plan_out", None):
        return str(args.plan_out)
    ensure_private_directory(Path(".state"))
    plan_dir = ensure_private_directory(Path(".state/plans"))
    op_hash = _sha256_text(operation.operation_id)
    plan_id = f"{op_hash[:8]}-{secrets.token_hex(6)}"
    return str(plan_dir / f"{plan_id}.json")


def _validate_output_file_roles(
    args: argparse.Namespace,
    outputs: dict[str, str | Path | None],
) -> None:
    controls: dict[str, str | Path | None] = {
        "environment file (--env-file)": getattr(args, "env_file", None),
        "JSON input file (--input)": getattr(args, "input", None),
        "plan input file (--plan-in)": getattr(args, "plan_in", None),
    }
    active_outputs = {
        role: path for role, path in outputs.items() if path is not None and str(path)
    }
    active_controls = {
        role: path for role, path in controls.items() if path is not None and str(path)
    }
    output_items = list(active_outputs.items())
    for index, (left_role, left_path) in enumerate(output_items):
        for right_role, right_path in output_items[index + 1 :]:
            if file_paths_alias(left_path, right_path):
                raise ValidationError(
                    f"File role collision: {left_role} and {right_role} must use different files"
                )
        for control_role, control_path in active_controls.items():
            if file_paths_alias(left_path, control_path):
                raise ValidationError(
                    f"File role collision: {left_role} must not alias {control_role}"
                )


def _receipt_path(args: argparse.Namespace, plan_data: dict[str, Any]) -> str:
    if getattr(args, "receipt_out", None):
        return str(args.receipt_out)
    ensure_private_directory(Path(".state"))
    receipt_dir = ensure_private_directory(Path(".state/receipts"))
    plan_hash = str(plan_data.get("plan_hash") or _sha256_text(json.dumps(plan_data, sort_keys=True)))
    return str(receipt_dir / f"{plan_hash[:16]}.json")


def _plan_file_warning(operation: OperationMeta) -> dict[str, Any]:
    return {
        "requires_no_snapshot_ack": bool(operation.snapshot_plan.get("requires_no_snapshot_ack")),
        "before_state_operation_id": operation.snapshot_plan.get("before_state_operation_id"),
        "readback_operation_id": operation.snapshot_plan.get("readback_operation_id"),
        "honest_note": operation.snapshot_plan.get("honest_note", "Not documented"),
    }


def _operation_acks(operation: OperationMeta) -> dict[str, bool]:
    return {
        "ack_send": operation.operation_id in {"createAccountInvite", "webhookTest", "webhookResend"},
        "ack_spend": bool(operation.billable),
        "ack_terms": operation.operation_id == "domainCreate",
        "ack_destructive": bool(operation.destructive),
        "ack_secret": bool(operation.secret_bearing_result)
        or operation.operation_id == "emailSetPassword",
        "ack_no_snapshot": bool(operation.snapshot_plan.get("requires_no_snapshot_ack")),
    }


def _assert_authenticated(operation: OperationMeta, cfg: Config, force: bool = True) -> None:
    if operation.auth == "api-key-headers" and force:
        if not cfg.api_key or not cfg.secret_api_key:
            raise AuthError("Authenticated operation requires PORKBUN_API_KEY and PORKBUN_SECRET_API_KEY")


def _effective_target(operation: OperationMeta, path_params: dict[str, Any], query_params: dict[str, Any]) -> str:
    safe_path = _redact(path_params)
    safe_query = _redact(query_params)
    return f"{operation.method} {operation.path}" + (
        " " + json.dumps({"path": safe_path}, sort_keys=True) if path_params else ""
    ) + (
        " " + json.dumps({"query": safe_query}, sort_keys=True) if query_params else ""
    )


def _target_signature(operation: OperationMeta, target: str, payload: dict[str, Any], dry_run_overlay: bool) -> str:
    candidate = {
        "target": target,
        "method": operation.method,
        "payload": payload,
        "dry_run": bool(dry_run_overlay),
    }
    return _sha256_text(json.dumps(candidate, sort_keys=True))


def _compute_cost_signature(result: Any) -> str:
    if not isinstance(result, dict):
        return ""
    for key in ("cost", "price", "total", "estimatedCost", "quote"):
        if key in result and isinstance(result[key], (int, float, str)):
            return f"{key}={result[key]}"
    nested = result.get("data") if isinstance(result, dict) else None
    if isinstance(nested, dict):
        for key in ("cost", "price", "total", "estimatedCost", "quote"):
            if key in nested and isinstance(nested[key], (int, float, str)):
                return f"{key}={nested[key]}"
    return ""


def _valid_cost_signature(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return bool(
        re.fullmatch(
            r"(cost|price|total|estimatedCost|quote)=(?:0|[1-9][0-9]*)(?:\.[0-9]+)?",
            value,
        )
    )


def _execute_api_call(
    *,
    operation: OperationMeta,
    cfg: Config,
    path_params: dict[str, Any],
    query_params: dict[str, Any],
    payload: dict[str, Any],
    transport: Transport,
    include_dry_run_overlay: bool = False,
    idempotency_key: str | None = None,
    force_auth_headers: bool = False,
) -> tuple[Any, TransportMeta]:
    headers = _safe_headers(cfg, operation, force_auth=force_auth_headers)
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key

    call_payload = deepcopy(payload)
    if include_dry_run_overlay and operation.native_dry_run:
        if call_payload is None:
            call_payload = {}
        call_payload = dict(call_payload)
        call_payload["dryRun"] = True

    sensitive_values = _request_sensitive_values(cfg, path_params, query_params, payload)
    try:
        response = transport.request(
            method=operation.method,
            url=cfg.api_host.rstrip("/") + _render_url(operation, path_params),
            headers=headers,
            params=query_params,
            json_body=call_payload if call_payload else None,
            timeout_s=cfg.timeout_s,
        )
    except ToolError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ProviderError(
            code="TRANSPORT_ERROR",
            message=scrub_text(str(exc), sensitive_values),
        ) from exc

    meta = _collect_transport_meta(response)
    data = _parse_json_response(response)

    if 300 <= response.status < 400:
        raise ProviderError(
            code="HTTP_REDIRECT",
            message=f"Porkbun returned an unexpected HTTP {response.status} redirect",
            status=response.status,
            request_id=meta.request_id,
            api_version=meta.api_version,
            rate_limits=meta.rate_limits,
            retry_after=meta.retry_after,
        )
    if response.status < 200 or response.status >= 400:
        code = "UNKNOWN"
        message = f"HTTP {response.status}"
        if isinstance(data, dict):
            code = str(data.get("code") or data.get("errorCode") or code)
            message = str(data.get("message") or data.get("error") or message)
        raise ProviderError(
            code=scrub_text(code, sensitive_values),
            message=scrub_text(message, sensitive_values),
            status=response.status,
            request_id=meta.request_id,
            api_version=meta.api_version,
            rate_limits=meta.rate_limits,
            retry_after=meta.retry_after,
        )
    if isinstance(data, dict) and str(data.get("status") or "").upper() == "ERROR":
        raise ProviderError(
            code=scrub_text(
                str(data.get("code") or data.get("errorCode") or "UNKNOWN"),
                sensitive_values,
            ),
            message=scrub_text(
                str(data.get("message") or data.get("error") or "Porkbun returned an error"),
                sensitive_values,
            ),
            status=response.status,
            request_id=meta.request_id,
            api_version=meta.api_version,
            rate_limits=meta.rate_limits,
            retry_after=meta.retry_after,
        )

    return data, meta


def _create_plan(
    *,
    operation: OperationMeta,
    cfg: Config,
    args: argparse.Namespace,
    path_params: dict[str, Any],
    query_params: dict[str, Any],
    payload: dict[str, Any],
    transport: Transport,
    target: str,
) -> tuple[dict[str, Any], TransportMeta | None]:
    destination = _plan_path(args, operation, payload)
    _validate_output_file_roles(
        args,
        {"plan output (--plan-out/default)": destination},
    )
    reservation = reserve_atomic_file(destination)
    sensitive_values = _request_sensitive_values(cfg, path_params, query_params, payload)
    try:
        signing_key = _load_plan_signing_key(create=True)
        plan_id = f"p{secrets.token_hex(8)}"
        snapshot = _plan_file_warning(operation)
        snapshot_result = None
        snapshot_transport_meta = None

        before_state_op_id = operation.snapshot_plan.get("before_state_operation_id")
        if before_state_op_id:
            before_state_op = _OPERATION_MAP.get(str(before_state_op_id))
            if before_state_op:
                before_state_path_params, before_state_query_params = _derive_operation_args(
                    operation=before_state_op,
                    parsed_path=path_params,
                    parsed_query=query_params,
                    payload=payload,
                )
                try:
                    snapshot_result, snapshot_transport_meta = _execute_api_call(
                        operation=before_state_op,
                        cfg=cfg,
                        path_params=before_state_path_params,
                        query_params=before_state_query_params,
                        payload={},
                        transport=transport,
                    )
                    snapshot["before_state"] = sanitize(snapshot_result, sensitive_values)
                except ToolError as exc:  # noqa: BLE001
                    snapshot["no_snapshot_warning"] = (
                        f"Failed to collect before-state: {type(exc).__name__}"
                    )
                    snapshot["requires_no_snapshot_ack"] = True
        elif bool(operation.snapshot_plan.get("requires_no_snapshot_ack")):
            snapshot["no_snapshot_warning"] = "No documented before-state for this operation"

        dry_run_result = None
        dry_run_signature = None
        if operation.native_dry_run:
            dry_run_result, _ = _execute_api_call(
                operation=operation,
                cfg=cfg,
                path_params=path_params,
                query_params=query_params,
                payload=payload,
                transport=transport,
                include_dry_run_overlay=True,
            )
            dry_run_signature = _compute_cost_signature(dry_run_result)

        plan_obj: dict[str, Any] = {
            "schema_version": 2,
            "plan_id": plan_id,
            "operation_id": operation.operation_id,
            "command": operation.command,
            "target": target,
            "path_params": sanitize(path_params, sensitive_values),
            "query_params": sanitize(query_params, sensitive_values),
            "parameter_sha256": _sha256_text(
                json.dumps({"path": path_params, "query": query_params}, sort_keys=True)
            ),
            "payload": sanitize(payload, sensitive_values),
            "input_sha256": _sha256_text(json.dumps(payload, sort_keys=True)),
            "idempotency_key": secrets.token_hex(16),
            "risk_flags": {
                "write": operation.write,
                "destructive": operation.destructive,
                "billable": operation.billable,
                "terms_required": operation.terms_required,
                **_operation_acks(operation),
            },
            "snapshot": snapshot,
            "snapshot_data": sanitize(snapshot_result or {}, sensitive_values),
            "dry_run": {
                "requested": bool(operation.native_dry_run),
                "signature": (
                    _sha256_text(json.dumps(dry_run_result, sort_keys=True))
                    if dry_run_result is not None
                    else None
                ),
                "cost_signature": dry_run_signature,
                "result": sanitize(dry_run_result, sensitive_values),
            },
            "validation": {
                "ok": True,
            },
            "created_at_utc": _iso_now(),
            "expires_at_utc": (
                datetime.now(UTC) + timedelta(hours=24)
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "command_input_signature": _target_signature(
                operation,
                target,
                payload,
                dry_run_overlay=False,
            ),
        }
        _sign_plan(plan_obj, signing_key)
        plan_obj["plan_out"] = reservation.commit_json(plan_obj)
        return plan_obj, snapshot_transport_meta
    except Exception:
        reservation.cleanup()
        raise


def _compare_plan(
    plan: dict[str, Any],
    operation: OperationMeta,
    target: str,
    path_params: dict[str, Any],
    query_params: dict[str, Any],
    payload: dict[str, Any],
    args: argparse.Namespace,
) -> None:
    _verify_plan_signature(plan)
    if plan.get("operation_id") != operation.operation_id:
        raise SafetyError("Plan operation_id does not match this command")
    if plan.get("command") != operation.command:
        raise SafetyError("Plan command does not match this command")
    if str(plan.get("target")) != str(target):
        raise SafetyError("Plan target does not match this command")
    if plan.get("input_sha256") != _sha256_text(json.dumps(payload, sort_keys=True)):
        raise SafetyError("Plan input hash does not match this command input")
    parameter_sha256 = _sha256_text(
        json.dumps(
            {
                "path": path_params,
                "query": query_params,
            },
            sort_keys=True,
        )
    )
    stored_parameter_hash = plan.get("parameter_sha256")
    if stored_parameter_hash is not None and stored_parameter_hash != parameter_sha256:
        raise SafetyError("Plan parameter hash does not match this command input")

    expires_at = plan.get("expires_at_utc")
    if not isinstance(expires_at, str):
        raise SafetyError("Plan has expired")
    try:
        parsed_expiry = datetime.strptime(expires_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError as exc:
        raise SafetyError("Plan has expired") from exc
    if datetime.now(UTC) >= parsed_expiry:
        raise SafetyError("Plan has expired")

    idempotency_key = plan.get("idempotency_key")
    if not isinstance(idempotency_key, str) or not re.fullmatch(r"[0-9a-f]{32}", idempotency_key):
        raise SafetyError("Plan idempotency key is missing or invalid")

    if bool(plan.get("snapshot", {}).get("requires_no_snapshot_ack", False)):
        if not bool(plan.get("snapshot", {}).get("snapshot_accepted", False)):
            if not bool(args.ack_no_snapshot):
                raise SafetyError("Plan requires --ack-no-snapshot")


def _apply_from_plan(
    *,
    operation: OperationMeta,
    cfg: Config,
    args: argparse.Namespace,
    path_params: dict[str, Any],
    query_params: dict[str, Any],
    payload: dict[str, Any],
    transport: Transport,
    plan: dict[str, Any],
) -> dict[str, Any]:
    _assert_authenticated(operation, cfg)
    target = _effective_target(operation, path_params, query_params)
    _compare_plan(
        plan,
        operation,
        target,
        path_params,
        query_params,
        payload,
        args,
    )
    if operation.secret_bearing_result and not args.secret_out:
        raise SafetyError("Secret-bearing results require --secret-out")

    asks = _operation_acks(operation)
    missing: list[str] = []
    if asks["ack_send"] and not bool(args.ack_send):
        missing.append("--ack-send")
    if asks["ack_spend"] and not bool(args.ack_spend):
        missing.append("--ack-spend")
    if asks["ack_terms"] and not bool(args.ack_terms):
        missing.append("--ack-terms")
    if asks["ack_destructive"] and not bool(args.ack_destructive):
        missing.append("--ack-destructive")
    if asks["ack_secret"] and not bool(args.ack_secret):
        missing.append("--ack-secret")
    if asks["ack_no_snapshot"] and not bool(args.ack_no_snapshot):
        missing.append("--ack-no-snapshot")
    if missing:
        raise SafetyError(f"Missing required acknowledgement flags: {', '.join(missing)}")
    if not bool(args.yes):
        raise SafetyError("Apply requires --yes")

    idempotency_key = str(plan["idempotency_key"])
    planned_cost_signature = None
    if operation.billable:
        if not operation.native_dry_run:
            raise SafetyError("Billable write has no supported fresh cost validation")
        planned_cost_signature = plan.get("dry_run", {}).get("cost_signature")
        if not _valid_cost_signature(planned_cost_signature):
            raise SafetyError("Billable plan cost signature is missing or invalid")

    sensitive_values = _request_sensitive_values(cfg, path_params, query_params, payload)
    secret_reservation: AtomicFileReservation | None = None
    receipt_reservation: AtomicFileReservation | None = None
    try:
        receipt_destination = _receipt_path(args, plan)
        _validate_output_file_roles(
            args,
            {
                "secret output (--secret-out)": (
                    str(args.secret_out) if operation.secret_bearing_result else None
                ),
                "receipt output (--receipt-out/default)": receipt_destination,
            },
        )
        if operation.secret_bearing_result:
            secret_reservation = reserve_atomic_file(str(args.secret_out))
        receipt_reservation = reserve_atomic_file(receipt_destination)

        if operation.billable:
            dry_run_result, _ = _execute_api_call(
                operation=operation,
                cfg=cfg,
                path_params=path_params,
                query_params=query_params,
                payload=payload,
                transport=transport,
                include_dry_run_overlay=True,
            )
            fresh_signature = _compute_cost_signature(dry_run_result)
            if not _valid_cost_signature(fresh_signature):
                raise SafetyError("Fresh billable cost signature is missing or invalid")
            if not hmac.compare_digest(str(planned_cost_signature), fresh_signature):
                raise SafetyError("Billable write drift detected: cost signature changed")

        response, meta = _execute_api_call(
            operation=operation,
            cfg=cfg,
            path_params=path_params,
            query_params=query_params,
            payload=payload,
            transport=transport,
            idempotency_key=idempotency_key if operation.method == "POST" else None,
        )

        if secret_reservation is not None:
            secret_reservation.commit_text(
                json.dumps(response, ensure_ascii=False, indent=2) + "\n"
            )

        verification: dict[str, Any] = {
            "performed": False,
            "confirmed": False,
            "details": "No reliable readback operation is configured",
        }
        readback_op_id = operation.snapshot_plan.get("readback_operation_id")
        if readback_op_id:
            rb_operation = _OPERATION_MAP.get(str(readback_op_id))
            if rb_operation:
                try:
                    response_values = response if isinstance(response, dict) else {}
                    rb_path_params, rb_query_params = _derive_operation_args(
                        operation=rb_operation,
                        parsed_path=path_params,
                        parsed_query=query_params,
                        payload={**payload, **response_values},
                    )
                    rb_payload, _ = _execute_api_call(
                        operation=rb_operation,
                        cfg=cfg,
                        path_params=rb_path_params,
                        query_params=rb_query_params,
                        payload={},
                        transport=transport,
                    )
                    verification = {
                        "performed": True,
                        "confirmed": False,
                        "details": sanitize(rb_payload, sensitive_values),
                        "note": "Readback was captured but not semantically compared; review it before claiming the intended state.",
                    }
                except ToolError as exc:  # noqa: BLE001
                    verification = {
                        "performed": True,
                        "confirmed": False,
                        "details": scrub_text(str(exc), sensitive_values),
                        "note": "Readback failed; the write result is not independently confirmed.",
                    }

        receipt_payload = {
            "schema_version": 2,
            "tool": "porkbun",
            "version": __version__,
            "operation_id": operation.operation_id,
            "command": operation.command,
            "target": target,
            "applied_at_utc": _iso_now(),
            "changed": True,
            "idempotency_key": idempotency_key,
            "transport": {
                "request_id": meta.request_id,
                "api_version": meta.api_version,
                "rate_limits": meta.rate_limits,
                "retry_after": meta.retry_after,
            },
            "result": (
                sanitize(response, sensitive_values)
                if not operation.secret_bearing_result
                else {"status": "stored"}
            ),
            "verification": {
                "requested": bool(readback_op_id),
                **verification,
            },
            "plan_hash": plan.get("plan_hash"),
            "input_sha256": _sha256_text(json.dumps(payload, sort_keys=True)),
            "command_input_signature": _target_signature(
                operation,
                target,
                payload,
                dry_run_overlay=False,
            ),
        }
        if operation.secret_bearing_result:
            receipt_payload["result_stored"] = True
        receipt_payload = sanitize(receipt_payload, sensitive_values)
        receipt_path = receipt_reservation.commit_json(receipt_payload)

        return {
            "ok": True,
            "dry_run": False,
            "receipt": receipt_payload,
            "receipt_out": receipt_path,
            "transport": {
                "request_id": meta.request_id,
                "api_version": meta.api_version,
                "rate_limits": meta.rate_limits,
                "retry_after": meta.retry_after,
            },
        }
    except Exception:
        if secret_reservation is not None:
            secret_reservation.cleanup()
        if receipt_reservation is not None:
            receipt_reservation.cleanup()
        raise


def build_parser() -> _ToolArgumentParser:
    parser = _ToolArgumentParser(prog="porkbun", add_help=True)
    parser.add_argument("--version", action="store_true", help="Print installed tool version")
    parser.add_argument("--env-file", default=".env", help="Path to .env file")
    parser.add_argument("--output", default="json", choices=("json", "text"))
    parser.add_argument("--verbose", action="store_true", help="Print debug details to stderr")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Keep unexpected failures in scrubbed structured output",
    )
    parser.add_argument("--timeout-s", type=float, help="Request timeout")

    parser.add_argument("--plan-out", default=None, help="Where to write write-plan")
    parser.add_argument("--plan-in", default=None, help="Read a write plan for apply")
    parser.add_argument("--receipt-out", default=None, help="Where to write apply receipt")
    parser.add_argument("--secret-out", default=None, help="Where to write full secret-bearing result")
    parser.add_argument("--yes", action="store_true", help="Required for apply")
    parser.add_argument("--ack-spend", action="store_true", help="Ack spend-related operations")
    parser.add_argument("--ack-terms", action="store_true", help="Ack terms")
    parser.add_argument("--ack-destructive", action="store_true", help="Ack destructive operations")
    parser.add_argument("--ack-secret", action="store_true", help="Ack secret output")
    parser.add_argument("--ack-send", action="store_true", help="Ack send-heavy operations")
    parser.add_argument("--ack-no-snapshot", action="store_true", help="Ack no-snapshot plans")

    parser.set_defaults(plan_in=None, plan_out=None, receipt_out=None, secret_out=None)

    sub = parser.add_subparsers(dest="_cmd_group", required=False)

    onboarding = sub.add_parser("onboarding", help="Create placeholder .env file")
    onboarding.set_defaults(handler=_cmd_onboarding)

    auth = sub.add_parser("auth", help="Auth checks")
    auth_sub = auth.add_subparsers(dest="_auth_cmd", required=True)
    auth_check = auth_sub.add_parser("check", help="Auth check with ping endpoint")
    auth_check.set_defaults(handler=_cmd_auth_check)

    operations = sub.add_parser("operations", help="Operation metadata")
    operations_sub = operations.add_subparsers(dest="_operations_cmd", required=True)
    operations_list = operations_sub.add_parser("list", help="List provider operations")
    operations_list.set_defaults(handler=_cmd_operations_list)

    families: dict[str, dict[str, OperationMeta]] = {}
    for operation in _OPERATION_MAP.values():
        families.setdefault(operation.family_slug, {})[operation.kebab_operation_id] = operation

    for family_slug, ops in sorted(families.items()):
        family = sub.add_parser(family_slug, help=f"{family_slug} commands")
        family_sub = family.add_subparsers(dest="_operation", required=True)
        for op in sorted(ops.values(), key=lambda i: i.kebab_operation_id):
            node = family_sub.add_parser(op.kebab_operation_id, help=f"{op.operation_id}")
            file_only_parameters = (
                {"token"} if op.operation_id == "getAccountInviteStatus" else set()
            )
            for param in op.parameters:
                if param.get("in") not in {"path", "query"}:
                    continue
                name = str(param.get("name") or "").strip()
                if not name:
                    continue
                if name in file_only_parameters:
                    continue
                flag = f"--{_to_dashed(name)}"
                required = bool(param.get("required", False))
                node.add_argument(flag, dest=_to_dashed(name).replace("-", "_"), required=required)
            has_body = _operation_has_request_body(op) or bool(file_only_parameters)
            if has_body:
                node.add_argument("--input", default=None, help="JSON input file path")
            if op.write:
                node.add_argument("--apply", action="store_true")
            node.set_defaults(handler=_run_operation, operation=op)

    return parser


def _cmd_operations_list(args: argparse.Namespace, cfg: Config | None, out: Output, transport: Transport | None = None) -> int:
    inventory = _resource_inventory()
    rows = [
        {
            "command": op["command"],
            "operation_id": op["operation_id"],
            "family": op["family_slug"],
            "method": op["method"],
            "write": op["write"],
            "auth": op["auth"],
        }
        for op in inventory["operations"]
    ]
    out.emit({"ok": True, "count": len(rows), "operations": rows})
    return 0


def _cmd_onboarding(args: argparse.Namespace, cfg: Config | None, out: Output, transport: Transport | None = None) -> int:
    env_file = Path(args.env_file)
    created = False
    if env_file.is_symlink():
        raise ValidationError("Onboarding env target cannot be a symbolic link")
    if env_file.exists() and not env_file.is_file():
        raise ValidationError("Onboarding env target must be a regular file")
    if not env_file.exists():
        atomic_write_text(
            env_file,
            "PORKBUN_API_HOST=default\n"
            "PORKBUN_API_KEY=\n"
            "PORKBUN_SECRET_API_KEY=\n"
            "PORKBUN_TIMEOUT_S=30\n",
        )
        created = True

    out.emit(
        {
            "ok": True,
            "onboarding": {
                "env_file": str(env_file),
                "env_created": created,
                "next_steps": [
                    "Fill PORKBUN_API_KEY and PORKBUN_SECRET_API_KEY in .env",
                    "Run: porkbun auth check",
                ],
            },
        }
    )
    return 0


def _cmd_auth_check(args: argparse.Namespace, cfg: Config | None, out: Output, transport: Transport | None = None) -> int:
    op = _find_operation_by_command("porkbun utility ping-get")
    if transport is None:
        transport = RequestsTransport()

    if cfg is None:
        cfg = load_config(args.env_file)

    path_params, query_params = _split_path_query(op, args)

    if not cfg.api_key or not cfg.secret_api_key:
        out.emit({"ok": True, "command": op.command, "authenticated": False, "response": {"credentialsValid": False}})
        return 0

    data, meta = _execute_api_call(
        operation=op,
        cfg=cfg,
        path_params=path_params,
        query_params=query_params,
        payload={},
        transport=transport,
        force_auth_headers=True,
    )

    credentials_valid = bool(data.get("credentialsValid")) if isinstance(data, dict) else False
    out.emit(
        {
            "ok": True,
            "command": op.command,
            "authenticated": credentials_valid,
            "transport": {
                "request_id": meta.request_id,
                "api_version": meta.api_version,
                "rate_limits": meta.rate_limits,
                "retry_after": meta.retry_after,
            },
        }
    )
    return 0


def _run_operation(args: argparse.Namespace, cfg: Config | None, out: Output, transport: Transport | None = None) -> int:
    operation: OperationMeta = args.operation
    if transport is None:
        transport = RequestsTransport()
    if cfg is None:
        cfg = load_config(args.env_file)

    _assert_authenticated(operation, cfg)
    path_params, query_params = _split_path_query(operation, args)
    payload = _coerce_input_payload(getattr(args, "input", None))
    payload = _validate_body(operation, payload)
    path_params, query_params = _derive_operation_args(
        operation=operation,
        parsed_path=path_params,
        parsed_query=query_params,
        payload=payload,
    )
    _validate_parameters(operation, {**path_params, **query_params})
    request_payload = payload if _operation_has_request_body(operation) else {}

    target = _effective_target(operation, path_params, query_params)

    if not operation.write:
        if operation.secret_bearing_result and not getattr(args, "secret_out", None):
            raise SafetyError("Secret-bearing results require --secret-out")
        if operation.secret_bearing_result and not bool(args.ack_secret):
            raise SafetyError("Secret-bearing results require --ack-secret")

        sensitive_values = _request_sensitive_values(
            cfg,
            path_params,
            query_params,
            payload,
        )
        reservation: AtomicFileReservation | None = None
        try:
            if operation.secret_bearing_result:
                _validate_output_file_roles(
                    args,
                    {"secret output (--secret-out)": str(args.secret_out)},
                )
                reservation = reserve_atomic_file(str(args.secret_out))
            response, meta = _execute_api_call(
                operation=operation,
                cfg=cfg,
                path_params=path_params,
                query_params=query_params,
                payload=request_payload,
                transport=transport,
            )
            if reservation is not None:
                reservation.commit_text(
                    json.dumps(response, ensure_ascii=False, indent=2) + "\n"
                )
        except Exception:
            if reservation is not None:
                reservation.cleanup()
            raise

        if operation.secret_bearing_result:
            out.emit(
                {
                    "ok": True,
                    "dry_run": False,
                    "command": operation.command,
                    "operation_id": operation.operation_id,
                    "result_stored": True,
                    "response": {"result": "stored"},
                    "transport": {
                        "request_id": meta.request_id,
                        "api_version": meta.api_version,
                        "rate_limits": meta.rate_limits,
                        "retry_after": meta.retry_after,
                    },
                }
            )
            return 0
        out.emit(
            {
                "ok": True,
                "dry_run": False,
                "command": operation.command,
                "operation_id": operation.operation_id,
                "response": sanitize(response, sensitive_values),
                "transport": {
                    "request_id": meta.request_id,
                    "api_version": meta.api_version,
                    "rate_limits": meta.rate_limits,
                    "retry_after": meta.retry_after,
                },
            }
        )
        return 0

    if bool(args.apply):
        if not args.plan_in:
            raise SafetyError("Apply requires --plan-in")
        plan_obj = _load_json_file(args.plan_in)
        result = _apply_from_plan(
            operation=operation,
            cfg=cfg,
            args=args,
            path_params=path_params,
            query_params=query_params,
            payload=payload,
            transport=transport,
            plan=plan_obj,
        )
        out.emit(result)
        return 0

    plan_obj, _ = _create_plan(
        operation=operation,
        cfg=cfg,
        args=args,
        path_params=path_params,
        query_params=query_params,
        payload=payload,
        transport=transport,
        target=target,
    )
    out.emit({"ok": True, "dry_run": True, "command": operation.command, "plan": _redact(plan_obj), "plan_out": plan_obj.get("plan_out")})
    return 0


def _load_json_file(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise ValidationError(f"Plan file does not exist: {p}")
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise ValidationError(f"Invalid plan JSON: {p}") from exc
    if not isinstance(payload, dict):
        raise ValidationError("Plan file must be an object")
    return payload


def _coerce_output_mode(argv: list[str]) -> str:
    try:
        idx = argv.index("--output")
    except ValueError:
        return "json"
    if idx + 1 >= len(argv):
        return "json"
    value = str(argv[idx + 1]).lower()
    return value if value in {"json", "text"} else "json"


def _normalize_global_flags(argv: list[str]) -> list[str]:
    global_flags_with_value = {
        "--env-file",
        "--output",
        "--timeout-s",
        "--plan-out",
        "--plan-in",
        "--receipt-out",
        "--secret-out",
    }
    global_bool_flags = {
        "--verbose",
        "--debug",
        "--yes",
        "--ack-spend",
        "--ack-terms",
        "--ack-destructive",
        "--ack-secret",
        "--ack-send",
        "--ack-no-snapshot",
        "--version",
    }

    globals_: list[str] = []
    others: list[str] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in global_flags_with_value:
            globals_.append(arg)
            if i + 1 >= len(argv):
                break
            i += 1
            globals_.append(argv[i])
            i += 1
            continue
        if arg in global_bool_flags:
            globals_.append(arg)
            i += 1
            continue
        others.append(arg)
        i += 1
    return globals_ + others


def main(argv: list[str] | None = None, transport: Transport | None = None) -> int:
    if argv is None:
        import sys

        argv = sys.argv[1:]
    argv = _normalize_global_flags(list(argv))

    out = Output(
        mode=_coerce_output_mode(argv),
        sensitive_values=_sensitive_values_from_argv(argv),
    )
    parser = build_parser()

    try:
        args = parser.parse_args(argv)
    except ValidationError as exc:
        out.emit({"ok": False, "error_type": "ValidationError", "error": str(exc)})
        return 1

    if args.version:
        out.emit({"ok": True, "tool": "porkbun", "version": __version__, "command": "version"})
        return 0

    try:
        command = str(args._cmd_group or "")
        if command in {"", "None"}:
            parser.error("Missing command")

        cfg = load_config(args.env_file) if command not in {"onboarding"} else None
        if cfg is not None:
            out.add_sensitive_values((cfg.api_key, cfg.secret_api_key))
        if cfg is not None and args.timeout_s is not None:
            if args.timeout_s <= 0:
                raise ValidationError("--timeout-s must be greater than zero")
            cfg = Config(
                api_host=cfg.api_host,
                api_key=cfg.api_key,
                secret_api_key=cfg.secret_api_key,
                timeout_s=float(args.timeout_s),
            )

        handler = getattr(args, "handler", None)
        if handler is None:
            parser.error("Unknown command")

        typed_handler = cast(Callable[..., int], handler)
        return int(typed_handler(args=args, cfg=cfg, out=out, transport=transport))
    except ValidationError as exc:
        out.emit({"ok": False, "error_type": "ValidationError", "error": str(exc)})
        return 1
    except AuthError as exc:
        out.emit({"ok": False, "error_type": "AuthError", "error": str(exc)})
        return 1
    except SafetyError as exc:
        out.emit({"ok": True, "refused": True, "error_type": "SafetyError", "reasons": [str(exc)]})
        return 0
    except ProviderError as exc:
        out.emit(
            {
                "ok": False,
                "error_type": "ProviderError",
                "error": exc.message,
                "code": exc.code,
                "request_id": exc.request_id,
                "api_version": exc.api_version,
                "rate_limits": exc.rate_limits,
                "retry_after": exc.retry_after,
            }
        )
        return 1
    except Exception as exc:  # noqa: BLE001
        out.emit({"ok": False, "error_type": type(exc).__name__, "error": str(exc)})
        return 1
