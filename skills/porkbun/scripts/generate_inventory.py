from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any

ALLOWED_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def _load_policy(path: Path) -> dict[str, Any]:
    payload = _load_json(path)
    for key in [
        "api_version",
        "spec_sha256",
        "family_slug_map",
        "family_order",
        "write_operations",
        "billable_operations",
        "terms_required_operations",
        "secret_bearing_results",
        "native_dry_run_operations",
        "destructive_operations",
        "write_snapshot_policy",
    ]:
        if key not in payload:
            raise ValueError(f"Missing required policy key: {key} in {path}")
    return payload


def _sha256_bytes(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _to_kebab(value: str) -> str:
    s = str(value or "")
    if not s:
        return ""
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s)
    s = s.replace("_", "-")
    s = re.sub(r"-{2,}", "-", s)
    return s.lower()


def _normalize_parameter(entry: dict[str, Any]) -> dict[str, Any]:
    schema = entry.get("schema")
    if isinstance(schema, dict):
        schema = {
            k: schema.get(k)
            for k in ("type", "format", "$ref", "enum", "items", "properties", "required", "additionalProperties")
            if k in schema
        }
    return {
        "name": str(entry.get("name") or "").strip(),
        "in": str(entry.get("in") or "").strip(),
        "required": bool(entry.get("required")),
        "description": (str(entry.get("description") or "").strip() or None),
        "schema": schema,
    }


def _extract_parameters(operation: dict[str, Any], path_item: dict[str, Any]) -> list[dict[str, Any]]:
    params: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for source in (path_item.get("parameters"), operation.get("parameters")):
        if not isinstance(source, list):
            continue
        for raw in source:
            if not isinstance(raw, dict):
                continue
            entry = _normalize_parameter(raw)
            name = entry["name"]
            location = entry["in"]
            if not name or not location:
                continue
            key = (location, name)
            if key in seen:
                continue
            seen.add(key)
            params.append(entry)
    return sorted(params, key=lambda p: (p["in"], p["name"]))


def _schema_summary(schema: Any) -> dict[str, Any] | None:
    if not isinstance(schema, dict):
        return None
    out: dict[str, Any] = {}
    if "$ref" in schema:
        out["ref"] = str(schema["$ref"])
    if "type" in schema:
        out["type"] = schema["type"]
    if "format" in schema:
        out["format"] = schema["format"]
    if "required" in schema:
        out["required_fields"] = schema.get("required")
    if "properties" in schema and isinstance(schema["properties"], dict):
        out["property_count"] = len(schema["properties"])
    if "items" in schema:
        out["items"] = "array"
    if "allOf" in schema:
        out["has_all_of"] = True
        try:
            out["all_of_count"] = len(schema.get("allOf") or [])
        except TypeError:
            out["all_of_count"] = 0
    return out


def _extract_content_schemas(content: dict[str, Any] | None) -> dict[str, Any]:
    schemas: dict[str, dict[str, Any]] = {}
    media_types: list[str] = []
    if not isinstance(content, dict):
        return {"media_types": [], "schemas": {}}
    for media_type in sorted(content):
        media_obj = content[media_type]
        if not isinstance(media_type, str) or not isinstance(media_obj, dict):
            continue
        media_types.append(media_type)
        schema = media_obj.get("schema")
        if isinstance(schema, dict):
            schemas[media_type] = {
                "full_schema": schema,
                "schema_summary": _schema_summary(schema),
            }
        else:
            schemas[media_type] = {"full_schema": None, "schema_summary": None}
    return {"media_types": media_types, "schemas": schemas}


def _extract_request_body(operation: dict[str, Any]) -> dict[str, Any]:
    raw = operation.get("requestBody")
    if not isinstance(raw, dict):
        return {"required": False, "media_types": [], "schemas": {}}

    content = raw.get("content") if isinstance(raw, dict) else None
    out = _extract_content_schemas(content if isinstance(content, dict) else None)
    out["required"] = bool(raw.get("required"))
    return out


def _extract_response(operation: dict[str, Any]) -> dict[str, Any]:
    raw = operation.get("responses")
    if not isinstance(raw, dict):
        return {"status_code": None, "media_types": [], "schemas": {}}

    status_codes = [str(k) for k in raw.keys() if str(k).isdigit() or str(k) == "default"]
    status_codes = sorted(
        status_codes,
        key=lambda x: (0, int(x)) if x.isdigit() and int(x) else (1, 999),
    )
    status = status_codes[0] if status_codes else "default"
    block = raw.get(status)
    if not isinstance(block, dict):
        return {"status_code": status, "media_types": [], "schemas": {}}
    return {
        "status_code": status,
        **_extract_content_schemas(block.get("content") if isinstance(block, dict) else None),
    }


