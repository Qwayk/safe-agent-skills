from __future__ import annotations

import argparse
import html
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

DEFAULT_DIRECTORY_URL = "https://discovery.googleapis.com/discovery/v1/apis"
DEFAULT_OUTPUT_FILENAME = "gcp_discovery_inventory.json"
DEFAULT_COVERAGE_FILENAME = "api_coverage.md"
CLOUD_DOC_HOSTS = {"cloud.google.com", "docs.cloud.google.com"}
EXPLICIT_CORE_SERVICE_IDS = {
    "billingbudgets",
    "cloudasset",
    "cloudbilling",
    "compute",
    "container",
    "dns",
    "logging",
    "pubsub",
    "sqladmin",
    "storage",
}

EXCLUDED_FAMILY_RULES: list[tuple[str, str, tuple[str, ...]]] = [
    ("ads", "separate Google Ads product", ("adexchangebuyer", "admob", "adsense", "dfareporting", "displayvideo", "doubleclick", "searchads360", "realtimebidding", "authorizedbuyersmarketplace", "merchantapi")),
    ("analytics", "separate Google Analytics product", ("analyticsadmin", "analyticsdata", "marketingplatformadmin")),
    ("business_profile", "separate Business Profile or My Business product", ("businessprofile", "mybusiness")),
    ("maps_consumer_content", "separate Maps or consumer/content API", ("addressvalidation", "airquality", "areainsights", "civicinfo", "customsearch", "factchecktools", "googleadsense", "kgsearch", "pagespeedonline", "pollen", "searchconsole", "streetviewpublish", "safebrowsing", "solar", "travelimpactmodel", "webfonts", "webrisk")),
    ("merchant", "separate Merchant product", ("merchant", "manufacturers")),
    ("search_console", "separate Search Console product", ("searchconsole", "indexing")),
    ("tag_manager", "separate Tag Manager product", ("tagmanager",)),
    ("workspace_user", "separate Workspace user API", ("admin:", "appsmarket", "chat", "classroom", "cloudsearch", "docs:v1", "drive", "driveactivity", "drivelabels", "forms", "gmail", "gmailpostmastertools", "groupsmigration", "groupssettings", "keep", "licensing", "meet", "oauth2", "people", "reseller", "script", "sheets", "slides", "tasks", "vault", "workspaceevents")),
    ("youtube", "separate YouTube product", ("youtube",)),
]

GOOGLEAPIS_PROTO_FALLBACKS: dict[tuple[str, str], dict[str, str]] = {
    ("datalabeling", "v1beta1"): {
        "source_url": "https://raw.githubusercontent.com/googleapis/googleapis/master/google/cloud/datalabeling/v1beta1/data_labeling_service.proto",
        "base_url": "https://datalabeling.googleapis.com/",
        "include_reason": "official googleapis interface definition fallback because Discovery returned an error",
    }
}

OFFICIAL_REST_DOC_FALLBACKS: dict[tuple[str, str], dict[str, str]] = {
    ("integrations", "v1"): {
        "source_url": "https://docs.cloud.google.com/application-integration/docs/reference/rest",
        "base_url": "https://integrations.googleapis.com/",
        "include_reason": "official Application Integration REST documentation fallback because Discovery returned an error",
    }
}

