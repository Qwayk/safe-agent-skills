#!/usr/bin/env python3
"""Generate Jira's fixed command inventory and coverage ledger from pinned specs."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SPEC_INPUTS = (
    {
        "surface": "platform",
        "file": "specs/jira-platform-v3.openapi.json",
        "url": "https://dac-static.atlassian.com/cloud/jira/platform/swagger-v3.v3.json",
        "sha256": "25a377a1f482640eb7272052cbe51f9ddd6c20c3195257f36610cd8d408d8f27",
        "expected_operations": 616,
    },
    {
        "surface": "software",
        "file": "specs/jira-software.openapi.json",
        "url": "https://dac-static.atlassian.com/cloud/jira/software/swagger.v3.json",
        "sha256": "4e108d54b99064475c6ba0f986cce46dcace81336e034b58a5400b93174b927a",
        "expected_operations": 105,
    },
)
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
READ_POST_PREFIXES = (
    "check",
    "evaluate",
    "expand",
    "find",
    "get",
    "match",
    "parse",
    "search",
    "validate",
)
READ_POST_OPERATION_IDS = {
    "analyseExpression",
    "bulkFetchIssues",
    "countIssues",
    "listWorkflowHistory",
    "migrateQueries",
    "readWorkflowFromHistory",
    "readWorkflowPreviews",
    "readWorkflowSchemes",
    "readWorkflows",
    "sanitiseJqlQueries",
    "suggestedPrioritiesForMappings",
}
HIGH_RISK_PATTERNS = {
    "destructive": (
        r"(?:^|-)(?:archive|cancel|delete|merge|redact|remove|restore|swap|trash|unarchive)(?:d|s|ed|ing)?(?:-|$)",
    ),
    "bulk": (
        r"(?:^|-)bulk(?:-|$)",
        r"(?:^|-)(?:async|asynchronous)(?:-|$)",
        r"(?:^|-)multiple(?:-|$)",
    ),
    "permission": (r"permission", r"security"),
    "membership": (
        r"(?:^|-)(?:group|member|membership|role|team|user|watcher)(?:s|ship)?(?:-|$)",
    ),
    "workflow": (r"workflow", r"transition"),
    "scheme": (r"scheme", r"field-configuration"),
    "project-administration": (r"^rest-api-3-project(?:-|$)",),
    "webhook": (r"webhook",),
    "attachment": (r"attachment",),
    "notification": (r"notification", r"notify"),
    "sprint-move": (r"(?:move-issues|move.*sprint|sprint.*move)",),
    "ranking": (
        r"(?:^|-)rank(?:ed|ing|s)?(?:-|$)",
        r"(?:^|-)move(?:d|s|ing)?(?:-|$)",
    ),
}

# Governor-proved misses remain explicit even when a broader auditable category also matches.
HIGH_RISK_OPERATION_OVERRIDES = {
    "add-security-level",
    "add-security-level-members",
    "archive-issues",
    "archive-issues-async",
    "associate-projects-to-field-association-schemes",
    "merge-versions",
    "remove-associations",
    "remove-issues-from-epic",
    "remove-level",
    "remove-member-from-security-level",
    "set-default-levels",
    "set-field-configuration-scheme-mapping",
    "unarchive-issues",
}

PROJECT_ADMINISTRATION_COMMANDS = {
    "assign-projects-to-custom-field-context",
    "create-component",
    "create-related-work",
    "create-version",
    "update-component",
    "update-related-work",
    "update-version",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slug(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", value)
    value = re.sub(r"[^A-Za-z0-9]+", "-", value)
    return value.strip("-").lower()


def resolve_ref(spec: dict[str, Any], value: Any) -> Any:
    if not isinstance(value, dict) or "$ref" not in value:
        return value
    ref = value["$ref"]
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return value
    current: Any = spec
    for part in ref[2:].split("/"):
        current = current[part.replace("~1", "/").replace("~0", "~")]
    return current


def schema_type(spec: dict[str, Any], schema: Any) -> str:
    schema = resolve_ref(spec, schema)
    if not isinstance(schema, dict):
        return "string"
    if "type" in schema:
        return str(schema["type"])
    if "oneOf" in schema or "anyOf" in schema:
        return "union"
    return "object"


def compact_text(value: Any, limit: int = 280) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def access_classification(path: str, operation: dict[str, Any]) -> tuple[str, str]:
    text = " ".join(
        [str(operation.get("summary") or ""), str(operation.get("description") or "")]
    ).lower()
    if path.startswith("/rest/operations/"):
        return "intentionally-excluded", "Jira Operations is outside the selected product boundary."
    if "service-registry" in path:
        return (
            "intentionally-excluded",
            "Jira Service Management is outside the selected product boundary.",
        )
    if path.startswith("/rest/forge/") or "only forge" in text or "forge apps only" in text:
        return "access-gated-forge", "Requires a Forge app credential or runtime."
    if (
        path.startswith("/rest/atlassian-connect/")
        or "only connect" in text
        or "connect apps only" in text
    ):
        return "access-gated-connect", "Requires an Atlassian Connect app credential or runtime."
    if "experimental" in text:
        return "developer-preview", "Official description marks this operation experimental."
    if operation.get("deprecated"):
        return "implemented-deprecated", "Official description marks this operation deprecated."
    security = operation.get("security")
    if isinstance(security, list) and security:
        names = {name for option in security if isinstance(option, dict) for name in option}
        if names and "basicAuth" not in names and "OAuth2" in names:
            return "implemented-oauth-only", "Requires the supported OAuth 2.0 bearer path."
    return (
        "implemented-live-unverified",
        "Implemented from the pinned official description; no live Jira call was run.",
    )


def operation_kind(method: str, operation_id: str, summary: str) -> str:
    if method in {"GET", "HEAD", "OPTIONS"}:
        return "read"
    if method == "POST":
        if operation_id in READ_POST_OPERATION_IDS:
            return "read"
        normalized = re.sub(r"[^a-z]", "", operation_id.lower())
        if normalized.startswith(READ_POST_PREFIXES):
            return "read"
        summary_words = summary.lower().split()
        if summary_words and summary_words[0] in READ_POST_PREFIXES:
            return "read"
    return "write"


def high_risk_reasons(
    *, kind: str, method: str, path: str, command: str, operation_id: str, summary: str
) -> list[str]:
    if kind != "write":
        return []
    searchable = slug(" ".join((path, command, operation_id, summary)))
    reasons = [
        category
        for category, patterns in HIGH_RISK_PATTERNS.items()
        if any(re.search(pattern, searchable) for pattern in patterns)
    ]
    if method == "DELETE" and "destructive" not in reasons:
        reasons.append("destructive")
    if command in PROJECT_ADMINISTRATION_COMMANDS:
        reasons.append("project-administration")
    if command in HIGH_RISK_OPERATION_OVERRIDES:
        reasons.append("explicit-audit-override")
    return sorted(set(reasons))


def normalized_parameters(
    spec: dict[str, Any], path_parameters: list[Any], operation_parameters: list[Any]
) -> list[dict[str, Any]]:
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    for raw in [*path_parameters, *operation_parameters]:
        param = resolve_ref(spec, raw)
        if not isinstance(param, dict):
            continue
        name = str(param.get("name") or "").strip()
        location = str(param.get("in") or "").strip()
        if not name or location not in {"path", "query", "header"}:
            continue
        if location == "header" and name.lower() in {"authorization", "cookie"}:
            continue
        schema = resolve_ref(spec, param.get("schema") or {})
        is_free_form_object = (
            location == "query"
            and name == "params"
            and schema_type(spec, schema) == "object"
            and "free-form" in str(param.get("description") or "").lower()
        )
        entry = {
            "name": name,
            "cli_flag": "--" + slug(name),
            "in": location,
            "required": bool(param.get("required")) or location == "path" or is_free_form_object,
            "schema_type": schema_type(spec, schema),
            "array": isinstance(schema, dict) and schema.get("type") == "array",
            "free_form_object": is_free_form_object,
            "description": compact_text(param.get("description")),
        }
        merged[(location, name)] = entry
    return sorted(merged.values(), key=lambda item: (item["in"], item["name"]))


def build_inventory() -> dict[str, Any]:
    operations: list[dict[str, Any]] = []
    manifest_specs: list[dict[str, Any]] = []
    paths_by_surface: dict[str, set[tuple[str, str]]] = {}

    for source in SPEC_INPUTS:
        spec_path = ROOT / source["file"]
        actual_hash = sha256(spec_path)
        if actual_hash != source["sha256"]:
            raise SystemExit(f"Pinned hash mismatch for {source['file']}: {actual_hash}")
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        surface = str(source["surface"])
        surface_paths: set[tuple[str, str]] = set()
        for path, path_item in sorted(spec.get("paths", {}).items()):
            if not isinstance(path_item, dict):
                continue
            path_parameters = path_item.get("parameters") or []
            for method, operation in sorted(path_item.items()):
                if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                    continue
                http_method = method.upper()
                operation_id = str(operation.get("operationId") or f"{method}-{path}")
                command = slug(operation_id)
                status, status_note = access_classification(path, operation)
                summary = compact_text(operation.get("summary") or operation_id, 180)
                kind = operation_kind(http_method, operation_id, summary)
                risk_reasons = high_risk_reasons(
                    kind=kind,
                    method=http_method,
                    path=path,
                    command=command,
                    operation_id=operation_id,
                    summary=summary,
                )
                request_content = sorted(
                    (operation.get("requestBody", {}).get("content") or {}).keys()
                )
                response_content = sorted(
                    {
                        content_type
                        for response in (operation.get("responses") or {}).values()
                        if isinstance(resolve_ref(spec, response), dict)
                        for content_type in (
                            resolve_ref(spec, response).get("content", {}) or {}
                        ).keys()
                    }
                )
                security = operation.get("security") or spec.get("security") or []
                oauth_scopes = sorted(
                    {
                        scope
                        for option in security
                        if isinstance(option, dict)
                        for name, scopes in option.items()
                        if name == "OAuth2" and isinstance(scopes, list)
                        for scope in scopes
                    }
                )
                surface_paths.add((http_method, path))
                operations.append(
                    {
                        "surface": surface,
                        "command": command,
                        "full_command": f"jira-safe {surface} {command}",
                        "operation_id": operation_id,
                        "method": http_method,
                        "path": path,
                        "summary": summary,
                        "description": compact_text(operation.get("description")),
                        "tags": [str(tag) for tag in operation.get("tags") or []],
                        "kind": kind,
                        "high_risk": bool(risk_reasons),
                        "high_risk_reasons": risk_reasons,
                        "coverage_status": status,
                        "coverage_note": status_note,
                        "callable_with_supported_auth": status.startswith("implemented"),
                        "parameters": normalized_parameters(
                            spec, path_parameters, operation.get("parameters") or []
                        ),
                        "request_body_required": bool(
                            operation.get("requestBody", {}).get("required")
                        ),
                        "request_content_types": request_content,
                        "response_content_types": response_content,
                        "oauth_scopes": oauth_scopes,
                    }
                )
        paths_by_surface[surface] = surface_paths
        count = len(surface_paths)
        if count != source["expected_operations"]:
            raise SystemExit(
                f"Operation count mismatch for {surface}: {count} != {source['expected_operations']}"
            )
        manifest_specs.append(
            {
                **source,
                "title": spec.get("info", {}).get("title"),
                "version": spec.get("info", {}).get("version"),
                "actual_sha256": actual_hash,
                "operation_count": count,
            }
        )

    keys = [(op["surface"], op["command"]) for op in operations]
    if len(keys) != len(set(keys)):
        duplicates = [key for key, count in Counter(keys).items() if count > 1]
        raise SystemExit(f"Generated command collision: {duplicates}")
    method_paths = [(op["method"], op["path"]) for op in operations]
    if len(method_paths) != len(set(method_paths)):
        raise SystemExit("The selected specs contain overlapping method/path rows")

    callable_gets = {
        op["path"]: op
        for op in operations
        if op["method"] == "GET" and op["callable_with_supported_auth"]
    }
    for operation in operations:
        operation["snapshot_get_available"] = (
            operation["kind"] == "write"
            and operation["method"] in {"PUT", "PATCH", "DELETE"}
            and operation["path"] in callable_gets
        )
        get_operation = callable_gets.get(operation["path"])
        get_query_names = {
            parameter["name"]
            for parameter in (get_operation or {}).get("parameters", [])
            if parameter["in"] == "query"
        }
        operation["snapshot_query_names"] = sorted(
            parameter["name"]
            for parameter in operation["parameters"]
            if parameter["in"] == "query" and parameter["name"] in get_query_names
        )

    operations.sort(key=lambda item: (item["surface"], item["command"]))
    status_counts = Counter(op["coverage_status"] for op in operations)
    kind_counts = Counter(op["kind"] for op in operations)
    return {
        "schema_version": 1,
        "generated_from_pinned_specs": True,
        "pinned_date": "2026-07-27",
        "command_prefix": "jira-safe",
        "specs": manifest_specs,
        "operation_count": len(operations),
        "unique_method_path_count": len(set(method_paths)),
        "coverage_status_counts": dict(sorted(status_counts.items())),
        "kind_counts": dict(sorted(kind_counts.items())),
        "high_risk_write_count": sum(
            1 for operation in operations if operation["kind"] == "write" and operation["high_risk"]
        ),
        "operations": operations,
    }


def markdown_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_outputs(inventory: dict[str, Any]) -> None:
    inventory_path = ROOT / "src/jira_safe_agent_cli/operations.json"
    inventory_path.write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "pinned_date": inventory["pinned_date"],
        "specs": inventory["specs"],
        "operation_count": inventory["operation_count"],
        "unique_method_path_count": inventory["unique_method_path_count"],
        "high_risk_write_count": inventory["high_risk_write_count"],
    }
    (ROOT / "specs/manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    counts = inventory["coverage_status_counts"]
    lines = [
        "# Jira Cloud API coverage",
        "",
        "This is the operation-by-operation source of truth for the fixed Jira command surface.",
        "It is generated deterministically from the two pinned official OpenAPI descriptions.",
        "",
        "## Boundary",
        "",
        "- Jira Cloud Platform REST API v3: 616 operations.",
        "- Jira Software Cloud REST API: 105 operations.",
        "- Total: 721 unique method-and-path rows before access classification, with no duplicates.",
        "- Outside the product: Jira Service Management, Assets, Operations, Confluence, org-admin APIs outside the selected descriptions, Jira Data Center/Server, and undocumented endpoints.",
        "- Live Jira behavior is unverified because this build used no credential and made no provider request.",
        f"- Stronger approval is required for {inventory['high_risk_write_count']} of 360 writes.",
        "",
        "## Pinned inputs",
        "",
    ]
    for spec in inventory["specs"]:
        lines.append(
            f"- {spec['surface'].title()}: `{spec['file']}` — SHA-256 `{spec['actual_sha256']}` — {spec['operation_count']} operations — official source: {spec['url']}"
        )
    lines.extend(["", "## Classification summary", ""])
    for status, count in counts.items():
        lines.append(f"- `{status}`: {count}")
    lines.extend(
        [
            "",
            "`implemented-live-unverified`, `implemented-deprecated`, and `implemented-oauth-only` operations have fixed commands. Gated, preview, and intentionally excluded rows also keep fixed names but fail closed before any network request.",
            "",
            "## Operation ledger",
            "",
            "| Surface | Operation | Endpoint | Kind | Coverage | Snapshot/readback | Notes |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for operation in inventory["operations"]:
        snapshot = (
            "GET same path"
            if operation["snapshot_get_available"]
            else "no reliable generic snapshot"
        )
        lines.append(
            "| {surface} | `{command}` | `{method} {path}` | {kind} | `{status}` | {snapshot} | {note} |".format(
                surface=markdown_cell(operation["surface"]),
                command=markdown_cell(operation["full_command"]),
                method=operation["method"],
                path=markdown_cell(operation["path"]),
                kind=operation["kind"],
                status=operation["coverage_status"],
                snapshot=snapshot,
                note=markdown_cell(
                    operation["coverage_note"]
                    + (
                        " Stronger approval: " + ", ".join(operation["high_risk_reasons"]) + "."
                        if operation["high_risk_reasons"]
                        else ""
                    )
                ),
            )
        )
    lines.extend(
        [
            "",
            "## Regenerate and verify",
            "",
            "```bash",
            ".venv/bin/python generate_inventory.py",
            "git diff --exit-code -- specs/manifest.json src/jira_safe_agent_cli/operations.json docs/api_coverage.md",
            "```",
            "",
            "The first command verifies both hashes and both operation counts before writing deterministic outputs. The second proves a clean regeneration when the tracked outputs already match.",
        ]
    )
    (ROOT / "docs/api_coverage.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    write_outputs(build_inventory())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
