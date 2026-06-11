from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .errors import ValidationError
from .official_inventory import OperationSpec, load_official_operations_file


def tool_root_path() -> Path:
    return Path(__file__).resolve().parents[2]


def pinned_official_operations_path() -> Path:
    docs = tool_root_path() / "docs"
    candidates = sorted(docs.glob("official_operations_v1_*.txt"))
    if not candidates:
        raise RuntimeError(f"Missing pinned official operations list under {docs}")
    return candidates[-1]


def load_operations_from_pinned_snapshot() -> list[OperationSpec]:
    path = pinned_official_operations_path()
    if not path.exists():
        raise RuntimeError(f"Missing pinned operations list: {path}")
    return load_official_operations_file(path)


def operations_by_command(ops: list[OperationSpec]) -> dict[str, OperationSpec]:
    out: dict[str, OperationSpec] = {}
    for operation in ops:
        out[operation.operation_command] = operation
    return out


_OPTIONAL_SEGMENT_RE = re.compile(r"\[([^\[\]]+)\]")
_PATH_PARAM_RE = re.compile(r"{([a-zA-Z0-9_\-]+)}|:([a-zA-Z0-9_\-]+)")
_PATH_PARAM_NAME_RE = re.compile(r"[a-zA-Z0-9_\-]+")


def _extract_required_path_params(path_template: str) -> list[str]:
    required: list[str] = []
    inside_optional = 0
    i = 0
    while i < len(path_template):
        char = path_template[i]
        if char == "[":
            inside_optional += 1
            i += 1
            continue
        if char == "]":
            inside_optional = max(0, inside_optional - 1)
            i += 1
            continue
        if inside_optional != 0:
            i += 1
            continue

        if char == "{":
            end = path_template.find("}", i + 1)
            if end != -1:
                name = path_template[i + 1 : end].strip()
                if name and name not in required and _PATH_PARAM_NAME_RE.fullmatch(name):
                    required.append(name)
                i = end + 1
                continue
        elif char == ":":
            match = _PATH_PARAM_NAME_RE.match(path_template, i + 1)
            if match:
                name = match.group(0)
                if name and name not in required:
                    required.append(name)
                i = match.end()
                continue
        i += 1

    return required


def _fill_segment(segment: str, values: dict[str, str], *, require_all: bool) -> tuple[str, list[str]]:
    missing: list[str] = []

    def repl(match: re.Match[str]) -> str:
        name = match.group(1) or match.group(2) or ""
        value = str(values.get(name) or "").strip()
        if value:
            return value
        missing.append(name)
        return "{" + name + "}"

    filled = _PATH_PARAM_RE.sub(repl, segment)
    if require_all and missing:
        return "", missing
    return filled, missing


def substitute_path_params(path_template: str, values: dict[str, str]) -> tuple[str, list[str]]:
    def optional_repl(match: re.Match[str]) -> str:
        segment = match.group(1)
        filled, missing = _fill_segment(segment, values, require_all=True)
        return "" if missing else filled

    path = _OPTIONAL_SEGMENT_RE.sub(optional_repl, path_template)
    filled, missing = _fill_segment(path, values, require_all=False)
    normalized = re.sub(r"/{2,}", "/", filled)
    if not normalized.startswith("/"):
        normalized = "/" + normalized
    return normalized, sorted(set(missing))


def join_base_url_and_path(base_url: str, path_with_leading_slash: str) -> str:
    base = str(base_url or "").rstrip("/")
    path = str(path_with_leading_slash or "")
    if not path.startswith("/"):
        path = "/" + path
    return base + path


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


def _parse_kv_pairs(pairs: list[str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
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
    body_format: str,
) -> dict[str, Any]:
    path_dict_from_json = _load_json_arg(path_json) or {}
    query_dict_from_json = _load_json_arg(query_json) or {}
    body_from_json = _load_json_arg(body_json) or {}

    if not isinstance(path_dict_from_json, dict):
        raise ValidationError("--path-json must be a JSON object (or a path to one)")
    if not isinstance(query_dict_from_json, dict):
        raise ValidationError("--query-json must be a JSON object (or a path to one)")
    if not isinstance(body_from_json, dict):
        raise ValidationError("--body-json must be a JSON object (or a path to one)")

    path_dict = {str(key): str(value) for key, value in path_dict_from_json.items()}
    path_dict.update(_parse_kv_pairs(path_pairs))

    query_dict = {str(key): value for key, value in query_dict_from_json.items()}
    query_dict.update(_parse_kv_pairs(query_pairs))

    body_dict = {str(key): value for key, value in body_from_json.items()}
    body_dict.update(_parse_kv_pairs(body_pairs))

    files: dict[str, str] = {}
    for raw in file_pairs or []:
        text = str(raw or "").strip()
        if not text:
            continue
        if "=" not in text:
            raise ValidationError(f"Invalid file pair (field=path): {text}")
        field, path = text.split("=", 1)
        field = field.strip()
        path = path.strip()
        if not field or not path:
            raise ValidationError(f"Invalid file pair (field=path): {text}")
        file_path = Path(path)
        if not file_path.exists():
            raise ValidationError(f"Invalid file path for field '{field}': {path}")
        if not file_path.is_file():
            raise ValidationError(f"Invalid file path for field '{field}' (not a file): {path}")
        files[field] = path

    filled_path, missing_path = substitute_path_params(op.path, path_dict)
    url = join_base_url_and_path(base_url, filled_path)

    missing_required: list[dict[str, str]] = []
    required_path_params = op.required_path_params or tuple(_extract_required_path_params(op.path))
    for name in required_path_params:
        if name not in path_dict:
            missing_required.append({"in": "path", "name": name})

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
            "section": op.section,
            "oauth_scope": op.oauth_scope,
            "missing_path_params": missing_path,
        },
        "inputs": {
            "path": path_dict,
            "query": query_dict,
            "body": body_dict,
            "files": files,
            "body_format": body_format,
        },
        "requirements": {
            "missing_required": missing_required,
        },
    }
