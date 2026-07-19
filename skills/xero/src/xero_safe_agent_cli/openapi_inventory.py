from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

PINNED_COMMIT = "e952d0bda3628facbf7afc5990ad6a0e7e77bd1e"
PINNED_RELEASE = "16.1.0"

SPEC_FILES = {
    "accounting": "xero_accounting.yaml",
    "app-store": "xero-app-store.yaml",
    "assets": "xero_assets.yaml",
    "bank-feeds": "xero_bankfeeds.yaml",
    "files": "xero_files.yaml",
    "finance": "xero-finance.yaml",
    "identity": "xero-identity.yaml",
    "payroll-au": "xero-payroll-au.yaml",
    "payroll-au-v2": "xero-payroll-au-v2.yaml",
    "payroll-nz": "xero-payroll-nz.yaml",
    "payroll-uk": "xero-payroll-uk.yaml",
    "projects": "xero-projects.yaml",
}
CALLBACK_SPEC_FILE = "xero-webhooks.yaml"
HTTP_METHODS = {"delete", "get", "head", "options", "patch", "post", "put", "trace"}

EXPECTED_SOURCE_HASHES = {
    "xero_accounting.yaml": "140f64f8e6bd2d8524b8ffdbffd08589d417efa5466ba57bfa04939a69ff6db8",
    "xero_assets.yaml": "41cb1bb75fc4f7d11a70d9853b71fad7a0dfcff8acdca488836ca77dcdaffe79",
    "xero_bankfeeds.yaml": "a542ef112adfd8c6629f786af4c726f285d6aaa48562a0969dd303f45db9c7c9",
    "xero_files.yaml": "64c08f9a8548d032ff9ba8b465ffd86569526922fb08cf3b2c8dcbb3fb0b0ad4",
    "xero-finance.yaml": "402a2dc5d09fc81f9c04519c9dc5accdac99b475f9a2566f52b1758dbf302266",
    "xero-identity.yaml": "d95f4204d8ec369dac2bb1ee6e6b8cfb88f845a09cbcba630475dd34c73cf2bd",
    "xero-payroll-au.yaml": "35651d98854ef01b1757e4c10e6b171ca42860e3097e072c45183d4cb2d6f28b",
    "xero-payroll-au-v2.yaml": "849a5f732ef105238a3965c56725eb3ce74b6cc9ce754faf23e61b82399f1c84",
    "xero-payroll-nz.yaml": "fe4f1721e71178655bc4bcba01eb6e7811a4cbe55d4ab1cac41d6e9ade9992bb",
    "xero-payroll-uk.yaml": "cbba3714fc5f4c84885aeabd4b40836b9ae48032f355efa3249f6fda665c35b7",
    "xero-projects.yaml": "20deed41dcc3634accc71877606e0ed006a786f7cc6968a1dff230f3544e703e",
    "xero-app-store.yaml": "caf12b43573a68ef495137cee27034b83813c503cd7aa266e6483b0f3f5a7a69",
    "xero-webhooks.yaml": "822244b387a8e26ca948abd338cbee419b6167408ad615582802346587ed7eac",
}

OFFICIAL_REFERENCES = {
    "openapi": "https://github.com/XeroAPI/Xero-OpenAPI/tree/e952d0bda3628facbf7afc5990ad6a0e7e77bd1e",
    "scopes": "https://developer.xero.com/documentation/guides/oauth2/scopes",
    "granular_scopes": "https://developer.xero.com/faq/granular-scopes",
    "pkce": "https://developer.xero.com/documentation/guides/oauth2/pkce-flow",
    "oauth": "https://developer.xero.com/documentation/guides/oauth2/overview",
    "custom_connections": "https://developer.xero.com/documentation/guides/oauth2/custom-connections/",
    "client_credentials": "https://developer.xero.com/documentation/guides/oauth2/client-credentials/",
    "einvoicing": "https://developer.xero.com/documentation/api/einvoicing/einvoicing-registrations",
    "practice_manager": "https://developer.xero.com/documentation/api/practice-manager-3-1/overview-practice-manager",
    "xero_hq": "https://developer.xero.com/documentation/guides/oauth2/tenants/",
    "xero_tax": "https://developer.xero.com/partner/security-standard-for-xero-api-consumers",
    "payment_services": "https://developer.xero.com/documentation/api/accounting/paymentservices",
    "app_store": "https://developer.xero.com/documentation/api/xero-app-store/overview",
    "xass_pricing": "https://developer.xero.com/documentation/xero-app-store/app-partner-guides/xero-app-store-subscriptions-pricing/",
    "pricing_policy_faq": "https://developer.xero.com/faq/pricing-and-policy-updates",
    "developer_pricing": "https://developer.xero.com/pricing",
    "reports": "https://developer.xero.com/documentation/api/accounting/reports",
    "limits": "https://developer.xero.com/documentation/guides/oauth2/limits",
    "changelog": "https://developer.xero.com/changelog",
}

