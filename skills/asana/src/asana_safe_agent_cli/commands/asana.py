from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import stat
import time
from contextlib import ExitStack
from pathlib import Path
from typing import Any
from urllib.parse import quote

from ..errors import SafetyError, ToolError, ValidationError
from ..http import HttpClient, HttpResponse
from ..inventory import manifest, operation_for_command, operation_for_id, operations
from ..json_files import get_or_create_private_bytes, read_json_file, write_json_file

_TOOL_NAME = "qwayk-asana-safe-agent-cli"
_PLAN_SCHEMA_VERSION = 2
_PLAN_INTEGRITY_ALGORITHM = "HMAC-SHA256"
_ROLLBACK_STATEMENT = {
    "supported": False,
    "note": "A before-state is review evidence, not a promised restore path.",
}

_SECRET_KEYS = {
    "access_token",
    "authorization",
    "client_secret",
    "password",
    "personal_access_token",
    "refresh_token",
    "secret",
    "service_account_token",
    "token",
    "x-hook-secret",
    "x_hook_secret",
}


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): (
                "***REDACTED***"
                if str(key).lower() in _SECRET_KEYS
                or str(key).lower().endswith("_secret")
                or str(key).lower().endswith("_token")
                else _redact(item)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _safe_json(response: HttpResponse) -> Any:
    if not response.body:
        return None
    try:
        return _redact(response.json())
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _request_id(response: HttpResponse) -> str | None:
    for key in ("x-request-id", "asana-request-id", "x-asana-request-id"):
        if response.headers.get(key):
            return response.headers[key]
    return None


def _error_for_response(response: HttpResponse) -> ToolError:
    suffix = f" Request ID: {_request_id(response)}." if _request_id(response) else ""
    return ToolError(f"Asana returned HTTP {response.status}; no change is reported as successful.{suffix}")


def _parse_key_values(values: list[str] | None) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw in values or []:
        if "=" not in raw:
            raise ValidationError(f"Expected NAME=VALUE, got: {raw}")
        key, value = raw.split("=", 1)
        key = key.strip()
        if not key:
            raise ValidationError("Parameter name cannot be empty")
        if key in parsed:
            raise ValidationError(f"Parameter was provided more than once: {key}")
        parsed[key] = value
    return parsed


def _coerce_parameter(raw: str, parameter: dict[str, Any]) -> Any:
    value_type = parameter.get("type")
    if value_type == "boolean":
        lowered = raw.lower()
        if lowered not in {"true", "false", "1", "0", "yes", "no"}:
            raise ValidationError(f"{parameter['name']} must be true or false")
        return "true" if lowered in {"true", "1", "yes"} else "false"
    if value_type == "integer":
        try:
            return int(raw)
        except ValueError:
            raise ValidationError(f"{parameter['name']} must be an integer") from None
    if value_type == "number":
        try:
            return float(raw)
        except ValueError:
            raise ValidationError(f"{parameter['name']} must be a number") from None
    allowed = parameter.get("enum")
    if isinstance(allowed, list) and raw not in {str(item) for item in allowed}:
        raise ValidationError(
            f"{parameter['name']} must be one of: {', '.join(str(item) for item in allowed)}"
        )
    return raw


def _target(
    operation: dict[str, Any], raw_params: list[str] | None
) -> tuple[str, dict[str, Any], dict[str, str]]:
    supplied = _parse_key_values(raw_params)
    parameter_defs: dict[str, dict[str, Any]] = {}
    for parameter in operation["parameters"]:
        name = str(parameter.get("name") or "")
        if name:
            parameter_defs[name] = parameter
    unknown = sorted(set(supplied) - set(parameter_defs))
    if unknown:
        raise ValidationError(
            f"Unknown parameter(s) for {operation['command']}: {', '.join(unknown)}"
        )
    missing = sorted(
        name
        for name, parameter in parameter_defs.items()
        if parameter.get("required") and name not in supplied
    )
    if missing:
        raise ValidationError(f"Missing required parameter(s): {', '.join(missing)}")
    path = str(operation["path"])
    query: dict[str, Any] = {}
    for name, raw in supplied.items():
        parameter = parameter_defs[name]
        value = _coerce_parameter(raw, parameter)
        if parameter.get("in") == "path":
            if not str(value).strip():
                raise ValidationError(f"Path parameter cannot be empty: {name}")
            path = path.replace("{" + name + "}", quote(str(value), safe=""))
        elif parameter.get("in") == "query":
            query[name] = value
        else:
            raise ValidationError(f"Unsupported parameter location for {name}")
    if "{" in path or "}" in path:
        raise ValidationError("Not all path parameters were resolved")
    return path, query, supplied


def _parse_body(data_json: str | None, data_file: str | None) -> dict[str, Any] | None:
    if data_json and data_file:
        raise ValidationError("Use only one of --data-json or --data-file")
    value: Any = None
    if data_json:
        try:
            value = json.loads(data_json)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"--data-json is invalid JSON: {exc.msg}") from None
    elif data_file:
        value = read_json_file(data_file)
    if value is not None and not isinstance(value, dict):
        raise ValidationError("Request data must be one JSON object")
    if isinstance(value, dict) and _redact(value) != value:
        raise ValidationError("Request data contains a secret-like field that cannot be saved safely")
    return value


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_metadata(values: list[str] | None, operation: dict[str, Any]) -> list[dict[str, Any]]:
    raw_files = _parse_key_values(values)
    request_body = operation.get("request_body")
    multipart_schema = (
        request_body.get("content", {}).get("multipart/form-data", {})
        if isinstance(request_body, dict)
        else {}
    )
    if raw_files and not multipart_schema:
        raise ValidationError("--file is allowed only for the fixed attachment upload command")
    allowed_file_fields = {
        name
        for name, metadata in multipart_schema.get("properties", {}).items()
        if metadata.get("format") == "binary"
    }
    unknown_file_fields = sorted(set(raw_files) - allowed_file_fields)
    if unknown_file_fields:
        raise ValidationError(
            f"Unknown documented file field(s): {', '.join(unknown_file_fields)}"
        )
    metadata: list[dict[str, Any]] = []
    for field, raw_path in raw_files.items():
        path = Path(raw_path).expanduser().resolve()
        if not path.is_file():
            raise ValidationError(f"Upload file not found: {path}")
        metadata.append(
            {
                "field": field,
                "path": str(path),
                "name": path.name,
                "size": path.stat().st_size,
                "sha256": _file_sha256(path),
            }
        )
    return metadata


