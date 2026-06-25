from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

from .config import Config
from .google_auth import load_adc_credentials
from .generated_registry import DiscoveryRegistry, load_inventory, load_registry
from .errors import SafetyError, ValidationError
from .http import HttpClient
from .json_files import read_json_file, write_json_file
from .redaction import (
    iter_scalar_strings,
    redact_jsonish,
    redact_jsonish_with_values,
    redact_text,
    sanitize_error_message,
)

_READ_METHODS = {"GET", "HEAD"}
_REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ResolvedInput:
    path_values: dict[str, Any]
    query_params: dict[str, Any]
    body: Any
    fingerprint_input: dict[str, Any]


def _utc_now() -> str:
    import time

    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_json(obj: Any) -> str:
    return hashlib.sha256(_canonical_json(obj).encode("utf-8")).hexdigest()


def _inventory_path() -> Path:
    return _REPO_ROOT / "docs" / "_generated" / "gcp_discovery_inventory.json"


def inventory_summary() -> dict[str, Any]:
    data = load_inventory(_REPO_ROOT)
    return {
        "ok": True,
        "generated_at": data.get("generated_at"),
        "boundary": data.get("boundary"),
        "summary": data.get("summary", {}),
        "services": {
            "count": len(data.get("services", [])),
            "api_ids": [str(service.get("api_id") or "") for service in data.get("services", []) if service.get("api_id")],
        },
    }


def _service_map(registry: DiscoveryRegistry) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for service in registry.data.get("services", []):
        api_id = str(service.get("api_id") or "").strip()
        if api_id:
            out[api_id] = service
    return out


def _operation_map(service: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for operation in service.get("operations", []):
        op_name = str(operation.get("operation_name") or "").strip()
        if op_name:
            out[op_name] = operation
    return out


def _extract_path_names(path_template: str) -> list[tuple[str, bool]]:
    names: list[tuple[str, bool]] = []
    for match in re.finditer(r"{(\+)?([^}]+)}", path_template):
        names.append((match.group(2), bool(match.group(1))))
    return names


def _coerce_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    return {}


def _normalize_input(input_obj: dict[str, Any], *, path_template: str, http_method: str) -> ResolvedInput:
    top_level = {k: v for k, v in input_obj.items() if k not in {"path", "query", "body", "headers"}}
    path_section = _coerce_mapping(input_obj.get("path"))
    query_section = _coerce_mapping(input_obj.get("query"))
    body = input_obj.get("body") if "body" in input_obj else None

    path_values: dict[str, Any] = {}
    path_names = _extract_path_names(path_template)
    for name, _ in path_names:
        if name in path_section:
            path_values[name] = path_section[name]
        elif name in top_level:
            path_values[name] = top_level[name]

    missing = [name for name, _ in path_names if str(path_values.get(name) or "").strip() == ""]
    if missing:
        raise ValidationError("Missing required path parameters: " + ", ".join(sorted(set(missing))))

    query_params = dict(query_section)
    body_payload = body
    top_level_remaining = {
        key: value
        for key, value in top_level.items()
        if key not in path_values and key not in query_params
    }
    if http_method in _READ_METHODS:
        for key, value in top_level_remaining.items():
            query_params.setdefault(key, value)
    elif body_payload is None and top_level_remaining:
        body_payload = top_level_remaining
    elif body_payload is None and query_section:
        query_params.update(top_level_remaining)

    fingerprint_input = {
        "body": body_payload,
        "path": path_values,
        "query": query_params,
    }
    return ResolvedInput(
        path_values=path_values,
        query_params=query_params,
        body=body_payload,
        fingerprint_input=fingerprint_input,
    )


def _build_url(*, base_url: str, path_template: str, path_values: dict[str, Any]) -> str:
    path = path_template
    for name, allow_slash in _extract_path_names(path_template):
        raw_value = str(path_values.get(name) or "")
        encoded = quote(raw_value, safe="/" if allow_slash else "")
        path = path.replace(f"{{+{name}}}", encoded)
        path = path.replace(f"{{{name}}}", encoded)
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def _base_url_from_discovery_doc(discovery_doc: dict[str, Any]) -> str:
    base_url = str(discovery_doc.get("baseUrl") or "").strip()
    if base_url:
        return base_url.rstrip("/")
    root_url = str(discovery_doc.get("rootUrl") or "").strip()
    service_path = str(discovery_doc.get("servicePath") or "").strip("/")
    if root_url and service_path:
        return f"{root_url.rstrip('/')}/{service_path}"
    raise RuntimeError("Discovery document missing baseUrl or rootUrl/servicePath")


def load_discovery_document(service: dict[str, Any], *, timeout_s: float) -> dict[str, Any]:
    import requests

    url = str(service.get("discovery_rest_url") or "").strip()
    base_url = str(service.get("base_url") or "").strip()
    if not url:
        if base_url:
            return {"baseUrl": base_url}
        raise RuntimeError("Service is missing discovery_rest_url")
    resp = requests.get(url, timeout=timeout_s, headers={"Accept": "application/json"})
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, dict):
        raise RuntimeError("Discovery document must be a JSON object")
    return data


