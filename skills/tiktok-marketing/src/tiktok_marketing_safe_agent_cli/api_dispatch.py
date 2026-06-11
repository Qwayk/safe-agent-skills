from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .errors import ValidationError
from .official_inventory import OperationSpec, load_official_operations_file


def tool_root_path() -> Path:
    # .../src/tiktok_marketing_safe_agent_cli/api_dispatch.py -> tool root is 3 levels up
    return Path(__file__).resolve().parents[2]


def pinned_official_operations_path() -> Path:
    docs_dir = tool_root_path() / "docs"
    candidates = sorted(docs_dir.glob("official_operations_v1_*.json"))
    if not candidates:
        raise RuntimeError(f"Missing pinned official operations list under {docs_dir}")
    return candidates[-1]


def load_operations_from_pinned_snapshot() -> list[OperationSpec]:
    path = pinned_official_operations_path()
    if not path.exists():
        raise RuntimeError(f"Missing pinned official operations list: {path}")
    return load_official_operations_file(path)


def operations_by_command(ops: list[OperationSpec]) -> dict[str, OperationSpec]:
    out: dict[str, OperationSpec] = {}
    for operation in ops:
        out[operation.operation_command] = operation
    return out


def join_base_url_and_path(base_url: str, path_with_leading_slash: str) -> str:
    base = str(base_url or "").rstrip("/")
    path = str(path_with_leading_slash or "")
    if not path.startswith("/"):
        path = "/" + path
    return base + path


_PATH_PARAM_RE = re.compile(r"{([a-zA-Z0-9_\-]+)}")