def _validate_body(operation: dict[str, Any], body: dict[str, Any] | None, files: list[dict[str, Any]]) -> None:
    if body is not None and _redact(body) != body:
        raise ValidationError("Request data contains a secret-like field that cannot be saved safely")
    request_body = operation.get("request_body")
    if request_body and request_body.get("required") and body is None and not files:
        raise ValidationError(f"{operation['command']} requires --data-json, --data-file, or --file")
    if (
        request_body
        and "multipart/form-data" in request_body.get("content", {})
        and body is None
        and not files
    ):
        raise ValidationError(f"{operation['command']} requires attachment form data or --file")
    if not request_body and body is not None:
        raise ValidationError(f"{operation['command']} does not accept a request body")
    if body is not None and request_body:
        content = request_body.get("content", {})
        if not ({"application/json", "multipart/form-data"} & set(content)):
            raise ValidationError("This operation's documented request body is not supported")
        media_type = "multipart/form-data" if "multipart/form-data" in content else "application/json"
        schema = content[media_type]
        allowed = set(schema.get("properties", {}))
        unknown = sorted(set(body) - allowed)
        if unknown:
            raise ValidationError(
                f"Undocumented top-level request field(s): {', '.join(unknown)}"
            )
        missing = sorted(set(schema.get("required", [])) - set(body))
        if missing:
            raise ValidationError(f"Missing required request field(s): {', '.join(missing)}")
        if media_type == "application/json" and "data" not in body:
            raise ValidationError("Asana JSON write bodies require a top-level `data` object")
        for name, value in body.items():
            expected_type = schema.get("properties", {}).get(name, {}).get("type")
            valid = {
                "object": isinstance(value, dict),
                "array": isinstance(value, list),
                "string": isinstance(value, str),
                "boolean": isinstance(value, bool),
                "integer": isinstance(value, int) and not isinstance(value, bool),
                "number": isinstance(value, (int, float)) and not isinstance(value, bool),
            }.get(expected_type, True)
            if not valid:
                raise ValidationError(f"Request field {name} must be {expected_type}")
        if operation["operation_id"] == "createAttachmentForObject" and "connect_to_app" in body:
            raise ValidationError("connect_to_app belongs to the excluded App Components surface")