def _read_policy_list(policy: dict[str, Any], key: str) -> frozenset[str]:
    value = policy.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"Policy key must be a list: {key}")
    return frozenset(str(v) for v in value if str(v).strip())


def _operation_to_command(family_slug: str, operation_id: str) -> str:
    return f"porkbun {family_slug} {_to_kebab(operation_id)}"


def generate_inventory(spec_path: Path, policy_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    policy = _load_policy(policy_path)
    openapi = _load_json(spec_path)
    paths = openapi.get("paths")
    if not isinstance(paths, dict):
        raise ValueError(f"Missing paths in {spec_path}")

    write_ops = _read_policy_list(policy, "write_operations")
    secret_ops = _read_policy_list(policy, "secret_bearing_results")
    dry_run_ops = _read_policy_list(policy, "native_dry_run_operations")
    billable_ops = _read_policy_list(policy, "billable_operations")
    terms_ops = _read_policy_list(policy, "terms_required_operations")
    destructive_ops = _read_policy_list(policy, "destructive_operations")
    snapshot_policy_map = policy.get("write_snapshot_policy", {})
    if not isinstance(snapshot_policy_map, dict):
        raise ValueError("snapshot_policy must be a mapping")
    family_slug_map = {k: str(v) for k, v in policy["family_slug_map"].items()}
    family_order = list(policy["family_order"])
    family_rank = {slug: i for i, slug in enumerate(family_order)}

    operations: list[dict[str, Any]] = []
    path_count = 0
    global_security = openapi.get("security")
    info_version = openapi.get("info", {}).get("version", "")
    for path in sorted(paths):
        path_item = paths[path]
        if not isinstance(path_item, dict):
            continue
        has_method = False
        for method in sorted(path_item):
            if method.lower() not in ALLOWED_METHODS:
                continue
            has_method = True
            method_obj = path_item[method]
            if not isinstance(method_obj, dict):
                continue
            operation_id = str(method_obj.get("operationId") or "").strip()
            if not operation_id:
                continue
            tags = method_obj.get("tags") or []
            if not isinstance(tags, list) or not tags:
                raise ValueError(f"Missing tags for {method.upper()} {path}")
            raw_family = str(tags[0])
            if raw_family not in family_slug_map:
                raise ValueError(f"Unexpected tag '{raw_family}' for {path} {method}")
            family_slug = family_slug_map[raw_family]
            op_params = _extract_parameters(method_obj, path_item)
            request_io = _extract_request_body(method_obj)
            response_io = _extract_response(method_obj)
            operation_security = method_obj.get("security")
            auth = "public"
            if operation_security is None:
                if global_security is not None:
                    auth = "api-key-headers"
            elif operation_security != []:
                auth = "api-key-headers"
            command = _operation_to_command(family_slug, operation_id)
            is_write = operation_id in write_ops
            is_secret = operation_id in secret_ops
            requires_strong_ack = is_write
            snapshot_policy = snapshot_policy_map.get(operation_id, {})
            if not isinstance(snapshot_policy, dict):
                snapshot_policy = {}
            before_state = snapshot_policy.get("before_state_operation_id")
            if before_state is not None and not isinstance(before_state, str):
                before_state = str(before_state)
            if not str(before_state or "").strip():
                before_state = None
            readback = snapshot_policy.get("readback_operation_id")
            if readback is not None and not isinstance(readback, str):
                readback = str(readback)
            if not str(readback or "").strip():
                readback = None
            requires_no_snapshot_ack = bool(snapshot_policy.get("requires_no_snapshot_ack"))
            snapshot_note = (
                str(snapshot_policy.get("honest_note") or snapshot_policy.get("note") or "").strip()
                or "Not documented"
            )
            operations.append(
                {
                    "family_slug": family_slug,
                    "family_tag": raw_family,
                    "operation_id": operation_id,
                    "kebab_operation_id": _to_kebab(operation_id),
                    "command": command,
                    "method": method.upper(),
                    "path": path,
                    "summary": (str(method_obj.get("summary") or "").strip() or None),
                    "description": (str(method_obj.get("description") or "").strip() or None),
                    "parameters": op_params,
                    "request": request_io,
                    "response": response_io,
                    "auth": auth,
                    "write": is_write,
                    "destructive": operation_id in destructive_ops,
                    "native_dry_run": operation_id in dry_run_ops,
                    "secret_bearing_result": is_secret,
                    "billable": operation_id in billable_ops,
                    "terms_required": operation_id in terms_ops,
                    "snapshot_plan": {
                        "before_state_operation_id": before_state,
                        "readback_operation_id": readback,
                        "requires_no_snapshot_ack": requires_no_snapshot_ack,
                        "honest_note": snapshot_note,
                    },
                    "risk_profile": {
                        "reads": (not is_write),
                        "writes": is_write,
                        "high_risk": requires_strong_ack,
                        "requires_stronger_acknowledgement": requires_strong_ack,
                    },
                    "effect": "write" if is_write else "read",
                }
            )
        if has_method:
            path_count += 1

    method_counter = Counter(op["method"] for op in operations)
    families = sorted(
        {op["family_slug"] for op in operations},
        key=lambda slug: family_rank.get(slug, 10_000),
    )
    operations.sort(
        key=lambda op: (family_rank.get(op["family_slug"], 10_000), op["method"], op["path"], op["operation_id"])
    )
    totals = {
        "path_count": path_count,
        "operation_count": len(operations),
        "method_counts": dict(method_counter),
        "family_count": len(families),
        "write_count": sum(1 for op in operations if op["write"]),
        "read_count": sum(1 for op in operations if not op["write"]),
        "operation_ids": sorted(op["operation_id"] for op in operations),
        "commands_count": len(operations),
        "unique_commands": len({op["command"] for op in operations}),
    }
    summary = {
        "tool": "qwayk-porkbun-safe-agent-cli",
        "api_version": str(policy["api_version"]),
        "openapi_version": str(openapi.get("openapi") or ""),
        "spec_sha256": policy["spec_sha256"],
        "provider": "Porkbun",
        "spec_source": str(policy["spec_source"]),
        "production_servers": list(policy.get("production_servers", [])),
        "info_version": str(info_version or "").strip(),
        "totals": totals,
        "families": families,
        "method_counts": dict(method_counter),
    }
    return summary, operations


def _render_schema_cells(payload: dict[str, Any]) -> str:
    if not payload:
        return "none"
    media_types = payload.get("media_types") or []
    if not media_types:
        return "none"
    out: list[str] = []
    schemas = payload.get("schemas", {})
    for media_type in sorted(media_types):
        info = schemas.get(media_type) if isinstance(schemas, dict) else None
        summary = info.get("schema_summary") if isinstance(info, dict) else None
        if isinstance(summary, dict) and summary:
            bits = []
            if "ref" in summary:
                bits.append(summary["ref"])
            if "type" in summary:
                bits.append(f"type={summary['type']}")
            if "format" in summary:
                bits.append(f"format={summary['format']}")
            if "property_count" in summary:
                bits.append(f"props={summary['property_count']}")
            if not bits:
                bits.append("schema-present")
            out.append(f"{media_type}: {'; '.join(bits)}")
        else:
            out.append(f"{media_type}")
    return "<br>".join(out)


def _parameter_summary(parameters: Iterable[dict[str, Any]]) -> str:
    rows = sorted(
        list(parameters),
        key=lambda row: (str(row.get("in", "")), str(row.get("name", ""))),
    )
    if not rows:
        return "none"
    parts = [f"{row.get('in')}:{row.get('name')}" for row in rows]
    return "<br>".join(parts)


def _read_state_command_by_operation(operations: list[dict[str, Any]]) -> dict[str, str]:
    return {op["operation_id"]: str(op["command"]) for op in operations}


def write_outputs(
    summary: dict[str, Any],
    operations: list[dict[str, Any]],
    inventory_path: Path,
    coverage_path: Path,
) -> None:
    payload = {"summary": summary, "operations": operations}
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    tags = summary["families"]
    command_by_operation = _read_state_command_by_operation(operations)
    lines: list[str] = [
        "# API coverage (Porkbun OpenAPI v3.9)",
        "",
        "This table is the complete deterministic inventory for the pinned official v3.9 OpenAPI boundary.",
        "",
        "## Summary",
        "",
        f"- Provider: {summary['provider']}",
        f"- API version: {summary['api_version']}",
        f"- OpenAPI: {summary['openapi_version']}",
        f"- Spec SHA-256: `{summary['spec_sha256']}`",
        f"- Spec source: {summary['spec_source']}",
        f"- Paths: {summary['totals']['path_count']}",
        f"- Operations: {summary['totals']['operation_count']}",
        f"- GET / POST: {summary['method_counts'].get('GET', 0)} / {summary['method_counts'].get('POST', 0)}",
        f"- Families: {', '.join(tags)}",
        f"- Writes: {summary['totals']['write_count']} (high-risk)",
        f"- Reads: {summary['totals']['read_count']}",
        "",
        "## Canonical operation inventory",
        "",
        "| Family | Method | Path | Operation ID | CLI command | Effect | Auth | Dry-run | Secret-bearing | Destructive | Billable | Terms required | No-snapshot | Before-state | Readback | Snapshot note | Params | Request schema | Response schema |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]

    for op in operations:
        request_cell = _render_schema_cells(op["request"])
        response_cell = _render_schema_cells(op["response"])
        auth_cell = "public" if op["auth"] == "public" else "headers"
        snapshot_plan = op["snapshot_plan"]
        before_state_op = snapshot_plan.get("before_state_operation_id") if isinstance(snapshot_plan, dict) else None
        before_state_command = (
            command_by_operation.get(str(before_state_op), str(before_state_op or "").strip()) if before_state_op else "none"
        )
        if not before_state_command:
            before_state_command = "none"
        readback_op = snapshot_plan.get("readback_operation_id") if isinstance(snapshot_plan, dict) else None
        readback_command = (
            command_by_operation.get(str(readback_op), str(readback_op or "").strip()) if readback_op else "none"
        )
        if not readback_command:
            readback_command = "none"
        note = str(snapshot_plan.get("honest_note", "Not documented")).replace("|", "/")
        lines.append(
            "| "
            f"{op['family_slug']} | "
            f"{op['method']} | "
            f"{op['path']} | "
            f"{op['operation_id']} | "
            f"`{op['command']}` | "
            f"{op['effect']} | "
            f"{auth_cell} | "
            f"{'yes' if op['native_dry_run'] else 'no'} | "
            f"{'yes' if op['secret_bearing_result'] else 'no'} | "
            f"{'yes' if op['destructive'] else 'no'} | "
            f"{'yes' if op['billable'] else 'no'} | "
            f"{'yes' if op['terms_required'] else 'no'} | "
            f"{'yes' if snapshot_plan.get('requires_no_snapshot_ack', False) else 'no'} | "
            f"{before_state_command} | "
            f"{readback_command} | "
            f"{note} | "
            f"{_parameter_summary(op['parameters'])} | "
            f"{request_cell} | "
            f"{response_cell} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Write operations are fixed commands and must use approval gates in runtime implementation.")
    lines.append("- Snapshot/readback notes are intentionally inline from the inventory policy.")
    coverage_path.parent.mkdir(parents=True, exist_ok=True)
    coverage_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build deterministic Porkbun API operation inventory.")
    parser.add_argument(
        "--spec",
        default=str(Path(__file__).resolve().parents[1] / "vendor" / "porkbun-openapi-v3.9.json"),
        help="Pinned OpenAPI specification JSON.",
    )
    parser.add_argument(
        "--policy",
        default=str(Path(__file__).resolve().parent / "porkbun_inventory_policy.json"),
        help="Policy overrides for command, risk, and operation annotations.",
    )
    parser.add_argument(
        "--inventory",
        default=str(Path(__file__).resolve().parents[1] / "docs" / "operation_inventory.json"),
        help="Output static operation inventory JSON path.",
    )
    parser.add_argument(
        "--coverage",
        default=str(Path(__file__).resolve().parents[1] / "docs" / "api_coverage.md"),
        help="Output coverage document path.",
    )
    args = parser.parse_args(argv)

    spec_path = Path(args.spec).resolve()
    policy_path = Path(args.policy).resolve()
    inventory_path = Path(args.inventory).resolve()
    coverage_path = Path(args.coverage).resolve()

    if not spec_path.exists():
        raise FileNotFoundError(f"Missing spec file: {spec_path}")
    if not policy_path.exists():
        raise FileNotFoundError(f"Missing policy file: {policy_path}")

    computed_sha = _sha256_bytes(spec_path)
    policy = _load_policy(policy_path)
    if computed_sha != policy["spec_sha256"]:
        raise ValueError(f"Spec SHA mismatch: {computed_sha} != {policy['spec_sha256']}")

    summary, operations = generate_inventory(spec_path, policy_path)
    write_outputs(summary, operations, inventory_path, coverage_path)
    print(
        f"[inventory] generated path={inventory_path} operations={len(operations)} "
        f"writes={summary['totals']['write_count']} reads={summary['totals']['read_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
