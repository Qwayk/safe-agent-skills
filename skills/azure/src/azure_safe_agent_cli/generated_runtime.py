from __future__ import annotations

import hashlib
import json
import re
import time
from typing import Any
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qs, quote, urlencode, urljoin, urlsplit

from .azure_auth import AzureConnection, https_origin, resolve_connection
from .config import Config
from .errors import SafetyError, ValidationError
from .generated_registry import AzureRegistry, load_inventory, load_registry
from .http import HttpClient, HttpStatusError, safe_url
from .json_files import read_json_file, write_json_file
from .redaction import (
    REDACTED,
    iter_scalar_strings,
    redact_jsonish,
    redact_jsonish_with_values,
    sanitize_error_message,
)

READ_CLASSES = {"read", "sensitive_read"}


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_json(obj: Any) -> str:
    return hashlib.sha256(_canonical_json(obj).encode("utf-8")).hexdigest()


def inventory_summary() -> dict[str, Any]:
    data = load_inventory()
    services = data.get("services", [])
    return {
        "ok": True,
        "generated_at_utc": data.get("generated_at_utc"),
        "source": data.get("source"),
        "boundary": data.get("boundary"),
        "summary": data.get("summary", {}),
        "services": {
            "count": len(services),
            "command_count": sum(bool(service.get("operations")) for service in services),
            "service_ids": [str(service.get("service_id") or "") for service in services if service.get("service_id")],
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


def _normalize_input(
    input_obj: dict[str, Any], *, path_template: str, api_version: str, subscription: str | None,
) -> dict[str, Any]:
    top_level = {k: v for k, v in input_obj.items() if k not in {"path", "query", "body", "headers"}}
    path_values = _coerce_mapping(input_obj.get("path"))
    query_params = _coerce_mapping(input_obj.get("query"))
    body = input_obj.get("body") if "body" in input_obj else None

    for name in _extract_path_names(path_template):
        if name in path_values:
            continue
        if name in top_level:
            path_values[name] = top_level.pop(name)
        elif name.casefold() == "subscriptionid" and subscription:
            path_values[name] = subscription

    missing = [name for name in _extract_path_names(path_template) if str(path_values.get(name) or "").strip() == ""]
    if missing:
        raise ValidationError("Missing required path parameters: " + ", ".join(sorted(set(missing))))

    query_params.setdefault("api-version", api_version)
    if body is None and top_level:
        body = top_level
    return {"path": path_values, "query": query_params, "body": body}


_ARM_SCOPE_FIELDS = {"scope", "resourceid", "resourceuri"}
_ARM_REFERENCES = re.compile(r"(?:^|/)(subscriptions|resourcegroups)/([^/]+)", re.IGNORECASE)


def _arm_id(value: str) -> bool:
    return value.lstrip("/").casefold().startswith(("subscriptions/", "providers/", "tenants/", "resourcegroups/"))


def _build_url(*, endpoint: str, operation: dict[str, Any], path_values: dict[str, Any]) -> str:
    path = str(operation.get("path") or "")
    for name in _extract_path_names(path):
        value = str(path_values[name])
        if value in {".", ".."}:
            raise ValidationError("Use the Azure resource name in the request path.")
        is_scope = name.casefold() in _ARM_SCOPE_FIELDS and _arm_id(value)
        if is_scope:
            value = value.strip("/")
            if any(not part or part in {".", ".."} for part in value.split("/")):
                raise ValidationError("Use a complete Azure resource ID for the scope.")
        path = path.replace(f"{{{name}}}", quote(value, safe="/" if is_scope else ""))
    return f"{endpoint.rstrip('/')}/{path.lstrip('/')}"


def _targets(fields: Any):
    if isinstance(fields, dict):
        for key, value in fields.items():
            name = str(key).replace("_", "").casefold()
            if isinstance(value, str):
                if name in {"subscription", "subscriptionid"}:
                    yield "subscriptions", value
                elif name in {"resourcegroup", "resourcegroupname"}:
                    yield "resourcegroups", value
                elif name in {"location", "locationname", "region", "regionname"}:
                    yield "locations", value
                elif name in {"tenant", "tenantid"}:
                    yield "tenants", value
                elif name in _ARM_SCOPE_FIELDS or name.endswith("resourceid") or name == "id":
                    if _arm_id(value):
                        for kind, match in _ARM_REFERENCES.findall(value):
                            yield kind.casefold(), match
            elif name not in {"tags", "metadata", "labels"}:
                yield from _targets(value)
    elif isinstance(fields, list):
        for value in fields:
            yield from _targets(value)


def _requested_subscription(input_obj: dict[str, Any]) -> str | None:
    path = _coerce_mapping(input_obj.get("path"))
    for fields in (path, {key: value for key, value in input_obj.items() if isinstance(value, str)}):
        for kind, value in _targets(fields):
            if kind == "subscriptions" and value:
                return value
    return None


def _validate_allowlists(cfg: Config, *, service_id: str, resolved: dict[str, Any]) -> None:
    groups = {
        "services": ("AZURE_ALLOWED_SERVICES", cfg.allowed_services),
        "tenants": ("AZURE_ALLOWED_TENANTS", cfg.allowed_tenants),
        "subscriptions": ("AZURE_ALLOWED_SUBSCRIPTIONS", cfg.allowed_subscriptions),
        "resourcegroups": ("AZURE_ALLOWED_RESOURCE_GROUPS", cfg.allowed_resource_groups),
        "locations": ("AZURE_ALLOWED_LOCATIONS", cfg.allowed_locations),
    }
    targets = [("services", service_id), *list(_targets(resolved))]
    if cfg.tenant_id:
        targets.append(("tenants", cfg.tenant_id))
    for kind, value in targets:
        setting, allowed = groups[kind]
        if value and allowed and value.casefold() not in {item.casefold() for item in allowed}:
            raise SafetyError(f"Refused: target is outside {setting}")


_SPEND_OPERATIONS = {
    "VirtualMachines_Start",
    "VirtualMachines_CreateOrUpdate",
    "VirtualMachineScaleSets_Start",
    "VirtualMachineScaleSets_CreateOrUpdate",
    "Disks_CreateOrUpdate",
    "CapacityReservations_CreateOrUpdate",
    "ManagedClusters_CreateOrUpdate",
}


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


def _build_plan(*, tool: str, version: str, service_id: str, service: dict[str, Any], operation_name: str, operation: dict[str, Any], resolved: dict[str, Any], command: str, connection: AzureConnection | None) -> dict[str, Any]:
    source = _plan_source(service_id=service_id, operation_name=operation_name, operation=operation, resolved=resolved)
    details = connection.review_details() if connection else None
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
        "plan_fingerprint": _sha256_json({"request": source, "connection": details}),
        "connection": details,
        "requires_spending_approval": operation.get("resource_provider") in {"Microsoft.Compute", "Microsoft.ContainerService"}
        and operation.get("operation_id") in _SPEND_OPERATIONS,
        "rollback": {"supported": False, "notes": "Azure generated writes do not claim automatic rollback; review the plan before applying."},
        "verification_plan": "Provider response is checked; operation-specific read-back is marked limited until safe target credentials are available.",
    }


def _validate_plan_matches(saved: dict[str, Any], expected: dict[str, Any]) -> None:
    if not isinstance(saved.get("connection"), dict):
        raise SafetyError("Refused: make and review a new plan with --bind-azure.")
    fields = (
        "service_id", "operation_name", "operation_id", "http_method", "path_template",
        "api_version", "input_fingerprint", "risk_categories", "classification", "requires_spending_approval",
    )
    if any(saved.get(field) != expected[field] for field in fields):
        raise SafetyError("Refused: the request or its approval rules changed. Review a new plan.")
    if saved["connection"] != expected["connection"] or saved.get("plan_fingerprint") != expected["plan_fingerprint"]:
        raise SafetyError("Refused: the Azure identity, subscription or endpoint changed. Review a new plan.")
    if saved.get("request_preview") != expected["request_preview"]:
        raise SafetyError("Refused: the saved request preview changed. Review a new plan.")


def _validate_apply_gates(plan: dict[str, Any], args: Any) -> None:
    if not args.plan_in:
        raise SafetyError("Refused: live writes require --plan-in")
    if not args.yes:
        raise SafetyError("Refused: live writes require --apply --yes")
    risks = set(plan["risk_categories"])
    if {"no_snapshot", "identity_security", "spend_quota", "public_exposure"} & risks and not args.ack_no_snapshot:
        raise SafetyError("Refused: this Azure write requires --ack-no-snapshot")
    if "irreversible" in risks and not args.ack_irreversible:
        raise SafetyError("Refused: irreversible Azure writes require --ack-irreversible")
    if plan["requires_spending_approval"] and not args.ack_spend_money:
        raise SafetyError("Refused: this Azure change can add charges. Get approval and use --ack-spend-money.")


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
        "response_url": safe_url(str(getattr(response, "url", "") or "")),
        "response": safe_body,
    }