def _validate_file_metadata(
    operation: dict[str, Any], value: Any
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise SafetyError("Plan file metadata is invalid")
    request_body = operation.get("request_body")
    multipart_schema = (
        request_body.get("content", {}).get("multipart/form-data", {})
        if isinstance(request_body, dict)
        else {}
    )
    allowed_fields = {
        name
        for name, metadata in multipart_schema.get("properties", {}).items()
        if metadata.get("format") == "binary"
    }
    validated: list[dict[str, Any]] = []
    seen: set[str] = set()
    expected_keys = {"field", "path", "name", "size", "sha256"}
    for item in value:
        if not isinstance(item, dict) or set(item) != expected_keys:
            raise SafetyError("Plan file metadata is invalid")
        field = item.get("field")
        if not isinstance(field, str) or field not in allowed_fields or field in seen:
            raise SafetyError("Plan contains an undocumented or duplicate file field")
        raw_path = item.get("path")
        if not isinstance(raw_path, str):
            raise SafetyError("Plan file path is invalid")
        path = Path(raw_path).expanduser().resolve()
        if not path.is_file():
            raise SafetyError(f"Planned upload file is unavailable: {path.name}")
        actual = {
            "field": field,
            "path": str(path),
            "name": path.name,
            "size": path.stat().st_size,
            "sha256": _file_sha256(path),
        }
        if actual != item:
            raise SafetyError(f"Upload file metadata changed after planning: {path.name}")
        seen.add(field)
        validated.append(actual)
    return validated


def _risk_for_request(
    operation: dict[str, Any], body: dict[str, Any] | None, file_metadata: list[dict[str, Any]]
) -> tuple[str, list[str]]:
    risk_reasons = set(operation["risk_reasons"])

    def inspect_request(value: Any, *, key: str = "") -> None:
        lowered = key.lower()
        if lowered in {"assignee", "followers", "members", "member", "approval_status"}:
            risk_reasons.add("visible collaboration, notification, or approval effect")
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                inspect_request(child_value, key=str(child_key))
        elif isinstance(value, list):
            if len(value) > 1:
                risk_reasons.add("bulk or fan-out request data")
            for child in value:
                inspect_request(child, key=key)

    inspect_request(body)
    if len(file_metadata) > 1:
        risk_reasons.add("multiple file upload")
    risk_class = "write_stronger_approval" if risk_reasons else "write"
    return risk_class, sorted(risk_reasons)


def _client(ctx: dict[str, Any]) -> HttpClient:
    injected = ctx.get("http_client")
    if injected is not None:
        return injected
    return HttpClient(
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"qwayk-asana-safe-agent-cli/{ctx['tool_version']}",
    )


def _send(
    *,
    client: HttpClient,
    ctx: dict[str, Any],
    method: str,
    path: str,
    query: dict[str, Any],
    body: dict[str, Any] | None,
    file_metadata: list[dict[str, Any]],
) -> HttpResponse:
    url = str(ctx["cfg"].base_url).rstrip("/") + "/" + path.lstrip("/")
    headers = {"Authorization": f"Bearer {ctx['cfg'].token}", "Accept": "application/json"}
    with ExitStack() as stack:
        files: dict[str, tuple[str, Any]] = {}
        for item in file_metadata:
            file_path = Path(str(item["path"]))
            actual_hash = _file_sha256(file_path)
            if actual_hash != item["sha256"]:
                raise SafetyError(f"Upload file changed after planning: {file_path.name}")
            handle = stack.enter_context(file_path.open("rb"))
            files[str(item["field"])] = (str(item["name"]), handle)
        multipart = bool(files)
        return client.request(
            method,
            url,
            headers=headers,
            params=query,
            json_body=None if multipart else body,
            data=body if multipart else None,
            files=files or None,
            retries=2 if method == "GET" else 0,
        )


def _snapshot(
    operation: dict[str, Any],
    *,
    client: HttpClient,
    ctx: dict[str, Any],
    path: str,
    query: dict[str, Any],
) -> dict[str, Any]:
    snapshot_id = operation.get("snapshot_operation_id")
    if not snapshot_id:
        return {
            "available": False,
            "warning": "Asana does not expose a reliable same-target before-state for this operation.",
        }
    snapshot_operation = operation_for_id(str(snapshot_id))
    response = _send(
        client=client,
        ctx=ctx,
        method="GET",
        path=path,
        query={key: value for key, value in query.items() if key in {"opt_fields", "opt_pretty"}},
        body=None,
        file_metadata=[],
    )
    if response.status >= 300:
        return {
            "available": False,
            "warning": f"Before-state read `{snapshot_operation['command']}` returned HTTP {response.status}.",
        }
    data = _safe_json(response)
    return {
        "available": True,
        "operation_id": snapshot_id,
        "captured_at_utc": _utc_now(),
        "sha256": _canonical_hash(data),
        "data": data,
    }


def _plan_fingerprint(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in plan.items()
        if key not in {"generated_at_utc", "integrity", "plan_id"}
    }


def _state_root(env_file: str) -> Path:
    return Path(env_file).expanduser().resolve().parent / ".state"


def _signing_key_path(env_file: str) -> Path:
    return _state_root(env_file) / "plan-signing.key"


def _signing_key(env_file: str, *, create: bool) -> bytes:
    key_path = _signing_key_path(env_file)
    if create:
        key = get_or_create_private_bytes(key_path, secrets.token_bytes(32))
    else:
        if not key_path.is_file():
            raise SafetyError("The local plan-signing key is missing; create a new plan")
        mode = stat.S_IMODE(key_path.stat().st_mode)
        if mode & 0o077:
            key_path.chmod(mode & 0o600)
        key = key_path.read_bytes()
    if len(key) != 32:
        raise SafetyError("The local plan-signing key is invalid; create a new private state directory")
    return key


def _integrity_payload(plan: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in plan.items() if key != "integrity"}


def _sign_plan(plan: dict[str, Any], *, env_file: str) -> None:
    key = _signing_key(env_file, create=True)
    plan["integrity"] = {
        "algorithm": _PLAN_INTEGRITY_ALGORITHM,
        "key_id": hashlib.sha256(key).hexdigest()[:16],
        "signature": hmac.new(key, _canonical_bytes(_integrity_payload(plan)), hashlib.sha256).hexdigest(),
    }


def _write_plan(plan: dict[str, Any], *, env_file: str, requested_path: str | None) -> str:
    target = (
        Path(requested_path).expanduser()
        if requested_path
        else _state_root(env_file) / "plans" / f"{plan['plan_id']}.json"
    )
    return write_json_file(target, _redact(plan))


def _build_plan(
    operation: dict[str, Any],
    *,
    path: str,
    query: dict[str, Any],
    parameter_inputs: dict[str, str],
    body: dict[str, Any] | None,
    file_metadata: list[dict[str, Any]],
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    risk_class, risk_reasons = _risk_for_request(operation, body, file_metadata)
    plan: dict[str, Any] = {
        "schema_version": _PLAN_SCHEMA_VERSION,
        "tool": _TOOL_NAME,
        "generated_at_utc": _utc_now(),
        "operation_id": operation["operation_id"],
        "command": operation["command"],
        "method": operation["method"],
        "parameter_inputs": parameter_inputs,
        "target": {"path": path, "query": query},
        "request_body": body,
        "files": file_metadata,
        "risk_class": risk_class,
        "risk_reasons": risk_reasons,
        "snapshot": snapshot,
        "verification_operation_id": operation.get("verification_operation_id"),
        "rollback": dict(_ROLLBACK_STATEMENT),
    }
    plan["plan_id"] = _canonical_hash(_plan_fingerprint(plan))[:20]
    return plan


def _validate_snapshot_contract(snapshot: Any, operation: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("available"), bool):
        raise SafetyError("Plan snapshot metadata is invalid")
    snapshot_id = operation.get("snapshot_operation_id")
    if not snapshot_id:
        expected = {
            "available": False,
            "warning": "Asana does not expose a reliable same-target before-state for this operation.",
        }
        if snapshot != expected:
            raise SafetyError("Plan snapshot does not match the fixed operation")
        return dict(expected)
    if snapshot["available"]:
        if set(snapshot) != {"available", "operation_id", "captured_at_utc", "sha256", "data"}:
            raise SafetyError("Plan snapshot metadata is invalid")
        if snapshot.get("operation_id") != snapshot_id:
            raise SafetyError("Plan snapshot operation does not match the fixed operation")
        if not isinstance(snapshot.get("captured_at_utc"), str):
            raise SafetyError("Plan snapshot capture time is invalid")
        if snapshot.get("sha256") != _canonical_hash(snapshot.get("data")):
            raise SafetyError("Plan snapshot content identity is invalid")
        return dict(snapshot)
    snapshot_operation = operation_for_id(str(snapshot_id))
    warning = snapshot.get("warning")
    prefix = f"Before-state read `{snapshot_operation['command']}` returned HTTP "
    if set(snapshot) != {"available", "warning"} or not isinstance(warning, str):
        raise SafetyError("Plan no-snapshot metadata is invalid")
    status = warning.removeprefix(prefix).removesuffix(".")
    if not warning.startswith(prefix) or not warning.endswith(".") or not status.isdigit():
        raise SafetyError("Plan no-snapshot reason does not match the fixed operation")
    return dict(snapshot)


def _revalidate_plan(plan: dict[str, Any], operation: dict[str, Any]) -> dict[str, Any]:
    expected_keys = {
        "schema_version",
        "tool",
        "generated_at_utc",
        "operation_id",
        "command",
        "method",
        "parameter_inputs",
        "target",
        "request_body",
        "files",
        "risk_class",
        "risk_reasons",
        "snapshot",
        "verification_operation_id",
        "rollback",
        "plan_id",
        "integrity",
    }
    if set(plan) != expected_keys:
        raise SafetyError("Plan fields do not match the authenticated plan schema")
    if plan.get("schema_version") != _PLAN_SCHEMA_VERSION or plan.get("tool") != _TOOL_NAME:
        raise SafetyError("Plan tool or schema does not match this runtime")
    if plan.get("operation_id") != operation["operation_id"] or plan.get("command") != operation["command"]:
        raise SafetyError("Plan operation does not match the selected fixed command")
    if plan.get("method") != operation["method"]:
        raise SafetyError("Plan method does not match the selected fixed command")
    parameter_inputs = plan.get("parameter_inputs")
    if not isinstance(parameter_inputs, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in parameter_inputs.items()
    ):
        raise SafetyError("Plan parameter inputs are invalid")
    path, query, reconstructed_inputs = _target(
        operation, [f"{key}={value}" for key, value in parameter_inputs.items()]
    )
    target = plan.get("target")
    expected_target = {"path": path, "query": query}
    if reconstructed_inputs != parameter_inputs or target != expected_target:
        raise SafetyError("Plan target does not match the fixed operation and validated inputs")
    body_value = plan.get("request_body")
    if body_value is not None and not isinstance(body_value, dict):
        raise SafetyError("Plan request body is invalid")
    body = body_value if isinstance(body_value, dict) else None
    files = _validate_file_metadata(operation, plan.get("files"))
    _validate_body(operation, body, files)
    risk_class, risk_reasons = _risk_for_request(operation, body, files)
    if plan.get("risk_class") != risk_class or plan.get("risk_reasons") != risk_reasons:
        raise SafetyError("Plan risk classification does not match the fixed operation and request")
    snapshot = _validate_snapshot_contract(plan.get("snapshot"), operation)
    verification_id = operation.get("verification_operation_id")
    if plan.get("verification_operation_id") != verification_id:
        raise SafetyError("Plan verification does not match the fixed operation")
    if plan.get("rollback") != _ROLLBACK_STATEMENT:
        raise SafetyError("Plan rollback statement does not match this runtime")
    trusted = dict(plan)
    trusted.update(
        {
            "method": operation["method"],
            "target": expected_target,
            "request_body": body,
            "files": files,
            "risk_class": risk_class,
            "risk_reasons": risk_reasons,
            "snapshot": snapshot,
            "verification_operation_id": verification_id,
            "rollback": dict(_ROLLBACK_STATEMENT),
        }
    )
    return trusted


def _load_and_validate_plan(path: str, operation: dict[str, Any], *, env_file: str) -> dict[str, Any]:
    value = read_json_file(path)
    if not isinstance(value, dict):
        raise ValidationError("Plan file must contain one JSON object")
    integrity = value.get("integrity")
    if not isinstance(integrity, dict) or set(integrity) != {"algorithm", "key_id", "signature"}:
        raise SafetyError("Plan is missing authenticated local integrity; create a new plan")
    key = _signing_key(env_file, create=False)
    expected_key_id = hashlib.sha256(key).hexdigest()[:16]
    expected_signature = hmac.new(
        key, _canonical_bytes(_integrity_payload(value)), hashlib.sha256
    ).hexdigest()
    if (
        integrity.get("algorithm") != _PLAN_INTEGRITY_ALGORITHM
        or integrity.get("key_id") != expected_key_id
        or not isinstance(integrity.get("signature"), str)
        or not hmac.compare_digest(integrity["signature"], expected_signature)
    ):
        raise SafetyError("Plan authenticated integrity check failed; create and review a new plan")
    expected = _canonical_hash(_plan_fingerprint(value))[:20]
    if value.get("plan_id") != expected:
        raise SafetyError("Plan contents changed after the plan ID was created")
    return _revalidate_plan(value, operation)


def _assert_snapshot_unchanged(
    plan: dict[str, Any], *, operation: dict[str, Any], client: HttpClient, ctx: dict[str, Any]
) -> None:
    snapshot = plan.get("snapshot")
    if not isinstance(snapshot, dict) or not snapshot.get("available"):
        return
    current = _snapshot(
        operation,
        client=client,
        ctx=ctx,
        path=str(plan["target"]["path"]),
        query=dict(plan["target"].get("query") or {}),
    )
    if not current.get("available"):
        raise SafetyError("The before-state can no longer be read; create and review a new plan")
    if current.get("sha256") != snapshot.get("sha256"):
        raise SafetyError("The Asana target changed after planning; create and review a new plan")


def _subset(expected: Any, actual: Any) -> bool:
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and _subset(value, actual[key]) for key, value in expected.items()
        )
    if isinstance(expected, list):
        return expected == actual
    return expected == actual


def _verify(
    plan: dict[str, Any],
    operation: dict[str, Any],
    *,
    client: HttpClient,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    verification_id = plan.get("verification_operation_id")
    if not verification_id:
        return {
            "verified": False,
            "reason": "The official specification does not provide a reliable same-target readback.",
        }
    response = _send(
        client=client,
        ctx=ctx,
        method="GET",
        path=str(plan["target"]["path"]),
        query={
            key: value
            for key, value in dict(plan["target"].get("query") or {}).items()
            if key in {"opt_fields", "opt_pretty"}
        },
        body=None,
        file_metadata=[],
    )
    if operation["method"] == "DELETE":
        return {
            "verified": response.status in {404, 410},
            "method": "same-target absence readback",
            "status": response.status,
        }
    if response.status >= 300:
        return {"verified": False, "method": "same-target readback", "status": response.status}
    actual = _safe_json(response)
    expected_body = plan.get("request_body")
    if isinstance(expected_body, dict) and isinstance(actual, dict):
        expected_data = expected_body.get("data", expected_body)
        actual_data = actual.get("data", actual)
        matched = _subset(expected_data, actual_data)
    else:
        matched = True
    return {
        "verified": matched,
        "method": "same-target readback",
        "status": response.status,
        "requested_fields_match": matched,
    }


def _async_state(operation: dict[str, Any], response: HttpResponse, payload: Any) -> str:
    if response.status == 202:
        return "accepted"
    if not operation.get("async"):
        return "request_completed"
    data = payload.get("data") if isinstance(payload, dict) else None
    status = data.get("status") if isinstance(data, dict) else None
    if isinstance(status, str):
        return status
    return "accepted_or_started_unverified"


def _find_job_gid(payload: Any) -> str | None:
    if isinstance(payload, dict):
        if payload.get("resource_type") == "job" and payload.get("gid"):
            return str(payload["gid"])
        for key, value in payload.items():
            if key in {"job", "new_job"} and isinstance(value, dict) and value.get("gid"):
                return str(value["gid"])
            found = _find_job_gid(value)
            if found:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = _find_job_gid(value)
            if found:
                return found
    return None


def _poll_job(
    job_gid: str,
    *,
    client: HttpClient,
    ctx: dict[str, Any],
    timeout_s: float,
    interval_s: float,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_s
    history: list[str] = []
    while True:
        response = _send(
            client=client,
            ctx=ctx,
            method="GET",
            path=f"/jobs/{quote(job_gid, safe='')}",
            query={},
            body=None,
            file_metadata=[],
        )
        if response.status >= 300:
            return {"state": "poll_failed", "status": response.status, "history": history}
        payload = _safe_json(response)
        data = payload.get("data") if isinstance(payload, dict) else None
        state = str(data.get("status") or "unknown") if isinstance(data, dict) else "unknown"
        history.append(state)
        if state in {"succeeded", "failed"}:
            return {"state": state, "history": history, "job": payload}
        if time.monotonic() >= deadline:
            return {"state": "running_or_queued", "history": history, "timed_out": True}
        time.sleep(interval_s)


def cmd_commands_list(args: Any, ctx: dict[str, Any]) -> int:
    rows = []
    for operation in operations():
        if not operation.get("command"):
            continue
        if args.family and operation["family"].lower() != args.family.lower():
            continue
        if args.method and operation["method"] != args.method:
            continue
        if args.writes_only and operation["method"] == "GET":
            continue
        rows.append(
            {
                "command": operation["command"],
                "family": operation["family"],
                "method": operation["method"],
                "operation_id": operation["operation_id"],
                "risk_class": operation["risk_class"],
                "summary": operation["summary"],
            }
        )
    ctx["out"].emit({"ok": True, "count": len(rows), "commands": rows, "manifest": manifest()})
    return 0


def cmd_commands_show(args: Any, ctx: dict[str, Any]) -> int:
    operation = operation_for_command(str(args.operation))
    ctx["out"].emit({"ok": True, "operation": operation})
    return 0


def cmd_auth_check(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    response = _send(
        client=_client(ctx),
        ctx=ctx,
        method="GET",
        path="/users/me",
        query={"opt_fields": "gid,name,resource_type"},
        body=None,
        file_metadata=[],
    )
    if response.status >= 300:
        raise _error_for_response(response)
    payload = _safe_json(response)
    data = payload.get("data") if isinstance(payload, dict) else None
    identity = (
        {key: data.get(key) for key in ("gid", "name", "resource_type")}
        if isinstance(data, dict)
        else None
    )
    ctx["out"].emit(
        {
            "ok": True,
            "connected": True,
            "base_url": ctx["cfg"].base_url,
            "identity": identity,
        }
    )
    return 0


def _read_pages(
    operation: dict[str, Any],
    *,
    client: HttpClient,
    ctx: dict[str, Any],
    path: str,
    query: dict[str, Any],
    paginate: bool,
    max_pages: int,
) -> tuple[HttpResponse, Any, int]:
    page = 0
    all_data: list[Any] = []
    last_response: HttpResponse | None = None
    last_payload: Any = None
    working_query = dict(query)
    while True:
        page += 1
        response = _send(
            client=client,
            ctx=ctx,
            method="GET",
            path=path,
            query=working_query,
            body=None,
            file_metadata=[],
        )
        if response.status >= 300:
            raise _error_for_response(response)
        payload = _safe_json(response)
        last_response, last_payload = response, payload
        if not paginate:
            break
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            break
        all_data.extend(payload["data"])
        next_page = payload.get("next_page")
        offset = next_page.get("offset") if isinstance(next_page, dict) else None
        if not offset or not payload["data"] or page >= max_pages:
            last_payload = {**payload, "data": all_data, "pages_fetched": page}
            break
        working_query["offset"] = offset
    assert last_response is not None
    return last_response, last_payload, page


def cmd_api(args: Any, ctx: dict[str, Any]) -> int:
    operation = operation_for_command(str(args.operation))
    client = _client(ctx)
    if operation["method"] == "GET":
        if args.apply or args.plan_in or args.approve:
            raise ValidationError("Read commands do not accept write approval flags")
        path, query, _ = _target(operation, args.param)
        response, payload, pages = _read_pages(
            operation,
            client=client,
            ctx=ctx,
            path=path,
            query=query,
            paginate=bool(args.paginate),
            max_pages=int(args.max_pages),
        )
        content_type = response.headers.get("content-type", "")
        if payload is None and response.body:
            if not args.download_to:
                raise SafetyError("Binary or non-JSON content must be written with --download-to")
            download_path = Path(args.download_to).expanduser()
            download_path.parent.mkdir(parents=True, exist_ok=True)
            download_path.write_bytes(response.body)
            payload = {
                "saved_to": str(download_path),
                "bytes": len(response.body),
                "sha256": hashlib.sha256(response.body).hexdigest(),
                "content_type": content_type,
            }
        result = {
            "ok": True,
            "command": operation["command"],
            "operation_id": operation["operation_id"],
            "status": response.status,
            "state": _async_state(operation, response, payload),
            "pages_fetched": pages,
            "result": payload,
        }
        ctx["audit"].write("asana.read", {key: result[key] for key in result if key != "result"})
        ctx["out"].emit(result)
        return 0

    if args.apply:
        if not args.plan_in:
            raise SafetyError("Apply requires --plan-in with the saved plan")
        if args.param or args.data_json or args.data_file or args.file:
            raise SafetyError("Apply uses only the saved plan; do not repeat request parameters or data")
        plan = _load_and_validate_plan(args.plan_in, operation, env_file=ctx["env_file"])
        if not args.approve or args.approve != plan["plan_id"]:
            raise SafetyError(f"Apply requires --approve {plan['plan_id']}")
        snapshot = plan.get("snapshot")
        if isinstance(snapshot, dict) and not snapshot.get("available") and not args.acknowledge_no_snapshot:
            raise SafetyError("This plan has no reliable before-state; add --acknowledge-no-snapshot")
        if plan.get("risk_class") == "write_stronger_approval" and not args.acknowledge_risk:
            reasons = ", ".join(str(reason) for reason in plan.get("risk_reasons", []))
            raise SafetyError(f"This operation requires --acknowledge-risk: {reasons}")
        _assert_snapshot_unchanged(plan, operation=operation, client=client, ctx=ctx)
        response = _send(
            client=client,
            ctx=ctx,
            method=str(plan["method"]),
            path=str(plan["target"]["path"]),
            query=dict(plan["target"].get("query") or {}),
            body=plan.get("request_body") if isinstance(plan.get("request_body"), dict) else None,
            file_metadata=list(plan.get("files") or []),
        )
        payload = _safe_json(response)
        provider_ok = response.status < 300
        verification = (
            _verify(plan, operation, client=client, ctx=ctx)
            if provider_ok
            else {"verified": False, "reason": "Provider request failed"}
        )
        state = _async_state(operation, response, payload)
        async_followup: dict[str, Any] | None = None
        if provider_ok and operation.get("async") and args.wait:
            job_gid = _find_job_gid(payload)
            async_followup = (
                _poll_job(
                    job_gid,
                    client=client,
                    ctx=ctx,
                    timeout_s=float(args.wait_timeout_s),
                    interval_s=float(args.poll_interval_s),
                )
                if job_gid
                else {
                    "state": "accepted_or_started_unverified",
                    "reason": "The response did not include a job GID; use the fixed status command for this resource.",
                }
            )
            state = str(async_followup["state"])
        receipt = {
            "schema_version": 1,
            "tool": "qwayk-asana-safe-agent-cli",
            "applied_at_utc": _utc_now(),
            "plan_id": plan["plan_id"],
            "operation_id": operation["operation_id"],
            "command": operation["command"],
            "provider_status": response.status,
            "request_id": _request_id(response),
            "state": state,
            "verification": verification,
            "async_followup": async_followup,
            "result": payload,
            "rollback": {"supported": False},
        }
        receipt_target = (
            Path(args.receipt_out).expanduser()
            if args.receipt_out
            else _state_root(ctx["env_file"]) / "receipts" / f"{plan['plan_id']}.json"
        )
        receipt_path = write_json_file(receipt_target, _redact(receipt))
        result = {
            "ok": provider_ok,
            "dry_run": False,
            "state": state,
            "receipt": receipt,
            "receipt_out": receipt_path,
        }
        ctx["audit"].write(
            "asana.write.applied" if provider_ok else "asana.write.failed",
            {
                "plan_id": plan["plan_id"],
                "operation_id": operation["operation_id"],
                "provider_status": response.status,
                "receipt_out": receipt_path,
            },
        )
        ctx["out"].emit(result)
        return 0 if provider_ok else 1

    if args.plan_in or args.approve or args.acknowledge_no_snapshot or args.acknowledge_risk:
        raise ValidationError("Approval flags are used only with --apply")
    path, query, parameter_inputs = _target(operation, args.param)
    body = _parse_body(args.data_json, args.data_file)
    file_metadata = _file_metadata(args.file, operation)
    _validate_body(operation, body, file_metadata)
    snapshot = _snapshot(
        operation,
        client=client,
        ctx=ctx,
        path=path,
        query=query,
    )
    plan = _build_plan(
        operation,
        path=path,
        query=query,
        parameter_inputs=parameter_inputs,
        body=body,
        file_metadata=file_metadata,
        snapshot=snapshot,
    )
    _sign_plan(plan, env_file=ctx["env_file"])
    plan_path = _write_plan(plan, env_file=ctx["env_file"], requested_path=args.plan_out)
    result = {
        "ok": True,
        "dry_run": True,
        "plan": plan,
        "plan_out": plan_path,
        "next_action": f"Review the plan, then apply with --plan-in {plan_path} --apply --approve {plan['plan_id']}.",
    }
    ctx["audit"].write(
        "asana.write.planned",
        {"plan_id": plan["plan_id"], "operation_id": operation["operation_id"], "plan_out": plan_path},
    )
    ctx["out"].emit(result)
    return 0
