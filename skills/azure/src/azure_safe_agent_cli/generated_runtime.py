from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote

from .config import Config
from .errors import SafetyError, ValidationError
from .generated_registry import AzureRegistry, load_inventory, load_registry
from .http import HttpClient
from .json_files import read_json_file, write_json_file
from .redaction import (
    REDACTED,
    iter_scalar_strings,
    redact_jsonish,
    redact_jsonish_with_values,
    sanitize_error_message,
)

READ_CLASSES = {"read", "sensitive_read"}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_json(obj: Any) -> str:
    return hashlib.sha256(_canonical_json(obj).encode("utf-8")).hexdigest()


def inventory_summary() -> dict[str, Any]:
    data = load_inventory(_repo_root())
    return {
        "ok": True,
        "generated_at_utc": data.get("generated_at_utc"),
        "source": data.get("source"),
        "boundary": data.get("boundary"),
        "summary": data.get("summary", {}),
        "services": {
            "count": len(data.get("services", [])),
            "service_ids": [str(service.get("service_id") or "") for service in data.get("services", []) if service.get("service_id")],
        },
    }


def _extract_path_names(path_template: str) -> list[str]:
    return [match.group(1) for match in re.finditer(r"{([^}]+)}", path_template)]


def _coerce_mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _load_input_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    data = read_json_file(path)
    if not isinstance(data, dict):
        raise ValidationError("Input JSON must be a JSON object")
    return data


def _normalize_input(input_obj: dict[str, Any], *, path_template: str, api_version: str) -> dict[str, Any]:
    top_level = {k: v for k, v in input_obj.items() if k not in {"path", "query", "body", "headers"}}
    path_values = _coerce_mapping(input_obj.get("path"))
    query_params = _coerce_mapping(input_obj.get("query"))
    body = input_obj.get("body") if "body" in input_obj else None

    for name in _extract_path_names(path_template):
        if name in path_values:
            continue
        if name in top_level:
            path_values[name] = top_level.pop(name)

    missing = [name for name in _extract_path_names(path_template) if str(path_values.get(name) or "").strip() == ""]
    if missing:
        raise ValidationError("Missing required path parameters: " + ", ".join(sorted(set(missing))))

    query_params.setdefault("api-version", api_version)
    if body is None and top_level:
        body = top_level
    return {"path": path_values, "query": query_params, "body": body}


def _build_url(*, cfg: Config, operation: dict[str, Any], path_values: dict[str, Any]) -> str:
    path = str(operation.get("path") or "")
    for name in _extract_path_names(path):
        raw = str(path_values.get(name) or "")
        path = path.replace(f"{{{name}}}", quote(raw, safe=""))
    if str(operation.get("plane") or "") == "data_plane":
        if not cfg.data_plane_endpoint:
            raise ValidationError("Missing AZURE_DATA_PLANE_ENDPOINT for data-plane command")
        base_url = cfg.data_plane_endpoint
    else:
        base_url = cfg.management_endpoint
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def _validate_allowlists(cfg: Config, *, service_id: str, path_values: dict[str, Any], operation: dict[str, Any]) -> None:
    if cfg.allowed_services and service_id not in cfg.allowed_services:
        raise SafetyError(f"Refused: service {service_id} is not in AZURE_ALLOWED_SERVICES")
    tenant_candidates = [str(path_values.get(k) or "") for k in path_values if "tenant" in k.lower()]
    if cfg.tenant_id:
        tenant_candidates.append(cfg.tenant_id)
    if cfg.allowed_tenants:
        for value in tenant_candidates:
            if value and value not in cfg.allowed_tenants:
                raise SafetyError(f"Refused: tenant {value} is not in AZURE_ALLOWED_TENANTS")
    if cfg.allowed_subscriptions:
        for key, value in path_values.items():
            if "subscription" in key.lower() and str(value) not in cfg.allowed_subscriptions:
                raise SafetyError(f"Refused: {key}={value} is not in AZURE_ALLOWED_SUBSCRIPTIONS")
    if cfg.allowed_resource_groups:
        for key, value in path_values.items():
            lowered = key.lower()
            if "resourcegroup" in lowered or "resource_group" in lowered:
                if str(value) not in cfg.allowed_resource_groups:
                    raise SafetyError(f"Refused: {key}={value} is not in AZURE_ALLOWED_RESOURCE_GROUPS")
    if cfg.allowed_locations:
        candidates: list[tuple[str, str]] = []
        for key, value in path_values.items():
            if "location" in key.lower() or "region" in key.lower():
                candidates.append((key, str(value)))
        body = operation.get("request_preview_body")
        _ = body
        for key, value in candidates:
            if value and value not in cfg.allowed_locations:
                raise SafetyError(f"Refused: {key}={value} is not in AZURE_ALLOWED_LOCATIONS")