READ_METHODS = {"GET", "HEAD"}
READ_VERBS = {
    "batchget",
    "check",
    "describe",
    "fetch",
    "get",
    "getiampolicy",
    "list",
    "lookup",
    "query",
    "search",
    "testiampermissions",
    "validate",
    "wait",
}
DELETE_VERBS = {
    "delete",
    "destroy",
    "purge",
    "remove",
    "revoke",
}
MUTATING_VERBS = {
    "add",
    "approve",
    "attach",
    "bind",
    "cancel",
    "clear",
    "copy",
    "create",
    "disable",
    "enable",
    "export",
    "grant",
    "import",
    "insert",
    "move",
    "patch",
    "promote",
    "put",
    "replace",
    "reset",
    "restore",
    "resume",
    "run",
    "set",
    "sign",
    "start",
    "stop",
    "suspend",
    "undelete",
    "unbind",
    "update",
}
SECURITY_IDENTITY_TOKENS = {
    "accesscontextmanager",
    "accessapproval",
    "credential",
    "iam",
    "identity",
    "member",
    "oauth",
    "permission",
    "principal",
    "policy",
    "role",
    "securitycenter",
    "serviceaccount",
    "serviceaccounts",
    "serviceusage",
    "token",
}
SECRET_TOKENS = {
    "credential",
    "password",
    "secret",
    "token",
    "privatekey",
    "private-key",
    "signblob",
    "signjwt",
}
NETWORK_TOKENS = {
    "backend",
    "dns",
    "egress",
    "endpoint",
    "firewall",
    "forwarding",
    "gateway",
    "ingress",
    "interconnect",
    "loadbalancer",
    "load-balancer",
    "network",
    "nat",
    "peering",
    "private",
    "public",
    "route",
    "router",
    "subnet",
    "vpn",
}
PUBLIC_EXPOSURE_TOKENS = {
    "acl",
    "allow",
    "binding",
    "firewall",
    "iam",
    "member",
    "policy",
    "public",
    "securitypolicy",
    "visibility",
}
SPEND_QUOTA_SERVICE_IDS = {
    "aiplatform",
    "artifactregistry",
    "batch",
    "bigquery",
    "cloudbuild",
    "cloudfunctions",
    "cloudrun",
    "compute",
    "container",
    "dataflow",
    "dataproc",
    "datastream",
    "firestore",
    "gkehub",
    "integrations",
    "logging",
    "monitoring",
    "pubsub",
    "run",
    "spanner",
    "sqladmin",
    "storage",
    "workflows",
}
DATABASE_SERVICE_IDS = {"bigquery", "datastore", "firestore", "sqladmin", "spanner"}
NETWORK_SERVICE_IDS = {"compute", "networkmanagement", "networksecurity", "networkservices", "servicenetworking", "trafficdirector"}
SECURITY_SERVICE_IDS = {"accessapproval", "accesscontextmanager", "cloudidentity", "cloudkms", "iap", "iam", "integrations", "kmsinventory", "policytroubleshooter", "secretmanager", "securitycenter", "securityposture", "serviceusage"}
SECRET_SERVICE_IDS = {"secretmanager"}
BILLABLE_DELETE_SERVICE_IDS = {"compute", "storage", "sqladmin", "datastore", "firestore", "spanner"}


@dataclass(frozen=True)
class InventoryContext:
    directory_url: str
    generated_at: str


def fetch_json(url: str, *, timeout_s: float = 30.0) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=timeout_s, headers={"Accept": "application/json"})
            if response.status_code in {429, 500, 502, 503, 504} and attempt < 2:
                time.sleep(1 + attempt)
                continue
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError(f"Expected JSON object from {url}")
            return data
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < 2:
                time.sleep(1 + attempt)
                continue
            break
    if last_error is not None:
        raise last_error
    raise RuntimeError(f"Failed to fetch JSON from {url}")


def fetch_text(url: str, *, timeout_s: float = 30.0) -> str:
    response = requests.get(url, timeout=timeout_s, headers={"Accept": "text/plain"})
    response.raise_for_status()
    return response.text


