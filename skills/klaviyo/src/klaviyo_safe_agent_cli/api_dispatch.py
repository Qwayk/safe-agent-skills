from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .errors import ValidationError
from .official_inventory import OperationSpec, load_operations_from_pinned_snapshot


_PATH_PARAM_RE = re.compile(r"{([a-zA-Z0-9_\\-]+)}")


def operations_by_command(operations: list[OperationSpec]) -> dict[str, OperationSpec]:
    return {op.operation_command: op for op in operations}


def substitute_path_params(path_template: str, values: dict[str, str]) -> tuple[str, list[str]]:
    missing: list[str] = []

    def repl(match: re.Match[str]) -> str:
        name = match.group(1)
        if not name:
            return ""
        if name in values:
            return str(values[name])
        missing.append(name)
        return "{" + name + "}"

    filled = _PATH_PARAM_RE.sub(repl, path_template)
    return filled, sorted(set(missing))


def join_base_url_and_path(base_url: str, path_with_leading_slash: str) -> str:
    base = str(base_url or "").rstrip("/")
    path = str(path_with_leading_slash or "")
    if not path.startswith("/"):
        path = "/" + path
    return base + path


def _load_json_arg(value: str | None) -> Any:
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    p = Path(raw)
    if p.exists() and p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    return json.loads(raw)


def _parse_kv_pairs(values: list[str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in values or []:
        text = str(raw or "").strip()
        if not text:
            continue
        if "=" not in text:
            raise ValidationError(f"Invalid key=value item: {text}")
        key, value = text.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValidationError(f"Invalid key=value item (empty key): {text}")
        out[key] = value
    return out


def _normalize_query_value(value: Any) -> Any:
    if isinstance(value, list):
        return ",".join(str(item) for item in value)
    if isinstance(value, tuple):
        return ",".join(str(item) for item in value)
    return str(value)


def build_api_call_plan(
    *,
    tool: str,
    tool_version: str,
    env_fingerprint: str,
    op: OperationSpec,
    base_url: str,
    path_json: str | None,
    query_json: str | None,
    body_json: str | None,
    path_pairs: list[str] | None,
    query_pairs: list[str] | None,
    file_pairs: list[str] | None,
) -> dict[str, Any]:
    path_from_json = _load_json_arg(path_json) or {}
    query_from_json = _load_json_arg(query_json) or {}
    body_obj = _load_json_arg(body_json)

    if not isinstance(path_from_json, dict):
        raise ValidationError("--path-json must be a JSON object or path to JSON object")
    if not isinstance(query_from_json, dict):
        raise ValidationError("--query-json must be a JSON object or path to JSON object")
    if body_obj is not None and not isinstance(body_obj, dict):
        raise ValidationError("--body-json must be a JSON object or path to JSON object")

    path_values = {str(k): str(v) for k, v in path_from_json.items()}
    path_values.update(_parse_kv_pairs(path_pairs))

    query_values = {str(k): _normalize_query_value(v) for k, v in query_from_json.items()}
    query_values.update(_parse_kv_pairs(query_pairs))

    files: dict[str, str] = {}
    for raw in file_pairs or []:
        text = str(raw or "").strip()
        if not text:
            continue
        if "=" not in text:
            raise ValidationError(f"Invalid file pair (field=path): {text}")
        field, value = text.split("=", 1)
        field = field.strip()
        value = value.strip()
        if not field or not value:
            raise ValidationError(f"Invalid file pair (field=path): {text}")
        files[field] = value

    filled_path, missing_path_params = substitute_path_params(op.path, path_values)
    url = join_base_url_and_path(base_url, filled_path)

    missing_inputs: list[dict[str, Any]] = []
    for name in op.required_path_params:
        if name not in path_values:
            missing_inputs.append({"in": "path", "name": name})

    if op.requires_company_id and "company_id" not in query_values:
        missing_inputs.append({"in": "query", "name": "company_id"})

    if op.required_request_body and body_obj is None:
        missing_inputs.append({"in": "body", "name": "requestBody"})

    return {
        "tool": tool,
        "version": tool_version or None,
        "dry_run": True,
        "env_fingerprint": env_fingerprint,
        "operation": {
            "operation_command": op.operation_command,
            "method": op.method,
            "path_template": op.path,
            "path_filled": filled_path,
            "url": url,
            "doc_url": op.doc_url,
            "requires_company_id": op.requires_company_id,
            "tags": list(op.tags),
            "subtag": op.subtag,
            "content_types": list(op.content_types),
            "has_multipart_request": bool(op.has_multipart_request),
        },
        "inputs": {
            "path": path_values,
            "query": query_values,
            "body": body_obj if body_obj is not None else {},
            "files": files,
        },
        "requirements": {
            "missing_required": sorted(missing_inputs, key=lambda item: (item.get("in"), item.get("name"))),
        },
        "operation_aliases": list(op.operation_aliases),
        "has_multipart_request": bool(op.has_multipart_request),
    }