def _operation_status(body: Any) -> str:
    if not isinstance(body, dict):
        return ""
    properties = _coerce_mapping(body.get("properties"))
    return str(body.get("status") or body.get("provisioningState") or properties.get("provisioningState") or "").lower()


def _safe_status_url(url: str) -> str:
    parts = urlsplit(url)
    version = parse_qs(parts.query).get("api-version", [])
    return safe_url(url) + ("?" + urlencode({"api-version": version[0]}) if version else "")


def _retry_after(value: str) -> float:
    try:
        return max(0, int(value))
    except ValueError:
        try:
            return max(0, parsedate_to_datetime(value).timestamp() - time.time())
        except (OverflowError, ValueError, TypeError):
            return 0


def _poll_azure_async_operation(
    *,
    client: HttpClient,
    response: Any,
    headers: dict[str, str],
    redaction_values: list[str],
    request_url: str | None = None,
) -> dict[str, Any]:
    response_headers = {str(k).lower(): str(v) for k, v in getattr(response, "headers", {}).items()}
    state = _operation_status(_safe_response(response, redaction_values=[])["response"])
    result: dict[str, Any] = {"polling_performed": False, "status": None, "attempts": 0}
    if state in {"failed", "canceled", "cancelled"}:
        return {**result, "status": state}
    long_running_url = response_headers.get("azure-asyncoperation") or response_headers.get("operation-location")
    pending = getattr(response, "status", 0) == 202 or state not in {"", "succeeded"}
    target = long_running_url or (response_headers.get("location") if pending else None)
    if not target:
        return {**result, "status": "pending" if pending else None}
    original = request_url or str(getattr(response, "url", ""))
    target = urljoin(original, target)
    try:
        trusted = https_origin(original) == https_origin(target)
    except ValidationError:
        trusted = False
    result["status"] = "pending"
    if not trusted:
        result["note"] = "Azure returned a status URL on a different host. Check the resource directly."
        return result

    result["status_url"] = _safe_status_url(target)
    delay = _retry_after(response_headers.get("retry-after", ""))
    if delay > 0:
        result["retry_after_seconds"] = round(delay)
        return result

    result.update(polling_performed=True, attempts=1)
    try:
        reply = client.request("GET", target, headers=headers)
    except RuntimeError:
        result.update(status="outcome_unknown", note="The Azure status check did not finish.")
        return result
    safe = _safe_response(reply, redaction_values=redaction_values)
    try:
        state = _operation_status(reply.json())
    except (ValueError, AttributeError):
        state = ""
    if state in {"succeeded", "failed", "canceled", "cancelled"}:
        result["status"] = state
    elif not long_running_url and getattr(reply, "status", 0) in {200, 201, 204} and not state:
        result["status"] = "succeeded"
    result["response"] = safe["response"]
    next_delay = _retry_after(getattr(reply, "headers", {}).get("retry-after", ""))
    if result["status"] == "pending" and next_delay > 0:
        result["retry_after_seconds"] = round(next_delay)
    return result