def _redaction_values(cfg: Config | None, input_obj: dict[str, Any] | None, plan_obj: dict[str, Any] | None = None) -> list[str]:
    values: list[str] = []
    if cfg is not None:
        values.extend(list(cfg.redaction_values()))
    if input_obj:
        values.extend(iter_scalar_strings(input_obj))
    if plan_obj:
        values.extend(iter_scalar_strings(plan_obj))
    return [value for value in values if isinstance(value, str) and value.strip()]


def _request_headers(*, token: str, quota_project: str | None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    if quota_project:
        headers["x-goog-user-project"] = quota_project
    return headers


def _load_input_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    data = read_json_file(path)
    if not isinstance(data, dict):
        raise ValidationError("Input JSON must be a JSON object")
    return data


def _service_operation(registry: DiscoveryRegistry, service_id: str, operation_name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    service = registry.get_service(service_id)
    if not service:
        raise ValidationError(f"Unknown service: {service_id}")
    operation = registry.get_operation(service_id, operation_name)
    if not operation:
        raise ValidationError(f"Unknown operation for {service_id}: {operation_name}")
    return service, operation


def _zone_to_region(value: str) -> str:
    value = str(value).strip()
    if re.search(r"-[a-z]$", value):
        return value.rsplit("-", 1)[0]
    return value


def _location_candidates_from_resource_name(value: str) -> list[tuple[str, str]]:
    parts = [part for part in str(value).split("/") if part]
    candidates: list[tuple[str, str]] = []
    for index, part in enumerate(parts[:-1]):
        lowered = part.lower()
        next_value = parts[index + 1]
        if lowered == "locations":
            candidates.append(("location", _zone_to_region(next_value)))
        elif lowered == "zones":
            candidates.append(("zone", _zone_to_region(next_value)))
        elif lowered == "regions":
            candidates.append(("region", next_value))
    return candidates


def _region_candidates(path_values: dict[str, Any]) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    for path_key, raw_value in path_values.items():
        key = str(path_key).lower()
        value = str(raw_value or "").strip()
        if not value:
            continue
        candidates.extend((f"{path_key}:{kind}", candidate) for kind, candidate in _location_candidates_from_resource_name(value))
        if "zone" in key:
            candidates.append((str(path_key), _zone_to_region(value)))
        elif key in {"region", "regionid", "regionsid"} or "region" in key:
            candidates.append((str(path_key), value))
        elif key in {"location", "locations", "locationid", "locationsid"} or "location" in key:
            candidates.append((str(path_key), _zone_to_region(value)))
    deduped: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for label, candidate in candidates:
        item = (label, candidate)
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def _validate_allowlists(cfg: Config | None, path_values: dict[str, Any]) -> None:
    if cfg is None:
        return
    checks: list[tuple[str, tuple[str, ...], str]] = [
        ("project", cfg.allowed_projects, "GCP_ALLOWED_PROJECTS"),
        ("folder", cfg.allowed_folders, "GCP_ALLOWED_FOLDERS"),
        ("organization", cfg.allowed_organizations, "GCP_ALLOWED_ORGANIZATIONS"),
        ("org", cfg.allowed_organizations, "GCP_ALLOWED_ORGANIZATIONS"),
        ("billingaccount", cfg.allowed_billing_accounts, "GCP_ALLOWED_BILLING_ACCOUNTS"),
        ("billing_account", cfg.allowed_billing_accounts, "GCP_ALLOWED_BILLING_ACCOUNTS"),
    ]
    for key, allowed, label in checks:
        if not allowed:
            continue
        for path_key, raw_value in path_values.items():
            lowered = str(path_key).lower()
            if key not in lowered:
                continue
            if str(raw_value) not in allowed:
                raise SafetyError(f"Refused: {path_key}={raw_value} is not in {label}")
    if cfg.allowed_regions:
        for source, candidate in _region_candidates(path_values):
            if candidate not in cfg.allowed_regions:
                raise SafetyError(f"Refused: {source} resolves to {candidate}, which is not in GCP_ALLOWED_REGIONS")


def _fingerprint_source(
    *,
    service_id: str,
    operation_name: str,
    operation_id: str,
    http_method: str,
    path_template: str,
    resolved_input: ResolvedInput,
    quota_project: str | None,
) -> dict[str, Any]:
    return {
        "service_id": service_id,
        "operation_name": operation_name,
        "operation_id": operation_id,
        "http_method": http_method,
        "path_template": path_template,
        "input": resolved_input.fingerprint_input,
        "quota_project": quota_project or "",
    }


def _build_plan(
    *,
    tool: str,
    version: str,
    service: dict[str, Any],
    operation: dict[str, Any],
    resolved_input: ResolvedInput,
    quota_project: str | None,
    command_str: str | None,
) -> dict[str, Any]:
    service_id = str(service.get("api_id") or "")
    operation_name = str(operation.get("operation_name") or "")
    operation_id = str(operation.get("operation_id") or "")
    http_method = str(operation.get("http_method") or "").upper()
    path_template = str(operation.get("path") or "")
    request_preview = {
        "method": http_method,
        "path_template": path_template,
        "path_values": resolved_input.path_values,
        "query": resolved_input.query_params,
        "body": resolved_input.body,
    }
    fingerprint_source = _fingerprint_source(
        service_id=service_id,
        operation_name=operation_name,
        operation_id=operation_id,
        http_method=http_method,
        path_template=path_template,
        resolved_input=resolved_input,
        quota_project=quota_project,
    )
    input_fingerprint = _sha256_json(fingerprint_source["input"])
    plan_source = {
        "service_id": service_id,
        "operation_name": operation_name,
        "operation_id": operation_id,
        "classification": str(operation.get("classification") or ""),
        "http_method": http_method,
        "path_template": path_template,
        "input_fingerprint": input_fingerprint,
        "request_preview": request_preview,
        "risk_categories": sorted(set(operation.get("risk_categories") or [])),
        "quota_project": quota_project or "",
    }
    quota_project_fingerprint = _sha256_json({"quota_project": quota_project or ""})
    return {
        "tool": tool,
        "version": version,
        "generated_at_utc": _utc_now(),
        "command": command_str,
        "service_id": service_id,
        "service_title": service.get("title"),
        "service_version": service.get("version"),
        "operation_name": operation_name,
        "operation_id": operation_id,
        "classification": operation.get("classification"),
        "http_method": http_method,
        "path_template": path_template,
        "risk_categories": sorted(set(operation.get("risk_categories") or [])),
        "quota_project": quota_project or "",
        "quota_project_fingerprint": quota_project_fingerprint,
        "request_preview": request_preview,
        "input": resolved_input.fingerprint_input,
        "input_fingerprint": input_fingerprint,
        "plan_fingerprint": _sha256_json(plan_source),
    }


def _load_plan(plan_path: str) -> dict[str, Any]:
    plan = read_json_file(plan_path)
    if not isinstance(plan, dict):
        raise ValueError("Plan file must be a JSON object")
    return plan


def _validate_plan_matches(plan: dict[str, Any], *, service_id: str, operation_name: str, current_input_fingerprint: str, quota_project: str | None) -> None:
    if str(plan.get("service_id") or "") != service_id:
        raise SafetyError("Refused: plan service does not match current args")
    if str(plan.get("operation_name") or "") != operation_name:
        raise SafetyError("Refused: plan operation does not match current args")
    if str(plan.get("input_fingerprint") or "") != current_input_fingerprint:
        raise SafetyError("Refused: plan input does not match current args")
    plan_quota_project = str(plan.get("quota_project") or "")
    current_quota_project = quota_project or ""
    plan_quota_fingerprint = str(plan.get("quota_project_fingerprint") or "")
    current_quota_fingerprint = _sha256_json({"quota_project": current_quota_project})
    if plan_quota_project not in {current_quota_project, "***REDACTED***"} and plan_quota_fingerprint != current_quota_fingerprint:
        raise SafetyError("Refused: plan quota project does not match current args")
    if plan_quota_project == "***REDACTED***" and plan_quota_fingerprint != current_quota_fingerprint:
        raise SafetyError("Refused: plan quota project does not match current args")


def _validate_apply_gates(*, plan: dict[str, Any], args: Any) -> None:
    if not str(getattr(args, "plan_in", "") or "").strip():
        raise SafetyError("Refused: live writes require --plan-in")
    if not bool(getattr(args, "apply", False)):
        raise SafetyError("Refused: live writes require --apply")
    if not bool(getattr(args, "yes", False)):
        raise SafetyError("Refused: live writes require --apply --yes")
    risk_categories = {str(item) for item in (plan.get("risk_categories") or [])}
    classification = str(plan.get("classification") or "")
    if ("no_snapshot" in risk_categories or "high" in classification.lower()) and not bool(getattr(args, "ack_no_snapshot", False)):
        raise SafetyError("Refused: high-risk or no_snapshot writes require --ack-no-snapshot")
    if "irreversible" in risk_categories and not bool(getattr(args, "ack_irreversible", False)):
        raise SafetyError("Refused: irreversible writes require --ack-irreversible")


def _json_safe_response(response: Any, *, redaction_values: list[str]) -> Any:
    try:
        payload = response.json()
    except Exception:
        text = getattr(response, "text", "")
        return redact_text(str(text), redaction_values)
    return redact_jsonish_with_values(redact_jsonish(payload), redaction_values)


def _response_payload(*, request: dict[str, Any], response: Any, redaction_values: list[str]) -> dict[str, Any]:
    return {
        "request": redact_jsonish_with_values(redact_jsonish(request), redaction_values),
        "response_status": int(getattr(response, "status", getattr(response, "status_code", 0)) or 0),
        "response": _json_safe_response(response, redaction_values=redaction_values),
        "response_url": redact_text(str(getattr(response, "url", "") or ""), redaction_values),
    }


def _write_output_file(path: str | None, payload: dict[str, Any]) -> str | None:
    if not path:
        return None
    return write_json_file(path, payload)


def _display_path(path: str | None, *, env_file: str | None) -> str | None:
    if not path:
        return None
    base = Path(env_file or ".env").expanduser().resolve().parent
    resolved = Path(path).expanduser().resolve()
    try:
        return str(resolved.relative_to(base))
    except ValueError:
        return f"<outside-env-dir>/{resolved.name}"


def execute_generated_operation(args: Any, ctx: dict[str, Any]) -> int:
    registry = load_registry(_REPO_ROOT)
    service_id = str(getattr(args, "cmd", "") or "").strip()
    operation_name = str(getattr(args, "operation", "") or "").strip()
    try:
        service, operation = _service_operation(registry, service_id, operation_name)
        cfg: Config | None = ctx.get("cfg")
        quota_project = str(getattr(args, "quota_project", "") or "").strip() or (cfg.quota_project if cfg else None)
        input_obj = _load_input_json(str(getattr(args, "input_json", "") or "").strip())
        http_method = str(operation.get("http_method") or "").upper()
        path_template = str(operation.get("path") or "")
        resolved_input = _normalize_input(input_obj, path_template=path_template, http_method=http_method)
        _validate_allowlists(cfg, resolved_input.path_values)
        version = str(ctx.get("tool_version") or "")
        command_str = str(ctx.get("command_str") or "")
        plan = _build_plan(
            tool=str(ctx.get("tool") or "qwayk-gcp-safe-agent-cli"),
            version=version,
            service=service,
            operation=operation,
            resolved_input=resolved_input,
            quota_project=quota_project,
            command_str=command_str,
        )
        output_redaction_values = list(cfg.redaction_values()) if cfg is not None else []
        if quota_project:
            output_redaction_values.append(quota_project)
        error_redaction_values = _redaction_values(cfg, input_obj, plan)
        plan_safe = redact_jsonish_with_values(redact_jsonish(plan), output_redaction_values)
        plan_file_redaction_values = [*output_redaction_values, *iter_scalar_strings(input_obj)]
        plan_file_safe = redact_jsonish_with_values(redact_jsonish(plan), plan_file_redaction_values)
        is_read = str(operation.get("classification") or "") == "read"
        plan_out = str(getattr(args, "plan_out", "") or "").strip() or str(ctx.get("plan_out") or "").strip()
        output_file = str(getattr(args, "output_file", "") or "").strip() or str(ctx.get("output_file") or "").strip()
        if not bool(getattr(args, "apply", False)) and not is_read:
            plan_path = _write_output_file(plan_out, plan_file_safe)
            payload = {
                "ok": True,
                "dry_run": True,
                "service_id": service_id,
                "operation_name": operation_name,
                "classification": operation.get("classification"),
                "risk_categories": plan_safe["risk_categories"],
                "plan": plan_safe,
                "plan_out": plan_path,
                "request": plan_safe["request_preview"],
            }
            output_path = _write_output_file(output_file, payload)
            if output_path:
                payload["output_file"] = _display_path(output_path, env_file=str(ctx.get("env_file") or ".env"))
            if plan_path:
                payload["plan_out"] = _display_path(plan_path, env_file=str(ctx.get("env_file") or ".env"))
            ctx["out"].emit(payload)
            return 0

        if is_read:
            try:
                discovery_doc = load_discovery_document(service, timeout_s=float(ctx.get("timeout_s") or 30.0))
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(sanitize_error_message(exc, error_redaction_values)) from None
            base_url = _base_url_from_discovery_doc(discovery_doc)
            url = _build_url(base_url=base_url, path_template=path_template, path_values=resolved_input.path_values)
            try:
                adc = load_adc_credentials(quota_project_id=quota_project)
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(sanitize_error_message(exc, error_redaction_values)) from None
            headers = _request_headers(token=str(getattr(adc.credentials, "token", "") or ""), quota_project=adc.quota_project_id)
            client = HttpClient(
                timeout_s=float(ctx.get("timeout_s") or 30.0),
                verbose=bool(ctx.get("verbose", False)),
                user_agent=f"{ctx.get('tool') or 'qwayk-gcp-safe-agent-cli'}/{ctx.get('tool_version') or ''}".strip("/"),
                redaction_values=[*output_redaction_values, *iter_scalar_strings(input_obj)],
            )
            try:
                response = client.request(
                    http_method,
                    url,
                    headers=headers,
                    params=resolved_input.query_params or None,
                    json_body=resolved_input.body if isinstance(resolved_input.body, (dict, list)) else resolved_input.body,
                )
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(sanitize_error_message(exc, error_redaction_values)) from None
            response_payload = _response_payload(
                request={
                    "method": http_method,
                    "url": url,
                    "params": resolved_input.query_params,
                    "body": resolved_input.body,
                },
                response=response,
                redaction_values=[*output_redaction_values, *iter_scalar_strings(input_obj)],
            )
            payload = {
                "ok": True,
                "dry_run": False,
                "service_id": service_id,
                "operation_name": operation_name,
                "classification": operation.get("classification"),
                "risk_categories": plan_safe["risk_categories"],
                **response_payload,
            }
            output_path = _write_output_file(output_file, payload)
            if output_path:
                payload["output_file"] = _display_path(output_path, env_file=str(ctx.get("env_file") or ".env"))
            ctx["out"].emit(payload)
            return 0

        plan_in = str(getattr(args, "plan_in", "") or "").strip()
        if not plan_in:
            raise SafetyError("Refused: live writes require --plan-in")
        if not str(getattr(args, "input_json", "") or "").strip():
            raise SafetyError("Refused: live writes require --input-json so the plan fingerprint can be checked")
        if not bool(getattr(args, "apply", False)):
            raise SafetyError("Refused: live writes require --apply")
        if not bool(getattr(args, "yes", False)):
            raise SafetyError("Refused: live writes require --apply --yes")

        current_input_fingerprint = _sha256_json(
            _fingerprint_source(
                service_id=service_id,
                operation_name=operation_name,
                operation_id=str(operation.get("operation_id") or ""),
                http_method=http_method,
                path_template=path_template,
                resolved_input=resolved_input,
                quota_project=quota_project,
            )["input"]
        )
        plan = _load_plan(plan_in)
        _validate_plan_matches(
            plan,
            service_id=service_id,
            operation_name=operation_name,
            current_input_fingerprint=current_input_fingerprint,
            quota_project=quota_project,
        )
        _validate_apply_gates(plan=plan, args=args)

        try:
            discovery_doc = load_discovery_document(service, timeout_s=float(ctx.get("timeout_s") or 30.0))
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(sanitize_error_message(exc, error_redaction_values)) from None
        base_url = _base_url_from_discovery_doc(discovery_doc)
        url = _build_url(base_url=base_url, path_template=path_template, path_values=resolved_input.path_values)
        try:
            adc = load_adc_credentials(quota_project_id=quota_project)
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(sanitize_error_message(exc, error_redaction_values)) from None
        headers = _request_headers(token=str(getattr(adc.credentials, "token", "") or ""), quota_project=adc.quota_project_id)
        client = HttpClient(
            timeout_s=float(ctx.get("timeout_s") or 30.0),
            verbose=bool(ctx.get("verbose", False)),
            user_agent=f"{ctx.get('tool') or 'qwayk-gcp-safe-agent-cli'}/{ctx.get('tool_version') or ''}".strip("/"),
            redaction_values=[*output_redaction_values, *iter_scalar_strings(input_obj)],
        )
        try:
            response = client.request(
                http_method,
                url,
                headers=headers,
                params=resolved_input.query_params or None,
                json_body=resolved_input.body if isinstance(resolved_input.body, (dict, list)) else resolved_input.body,
            )
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(sanitize_error_message(exc, error_redaction_values)) from None
        response_payload = _response_payload(
            request={
                "method": http_method,
                "url": url,
                "params": resolved_input.query_params,
                "body": resolved_input.body,
            },
            response=response,
            redaction_values=[*output_redaction_values, *iter_scalar_strings(input_obj)],
        )
        receipt = {
            "tool": ctx.get("tool") or "qwayk-gcp-safe-agent-cli",
            "version": version,
            "generated_at_utc": _utc_now(),
            "service_id": service_id,
            "operation_name": operation_name,
            "operation_id": str(operation.get("operation_id") or ""),
            "classification": operation.get("classification"),
            "risk_categories": sorted(set(operation.get("risk_categories") or [])),
            "plan_fingerprint": str(plan.get("plan_fingerprint") or ""),
            "plan_check": {
                "matches": True,
                "service_id": service_id,
                "operation_name": operation_name,
                "input_fingerprint": current_input_fingerprint,
            },
            "read_back_verified": False,
            "verification_status": "limited_verification",
            "verification_note": "limited verification: successful provider response only; no read-back check ran.",
            **response_payload,
        }
        receipt_out = str(getattr(args, "receipt_out", "") or "").strip() or str(ctx.get("receipt_out") or "").strip()
        receipt_path = _write_output_file(receipt_out, receipt)
        payload = {
            "ok": True,
            "dry_run": False,
            "applied": True,
            "service_id": service_id,
            "operation_name": operation_name,
            "classification": operation.get("classification"),
            "risk_categories": receipt["risk_categories"],
            "receipt": redact_jsonish_with_values(redact_jsonish(receipt), output_redaction_values),
            "receipt_out": receipt_path,
            **response_payload,
        }
        output_path = _write_output_file(output_file, payload)
        if output_path:
            payload["output_file"] = _display_path(output_path, env_file=str(ctx.get("env_file") or ".env"))
        if receipt_path:
            payload["receipt_out"] = _display_path(receipt_path, env_file=str(ctx.get("env_file") or ".env"))
        ctx["out"].emit(payload)
        return 0
    except Exception:
        raise
