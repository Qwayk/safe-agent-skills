from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .manual_contracts import (
    apply_parameter_contract,
    apply_request_contract,
    load_manual_contracts,
    public_manual_metadata,
)

PINNED_REPOSITORY = "https://github.com/twilio/twilio-oai"
PINNED_COMMIT = "ef1d81e7b6e49e602530601e913eedc21aedd6da"
CATALOG_SCHEMA_VERSION = 1

HTTP_METHODS = ("get", "post", "delete", "put", "patch")
METHOD_ORDER = {method.upper(): index for index, method in enumerate(HTTP_METHODS)}
LEGACY_EOL_FAMILIES = frozenset({"chat", "ip_messaging", "notify"})
LEGACY_EOL_REASONS = {
    "chat": "Programmable Chat is past EOL; use the supported Conversations API.",
    "ip_messaging": "IP Messaging is past EOL; use the supported Conversations API.",
    "notify": "Twilio Notify reached EOL on 2025-12-31 and is no longer supported.",
}
SCHEDULED_EOL_DATES = {
    "frontline": "2026-09-30",
}
VERSION_COMPARISONS = (
    ("chat", "chat-v1", "chat-v2", 16),
    ("ip_messaging", "ip-messaging-v1", "ip-messaging-v2", 16),
    ("studio", "studio-v1", "studio-v2", 6),
    ("pricing", "pricing-v1", "pricing-v2", 1),
)

SNAPSHOT_STRATEGIES = frozenset(
    {
        "none_read",
        "fetch_before_change",
        "fetch_before_delete",
        "no_snapshot_action",
        "no_snapshot_create",
    }
)
VERIFICATION_STRATEGIES = frozenset(
    {
        "confirm_absent_or_terminal",
        "fetch_created_resource_or_provider_status",
        "inspect_response",
        "provider_status_or_response",
        "refetch_changed_resource",
    }
)

_CONTRACT_DOC_KEYS = frozenset(
    {"description", "summary", "examples", "example", "tags", "title"}
)
_PRODUCTION_FAMILIES = frozenset(
    {"flex", "proxy", "routes", "serverless", "studio", "taskrouter", "trunking", "voice"}
)
_PRODUCTION_TOKENS = (
    "application",
    "build",
    "callback",
    "call",
    "campaign",
    "channel-sender",
    "conference",
    "configuration",
    "deployment",
    "environment",
    "execution",
    "flow",
    "geo-permission",
    "geopermission",
    "messaging-service",
    "participant",
    "route",
    "short-code",
    "sink",
    "sip",
    "stream",
    "subscription",
    "task-queue",
    "trunk",
    "us-app-to-person",
    "webhook",
    "worker",
    "workspace",
)
_IDENTITY_COMPLIANCE_TOKENS = (
    "a2p",
    "brand",
    "bundle",
    "campaign",
    "compliance",
    "end-user",
    "geo-permission",
    "geopermission",
    "porting",
    "regulatory",
    "sender-id-registration",
    "supporting-document",
    "toll-free",
    "tollfree",
    "us-app-to-person",
)
_SPEND_TOKENS = (
    "campaign",
    "hosted-number",
    "incoming-phone-number",
    "lookup",
    "payments",
    "phone-number",
    "purchase",
    "recording",
    "short-code",
    "siprec",
    "stream",
    "toll-free",
    "tollfree",
    "transcription",
    "us-app-to-person",
)


def resolve_spec_dir(spec_root: Path | str) -> Path:
    """Return the directory containing the pinned Twilio JSON specifications."""

    root = Path(spec_root).expanduser().resolve()
    candidates = (root, root / "spec" / "json", root / "json")
    for candidate in candidates:
        if candidate.is_dir() and any(candidate.glob("twilio_*.json")):
            return candidate
    raise FileNotFoundError(
        f"No twilio_*.json specifications found under {root} or its spec/json directory"
    )


def operation_id_to_kebab(operation_id: str) -> str:
    """Convert one OpenAPI operationId to its fixed command suffix."""

    value = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", operation_id)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", value)
    value = re.sub(r"[^A-Za-z0-9]+", "-", value)
    return value.strip("-").lower()