def _substitute_path_params(path_template: str, values: dict[str, str]) -> tuple[str, list[str]]:
    missing: list[str] = []

    def repl(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in values:
            return str(values[name])
        missing.append(name)
        return "{" + name + "}"

    filled = _PATH_PARAM_RE.sub(repl, path_template)
    return filled, sorted(set(missing))


def _coerce_dict(value: Any, *, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValidationError(f"--{label} must be a JSON object (or a file path to one)")
    return {str(key): item for key, item in value.items()}


def _coerce_body(value: Any) -> Any | None:
    if value is None:
        return None
    if isinstance(value, (list, dict, str, int, float, bool)):
        return value
    raise ValidationError("--body-json must be JSON, or a path to JSON")


def _coerce_text(value: str | None) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def _load_json_arg(value: str | None) -> Any | None:
    text = _coerce_text(value)
    if text is None:
        return None
    p = Path(text)
    if p.exists() and p.is_file():
        text = p.read_text(encoding="utf-8")
    return json.loads(text)


def _parse_kv_pairs(pairs: list[str] | None, *, allow_multi: bool = False) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for raw in pairs or []:
        text = str(raw or "").strip()
        if not text:
            continue
        if "=" not in text:
            raise ValidationError(f"Invalid key=value pair: {text}")
        key, value = text.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValidationError(f"Invalid key=value pair (empty key): {text}")
        if allow_multi and key in out:
            existing = out[key]
            if isinstance(existing, list):
                existing.append(value)
            else:
                out[key] = [existing, value]
            continue
        out[key] = value
    return out


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
    body_pairs: list[str] | None,
    file_pairs: list[str] | None,
    query_defaults: dict[str, str] | None,
    header_defaults: dict[str, str] | None,
) -> dict[str, Any]:
    path_obj = _load_json_arg(path_json)
    query_obj = _load_json_arg(query_json)
    body_obj = _load_json_arg(body_json)

    path_dict = _coerce_dict(path_obj, label="path-json")
    query_dict = _coerce_dict(query_obj, label="query-json")
    body_inputs = _coerce_body(body_obj)

    path_dict.update(_parse_kv_pairs(path_pairs))
    query_dict.update(_parse_kv_pairs(query_pairs, allow_multi=True))
    body_pairs_dict = _parse_kv_pairs(body_pairs)

    query_defaults = query_defaults or {}
    header_defaults = header_defaults or {}

    for query_name, source in op.query_param_sources.items():
        if query_name in query_dict:
            continue
        if source and source in query_defaults:
            default_value = str(query_defaults[source]).strip()
            if default_value:
                query_dict[query_name] = default_value

    headers: dict[str, str] = {}
    for header_name, source in op.header_param_sources.items():
        if source and source in header_defaults:
            value = str(header_defaults[source]).strip()
            if value:
                headers[header_name] = value

    path_filled, missing_path = _substitute_path_params(op.path, path_dict)

    if body_pairs_dict and isinstance(body_inputs, dict):
        body_inputs = dict(body_inputs)
        body_inputs.update(body_pairs_dict)
    elif body_pairs_dict and body_inputs is None:
        body_inputs = body_pairs_dict
    elif body_pairs_dict and not isinstance(body_inputs, dict):
        raise ValidationError("--body-json must be a JSON object when using --body key=value pairs")

    files: dict[str, str] = {}
    for raw in file_pairs or []:
        text = str(raw or "").strip()
        if not text:
            continue
        if "=" not in text:
            raise ValidationError(f"Invalid file pair (field=path): {text}")
        field, file_path = text.split("=", 1)
        field = field.strip()
        file_path = file_path.strip()
        if not field or not file_path:
            raise ValidationError(f"Invalid file pair (field=path): {text}")
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise ValidationError(f"Invalid file path for field '{field}': {file_path_obj}")
        if not file_path_obj.is_file():
            raise ValidationError(f"Invalid file path for field '{field}' (not a file): {file_path_obj}")
        files[field] = str(file_path_obj)

    if files and op.body_mode != "multipart":
        raise ValidationError(f"{op.operation_command} does not support multipart file upload")
    if files:
        allowed = set(op.file_param_names)
        for field in files:
            if field not in allowed:
                raise ValidationError(
                    f"Field '{field}' is not a supported file parameter for {op.operation_command}"
                )
    if op.body_mode == "multipart" and body_inputs is not None and not isinstance(body_inputs, dict):
        raise ValidationError("--body-json must be a JSON object for multipart operations")

    missing_required: list[dict[str, Any]] = []
    for name in op.required_path_params:
        if name not in path_dict:
            missing_required.append({"in": "path", "name": name})
    header_names_lower = {str(name).lower() for name in op.required_header_params}
    header_names_lower.update(str(name).lower() for name in op.header_param_sources)
    for name in op.required_query_params:
        if str(name).lower() in header_names_lower:
            continue
        if name not in query_dict:
            missing_required.append({"in": "query", "name": name})
    for name in op.required_header_params:
        if name not in headers:
            missing_required.append({"in": "header", "name": name})
    if op.required_request_body and body_inputs is None:
        missing_required.append({"in": "body", "name": "requestBody"})

    return {
        "tool": tool,
        "version": tool_version or None,
        "generated_at_utc": None,
        "env_fingerprint": env_fingerprint,
        "operation": {
            "operation_command": op.operation_command,
            "method": op.method,
            "path_template": op.path,
            "path_filled": path_filled,
            "url": join_base_url_and_path(base_url, path_filled),
            "doc_url": op.doc_url,
            "family": op.family,
            "body_mode": op.body_mode,
            "source_files": list(op.source_files),
            "tags": sorted(op.tags),
            "source": op.source,
            "summary": op.summary,
        },
        "headers": {
            "provided": {str(k): str(v) for k, v in sorted(headers.items(), key=lambda item: item[0])},
            "missing": [],
        },
        "inputs": {
            "path": {str(k): str(v) for k, v in sorted(path_dict.items())},
            "query": {str(k): v for k, v in sorted(query_dict.items())},
            "body": body_inputs,
            "files": dict(sorted(files.items())),
            "body_mode": op.body_mode,
        },
        "requirements": {
            "missing_required": sorted(missing_required, key=lambda item: (item.get("in"), item.get("name")))
        },
        "dry_run": True,
    }
