from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

from . import __version__, operations
from .audit_log import AuditLogger, CompositeAuditLogger
from .commands import onboarding as onboarding_cmd
from .config import load_config
from .errors import SafetyError, ToolError, ValidationError
from .http import HttpClient
from .json_files import read_json_file, write_json_file
from .output import Output
from .runs import (
    RunContext,
    append_index_row,
    build_deterministic_summary,
    find_run,
    init_run_context,
    list_runs,
    runs_index_path_for_env_file,
    write_summary_md,
)

_REDACTED = "***REDACTED***"

_PRIVATE_KEYS = {
    "address1",
    "address2",
    "admin",
    "attributes",
    "bankaccount",
    "billing",
    "buyeremail",
    "buyerusername",
    "cardnumber",
    "city",
    "contact",
    "contactid",
    "contacts",
    "country",
    "cvv",
    "email",
    "fax",
    "faxext",
    "firstname",
    "iban",
    "lastname",
    "organization",
    "paymentmethod",
    "phone",
    "phoneext",
    "postalcode",
    "private_contact",
    "privatecontacts",
    "registrant",
    "selleremail",
    "sellerusername",
    "stateprovince",
    "taxnumber",
    "tech",
    "transactionid",
}

_SENSITIVE_PATH_PARAMS = {"contact", "transactionId"}
_SUCCESS_STATUSES = {200, 201, 202, 204}

_QUERY_RULES: dict[str, dict[str, Any]] = {
    "getResourceRecordsList": {
        "take": {"default": 100, "minimum": 1, "maximum": 500},
        "skip": {"default": 0, "minimum": 0, "maximum": 2147483647},
        "orderBy": {"choices": {"type", "-type", "name", "-name"}},
    },
    "getDomainList": {
        "take": {"default": 100, "minimum": 1, "maximum": 100},
        "skip": {"default": 0, "minimum": 0, "maximum": 2147483647},
        "orderBy": {
            "choices": {
                "name",
                "-name",
                "unicodeName",
                "-unicodeName",
                "registrationDate",
                "-registrationDate",
                "expirationDate",
                "-expirationDate",
            }
        },
    },
    "getSellerHubDomainList": {
        "take": {"default": 100, "minimum": 1, "maximum": 100},
        "skip": {"default": 0, "minimum": 0, "maximum": 2147483647},
    },
    "getSoldDomains": {
        "take": {"default": 100, "minimum": 1, "maximum": 100},
    },
    "getSafePayTransactionList": {
        "take": {"default": 100, "minimum": 1, "maximum": 100},
        "skip": {"default": 0, "minimum": 0, "maximum": 2147483647},
    },
}

_OPAQUE_PRIVATE_OPERATIONS = {
    "createCheckoutLink",
    "createSafePayTransaction",
    "getAuthCode",
    "getSafePayTransaction",
    "getSafePayTransactionList",
    "readAttributeDetails",
    "readDetails",
    "saveDetails",
}

_OPAQUE_RESPONSE_KEYS = {"_raw", "body", "detail", "details", "error", "message", "payload", "raw", "response"}


def _status_label(status_code: int) -> str:
    if status_code == 202:
        return "accepted_not_completed"
    if status_code in _SUCCESS_STATUSES:
        return "completed"
    return "failed"


def _redact(payload: Any) -> Any:
    if isinstance(payload, dict):
        out: dict[str, Any] = {}
        for k, v in payload.items():
            key = str(k).lower()
            if key in {
                "authorization",
                "authorizationcode",
                "authorization_code",
                "authcode",
                "password",
                "secret",
                "token",
                "apikey",
                "api_key",
                "x-api-key",
                "x-api-secret",
                "transferauthcode",
                "transfer_auth_code",
                "private_contact",
                "privatecontacts",
                "cardnumber",
                "cvv",
                "iban",
                "bankaccount",
            } or key in _PRIVATE_KEYS or key.endswith("_token") or key.endswith("_secret") or key.endswith("_api_key"):
                out[k] = _REDACTED
            elif "safepay" in key and ("card" in key or "account" in key or "iban" in key or "token" in key):
                out[k] = _REDACTED
            elif "authorization" in key and "code" in key:
                out[k] = _REDACTED
            elif "private" in key and "contact" in key:
                out[k] = _REDACTED
            else:
                out[k] = _redact(v)
        return out
    if isinstance(payload, list):
        return [_redact(x) for x in payload]
    return payload


class _ToolArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


@dataclass(frozen=True)
class _ApiCallResult:
    status_code: int
    payload: Any
    headers: dict[str, str]
    attempts: int
    throttled: bool
    retry_after: int | None


def _to_error_payload(message: str, *, error_type: str = "ToolError", extra: dict[str, Any] | None = None) -> dict[str, Any]:
    base: dict[str, Any] = {"ok": False, "error": message, "error_type": error_type}
    if extra:
        base.update(extra)
    return _redact(base)


def _safe_parse_json_file(path: str | None, *, field: str) -> dict[str, Any]:
    if not path:
        raise ValidationError(f"{field} requires --body-file")
    body = read_json_file(path)
    if not isinstance(body, dict):
        raise ValidationError(f"{field} must be a JSON object")
    return body


_RISK_ACK_MAP: dict[str, str] = {
    "spend": "ack_spend",
    "ownership": "ack_ownership",
    "dns-risk": "ack_dns_risk",
    "financial": "ack_financial",
    "destructive": "ack_destructive",
    "private-data": "ack_private_data",
}


_RISK_CATEGORIES: dict[str, tuple[str, ...]] = {
    # registration, renew, restore
    "domainCreate": ("ownership", "spend"),
    "domainRenew": ("ownership", "spend"),
    "domainRestore": ("ownership", "spend"),
    # transfer
    "transferRequest": ("ownership", "private-data"),
    "updateTransferLock": ("ownership",),
    # contacts / privacy / settings
    "saveDetails": ("private-data",),
    "saveContactAttributes": ("private-data",),
    "setDomainContacts": ("private-data",),
    "updateDomainEmailProtectionPreference": ("private-data",),
    "updateDomainPrivacyPreference": ("private-data",),
    # DNS / nameserver families
    "saveRecords": ("dns-risk",),
    "deleteRecords": ("dns-risk",),
    "setDomainNameservers": ("dns-risk",),
    "getDomainPersonalNameservers": (),
    "updateDomainPersonalNameserverHostInfo": ("dns-risk",),
    "deleteDomainPersonalNameserverHostInfo": ("dns-risk", "destructive"),
    "updateAutorenewal": ("spend",),
    # SellerHub
    "updateSellerHubDomain": ("ownership", "financial"),
    "deleteSellerHubDomain": ("ownership", "financial", "destructive"),
    "createSellerHubDomain": ("ownership", "financial"),
    # checkout / payments
    "createCheckoutLink": ("ownership", "financial"),
    "createSafePayTransaction": ("ownership", "financial", "private-data"),
}

_ACK_NO_SNAPSHOT = "ack_no_snapshot"
_ACK_NO_SNAPSHOT_CLI = "ack-no-snapshot"

_RISK_CATEGORY_ORDER: tuple[str, ...] = (
    "spend",
    "ownership",
    "dns-risk",
    "financial",
    "destructive",
    "private-data",
)

_ACK_FLAG_ORDER: tuple[str, ...] = (
    "ack_spend",
    "ack_ownership",
    "ack_dns_risk",
    "ack_financial",
    "ack_destructive",
    "ack_private_data",
    _ACK_NO_SNAPSHOT,
)


def _ack_flag_display(flag: str) -> str:
    if flag == _ACK_NO_SNAPSHOT:
        return _ACK_NO_SNAPSHOT_CLI
    return flag.replace("_", "-")


def _command_requires_credentials(args: argparse.Namespace) -> bool:
    cmd = str(getattr(args, "cmd", "") or "")
    if cmd in {"runs", "onboarding"}:
        return False
    if cmd == "auth":
        return True
    spec = getattr(args, "spec", None)
    if isinstance(spec, operations.OperationSpec) and not spec.stable:
        return False
    if spec is not None and bool(getattr(args, "write_capable", False)):
        return bool(getattr(args, "apply", False))
    return True


