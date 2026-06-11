from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import ValidationError
from .official_inventory import OperationSpec, load_pinned_inventory


def load_operations_from_pinned_snapshot() -> list[OperationSpec]:
    return load_pinned_inventory()


def operations_by_command(ops: list[OperationSpec]) -> dict[str, OperationSpec]:
    return {operation.operation_command: operation for operation in ops}


def join_base_url_and_path(base_url: str, path_with_leading_slash: str) -> str:
    base = str(base_url or "").rstrip("/")
    path = str(path_with_leading_slash or "")
    if not path.startswith("/"):
        path = "/" + path
    return base + path


def select_service_url(op: OperationSpec, cfg: Any, override: str | None = None) -> str:
    if override:
        return str(override).rstrip("/")

    route = op.route_hint
    if route == "chat":
        return str(getattr(cfg, "chat_url", "") or getattr(cfg, "entryway_url", "")).rstrip("/")
    if route == "ozone":
        return str(getattr(cfg, "ozone_url", "") or getattr(cfg, "entryway_url", "")).rstrip("/")
    if route == "labeler":
        return str(getattr(cfg, "labeler_url", "") or getattr(cfg, "ozone_url", "") or getattr(cfg, "entryway_url", "")).rstrip("/")
    if route == "relay":
        return str(getattr(cfg, "relay_url", "") or getattr(cfg, "entryway_url", "")).rstrip("/")
    if route == "public-api":
        return str(getattr(cfg, "public_api_url", "") or getattr(cfg, "entryway_url", "")).rstrip("/")
    if route == "appview":
        return str(getattr(cfg, "appview_url", "") or getattr(cfg, "entryway_url", "")).rstrip("/")
    return str(getattr(cfg, "default_pds_url", "") or getattr(cfg, "entryway_url", "")).rstrip("/")


def _load_json_arg(value: str | None) -> Any:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    path = Path(text)
    if path.exists() and path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return json.loads(text)


def _parse_kv_pairs(pairs: list[str] | None, *, label: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in pairs or []:
        text = str(raw or "").strip()
        if not text:
            continue
        if "=" not in text:
            raise ValidationError(f"Invalid {label} pair (key=value expected): {text}")
        key, value = text.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValidationError(f"Invalid {label} pair (empty key): {text}")
        out[key] = value
    return out


def _validate_input_file(path_value: str | None) -> str | None:
    if path_value is None:
        return None
    text = str(path_value).strip()
    if not text:
        return None
    path = Path(text)
    if not path.exists():
        raise ValidationError(f"Invalid --input-file path: {text}")
    if not path.is_file():
        raise ValidationError(f"Invalid --input-file path (not a file): {text}")
    return text


def build_api_call_plan(
    *,
    tool: str,
    tool_version: str,
    env_fingerprint: str,
    op: OperationSpec,
    cfg: Any,
    query_json: str | None,
    body_json: str | None,
    query_pairs: list[str] | None,
    body_pairs: list[str] | None,
    input_file: str | None,
    input_content_type: str | None,
    service_url: str | None,
) -> dict[str, Any]:
    query_from_json = _load_json_arg(query_json) or {}
    body_from_json = _load_json_arg(body_json) or {}

    if not isinstance(query_from_json, dict):
        raise ValidationError("--query-json must be a JSON object (or a path to one)")
    if not isinstance(body_from_json, dict):
        raise ValidationError("--body-json must be a JSON object (or a path to one)")

    query_dict = {str(key): value for key, value in query_from_json.items()}
    query_dict.update(_parse_kv_pairs(query_pairs, label="query"))

    body_dict = {str(key): value for key, value in body_from_json.items()}
    body_dict.update(_parse_kv_pairs(body_pairs, label="body"))

    input_file_value = _validate_input_file(input_file)
    content_type = str(input_content_type or "").strip() or None

    missing_required: list[dict[str, str]] = []
    for name in op.required_query_params:
        if name not in query_dict:
            missing_required.append({"in": "query", "name": name})
    for name in op.required_body_fields:
        if name not in body_dict:
            missing_required.append({"in": "body", "name": name})
    if op.input_encoding and op.input_encoding not in {"application/json"} and not input_file_value:
        missing_required.append({"in": "input_file", "name": "input_file"})

    target_base_url = select_service_url(op, cfg, override=service_url)
    url = join_base_url_and_path(target_base_url, op.path)

    return {
        "tool": tool,
        "version": tool_version or None,
        "dry_run": True,
        "env_fingerprint": env_fingerprint,
        "operation": {
            "lexicon_id": op.lexicon_id,
            "operation_command": op.operation_command,
            "namespace": op.namespace,
            "group": op.group,
            "kind": op.kind,
            "http_method": op.http_method,
            "path": op.path,
            "url": url,
            "service_url": target_base_url,
            "route_hint": op.route_hint,
            "doc_url": op.doc_url,
            "docs_source": op.docs_source,
            "stability": op.stability,
            "input_encoding": op.input_encoding,
        },
        "inputs": {
            "query": query_dict,
            "body": body_dict,
            "input_file": input_file_value,
            "input_content_type": content_type,
        },
        "requirements": {
            "required_query_params": list(op.required_query_params),
            "required_body_fields": list(op.required_body_fields),
            "missing_required": missing_required,
        },
    }