def build_inventory(spec_root: Path | str) -> dict[str, Any]:
    """Build the deterministic operation catalog from a Twilio OpenAPI checkout."""

    spec_dir = resolve_spec_dir(spec_root)
    spec_paths = sorted(spec_dir.glob("twilio_*.json"), key=lambda path: path.name)
    if len(spec_paths) != 60:
        raise ValueError(f"Expected 60 pinned JSON specs, found {len(spec_paths)} in {spec_dir}")

    documents: dict[str, dict[str, Any]] = {}
    spec_hashes: dict[str, str] = {}
    spec_file_rows: list[dict[str, Any]] = []
    method_counts: Counter[str] = Counter()
    path_count = 0
    raw_operation_count = 0

    for spec_path in spec_paths:
        raw = spec_path.read_bytes()
        document = json.loads(raw)
        if not isinstance(document, dict) or not isinstance(document.get("paths"), dict):
            raise ValueError(f"Invalid OpenAPI paths object in {spec_path.name}")
        documents[spec_path.name] = document
        digest = hashlib.sha256(raw).hexdigest()
        spec_hashes[spec_path.name] = digest
        operations_in_file = sum(
            1
            for path_item in document["paths"].values()
            for method in HTTP_METHODS
            if method in path_item
        )
        for path_item in document["paths"].values():
            for method in HTTP_METHODS:
                if method in path_item:
                    method_counts[method.upper()] += 1
        path_count += len(document["paths"])
        raw_operation_count += operations_in_file
        spec_file_rows.append(
            {
                "filename": spec_path.name,
                "operation_count": operations_in_file,
                "path_count": len(document["paths"]),
                "sha256": digest,
                "source_spec": f"spec/json/{spec_path.name}",
            }
        )

    _validate_boundary(path_count, raw_operation_count, method_counts)
    exact_duplicates, duplicate_summary = _find_version_duplicates(documents)
    manual_contracts = load_manual_contracts()

    rows: list[dict[str, Any]] = []
    for filename in sorted(documents):
        document = documents[filename]
        family, version, spec_id = _spec_identity(filename)
        for literal_path, path_item in document["paths"].items():
            for method in HTTP_METHODS:
                if method not in path_item:
                    continue
                operation = path_item[method]
                operation_id = str(operation.get("operationId") or "").strip()
                if not operation_id:
                    raise ValueError(f"Missing operationId: {filename} {method.upper()} {literal_path}")
                row = _build_operation_row(
                    filename=filename,
                    source_sha256=spec_hashes[filename],
                    document=document,
                    family=family,
                    version=version,
                    spec_id=spec_id,
                    literal_path=literal_path,
                    path_item=path_item,
                    method=method,
                    operation=operation,
                    exact_duplicates=exact_duplicates,
                    manual_contracts=manual_contracts,
                )
                rows.append(row)

    rows.sort(
        key=lambda row: (
            row["source_filename"],
            row["path"],
            METHOD_ORDER[row["method"]],
            row["operation_id"],
        )
    )
    disposition_counts = Counter(row["disposition"] for row in rows)
    expected_dispositions = {
        "command": 1_333,
        "legacy_eol": 205,
        "canonical_duplicate": 9,
        "developer_preview": 1,
        "private_or_unavailable": 6,
    }
    if dict(disposition_counts) != expected_dispositions:
        raise ValueError(
            f"Unexpected disposition totals: {dict(disposition_counts)}; "
            f"expected {expected_dispositions}"
        )
    commands = [row["command"] for row in rows if row["disposition"] == "command"]
    if len(commands) != len(set(commands)):
        duplicates = sorted(name for name, count in Counter(commands).items() if count > 1)
        raise ValueError(f"Generated command names are not unique: {duplicates}")

    catalog = {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "source": {
            "commit": PINNED_COMMIT,
            "methods": dict(sorted(method_counts.items())),
            "operation_count": raw_operation_count,
            "path_count": path_count,
            "repository": PINNED_REPOSITORY,
            "spec_count": len(spec_paths),
            "spec_files": spec_file_rows,
        },
        "counts": {
            "canonical_duplicate": disposition_counts["canonical_duplicate"],
            "command": disposition_counts["command"],
            "developer_preview": disposition_counts["developer_preview"],
            "legacy_eol": disposition_counts["legacy_eol"],
            "private_or_unavailable": disposition_counts["private_or_unavailable"],
            "raw_operations": len(rows),
        },
        "duplicate_analysis": duplicate_summary,
        "operations": rows,
    }
    # Manual schemas use immutable tuples in source for reviewability. Normalize the public
    # catalog to JSON-native lists so the in-memory build and checked-in artifact are identical.
    return json.loads(json.dumps(catalog, ensure_ascii=False))