SUPERSEDED_AU_OPERATIONS = {
    "getLeaveApplications": "payroll-au.get-leave-applications-v2",
    "getTimesheets": "payroll-au-v2.get-timesheets",
    "createTimesheet": "payroll-au-v2.create-timesheet",
    "getTimesheet": "payroll-au-v2.get-timesheet",
    "updateTimesheet": "payroll-au-v2.update-timesheet-line",
}

REGIONS = {
    "app-store": "AU,NZ,UK",
    "payroll-au": "AU",
    "payroll-au-v2": "AU",
    "payroll-nz": "NZ",
    "payroll-uk": "UK",
}

ACCESS_GATES = {
    "app-store": (
        "legacy Xero App Store partner and marketplace billing access in AU, NZ, and UK; "
        "Xero deprecated Xero App Store Subscriptions (XASS) in March 2026, accepted no "
        "new apps after 4 December 2025, and required existing customers to migrate by "
        "1 July 2026; the endpoints remain in the pinned and current API reference only "
        "for legacy transition needs; live entitlement and behavior remain unverified"
    ),
    "bank-feeds": "closed API for financial institutions with an established Financial Services partnership; the integration must be certified",
    "finance": "closed API available only to established Financial Services partners for lending; additional certification and commercial terms may apply",
    "payroll-au": "Australia Payroll must be enabled; the authorising user must be Standard or Adviser with Payroll Admin permission",
    "payroll-au-v2": "Australia Payroll must be enabled; the authorising user must be Standard or Adviser with Payroll Admin permission",
    "payroll-nz": "New Zealand Payroll must be enabled; the authorising user must be Standard or Adviser with Payroll Admin permission",
    "payroll-uk": "United Kingdom Payroll must be enabled; the authorising user must be Standard or Adviser with Payroll Admin permission, and the app needs Xero partner permissions",
    "projects": "the organisation must have the Xero Projects product provisioned",
}

ACCOUNTING_SCOPE_RESOURCES = {
    "invoices": {"CreditNotes", "Invoices", "LinkedTransactions", "Quotes", "PurchaseOrders", "RepeatingInvoices"},
    "payments": {"BatchPayments", "Overpayments", "Payments", "Prepayments"},
    "banktransactions": {"BankTransactions", "BankTransfers"},
    "manualjournals": {"ManualJournals"},
    "contacts": {"Contacts", "ContactGroups"},
    "settings": {
        "Accounts",
        "BrandingThemes",
        "Currencies",
        "Items",
        "InvoiceReminders",
        "Organisation",
        "Setup",
        "TaxRates",
        "TrackingCategories",
        "Users",
    },
}

REPORT_SCOPES = {
    "AgedPayablesByContact": "accounting.reports.aged.read",
    "AgedReceivablesByContact": "accounting.reports.aged.read",
    "BalanceSheet": "accounting.reports.balancesheet.read",
    "BankSummary": "accounting.reports.banksummary.read",
    "BudgetSummary": "accounting.reports.budgetsummary.read",
    "ExecutiveSummary": "accounting.reports.executivesummary.read",
    "ProfitAndLoss": "accounting.reports.profitandloss.read",
    "TrialBalance": "accounting.reports.trialbalance.read",
    "TenNinetyNine": "accounting.reports.tenninetynine.read",
}

SENSITIVE_TERMS = {
    "account",
    "bank",
    "billing",
    "contact",
    "credit",
    "employee",
    "file",
    "invoice",
    "journal",
    "pay",
    "receipt",
    "statement",
    "subscription",
    "tax",
}

SENSITIVE_SPEC_IDS = {"assets", "finance", "identity", "projects"}

HIGH_RISK_FLAGS = {
    "auth",
    "bank",
    "billing",
    "bulk",
    "destructive",
    "employment",
    "file",
    "financial",
    "legal",
    "payroll",
    "send",
    "tax",
}

def operation_id_to_kebab(value: str) -> str:
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", value)
    text = re.sub(r"[^A-Za-z0-9]+", "-", text)
    return text.strip("-").lower()


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"OpenAPI document is not an object: {path}")
    return data