def _host(value: str | None) -> str:
    if not value:
        return ""
    return urlparse(value).netloc.lower()


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _slugify(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", value)
    value = re.sub(r"[^A-Za-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-").lower()


def _operation_name(resource_path: list[str], method_name: str) -> str:
    raw = "-".join(resource_path + [method_name])
    raw = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", raw)
    return _slugify(raw)


def _normalized_service_key(service_id: str) -> str:
    return _slugify(service_id)


def _service_lookup_key(item: dict[str, Any]) -> str:
    api_id = _text(item.get("name") or item.get("id", "").split(":", 1)[0])
    version = _text(item.get("version"))
    return f"{api_id}:{version}" if version else api_id


def _matches_excluded_family(service_id: str, title: str, documentation_link: str) -> tuple[bool, str | None]:
    service_key = service_id.lower()
    haystack = f"{service_id} {title} {documentation_link}".lower()
    for family_name, reason, needles in EXCLUDED_FAMILY_RULES:
        if any(service_key == needle or service_key.startswith(f"{needle}:") for needle in needles):
            return True, f"{family_name}: {reason}"
        if any(needle.endswith(":") and needle in haystack for needle in needles):
            return True, f"{family_name}: {reason}"
    return False, None


def _is_in_scope_api(item: dict[str, Any]) -> tuple[bool, str]:
    service_id = _text(item.get("name") or item.get("id", "").split(":", 1)[0])
    title = _text(item.get("title"))
    documentation_link = _text(item.get("documentationLink"))
    preferred = bool(item.get("preferred"))
    excluded, reason = _matches_excluded_family(service_id, title, documentation_link)
    if excluded:
        return False, reason or "excluded family"
    if not preferred:
        return False, "not the preferred Discovery version"

    if service_id in EXPLICIT_CORE_SERVICE_IDS:
        return True, "preferred explicit core GCP service"

    if _host(documentation_link) in CLOUD_DOC_HOSTS:
        return True, "preferred Cloud docs entry"

    return False, "not a Cloud docs preferred entry"


def _walk_operations(service_doc: dict[str, Any], service_id: str, version: str) -> list[dict[str, Any]]:
    operations: list[dict[str, Any]] = []

    def visit(resources: dict[str, Any], parents: list[str]) -> None:
        for resource_name, resource in sorted(resources.items()):
            resource_methods = resource.get("methods") or {}
            current_path = parents + [resource_name]
            for method_name, method in sorted(resource_methods.items()):
                operations.append(
                    _build_operation(
                        service_id=service_id,
                        version=version,
                        resource_path=current_path,
                        method_name=method_name,
                        method=method,
                    )
                )
            child_resources = resource.get("resources") or {}
            if child_resources:
                visit(child_resources, current_path)

    visit(service_doc.get("resources") or {}, [])
    return operations


def _build_operation(
    *,
    service_id: str,
    version: str,
    resource_path: list[str],
    method_name: str,
    method: dict[str, Any],
) -> dict[str, Any]:
    method_id = _text(method.get("id")) or f"{service_id}.{'.'.join(resource_path + [method_name])}"
    http_method = _text(method.get("httpMethod")).upper()
    path = _text(method.get("path"))
    flat_path = _text(method.get("flatPath"))
    description = _text(method.get("description"))
    operation_name = _operation_name(resource_path, method_name)
    classification = _classify_operation(
        method_id=method_id,
        method_name=method_name,
        http_method=http_method,
        path=path,
        description=description,
    )
    risk_categories = _classify_risks(
        service_id=service_id,
        method_id=method_id,
        method_name=method_name,
        http_method=http_method,
        path=path,
        classification=classification,
    )
    evidence = _build_evidence(
        service_id=service_id,
        version=version,
        method_id=method_id,
        method_name=method_name,
        http_method=http_method,
        path=path,
        classification=classification,
    )

    return {
        "operation_id": method_id,
        "operation_name": operation_name,
        "resource_path": resource_path,
        "method_name": method_name,
        "http_method": http_method,
        "path": path,
        "flat_path": flat_path,
        "description": description,
        "classification": classification,
        "risk_categories": sorted(risk_categories),
        "evidence": evidence,
    }


def _classify_operation(
    *,
    method_id: str,
    method_name: str,
    http_method: str,
    path: str,
    description: str,
) -> str:
    _ = (path, description)
    verb = _method_verb(method_name)
    method_lower = method_name.lower()
    if http_method in READ_METHODS and verb not in DELETE_VERBS and verb not in MUTATING_VERBS:
        return "read"
    if http_method in {"POST"} and (method_lower in READ_VERBS or verb in READ_VERBS):
        return "read"
    if http_method == "DELETE" or verb in DELETE_VERBS:
        return "irreversible"
    if method_lower in {"setiampolicy", "setpolicy"} or verb in MUTATING_VERBS:
        return "high_no_snapshot"
    if http_method in {"POST", "PUT", "PATCH"}:
        return "remote_write"
    if http_method in READ_METHODS:
        return "read"
    return "unknown_mutating"


def _method_verb(method_name: str) -> str:
    parts = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", method_name).replace("_", " ").split()
    return parts[0].lower() if parts else method_name.lower()


def _classify_risks(
    *,
    service_id: str,
    method_id: str,
    method_name: str,
    http_method: str,
    path: str,
    classification: str,
) -> set[str]:
    tokens = f"{service_id} {method_id} {method_name} {path}".lower()
    risks: set[str] = set()
    if classification != "read":
        risks.add("no_snapshot")
    if classification == "irreversible":
        risks.add("irreversible")
    if service_id in SPEND_QUOTA_SERVICE_IDS and classification != "read":
        risks.add("spend_quota")
    if service_id in SECURITY_SERVICE_IDS or any(token in tokens for token in SECURITY_IDENTITY_TOKENS):
        risks.add("security_identity")
    if service_id in SECRET_SERVICE_IDS or any(token in tokens for token in SECRET_TOKENS):
        risks.add("secret")
    if service_id in NETWORK_SERVICE_IDS or any(token in tokens for token in NETWORK_TOKENS):
        risks.add("network")
    if any(token in tokens for token in PUBLIC_EXPOSURE_TOKENS):
        risks.add("public_exposure")
    if service_id == "compute" and classification == "irreversible":
        risks.add("compute_delete")
    if service_id in {"storage", "storagebatchoperations", "storagetransfer"} and classification == "irreversible":
        risks.add("storage_delete")
    if service_id in DATABASE_SERVICE_IDS and classification == "irreversible":
        risks.add("database_delete")
    if service_id == "compute" and http_method in {"POST", "PATCH", "PUT"}:
        risks.add("spend_quota")
    if service_id in {"sqladmin", "datastore", "firestore", "spanner", "bigquery"} and classification != "read":
        risks.add("database_delete" if classification == "irreversible" else "spend_quota")
    return risks


def _build_evidence(
    *,
    service_id: str,
    version: str,
    method_id: str,
    method_name: str,
    http_method: str,
    path: str,
    classification: str,
) -> str:
    parts = [
        f"{service_id}:{version}",
        f"{http_method} {method_name}",
        f"path={path}" if path else "path=unknown",
        f"classification={classification}",
    ]
    return "; ".join(parts)


def _service_entry(item: dict[str, Any], service_doc: dict[str, Any], *, include_reason: str) -> dict[str, Any]:
    service_id = _text(item.get("name") or item.get("id", "").split(":", 1)[0])
    version = _text(item.get("version"))
    operations = _walk_operations(service_doc, service_id, version)
    return {
        "service_id": f"{service_id}:{version}" if version else service_id,
        "api_id": service_id,
        "version": version,
        "title": _text(item.get("title")),
        "documentation_link": _text(item.get("documentationLink")),
        "discovery_rest_url": _text(item.get("discoveryRestUrl")),
        "preferred": bool(item.get("preferred")),
        "include_reason": include_reason,
        "operations": operations,
        "operation_count": len(operations),
    }


def _proto_http_path_to_discovery_path(path: str) -> str:
    path = path.strip().lstrip("/")
    return re.sub(r"{([^}=]+)=[^}]+}", r"{+\1}", path)


def _parse_googleapis_proto_operations(proto_text: str, *, service_id: str, version: str) -> list[dict[str, Any]]:
    rpc_matches = list(re.finditer(r"^\s*rpc\s+(\w+)\s*\(", proto_text, flags=re.M))
    operations: list[dict[str, Any]] = []
    for index, match in enumerate(rpc_matches):
        method_name = match.group(1)
        end = rpc_matches[index + 1].start() if index + 1 < len(rpc_matches) else len(proto_text)
        block = proto_text[match.start() : end]
        http_match = re.search(r'^\s*(get|post|put|patch|delete):\s*"([^"]+)"', block, flags=re.M)
        if not http_match:
            continue
        http_method = http_match.group(1).upper()
        path = _proto_http_path_to_discovery_path(http_match.group(2))
        method_id = f"{service_id}.{method_name}"
        operation_name = _operation_name([], method_name)
        classification = _classify_operation(
            method_id=method_id,
            method_name=method_name,
            http_method=http_method,
            path=path,
            description="official googleapis interface definition fallback",
        )
        risk_categories = _classify_risks(
            service_id=service_id,
            method_id=method_id,
            method_name=method_name,
            http_method=http_method,
            path=path,
            classification=classification,
        )
        operations.append(
            {
                "operation_id": method_id,
                "operation_name": operation_name,
                "resource_path": [],
                "method_name": method_name,
                "http_method": http_method,
                "path": path,
                "flat_path": path,
                "description": "Generated from official googleapis interface definition fallback.",
                "classification": classification,
                "risk_categories": sorted(risk_categories),
                "evidence": _build_evidence(
                    service_id=service_id,
                    version=version,
                    method_id=method_id,
                    method_name=method_name,
                    http_method=http_method,
                    path=path,
                    classification=classification,
                ),
            }
        )
    return operations


def _googleapis_proto_service_entry(item: dict[str, Any], fallback: dict[str, str], *, reason: str) -> dict[str, Any]:
    service_id = _text(item.get("name") or item.get("id", "").split(":", 1)[0])
    version = _text(item.get("version"))
    proto_text = fetch_text(fallback["source_url"])
    operations = _parse_googleapis_proto_operations(proto_text, service_id=service_id, version=version)
    return {
        "service_id": f"{service_id}:{version}" if version else service_id,
        "api_id": service_id,
        "version": version,
        "title": _text(item.get("title")),
        "documentation_link": _text(item.get("documentationLink")),
        "discovery_rest_url": "",
        "official_interface_definition_url": fallback["source_url"],
        "base_url": fallback["base_url"],
        "preferred": bool(item.get("preferred")),
        "include_reason": reason,
        "operations": operations,
        "operation_count": len(operations),
    }


def _strip_html_tags(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def _absolute_cloud_docs_url(path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"https://docs.cloud.google.com{path}"


def _extract_application_integration_method_links(index_html: str) -> list[str]:
    links: set[str] = set()
    for match in re.finditer(
        r'href="(?P<href>/application-integration/docs/reference/rest/v[12]/[^"#?]+/[^"/#?]+)"',
        index_html,
    ):
        href = html.unescape(match.group("href"))
        method_name = href.rsplit("/", 1)[-1]
        if method_name and method_name != "overview":
            links.add(_absolute_cloud_docs_url(href))
    return sorted(links)


def _extract_application_integration_index_methods(index_html: str) -> dict[str, dict[str, str]]:
    methods: dict[str, dict[str, str]] = {}
    row_pattern = re.compile(
        r'<tr>\s*<td>\s*<code[^>]*>\s*<a href="(?P<href>[^"]+)">(?P<method>[^<]+)</a></code>\s*</td>\s*'
        r"<td>\s*<code[^>]*>\s*(?P<http>GET|POST|PUT|PATCH|DELETE|HEAD)\s+(?P<path>[^<]+)</code>\s*<br>\s*"
        r"(?P<description>.*?)</td>\s*</tr>",
        flags=re.S,
    )
    for match in row_pattern.finditer(index_html):
        url = _absolute_cloud_docs_url(html.unescape(match.group("href")))
        methods[url] = {
            "http_method": match.group("http").upper(),
            "path": _rest_doc_path_to_discovery_path(match.group("path")),
            "description": _strip_html_tags(match.group("description")),
        }
    return methods


def _rest_doc_path_to_discovery_path(path: str) -> str:
    path = html.unescape(path).strip()
    path = re.sub(r"^https://integrations\.googleapis\.com/", "", path)
    path = path.lstrip("/")
    return re.sub(r"{([^}=]+)=[^}]+}", r"{+\1}", path)


def _build_application_integration_rest_operation(
    *,
    url: str,
    http_method: str,
    path: str,
    description: str,
) -> dict[str, Any]:
    url_match = re.search(
        r"/application-integration/docs/reference/rest/(?P<version>v[12])/(?P<resource>[^/]+)/(?P<method>[^/?#]+)",
        url,
    )
    if not url_match:
        raise ValueError(f"Cannot parse Application Integration REST method URL: {url}")

    version = url_match.group("version")
    resource = html.unescape(url_match.group("resource"))
    method_name = html.unescape(url_match.group("method"))
    resource_path = [version] + resource.split(".")
    method_id = f"integrations.{version}.{resource}.{method_name}"
    if not description:
        description = "Generated from official Application Integration REST documentation."

    operation_name = _operation_name(resource_path, method_name)
    classification = _classify_operation(
        method_id=method_id,
        method_name=method_name,
        http_method=http_method,
        path=path,
        description=description,
    )
    risk_categories = _classify_risks(
        service_id="integrations",
        method_id=method_id,
        method_name=method_name,
        http_method=http_method,
        path=path,
        classification=classification,
    )
    evidence = _build_evidence(
        service_id="integrations",
        version=version,
        method_id=method_id,
        method_name=method_name,
        http_method=http_method,
        path=path,
        classification=classification,
    )
    return {
        "operation_id": method_id,
        "operation_name": operation_name,
        "resource_path": resource_path,
        "method_name": method_name,
        "http_method": http_method,
        "path": path,
        "flat_path": path,
        "description": description,
        "classification": classification,
        "risk_categories": sorted(risk_categories),
        "source_url": url,
        "evidence": f"{evidence}; source={url}",
    }


def _parse_application_integration_method_page(url: str, page_html: str) -> dict[str, Any]:
    http_match = re.search(
        r"<code[^>]*>\s*(?P<http>GET|POST|PUT|PATCH|DELETE|HEAD)\s+"
        r"https://integrations\.googleapis\.com/(?P<path>[^<]+)</code>",
        page_html,
        flags=re.S,
    )
    if not http_match:
        raise ValueError(f"Cannot find HTTP request in Application Integration REST method page: {url}")

    desc_match = re.search(r"</h1>\s*(?P<description>.*?)<h2[^>]*>\s*HTTP request", page_html, flags=re.S | re.I)
    description = _strip_html_tags(desc_match.group("description")) if desc_match else ""
    return _build_application_integration_rest_operation(
        url=url,
        http_method=http_match.group("http").upper(),
        path=_rest_doc_path_to_discovery_path(http_match.group("path")),
        description=description,
    )


def _application_integration_rest_service_entry(
    item: dict[str, Any],
    fallback: dict[str, str],
    *,
    reason: str,
) -> dict[str, Any]:
    index_html = fetch_text(fallback["source_url"])
    method_links = _extract_application_integration_method_links(index_html)
    index_methods = _extract_application_integration_index_methods(index_html)
    operations: list[dict[str, Any]] = []
    for method_url in method_links:
        try:
            operations.append(_parse_application_integration_method_page(method_url, fetch_text(method_url)))
        except ValueError:
            index_method = index_methods.get(method_url)
            if index_method is None:
                raise
            operations.append(
                _build_application_integration_rest_operation(
                    url=method_url,
                    http_method=index_method["http_method"],
                    path=index_method["path"],
                    description=index_method["description"],
                )
            )
    operations.sort(key=lambda operation: operation["operation_name"])
    return {
        "service_id": "integrations:v1+v2-rest",
        "api_id": "integrations",
        "version": "v1+v2-rest",
        "title": _text(item.get("title")) or "Application Integration API",
        "documentation_link": fallback["source_url"],
        "discovery_rest_url": "",
        "official_rest_documentation_url": fallback["source_url"],
        "base_url": fallback["base_url"],
        "preferred": bool(item.get("preferred")),
        "include_reason": reason,
        "operations": operations,
        "operation_count": len(operations),
    }


def _summarize_services(services: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, int] = {
        "included_service_count": len(services),
        "included_operation_count": 0,
        "read_operation_count": 0,
        "remote_write_operation_count": 0,
        "high_no_snapshot_operation_count": 0,
        "irreversible_operation_count": 0,
        "unknown_mutating_operation_count": 0,
    }
    risk_counts: dict[str, int] = {}
    for service in services:
        for operation in service["operations"]:
            summary["included_operation_count"] += 1
            classification = operation["classification"]
            if classification == "read":
                summary["read_operation_count"] += 1
            elif classification == "remote_write":
                summary["remote_write_operation_count"] += 1
            elif classification == "high_no_snapshot":
                summary["high_no_snapshot_operation_count"] += 1
            elif classification == "irreversible":
                summary["irreversible_operation_count"] += 1
            else:
                summary["unknown_mutating_operation_count"] += 1
            for risk in operation["risk_categories"]:
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
    summary["risk_counts"] = risk_counts
    return summary


def _build_exceptions(directory_items: list[dict[str, Any]], included_keys: set[str]) -> list[dict[str, Any]]:
    exceptions: list[dict[str, Any]] = []
    for item in directory_items:
        key = _service_lookup_key(item)
        if key in included_keys:
            continue
        service_id = _text(item.get("name") or item.get("id", "").split(":", 1)[0])
        title = _text(item.get("title"))
        documentation_link = _text(item.get("documentationLink"))
        reason = _is_in_scope_api(item)[1]
        exceptions.append(
            {
                "service_id": key,
                "title": title,
                "documentation_link": documentation_link,
                "kind": "excluded",
                "reason": reason,
            }
        )
    return exceptions


def _record_gap_exception(item: dict[str, Any], reason: str) -> dict[str, Any]:
    service_id = _text(item.get("name") or item.get("id", "").split(":", 1)[0])
    version = _text(item.get("version"))
    return {
        "service_id": f"{service_id}:{version}" if version else service_id,
        "title": _text(item.get("title")),
        "documentation_link": _text(item.get("documentationLink")),
        "kind": "discovery-gap" if _text(item.get("discoveryRestUrl")) else "official-interface-definition-needed",
        "reason": reason,
    }


def build_inventory(directory_data: dict[str, Any], *, directory_url: str = DEFAULT_DIRECTORY_URL) -> dict[str, Any]:
    items = list(directory_data.get("items") or [])
    included_services: list[dict[str, Any]] = []
    included_keys: set[str] = set()
    gap_exceptions: list[dict[str, Any]] = []
    for item in sorted(items, key=lambda data: (_text(data.get("name") or data.get("id", "").split(":", 1)[0]), _text(data.get("version")))):
        include, reason = _is_in_scope_api(item)
        if not include:
            continue
        discovery_rest_url = _text(item.get("discoveryRestUrl"))
        if not discovery_rest_url:
            included_keys.add(_service_lookup_key(item))
            gap_exceptions.append(_record_gap_exception(item, "missing discoveryRestUrl field"))
            continue
        service_id = _text(item.get("name") or item.get("id", "").split(":", 1)[0])
        version = _text(item.get("version"))
        try:
            service_doc = fetch_json(discovery_rest_url)
        except Exception as exc:  # noqa: BLE001
            rest_fallback = OFFICIAL_REST_DOC_FALLBACKS.get((service_id, version))
            if rest_fallback is not None:
                service = _application_integration_rest_service_entry(
                    item,
                    rest_fallback,
                    reason=f"{rest_fallback['include_reason']}: {type(exc).__name__}: {exc}",
                )
                included_services.append(service)
                included_keys.add(_service_lookup_key(item))
                continue
            fallback = GOOGLEAPIS_PROTO_FALLBACKS.get((service_id, version))
            if fallback is not None:
                service = _googleapis_proto_service_entry(
                    item,
                    fallback,
                    reason=f"{fallback['include_reason']}: {type(exc).__name__}: {exc}",
                )
                included_services.append(service)
                included_keys.add(_service_lookup_key(item))
                continue
            included_keys.add(_service_lookup_key(item))
            gap_exceptions.append(_record_gap_exception(item, f"{type(exc).__name__}: {exc}"))
            continue
        service = _service_entry(item, service_doc, include_reason=reason)
        included_services.append(service)
        included_keys.add(_service_lookup_key(item))

    summary = _summarize_services(included_services)
    exceptions = _build_exceptions(items, included_keys)
    exceptions.extend(gap_exceptions)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    summary["excluded_service_count"] = len(items) - len(included_services)
    summary["exceptions_count"] = len(exceptions)
    summary["discovery_gap_count"] = sum(1 for row in exceptions if row["kind"] == "discovery-gap")
    summary["official_interface_definition_needed_count"] = sum(
        1 for row in exceptions if row["kind"] == "official-interface-definition-needed"
    )
    return {
        "generated_at": generated_at,
        "source": {"directory_url": directory_url},
        "boundary": {
            "explicit_core_service_ids": sorted(EXPLICIT_CORE_SERVICE_IDS),
            "cloud_doc_hosts": sorted(CLOUD_DOC_HOSTS),
            "excluded_families": [
                {"name": family_name, "reason": reason, "needles": list(needles)}
                for family_name, reason, needles in EXCLUDED_FAMILY_RULES
            ],
            "official_interface_definition_fallbacks": [
                {
                    "service_id": f"{service_id}:{version}",
                    "source_url": fallback["source_url"],
                    "base_url": fallback["base_url"],
                }
                for (service_id, version), fallback in sorted(GOOGLEAPIS_PROTO_FALLBACKS.items())
            ],
            "official_rest_documentation_fallbacks": [
                {
                    "service_id": f"{service_id}:{version}",
                    "source_url": fallback["source_url"],
                    "base_url": fallback["base_url"],
                }
                for (service_id, version), fallback in sorted(OFFICIAL_REST_DOC_FALLBACKS.items())
            ],
        },
        "summary": summary,
        "services": included_services,
        "exceptions_ledger": exceptions,
    }


def build_coverage_markdown(inventory: dict[str, Any]) -> str:
    lines: list[str] = []
    summary = inventory["summary"]
    lines.append("# API coverage")
    lines.append("")
    lines.append(f"Generated from the official Discovery directory on {inventory['generated_at']} UTC.")
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append(f"- Source directory: `{inventory['source']['directory_url']}`")
    lines.append(f"- Cloud docs hosts: {', '.join(inventory['boundary']['cloud_doc_hosts'])}")
    lines.append(f"- Explicit core developer-doc services: {', '.join(inventory['boundary']['explicit_core_service_ids'])}")
    lines.append("- Included only preferred entries from the official Discovery directory.")
    lines.append("- Used official Google fallback sources only when a selected Discovery document was missing or unavailable.")
    lines.append("- Excluded separate Google product families listed in the boundary data.")
    lines.append("- No raw-request bridge or arbitrary URL bridge is part of this slice.")
    lines.append("")
    lines.append("## Inventory summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|---|---:|")
    for key, label in [
        ("included_service_count", "Included services"),
        ("included_operation_count", "Included operations"),
        ("read_operation_count", "Read operations"),
        ("remote_write_operation_count", "Remote write operations"),
        ("high_no_snapshot_operation_count", "High no snapshot operations"),
        ("irreversible_operation_count", "Irreversible operations"),
        ("unknown_mutating_operation_count", "Unknown mutating operations"),
    ]:
        lines.append(f"| {label} | {summary.get(key, 0)} |")
    lines.append("")
    lines.append("## Per-operation evidence")
    lines.append("")
    for service in inventory["services"]:
        lines.append(f"### {service['service_id']} - {service['title']}")
        lines.append("")
        lines.append("| Operation | HTTP | Class | Risks | Evidence |")
        lines.append("|---|---|---|---|---|")
        for operation in service["operations"]:
            risks = ", ".join(operation["risk_categories"]) or "-"
            evidence = operation["evidence"].replace("|", "\\|")
            lines.append(
                f"| {operation['operation_name']} | {operation['http_method']} | {operation['classification']} | {risks} | {evidence} |"
            )
        lines.append("")
    lines.append("## Safety and risk coverage")
    lines.append("")
    lines.append("| Risk category | Count |")
    lines.append("|---|---:|")
    for risk_name in sorted(summary.get("risk_counts", {})):
        lines.append(f"| {risk_name} | {summary['risk_counts'][risk_name]} |")
    lines.append("")
    lines.append("## Exceptions ledger")
    lines.append("")
    lines.append("| Kind | Service | Reason | Documentation |")
    lines.append("|---|---|---|---|")
    for row in inventory["exceptions_ledger"]:
        lines.append(
            f"| {row['kind']} | {row['service_id']} | {row['reason']} | {row['documentation_link']} |"
        )
    if not inventory["exceptions_ledger"]:
        lines.append("| none | none | no discovery gaps identified in this slice | - |")
    lines.append("")
    return "\n".join(lines)


def generate_inventory(
    *,
    directory_url: str = DEFAULT_DIRECTORY_URL,
    output_dir: Path,
    coverage_path: Path,
) -> dict[str, Any]:
    directory_data = fetch_json(directory_url)
    inventory = build_inventory(directory_data, directory_url=directory_url)
    output_dir.mkdir(parents=True, exist_ok=True)
    coverage_path.parent.mkdir(parents=True, exist_ok=True)
    (output_dir / DEFAULT_OUTPUT_FILENAME).write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8")
    coverage_path.write_text(build_coverage_markdown(inventory), encoding="utf-8")
    return inventory


def _default_paths() -> tuple[Path, Path]:
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / "docs" / "_generated", repo_root / "docs" / DEFAULT_COVERAGE_FILENAME


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate the GCP Discovery inventory and coverage docs.")
    parser.add_argument("--directory-url", default=DEFAULT_DIRECTORY_URL)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--coverage-path", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    default_output_dir, default_coverage_path = _default_paths()
    output_dir = Path(args.output_dir) if args.output_dir else default_output_dir
    coverage_path = Path(args.coverage_path) if args.coverage_path else default_coverage_path
    generate_inventory(directory_url=args.directory_url, output_dir=output_dir, coverage_path=coverage_path)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