def _service_operation(registry: AzureRegistry, service_id: str, operation_name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    service = registry.get_service(service_id)
    if not service:
        raise ValidationError(f"Unknown Azure service command: {service_id}")
    operation = registry.get_operation(service_id, operation_name)
    if not operation:
        raise ValidationError(f"Unknown Azure operation for {service_id}: {operation_name}")
    return service, operation


def _plan_source(*, service_id: str, operation_name: str, operation: dict[str, Any], resolved: dict[str, Any]) -> dict[str, Any]:
    return {
        "service_id": service_id,
        "operation_name": operation_name,
        "operation_id": operation.get("operation_id"),
        "method": operation.get("http_method"),
        "path": operation.get("path"),
        "version": operation.get("version"),
        "resolved_input": resolved,
    }


def _build_plan(*, tool: str, version: str, service_id: str, service: dict[str, Any], operation_name: str, operation: dict[str, Any], resolved: dict[str, Any], command: str) -> dict[str, Any]:
    source = _plan_source(service_id=service_id, operation_name=operation_name, operation=operation, resolved=resolved)
    return {
        "tool": tool,
        "version": version,
        "generated_at_utc": _utc_now(),
        "command": command,
        "service_id": service_id,
        "service": service.get("service"),
        "operation_name": operation_name,
        "operation_id": operation.get("operation_id"),
        "classification": operation.get("classification"),
        "risk_categories": sorted(set(operation.get("risk_categories") or [])),
        "http_method": operation.get("http_method"),
        "path_template": operation.get("path"),
        "api_version": operation.get("version"),
        "lifecycle": operation.get("lifecycle"),
        "request_preview": {
            "method": operation.get("http_method"),
            "path_template": operation.get("path"),
            "path": resolved["path"],
            "query": resolved["query"],
            "body": resolved["body"],
        },
        "input_fingerprint": _sha256_json(resolved),
        "plan_fingerprint": _sha256_json(source),
        "rollback": {"supported": False, "notes": "Azure generated writes do not claim automatic rollback; review the plan before applying."},
        "verification_plan": "Provider response is checked; operation-specific read-back is marked limited until safe target credentials are available.",
    }


def _validate_plan_matches(plan: dict[str, Any], *, service_id: str, operation_name: str, input_fingerprint: str) -> None:
    if str(plan.get("service_id") or "") != service_id:
        raise SafetyError("Refused: plan service does not match current args")
    if str(plan.get("operation_name") or "") != operation_name:
        raise SafetyError("Refused: plan operation does not match current args")
    if str(plan.get("input_fingerprint") or "") != input_fingerprint:
        raise SafetyError("Refused: plan input does not match current args")


def _validate_apply_gates(plan: dict[str, Any], args: Any) -> None:
    if not str(getattr(args, "plan_in", "") or "").strip():
        raise SafetyError("Refused: live writes require --plan-in")
    if not bool(getattr(args, "apply", False)):
        raise SafetyError("Refused: live writes require --apply")
    if not bool(getattr(args, "yes", False)):
        raise SafetyError("Refused: live writes require --apply --yes")
    risks = {str(item) for item in plan.get("risk_categories") or []}
    if ({"no_snapshot", "identity_security", "spend_quota", "public_exposure"} & risks) and not bool(getattr(args, "ack_no_snapshot", False)):
        raise SafetyError("Refused: high-risk Azure writes require --ack-no-snapshot")
    if "irreversible" in risks and not bool(getattr(args, "ack_irreversible", False)):
        raise SafetyError("Refused: irreversible Azure writes require --ack-irreversible")


def _write_output_file(path: str | None, payload: dict[str, Any]) -> str | None:
    if not path:
        return None
    return write_json_file(path, payload)


def _redact_sensitive_read_body(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _redact_sensitive_read_body(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_sensitive_read_body(item) for item in value]
    if value is None:
        return None
    return REDACTED


def _safe_response(response: Any, *, redaction_values: list[str], sensitive_read: bool = False) -> dict[str, Any]:
    try:
        body = response.json()
    except Exception:
        body = str(getattr(response, "text", "") or "")
    if sensitive_read:
        safe_body = _redact_sensitive_read_body(redact_jsonish_with_values(redact_jsonish(body), redaction_values))
    else:
        safe_body = redact_jsonish_with_values(redact_jsonish(body), redaction_values)
    return {
        "response_status": int(getattr(response, "status", getattr(response, "status_code", 0)) or 0),
        "response_url": str(getattr(response, "url", "") or ""),
        "response": safe_body,
    }


def _poll_azure_async_operation(
    *,
    client: HttpClient,
    response: Any,
    headers: dict[str, str],
    redaction_values: list[str],
    max_polls: int = 5,
) -> dict[str, Any]:
    response_headers = {str(k).lower(): str(v) for k, v in getattr(response, "headers", {}).items()}
    poll_url = response_headers.get("azure-asyncoperation") or response_headers.get("operation-location") or response_headers.get("location")
    if not poll_url:
        return {"polling_performed": False, "status": None, "attempts": 0}

    last_payload: Any = None
    for attempt in range(1, max_polls + 1):
        poll_response = client.request("GET", poll_url, headers=headers, retries=3)
        try:
            last_payload = poll_response.json()
        except Exception:
            last_payload = str(getattr(poll_response, "text", "") or "")
        status = ""
        if isinstance(last_payload, dict):
            status = str(last_payload.get("status") or last_payload.get("provisioningState") or "").lower()
        if status in {"succeeded", "failed", "canceled", "cancelled"}:
            return {
                "polling_performed": True,
                "status": status,
                "attempts": attempt,
                "response": redact_jsonish_with_values(redact_jsonish(last_payload), redaction_values),
            }
    return {
        "polling_performed": True,
        "status": "incomplete",
        "attempts": max_polls,
        "response": redact_jsonish_with_values(redact_jsonish(last_payload), redaction_values),
    }


def execute_generated_operation(args: Any, ctx: dict[str, Any]) -> int:
    registry = load_registry(_repo_root())
    service_id = str(getattr(args, "cmd", "") or "").strip()
    operation_name = str(getattr(args, "operation", "") or "").strip()
    cfg: Config = ctx["cfg"]
    service, operation = _service_operation(registry, service_id, operation_name)
    input_obj = _load_input_json(str(getattr(args, "input_json", "") or "").strip())
    resolved = _normalize_input(input_obj, path_template=str(operation.get("path") or ""), api_version=str(operation.get("version") or ""))
    _validate_allowlists(cfg, service_id=service_id, path_values=resolved["path"], operation=operation)

    plan = _build_plan(
        tool=str(ctx.get("tool") or "qwayk-azure-safe-agent-cli"),
        version=str(ctx.get("tool_version") or ""),
        service_id=service_id,
        service=service,
        operation_name=operation_name,
        operation=operation,
        resolved=resolved,
        command=str(ctx.get("command_str") or ""),
    )
    redaction_values = list(cfg.redaction_values()) + list(iter_scalar_strings(input_obj))
    plan_safe = redact_jsonish_with_values(redact_jsonish(plan), redaction_values)
    is_read = str(operation.get("classification") or "") in READ_CLASSES

    plan_out = str(getattr(args, "plan_out", "") or "").strip() or str(ctx.get("plan_out") or "").strip()
    receipt_out = str(getattr(args, "receipt_out", "") or "").strip() or str(ctx.get("receipt_out") or "").strip()
    output_file = str(getattr(args, "output_file", "") or "").strip()

    if not is_read and not bool(getattr(args, "apply", False)):
        plan_path = _write_output_file(plan_out, plan_safe)
        payload = {
            "ok": True,
            "dry_run": True,
            "changed": False,
            "service_id": service_id,
            "operation_name": operation_name,
            "classification": operation.get("classification"),
            "risk_categories": plan_safe["risk_categories"],
            "plan": plan_safe,
            "plan_out": plan_path,
        }
        output_path = _write_output_file(output_file, payload)
        if output_path:
            payload["output_file"] = output_path
        ctx["out"].emit(payload)
        return 0

    if not cfg.token:
        raise ValidationError("Missing AZURE_API_TOKEN")

    try:
        url = _build_url(cfg=cfg, operation=operation, path_values=resolved["path"])
        client = HttpClient(
            timeout_s=float(ctx.get("timeout_s") or 30.0),
            verbose=bool(ctx.get("verbose", False)),
            user_agent=f"{ctx.get('tool') or 'qwayk-azure-safe-agent-cli'}/{ctx.get('tool_version') or ''}".strip("/"),
        )
        headers = {"Authorization": f"Bearer {cfg.token}", "Accept": "application/json"}
        if resolved["body"] is not None:
            headers["Content-Type"] = "application/json"
        if is_read:
            sensitive_read = "sensitive_read" in set(plan_safe["risk_categories"])
            response = client.request(
                str(operation.get("http_method") or "GET"),
                url,
                headers=headers,
                params=resolved["query"],
                json_body=resolved["body"] if isinstance(resolved["body"], dict) else None,
                retries=3,
            )
            payload = {
                "ok": True,
                "dry_run": False,
                "changed": False,
                "service_id": service_id,
                "operation_name": operation_name,
                "classification": operation.get("classification"),
                "risk_categories": plan_safe["risk_categories"],
                "sensitive_output_redacted": sensitive_read,
                **_safe_response(response, redaction_values=redaction_values, sensitive_read=sensitive_read),
            }
            output_path = _write_output_file(output_file, payload)
            if output_path:
                payload["output_file"] = output_path
            ctx["out"].emit(payload)
            return 0

        plan_in = str(getattr(args, "plan_in", "") or "").strip()
        if not plan_in:
            raise SafetyError("Refused: live writes require --plan-in")
        saved_plan = read_json_file(plan_in)
        if not isinstance(saved_plan, dict):
            raise SafetyError("Refused: plan file must be a JSON object")
        _validate_plan_matches(saved_plan, service_id=service_id, operation_name=operation_name, input_fingerprint=plan["input_fingerprint"])
        _validate_apply_gates(saved_plan, args)
        response = client.request(
            str(operation.get("http_method") or "POST"),
            url,
            headers=headers,
            params=resolved["query"],
            json_body=resolved["body"] if isinstance(resolved["body"], dict) else None,
            retries=3,
        )
        polling = _poll_azure_async_operation(
            client=client,
            response=response,
            headers=headers,
            redaction_values=redaction_values,
        )
        receipt = {
            "tool": ctx.get("tool") or "qwayk-azure-safe-agent-cli",
            "version": ctx.get("tool_version"),
            "generated_at_utc": _utc_now(),
            "service_id": service_id,
            "operation_name": operation_name,
            "classification": operation.get("classification"),
            "risk_categories": plan_safe["risk_categories"],
            "plan_fingerprint": saved_plan.get("plan_fingerprint"),
            "changed": True,
            "verified": False,
            "verification_status": "limited_verification",
            "verification_note": "Azure returned a successful response; generated operation-specific read-back is live-unverified.",
            "azure_async_polling": polling,
            **_safe_response(response, redaction_values=redaction_values),
        }
        receipt_safe = redact_jsonish_with_values(redact_jsonish(receipt), redaction_values)
        receipt_path = _write_output_file(receipt_out, receipt_safe)
        payload = {
            "ok": True,
            "dry_run": False,
            "applied": True,
            "changed": True,
            "service_id": service_id,
            "operation_name": operation_name,
            "classification": operation.get("classification"),
            "risk_categories": plan_safe["risk_categories"],
            "receipt": receipt_safe,
            "receipt_out": receipt_path,
        }
        output_path = _write_output_file(output_file, payload)
        if output_path:
            payload["output_file"] = output_path
        ctx["out"].emit(payload)
        return 0
    except (SafetyError, ValidationError):
        raise
    except Exception as exc:
        raise RuntimeError(sanitize_error_message(exc, redaction_values)) from None