def _canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256_hex(payload: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()


def _display_path_params(path_params: dict[str, str]) -> dict[str, str]:
    displayed: dict[str, str] = {}
    for key, value in path_params.items():
        if key in _SENSITIVE_PATH_PARAMS:
            displayed[key] = f"sha256:{_sha256_hex(value)}"
        else:
            displayed[key] = value
    return displayed


def _persisted_command_display(args: argparse.Namespace, argv: list[str]) -> str:
    spec = getattr(args, "spec", None)
    if not isinstance(spec, operations.OperationSpec):
        return "qwayk-spaceship-safe-agent-cli " + " ".join(argv)
    raw_path_params = {name: str(getattr(args, name)) for name in spec.path_params}
    displayed = _display_path_params(raw_path_params)
    parts = ["qwayk-spaceship-safe-agent-cli", *spec.command]
    parts.extend(displayed[name] for name in spec.path_params)
    return " ".join(parts)


def _build_selector(operation_spec: operations.OperationSpec, path_params: dict[str, str], query: dict[str, Any]) -> dict[str, Any]:
    return {
        "command": ["qwayk-spaceship-safe-agent-cli", *operation_spec.command],
        "path": {"template": operation_spec.path_template, "params": _display_path_params(path_params)},
        "query": query,
    }


def _normalize_query_values(query: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in sorted(query.keys()):
        value = query[key]
        if isinstance(value, str):
            value = str(value).strip()
        out[key] = value
    return out


def _prepare_query_params(spec: operations.OperationSpec, args: Any) -> dict[str, Any]:
    query = _normalize_query_values(
        {
            name: getattr(args, name)
            for name in spec.query_params
            if getattr(args, name, None) is not None
        }
    )
    rules = _QUERY_RULES.get(spec.operation_id, {})
    for name, rule in rules.items():
        if name not in query and "default" in rule:
            query[name] = rule["default"]
        if name not in query:
            continue
        value = query[name]
        if "minimum" in rule or "maximum" in rule:
            try:
                number = int(value)
            except (TypeError, ValueError) as exc:
                raise ValidationError(f"{name} must be an integer") from exc
            minimum = int(rule.get("minimum", number))
            maximum = int(rule.get("maximum", number))
            if number < minimum or number > maximum:
                raise ValidationError(
                    f"{name} must be between {minimum} and {maximum} for {spec.operation_id}"
                )
            query[name] = number
        choices = rule.get("choices")
        if choices and value not in choices:
            allowed = ", ".join(sorted(str(choice) for choice in choices))
            raise ValidationError(f"{name} must be one of: {allowed}")
    return query


def _risk_categories(operation_id: str) -> tuple[str, ...]:
    if operation_id not in _RISK_CATEGORIES:
        return ()
    return _RISK_CATEGORIES[operation_id]


def _operation_is_private(operation_id: str) -> bool:
    return operation_id in _OPAQUE_PRIVATE_OPERATIONS or "private-data" in _risk_categories(operation_id)


def _safe_exception_message(args: argparse.Namespace, error: Exception) -> str:
    spec = getattr(args, "spec", None)
    if isinstance(spec, operations.OperationSpec) and _operation_is_private(spec.operation_id):
        return f"Private operation error redacted; sha256:{_sha256_hex(str(error))}"
    return str(error)


def _required_ack_flags(operation_id: str, *, no_snapshot: bool) -> list[str]:
    flags: list[str] = []
    for category in _risk_categories(operation_id):
        flag = _RISK_ACK_MAP.get(category)
        if flag:
            flags.append(flag)
    if no_snapshot:
        flags.append(_ACK_NO_SNAPSHOT)
    # stable deterministic output order
    deduped: list[str] = []
    for flag in _ACK_FLAG_ORDER:
        if flag in flags and flag not in deduped:
            deduped.append(flag)
    return deduped


def _required_ack_names(operation_id: str, *, no_snapshot: bool) -> list[str]:
    flags = _required_ack_flags(operation_id, no_snapshot=no_snapshot)
    return [_ack_flag_display(flag) for flag in flags]


def _missing_acknowledgments(operation_id: str, args: argparse.Namespace, *, no_snapshot: bool) -> list[str]:
    missing: list[str] = []
    for flag in _required_ack_flags(operation_id, no_snapshot=no_snapshot):
        if not bool(getattr(args, flag, False)):
            missing.append(_ack_flag_display(flag))
    return missing


def _extract_spend_fields(payload: Any) -> dict[str, Any]:
    exposed = _walk_exposed_fields(payload)
    financial_fragments = (
        "amount",
        "availability",
        "available",
        "currency",
        "duration",
        "expiration",
        "fee",
        "price",
        "total",
        "year",
    )
    return {
        key: value
        for key, value in exposed.items()
        if any(fragment in key.lower() for fragment in financial_fragments)
    }


def _walk_exposed_fields(payload: Any, *, prefix: str = "") -> dict[str, Any]:
    wanted_fragments = (
        "amount",
        "availability",
        "available",
        "currency",
        "duration",
        "expiration",
        "fee",
        "price",
        "status",
        "year",
    )
    found: dict[str, Any] = {}
    if isinstance(payload, dict):
        for raw_key, value in payload.items():
            key = str(raw_key)
            path = f"{prefix}.{key}" if prefix else key
            normalized = key.lower()
            if any(fragment in normalized for fragment in wanted_fragments) and not isinstance(value, (dict, list)):
                found[path] = value
            found.update(_walk_exposed_fields(value, prefix=path))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            found.update(_walk_exposed_fields(value, prefix=f"{prefix}[{index}]"))
    return found


def _critical_request_fields(
    operation_id: str,
    path_params: dict[str, str],
    body: dict[str, Any] | None,
) -> dict[str, Any]:
    body = body or {}
    fields: dict[str, Any] = {"target": _display_path_params(path_params)}
    field_names: dict[str, tuple[str, ...]] = {
        "domainCreate": ("years", "autoRenew", "privacyProtection", "contacts"),
        "domainRenew": ("years", "currentExpirationDate"),
        "domainRestore": (),
        "createCheckoutLink": ("domainName", "type", "basePrice", "feePercentageShare"),
        "createSafePayTransaction": (
            "domainName",
            "initiatedBy",
            "basePrice",
            "type",
            "ltoSettings",
            "feePercentageShare",
            "buyerEmail",
            "buyerUsername",
            "sellerEmail",
            "sellerUsername",
            "confirmedBy",
            "paymentMethod",
        ),
    }
    for name in field_names.get(operation_id, ()):
        if name not in body:
            continue
        value = body[name]
        if name.lower() in _PRIVATE_KEYS or name in {
            "buyerEmail",
            "buyerUsername",
            "sellerEmail",
            "sellerUsername",
            "paymentMethod",
            "contacts",
        }:
            fields[name] = f"sha256:{_sha256_hex(value)}"
        else:
            fields[name] = _redact(value)
    return fields


def _redacted_request_body(operation_id: str, body: dict[str, Any] | None) -> Any:
    if body is None:
        return None
    if "private-data" in _risk_categories(operation_id):
        return {"redacted": True, "sha256": _sha256_hex(body)}
    return _redact(body)


def _redact_extra_keys(payload: Any, keys: set[str]) -> Any:
    if isinstance(payload, dict):
        return {
            key: (_REDACTED if str(key).lower() in keys else _redact_extra_keys(value, keys))
            for key, value in payload.items()
        }
    if isinstance(payload, list):
        return [_redact_extra_keys(value, keys) for value in payload]
    return payload


def _contains_opaque_response_key(payload: Any) -> bool:
    if isinstance(payload, dict):
        return any(str(key).lower() in _OPAQUE_RESPONSE_KEYS for key in payload) or any(
            _contains_opaque_response_key(value) for value in payload.values()
        )
    if isinstance(payload, list):
        return any(_contains_opaque_response_key(value) for value in payload)
    return False


def _redact_operation_payload(operation_id: str, payload: Any) -> Any:
    if payload is None:
        return None
    if operation_id in {"readAttributeDetails", "saveContactAttributes"}:
        return {"redacted": True, "sha256": _sha256_hex(payload)}
    if _operation_is_private(operation_id):
        if _contains_opaque_response_key(payload) or not isinstance(payload, (dict, list)):
            return {"redacted": True, "sha256": _sha256_hex(payload)}
    safe = _redact(payload)
    if operation_id == "createCheckoutLink":
        return _redact_extra_keys(safe, {"checkoutlink", "checkouturl", "link", "url"})
    if operation_id in {
        "createSafePayTransaction",
        "getSafePayTransaction",
        "getSafePayTransactionList",
    }:
        return _redact_extra_keys(
            safe,
            {"buyerid", "id", "sellerid", "transactionid", "url"},
        )
    return safe


def _operation_lookup(operation_id: str) -> operations.OperationSpec | None:
    for spec in operations.OFFICIAL_OPERATIONS:
        if spec.operation_id == operation_id:
            return spec
    return None


def _preflight_request(operation_id: str, path_params: dict[str, str], body: dict[str, Any] | None) -> tuple[operations.OperationSpec, dict[str, str], dict[str, Any], bool] | None:
    # returns (operation, path_params, query, snapshot_required)
    if operation_id in {"domainCreate"}:
        spec = _operation_lookup("checkSingleDomainAvailability")
        if spec is None:
            return None
        return spec, {"domain": path_params.get("domain", "")}, {}, True

    if operation_id in {"domainRenew", "domainRestore", "updateAutorenewal", "setDomainContacts", "setDomainNameservers", "updateDomainEmailProtectionPreference", "updateDomainPrivacyPreference"}:
        spec = _operation_lookup("getDomainInfo")
        if spec is None:
            return None
        return spec, {"domain": path_params.get("domain", "")}, {}, True

    if operation_id in {"saveRecords", "deleteRecords"}:
        spec = _operation_lookup("getResourceRecordsList")
        if spec is None:
            return None
        return spec, {"domain": path_params.get("domain", "")}, {}, True

    if operation_id in {"transferRequest", "updateTransferLock"}:
        spec = _operation_lookup("getTransferInfo")
        if spec is None:
            return None
        return spec, {"domain": path_params.get("domain", "")}, {}, True

    if operation_id in {"updateDomainPersonalNameserverHostInfo", "deleteDomainPersonalNameserverHostInfo"}:
        spec = _operation_lookup("getDomainPersonalNameservers")
        if spec is None:
            return None
        return spec, {"domain": path_params.get("domain", "")}, {}, True

    if operation_id in {"updateSellerHubDomain", "deleteSellerHubDomain", "createCheckoutLink", "createSafePayTransaction"}:
        spec = _operation_lookup("getSellerHubDomain")
        if spec is None:
            return None
        domain = ""
        if "domain" in path_params:
            domain = path_params.get("domain", "")
        elif body and isinstance(body.get("domainName"), str):
            domain = str(body["domainName"])
        if not domain:
            return None
        return spec, {"domain": domain}, {}, True

    return None


def _preflight_payload(
    *,
    transport: HttpClient,
    cfg: Any,
    request: tuple[operations.OperationSpec, dict[str, str], dict[str, Any], bool],
    headers: dict[str, str],
) -> tuple[dict[str, Any], str]:
    preflight_spec, preflight_path_params, preflight_query, _ = request
    result = _call_transport(
        transport=transport,
        spec=preflight_spec,
        url=_build_url(cfg.base_url, preflight_spec.path_template, preflight_path_params),
        headers=headers,
        params=preflight_query,
        body=None,
    )
    payload = _redact(result.payload)
    if result.status_code == 429:
        raise SafetyError(f"Preflight rejected by rate limit: {preflight_spec.operation_id}")
    if result.status_code not in _SUCCESS_STATUSES:
        raise SafetyError(f"Preflight failed ({preflight_spec.operation_id}): status {result.status_code}")
    if preflight_spec.method == "GET" and result.status_code in _SUCCESS_STATUSES:
        # capture readback payload for snapshot comparison and redaction
        return payload, _sha256_hex(result.payload)
    return payload, _sha256_hex(result.payload)


def _readback_verification_payload(
    *,
    transport: HttpClient,
    cfg: Any,
    operation_id: str,
    headers: dict[str, str],
    path_params: dict[str, str],
    request_body: dict[str, Any] | None,
    write_response: Any,
) -> tuple[bool, dict[str, Any]]:
    verifyable: dict[str, str] = {
        # conservative list: operations with reliable readback target.
        "saveRecords": "getResourceRecordsList",
        "deleteRecords": "getResourceRecordsList",
        "setDomainContacts": "getDomainInfo",
        "setDomainNameservers": "getDomainInfo",
        "updateDomainEmailProtectionPreference": "getDomainInfo",
        "updateDomainPrivacyPreference": "getDomainInfo",
        "updateAutorenewal": "getDomainInfo",
        "updateTransferLock": "getTransferInfo",
        "updateDomainPersonalNameserverHostInfo": "getDomainPersonalNameservers",
        "deleteDomainPersonalNameserverHostInfo": "getDomainPersonalNameservers",
        "updateSellerHubDomain": "getSellerHubDomain",
        "deleteSellerHubDomain": "getSellerHubDomain",
        "domainRenew": "getDomainInfo",
        "domainRestore": "getDomainInfo",
        "transferRequest": "getTransferInfo",
        "domainCreate": "getDomainInfo",
        "saveDetails": "readDetails",
        "saveContactAttributes": "readAttributeDetails",
        "createSellerHubDomain": "getSellerHubDomain",
        "createSafePayTransaction": "getSafePayTransaction",
    }
    verif_id = verifyable.get(operation_id)
    if not verif_id:
        return False, {"status": "unverified", "reason": "no_reliable_readback_mapping"}
    spec = _operation_lookup(verif_id)
    if spec is None:
        return False, {"status": "unverified", "reason": "missing_verify_operation"}
    body = None
    response_obj = write_response if isinstance(write_response, dict) else {}
    request_obj = request_body or {}
    if operation_id in {"saveDetails", "saveContactAttributes"}:
        contact = str(response_obj.get("contactId") or "").strip()
        if not contact:
            return False, {
                "status": "unverified",
                "reason": "missing_response_contact_id",
            }
        verify_path = {"contact": contact}
    elif operation_id == "createSellerHubDomain":
        domain = str(request_obj.get("name") or "").strip()
        if not domain:
            return False, {
                "status": "unverified",
                "reason": "missing_request_domain_name",
            }
        verify_path = {"domain": domain}
    elif operation_id == "createSafePayTransaction":
        transaction_id = str(response_obj.get("transactionId") or "").strip()
        if not transaction_id:
            return False, {
                "status": "unverified",
                "reason": "missing_response_transaction_id",
            }
        verify_path = {"transactionId": transaction_id}
    else:
        verify_path = {k: v for k, v in path_params.items()}
    result = _call_transport(
        transport=transport,
        spec=spec,
        url=_build_url(cfg.base_url, spec.path_template, verify_path),
        headers=headers,
        params={},
        body=body,
    )
    if operation_id == "deleteSellerHubDomain" and result.status_code == 404:
        return True, {
            "status": "verified_absent",
            "status_code": result.status_code,
            "selector": _build_selector(spec, verify_path, {}),
        }
    if result.status_code == 200:
        return True, {
            "status": "verified",
            "status_code": result.status_code,
            "selector": _build_selector(spec, verify_path, {}),
            "payload": _redact_operation_payload(spec.operation_id, result.payload),
        }
    return False, {"status": "unverified", "status_code": result.status_code, "reason": "readback_failed"}


def _build_url(base_url: str, path_template: str, path_params: dict[str, str]) -> str:
    path = path_template
    for key in tuple(part[1:-1] for part in path_template.split("/") if part.startswith("{") and part.endswith("}")):
        if key not in path_params:
            raise ValidationError(f"Missing path parameter: {key}")
        path = path.replace(f"{{{key}}}", quote(str(path_params[key]), safe=""))
    if "{" in path or "}" in path:
        raise ValidationError("Unresolved path parameter")
    return base_url + path


def _extract_items(payload: Any) -> tuple[list[Any], dict[str, Any]]:
    if isinstance(payload, list):
        return payload, {}
    if not isinstance(payload, dict):
        return [], {}
    for key in ("items", "domains", "records", "transactions", "sellerhubDomains", "data", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            extras = dict(payload)
            extras.pop(key, None)
            return value, extras
    return [], dict(payload)


def _call_transport(
    *,
    transport: HttpClient,
    spec: operations.OperationSpec,
    url: str,
    headers: dict[str, str],
    params: dict[str, Any] | None,
    body: dict[str, Any] | None,
) -> _ApiCallResult:
    resp = transport.request(spec.method, url, headers=headers, params=params, json_body=body)
    try:
        parsed = json.loads(resp.body.decode("utf-8")) if resp.body else None
    except Exception:
        parsed = {"_raw": resp.text()} if resp.body else None
    return _ApiCallResult(
        status_code=resp.status,
        payload=parsed,
        headers=resp.headers,
        attempts=resp.attempts,
        throttled=resp.throttled,
        retry_after=resp.retry_after,
    )


def _run_get_with_pagination(
    *,
    transport: HttpClient,
    spec: operations.OperationSpec,
    cfg_base: str,
    path_params: dict[str, str],
    query: dict[str, Any],
    headers: dict[str, str],
    body: dict[str, Any] | None,
) -> tuple[_ApiCallResult, list[Any], str | None]:
    url = _build_url(cfg_base, spec.path_template, path_params)
    items: list[Any] = []
    next_cursor: str | None = None

    has_cursor = "cursor" in spec.query_params
    has_skip = "skip" in spec.query_params
    take = query.get("take")
    take_int = int(take) if take is not None else None
    operation_take_rule = _QUERY_RULES.get(spec.operation_id, {}).get("take", {})
    page_limit = int(operation_take_rule.get("maximum", 100))

    page = 1
    current_skip = int(query.get("skip") or 0) if has_skip else None
    current_cursor = str(query.get("cursor") or "").strip() or None
    last_result: _ApiCallResult | None = None

    while page <= 10:
        page += 1
        page_take = page_limit
        if take_int is not None and take_int > 0:
            remaining = max(0, take_int - len(items))
            page_take = max(1, min(page_take, remaining))
        page_params: dict[str, Any] = dict(query)
        if has_skip and current_skip is not None:
            page_params["skip"] = current_skip
            page_params["take"] = page_take
        if has_cursor and current_cursor:
            page_params["cursor"] = current_cursor
        if "take" in query and has_skip and "take" not in page_params:
            page_params["take"] = page_take
        if "orderBy" in query:
            page_params["orderBy"] = query["orderBy"]

        result = _call_transport(
            transport=transport,
            spec=spec,
            url=url,
            headers=headers,
            params=page_params,
            body=body,
        )
        if result.status_code not in _SUCCESS_STATUSES:
            return result, items, current_cursor
        if result.status_code == 202:
            # accepted_no_completed means no list semantics for us.
            last_result = result
            break

        last_result = result
        data_items, extras = _extract_items(result.payload)
        items.extend(data_items)

        if has_cursor and isinstance(extras.get("cursor"), str) and extras["cursor"]:
            current_cursor = str(extras["cursor"])
            next_cursor = current_cursor
            if take_int is not None and len(items) >= take_int:
                break
            continue
        if take_int is not None and len(items) >= take_int:
            break
        if has_skip and isinstance(extras.get("nextSkip"), int):
            if isinstance(current_skip, int):
                current_skip = extras["nextSkip"]
                continue
        if has_skip and isinstance(current_skip, int):
            if not data_items:
                break
            current_skip = current_skip + len(data_items)
            continue
        break
    if last_result is None:
        raise ToolError("No response from API request")
    return last_result, items, next_cursor


def _run_operation(
    spec: operations.OperationSpec,
    *,
    cfg,
    args: Any,
    transport: Any,
    out: Output,
    ctx: dict[str, Any] | None = None,
) -> int:
    has_credentials = bool(cfg.api_key) and bool(cfg.api_secret)
    effective_plan_out = getattr(args, "plan_out", None) or (ctx or {}).get("plan_out")
    effective_receipt_out = getattr(args, "receipt_out", None) or (ctx or {}).get("receipt_out")

    if not spec.stable:
        out.emit(
            _redact(
                {
                    "ok": True,
                    "operation_id": spec.operation_id,
                    "refused": True,
                    "refusal_type": "UnavailableOperation",
                    "reasons": [f"{spec.operation_id} is a local HTTP-501 operation"],
                    "status_code": 501,
                    "dry_run": True,
                }
            )
        )
        return 0

    path_params = {p: str(getattr(args, p)) for p in spec.path_params}
    query_params = _prepare_query_params(spec, args)
    body = None
    if spec.body or spec.read_like:
        body = _safe_parse_json_file(getattr(args, "body_file", None), field=spec.operation_id)

    is_write = spec.method != "GET" and not spec.read_like
    apply = bool(getattr(args, "apply", False))
    yes = bool(getattr(args, "yes", False))
    command_name = f"qwayk-spaceship-safe-agent-cli {' '.join(spec.command)}"
    headers = {
        "X-API-Key": cfg.api_key,
        "X-API-Secret": cfg.api_secret,
    }

    if spec.read_like:
        disallowed_read_flags = {
            "--apply": apply,
            "--yes": yes,
            "--plan-in": bool(getattr(args, "plan_in", None)),
            "--plan-out": bool(getattr(args, "plan_out", None)),
            "--receipt-out": bool(getattr(args, "receipt_out", None)),
        }
        used = [flag for flag, enabled in disallowed_read_flags.items() if enabled]
        if used:
            raise ValidationError(
                f"{spec.operation_id} is an authenticated read-like command and does not accept write flags: "
                + ", ".join(used)
            )

    if apply:
        if not has_credentials:
            raise SafetyError("Apply requires SPACESHIP_API_KEY and SPACESHIP_API_SECRET")
        if not bool(getattr(args, "plan_in", None)):
            out.emit(
                _redact(
                    {
                        "ok": True,
                        "dry_run": False,
                        "refused": True,
                        "reasons": ["Apply requires --plan-in"],
                        "refusal_type": "SafetyError",
                        "operation_id": spec.operation_id,
                        "command": command_name,
                        "status_label": "refused",
                    }
                )
            )
            return 0
        if not yes:
            out.emit(
                _redact(
                    {
                        "ok": True,
                        "dry_run": False,
                        "refused": True,
                        "reasons": ["Apply requires --yes"],
                        "refusal_type": "SafetyError",
                        "operation_id": spec.operation_id,
                        "command": command_name,
                        "status_label": "refused",
                    }
                )
            )
            return 0

    if not is_write:
        if spec.method == "GET" and any(q in spec.query_params for q in ("take", "skip", "cursor")):
            result, items, next_cursor = _run_get_with_pagination(
                transport=transport,
                spec=spec,
                cfg_base=cfg.base_url,
                path_params=path_params,
                query=query_params,
                headers=headers,
                body=body,
            )
            payload: dict[str, Any] = {
                "ok": result.status_code in _SUCCESS_STATUSES,
                "operation_id": spec.operation_id,
                "command": command_name,
                "method": spec.method,
                "status_code": result.status_code,
                "async_operation_id": result.headers.get("spaceship-async-operationid"),
                "result": {"items": items, "count": len(items)},
                "status_label": _status_label(result.status_code),
                "rate_limited": result.throttled,
                "attempts": result.attempts,
                "rate_retry_after_seconds": result.retry_after,
            }
            if next_cursor:
                payload["cursor"] = next_cursor
            if result.status_code == 429:
                payload["ok"] = False
                payload["error_type"] = "RateLimit"
                payload["error"] = "rate_limit"
                out.emit(_redact(payload))
                return 1
            if result.status_code not in _SUCCESS_STATUSES:
                payload["ok"] = False
                payload["error_type"] = "RequestError"
                payload["error"] = _redact_operation_payload(spec.operation_id, result.payload)
                out.emit(payload)
                return 1
            out.emit(_redact(payload))
            return 0

        result = _call_transport(
            transport=transport,
            spec=spec,
            url=_build_url(cfg.base_url, spec.path_template, path_params),
            headers=headers,
            params=query_params,
            body=body,
        )

        payload = {
            "ok": result.status_code in _SUCCESS_STATUSES,
            "operation_id": spec.operation_id,
            "command": command_name,
            "method": spec.method,
            "status_code": result.status_code,
            "status_label": _status_label(result.status_code),
            "async_operation_id": result.headers.get("spaceship-async-operationid"),
            "result": _redact_operation_payload(spec.operation_id, result.payload),
            "rate_limited": result.throttled,
            "attempts": result.attempts,
            "rate_retry_after_seconds": result.retry_after,
        }
        if result.status_code == 429:
            payload["ok"] = False
            payload["error_type"] = "RateLimit"
            payload["error"] = "rate_limit"
            out.emit(_redact(payload))
            return 1
        if result.status_code not in _SUCCESS_STATUSES:
            payload["ok"] = False
            payload["error_type"] = "RequestError"
            payload["error"] = _redact_operation_payload(spec.operation_id, result.payload)
            out.emit(payload)
            return 1

        out.emit(_redact(payload))
        return 0

    # write-like branch
    risk_categories = list(_risk_categories(spec.operation_id))
    preflight = _preflight_request(spec.operation_id, path_params, body)

    preflight_payload: dict[str, Any] | None = None
    preflight_digest: str | None = None
    preflight_financial: dict[str, Any] | None = None
    preflight_metadata: dict[str, Any] = {
        "used": False,
    }

    if preflight is not None and has_credentials and not apply:
        preflight_spec, preflight_path_params, preflight_query, preflight_snapshot_enabled = preflight
        preflight_metadata["used"] = True
        preflight_metadata["operation_id"] = preflight_spec.operation_id
        preflight_metadata["path_template"] = preflight_spec.path_template
        preflight_metadata["path_params"] = _display_path_params(preflight_path_params)
        preflight_metadata["query"] = preflight_query
        if not apply:
            try:
                preflight_payload, preflight_digest = _preflight_payload(
                    transport=transport,
                    cfg=cfg,
                    request=(preflight_spec, preflight_path_params, preflight_query, preflight_snapshot_enabled),
                    headers=headers,
                )
                preflight_metadata["snapshot_digest"] = preflight_digest
                preflight_metadata["payload_redacted"] = _redact(preflight_payload)
                preflight_metadata["exposed_fields"] = _walk_exposed_fields(preflight_payload)
                if any(c in risk_categories for c in ("spend", "financial")):
                    preflight_financial = _extract_spend_fields(preflight_payload)
            except SafetyError as e:
                preflight_metadata["error"] = str(e)

    no_snapshot = preflight is None or not bool(preflight[3] if preflight else True)
    if not apply:
        no_snapshot = no_snapshot or preflight_payload is None
        if not has_credentials:
            no_snapshot = True
    needs_financial_recheck = any(c in risk_categories for c in ("spend", "financial"))
    provider_cannot_recheck_full_financial_terms = spec.operation_id in {
        "domainRenew",
        "domainRestore",
        "createCheckoutLink",
        "createSafePayTransaction",
    }
    financial_recheck_available = (
        bool(preflight_financial) and not provider_cannot_recheck_full_financial_terms
        if needs_financial_recheck
        else True
    )
    no_reliable_recheck = needs_financial_recheck and not financial_recheck_available
    requires_no_snapshot_ack = no_snapshot or no_reliable_recheck
    required_ack_flags = _required_ack_names(
        spec.operation_id,
        no_snapshot=requires_no_snapshot_ack,
    )
    body_sha256 = _sha256_hex(body) if body is not None else None
    critical_request_fields = _critical_request_fields(spec.operation_id, path_params, body)

    plan_base: dict[str, Any] = {
        "ok": True,
        "dry_run": True,
        "plan_kind": "deterministic_only",
        "tool": "qwayk-spaceship-safe-agent-cli",
        "version": __version__,
        "operation_id": spec.operation_id,
        "command": command_name,
        "env_fingerprint": cfg.base_url,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "method": spec.method,
        "path_template": spec.path_template,
        "selector": _build_selector(spec, path_params, query_params),
        "path_params": _display_path_params(path_params),
        "query": query_params,
        "body_sha256": body_sha256,
        "redacted_body": _redacted_request_body(spec.operation_id, body),
        "critical_request_fields": critical_request_fields,
        "risk_categories": risk_categories,
        "required_acknowledgements": required_ack_flags,
        "snapshot": {
            "available": not no_snapshot,
            "preflight": preflight_metadata,
            "preflight_financial_fields": preflight_financial,
        },
        "financial_recheck": {
            "required": needs_financial_recheck,
            "available": financial_recheck_available,
            "fields": preflight_financial,
            "warning": (
                "The official API exposes no reliable amount, currency, or fee recheck for this operation. "
                "Review the exact request fields and use --ack-no-snapshot before apply."
                if no_reliable_recheck
                else None
            ),
        },
        "no_snapshot_warning": (
            "No reliable state snapshot or required financial recheck is available; this write requires --ack-no-snapshot"
            if requires_no_snapshot_ack
            else None
        ),
    }
    plan_base["plan_integrity"] = _sha256_hex({k: v for k, v in plan_base.items() if k != "plan_integrity"})

    if not apply:
        plan_path = None
        if effective_plan_out:
            plan_path = write_json_file(effective_plan_out, plan_base)
        plan_base["plan_path"] = plan_path
        out.emit(_redact(plan_base))
        return 0

    try:
        plan_in_obj = read_json_file(args.plan_in)
        if not isinstance(plan_in_obj, dict):
            raise ValidationError("Plan file must be a JSON object")

        if plan_in_obj.get("operation_id") != spec.operation_id:
            raise SafetyError("Refused: plan operation_id does not match current command")
        if plan_in_obj.get("command") != command_name:
            raise SafetyError("Refused: plan command does not match current command")
        if _normalize_query_values(plan_in_obj.get("query") or {}) != query_params:
            raise SafetyError("Refused: query mismatch")
        if plan_in_obj.get("path_params") != _display_path_params(path_params):
            raise SafetyError("Refused: path parameter mismatch")
        if plan_in_obj.get("body_sha256") != body_sha256:
            raise SafetyError("Refused: body SHA-256 mismatch")
        if plan_in_obj.get("selector") != _build_selector(spec, path_params, query_params):
            raise SafetyError("Refused: selector mismatch")
        if plan_in_obj.get("critical_request_fields") != critical_request_fields:
            raise SafetyError("Refused: critical request fields mismatch")

        if isinstance(plan_in_obj.get("snapshot"), dict):
            plan_snapshot = plan_in_obj["snapshot"]
            if isinstance(plan_snapshot, dict):
                no_snapshot = bool(preflight is None or not bool(preflight[3] if preflight else True) or not bool(plan_snapshot.get("available")))

        plan_financial_recheck = plan_in_obj.get("financial_recheck")
        if isinstance(plan_financial_recheck, dict):
            no_reliable_recheck = bool(plan_financial_recheck.get("required")) and not bool(
                plan_financial_recheck.get("available")
            )
        requires_no_snapshot_ack = no_snapshot or no_reliable_recheck

        missing_ack = _missing_acknowledgments(
            spec.operation_id,
            args,
            no_snapshot=requires_no_snapshot_ack,
        )
        if missing_ack:
            raise SafetyError(f"Refused: missing required acknowledgments: {', '.join(missing_ack)}")

        if preflight is not None:
            preflight_spec, preflight_path_params, preflight_query, preflight_snapshot_enabled = preflight
            current_preflight_payload, current_preflight_digest = _preflight_payload(
                transport=transport,
                cfg=cfg,
                request=(preflight_spec, preflight_path_params, preflight_query, preflight_snapshot_enabled),
                headers=headers,
            )
            preflight_payload = current_preflight_payload
            preflight_digest = current_preflight_digest
            snapshot_block = plan_in_obj.get("snapshot")
            if not isinstance(snapshot_block, dict):
                raise SafetyError("Refused: plan snapshot missing for drift check")
            preflight_block = snapshot_block.get("preflight")
            if not isinstance(preflight_block, dict):
                raise SafetyError("Refused: plan preflight data missing")
            if not no_snapshot:
                plan_snapshot_digest = preflight_block.get("snapshot_digest")
                if not plan_snapshot_digest:
                    raise SafetyError("Refused: plan snapshot digest missing")
                if str(plan_snapshot_digest) != str(current_preflight_digest):
                    raise SafetyError("Refused: snapshot preflight digest drift detected")

            previous_exposed = preflight_block.get("exposed_fields") or {}
            current_exposed = _walk_exposed_fields(current_preflight_payload)
            if previous_exposed and current_exposed != previous_exposed:
                raise SafetyError("Refused: exposed preflight fields changed")

            if any(c in risk_categories for c in ("spend", "financial")):
                preflight_financial = _extract_spend_fields(current_preflight_payload)
                previous_financial = snapshot_block.get("preflight_financial_fields") or {}
                current_financial = _extract_spend_fields(current_preflight_payload)
                if previous_financial and current_financial != previous_financial:
                    raise SafetyError("Refused: spend or financial preflight values changed")

        if str(plan_in_obj.get("plan_integrity") or "") != str(_sha256_hex({k: v for k, v in plan_in_obj.items() if k != "plan_integrity"})):
            raise SafetyError("Refused: plan integrity mismatch")

        result = _call_transport(
            transport=transport,
            spec=spec,
            url=_build_url(cfg.base_url, spec.path_template, path_params),
            headers=headers,
            params=query_params,
            body=body,
        )

        if result.status_code == 429:
            payload = {
                "ok": False,
                "operation_id": spec.operation_id,
                "command": command_name,
                "method": spec.method,
                "status_code": result.status_code,
                "status_label": _status_label(result.status_code),
                "async_operation_id": result.headers.get("spaceship-async-operationid"),
                "result": _redact_operation_payload(spec.operation_id, result.payload),
                "rate_limited": result.throttled,
                "attempts": result.attempts,
                "rate_retry_after_seconds": result.retry_after,
                "error_type": "RateLimit",
                "error": "rate_limit",
                "dry_run": False,
            }
            out.emit(_redact(payload))
            if effective_receipt_out:
                write_json_file(
                    effective_receipt_out,
                    {
                        "ok": False,
                        "dry_run": False,
                        "refused": False,
                        "operation_id": spec.operation_id,
                        "command": command_name,
                        "status_code": result.status_code,
                        "status_label": payload["status_label"],
                        "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "result": _redact_operation_payload(spec.operation_id, result.payload),
                        "verification": {"status": "unverified", "reason": "rate_limit"},
                    },
                )
            return 1

        if result.status_code not in _SUCCESS_STATUSES:
            payload = {
                "ok": False,
                "operation_id": spec.operation_id,
                "command": command_name,
                "method": spec.method,
                "status_code": result.status_code,
                "status_label": _status_label(result.status_code),
                "async_operation_id": result.headers.get("spaceship-async-operationid"),
                "result": _redact_operation_payload(spec.operation_id, result.payload),
                "rate_limited": result.throttled,
                "attempts": result.attempts,
                "rate_retry_after_seconds": result.retry_after,
                "error_type": "RequestError",
                "error": _redact_operation_payload(spec.operation_id, result.payload),
                "dry_run": False,
            }
            out.emit(_redact(payload))
            if effective_receipt_out:
                write_json_file(
                    effective_receipt_out,
                    {
                        "ok": False,
                        "dry_run": False,
                        "refused": False,
                        "operation_id": spec.operation_id,
                        "command": command_name,
                        "status_code": result.status_code,
                        "status_label": payload["status_label"],
                        "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "result": _redact_operation_payload(spec.operation_id, result.payload),
                        "verification": {"status": "unverified", "reason": "write_failed"},
                    },
                )
            return 1

        if result.status_code == 202:
            verification_status = "accepted_not_completed"
            verification = {
                "status": verification_status,
                "status_code": result.status_code,
                "details": "Async provider operation accepted; verification deferred",
                "async_operation_id": result.headers.get("spaceship-async-operationid"),
            }
            verified = False
        else:
            verified, verification = _readback_verification_payload(
                transport=transport,
                cfg=cfg,
                operation_id=spec.operation_id,
                headers=headers,
                path_params=path_params,
                request_body=body,
                write_response=result.payload,
            )
            verification_status = "verified" if verified else "unverified"

        receipt = {
            "ok": True,
            "dry_run": False,
            "refused": False,
            "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "operation_id": spec.operation_id,
            "command": command_name,
            "selector": plan_base["selector"],
            "plan_integrity": plan_in_obj.get("plan_integrity"),
            "request_body_sha256": body_sha256,
            "request_body": _redacted_request_body(spec.operation_id, body),
            "preflight": {
                "operation_id": (preflight[0].operation_id if preflight else None),
                "payload_redacted": preflight_payload,
                "preflight_financial_fields": preflight_financial,
            },
            "transport": {
                "status_code": result.status_code,
                "status_label": _status_label(result.status_code),
                "attempts": result.attempts,
                "rate_limited": result.throttled,
                "retry_after": result.retry_after,
                "async_operation_id": result.headers.get("spaceship-async-operationid"),
            },
            "verification": _redact(verification),
        }

        output_payload = {
            "ok": True,
            "refused": False,
            "operation_id": spec.operation_id,
            "command": command_name,
            "method": spec.method,
            "status_code": result.status_code,
            "status_label": _status_label(result.status_code),
            "async_operation_id": result.headers.get("spaceship-async-operationid"),
            "result": _redact_operation_payload(spec.operation_id, result.payload),
            "rate_limited": result.throttled,
            "attempts": result.attempts,
            "rate_retry_after_seconds": result.retry_after,
            "dry_run": False,
            "verification": _redact(verification),
            "verification_status": verification_status,
            "receipt": receipt,
        }
        if effective_receipt_out:
            write_json_file(effective_receipt_out, _redact(receipt))
        out.emit(_redact(output_payload))
        return 0
    except SafetyError as e:
        refusal = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "refusal_type": "SafetyError",
            "reasons": [str(e)],
            "operation_id": spec.operation_id,
            "command": command_name,
            "status_label": "refused",
        }
        if effective_receipt_out:
            write_json_file(
                effective_receipt_out,
                {
                    "ok": False,
                    "dry_run": False,
                    "refused": True,
                    "reasons": [str(e)],
                    "operation_id": spec.operation_id,
                    "command": command_name,
                    "refused_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                },
            )
        out.emit(_redact(refusal))
        return 0
    except ValidationError as e:
        refusal = {
            "ok": False,
            "dry_run": False,
            "refused": True,
            "refusal_type": "ValidationError",
            "reasons": [str(e)],
            "operation_id": spec.operation_id,
            "command": command_name,
            "status_label": "refused",
        }
        if effective_receipt_out:
            write_json_file(effective_receipt_out, _redact(refusal))
        out.emit(_redact(refusal))
        return 1


def _cmd_api_call(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    spec = args.spec
    cfg = ctx["cfg"]
    transport = ctx["transport"]
    return _run_operation(spec, cfg=cfg, args=args, transport=transport, out=ctx["out"], ctx=ctx)


def _cmd_runs_list(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    runs_index = ctx.get("runs_index_path")
    if not runs_index:
        ctx["out"].emit({"ok": True, "runs": [], "count": 0})
        return 0
    rows = list_runs(runs_index, limit=int(getattr(args, "limit", 20) or 20))
    ctx["out"].emit({"ok": True, "runs": rows, "count": len(rows)})
    return 0


def _cmd_runs_show(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    rid = str(getattr(args, "run_id", "") or "").strip()
    if not rid:
        ctx["out"].emit({"ok": False, "error": "Missing --run-id", "error_type": "ValidationError"})
        return 1
    runs_index = ctx.get("runs_index_path")
    if not runs_index or not runs_index.exists():
        ctx["out"].emit({"ok": False, "error": "No runs index found", "error_type": "NotFound"})
        return 1
    row = find_run(runs_index, run_id=rid)
    if not row:
        ctx["out"].emit({"ok": False, "error": f"Run not found: {rid}", "error_type": "NotFound"})
        return 1
    summary = None
    try:
        ad = row.get("artifacts_dir")
        if isinstance(ad, str) and ad:
            p = (Path(ad) / "summary.md")
            if p.exists():
                summary = p.read_text(encoding="utf-8")
    except Exception:
        summary = None
    ctx["out"].emit({"ok": True, "run": row, "summary_md": summary})
    return 0


def _cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    ctx["out"].emit(
        _redact(
            {
                "ok": True,
                "auth": "configured",
                "base_url": cfg.base_url,
            }
        )
    )
    return 0


def _register_api_parsers(operations_parent: argparse._SubParsersAction) -> None:
    parser_cache: dict[tuple[str, ...], argparse.ArgumentParser] = {}
    subparsers_cache: dict[tuple[str, ...], argparse._SubParsersAction] = {(): operations_parent}

    for spec in operations.OFFICIAL_OPERATIONS:
        node: tuple[str, ...] = ()
        for i, part in enumerate(spec.command):
            is_leaf = i == len(spec.command) - 1
            parent = subparsers_cache[node]
            current = node + (part,)
            parser = parser_cache.get(current)
            if parser is None:
                help_text = spec.help_text if is_leaf else f"{part.replace('-', ' ').title()} commands"
                parser = parent.add_parser(part, help=help_text)
                parser_cache[current] = parser
                if not is_leaf:
                    subparsers_cache[current] = parser.add_subparsers(
                        dest=f"cmd_{len(node)}",
                        required=True,
                        parser_class=_ToolArgumentParser,
                    )
            if is_leaf:
                for path_param in spec.path_params:
                    parser.add_argument(path_param)
                for q in spec.query_params:
                    if q == "orderBy":
                        parser.add_argument("--order-by", dest="orderBy")
                    elif q == "saleDateTimeFrom":
                        parser.add_argument("--sale-date-time-from", dest="saleDateTimeFrom")
                    elif q == "saleDateTimeTo":
                        parser.add_argument("--sale-date-time-to", dest="saleDateTimeTo")
                    elif q in {"take", "skip"}:
                        parser.add_argument(f"--{q}", type=int)
                    else:
                        parser.add_argument(f"--{q}")
                if spec.body or spec.read_like:
                    parser.add_argument("--body-file", required=True, help="Path to body JSON file")
                parser.set_defaults(
                    spec=spec,
                    write_capable=spec.method != "GET" and not spec.read_like,
                    func=_cmd_api_call,
                )
            node = current


def _build_parser() -> argparse.ArgumentParser:
    p = _ToolArgumentParser(prog="qwayk-spaceship-safe-agent-cli")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    p.add_argument("--debug", action="store_true", help="Show stack traces on errors")
    p.add_argument("--output", choices=("json", "text"), default="json", help="Output format")
    p.add_argument("--log-file", default=None, help="Optional audit log path (JSONL)")
    p.add_argument("--run-id", default=None, help="Optional run id (local history)")
    p.add_argument("--artifacts-dir", default=None, help="Optional artifacts directory")
    p.add_argument("--no-artifacts", action="store_true", help="Disable run artifacts")
    p.add_argument("--plan-out", default=None, help="Write dry-run plan JSON")
    p.add_argument("--apply", action="store_true", help="Apply confirmation flag")
    p.add_argument("--yes", action="store_true", help="Additional confirmation flag")
    p.add_argument("--plan-in", default=None, help="Apply from existing plan JSON")
    p.add_argument("--receipt-out", default=None, help="Write apply receipt JSON")
    p.add_argument("--ack-spend", action="store_true", help="Acknowledge spend/cost side effects")
    p.add_argument("--ack-ownership", action="store_true", help="Acknowledge ownership change side effects")
    p.add_argument("--ack-dns-risk", action="store_true", help="Acknowledge DNS-risk side effects")
    p.add_argument("--ack-financial", action="store_true", help="Acknowledge financial side effects")
    p.add_argument("--ack-destructive", action="store_true", help="Acknowledge destructive side effects")
    p.add_argument("--ack-private-data", action="store_true", help="Acknowledge private-data handling")
    p.add_argument("--ack-no-snapshot", action="store_true", help="Acknowledge no reliable snapshot is available")

    sub = p.add_subparsers(dest="cmd", required=False, parser_class=_ToolArgumentParser)

    runs = sub.add_parser("runs", help="Run history")
    runs_sub = runs.add_subparsers(dest="runs_cmd", required=True, parser_class=_ToolArgumentParser)
    runs_list = runs_sub.add_parser("list", help="List recent runs")
    runs_list.add_argument("--limit", type=int, default=20, help="Max runs to return")
    runs_list.set_defaults(func=_cmd_runs_list, write_capable=False)
    runs_show = runs_sub.add_parser("show", help="Show a run")
    runs_show.add_argument("--run-id", required=True)
    runs_show.set_defaults(func=_cmd_runs_show, write_capable=False)

    onboarding = sub.add_parser("onboarding", help="Create setup files and show required env keys")
    onboarding.add_argument("--no-write-env", action="store_true", help="Only show instructions")
    onboarding.set_defaults(func=onboarding_cmd.cmd_onboarding, write_capable=False)

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Validate local config")
    auth_check.set_defaults(func=_cmd_auth_check, write_capable=False)

    _register_api_parsers(sub)
    return p


def _output_mode_from_argv(argv: list[str]) -> str:
    try:
        idx = argv.index("--output")
    except ValueError:
        return "json"
    if idx + 1 >= len(argv):
        return "json"
    value = str(argv[idx + 1] or "").strip()
    return value if value in {"json", "text"} else "json"


def _finalize_run_artifacts(
    *,
    run_ctx: RunContext,
    tool: str,
    version: str,
    command: str | None,
    env_fingerprint: str | None,
    output_obj: dict | None,
    audit_log_path: str | None,
    audit_log_global_path: str | None,
    apply: bool | None,
    yes: bool | None,
) -> None:
    if not run_ctx.enabled or not run_ctx.artifacts_dir or not run_ctx.runs_index_path or not run_ctx.run_id:
        return
    plan_file = run_ctx.artifacts_dir / "plan.json"
    receipt_file = run_ctx.artifacts_dir / "receipt.json"
    append_index_row(
        run_ctx.runs_index_path,
        {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "run_id": run_ctx.run_id,
            "artifacts_dir": str(run_ctx.artifacts_dir),
            "tool": tool,
            "version": version,
            "command": command,
            "env_fingerprint": env_fingerprint,
            "dry_run": bool(output_obj.get("dry_run")) if isinstance(output_obj, dict) else None,
            "apply": apply,
            "yes": yes,
            "ok": bool(output_obj.get("ok")) if isinstance(output_obj, dict) else None,
            "refused": bool(output_obj.get("refused")) if isinstance(output_obj, dict) else False,
            "plan_path": str(plan_file) if plan_file.exists() else None,
            "receipt_path": str(receipt_file) if receipt_file.exists() else None,
            "audit_log": audit_log_path,
            "audit_log_global": audit_log_global_path,
        },
    )
    summary = build_deterministic_summary(
        tool=tool,
        version=version,
        run_id=run_ctx.run_id,
        env_fingerprint=env_fingerprint,
        command=command,
        output_obj=output_obj,
        plan_path=str(plan_file) if plan_file.exists() else None,
        receipt_path=str(receipt_file) if receipt_file.exists() else None,
        audit_log_path=audit_log_path,
        audit_log_global_path=audit_log_global_path,
        runs_index_path=str(run_ctx.runs_index_path),
    )
    write_summary_md(path=run_ctx.artifacts_dir / "summary.md", lines=summary)


def main(argv: list[str]) -> int:
    parser = _build_parser()
    out = Output(mode=_output_mode_from_argv(argv))

    try:
        args = parser.parse_args(argv)
    except ValidationError as e:
        out.emit(_to_error_payload(str(e), error_type="ValidationError"))
        return 1
    except SystemExit as e:
        try:
            return int(e.code or 0)
        except Exception:
            return 0

    write_capable = bool(getattr(args, "write_capable", False))
    try:
        run_ctx = init_run_context(
            env_file=str(args.env_file),
            enabled=write_capable,
            run_id=str(args.run_id) if args.run_id is not None else None,
            artifacts_dir=str(args.artifacts_dir) if args.artifacts_dir else None,
            no_artifacts=bool(args.no_artifacts),
        )
    except ValidationError as e:
        out.emit(_to_error_payload(str(e), error_type="ValidationError"))
        return 1
    run_audit_log_path = str(run_ctx.audit_log_path) if (run_ctx.enabled and run_ctx.audit_log_path) else None
    global_audit_log_path = str(args.log_file) if args.log_file else None
    runs_index_path = runs_index_path_for_env_file(str(args.env_file))

    loggers: list[AuditLogger] = []
    if run_audit_log_path:
        loggers.append(AuditLogger(path=run_audit_log_path, enabled=True))
    if global_audit_log_path:
        loggers.append(AuditLogger(path=global_audit_log_path, enabled=True))
    audit = CompositeAuditLogger(loggers) if len(loggers) > 1 else (loggers[0] if loggers else AuditLogger(path=None, enabled=False))

    if str(getattr(args, "cmd", "") or "") == "runs":
        run_ctx = RunContext(
            enabled=False,
            run_id=None,
            artifacts_dir=None,
            runs_index_path=runs_index_path,
            audit_log_path=None,
        )

    out.set_provenance(
        {
            "run_id": run_ctx.run_id,
            "artifacts_dir": str(run_ctx.artifacts_dir) if run_ctx.artifacts_dir else None,
            "runs_index": str(run_ctx.runs_index_path) if run_ctx.runs_index_path else str(runs_index_path),
            "audit_log": run_audit_log_path or global_audit_log_path,
            "audit_log_global": global_audit_log_path,
        }
    )

    command_str = _persisted_command_display(args, argv)
    audit_spec = getattr(args, "spec", None)
    audit_operation_id = (
        audit_spec.operation_id if isinstance(audit_spec, operations.OperationSpec) else None
    )
    audit.bind_context(
        {
            "tool": "qwayk-spaceship-safe-agent-cli",
            "version": __version__,
            "run_id": run_ctx.run_id,
            "command": command_str,
            "operation_id": audit_operation_id,
            "private_data": bool(
                audit_operation_id and _operation_is_private(audit_operation_id)
            ),
            "apply": bool(args.apply),
            "yes": bool(args.yes),
        }
    )

    try:
        if bool(args.version):
            out.emit({"ok": True, "tool": "qwayk-spaceship-safe-agent-cli", "version": __version__})
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        requires_credentials = _command_requires_credentials(args)
        cfg = load_config(args.env_file, require_credentials=requires_credentials)
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s

        if str(getattr(args, "cmd", "") or "") in {"runs", "onboarding"}:
            ctx = {
                "cfg": cfg,
                "out": out,
                "audit": audit,
                "transport": None,
                "tool": "qwayk-spaceship-safe-agent-cli",
                "tool_version": __version__,
                "command_str": command_str,
                "env_file": str(args.env_file),
                "timeout_s": None,
                "verbose": bool(args.verbose),
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "plan_out": args.plan_out,
                "plan_in": args.plan_in,
                "receipt_out": args.receipt_out,
                "run_id": run_ctx.run_id,
                "artifacts_dir": run_ctx.artifacts_dir,
                "runs_index_path": runs_index_path,
            }
            rc = int(args.func(args, ctx))
            return rc

        if str(getattr(args, "cmd", "") or "") == "auth":
            ctx = {
                "cfg": cfg,
                "out": out,
                "audit": audit,
                "transport": HttpClient(timeout_s=cfg.timeout_s, verbose=bool(args.verbose), user_agent=f"qwayk-spaceship-safe-agent-cli/{__version__}"),
                "tool": "qwayk-spaceship-safe-agent-cli",
                "tool_version": __version__,
                "command_str": command_str,
                "env_file": str(args.env_file),
                "timeout_s": cfg.timeout_s,
                "verbose": bool(args.verbose),
                "apply": bool(args.apply),
                "yes": bool(args.yes),
                "plan_out": args.plan_out,
                "plan_in": args.plan_in,
                "receipt_out": args.receipt_out,
                "run_id": run_ctx.run_id,
                "artifacts_dir": run_ctx.artifacts_dir,
                "runs_index_path": run_ctx.runs_index_path,
                "audit_log_path": run_audit_log_path or global_audit_log_path,
                "audit_log_run_path": run_audit_log_path,
                "audit_log_global_path": global_audit_log_path,
            }
            rc = int(args.func(args, ctx))
            return rc

        transport = HttpClient(timeout_s=timeout_s, verbose=bool(args.verbose), user_agent=f"qwayk-spaceship-safe-agent-cli/{__version__}")
        ctx = {
            "cfg": cfg,
            "out": out,
            "audit": audit,
            "transport": transport,
            "tool": "qwayk-spaceship-safe-agent-cli",
            "tool_version": __version__,
            "command_str": command_str,
            "env_file": str(args.env_file),
            "timeout_s": timeout_s,
            "verbose": bool(args.verbose),
            "apply": bool(args.apply),
            "yes": bool(args.yes),
            "plan_out": args.plan_out,
            "plan_in": args.plan_in,
            "receipt_out": args.receipt_out,
            "run_id": run_ctx.run_id,
            "artifacts_dir": run_ctx.artifacts_dir,
            "runs_index_path": run_ctx.runs_index_path,
            "audit_log_path": run_audit_log_path or global_audit_log_path,
            "audit_log_run_path": run_audit_log_path,
            "audit_log_global_path": global_audit_log_path,
        }

        if run_ctx.enabled and run_ctx.artifacts_dir:
            if not bool(args.apply) and not ctx.get("plan_out"):
                ctx["plan_out"] = str(run_ctx.artifacts_dir / "plan.json")
            if bool(args.apply) and not ctx.get("receipt_out"):
                ctx["receipt_out"] = str(run_ctx.artifacts_dir / "receipt.json")

        rc = int(args.func(args, ctx))
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="qwayk-spaceship-safe-agent-cli",
            version=__version__,
            command=command_str,
            env_fingerprint=cfg.base_url,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return rc

    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    except SafetyError as e:
        audit.write("refused", {"reason": str(e)})
        out.emit({"ok": True, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError"})
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="qwayk-spaceship-safe-agent-cli",
            version=__version__,
            command=command_str,
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 0
    except ToolError as e:
        safe_message = _safe_exception_message(args, e)
        audit.write("error", {"error": safe_message, "error_type": type(e).__name__})
        out.emit(_to_error_payload(safe_message, error_type=type(e).__name__, extra={"command": getattr(args, "cmd", None)}))
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="qwayk-spaceship-safe-agent-cli",
            version=__version__,
            command=command_str,
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 1
    except Exception as e:  # noqa: BLE001
        if bool(args.debug):
            raise
        safe_message = _safe_exception_message(args, e)
        audit.write("error", {"error": safe_message, "error_type": type(e).__name__})
        out.emit(_to_error_payload(safe_message, error_type=type(e).__name__))
        _finalize_run_artifacts(
            run_ctx=run_ctx,
            tool="qwayk-spaceship-safe-agent-cli",
            version=__version__,
            command=command_str,
            env_fingerprint=None,
            output_obj=out.last if isinstance(out.last, dict) else None,
            audit_log_path=run_audit_log_path or global_audit_log_path,
            audit_log_global_path=global_audit_log_path,
            apply=bool(args.apply),
            yes=bool(args.yes),
        )
        return 1
    finally:
        audit.close()


build_parser = _build_parser