def _safe_plan(plan: dict[str, Any], values: list[str]) -> dict[str, Any]:
    return {
        **plan,
        "command": redact_jsonish_with_values(plan["command"], values),
        "request_preview": {
            **plan["request_preview"],
            "path": redact_jsonish_with_values(plan["request_preview"]["path"], values),
            "query": redact_jsonish_with_values(redact_jsonish(plan["request_preview"]["query"]), values),
            "body": redact_jsonish_with_values(redact_jsonish(plan["request_preview"]["body"]), values),
        },
    }


def _write_result(
    client: HttpClient, *, url: str, headers: dict[str, str], plan: dict[str, Any],
    resolved: dict[str, Any], redaction_values: list[str],
) -> dict[str, Any]:
    polling = {"polling_performed": False, "status": None, "attempts": 0}
    try:
        response = client.request(plan["http_method"], url, headers=headers, params=resolved["query"],
                                  json_body=resolved["body"])
    except RuntimeError as exc:
        status = exc.status if isinstance(exc, HttpStatusError) else None
        rejected = status is not None and 400 <= status < 500 and status != 408
        return {
            "ok": False, "applied": False if rejected else None,
            "verification_status": "rejected" if rejected else "outcome_unknown",
            "verification_note": "Check the resource or Azure operation history before retrying.",
            "azure_async_polling": polling, "response_status": status, "response": None,
            "error": sanitize_error_message(exc, redaction_values),
        }

    polling = _poll_azure_async_operation(
        client=client, response=response, headers=headers, redaction_values=redaction_values, request_url=url,
    )
    state = polling["status"]
    status = "limited_verification"
    note = "Azure returned a reply. Read the resource to verify the change."
    applied = True
    if state in {"failed", "canceled", "cancelled"}:
        status = "operation_failed"
        note = "Azure reported that the operation failed or was canceled. Check the resource before retrying."
        applied = False
    elif state in {"pending", "outcome_unknown"}:
        status = state
        note = "Check the Azure operation or resource before reporting completion or retrying."
        applied = None
    return {
        "ok": status not in {"operation_failed", "outcome_unknown"},
        "applied": applied, "verification_status": status, "verification_note": note,
        "azure_async_polling": polling, **_safe_response(response, redaction_values=redaction_values),
    }


