from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import time
from contextlib import ExitStack
from importlib.resources import files as package_files
from pathlib import Path
from typing import Any
from urllib.parse import quote

from . import __version__
from .config import Config
from .errors import NotSupportedError, SafetyError, ToolError, ValidationError
from .http import HttpClient, HttpResponse

SECRET_KEYS = {
    "api_token",
    "authorization",
    "cookie",
    "password",
    "secret",
    "token",
}
PROTECTED_HEADERS = {"authorization", "cookie", "set-cookie"}
PUBLIC_CURSOR_TOKEN_KEYS = {"continuationtoken", "nextpagetoken", "pagetoken"}


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load_inventory() -> dict[str, Any]:
    resource = package_files("jira_safe_agent_cli").joinpath("operations.json")
    data = json.loads(resource.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("operation_count") != 721:
        raise RuntimeError("Packaged Jira operation inventory is invalid")
    return data


def operation_map(inventory: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(operation["surface"]), str(operation["command"])): operation
        for operation in inventory["operations"]
    }


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            lowered = str(key).lower()
            compact = re.sub(r"[^a-z0-9]", "", lowered)
            if (
                lowered in SECRET_KEYS
                or compact in {"apikey", "authorization", "cookie", "password", "secret", "token"}
                or compact.endswith("secret")
                or compact.endswith("password")
                or (
                    (compact.endswith("token") or compact.endswith("tokens"))
                    and compact not in PUBLIC_CURSOR_TOKEN_KEYS
                )
            ):
                result[key] = "***REDACTED***"
            else:
                result[key] = redact(item)
        return result
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def plan_signing_key_path(env_file: str) -> Path:
    return Path(env_file).expanduser().resolve().parent / ".state" / "plan-signing.key"


def load_plan_signing_key(env_file: str, *, create: bool) -> bytes:
    path = plan_signing_key_path(env_file)
    if not path.exists():
        if not create:
            raise SafetyError(
                "The local plan-signing key is missing; create and review a new plan on this install"
            )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(secrets.token_bytes(32))
        os.chmod(path, 0o600)
    if not path.is_file() or path.is_symlink():
        raise SafetyError("The local plan-signing key path is unsafe")
    if os.stat(path).st_mode & 0o077:
        raise SafetyError("The local plan-signing key must use mode 0600")
    key = path.read_bytes()
    if len(key) != 32:
        raise SafetyError("The local plan-signing key is invalid")
    return key


def sign_plan(plan: dict[str, Any], key: bytes) -> dict[str, Any]:
    signed = dict(plan)
    signed.pop("integrity_hmac_sha256", None)
    signed["integrity_hmac_sha256"] = hmac.new(
        key, canonical_hash(signed).encode("ascii"), hashlib.sha256
    ).hexdigest()
    return signed


