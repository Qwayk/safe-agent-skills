from __future__ import annotations

import hashlib
import json
import mimetypes
import secrets
import stat
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import quote

from .auth import TokenStore
from .errors import SafetyError, ValidationError
from .http import HttpResponse
from .redaction import redact, redact_all_leaves
from .registry import CatalogRegistry
from .state import (
    create_private_json,
    read_json_object,
    sha256_json,
    write_private_bytes,
    write_private_json,
)
from .tenants import TenantStore

ALLOWED_INPUT_KEYS = {"body", "file_path", "headers", "media_type", "path", "query"}
PROTECTED_HEADER_NAMES = {
    "authorization",
    "content-length",
    "host",
    "xero-tenant-id",
    "xero-user-id",
}
SAFE_RATE_LIMIT_HEADERS = {
    "retry-after",
    "x-appminlimit-remaining",
    "x-daylimit-remaining",
    "x-minlimit-remaining",
    "x-rate-limit-problem",
}
MAX_REQUEST_BYTES = 10 * 1024 * 1024


class Transport(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        data: Any | None = None,
        files: dict[str, Any] | None = None,
        retries: int = 0,
        retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
    ) -> HttpResponse: ...


@dataclass(frozen=True)
class ExecutionOptions:
    apply: bool = False
    plan_out: Path | None = None
    plan_in: Path | None = None
    receipt_out: Path | None = None
    protected_output: Path | None = None
    approve: bool = False
    approve_high_risk: bool = False
    ack_no_snapshot: bool = False
    allow_deprecated_scope: bool = False
    idempotency_key: str | None = None