def execute_generated_operation(args: Any, ctx: dict[str, Any]) -> int:
    registry = load_registry()
    service_id, operation_name = args.cmd, args.operation
    cfg: Config = ctx["cfg"]
    service, operation = _service_operation(registry, service_id, operation_name)
    input_obj = _load_input_json(args.input_json)
    is_read = operation.get("classification") in READ_CLASSES
    data_plane = operation.get("plane") == "data_plane"
    subscription = _requested_subscription(input_obj) or cfg.subscription_id
    plan_in = str(args.plan_in or "").strip()
    apply = bool(args.apply and not is_read)
    saved = None
    if apply:
        if not plan_in:
            raise SafetyError("Refused: live writes require --plan-in")
        if not args.yes:
            raise SafetyError("Refused: live writes require --apply --yes")
        saved = read_json_file(plan_in)
        if not isinstance(saved, dict) or not isinstance(saved.get("connection"), dict):
            raise SafetyError("Refused: make and review a new plan with --bind-azure.")

    _validate_allowlists(cfg, service_id=service_id, resolved=input_obj)
    if subscription:
        _validate_allowlists(cfg, service_id=service_id, resolved={"subscriptionId": subscription})
    connection = None
    timeout = float(ctx.get("timeout_s") or 30.0)
    if is_read or apply or args.bind_azure:
        connection = resolve_connection(
            cfg, env_file=ctx["env_file"], subscription=subscription, data_plane=data_plane, timeout=timeout,
        )

    resolved = _normalize_input(
        input_obj, path_template=str(operation["path"]), api_version=str(operation["version"]),
        subscription=connection.subscription if connection else subscription,
    )
    _validate_allowlists(cfg, service_id=service_id, resolved=resolved)
    plan = _build_plan(
        tool=ctx["tool"], version=ctx["tool_version"], service_id=service_id, service=service,
        operation_name=operation_name, operation=operation, resolved=resolved, command=ctx["command_str"],
        connection=connection,
    )
    input_values = list(iter_scalar_strings(input_obj))
    plan_safe = _safe_plan(plan, [*input_values, *iter_scalar_strings(resolved["path"])])
    payload = {
        "ok": True, "dry_run": connection is None or not (is_read or apply), "changed": False,
        "service_id": service_id, "operation_name": operation_name,
        "classification": operation["classification"], "risk_categories": plan["risk_categories"],
    }
    if not (is_read or apply):
        payload.update(
            approval_ready=connection is not None, plan=plan_safe,
            plan_out=_write_output_file(args.plan_out or ctx.get("plan_out"), plan_safe),
        )
        if connection is None:
            payload["next_step"] = "Use --bind-azure to prepare a plan for approval."
    else:
        assert connection is not None
        if saved is not None:
            _validate_apply_gates(plan, args)
            _validate_plan_matches(saved, plan_safe)
        url = _build_url(endpoint=connection.endpoint, operation=operation, path_values=resolved["path"])
        values = [*cfg.redaction_values(), *input_values, connection.token]
        client = HttpClient(timeout_s=timeout, verbose=bool(args.verbose), user_agent=f"{ctx['tool']}/{ctx['tool_version']}")
        headers = {"Authorization": f"Bearer {connection.token}", "Accept": "application/json"}
        if is_read:
            sensitive = "sensitive_read" in plan["risk_categories"]
            response = client.request(plan["http_method"], url, headers=headers, params=resolved["query"],
                                      json_body=resolved["body"], retries=3)
            payload.update(sensitive_output_redacted=sensitive,
                           **_safe_response(response, redaction_values=values, sensitive_read=sensitive))
        else:
            result = _write_result(
                client, url=url, headers=headers, plan=plan, resolved=resolved, redaction_values=values,
            )
            receipt = {
                **payload, **result, "tool": ctx["tool"], "version": ctx["tool_version"],
                "generated_at_utc": _utc_now(), "plan_fingerprint": plan["plan_fingerprint"],
                "connection": connection.review_details(), "changed": result["applied"], "verified": False,
            }
            receipt = redact_jsonish_with_values(redact_jsonish(receipt), [connection.token])
            payload.update(
                ok=result["ok"], changed=result["applied"], applied=result["applied"], receipt=receipt,
                receipt_out=_write_output_file(args.receipt_out or ctx.get("receipt_out"), receipt),
            )
    output_path = _write_output_file(args.output_file, payload)
    if output_path:
        payload["output_file"] = output_path
    ctx["out"].emit(payload)
    return 0 if payload["ok"] else 1