def write_private_json(path: Path, value: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.chmod(path, 0o600)
    return str(path)


def parse_pairs(values: list[str] | None, *, label: str) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for raw in values or []:
        if "=" not in raw:
            raise ValidationError(f"{label} must use name=value: {raw}")
        key, value = raw.split("=", 1)
        key = key.strip()
        if not key:
            raise ValidationError(f"{label} has an empty name")
        result.append((key, value))
    return result


def _arg_value(args: Any, parameter: dict[str, Any]) -> Any:
    return getattr(args, parameter["cli_flag"][2:].replace("-", "_"), None)


def _body_descriptor(args: Any, operation: dict[str, Any]) -> dict[str, Any] | None:
    content_types = operation["request_content_types"]
    body_file = getattr(args, "body_file", None)
    file_pairs = parse_pairs(getattr(args, "file", None), label="--file")
    form = parse_pairs(getattr(args, "form", None), label="--form")
    selected = getattr(args, "content_type", None)
    if selected and selected not in content_types:
        raise ValidationError(f"Unsupported --content-type for this command: {selected}")
    if file_pairs or form:
        if "multipart/form-data" not in content_types:
            raise ValidationError("--file and --form are only valid for multipart operations")
        if body_file:
            raise ValidationError("Do not combine --body-file with --file or --form")
        files_out = []
        for field, raw_path in file_pairs:
            path = Path(raw_path).expanduser().resolve()
            if not path.is_file():
                raise ValidationError(f"Upload file not found: {path}")
            files_out.append(
                {
                    "field": field,
                    "path": str(path),
                    "sha256": file_sha256(path),
                    "size": path.stat().st_size,
                }
            )
        return {
            "mode": "multipart",
            "content_type": "multipart/form-data",
            "files": files_out,
            "form": [{"name": name, "value": value} for name, value in form],
        }
    if body_file:
        path = Path(body_file).expanduser().resolve()
        if not path.is_file():
            raise ValidationError(f"Body file not found: {path}")
        content_type = selected
        if not content_type:
            content_type = next(
                (
                    item
                    for item in content_types
                    if item in {"application/json", "application/json-patch+json"}
                ),
                content_types[0] if content_types else "application/json",
            )
        if content_type == "*/*":
            try:
                json.loads(path.read_text(encoding="utf-8"))
                content_type = "application/json"
            except (UnicodeDecodeError, json.JSONDecodeError):
                content_type = "application/octet-stream"
        if content_type in {"application/json", "application/json-patch+json"}:
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValidationError(f"Body file is not valid JSON: {exc}") from None
        return {
            "mode": "file",
            "content_type": content_type,
            "path": str(path),
            "sha256": file_sha256(path),
            "size": path.stat().st_size,
        }
    if operation["request_body_required"]:
        raise ValidationError(
            "This command requires --body-file, or multipart --file/--form inputs"
        )
    return None


def _required_values(args: Any, operation: dict[str, Any]) -> None:
    missing = [
        parameter["cli_flag"]
        for parameter in operation["parameters"]
        if parameter["required"] and _arg_value(args, parameter) is None
    ]
    if missing:
        raise ValidationError("Missing required input(s): " + ", ".join(missing))


def build_plan(args: Any, config: Config, operation: dict[str, Any]) -> dict[str, Any]:
    _required_values(args, operation)
    path = str(operation["path"])
    query: dict[str, Any] = {}
    headers: dict[str, str] = {}
    inputs: dict[str, Any] = {}
    for parameter in operation["parameters"]:
        value = _arg_value(args, parameter)
        if value is None:
            continue
        inputs[parameter["name"]] = value
        if parameter["in"] == "path":
            path = path.replace("{" + parameter["name"] + "}", quote(str(value), safe=""))
        elif parameter["in"] == "query":
            if parameter["free_form_object"]:
                for name, item in parse_pairs(value, label=parameter["cli_flag"]):
                    query[name] = item
            else:
                query[parameter["name"]] = value
        elif parameter["in"] == "header":
            if parameter["name"].lower() in PROTECTED_HEADERS:
                raise ValidationError(
                    f"Protected header cannot be supplied as an operation input: {parameter['name']}"
                )
            headers[parameter["name"]] = str(value)
    if "{" in path or "}" in path:
        raise ValidationError("Not all path parameters were resolved")
    body = _body_descriptor(args, operation)
    no_snapshot = operation["kind"] == "write" and not operation["snapshot_get_available"]
    snapshot_query = {
        name: query[name] for name in operation["snapshot_query_names"] if name in query
    }
    core = {
        "schema_version": 2,
        "tool": "jira-safe",
        "tool_version": __version__,
        "created_at": utc_now(),
        "surface": operation["surface"],
        "command": operation["command"],
        "operation_id": operation["operation_id"],
        "base_url": config.base_url,
        "method": operation["method"],
        "path": path,
        "query": query,
        "headers": headers,
        "body": body,
        "kind": operation["kind"],
        "high_risk": operation["high_risk"],
        "snapshot_get_available": operation["snapshot_get_available"],
        "snapshot_query": snapshot_query,
        "no_snapshot_warning": (
            "No reliable generic before-state read exists for this operation. Apply requires --ack-no-snapshot."
            if no_snapshot
            else None
        ),
        "live_unverified": True,
        "inputs": inputs,
    }
    return core


def _expected_request_from_inputs(
    inputs: Any, operation: dict[str, Any]
) -> tuple[str, dict[str, Any], dict[str, str], dict[str, Any]]:
    if not isinstance(inputs, dict):
        raise SafetyError("Plan inputs are invalid")
    parameters = {str(item["name"]): item for item in operation["parameters"]}
    if set(inputs) - set(parameters):
        raise SafetyError("Plan contains inputs outside the selected fixed command")
    path = str(operation["path"])
    query: dict[str, Any] = {}
    headers: dict[str, str] = {}
    for name, parameter in parameters.items():
        value = inputs.get(name)
        if value is None:
            if parameter["required"]:
                raise SafetyError(f"Plan is missing required fixed-command input: {name}")
            continue
        location = parameter["in"]
        if location == "path":
            path = path.replace("{" + name + "}", quote(str(value), safe=""))
        elif location == "query":
            if parameter["free_form_object"]:
                if not isinstance(value, list):
                    raise SafetyError("The free-form property filter is invalid")
                for item_name, item_value in parse_pairs(value, label=parameter["cli_flag"]):
                    query[item_name] = item_value
            else:
                query[name] = value
        elif location == "header":
            if name.lower() in PROTECTED_HEADERS:
                raise SafetyError("Plan contains a protected request header")
            headers[name] = str(value)
    if "{" in path or "}" in path:
        raise SafetyError("Plan has unresolved fixed-command path parameters")
    snapshot_query = {
        name: query[name] for name in operation["snapshot_query_names"] if name in query
    }
    return path, query, headers, snapshot_query


def _validate_body_descriptor(body: Any, operation: dict[str, Any]) -> None:
    content_types = set(operation["request_content_types"])
    if body is None:
        if operation["request_body_required"]:
            raise SafetyError("Plan is missing its required request body")
        return
    if not isinstance(body, dict):
        raise SafetyError("Plan body descriptor is invalid")
    mode = body.get("mode")
    if mode == "file":
        if set(body) != {"mode", "content_type", "path", "sha256", "size"}:
            raise SafetyError("Plan file-body descriptor has unexpected fields")
        allowed = set(content_types)
        if "*/*" in allowed:
            allowed.update({"application/json", "application/octet-stream"})
        if body.get("content_type") not in allowed or body.get("content_type") == "*/*":
            raise SafetyError("Plan file-body content type is outside the fixed operation")
        if not isinstance(body.get("path"), str) or not Path(body["path"]).is_absolute():
            raise SafetyError("Plan file-body path is invalid")
        if not re.fullmatch(r"[0-9a-f]{64}", str(body.get("sha256") or "")):
            raise SafetyError("Plan file-body digest is invalid")
        if not isinstance(body.get("size"), int) or body["size"] < 0:
            raise SafetyError("Plan file-body size is invalid")
        return
    if mode == "multipart":
        if "multipart/form-data" not in content_types:
            raise SafetyError("Plan multipart body is outside the fixed operation")
        if set(body) != {"mode", "content_type", "files", "form"}:
            raise SafetyError("Plan multipart descriptor has unexpected fields")
        if body.get("content_type") != "multipart/form-data":
            raise SafetyError("Plan multipart content type is invalid")
        if not isinstance(body.get("files"), list) or not isinstance(body.get("form"), list):
            raise SafetyError("Plan multipart entries are invalid")
        for entry in body["files"]:
            if not isinstance(entry, dict) or set(entry) != {"field", "path", "sha256", "size"}:
                raise SafetyError("Plan multipart file descriptor is invalid")
            if not isinstance(entry["field"], str) or not entry["field"]:
                raise SafetyError("Plan multipart file field is invalid")
            if not isinstance(entry["path"], str) or not Path(entry["path"]).is_absolute():
                raise SafetyError("Plan multipart file path is invalid")
            if not re.fullmatch(r"[0-9a-f]{64}", str(entry["sha256"])):
                raise SafetyError("Plan multipart file digest is invalid")
            if not isinstance(entry["size"], int) or entry["size"] < 0:
                raise SafetyError("Plan multipart file size is invalid")
        for entry in body["form"]:
            if not isinstance(entry, dict) or set(entry) != {"name", "value"}:
                raise SafetyError("Plan multipart form descriptor is invalid")
            if not isinstance(entry["name"], str) or not isinstance(entry["value"], str):
                raise SafetyError("Plan multipart form entry is invalid")
        return
    raise SafetyError("Plan body mode is outside the selected fixed operation")


def validate_plan(
    plan: Any, config: Config, operation: dict[str, Any], signing_key: bytes
) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must contain one JSON object")
    allowed_keys = {
        "schema_version", "tool", "tool_version", "created_at", "surface", "command",
        "operation_id", "base_url", "method", "path", "query", "headers", "body", "kind",
        "high_risk", "snapshot_get_available", "snapshot_query", "no_snapshot_warning",
        "live_unverified", "inputs", "integrity_hmac_sha256",
    }
    if set(plan) != allowed_keys:
        raise SafetyError("Plan fields do not match the fixed saved-plan schema")
    signature = plan.get("integrity_hmac_sha256")
    core = {key: value for key, value in plan.items() if key != "integrity_hmac_sha256"}
    expected_signature = hmac.new(
        signing_key, canonical_hash(core).encode("ascii"), hashlib.sha256
    ).hexdigest()
    if not isinstance(signature, str) or not hmac.compare_digest(signature, expected_signature):
        raise SafetyError("Plan integrity check failed")
    no_snapshot = operation["kind"] == "write" and not operation["snapshot_get_available"]
    for key, expected in {
        "schema_version": 2,
        "tool": "jira-safe",
        "tool_version": __version__,
        "surface": operation["surface"],
        "command": operation["command"],
        "operation_id": operation["operation_id"],
        "method": operation["method"],
        "base_url": config.base_url,
        "kind": operation["kind"],
        "high_risk": operation["high_risk"],
        "snapshot_get_available": operation["snapshot_get_available"],
        "no_snapshot_warning": (
            "No reliable generic before-state read exists for this operation. Apply requires --ack-no-snapshot."
            if no_snapshot else None
        ),
        "live_unverified": True,
    }.items():
        if plan.get(key) != expected:
            raise SafetyError(f"Plan does not match the selected Jira target or command: {key}")
    path, query, headers, snapshot_query = _expected_request_from_inputs(
        plan.get("inputs"), operation
    )
    for key, expected in {
        "path": path,
        "query": query,
        "headers": headers,
        "snapshot_query": snapshot_query,
    }.items():
        if plan.get(key) != expected:
            raise SafetyError(f"Plan request does not match its fixed-command inputs: {key}")
    _validate_body_descriptor(plan.get("body"), operation)
    return plan


def load_plan(path: str) -> Any:
    plan_path = Path(path).expanduser().resolve()
    if not plan_path.is_file():
        raise ValidationError(f"Plan file not found: {plan_path}")
    try:
        return json.loads(plan_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Plan file is not valid JSON: {exc}") from None


def _load_body(
    descriptor: dict[str, Any] | None, stack: ExitStack
) -> tuple[Any, Any, Any, dict[str, str]]:
    if not descriptor:
        return None, None, None, {}
    mode = descriptor.get("mode")
    if mode == "multipart":
        files_payload: list[tuple[str, Any]] = []
        for entry in descriptor.get("files") or []:
            path = Path(entry["path"])
            if not path.is_file() or file_sha256(path) != entry["sha256"]:
                raise SafetyError(f"Multipart file changed after planning: {path}")
            handle = stack.enter_context(path.open("rb"))
            files_payload.append((entry["field"], (path.name, handle)))
        form_payload = [(entry["name"], entry["value"]) for entry in descriptor.get("form") or []]
        return None, form_payload, files_payload, {"X-Atlassian-Token": "no-check"}
    path = Path(descriptor["path"])
    if not path.is_file() or file_sha256(path) != descriptor["sha256"]:
        raise SafetyError(f"Body file changed after planning: {path}")
    content_type = str(descriptor["content_type"])
    raw = path.read_bytes()
    if content_type in {"application/json", "application/json-patch+json"}:
        return json.loads(raw.decode("utf-8")), None, None, {"Content-Type": content_type}
    if content_type == "text/plain":
        return None, raw.decode("utf-8"), None, {"Content-Type": content_type}
    return None, raw, None, {"Content-Type": content_type}


def _response_payload(response: HttpResponse, response_out: str | None) -> dict[str, Any]:
    content_type = response.headers.get("content-type", "").split(";", 1)[0].lower()
    if not response.body:
        body: Any = None
    elif "json" in content_type or response.body[:1] in {b"{", b"["}:
        try:
            body = redact(response.json())
        except (json.JSONDecodeError, UnicodeDecodeError):
            body = response.text()
    elif content_type.startswith("text/"):
        body = response.text()
    else:
        if not response_out:
            raise ValidationError("Jira returned binary content; rerun with --response-out FILE")
        output_path = Path(response_out).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.body)
        os.chmod(output_path, 0o600)
        body = {
            "saved_to": str(output_path),
            "size": len(response.body),
            "sha256": file_sha256(output_path),
        }
    return {
        "status": response.status,
        "url": response.url,
        "content_type": content_type or None,
        "body": body,
    }


def _client(config: Config, verbose: bool) -> HttpClient:
    return HttpClient(config=config, verbose=verbose, user_agent=f"jira-safe/{__version__}")


def _request_from_plan(
    client: HttpClient, plan: dict[str, Any], *, response_out: str | None, retries: int
) -> dict[str, Any]:
    url = str(plan["base_url"]) + str(plan["path"])
    with ExitStack() as stack:
        json_body, data, files_payload, body_headers = _load_body(plan.get("body"), stack)
        headers = {**(plan.get("headers") or {}), **body_headers}
        response = client.request(
            str(plan["method"]),
            url,
            headers=headers,
            params=plan.get("query") or None,
            json_body=json_body,
            data=data,
            files=files_payload,
            retries=retries,
        )
    return _response_payload(response, response_out)


def _has_apply_inputs(args: Any, operation: dict[str, Any]) -> bool:
    return any(
        _arg_value(args, parameter) is not None for parameter in operation["parameters"]
    ) or any(getattr(args, name, None) for name in ("body_file", "file", "form", "content_type"))


def run_operation(args: Any, ctx: dict[str, Any]) -> int:
    operation = ctx["operation"]
    out = ctx["out"]
    if not operation["callable_with_supported_auth"]:
        raise NotSupportedError(
            f"{operation['full_command']} is {operation['coverage_status']}: {operation['coverage_note']}"
        )
    require_auth = operation["kind"] == "read" or bool(args.apply)
    config = ctx["config_loader"](require_auth=require_auth)
    if operation["coverage_status"] == "implemented-oauth-only" and config.auth_mode != "bearer":
        raise NotSupportedError("This operation requires JIRA_OAUTH_ACCESS_TOKEN")

    if operation["kind"] == "read":
        plan = build_plan(args, config, operation)
        response = _request_from_plan(
            _client(config, bool(args.verbose)), plan, response_out=args.response_out, retries=2
        )
        payload = {"ok": True, "operation": operation["operation_id"], "result": response}
        ctx["audit"].write(
            "jira.read", {"operation": operation["operation_id"], "status": response["status"]}
        )
        out.emit(payload)
        return 0

    if not args.apply:
        plan = build_plan(args, config, operation)
        plan = sign_plan(plan, load_plan_signing_key(ctx["env_file"], create=True))
        plan_path = Path(ctx["plan_out"]).expanduser().resolve()
        write_private_json(plan_path, plan)
        payload = {
            "ok": True,
            "dry_run": True,
            "operation": operation["operation_id"],
            "target": {"base_url": config.base_url, "path": plan["path"]},
            "high_risk": plan["high_risk"],
            "snapshot_get_available": plan["snapshot_get_available"],
            "warning": plan["no_snapshot_warning"],
            "plan_path": str(plan_path),
            "next": "Review the saved plan, then rerun this fixed command with --apply --plan-in and the required approvals.",
        }
        ctx["audit"].write("jira.plan", payload)
        out.emit(payload)
        return 0

    if not args.plan_in:
        raise SafetyError("Apply requires --plan-in with a reviewed saved plan")
    if _has_apply_inputs(args, operation):
        raise SafetyError(
            "Apply reads inputs only from the saved plan; remove operation input flags"
        )
    plan = validate_plan(
        load_plan(args.plan_in),
        config,
        operation,
        load_plan_signing_key(ctx["env_file"], create=False),
    )
    if not args.yes:
        raise SafetyError("Apply requires --yes")
    if plan["high_risk"] and not args.ack_high_risk:
        raise SafetyError("This production-risk operation requires --ack-high-risk")
    if not plan["snapshot_get_available"] and not args.ack_no_snapshot:
        raise SafetyError("No reliable before-state read exists; apply requires --ack-no-snapshot")

    client = _client(config, bool(args.verbose))
    snapshot: dict[str, Any] | None = None
    snapshot_error: str | None = None
    if plan["snapshot_get_available"]:
        try:
            snapshot_response = client.request(
                "GET",
                config.base_url + plan["path"],
                params=plan.get("snapshot_query") or None,
                retries=2,
            )
            snapshot = _response_payload(
                snapshot_response, str(Path(ctx["artifacts_dir"]) / "before-response.bin")
            )
            write_private_json(Path(ctx["artifacts_dir"]) / "before.json", snapshot)
        except Exception as exc:  # noqa: BLE001
            snapshot_error = type(exc).__name__
            if not args.ack_no_snapshot:
                raise SafetyError(
                    "The before-state read failed; inspect access and rerun with --ack-no-snapshot only if you accept that risk"
                ) from None

    receipt_path = Path(ctx["receipt_out"]).expanduser().resolve()
    receipt: dict[str, Any] = {
        "schema_version": 1,
        "tool": "jira-safe",
        "tool_version": __version__,
        "applied_at": utc_now(),
        "operation": operation["operation_id"],
        "surface": operation["surface"],
        "command": operation["command"],
        "method": plan["method"],
        "base_url": config.base_url,
        "path": plan["path"],
        "plan_integrity_hmac_sha256": plan["integrity_hmac_sha256"],
        "snapshot_saved": snapshot is not None,
        "snapshot_error_type": snapshot_error,
        "high_risk_approved": bool(args.ack_high_risk),
        "no_snapshot_approved": bool(args.ack_no_snapshot),
        "live_unverified_build": True,
    }
    provider_response_out = args.response_out or str(
        Path(ctx["artifacts_dir"]) / "provider-response.bin"
    )
    try:
        result = _request_from_plan(client, plan, response_out=provider_response_out, retries=0)
        receipt["provider_result"] = result
    except ToolError as exc:
        receipt["ok"] = False
        receipt["provider_status"] = getattr(exc, "status", None)
        receipt["provider_error_type"] = type(exc).__name__
        write_private_json(receipt_path, redact(receipt))
        raise

    verification: dict[str, Any] | None = None
    if plan["snapshot_get_available"]:
        try:
            verify_response = client.request(
                "GET",
                config.base_url + plan["path"],
                params=plan.get("snapshot_query") or None,
                retries=2,
                raise_for_status=False,
            )
            if plan["method"] == "DELETE":
                verification = {
                    "expected_absent": True,
                    "status": verify_response.status,
                    "verified": verify_response.status == 404,
                }
            else:
                verification = {
                    "expected_readable": True,
                    "status": verify_response.status,
                    "verified": verify_response.status < 400,
                }
                if verify_response.status < 400:
                    write_private_json(
                        Path(ctx["artifacts_dir"]) / "after.json",
                        _response_payload(
                            verify_response,
                            str(Path(ctx["artifacts_dir"]) / "after-response.bin"),
                        ),
                    )
        except ToolError as exc:
            verification = {
                "verified": False,
                "error_type": type(exc).__name__,
                "status": getattr(exc, "status", None),
            }
    receipt["verification"] = verification
    receipt["ok"] = True
    write_private_json(receipt_path, redact(receipt))
    ctx["audit"].write(
        "jira.apply",
        {
            "operation": operation["operation_id"],
            "status": result["status"],
            "receipt": str(receipt_path),
        },
    )
    out.emit(
        {
            "ok": True,
            "applied": True,
            "operation": operation["operation_id"],
            "result": result,
            "snapshot_saved": snapshot is not None,
            "verification": verification,
            "receipt_path": str(receipt_path),
        }
    )
    return 0