def _git_commit(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("The Xero OpenAPI source must be a Git checkout at the pinned commit") from exc


def _json_pointer(document: dict[str, Any], pointer: str) -> Any:
    if not pointer.startswith("#/"):
        raise ValueError(f"Only local OpenAPI references are supported: {pointer}")
    current: Any = document
    for raw in pointer[2:].split("/"):
        key = raw.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or key not in current:
            raise ValueError(f"Broken OpenAPI reference: {pointer}")
        current = current[key]
    return current


def _resolve_ref(document: dict[str, Any], value: Any) -> Any:
    if isinstance(value, dict) and isinstance(value.get("$ref"), str):
        return _json_pointer(document, value["$ref"])
    return value


def _schema_summary(
    document: dict[str, Any], schema: Any, *, seen: frozenset[str] = frozenset()
) -> dict[str, Any]:
    if not isinstance(schema, dict):
        return {"type": "object", "required": [], "properties": {}}
    ref = schema.get("$ref")
    if isinstance(ref, str):
        if ref in seen:
            return {"type": "object", "required": [], "properties": {}, "circular_ref": ref}
        return _schema_summary(document, _json_pointer(document, ref), seen=seen | {ref})

    properties: dict[str, dict[str, Any]] = {}
    required = {str(name) for name in schema.get("required") or []}
    for branch in schema.get("allOf") or []:
        summary = _schema_summary(document, branch, seen=seen)
        properties.update(summary.get("properties") or {})
        required.update(summary.get("required") or [])
    for name, raw in (schema.get("properties") or {}).items():
        properties[str(name)] = _schema_summary(document, raw, seen=seen)

    inferred_type = schema.get("type")
    if not inferred_type and "items" in schema:
        inferred_type = "array"
    if not inferred_type and schema.get("enum"):
        sample = schema["enum"][0]
        inferred_type = (
            "boolean"
            if isinstance(sample, bool)
            else "integer"
            if isinstance(sample, int)
            else "number"
            if isinstance(sample, float)
            else "string"
        )
    result: dict[str, Any] = {
        "type": str(inferred_type or "object"),
        "required": sorted(required),
        "properties": {name: properties[name] for name in sorted(properties)},
    }
    if schema.get("enum") is not None:
        result["enum"] = schema["enum"]
    if schema.get("format") is not None:
        result["format"] = schema["format"]
    if schema.get("minimum") is not None:
        result["minimum"] = schema["minimum"]
    if schema.get("maximum") is not None:
        result["maximum"] = schema["maximum"]
    if schema.get("minLength") is not None:
        result["minLength"] = schema["minLength"]
    if schema.get("maxLength") is not None:
        result["maxLength"] = schema["maxLength"]
    if result["type"] == "array":
        result["items"] = _schema_summary(document, schema.get("items") or {}, seen=seen)
    if schema.get("oneOf"):
        branches = []
        for branch in schema["oneOf"]:
            summary = _schema_summary(document, branch, seen=seen)
            summary["partial_object"] = True
            branches.append(summary)
        result["oneOf"] = branches
    return result


def _parameter_contract(document: dict[str, Any], raw: Any) -> dict[str, Any]:
    parameter = _resolve_ref(document, raw)
    if not isinstance(parameter, dict):
        raise ValueError("OpenAPI parameter is not an object")
    schema = _resolve_ref(document, parameter.get("schema") or {})
    if not isinstance(schema, dict):
        schema = {}
    contract = {
        "name": str(parameter.get("name") or ""),
        "in": str(parameter.get("in") or ""),
        "required": bool(parameter.get("required")),
        "type": str(schema.get("type") or "string"),
        "format": schema.get("format"),
        "enum": schema.get("enum"),
        "explode": bool(parameter.get("explode", True)),
    }
    if schema.get("minimum") is not None:
        contract["minimum"] = schema["minimum"]
    if schema.get("maximum") is not None:
        contract["maximum"] = schema["maximum"]
    if schema.get("minLength") is not None:
        contract["minLength"] = schema["minLength"]
    if schema.get("maxLength") is not None:
        contract["maxLength"] = schema["maxLength"]
    if isinstance(schema.get("items"), dict):
        contract["items"] = _schema_summary(document, schema["items"])
    return contract


def _request_contract(document: dict[str, Any], raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    request = _resolve_ref(document, raw)
    if not isinstance(request, dict):
        raise ValueError("OpenAPI request body is not an object")
    content: dict[str, Any] = {}
    for media_type, media in sorted((request.get("content") or {}).items()):
        if not isinstance(media, dict):
            continue
        content[str(media_type)] = _schema_summary(document, media.get("schema") or {})
    return {"required": bool(request.get("required")), "content": content}


def _response_media_types(document: dict[str, Any], responses: Any) -> list[str]:
    media_types: set[str] = set()
    if not isinstance(responses, dict):
        return []
    for raw in responses.values():
        response = _resolve_ref(document, raw)
        if isinstance(response, dict):
            media_types.update(str(value) for value in (response.get("content") or {}))
    return sorted(media_types)


def _preferred_accept(media_types: list[str]) -> str:
    for value in ("application/pdf", "application/octet-stream"):
        if value in media_types:
            return value
    non_json = [value for value in media_types if "json" not in value.lower()]
    if non_json:
        return non_json[0]
    return "application/json"


def _resource(path: str) -> str:
    return next((part for part in path.split("/") if part), "")


def _minimum_scopes(spec_id: str, path: str, method: str, operation: dict[str, Any]) -> tuple[list[str], str]:
    read = method == "GET"
    if spec_id == "accounting":
        if "/Attachments" in path:
            return (["accounting.attachments.read"] if read else ["accounting.attachments"], "current")
        resource = _resource(path)
        if resource == "Reports":
            if path in {"/Reports", "/Reports/{ReportID}"}:
                return ["accounting.reports.taxreports.read"], "current"
            report = next((part for part in path.split("/")[2:] if part and not part.startswith("{")), "")
            if report in REPORT_SCOPES:
                return [REPORT_SCOPES[report]], "current"
            return ["accounting.reports.read"], "deprecated_compatibility_until_2027-09"
        if resource == "Budgets":
            return ["accounting.budgets.read"], "current"
        if resource == "Journals":
            return ["accounting.journals.read"], "advanced_tier_and_certification"
        if resource == "PaymentServices" or "/PaymentServices" in path:
            return ["paymentservices"], "certification_required"
        for suffix, resources in ACCOUNTING_SCOPE_RESOURCES.items():
            if resource in resources:
                return ([f"accounting.{suffix}.read"] if read else [f"accounting.{suffix}"], "current")
        if resource in {"ExpenseClaims", "Receipts"}:
            return (
                ["accounting.transactions.read"] if read else ["accounting.transactions"],
                "deprecated_compatibility_until_2027-09",
            )

    security = operation.get("security") or []
    scopes: list[str] = []
    for alternative in security:
        if not isinstance(alternative, dict):
            continue
        for values in alternative.values():
            if isinstance(values, list):
                scopes.extend(str(value) for value in values)
    scopes = sorted(set(scopes))
    if read:
        read_scopes = [value for value in scopes if value.endswith(".read") or value == "openid"]
        if read_scopes:
            return read_scopes, "current"
    write_scopes = [value for value in scopes if not value.endswith(".read")]
    return (write_scopes or scopes), "current"


def _risk_flags(spec_id: str, method: str, path: str, operation_id: str) -> list[str]:
    text = f"{spec_id} {path} {operation_id}".lower()
    flags: set[str] = set()
    if method != "GET":
        flags.add("write")
    if method == "DELETE" or any(term in operation_id.lower() for term in ("delete", "revert", "reject")):
        flags.add("destructive")
    if spec_id == "accounting" or spec_id in {"assets", "finance", "projects"}:
        flags.add("financial")
    if "bank" in text or spec_id == "bank-feeds":
        flags.add("bank")
    if spec_id.startswith("payroll"):
        flags.update({"payroll", "employment"})
    if "tax" in text or "super" in text:
        flags.add("tax")
    if spec_id == "files" or "attachment" in text or "file" in text:
        flags.add("file")
    if spec_id == "identity" and method == "DELETE":
        flags.add("auth")
    if spec_id == "app-store":
        flags.add("billing")
    if "emailinvoice" in operation_id.lower():
        flags.add("send")
    if any(term in operation_id.lower() for term in ("batch", "multiple", "orcreate")):
        flags.add("bulk")
    return sorted(flags)


def _sensitive_output(spec_id: str, path: str) -> bool:
    text = f"{spec_id} {path}".lower()
    return spec_id in SENSITIVE_SPEC_IDS or any(term in text for term in SENSITIVE_TERMS)


def _extra_approval(method: str, risk_flags: list[str]) -> bool:
    return method != "GET" and bool(set(risk_flags) & HIGH_RISK_FLAGS)


def _source_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verify_source_hashes(root: Path) -> None:
    for filename, expected in EXPECTED_SOURCE_HASHES.items():
        path = root / filename
        if not path.is_file():
            raise ValueError(f"Pinned Xero source file is missing: {filename}")
        actual = _source_hash(path)
        if actual != expected:
            raise ValueError(
                f"Pinned Xero source hash mismatch for {filename}: expected {expected}, found {actual}"
            )


def _operation_rows(spec_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    operations_by_spec: dict[str, int] = {}
    methods: Counter[str] = Counter()
    hashes: dict[str, str] = {}
    release_values: set[str] = set()

    for spec_id, filename in SPEC_FILES.items():
        path = spec_root / filename
        document = _load_yaml(path)
        hashes[filename] = _source_hash(path)
        release_values.add(str((document.get("info") or {}).get("version")))
        server = str(((document.get("servers") or [{}])[0] or {}).get("url") or "").rstrip("/")
        spec_count = 0
        for api_path, path_item in sorted((document.get("paths") or {}).items()):
            if not isinstance(path_item, dict):
                continue
            common_parameters = path_item.get("parameters") or []
            for method, operation in sorted(path_item.items()):
                if method.lower() not in HTTP_METHODS:
                    continue
                if not isinstance(operation, dict):
                    raise ValueError(f"Operation is not an object: {filename} {method} {api_path}")
                http_method = method.upper()
                operation_id = str(operation.get("operationId") or "")
                if not operation_id:
                    raise ValueError(f"Missing operationId: {filename} {http_method} {api_path}")
                disposition = "command"
                command: str | None = f"{spec_id}.{operation_id_to_kebab(operation_id)}"
                superseded_by = None
                if spec_id == "payroll-au" and operation_id in SUPERSEDED_AU_OPERATIONS:
                    disposition = "superseded_compatibility"
                    command = None
                    superseded_by = SUPERSEDED_AU_OPERATIONS[operation_id]

                parameters = [
                    _parameter_contract(document, raw)
                    for raw in [*common_parameters, *(operation.get("parameters") or [])]
                ]
                minimum_scopes, scope_status = _minimum_scopes(
                    spec_id, str(api_path), http_method, operation
                )
                if spec_id == "identity":
                    minimum_scopes = ["app.connections"]
                    scope_status = "current_non_tenanted"
                    if operation_id == "getConnections":
                        parameters.extend(
                            [
                                {
                                    "name": name,
                                    "in": "header",
                                    "required": False,
                                    "type": "string",
                                    "format": "uuid",
                                    "enum": None,
                                    "explode": True,
                                }
                                for name in ("Xero-Tenant-Id", "Xero-User-Id")
                            ]
                        )
                access_reason = ACCESS_GATES.get(spec_id)
                if spec_id == "accounting" and (
                    _resource(str(api_path)) == "PaymentServices" or "/PaymentServices" in str(api_path)
                ):
                    access_reason = "certified payment-service partner access"
                region = REGIONS.get(spec_id, "global")
                if spec_id == "accounting":
                    resource = _resource(str(api_path))
                    if resource == "Journals":
                        access_reason = (
                            "Xero Advanced tier and certification for new access; the authorising "
                            "user must be an Adviser or a Standard user with reporting permission; "
                            "new Custom Connections created from 29 April 2026 do not receive "
                            "accounting.journals.read"
                        )
                    elif resource in {"Reports", "ManualJournals"}:
                        access_reason = (
                            "the authorising user must be an Adviser or a Standard user with "
                            "reporting permission"
                        )
                    if operation_id == "getReportTenNinetyNine":
                        region = "US"
                        access_reason = "US organisations only; the authorising user must be an Adviser"
                    if operation_id in {"getReportsList", "getReportFromId"}:
                        region = "AU,NZ"
                        access_reason = (
                            "BAS tax reports are Australia-only and GST tax reports are New "
                            "Zealand-only; the authorising user must be an Adviser or a Standard "
                            "user with reporting permission"
                        )
                    if operation_id in {
                        "getOrganisationCISSettings",
                        "getContactCISSettings",
                    }:
                        region = "UK"
                    if resource in {"ExpenseClaims", "Receipts"}:
                        access_reason = (
                            "legacy access only for customers who used classic expense claims in "
                            "the six months before 10 July 2018; scheduled retirement February 2027"
                        )
                    if operation_id in {
                        "createContacts",
                        "createCreditNotes",
                        "createInvoices",
                        "updateContact",
                        "updateCreditNote",
                        "updateInvoice",
                        "updateOrCreateContacts",
                        "updateOrCreateCreditNotes",
                        "updateOrCreateInvoices",
                    }:
                        bank_admin_condition = (
                            "if the request creates or updates contact bank-account details, the "
                            "authorising user must have BankAccountAdmin permission"
                        )
                        access_reason = (
                            f"{access_reason}; {bank_admin_condition}"
                            if access_reason
                            else bank_admin_condition
                        )

                excluded_regions = (
                    ["US"]
                    if spec_id == "finance"
                    and operation_id == "getFinancialStatementCashflow"
                    else []
                )

                idempotency = any(
                    item["in"] == "header" and item["name"].lower() == "idempotency-key"
                    for item in parameters
                )
                tenant_bound_path_parameters = [
                    str(item["name"])
                    for item in parameters
                    if item.get("in") == "path"
                    and re.sub(r"[^a-z0-9]", "", str(item.get("name") or "").lower())
                    in {"organisationid", "tenantid"}
                ]
                scheduled_retirement = None
                if spec_id == "accounting" and _resource(str(api_path)) in {"ExpenseClaims", "Receipts"}:
                    scheduled_retirement = "2027-02"

                risk_flags = _risk_flags(spec_id, http_method, str(api_path), operation_id)
                response_media_types = _response_media_types(
                    document, operation.get("responses") or {}
                )
                rows.append(
                    {
                        "source_kind": "openapi",
                        "source_file": filename,
                        "source_hash": hashes[filename],
                        "spec_id": spec_id,
                        "server": server,
                        "method": http_method,
                        "path": str(api_path),
                        "operation_id": operation_id,
                        "summary": str(operation.get("summary") or "").strip(),
                        "command": command,
                        "disposition": disposition,
                        "superseded_by": superseded_by,
                        "region": region,
                        "excluded_regions": excluded_regions,
                        "access_gated": bool(access_reason),
                        "access_reason": access_reason,
                        "auth_flow": (
                            "client_credentials"
                            if spec_id in {"app-store", "identity"}
                            else "pkce"
                        ),
                        "tenant_required": spec_id not in {"app-store", "identity"},
                        "required_one_of_headers": (
                            ["Xero-Tenant-Id", "Xero-User-Id"]
                            if spec_id == "identity" and operation_id == "getConnections"
                            else []
                        ),
                        "tenant_bound_path_parameters": tenant_bound_path_parameters,
                        "minimum_scopes": minimum_scopes,
                        "scope_status": scope_status,
                        "parameters": parameters,
                        "request": _request_contract(document, operation.get("requestBody")),
                        "response_statuses": sorted(str(code) for code in (operation.get("responses") or {})),
                        "response_media_types": response_media_types,
                        "preferred_accept": _preferred_accept(response_media_types),
                        "idempotency_supported": idempotency,
                        "sensitive_output": _sensitive_output(spec_id, str(api_path)),
                        "risk_flags": risk_flags,
                        "extra_approval": _extra_approval(http_method, risk_flags),
                        "scheduled_retirement": scheduled_retirement,
                    }
                )
                spec_count += 1
                methods[http_method] += 1
        operations_by_spec[spec_id] = spec_count

    if release_values != {PINNED_RELEASE}:
        raise ValueError(f"Unexpected Xero OpenAPI release values: {sorted(release_values)}")
    return rows, {
        "operations_by_spec": operations_by_spec,
        "methods": dict(sorted(methods.items())),
        "source_hashes": hashes,
    }


def _manual_operations() -> list[dict[str, Any]]:
    base = {
        "source_kind": "official_docs_manual",
        "source_file": OFFICIAL_REFERENCES["einvoicing"],
        "source_hash": None,
        "spec_id": "einvoicing",
        "server": "https://api.xero.com/einvoicing.xro/1.0",
        "region": "AU,NZ",
        "excluded_regions": [],
        "access_gated": True,
        "access_reason": "approved Xero app partner access",
        "auth_flow": "pkce",
        "tenant_required": True,
        "tenant_bound_path_parameters": ["organisationId"],
        "minimum_scopes": ["einvoicing"],
        "scope_status": "certification_required",
        "response_statuses": ["200", "400", "401", "403"],
        "response_media_types": ["application/json"],
        "preferred_accept": "application/json",
        "idempotency_supported": False,
        "sensitive_output": True,
        "scheduled_retirement": None,
        "disposition": "command",
        "superseded_by": None,
    }
    path_parameter = {
        "name": "organisationId",
        "in": "path",
        "required": True,
        "type": "string",
        "format": "uuid",
        "enum": None,
        "explode": True,
    }
    return [
        {
            **base,
            "method": "GET",
            "path": "/registrations/{organisationId}",
            "operation_id": "getRegistration",
            "summary": "Retrieve an organisation's eInvoicing registration",
            "command": "einvoicing.get-registration",
            "parameters": [path_parameter],
            "request": None,
            "risk_flags": ["financial"],
            "extra_approval": False,
        },
        {
            **base,
            "method": "PUT",
            "path": "/registrations/{organisationId}/registerbybusinessnumber",
            "operation_id": "registerByBusinessNumber",
            "summary": "Register an organisation to receive eInvoices using its business number",
            "command": "einvoicing.register-by-business-number",
            "parameters": [path_parameter],
            "request": None,
            "risk_flags": ["financial", "legal", "write"],
            "extra_approval": True,
            "access_reason": (
                "approved Xero app partner access; the authorising user must have "
                "the Standard or Adviser role"
            ),
        },
    ]


def _attach_verification(rows: list[dict[str, Any]]) -> None:
    commands = [row for row in rows if row.get("command")]
    reads = [row for row in commands if row["method"] == "GET"]
    for row in commands:
        if row["method"] == "GET":
            row["snapshot_strategy"] = "not_applicable"
            row["verification_strategy"] = "response_received"
            row["verification_command"] = None
            continue
        exact = next(
            (
                candidate
                for candidate in reads
                if candidate["spec_id"] == row["spec_id"]
                and candidate["server"] == row["server"]
                and candidate["path"] == row["path"]
            ),
            None,
        )
        paired = exact if "{" in row["path"] else None
        if paired:
            row["snapshot_strategy"] = "paired_read_when_target_exists"
            row["verification_strategy"] = (
                "paired_absence_check_after_apply"
                if row["method"] == "DELETE"
                else "paired_read_after_apply"
            )
            row["verification_command"] = paired["command"]
        else:
            row["snapshot_strategy"] = "no_snapshot"
            row["verification_strategy"] = "provider_response_only"
            row["verification_command"] = None


def _manual_boundaries(callback_hash: str) -> dict[str, Any]:
    return {
        "webhooks": {
            "disposition": "callback_only",
            "source": CALLBACK_SPEC_FILE,
            "source_hash": callback_hash,
            "callable_operations": 0,
            "reason": "The official webhook specification defines callback payloads, not callable paths; this CLI documents signature verification but does not host callbacks.",
            "reference": "https://developer.xero.com/documentation/guides/webhooks/overview",
        },
        "practice_manager": {
            "disposition": "access_gated_docs_only",
            "callable_operations": None,
            "reason": "Practice Manager 3.1 requires app-partner registration and a security self-assessment, and Xero does not include a pinned machine-readable contract in release 16.1.0. The tool does not guess an endpoint inventory or add a generic bridge.",
            "reference": OFFICIAL_REFERENCES["practice_manager"],
            "scopes": [
                "practicemanager.client",
                "practicemanager.client.read",
                "practicemanager.job",
                "practicemanager.job.read",
                "practicemanager.staff",
                "practicemanager.staff.read",
                "practicemanager.time",
                "practicemanager.time.read",
            ],
        },
        "xero_hq": {
            "disposition": "access_gated_docs_only",
            "callable_operations": None,
            "reason": "Xero identifies Xero HQ practices as a distinct tenant and applies annual security self-assessment requirements to every Xero HQ API consumer. Release 16.1.0 has no pinned machine-readable Xero HQ contract, so the tool does not guess endpoints or scopes.",
            "reference": OFFICIAL_REFERENCES["xero_hq"],
        },
        "xero_tax": {
            "disposition": "access_gated_docs_only",
            "callable_operations": None,
            "reason": "Xero applies annual security self-assessment requirements to every Xero Tax API consumer. Release 16.1.0 has no pinned machine-readable Xero Tax contract, so the tool does not guess endpoints or scopes.",
            "reference": OFFICIAL_REFERENCES["xero_tax"],
        },
        "payment_services": {
            "disposition": "implemented_from_openapi_access_gated",
            "callable_operations": 4,
            "commands": [
                "accounting.create-branding-theme-payment-services",
                "accounting.get-payment-services",
                "accounting.create-payment-service",
                "accounting.get-branding-theme-payment-services",
            ],
            "reason": "The four operations are present in the pinned Accounting specification but require certified payment-service partner access and the paymentservices scope.",
            "reference": OFFICIAL_REFERENCES["payment_services"],
        },
        "einvoicing": {
            "disposition": "implemented_from_official_docs_access_gated",
            "callable_operations": 2,
            "commands": [
                "einvoicing.get-registration",
                "einvoicing.register-by-business-number",
            ],
            "reason": "The two official registration endpoints have explicit fixed commands. They are limited to Australia and New Zealand and require approved app-partner access.",
            "reference": OFFICIAL_REFERENCES["einvoicing"],
        },
    }


def build_inventory(spec_root: str | Path) -> dict[str, Any]:
    root = Path(spec_root).expanduser().resolve()
    if not root.exists():
        raise ValueError(f"Xero OpenAPI checkout not found: {root}")
    commit = _git_commit(root)
    if commit != PINNED_COMMIT:
        raise ValueError(f"Expected Xero OpenAPI commit {PINNED_COMMIT}, found {commit}")
    _verify_source_hashes(root)

    rows, source_details = _operation_rows(root)
    callback_path = root / CALLBACK_SPEC_FILE
    callback_document = _load_yaml(callback_path)
    if callback_document.get("paths") not in ({}, None):
        raise ValueError("The pinned webhook specification unexpectedly contains callable paths")
    callback_hash = _source_hash(callback_path)
    rows.extend(_manual_operations())
    _attach_verification(rows)
    rows.sort(key=lambda row: (row["spec_id"], row["operation_id"], row["method"], row["path"]))

    openapi_rows = [row for row in rows if row["source_kind"] == "openapi"]
    commands = [row for row in rows if row.get("command")]
    if len(openapi_rows) != 477:
        raise ValueError(f"Pinned Xero boundary changed: expected 477 operations, found {len(openapi_rows)}")
    if len({row["command"] for row in commands}) != len(commands):
        raise ValueError("Generated Xero command names are not unique")

    counts = Counter(row["disposition"] for row in rows)
    return {
        "catalog_version": 1,
        "source": {
            "repository": "https://github.com/XeroAPI/Xero-OpenAPI",
            "release": PINNED_RELEASE,
            "commit": commit,
            "executable_spec_count": len(SPEC_FILES),
            "callback_spec_count": 1,
            "openapi_operation_count": len(openapi_rows),
            "manual_operation_count": len(rows) - len(openapi_rows),
            **source_details,
            "callback_source_hash": callback_hash,
        },
        "counts": {
            "raw_openapi_operations": len(openapi_rows),
            "manual_operations": len(rows) - len(openapi_rows),
            "command": counts["command"],
            "superseded_compatibility": counts["superseded_compatibility"],
        },
        "references": OFFICIAL_REFERENCES,
        "manual_boundaries": _manual_boundaries(callback_hash),
        "operations": rows,
    }


def _md(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) or "—"
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_coverage(catalog: dict[str, Any]) -> str:
    source = catalog["source"]
    counts = catalog["counts"]
    boundaries = catalog["manual_boundaries"]
    lines = [
        "# Xero API coverage",
        "",
        "Last updated: **2026-07-19**",
        "",
        "This file is generated from Xero's official OpenAPI release and the small official manual supplement described below. It is the coverage source of truth for this tool.",
        "",
        "## Pinned boundary",
        "",
        f"- Official repository release: **{source['release']}**",
        f"- Pinned commit: `{source['commit']}`",
        f"- Executable specifications: **{source['executable_spec_count']}**",
        f"- Callback-only specifications: **{source['callback_spec_count']}**",
        f"- OpenAPI boundary: **{source['openapi_operation_count']} callable OpenAPI operations**",
        f"- Shipped surface: **{counts['command']} explicit commands**",
        f"- Superseded compatibility rows without commands: **{counts['superseded_compatibility']}**",
        f"- Official docs-only eInvoicing commands: **{source['manual_operation_count']}**",
        "",
        "The five omitted commands are older AU Payroll compatibility operations. Current commands use Leave Applications v2 and Payroll AU Timesheets 2.0. Every original row remains below with its replacement.",
        "",
        "## Official manual supplement",
        "",
        "| Family | Classification | Commands | Why | Official source |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for name in (
        "webhooks",
        "practice_manager",
        "xero_hq",
        "xero_tax",
        "payment_services",
        "einvoicing",
    ):
        item = boundaries[name]
        commands = item.get("commands") or []
        lines.append(
            f"| {_md(name.replace('_', ' ').title())} | {_md(item['disposition'])} | {_md(len(commands) if commands else 0)} | {_md(item['reason'])} | [Xero documentation]({_md(item['reference'])}) |"
        )
    lines.extend(
        [
            "",
            "Practice Manager, Xero HQ, and Xero Tax are not represented as guessed family-level commands. Xero documents access and security conditions for these surfaces, but release 16.1.0 does not include pinned machine-readable contracts for them. A future approved contract can add fixed commands without changing this boundary dishonestly.",
            "",
            "## Operation ledger",
            "",
            "| Source | Spec | Region | Method | Path | Operation ID | Command | Disposition | Scopes | Access | Risk | Snapshot | Verification |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in catalog["operations"]:
        source_label = "OpenAPI" if row["source_kind"] == "openapi" else "Official docs"
        command = row.get("command") or f"replaced by {row.get('superseded_by')}"
        access = row.get("access_reason") or "standard documented access"
        lines.append(
            "| "
            + " | ".join(
                _md(value)
                for value in (
                    source_label,
                    row["spec_id"],
                    row["region"],
                    row["method"],
                    row["path"],
                    row["operation_id"],
                    command,
                    row["disposition"],
                    row["minimum_scopes"],
                    access,
                    row["risk_flags"],
                    row.get("snapshot_strategy") or "not_callable",
                    row.get("verification_strategy") or "not_callable",
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Classification notes",
            "",
            "- Payroll commands are regional. The CLI refuses a payroll command when the selected tenant's country does not match the command region.",
            "- Bank Feeds, Finance, Payment Services, App Store, Practice Manager, Xero HQ, Xero Tax, and eInvoicing have partner, certification, commercial, security, or product access conditions. A fixed command does not imply that a particular Xero app is entitled to use it.",
            "- Expense Claims and Receipts remain pinned OpenAPI commands but are marked for Xero's February 2027 Classic Expenses retirement and rely on deprecated broad accounting scopes until Xero provides another official path.",
            "- Reports, Journals, and ManualJournals require an Adviser or a Standard user with reporting permission. `accounting.journals.read` also requires Xero Advanced and certification for new access. The commands remain explicit and access-gated.",
            "- Webhooks are callback-only. The tool documents signature verification but does not create a fake polling command or host a webhook server.",
            "- Live account, regional payroll, partner-only, commercial, and provider behavior were not tested during the source build.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(
    spec_root: str | Path, *, catalog_path: str | Path, coverage_path: str | Path
) -> dict[str, Any]:
    catalog = build_inventory(spec_root)
    catalog_output = Path(catalog_path)
    coverage_output = Path(coverage_path)
    catalog_output.parent.mkdir(parents=True, exist_ok=True)
    coverage_output.parent.mkdir(parents=True, exist_ok=True)
    catalog_output.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    coverage_output.write_text(render_coverage(catalog), encoding="utf-8")
    return catalog
