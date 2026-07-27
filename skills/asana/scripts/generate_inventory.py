#!/usr/bin/env python3
"""Generate the fixed Asana command inventory and coverage ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "specs" / "asana_oas.yaml"
INVENTORY_PATH = ROOT / "src" / "asana_safe_agent_cli" / "inventory" / "operations.json"
MANIFEST_PATH = ROOT / "src" / "asana_safe_agent_cli" / "inventory" / "manifest.json"
COVERAGE_PATH = ROOT / "docs" / "api_coverage.md"
CHECKSUM_PATH = ROOT / "specs" / "SHA256SUMS"
PINNED_COMMIT = "56796a67a3c093eedf55fd9682357957a2ebfd85"
EXPECTED_SHA256 = "cb3b90f4e0af56035eab0c648974f625b942a28a7144aa6c2326e38ca0bb3d56"
HTTP_METHODS = ("get", "post", "put", "delete", "patch", "head", "options", "trace")

STRONG_TAG_REASONS = {
    "Access requests": "access request or permission change",
    "Agents": "production agent or automation change",
    "Attachments": "file attachment change",
    "Audit log API": "broad organization data access",
    "Budgets": "budget administration",
    "Custom field settings": "project or portfolio administration",
    "Custom fields": "workspace or project field administration",
    "Exports": "broad export operation",
    "Memberships": "membership or permission change",
    "Ooo entries": "time and availability administration",
    "Organization exports": "organization-wide export",
    "Portfolio memberships": "membership or permission change",
    "Project memberships": "membership or permission change",
    "Project portfolio settings": "portfolio access or configuration administration",
    "Project statuses": "visible collaboration or notification",
    "Rates": "rate administration",
    "Reactions": "visible collaboration or notification",
    "Roles": "role or permission change",
    "Rules": "production rule or automation change",
    "Stories": "visible collaboration or notification",
    "Status updates": "visible collaboration or notification",
    "Team memberships": "membership or permission change",
    "Teams": "team administration",
    "Timesheet approval statuses": "approval administration",
    "Time tracking categories": "time administration",
    "Time tracking entries": "time administration",
    "Webhooks": "production webhook change",
    "Workspace memberships": "membership or permission change",
    "Workspaces": "workspace administration",
}


def _load_spec() -> dict[str, Any]:
    raw = SPEC_PATH.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED_SHA256:
        raise SystemExit(
            f"Pinned spec hash mismatch: expected {EXPECTED_SHA256}, got {actual}"
        )
    loaded = yaml.safe_load(raw)
    if not isinstance(loaded, dict):
        raise SystemExit("Pinned spec must parse as an object")
    return loaded


def _resolve(spec: dict[str, Any], value: Any) -> Any:
    seen: set[str] = set()
    current = value
    while isinstance(current, dict) and isinstance(current.get("$ref"), str):
        ref = current["$ref"]
        if not ref.startswith("#/") or ref in seen:
            break
        seen.add(ref)
        target: Any = spec
        for part in ref[2:].split("/"):
            target = target[part.replace("~1", "/").replace("~0", "~")]
        current = target
    return current


def _command_name(operation_id: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", operation_id)
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value)
    return value.strip("-").lower()


def _schema_summary(spec: dict[str, Any], schema: Any) -> dict[str, Any]:
    ref = schema.get("$ref") if isinstance(schema, dict) else None
    resolved = _resolve(spec, schema)
    if not isinstance(resolved, dict):
        return {}
    props = resolved.get("properties") if isinstance(resolved.get("properties"), dict) else {}
    return {
        "ref": ref,
        "type": resolved.get("type"),
        "format": resolved.get("format"),
        "required": sorted(str(x) for x in resolved.get("required", []) if isinstance(x, str)),
        "properties": {
            str(name): {
                "type": (_resolve(spec, item) or {}).get("type")
                if isinstance(_resolve(spec, item), dict)
                else None,
                "format": (_resolve(spec, item) or {}).get("format")
                if isinstance(_resolve(spec, item), dict)
                else None,
            }
            for name, item in sorted(props.items())
        },
    }


def _parameter(spec: dict[str, Any], raw: Any) -> dict[str, Any]:
    value = _resolve(spec, raw)
    if not isinstance(value, dict):
        raise SystemExit("Invalid parameter entry in pinned spec")
    schema = _resolve(spec, value.get("schema", {}))
    if not isinstance(schema, dict):
        schema = {}
    items = _resolve(spec, schema.get("items", {}))
    if not isinstance(items, dict):
        items = {}
    return {
        "name": value.get("name"),
        "in": value.get("in"),
        "required": bool(value.get("required")),
        "type": schema.get("type"),
        "format": schema.get("format"),
        "enum": schema.get("enum"),
        "default": schema.get("default"),
        "items_type": items.get("type"),
    }


def _access_classes(text: str) -> list[str]:
    checks = (
        ("service account", "service_account"),
        ("oauth", "oauth_scope_or_app"),
        ("enterprise", "enterprise_plan"),
        ("advanced", "advanced_plan"),
        ("admin", "admin_permission"),
        ("premium", "paid_plan"),
        ("only available", "availability_gate"),
        ("restricted", "restricted_access"),
    )
    lowered = text.lower()
    return [value for needle, value in checks if needle in lowered]


def _risk(method: str, tags: list[str], operation_id: str) -> tuple[str, list[str]]:
    if method == "GET":
        reasons = [STRONG_TAG_REASONS[tag] for tag in tags if tag in {"Audit log API", "Exports", "Organization exports"}]
        return ("sensitive_read" if reasons else "read", sorted(set(reasons)))
    reasons = [STRONG_TAG_REASONS[tag] for tag in tags if tag in STRONG_TAG_REASONS]
    if method == "DELETE":
        reasons.append("destructive delete")
    lowered = operation_id.lower()
    if any(word in lowered for word in ("duplicate", "instantiate", "bulk", "multiple")):
        reasons.append("bulk or fan-out action")
    if any(word in lowered for word in ("follower", "notification")):
        reasons.append("visible collaboration or notification")
    return ("write_stronger_approval" if reasons else "write", sorted(set(reasons)))


def _response_is_binary(spec: dict[str, Any], responses: Any) -> bool:
    if not isinstance(responses, dict):
        return False
    for response in responses.values():
        resolved = _resolve(spec, response)
        if not isinstance(resolved, dict):
            continue
        content = resolved.get("content")
        if not isinstance(content, dict):
            continue
        for media_type, media in content.items():
            schema = _resolve(spec, media.get("schema", {})) if isinstance(media, dict) else {}
            if media_type == "application/octet-stream":
                return True
            if isinstance(schema, dict) and schema.get("format") == "binary":
                return True
    return False


def _request_body(spec: dict[str, Any], raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    value = _resolve(spec, raw)
    if not isinstance(value, dict):
        return None
    content = value.get("content") if isinstance(value.get("content"), dict) else {}
    media: dict[str, Any] = {}
    for media_type, media_value in sorted(content.items()):
        schema = media_value.get("schema", {}) if isinstance(media_value, dict) else {}
        media[media_type] = _schema_summary(spec, schema)
    return {"required": bool(value.get("required")), "content": media}


def _build() -> tuple[dict[str, Any], dict[str, Any], str, str]:
    spec = _load_spec()
    paths = spec.get("paths")
    if not isinstance(paths, dict):
        raise SystemExit("Pinned spec has no paths object")
    operations: list[dict[str, Any]] = []
    tag_descriptions = {
        str(tag.get("name")): str(tag.get("description") or "")
        for tag in spec.get("tags", [])
        if isinstance(tag, dict) and tag.get("name")
    }
    operation_ids: set[str] = set()
    command_names: set[str] = set()
    path_methods = {
        (path, method.upper())
        for path, path_item in paths.items()
        if isinstance(path_item, dict)
        for method in HTTP_METHODS
        if method in path_item
    }
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        common_params = path_item.get("parameters", [])
        for method_lower in HTTP_METHODS:
            raw_operation = path_item.get(method_lower)
            if not isinstance(raw_operation, dict):
                continue
            method = method_lower.upper()
            operation_id = str(raw_operation.get("operationId") or "")
            if not operation_id or operation_id in operation_ids:
                raise SystemExit(f"Missing or duplicate operationId at {method} {path}")
            operation_ids.add(operation_id)
            command = _command_name(operation_id)
            if command in command_names:
                raise SystemExit(f"Command collision: {command}")
            command_names.add(command)
            tags = [str(x) for x in raw_operation.get("tags", [])]
            operation_text = " ".join(
                str(raw_operation.get(key) or "") for key in ("summary", "description")
            )
            tag_text = " ".join(tag_descriptions.get(tag, "") for tag in tags)
            text = f"{operation_text} {tag_text}".strip()
            risk_class, risk_reasons = _risk(method, tags, operation_id)
            excluded = method == "POST" and path == "/batch"
            access = _access_classes(text)
            lowered_text = text.lower()
            preview = bool(
                "api is in *preview*" in lowered_text
                or "developer preview" in lowered_text
                or "expected to change" in lowered_text
            )
            deprecated = bool(
                raw_operation.get("deprecated")
                or "*deprecated" in operation_text.lower()
                or tag_text.lstrip().lower().startswith("*deprecated")
            )
            if preview and method != "GET":
                risk_class = "write_stronger_approval"
                risk_reasons = sorted({*risk_reasons, "developer-preview operation"})
            parameters_raw = [*common_params, *raw_operation.get("parameters", [])]
            parameters = [_parameter(spec, item) for item in parameters_raw]
            request_body = _request_body(spec, raw_operation.get("requestBody"))
            security = raw_operation.get("security", spec.get("security", []))
            oauth_scopes = sorted(
                {
                    str(scope)
                    for requirement in security
                    if isinstance(requirement, dict)
                    for scope in requirement.get("oauth2", [])
                }
            )
            auth_schemes = sorted(
                {
                    str(scheme)
                    for requirement in security
                    if isinstance(requirement, dict)
                    for scheme in requirement
                }
            )
            has_same_path_get = (path, "GET") in path_methods
            pagination_names = {str(p.get("name")) for p in parameters if p.get("in") == "query"}
            async_operation = bool(
                set(tags) & {"Jobs", "Exports", "Organization exports"}
                or "asynchronous" in text.lower()
                or "async" in text.lower()
            )
            status = (
                "intentionally_excluded"
                if excluded
                else "implemented_developer_preview_live_unverified"
                if preview
                else "implemented_deprecated_live_unverified"
                if deprecated
                else "implemented_access_gated_live_unverified"
                if access
                else "implemented_live_unverified"
            )
            operations.append(
                {
                    "access": access,
                    "async": async_operation,
                    "auth": "bearer",
                    "auth_schemes": auth_schemes,
                    "command": None if excluded else command,
                    "deprecated": deprecated,
                    "excluded_reason": (
                        "Arbitrary relative-path batch bridge is outside the fixed-command product boundary."
                        if excluded
                        else None
                    ),
                    "family": tags[0] if tags else "Untagged",
                    "method": method,
                    "operation_id": operation_id,
                    "oauth_scopes": oauth_scopes,
                    "pagination": bool({"limit", "offset"} & pagination_names),
                    "parameters": parameters,
                    "path": path,
                    "preview": preview,
                    "request_body": request_body,
                    "response_binary": _response_is_binary(spec, raw_operation.get("responses")),
                    "risk_class": risk_class,
                    "risk_reasons": risk_reasons,
                    "snapshot_operation_id": (
                        next(
                            (
                                str(paths[path]["get"].get("operationId"))
                                for _ in (0,)
                                if has_same_path_get and method in {"PUT", "DELETE"}
                            ),
                            None,
                        )
                    ),
                    "status": status,
                    "summary": str(raw_operation.get("summary") or "").strip(),
                    "tags": tags,
                    "verification_operation_id": (
                        str(paths[path]["get"].get("operationId"))
                        if has_same_path_get and method in {"PUT", "DELETE"}
                        else None
                    ),
                }
            )

    method_counts = Counter(op["method"] for op in operations)
    status_counts = Counter(op["status"] for op in operations)
    families = sorted({str(op["family"]) for op in operations})
    manifest = {
        "api_version": "1.0",
        "command_count": sum(op["command"] is not None for op in operations),
        "family_count": len(families),
        "method_counts": dict(sorted(method_counts.items())),
        "openapi": spec.get("openapi"),
        "operation_count": len(operations),
        "path_count": len(paths),
        "pinned_commit": PINNED_COMMIT,
        "server": "https://app.asana.com/api/1.0",
        "sha256": EXPECTED_SHA256,
        "status_counts": dict(sorted(status_counts.items())),
    }
    inventory = {"manifest": manifest, "operations": operations}
    coverage = _coverage_markdown(manifest, operations)
    checksum = f"{EXPECTED_SHA256}  asana_oas.yaml\n"
    return inventory, manifest, coverage, checksum


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _coverage_markdown(manifest: dict[str, Any], operations: list[dict[str, Any]]) -> str:
    lines = [
        "# Asana REST API coverage",
        "",
        "This ledger accounts for every callable operation in Asana's pinned official REST specification.",
        "The command column names the fixed CLI command; it never accepts a method, URL, or arbitrary path.",
        "",
        "## Pinned boundary",
        "",
        f"- Official source: `Asana/openapi` commit `{manifest['pinned_commit']}`",
        "- File: `defs/asana_oas.yaml` (vendored as `specs/asana_oas.yaml`)",
        f"- SHA-256: `{manifest['sha256']}`",
        f"- Paths: **{manifest['path_count']}**",
        f"- Operations: **{manifest['operation_count']}**",
        f"- Tagged REST families: **{manifest['family_count']}**",
        f"- Shipped fixed commands: **{manifest['command_count']}**",
        "- App Components and SCIM: outside this product boundary",
        "- Live Asana proof: not run; every shipped operation is live-unverified",
        "",
        "## Classification key",
        "",
        "- `implemented_live_unverified`: fixed command is shipped from the official spec; no live credential was used.",
        "- `implemented_access_gated_live_unverified`: fixed command is shipped, but official text identifies a plan, permission, OAuth-app, admin, or service-account gate.",
        "- `implemented_developer_preview_live_unverified`: fixed command is shipped, but Asana marks the family as preview and subject to change.",
        "- `implemented_deprecated_live_unverified`: fixed command is shipped for boundary completeness, but Asana directs new integrations to a replacement family.",
        "- `intentionally_excluded`: represented in the ledger but not callable by product choice.",
        "",
        "## Operation ledger",
        "",
        "| Family | Method | Path | Operation ID | Fixed command | Status | Risk / access |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for op in operations:
        access = ", ".join(op["access"]) if op["access"] else "standard bearer access"
        risk = f"{op['risk_class']}; {access}"
        if op["excluded_reason"]:
            risk = op["excluded_reason"]
        lines.append(
            "| "
            + " | ".join(
                _cell(value)
                for value in (
                    op["family"],
                    op["method"],
                    f"`{op['path']}`",
                    f"`{op['operation_id']}`",
                    f"`asana-safe api {op['command']}`" if op["command"] else "—",
                    f"`{op['status']}`",
                    risk,
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Intentional exclusions",
            "",
            "`POST /batch` is the only operation inside the pinned REST file that is not shipped as a command.",
            "It accepts arbitrary relative paths, which would recreate the raw-request bridge forbidden by the product boundary.",
            "Its underlying REST operations remain available through their own fixed commands.",
            "",
            "App Components use a separate official specification and SCIM uses a separate `/scim` surface; neither is part of these counts.",
            "",
        ]
    )
    return "\n".join(lines)


def _serialized_outputs() -> dict[Path, str]:
    inventory, manifest, coverage, checksum = _build()
    return {
        INVENTORY_PATH: json.dumps(inventory, indent=2, sort_keys=True) + "\n",
        MANIFEST_PATH: json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        COVERAGE_PATH: coverage,
        CHECKSUM_PATH: checksum,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if generated files differ")
    args = parser.parse_args()
    outputs = _serialized_outputs()
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            print("Generated files are stale: " + ", ".join(stale), file=sys.stderr)
            return 1
        print("Generated inventory is current.")
        return 0
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(
        f"Generated {outputs[MANIFEST_PATH].count(chr(10))} manifest lines and "
        f"{json.loads(outputs[MANIFEST_PATH])['command_count']} fixed commands."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