def serialize_catalog(catalog: Mapping[str, Any]) -> str:
    return json.dumps(catalog, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_outputs(
    spec_root: Path | str,
    *,
    catalog_path: Path | str,
    coverage_path: Path | str,
) -> dict[str, Any]:
    """Generate and write both packaged inventory outputs."""

    catalog = build_inventory(spec_root)
    catalog_destination = Path(catalog_path)
    coverage_destination = Path(coverage_path)
    catalog_destination.parent.mkdir(parents=True, exist_ok=True)
    coverage_destination.parent.mkdir(parents=True, exist_ok=True)
    catalog_destination.write_text(serialize_catalog(catalog), encoding="utf-8")
    coverage_destination.write_text(render_coverage(catalog), encoding="utf-8")
    return catalog


def render_coverage(catalog: Mapping[str, Any]) -> str:
    """Render the human-inspectable coverage page from the exact catalog rows."""

    source = catalog["source"]
    counts = catalog["counts"]
    duplicate_analysis = catalog["duplicate_analysis"]
    operations = catalog["operations"]
    lines = [
        "# Twilio API coverage",
        "",
        "This file is generated from the pinned official Twilio OpenAPI checkout. It keeps one row "
        "for every raw HTTP operation so the command boundary and every non-command decision can "
        "be checked without guessing.",
        "",
        "Do not edit the tables by hand. Regenerate them with `scripts/generate_twilio_inventory.py`.",
        "",
        "## Pinned boundary",
        "",
        f"- Repository: `{source['repository']}`",
        f"- Commit: `{source['commit']}`",
        f"- JSON specifications: **{source['spec_count']:,}**",
        f"- Paths: **{source['path_count']:,}**",
        f"- Raw operations: **{source['operation_count']:,}**",
        "- HTTP methods: "
        + ", ".join(
            f"{method.upper()} {source['methods'][method.upper()]:,}" for method in HTTP_METHODS
        ),
        "",
        "## Boundary decisions",
        "",
        "Every raw operation has one of five dispositions. `command` rows receive one fixed command "
        "name. `legacy_eol` covers Chat, IP Messaging, Notify, and the removed Studio v1 Engagement. "
        "`canonical_duplicate` covers seven exact older Studio or Pricing contracts plus two deprecated "
        "Preview Marketplace writes superseded by Marketplace v1. `developer_preview` and "
        "`private_or_unavailable` rows ship no command only where current official evidence does not "
        "provide a stable callable request contract.",
        "",
        "The pinned OpenAPI contained 81 writes with at least one empty or untyped request section. "
        "Each was audited against current official Twilio docs and Twilio-owned product schemas. "
        "Seventy-one now use operation-specific manual supplements to expose callable schemas; the "
        "remaining audited rows retain explicit non-command dispositions. Flexible JSON is allowed only "
        "inside the exact documented field; restricted commands reject optional undocumented branches. "
        "Every audited row carries its official evidence in the table.",
        "",
        "The full-contract comparison found "
        f"**{duplicate_analysis['full_contract_pairs']}** exact older/newer pairs: Chat "
        f"{duplicate_analysis['by_family']['chat']}, IP Messaging "
        f"{duplicate_analysis['by_family']['ip_messaging']}, Studio "
        f"{duplicate_analysis['by_family']['studio']}, and Pricing "
        f"{duplicate_analysis['by_family']['pricing']}. The 32 Chat and IP Messaging pairs stay "
        "`legacy_eol`; they are not relabeled as duplicates.",
        "Notify stays `legacy_eol` because Twilio ended the product on 2025-12-31. The removed Studio "
        "v1 Engagement endpoint is also recorded as legacy rather than as a schema gap.",
        "Frontline's two operations remain command rows for existing customers until its scheduled "
        "EOL on 2026-09-30. They are marked access-gated and scheduled-EOL so a future refresh cannot "
        "silently present them as ordinary current commands.",
        "",
        "Preview, OAuth/access-gated, and live-unverified operations remain command rows when a fixed "
        "public contract exists. The flags describe those limits; they do not hide callable operations.",
        "",
        "## Count equation",
        "",
        f"**{counts['command']:,} command + {counts['legacy_eol']:,} legacy_eol + "
        f"{counts['canonical_duplicate']:,} canonical_duplicate + "
        f"{counts['developer_preview']:,} developer_preview + "
        f"{counts['private_or_unavailable']:,} private_or_unavailable = "
        f"{counts['raw_operations']:,} raw operations**",
        "",
        "## Pinned specification files",
        "",
        "| Source spec | Paths | Operations | SHA-256 |",
        "| --- | ---: | ---: | --- |",
    ]
    for entry in source["spec_files"]:
        lines.append(
            f"| `{entry['source_spec']}` | {entry['path_count']} | {entry['operation_count']} | "
            f"`{entry['sha256']}` |"
        )

    lines.extend(
        [
            "",
            "## Per-operation coverage",
            "",
            "`Command or target` is the fixed command for a command row, the higher-version command "
            "for a canonical duplicate, and an em dash for other non-command rows.",
            "",
            "| # | Source spec | Family | Version | Method | Literal path | operationId | "
            "Disposition | Command or target | Reason | Official evidence | Flags | Source pointer |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for index, row in enumerate(operations, start=1):
        classification = row["classification"]
        flags = []
        if classification["preview"]:
            flags.append("preview")
        if classification["access_gated"]:
            flags.append("access-gated")
        if classification["deprecated"]:
            flags.append("deprecated")
        if classification["scheduled_eol"]:
            flags.append(f"scheduled-eol-{classification['scheduled_eol']}")
        if classification.get("developer_preview"):
            flags.append("developer-preview")
        if classification.get("private_or_unavailable"):
            flags.append("private-or-unavailable")
        manual_contract = row.get("manual_contract") or {}
        if manual_contract.get("restrictions"):
            flags.append("restricted-contract")
        flags.append(f"live-{classification['live_verification']}")
        command_or_target = row["command"] or row["duplicate_of"] or "—"
        sources = manual_contract.get("sources") or []
        evidence = "<br>".join(
            f"[Twilio {source_index}]({source})"
            for source_index, source in enumerate(sources, start=1)
        ) or "Pinned OpenAPI"
        lines.append(
            f"| {index} | `{row['source_spec']}` | `{row['family']}` | `{row['version']}` | "
            f"`{row['method']}` | `{_markdown_code(row['path'])}` | "
            f"`{_markdown_code(row['operation_id'])}` | `{row['disposition']}` | "
            f"`{command_or_target}` | {_markdown_code(row['disposition_reason'])} | "
            f"{evidence} | "
            f"{', '.join(flags)} | "
            f"`{_markdown_code(row['source_pointer'])}` |"
        )
    return "\n".join(lines) + "\n"


def _validate_boundary(
    path_count: int, operation_count: int, method_counts: Mapping[str, int]
) -> None:
    expected_methods = {"GET": 777, "POST": 516, "DELETE": 230, "PUT": 19, "PATCH": 12}
    if path_count != 893 or operation_count != 1_554 or dict(method_counts) != expected_methods:
        raise ValueError(
            "Supplied specs do not match the pinned boundary: "
            f"paths={path_count}, operations={operation_count}, methods={dict(method_counts)}"
        )


def _spec_identity(filename: str) -> tuple[str, str, str]:
    stem = Path(filename).stem
    if not stem.startswith("twilio_"):
        raise ValueError(f"Unexpected Twilio spec filename: {filename}")
    raw_id = stem.removeprefix("twilio_")
    spec_id = raw_id.replace("_", "-")
    version_match = re.fullmatch(r"(.+)_((?:v\d+))", raw_id)
    if version_match:
        return version_match.group(1), version_match.group(2), spec_id
    if raw_id.startswith("iam_"):
        family, variant = raw_id.split("_", 1)
        return family, variant, spec_id
    return raw_id, "unversioned", spec_id


def _build_operation_row(
    *,
    filename: str,
    source_sha256: str,
    document: Mapping[str, Any],
    family: str,
    version: str,
    spec_id: str,
    literal_path: str,
    path_item: Mapping[str, Any],
    method: str,
    operation: Mapping[str, Any],
    exact_duplicates: Mapping[tuple[str, str], str],
    manual_contracts: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, Any]:
    operation_id = str(operation["operationId"])
    command_name = f"{spec_id}.{operation_id_to_kebab(operation_id)}"
    duplicate_target = exact_duplicates.get((spec_id, operation_id))
    source_pointer = f"#/paths/{_json_pointer_escape(literal_path)}/{method}"
    parameters = _merged_parameters(path_item, operation, document)
    if spec_id == "conversations-v2":
        parameters = _replace_conversations_v2_parameters(parameters, literal_path)
    request = _request_metadata(operation, document)
    manual_contract = manual_contracts.get((filename, operation_id))
    originally_unbounded = bool(
        method.upper() != "GET"
        and request is not None
        and any(
            has_unbounded_request_schema(request["schemas"][media_type]["resolved_schema"])
            for media_type in request["media_types"]
        )
    )
    if manual_contract is not None and not originally_unbounded:
        raise ValueError(
            f"Manual-contract audit mismatch for {filename} {operation_id}: "
            "the pinned request is not unbounded"
        )
    if (
        originally_unbounded
        and manual_contract is None
        and family not in LEGACY_EOL_FAMILIES
        and duplicate_target is None
    ):
        raise ValueError(f"Unaudited unbounded request contract: {filename} {operation_id}")
    if manual_contract is not None:
        try:
            request = apply_request_contract(request, manual_contract)
            parameters = apply_parameter_contract(parameters, manual_contract)
        except ValueError as exc:
            raise ValueError(f"Manual contract failed for {filename} {operation_id}: {exc}") from exc
    if family in LEGACY_EOL_FAMILIES:
        disposition = "legacy_eol"
        command = None
        duplicate_of = None
        disposition_reason = LEGACY_EOL_REASONS[family]
    elif manual_contract is not None:
        disposition = str(manual_contract["disposition"])
        command = command_name if disposition == "command" else None
        duplicate_of = manual_contract.get("duplicate_of")
        disposition_reason = str(manual_contract["reason"])
        if disposition == "command" and request is not None and any(
            has_unbounded_request_schema(request["schemas"][media_type]["resolved_schema"])
            for media_type in request["media_types"]
        ):
            raise ValueError(f"Manual command remains unbounded: {command_name}")
        if disposition == "canonical_duplicate" and not duplicate_of:
            raise ValueError(f"Manual duplicate has no target: {spec_id}.{operation_id}")
    elif duplicate_target is not None:
        disposition = "canonical_duplicate"
        command = None
        duplicate_of = duplicate_target
        disposition_reason = f"Exact older contract; use {duplicate_target}."
    else:
        disposition = "command"
        command = command_name
        duplicate_of = None
        disposition_reason = "Distinct callable operation in the pinned boundary."

    success_responses = _success_response_metadata(operation, document)
    security = _resolved_security(document, path_item, operation)
    servers = _effective_servers(document, path_item, operation)
    pii_fields = _operation_pii_fields(
        document=document,
        source_pointer=source_pointer,
        parameters=parameters,
        request=request,
        success_responses=success_responses,
    )
    if manual_contract is not None:
        for field in manual_contract.get("pii_fields_add") or ():
            pii_fields.append(
                {
                    "field": str(field),
                    "location": "manual_contract",
                    "source_pointer": source_pointer,
                }
            )
    server = str(servers[0].get("url") or "") if servers else ""
    access_gated = family in SCHEDULED_EOL_DATES or _is_access_gated(server, security)
    preview = family == "preview" or "preview" in (urlparse(server).hostname or "").lower()
    source_deprecated = bool(operation.get("deprecated", False))
    classification = {
        "access_gated": access_gated,
        "deprecated": source_deprecated,
        "legacy_eol": disposition == "legacy_eol",
        "live_verification": "unverified",
        "preview": preview,
        "scheduled_eol": SCHEDULED_EOL_DATES.get(family),
        "developer_preview": disposition == "developer_preview",
        "private_or_unavailable": disposition == "private_or_unavailable",
    }
    if manual_contract is not None and "preview" in (manual_contract.get("risk_add") or ()):
        classification["preview"] = True
    risk_flags = _risk_flags(
        family=family,
        method=method.upper(),
        literal_path=literal_path,
        operation_id=operation_id,
        has_pii=bool(pii_fields),
    )
    if manual_contract is not None:
        risk_set = set(risk_flags)
        risk_set.difference_update(manual_contract.get("risk_remove") or ())
        risk_set.update(manual_contract.get("risk_add") or ())
        risk_flags = sorted(risk_set)
    snapshot_strategy, verification_strategy = _strategies(method.upper(), operation_id)
    if manual_contract is not None:
        snapshot_strategy = str(manual_contract.get("snapshot_strategy") or snapshot_strategy)
        verification_strategy = str(
            manual_contract.get("verification_strategy") or verification_strategy
        )
    row = {
        "classification": classification,
        "command": command,
        "disposition": disposition,
        "disposition_reason": disposition_reason,
        "duplicate_of": duplicate_of,
        "family": family,
        "method": method.upper(),
        "operation_id": operation_id,
        "parameters": parameters,
        "path": literal_path,
        "path_x_twilio": copy.deepcopy(path_item.get("x-twilio", {})),
        "pii_fields": pii_fields,
        "request": request,
        "risk_flags": risk_flags,
        "security": security,
        "server": server,
        "servers": servers,
        "snapshot_strategy": snapshot_strategy,
        "source_filename": filename,
        "source_pointer": source_pointer,
        "source_sha256": source_sha256,
        "source_spec": f"spec/json/{filename}",
        "spec_id": spec_id,
        "success_responses": success_responses,
        "verification_strategy": verification_strategy,
        "version": version,
    }
    if manual_contract is not None:
        row["manual_contract"] = public_manual_metadata(manual_contract)
        if manual_contract.get("snapshot_required") is True:
            row["snapshot_required"] = True
        if manual_contract.get("expected_effect"):
            row["expected_effect"] = str(manual_contract["expected_effect"])
    return row


def is_empty_object_schema(schema: Any) -> bool:
    """Return whether a request schema declares no safe input fields."""

    return bool(
        isinstance(schema, dict)
        and schema.get("type") == "object"
        and not schema.get("properties")
        and not schema.get("oneOf")
        and not schema.get("allOf")
        and not schema.get("anyOf")
        and not schema.get("additionalProperties")
    )


def has_unbounded_request_schema(schema: Any) -> bool:
    """Return whether any request-schema section accepts input without a fixed type or shape."""

    if not isinstance(schema, dict):
        return False
    if schema.get("x-qwayk-documented-flexible-json") is True:
        return schema.get("type") != "object"
    if isinstance(schema.get("x-qwayk-json-string"), dict):
        contract = schema["x-qwayk-json-string"]
        inner = contract.get("schema")
        return schema.get("type") != "string" or not isinstance(inner, dict) or has_unbounded_request_schema(inner)
    if not schema or schema.get("additionalProperties") is True:
        return True
    schema_type = schema.get("type")
    compositions = ("oneOf", "anyOf", "allOf")
    if (
        schema_type == "object"
        and not schema.get("properties")
        and not any(schema.get(key) for key in compositions)
        and not isinstance(schema.get("additionalProperties"), dict)
        and schema.get("additionalProperties") is not False
    ):
        return True
    if schema_type == "array" and not isinstance(schema.get("items"), dict):
        return True

    structural_keys = {
        "$ref",
        "allOf",
        "anyOf",
        "const",
        "enum",
        "items",
        "not",
        "oneOf",
        "properties",
        "type",
    }
    documentation_keys = {
        "default",
        "description",
        "example",
        "format",
        "nullable",
        "readOnly",
        "title",
        "writeOnly",
    }
    if not (set(schema) & structural_keys) and set(schema) & documentation_keys:
        return True

    properties = schema.get("properties")
    if isinstance(properties, dict) and any(
        has_unbounded_request_schema(child) for child in properties.values()
    ):
        return True
    for key in ("items", "additionalProperties", "not"):
        child = schema.get(key)
        if isinstance(child, dict) and has_unbounded_request_schema(child):
            return True
    for key in compositions:
        children = schema.get(key)
        if isinstance(children, list) and any(
            has_unbounded_request_schema(child) for child in children
        ):
            return True
    return False


def _merged_parameters(
    path_item: Mapping[str, Any], operation: Mapping[str, Any], document: Mapping[str, Any]
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    positions: dict[tuple[str, str], int] = {}
    for parameter in list(path_item.get("parameters", [])) + list(operation.get("parameters", [])):
        resolved = copy.deepcopy(_resolve_local_ref(parameter, document))
        schema = resolved.get("schema")
        if isinstance(schema, dict):
            resolved["resolved_schema"] = _resolve_schema_tree(schema, document, ref_stack=())
        key = (str(resolved.get("name", "")), str(resolved.get("in", "")))
        if key in positions:
            merged[positions[key]] = resolved
        else:
            positions[key] = len(merged)
            merged.append(resolved)
    return merged


def _replace_conversations_v2_parameters(
    parameters: list[dict[str, Any]], literal_path: str
) -> list[dict[str, Any]]:
    """Use the resource-specific names required by the current Conversations v2 contract."""

    replacements: dict[str, str] = {}
    if "/ControlPlane/Configurations/" in literal_path:
        replacements["id"] = "ConfigurationSid"
    elif "/ControlPlane/Operations/" in literal_path:
        replacements["id"] = "OperationSid"
    elif "/Conversations/" in literal_path:
        replacements["id"] = "ConversationSid"
        replacements["ConversationId"] = "ConversationSid"
        replacements["ActionId"] = "ActionSid"
        if "/Participants/" in literal_path:
            replacements["id"] = "ParticipantSid"
        elif "/Communications/" in literal_path:
            replacements["id"] = "CommunicationSid"
    for parameter in parameters:
        name = str(parameter.get("name", ""))
        if name in replacements:
            parameter["name"] = replacements[name]
    return parameters


def _request_metadata(
    operation: Mapping[str, Any], document: Mapping[str, Any]
) -> dict[str, Any] | None:
    raw_body = operation.get("requestBody")
    if raw_body is None:
        return None
    body = _resolve_local_ref(raw_body, document)
    content = body.get("content", {})
    media_types = sorted(content)
    schemas: dict[str, Any] = {}
    for media_type in media_types:
        media = content[media_type]
        raw_schema = copy.deepcopy(media.get("schema", {}))
        entry: dict[str, Any] = {
            "schema": raw_schema,
            "resolved_schema": _resolve_schema_tree(raw_schema, document, ref_stack=()),
        }
        if "encoding" in media:
            entry["encoding"] = copy.deepcopy(media["encoding"])
        schemas[media_type] = entry
    return {
        "description": str(body.get("description", "")),
        "media_types": media_types,
        "required": bool(body.get("required", False)),
        "schemas": schemas,
    }


def _resolve_schema_tree(
    value: Any,
    document: Mapping[str, Any],
    *,
    ref_stack: tuple[str, ...],
) -> Any:
    if isinstance(value, list):
        return [_resolve_schema_tree(item, document, ref_stack=ref_stack) for item in value]
    if not isinstance(value, dict):
        return copy.deepcopy(value)
    ref = value.get("$ref")
    if isinstance(ref, str):
        if ref in ref_stack:
            return {"$ref": ref}
        resolved = _resolve_pointer(document, ref)
        merged = {
            key: copy.deepcopy(item)
            for key, item in value.items()
            if key != "$ref"
        }
        resolved_value = _resolve_schema_tree(
            resolved,
            document,
            ref_stack=ref_stack + (ref,),
        )
        if isinstance(resolved_value, dict):
            resolved_value.update(
                _resolve_schema_tree(merged, document, ref_stack=ref_stack + (ref,))
            )
        return resolved_value
    return {
        key: _resolve_schema_tree(item, document, ref_stack=ref_stack)
        for key, item in value.items()
    }


def _success_response_metadata(
    operation: Mapping[str, Any], document: Mapping[str, Any]
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    success_items = [
        (str(status), response)
        for status, response in operation.get("responses", {}).items()
        if str(status).startswith("2")
    ]
    for status, raw_response in sorted(success_items, key=lambda item: item[0]):
        response = _resolve_local_ref(raw_response, document)
        content = response.get("content", {})
        media_types = sorted(content)
        schemas = {
            media_type: copy.deepcopy(content[media_type].get("schema", {}))
            for media_type in media_types
        }
        results.append(
            {
                "description": str(response.get("description", "")),
                "media_types": media_types,
                "schemas": schemas,
                "status": status,
            }
        )
    return results


def _resolved_security(
    document: Mapping[str, Any],
    path_item: Mapping[str, Any],
    operation: Mapping[str, Any],
) -> dict[str, Any]:
    requirements = copy.deepcopy(
        operation.get("security", path_item.get("security", document.get("security", []))) or []
    )
    scheme_definitions = document.get("components", {}).get("securitySchemes", {})
    schemes: dict[str, Any] = {}
    for alternative in requirements:
        for scheme_name in alternative:
            raw_definition = scheme_definitions.get(scheme_name, {})
            schemes[scheme_name] = copy.deepcopy(_resolve_local_ref(raw_definition, document))
    return {"requirements": requirements, "schemes": schemes}


def _effective_servers(
    document: Mapping[str, Any],
    path_item: Mapping[str, Any],
    operation: Mapping[str, Any],
) -> list[dict[str, Any]]:
    servers = operation.get("servers", path_item.get("servers", document.get("servers", []))) or []
    return copy.deepcopy(list(servers))


def _operation_pii_fields(
    *,
    document: Mapping[str, Any],
    source_pointer: str,
    parameters: Sequence[Mapping[str, Any]],
    request: Mapping[str, Any] | None,
    success_responses: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for index, parameter in enumerate(parameters):
        name = str(parameter.get("name") or f"parameter-{index}")
        location = f"parameter:{parameter.get('in', 'unknown')}:{name}"
        _collect_pii(
            parameter,
            document=document,
            location=location,
            field=name,
            pointer=f"{source_pointer}/parameters/{index}",
            found=found,
            ref_stack=(),
        )
    if request is not None:
        for media_type in request["media_types"]:
            schema = request["schemas"][media_type]["schema"]
            _collect_pii(
                schema,
                document=document,
                location=f"request:{media_type}",
                field="request",
                pointer=f"{source_pointer}/requestBody/content/{_json_pointer_escape(media_type)}/schema",
                found=found,
                ref_stack=(),
            )
    for response in success_responses:
        for media_type in response["media_types"]:
            schema = response["schemas"][media_type]
            _collect_pii(
                schema,
                document=document,
                location=f"response:{response['status']}:{media_type}",
                field="response",
                pointer=(
                    f"{source_pointer}/responses/{_json_pointer_escape(response['status'])}/content/"
                    f"{_json_pointer_escape(media_type)}/schema"
                ),
                found=found,
                ref_stack=(),
            )
    unique: dict[str, dict[str, Any]] = {}
    for item in found:
        key = json.dumps(item, sort_keys=True, separators=(",", ":"))
        unique[key] = item
    return sorted(
        unique.values(),
        key=lambda item: (item["location"], item["field"], item["source_pointer"]),
    )


def _collect_pii(
    node: Any,
    *,
    document: Mapping[str, Any],
    location: str,
    field: str,
    pointer: str,
    found: list[dict[str, Any]],
    ref_stack: tuple[str, ...],
) -> None:
    if isinstance(node, list):
        for index, item in enumerate(node):
            _collect_pii(
                item,
                document=document,
                location=location,
                field=field,
                pointer=f"{pointer}/{index}",
                found=found,
                ref_stack=ref_stack,
            )
        return
    if not isinstance(node, dict):
        return
    ref = node.get("$ref")
    if isinstance(ref, str):
        if ref in ref_stack:
            return
        _collect_pii(
            _resolve_pointer(document, ref),
            document=document,
            location=location,
            field=field,
            pointer=ref,
            found=found,
            ref_stack=ref_stack + (ref,),
        )
        return
    x_twilio = node.get("x-twilio")
    if isinstance(x_twilio, dict) and isinstance(x_twilio.get("pii"), dict):
        found.append(
            {
                "field": field,
                "location": location,
                "pii": copy.deepcopy(x_twilio["pii"]),
                "source_pointer": pointer,
            }
        )

    properties = node.get("properties")
    if isinstance(properties, dict):
        for property_name, property_schema in sorted(properties.items()):
            _collect_pii(
                property_schema,
                document=document,
                location=f"{location}.{property_name}",
                field=str(property_name),
                pointer=f"{pointer}/properties/{_json_pointer_escape(str(property_name))}",
                found=found,
                ref_stack=ref_stack,
            )
    for schema_key in ("items", "additionalProperties"):
        child = node.get(schema_key)
        if isinstance(child, (dict, list)):
            suffix = "[]" if schema_key == "items" else ".*"
            _collect_pii(
                child,
                document=document,
                location=f"{location}{suffix}",
                field=field,
                pointer=f"{pointer}/{schema_key}",
                found=found,
                ref_stack=ref_stack,
            )
    for schema_key in ("allOf", "anyOf", "oneOf"):
        children = node.get(schema_key)
        if isinstance(children, list):
            for index, child in enumerate(children):
                _collect_pii(
                    child,
                    document=document,
                    location=location,
                    field=field,
                    pointer=f"{pointer}/{schema_key}/{index}",
                    found=found,
                    ref_stack=ref_stack,
                )
    schema = node.get("schema")
    if isinstance(schema, (dict, list)):
        _collect_pii(
            schema,
            document=document,
            location=location,
            field=field,
            pointer=f"{pointer}/schema",
            found=found,
            ref_stack=ref_stack,
        )


def _find_version_duplicates(
    documents: Mapping[str, Mapping[str, Any]]
) -> tuple[dict[tuple[str, str], str], dict[str, Any]]:
    duplicate_targets: dict[tuple[str, str], str] = {}
    by_family: dict[str, int] = {}
    for family, older_spec_id, newer_spec_id, expected_count in VERSION_COMPARISONS:
        older_filename = f"twilio_{older_spec_id.replace('-', '_')}.json"
        newer_filename = f"twilio_{newer_spec_id.replace('-', '_')}.json"
        older_document = documents[older_filename]
        newer_document = documents[newer_filename]
        older_contracts = _operation_contracts(older_document, family)
        newer_contracts = _operation_contracts(newer_document, family)
        exact_operation_ids = sorted(
            operation_id
            for operation_id in set(older_contracts) & set(newer_contracts)
            if older_contracts[operation_id] == newer_contracts[operation_id]
        )
        if len(exact_operation_ids) != expected_count:
            raise ValueError(
                f"Expected {expected_count} exact {family} version pairs, "
                f"found {len(exact_operation_ids)}"
            )
        by_family[family] = len(exact_operation_ids)
        if family not in LEGACY_EOL_FAMILIES:
            for operation_id in exact_operation_ids:
                duplicate_targets[(older_spec_id, operation_id)] = (
                    f"{newer_spec_id}.{operation_id_to_kebab(operation_id)}"
                )
    return duplicate_targets, {
        "by_family": by_family,
        "canonical_duplicate_rows": len(duplicate_targets),
        "full_contract_pairs": sum(by_family.values()),
        "legacy_pairs_retained_as_legacy_eol": sum(
            count for family, count in by_family.items() if family in LEGACY_EOL_FAMILIES
        ),
    }


def _operation_contracts(document: Mapping[str, Any], family: str) -> dict[str, str]:
    contracts: dict[str, str] = {}
    for literal_path, path_item in document["paths"].items():
        for method in HTTP_METHODS:
            if method not in path_item:
                continue
            operation = path_item[method]
            operation_id = str(operation["operationId"])
            contract = {
                "method": method,
                "parameters": list(path_item.get("parameters", []))
                + list(operation.get("parameters", [])),
                "path": re.sub(r"^/v[12](?=/|$)", "/vX", literal_path),
                "requestBody": operation.get("requestBody"),
                "responses": {
                    str(status): response
                    for status, response in operation.get("responses", {}).items()
                    if str(status).startswith("2")
                },
                "security": operation.get(
                    "security", path_item.get("security", document.get("security", []))
                ),
            }
            normalized = _normalize_contract(contract, document, family=family, ref_stack=())
            contracts[operation_id] = json.dumps(
                normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            )
    return contracts


def _normalize_contract(
    value: Any,
    document: Mapping[str, Any],
    *,
    family: str,
    ref_stack: tuple[str, ...],
) -> Any:
    if isinstance(value, dict):
        ref = value.get("$ref")
        if isinstance(ref, str):
            if ref in ref_stack:
                return {"$ref": "#cycle"}
            return _normalize_contract(
                _resolve_pointer(document, ref),
                document,
                family=family,
                ref_stack=ref_stack + (ref,),
            )
        return {
            key: _normalize_contract(item, document, family=family, ref_stack=ref_stack)
            for key, item in sorted(value.items())
            if key not in _CONTRACT_DOC_KEYS
        }
    if isinstance(value, list):
        return [
            _normalize_contract(item, document, family=family, ref_stack=ref_stack)
            for item in value
        ]
    if isinstance(value, str):
        normalized = re.sub(
            rf"(?i){re.escape(family)}\.v[12]", f"{family}.vX", value
        )
        return re.sub(r"(?i)/v[12](?=/|$)", "/vX", normalized)
    return value


def _resolve_local_ref(value: Any, document: Mapping[str, Any]) -> Any:
    if isinstance(value, dict) and isinstance(value.get("$ref"), str):
        return _resolve_pointer(document, value["$ref"])
    return value


def _resolve_pointer(document: Mapping[str, Any], pointer: str) -> Any:
    if not pointer.startswith("#/"):
        raise ValueError(f"External OpenAPI references are not supported: {pointer}")
    value: Any = document
    for raw_part in pointer[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        value = value[part]
    return value


def _is_access_gated(server: str, security: Mapping[str, Any]) -> bool:
    hostname = (urlparse(server).hostname or "").lower()
    if hostname.startswith("preview-iam."):
        return True
    return any(
        str(definition.get("type", "")).lower() == "oauth2"
        for definition in security["schemes"].values()
    )


def _risk_flags(
    *,
    family: str,
    method: str,
    literal_path: str,
    operation_id: str,
    has_pii: bool,
) -> list[str]:
    flags = ["read" if method == "GET" else "write"]
    text = f"{operation_id} {literal_path}".lower()
    operation_words = operation_id_to_kebab(operation_id)
    hazard_text = f"{operation_words} {literal_path.lower()}"
    is_write = method != "GET"
    if has_pii:
        flags.append("sensitive_data")
    if method == "DELETE" or operation_words.startswith(("delete-", "remove-", "release-")):
        flags.append("destructive")
    active_communication_change = bool(
        is_write
        and family == "api"
        and any(segment in literal_path.lower() for segment in ("/calls", "/conferences"))
        and operation_words.startswith(
            (
                "create-call",
                "create-participant",
                "create-realtime-transcription",
                "create-siprec",
                "create-stream",
                "update-call",
                "update-conference",
                "update-participant",
                "update-realtime-transcription",
                "update-siprec",
                "update-stream",
            )
        )
    )
    contact_action = bool(
        re.search(
            r"(?:create|send|start)-(?:message|call|verification|challenge|notification)",
            operation_words,
        )
        or operation_words == "create-validation-request"
        or active_communication_change
        or (
            is_write
            and family == "conversations"
            and "/messages" in literal_path.lower()
            and operation_words.startswith("create-")
        )
        or (
            is_write
            and family == "studio"
            and any(token in operation_words for token in ("execution", "engagement"))
        )
        or (is_write and family == "supersim" and operation_words == "create-sms-command")
        or (
            is_write
            and family == "api"
            and "/calls" in literal_path.lower()
            and operation_words.startswith(("create-call", "update-call", "create-participant"))
        )
    )
    if contact_action:
        flags.extend(["outbound_contact", "spend"])
    elif family == "lookups" or (
        is_write and any(token in hazard_text for token in _SPEND_TOKENS)
    ):
        flags.append("spend")
    if is_write and (
        family in {"wireless", "supersim"}
        or (family == "preview" and "/wireless" in literal_path.lower())
    ):
        flags.append("spend")
    if is_write and family == "api" and any(token in hazard_text for token in _SPEND_TOKENS):
        flags.append("spend")
    if is_write and family == "numbers" and "hosted-number-order" in operation_words:
        flags.append("spend")
    if is_write and ("bulk" in text or "batch" in text):
        flags.append("bulk")
    if family in {"iam", "oauth"} or any(
        token in operation_words
        for token in ("access-control", "credential", "geo-permission", "geopermission", "key", "permission", "role", "token")
    ):
        flags.append("auth_or_permission")
    if family == "trusthub" or any(
        token in hazard_text for token in _IDENTITY_COMPLIANCE_TOKENS
    ):
        flags.append("identity_or_compliance")
    if is_write and (
        family in _PRODUCTION_FAMILIES
        or any(token in hazard_text for token in _PRODUCTION_TOKENS)
    ):
        flags.append("production_change")
    return sorted(set(flags))


def _strategies(method: str, operation_id: str) -> tuple[str, str]:
    operation_words = operation_id_to_kebab(operation_id)
    if method == "GET":
        return "none_read", "inspect_response"
    if method == "DELETE" or operation_words.startswith(("delete-", "remove-", "release-")):
        return "fetch_before_delete", "confirm_absent_or_terminal"
    if method in {"PUT", "PATCH"} or operation_words.startswith(("update-", "modify-")):
        return "fetch_before_change", "refetch_changed_resource"
    if operation_words.startswith(("create-", "send-", "purchase-", "start-")):
        return "no_snapshot_create", "fetch_created_resource_or_provider_status"
    return "no_snapshot_action", "provider_status_or_response"


def _json_pointer_escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _markdown_code(value: str) -> str:
    return value.replace("|", "\\|").replace("`", "\\`")