class XeroRuntime:
    def __init__(
        self,
        registry: CatalogRegistry,
        transport: Transport,
        token_store: TokenStore,
        tenant_store: TenantStore,
        *,
        auth_profile: str = "pkce",
    ):
        if auth_profile not in {"pkce", "custom", "app-store"}:
            raise ValidationError("Unknown Xero auth profile")
        self.registry = registry
        self.transport = transport
        self.token_store = token_store
        self.tenant_store = tenant_store
        self.auth_profile = auth_profile

    @staticmethod
    def _token_scopes(token: dict[str, Any]) -> set[str]:
        raw = token.get("scope") or []
        values = raw.split() if isinstance(raw, str) else list(raw)
        return {str(value) for value in values}

    @staticmethod
    def _scope_is_present(granted: set[str], required: str) -> bool:
        if required in granted:
            return True
        if required.endswith(".read") and required[: -len(".read")] in granted:
            return True
        return False

    def _validate_access(
        self,
        operation: dict[str, Any],
        token: dict[str, Any],
        tenant: dict[str, Any] | None,
        options: ExecutionOptions,
    ) -> None:
        required = operation.get("minimum_scopes") or []
        granted = self._token_scopes(token)
        missing = [scope for scope in required if not self._scope_is_present(granted, scope)]
        if missing:
            raise ValidationError(
                "The local Xero token is missing required scope(s): " + ", ".join(missing)
            )
        if str(operation.get("scope_status") or "").startswith("deprecated_") and not options.allow_deprecated_scope:
            raise SafetyError(
                "This command still depends on a deprecated broad Xero scope. "
                "Review the scheduled retirement and repeat with --allow-deprecated-scope."
            )
        if operation.get("tenant_required") and tenant is None:
            raise ValidationError("This Xero command requires an explicitly selected tenant")
        if self.auth_profile == "custom" and not operation.get("tenant_required"):
            raise ValidationError(
                "Custom Connections are only available for single-organisation tenanted commands"
            )
        if self.auth_profile == "custom" and tenant is not None:
            if str(tenant.get("region") or "").upper() not in {"AU", "NZ", "UK", "US"}:
                raise SafetyError(
                    "Custom Connections support only AU, NZ, UK, or US organisations"
                )
            selected_fingerprint = str(tenant.get("credential_fingerprint") or "")
            token_fingerprint = str(token.get("credential_fingerprint") or "")
            if not selected_fingerprint or not token_fingerprint or not secrets.compare_digest(
                selected_fingerprint, token_fingerprint
            ):
                raise SafetyError(
                    "The Custom Connection credential changed after target discovery. "
                    "Run tenant custom-discover again before any provider command."
                )
        if self.auth_profile == "app-store" and operation.get("auth_flow") != "client_credentials":
            raise ValidationError("The App Store auth profile is only available for App Store commands")
        region = str(operation.get("region") or "global")
        allowed_regions = [value.strip() for value in region.split(",") if value.strip()]
        excluded_regions = {
            str(value).strip().upper()
            for value in operation.get("excluded_regions") or []
            if str(value).strip()
        }
        if tenant is not None and str(tenant.get("region") or "").upper() in excluded_regions:
            raise SafetyError(
                f"{operation['command']} is unavailable in region {tenant.get('region')}"
            )
        if tenant is not None and allowed_regions and set(allowed_regions) <= {"AU", "NZ", "UK", "US"}:
            selected_region = str(tenant.get("region") or "").upper()
            if selected_region not in allowed_regions:
                expected = " or ".join(allowed_regions)
                raise SafetyError(
                    f"{operation['command']} requires region {expected}; selected tenant is {selected_region or 'unknown'}"
                )

    @staticmethod
    def _caller_target_header_allowed(operation: dict[str, Any], name: str) -> bool:
        return (
            operation.get("spec_id") == "identity"
            and operation.get("auth_flow") == "client_credentials"
            and name.lower() in {"xero-tenant-id", "xero-user-id"}
        )

    @staticmethod
    def _validate_parameter_value(parameter: dict[str, Any], value: Any) -> None:
        name = str(parameter.get("name") or "")
        expected = str(parameter.get("type") or "string")
        valid = True
        if expected == "array":
            valid = isinstance(value, list)
        elif expected == "integer":
            valid = isinstance(value, int) and not isinstance(value, bool)
        elif expected == "number":
            valid = isinstance(value, (int, float)) and not isinstance(value, bool)
        elif expected == "boolean":
            valid = isinstance(value, bool)
        elif expected == "object":
            valid = isinstance(value, dict)
        elif expected == "string":
            valid = isinstance(value, str)
        if not valid:
            raise ValidationError(f"Input parameter {name} must be {expected}")
        if str(parameter.get("format") or "").lower() == "uuid":
            canonical = None
            if isinstance(value, str):
                try:
                    canonical = str(uuid.UUID(value))
                except ValueError:
                    pass
            if canonical is None or canonical != str(value).lower():
                raise ValidationError(f"Input parameter {name} must be a canonical UUID")
        if expected == "array":
            item_contract = parameter.get("items") or {}
            for index, item in enumerate(value):
                XeroRuntime._validate_parameter_value(
                    {**item_contract, "name": f"{name}[{index}]"}, item
                )
        choices = parameter.get("enum")
        if choices and value not in choices:
            raise ValidationError(
                f"Input parameter {name} must be one of: "
                + ", ".join(str(choice) for choice in choices)
            )
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            minimum = parameter.get("minimum")
            maximum = parameter.get("maximum")
            if minimum is not None and value < minimum:
                raise ValidationError(f"Input parameter {name} must be at least {minimum}")
            if maximum is not None and value > maximum:
                raise ValidationError(f"Input parameter {name} must be at most {maximum}")

    @staticmethod
    def _validate_json_schema(schema: dict[str, Any], value: Any, *, label: str) -> None:
        choices = schema.get("enum")
        if choices is not None and value not in choices:
            raise ValidationError(
                f"{label} must be one of: " + ", ".join(str(choice) for choice in choices)
            )
        expected = str(schema.get("type") or "object")
        if expected == "object":
            if not isinstance(value, dict):
                raise ValidationError(f"{label} must be a JSON object")
            allowed = set((schema.get("properties") or {}).keys())
            unknown = (
                sorted(set(value) - allowed)
                if allowed and not schema.get("partial_object")
                else []
            )
            if unknown:
                raise ValidationError("Unknown body field(s): " + ", ".join(unknown))
            missing = sorted(set(schema.get("required") or []) - set(value))
            if missing:
                raise ValidationError("Missing required body field(s): " + ", ".join(missing))
            properties = schema.get("properties") or {}
            for name, item in value.items():
                property_schema = properties.get(name)
                if isinstance(property_schema, str):
                    property_schema = {"type": property_schema}
                if isinstance(property_schema, dict):
                    XeroRuntime._validate_json_schema(
                        property_schema,
                        item,
                        label=f"{label}.{name}",
                    )
            one_of = schema.get("oneOf") or []
            if one_of:
                matches = 0
                for branch in one_of:
                    try:
                        XeroRuntime._validate_json_schema(branch, value, label=label)
                    except ValidationError:
                        continue
                    matches += 1
                if matches != 1:
                    raise ValidationError(
                        f"{label} must match exactly one documented oneOf shape"
                    )
            return
        if expected == "array":
            if not isinstance(value, list):
                raise ValidationError(f"{label} must be a JSON array")
            item_schema = schema.get("items") or {}
            for index, item in enumerate(value):
                XeroRuntime._validate_json_schema(
                    item_schema,
                    item,
                    label=f"{label}[{index}]",
                )
            return
        type_checks = {
            "string": lambda item: isinstance(item, str),
            "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
            "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
            "boolean": lambda item: isinstance(item, bool),
        }
        check = type_checks.get(expected)
        if check is not None and not check(value):
            raise ValidationError(f"{label} must be {expected}")
        if expected == "string" and isinstance(value, str):
            if str(schema.get("format") or "").lower() == "uuid":
                canonical = None
                try:
                    canonical = str(uuid.UUID(value))
                except ValueError:
                    pass
                if canonical is None or canonical != value.lower():
                    raise ValidationError(f"{label} must be a canonical UUID")
            minimum_length = schema.get("minLength")
            maximum_length = schema.get("maxLength")
            if minimum_length is not None and len(value) < minimum_length:
                raise ValidationError(
                    f"{label} must contain at least {minimum_length} characters"
                )
            if maximum_length is not None and len(value) > maximum_length:
                raise ValidationError(
                    f"{label} must contain at most {maximum_length} characters"
                )

    @staticmethod
    def _validate_input(operation: dict[str, Any], input_data: dict[str, Any]) -> None:
        unknown = sorted(set(input_data) - ALLOWED_INPUT_KEYS)
        if unknown:
            raise ValidationError("Unknown input field(s): " + ", ".join(unknown))
        for section in ("path", "query", "headers"):
            value = input_data.get(section, {})
            if not isinstance(value, dict):
                raise ValidationError(f"Input '{section}' must be a JSON object")
        file_path = input_data.get("file_path")
        if file_path is not None and not isinstance(file_path, str):
            raise ValidationError("Input 'file_path' must be a string")
        media_type = input_data.get("media_type")
        if media_type is not None and not isinstance(media_type, str):
            raise ValidationError("Input 'media_type' must be a string")
        if file_path and input_data.get("body") is not None:
            raise ValidationError("Use either input.body or input.file_path, not both")
        parameters = operation.get("parameters") or []
        supplied = {
            "path": input_data.get("path") or {},
            "query": input_data.get("query") or {},
            "header": input_data.get("headers") or {},
        }
        by_location: dict[str, dict[str, dict[str, Any]]] = {
            "path": {},
            "query": {},
            "header": {},
        }
        for parameter in parameters:
            name = str(parameter.get("name") or "")
            location = str(parameter.get("in") or "")
            if name.lower() == "xero-tenant-id" and not XeroRuntime._caller_target_header_allowed(
                operation, name
            ):
                continue
            if location in by_location:
                by_location[location][name] = parameter
            if parameter.get("required"):
                supplied_names = supplied.get(location, {})
                present = (
                    any(str(value).lower() == name.lower() for value in supplied_names)
                    if location == "header"
                    else name in supplied_names
                )
                if not present:
                    raise ValidationError(f"Missing required {location} input: {name}")
        for location, values in supplied.items():
            documented = by_location[location]
            if location == "header":
                documented_lower = {name.lower(): parameter for name, parameter in documented.items()}
                for name, value in values.items():
                    parameter = documented_lower.get(str(name).lower())
                    protected = str(name).lower() in PROTECTED_HEADER_NAMES
                    if parameter is None or (
                        protected
                        and not XeroRuntime._caller_target_header_allowed(operation, str(name))
                    ):
                        raise ValidationError(f"Unknown or protected header input: {name}")
                    XeroRuntime._validate_parameter_value(parameter, value)
            else:
                unknown_parameters = sorted(set(values) - set(documented))
                if unknown_parameters:
                    raise ValidationError(
                        f"Unknown {location} input(s): " + ", ".join(unknown_parameters)
                    )
                for name, value in values.items():
                    XeroRuntime._validate_parameter_value(documented[name], value)
        request = operation.get("request")
        body = input_data.get("body")
        if request and request.get("required") and body is None and not file_path:
            raise ValidationError("This fixed command requires input.body or input.file_path")
        if not request and body is not None:
            raise ValidationError("This fixed command does not accept input.body")
        if not request and file_path:
            raise ValidationError("This fixed command does not accept input.file_path")
        if request:
            content = request.get("content") or {}
            chosen_media = str(media_type or ("application/json" if body is not None else ""))
            if chosen_media and chosen_media not in content:
                raise ValidationError(
                    f"Media type {chosen_media} is not part of this fixed command contract"
                )
            if body is not None:
                schema = content.get("application/json")
                if not isinstance(schema, dict):
                    raise ValidationError("This fixed command accepts a file, not input.body")
                XeroRuntime._validate_json_schema(schema, body, label="input.body")
                try:
                    encoded_body = json.dumps(
                        body, ensure_ascii=True, allow_nan=False
                    ).encode("utf-8")
                except (TypeError, ValueError):
                    raise ValidationError(
                        "Xero request body must contain only finite JSON values"
                    ) from None
                if len(encoded_body) > MAX_REQUEST_BYTES:
                    raise ValidationError("Xero request body exceeds the 10 MB global limit")
            if file_path and not any(
                str(name).startswith("multipart/") or name == "application/octet-stream"
                for name in content
            ):
                raise ValidationError("This fixed command accepts JSON input, not input.file_path")
        required_one_of_headers = operation.get("required_one_of_headers") or []
        if required_one_of_headers:
            supplied_headers = {str(name).lower() for name in (input_data.get("headers") or {})}
            if not any(str(name).lower() in supplied_headers for name in required_one_of_headers):
                raise ValidationError(
                    "This command requires one of these documented headers: "
                    + ", ".join(str(name) for name in required_one_of_headers)
                )

    @staticmethod
    def _target(operation: dict[str, Any], input_data: dict[str, Any]) -> str:
        path = str(operation["path"])
        path_values = input_data.get("path") or {}
        for name, value in path_values.items():
            path = path.replace("{" + str(name) + "}", quote(str(value), safe=""))
        if "{" in path or "}" in path:
            raise ValidationError("Not all path placeholders were supplied")
        return str(operation["server"]).rstrip("/") + "/" + path.lstrip("/")

    @staticmethod
    def _safe_headers(response: HttpResponse) -> dict[str, str]:
        return {
            key: value
            for key, value in response.headers.items()
            if key.lower() in SAFE_RATE_LIMIT_HEADERS or key.lower().startswith("x-rate-limit")
        }

    @staticmethod
    def _query_params(operation: dict[str, Any], input_data: dict[str, Any]) -> dict[str, Any] | None:
        supplied = input_data.get("query") or {}
        if not supplied:
            return None
        contracts = {
            str(item.get("name")): item
            for item in operation.get("parameters") or []
            if item.get("in") == "query"
        }
        output: dict[str, Any] = {}
        for name, value in supplied.items():
            contract = contracts.get(str(name)) or {}
            if isinstance(value, list) and not bool(contract.get("explode", True)):
                output[str(name)] = ",".join(str(item) for item in value)
            else:
                output[str(name)] = value
        return output

    @staticmethod
    def _decode_response(response: HttpResponse) -> Any:
        content_type = response.headers.get("content-type", "")
        if "json" in content_type.lower() or response.body[:1] in {b"{", b"["}:
            try:
                return json.loads(response.body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                return {"unparsed_response": True, "size": len(response.body)}
        return {"binary": True, "size": len(response.body), "sha256": hashlib.sha256(response.body).hexdigest()}

    @staticmethod
    def _file_payload(
        operation: dict[str, Any], input_data: dict[str, Any]
    ) -> tuple[Path, bytes, str, str, dict[str, Any]]:
        source = Path(str(input_data["file_path"])).expanduser().resolve()
        if not source.is_file():
            raise ValidationError(f"Input file not found: {source}")
        content = source.read_bytes()
        if len(content) > MAX_REQUEST_BYTES:
            raise ValidationError("Xero upload exceeds the 10 MB global request limit")
        documented = list((operation.get("request") or {}).get("content") or {})
        requested_media_type = str(input_data.get("media_type") or "")
        if requested_media_type:
            request_media_type = requested_media_type
        else:
            multipart = next(
                (value for value in documented if str(value).startswith("multipart/")),
                None,
            )
            request_media_type = str(
                multipart
                or ("application/octet-stream" if "application/octet-stream" in documented else "")
            )
        if not request_media_type:
            raise ValidationError("The fixed file command has no supported request media type")
        file_media_type = mimetypes.guess_type(source.name)[0] or "application/octet-stream"
        metadata = {
            "name": source.name,
            "size": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            "request_media_type": request_media_type,
            "file_media_type": file_media_type,
        }
        return source, content, request_media_type, file_media_type, metadata

    @staticmethod
    def _validation_errors(value: Any) -> list[Any]:
        found: list[Any] = []
        if isinstance(value, dict):
            normalized_items = {
                str(key).lower().replace("_", ""): item for key, item in value.items()
            }
            if str(normalized_items.get("status") or "").upper() == "REJECTED":
                found.append({"status": "REJECTED"})
            if normalized_items.get("haserrors") is True:
                found.append({"HasErrors": True})
            if normalized_items.get("hasvalidationerrors") is True:
                found.append({"HasValidationErrors": True})
            if str(normalized_items.get("statusattributestring") or "").upper() == "ERROR":
                found.append({"StatusAttributeString": "ERROR"})
            for key, item in value.items():
                normalized = str(key).lower().replace("_", "")
                if normalized in {
                    "validationerrors",
                    "validationerror",
                    "error",
                    "errors",
                } and item:
                    found.append(item)
                found.extend(XeroRuntime._validation_errors(item))
        elif isinstance(value, list):
            for item in value:
                found.extend(XeroRuntime._validation_errors(item))
        return found

    def _request(
        self,
        operation: dict[str, Any],
        input_data: dict[str, Any],
        token: dict[str, Any],
        tenant: dict[str, Any] | None,
        *,
        idempotency_key: str | None,
        expected_file_metadata: dict[str, Any] | None = None,
    ) -> HttpResponse:
        url = self._target(operation, input_data)
        headers: dict[str, str] = {
            "Authorization": "Bearer " + str(token["access_token"]),
            "Accept": str(operation.get("preferred_accept") or "application/json"),
        }
        if operation.get("tenant_required") and self.auth_profile != "custom":
            assert tenant is not None
            headers["xero-tenant-id"] = str(tenant["tenant_id"])
        allowed_headers = {
            str(parameter["name"]).lower()
            for parameter in operation.get("parameters") or []
            if parameter.get("in") == "header"
        }
        for name, value in (input_data.get("headers") or {}).items():
            if str(name).lower() in PROTECTED_HEADER_NAMES and not self._caller_target_header_allowed(
                operation, str(name)
            ):
                raise SafetyError(f"Input cannot override protected header: {name}")
            if str(name).lower() not in allowed_headers:
                raise ValidationError(f"Header is not part of this fixed command contract: {name}")
            headers[str(name)] = str(value)
        if idempotency_key:
            if not operation.get("idempotency_supported"):
                raise ValidationError("This Xero operation does not document Idempotency-Key support")
            headers["Idempotency-Key"] = idempotency_key

        query = self._query_params(operation, input_data)
        json_body = input_data.get("body")
        data: Any | None = None
        files: dict[str, Any] | None = None
        file_path = input_data.get("file_path")
        if file_path:
            source, content, request_media_type, file_media_type, metadata = self._file_payload(
                operation, input_data
            )
            if expected_file_metadata is not None and metadata != expected_file_metadata:
                raise SafetyError("The planned file changed after planning; create and review a new plan")
            if request_media_type.startswith("multipart/"):
                if operation.get("spec_id") == "files" and operation.get("operation_id") in {
                    "uploadFile",
                    "uploadFileToFolder",
                }:
                    files = {
                        "body": (source.name, content, file_media_type),
                        "name": (None, source.name),
                        "filename": (None, source.name),
                        "mimeType": (None, file_media_type),
                    }
                else:
                    files = {"file": (source.name, content, file_media_type)}
            else:
                data = content
                headers["Content-Type"] = request_media_type
        elif json_body is not None:
            headers["Content-Type"] = str(input_data.get("media_type") or "application/json")

        return self.transport.request(
            str(operation["method"]),
            url,
            headers=headers,
            params=query,
            json_body=json_body,
            data=data,
            files=files,
            retries=2 if operation["method"] == "GET" else 0,
        )

    def _tenant_for(self, operation: dict[str, Any]) -> dict[str, Any] | None:
        return self.tenant_store.read() if operation.get("tenant_required") else None

    @staticmethod
    def _validate_tenant_bound_target(
        operation: dict[str, Any],
        input_data: dict[str, Any],
        tenant: dict[str, Any] | None,
    ) -> None:
        parameters = operation.get("tenant_bound_path_parameters") or []
        if not parameters:
            return
        if tenant is None:
            raise SafetyError("The fixed command has no selected tenant for its tenant-bound path")
        supplied = input_data.get("path") or {}
        selected_tenant_id = str(tenant.get("tenant_id") or "")
        for name in parameters:
            if str(supplied.get(name) or "") != selected_tenant_id:
                raise SafetyError(
                    f"Path input {name} must exactly match the selected tenant ID"
                )

    @staticmethod
    def _plan_integrity(plan: dict[str, Any]) -> str:
        return sha256_json({key: value for key, value in plan.items() if key != "integrity"})

    def _state_root(self) -> Path:
        token_parent = self.token_store.path.parent
        return token_parent.parent if token_parent.name == "oauth" else token_parent

    def _validate_saved_snapshot(self, snapshot: dict[str, Any]) -> None:
        raw_path = snapshot.get("protected_path")
        if not isinstance(raw_path, str) or not raw_path:
            raise SafetyError("The saved snapshot path is missing; create and review a new plan")
        snapshot_path = Path(raw_path).expanduser().resolve()
        snapshot_root = (self._state_root() / "snapshots").resolve()
        if not snapshot_path.is_relative_to(snapshot_root) or not snapshot_path.is_file():
            raise SafetyError("The saved snapshot is missing or outside protected state")
        if stat.S_IMODE(snapshot_path.stat().st_mode) != 0o600:
            raise SafetyError("The saved snapshot permissions changed; create and review a new plan")
        body = snapshot_path.read_bytes()
        if len(body) != snapshot.get("size") or hashlib.sha256(body).hexdigest() != snapshot.get(
            "sha256"
        ):
            raise SafetyError("The saved snapshot changed after planning; create and review a new plan")

    def _snapshot(
        self,
        operation: dict[str, Any],
        input_data: dict[str, Any],
        token: dict[str, Any],
        tenant: dict[str, Any] | None,
        options: ExecutionOptions,
        *,
        expected_not_found: bool = False,
    ) -> dict[str, Any] | None:
        command = operation.get("verification_command")
        if not command:
            return None
        read_operation = self.registry.get(str(command))
        if read_operation is None:
            return None
        read_input = {"path": dict(input_data.get("path") or {})}
        required_read_headers = {
            str(item.get("name"))
            for item in read_operation.get("parameters") or []
            if item.get("in") == "header" and item.get("required")
        }
        content_type_header = next(
            (name for name in required_read_headers if name.lower() == "contenttype"),
            None,
        )
        if content_type_header and input_data.get("file_path"):
            _, _, _, file_media_type, _ = self._file_payload(operation, input_data)
            read_input["headers"] = {content_type_header: file_media_type}
        try:
            self._validate_input(read_operation, read_input)
            self._validate_access(read_operation, token, tenant, options)
            self._validate_tenant_bound_target(read_operation, read_input, tenant)
        except (SafetyError, ValidationError):
            return None
        response = self._request(
            read_operation,
            read_input,
            token,
            tenant,
            idempotency_key=None,
        )
        if expected_not_found and response.status == 404:
            return {
                "command": command,
                "status": 404,
                "outcome": "verified_absent",
                "captured_at": int(time.time()),
            }
        if expected_not_found and response.status >= 400:
            return {
                "command": command,
                "status": response.status,
                "outcome": "absence_unverified",
                "captured_at": int(time.time()),
            }
        if response.status >= 400:
            return None
        digest = hashlib.sha256(response.body).hexdigest()
        snapshot_path = (
            self._state_root()
            / "snapshots"
            / f"{str(command).replace('.', '-')}-{digest[:16]}.bin"
        )
        write_private_bytes(snapshot_path, response.body)
        snapshot = {
            "command": command,
            "status": response.status,
            "protected_path": str(snapshot_path.resolve()),
            "size": len(response.body),
            "sha256": digest,
            "captured_at": int(time.time()),
        }
        if expected_not_found:
            snapshot["outcome"] = "still_present"
        return snapshot

    def _plan_path(self, options: ExecutionOptions, plan_id: str) -> Path:
        if options.plan_out:
            return options.plan_out
        return self._state_root() / "plans" / f"{plan_id}.json"

    def _receipt_path(self, options: ExecutionOptions, plan_id: str) -> Path:
        if options.receipt_out:
            return options.receipt_out
        return self._state_root() / "receipts" / f"{plan_id}.json"

    def _execution_marker_path(self, plan_id: str) -> Path:
        return self._state_root() / "executions" / f"{plan_id}.json"

    def _reserve_execution(
        self,
        plan: dict[str, Any],
        operation: dict[str, Any],
        tenant: dict[str, Any] | None,
        options: ExecutionOptions,
    ) -> tuple[Path, Path, dict[str, Any]]:
        plan_id = str(plan["plan_id"])
        marker_path = self._execution_marker_path(plan_id)
        if marker_path.exists():
            raise SafetyError(
                "This reviewed plan already has an execution record. Create and review a new plan."
            )
        receipt_path = self._receipt_path(options, plan_id)
        pending = {
            "schema_version": 1,
            "status": "pending_provider_attempt",
            "plan_id": plan_id,
            "plan_integrity": plan["integrity"],
            "command": operation["command"],
            "tenant": tenant,
            "target": plan["target"],
            "receipt_path": str(receipt_path.resolve()),
            "reserved_at": int(time.time()),
            "status_limit": (
                "This pending receipt proves only that the provider attempt was reserved. "
                "Do not repeat the plan without reviewing the final receipt state."
            ),
        }
        try:
            create_private_json(receipt_path, pending)
        except FileExistsError:
            raise SafetyError(
                "Receipt path already exists. Choose a new path before any provider attempt."
            ) from None
        except OSError as exc:
            raise SafetyError(
                f"Receipt path cannot be reserved safely: {type(exc).__name__}"
            ) from None
        marker = {
            "schema_version": 1,
            "status": "reserved",
            "plan_id": plan_id,
            "plan_integrity": plan["integrity"],
            "receipt_path": str(receipt_path.resolve()),
            "reserved_at": pending["reserved_at"],
        }
        try:
            create_private_json(marker_path, marker)
        except FileExistsError:
            pending["status"] = "blocked_duplicate_execution"
            write_private_json(receipt_path, pending)
            raise SafetyError(
                "This reviewed plan already has an execution record. Create and review a new plan."
            ) from None
        except OSError as exc:
            pending["status"] = "blocked_execution_reservation"
            write_private_json(receipt_path, pending)
            raise SafetyError(
                f"Plan execution cannot be reserved safely: {type(exc).__name__}"
            ) from None
        return receipt_path, marker_path, pending

    @staticmethod
    def _finalize_execution_marker(
        marker_path: Path, pending: dict[str, Any], status: str
    ) -> None:
        write_private_json(
            marker_path,
            {
                "schema_version": 1,
                "status": status,
                "plan_id": pending["plan_id"],
                "plan_integrity": pending["plan_integrity"],
                "receipt_path": str(Path(pending["receipt_path"]).resolve())
                if pending.get("receipt_path")
                else None,
                "updated_at": int(time.time()),
            },
        )

    def _create_plan(
        self,
        operation: dict[str, Any],
        input_data: dict[str, Any],
        token: dict[str, Any],
        tenant: dict[str, Any] | None,
        options: ExecutionOptions,
    ) -> dict[str, Any]:
        snapshot = self._snapshot(operation, input_data, token, tenant, options)
        no_snapshot = snapshot is None
        idempotency_key = options.idempotency_key
        if operation.get("idempotency_supported") and not idempotency_key:
            idempotency_key = str(uuid.uuid4())
        plan_nonce = str(uuid.uuid4())
        input_hash = sha256_json(input_data)
        plan_id = sha256_json(
            {
                "catalog": self.registry.inventory_hash,
                "auth_profile": self.auth_profile,
                "command": operation["command"],
                "tenant": tenant,
                "input_hash": input_hash,
                "snapshot": snapshot,
                "idempotency_key": idempotency_key,
                "plan_nonce": plan_nonce,
            }
        )[:24]
        file_metadata = None
        if input_data.get("file_path"):
            _, _, _, _, file_metadata = self._file_payload(operation, input_data)
        plan: dict[str, Any] = {
            "schema_version": 1,
            "plan_id": plan_id,
            "created_at": int(time.time()),
            "catalog_hash": self.registry.inventory_hash,
            "auth_profile": self.auth_profile,
            "command": operation["command"],
            "method": operation["method"],
            "target": self._target(operation, input_data),
            "tenant": tenant,
            "input": input_data,
            "input_hash": input_hash,
            "file_metadata": file_metadata,
            "minimum_scopes": operation.get("minimum_scopes") or [],
            "risk_flags": operation.get("risk_flags") or [],
            "extra_approval": bool(operation.get("extra_approval")),
            "snapshot": snapshot,
            "no_snapshot": no_snapshot,
            "no_snapshot_warning": (
                "Xero provides no reliable before-state for this exact action. Apply can proceed only with explicit no-snapshot acknowledgement."
                if no_snapshot
                else None
            ),
            "idempotency_key": idempotency_key,
            "plan_nonce": plan_nonce,
            "verification_strategy": operation.get("verification_strategy"),
            "verification_command": operation.get("verification_command"),
        }
        plan["integrity"] = self._plan_integrity(plan)
        plan_path = self._plan_path(options, plan_id)
        write_private_json(plan_path, plan)
        return {
            "ok": True,
            "dry_run": True,
            "command": operation["command"],
            "plan_id": plan_id,
            "plan_path": str(plan_path.resolve()),
            "tenant": tenant,
            "target": plan["target"],
            "risk_flags": plan["risk_flags"],
            "extra_approval_required": plan["extra_approval"],
            "no_snapshot": no_snapshot,
            "no_snapshot_warning": plan["no_snapshot_warning"],
            "verification_strategy": plan["verification_strategy"],
        }

    def _load_plan(
        self,
        operation: dict[str, Any],
        tenant: dict[str, Any] | None,
        options: ExecutionOptions,
        supplied_input: dict[str, Any],
    ) -> dict[str, Any]:
        if options.plan_in is None:
            raise SafetyError("Write apply requires --plan-in with the reviewed saved plan")
        try:
            plan = read_json_object(options.plan_in)
        except Exception as exc:  # noqa: BLE001
            raise SafetyError(f"Saved plan is invalid: {type(exc).__name__}") from None
        if plan.get("integrity") != self._plan_integrity(plan):
            raise SafetyError("Saved plan integrity check failed")
        if plan.get("catalog_hash") != self.registry.inventory_hash:
            raise SafetyError("Saved plan was created from a different Xero command catalog")
        if plan.get("auth_profile") != self.auth_profile:
            raise SafetyError("Saved plan was created with a different Xero auth profile")
        if plan.get("command") != operation["command"]:
            raise SafetyError("Saved plan command does not match the requested fixed command")
        if plan.get("tenant") != tenant:
            raise SafetyError("Selected Xero tenant changed after the plan was created")
        if supplied_input and sha256_json(supplied_input) != plan.get("input_hash"):
            raise SafetyError("Apply input changed after the plan was created")
        if not options.approve:
            raise SafetyError("Write apply requires --approve after reviewing the saved plan")
        if plan.get("extra_approval") and not options.approve_high_risk:
            raise SafetyError("This high-risk Xero change requires --approve-high-risk")
        if plan.get("no_snapshot") and not options.ack_no_snapshot:
            raise SafetyError("This plan has no safe before-state and requires --ack-no-snapshot")
        return plan

    def _apply(
        self,
        operation: dict[str, Any],
        supplied_input: dict[str, Any],
        token: dict[str, Any],
        tenant: dict[str, Any] | None,
        options: ExecutionOptions,
    ) -> dict[str, Any]:
        plan = self._load_plan(operation, tenant, options, supplied_input)
        input_data = plan["input"]
        self._validate_tenant_bound_target(operation, input_data, tenant)
        previous_snapshot = plan.get("snapshot")
        if previous_snapshot:
            self._validate_saved_snapshot(previous_snapshot)
        expected_file_metadata = plan.get("file_metadata")
        if expected_file_metadata is not None:
            _, _, _, _, current_file_metadata = self._file_payload(operation, input_data)
            if current_file_metadata != expected_file_metadata:
                raise SafetyError("The planned file changed after planning; create and review a new plan")
        receipt_path, marker_path, pending = self._reserve_execution(
            plan, operation, tenant, options
        )
        if previous_snapshot:
            try:
                current_snapshot = self._snapshot(operation, input_data, token, tenant, options)
            except RuntimeError as exc:
                pending.update(
                    {
                        "status": "blocked_prewrite_check_failed",
                        "error_type": type(exc).__name__,
                        "updated_at": int(time.time()),
                    }
                )
                write_private_json(receipt_path, pending)
                self._finalize_execution_marker(marker_path, pending, "blocked_before_write")
                raise SafetyError(
                    "The pre-write target check failed. No write was attempted; create and review a new plan."
                ) from None
            if current_snapshot is None or current_snapshot.get("sha256") != previous_snapshot.get("sha256"):
                pending.update(
                    {
                        "status": "blocked_target_changed",
                        "updated_at": int(time.time()),
                    }
                )
                write_private_json(receipt_path, pending)
                self._finalize_execution_marker(marker_path, pending, "blocked_before_write")
                raise SafetyError("Xero target changed after planning; create and review a new plan")

        try:
            response = self._request(
                operation,
                input_data,
                token,
                tenant,
                idempotency_key=plan.get("idempotency_key"),
                expected_file_metadata=expected_file_metadata,
            )
        except (SafetyError, ValidationError) as exc:
            pending.update(
                {
                    "status": "blocked_before_provider_attempt",
                    "error_type": type(exc).__name__,
                    "updated_at": int(time.time()),
                }
            )
            write_private_json(receipt_path, pending)
            self._finalize_execution_marker(marker_path, pending, "blocked_before_write")
            raise
        except RuntimeError as exc:
            pending.update(
                {
                    "status": "provider_attempt_outcome_uncertain",
                    "error_type": type(exc).__name__,
                    "attempted_at": int(time.time()),
                    "status_limit": (
                        "A provider request was attempted but no response was received. "
                        "Do not repeat this plan; verify Xero state first."
                    ),
                }
            )
            write_private_json(receipt_path, pending)
            self._finalize_execution_marker(marker_path, pending, "uncertain")
            raise RuntimeError(
                f"Xero request outcome is uncertain. Review the protected receipt at {receipt_path.resolve()}."
            ) from None
        decoded = self._decode_response(response)
        validation_errors = self._validation_errors(decoded)
        if response.status >= 400:
            provider_outcome = "rejected"
            ok = False
        elif validation_errors:
            provider_outcome = "validation_failed_or_partial"
            ok = False
        else:
            provider_outcome = "accepted_not_stronger_state"
            ok = True

        verification = None
        if ok and operation.get("verification_command"):
            try:
                verification = self._snapshot(
                    operation,
                    input_data,
                    token,
                    tenant,
                    options,
                    expected_not_found=operation["method"] == "DELETE",
                )
            except RuntimeError as exc:
                verification = {
                    "outcome": "verification_unavailable",
                    "error_type": type(exc).__name__,
                }
        if (
            operation["method"] == "DELETE"
            and operation.get("verification_command")
            and (not verification or verification.get("outcome") != "verified_absent")
        ):
            ok = False
            provider_outcome = "verification_failed_or_partial"
        receipt = {
            "schema_version": 1,
            "status": "completed",
            "plan_id": plan["plan_id"],
            "plan_integrity": plan["integrity"],
            "command": operation["command"],
            "tenant": tenant,
            "target": plan["target"],
            "applied_at": int(time.time()),
            "provider_status": response.status,
            "provider_outcome": provider_outcome,
            "provider_response": (
                redact_all_leaves(decoded)
                if operation.get("sensitive_output")
                else redact(decoded, sensitive=False)
            ),
            "validation_errors": (
                redact_all_leaves(validation_errors)
                if operation.get("sensitive_output")
                else redact(validation_errors, sensitive=False)
            ),
            "rate_limit_headers": self._safe_headers(response),
            "verification": verification,
            "status_limit": "Accepted does not mean posted, paid, sent, completed, reconciled, or compliant.",
        }
        try:
            write_private_json(receipt_path, receipt)
        except OSError as exc:
            self._finalize_execution_marker(marker_path, pending, "receipt_finalize_failed")
            raise RuntimeError(
                "The provider attempt completed, but the reserved receipt could not be finalized: "
                + type(exc).__name__
            ) from None
        self._finalize_execution_marker(marker_path, pending, "completed")
        return {
            "ok": ok,
            "dry_run": False,
            "command": operation["command"],
            "tenant": tenant,
            "target": plan["target"],
            "provider_status": response.status,
            "provider_outcome": provider_outcome,
            "verification": verification,
            "receipt_path": str(receipt_path.resolve()),
            "status_limit": receipt["status_limit"],
        }

    def _read(
        self,
        operation: dict[str, Any],
        input_data: dict[str, Any],
        token: dict[str, Any],
        tenant: dict[str, Any] | None,
        options: ExecutionOptions,
    ) -> dict[str, Any]:
        response = self._request(operation, input_data, token, tenant, idempotency_key=None)
        decoded = self._decode_response(response)
        ok = response.status < 400
        result: dict[str, Any] = {
            "ok": ok,
            "command": operation["command"],
            "tenant": tenant,
            "target": self._target(operation, input_data),
            "provider_status": response.status,
            "rate_limit_headers": self._safe_headers(response),
        }
        if options.protected_output:
            write_private_bytes(options.protected_output, response.body)
            result.update(
                {
                    "protected_output": str(options.protected_output.expanduser()),
                    "protected_output_size": len(response.body),
                    "protected_output_sha256": hashlib.sha256(response.body).hexdigest(),
                }
            )
        else:
            result["data"] = (
                redact_all_leaves(decoded)
                if operation.get("sensitive_output")
                else redact(decoded, sensitive=False)
            )
        return result

    def execute(
        self, command: str, input_data: dict[str, Any], options: ExecutionOptions
    ) -> dict[str, Any]:
        operation = self.registry.get(command)
        if operation is None:
            raise ValidationError(f"Unknown fixed Xero command: {command}")
        if not isinstance(input_data, dict):
            raise ValidationError("Command input must be a JSON object")
        if options.idempotency_key and not operation.get("idempotency_supported"):
            raise ValidationError(
                "This fixed command does not document Idempotency-Key support"
            )
        if not options.apply or input_data:
            self._validate_input(operation, input_data)
        token = self.token_store.read()
        tenant = self._tenant_for(operation)
        self._validate_access(operation, token, tenant, options)
        if not options.apply or input_data:
            self._validate_tenant_bound_target(operation, input_data, tenant)
        if operation["method"] == "GET":
            if options.apply or options.plan_in or options.plan_out:
                raise ValidationError("Read commands do not use write plan or apply flags")
            return self._read(operation, input_data, token, tenant, options)
        if options.apply:
            return self._apply(operation, input_data, token, tenant, options)
        return self._create_plan(operation, input_data, token, tenant, options)
