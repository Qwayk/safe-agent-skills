from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .errors import ValidationError
from .official_inventory import OperationSpec, load_official_operations_file


def tool_root_path() -> Path:
    # .../src/openai_api_tool/api_dispatch.py -> tool root is 3 levels up
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
    for o in ops:
        out[o.operation_command] = o
    return out


_PATH_PARAM_RE = re.compile(r"{([a-zA-Z0-9_\\-]+)}")


def substitute_path_params(path_template: str, values: dict[str, str]) -> tuple[str, list[str]]:
    missing: list[str] = []

    def repl(m: re.Match[str]) -> str:
        name = m.group(1)
        if name in values:
            return str(values[name])
        missing.append(name)
        return "{" + name + "}"

    filled = _PATH_PARAM_RE.sub(repl, path_template)
    missing_sorted = sorted(set(missing))
    return filled, missing_sorted


def join_base_url_and_path(base_url: str, path_with_leading_slash: str) -> str:
    base = str(base_url or "").rstrip("/")
    path = str(path_with_leading_slash or "")
    if not path.startswith("/"):
        path = "/" + path
    return base + path


def _load_json_arg(value: str | None) -> Any:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    p = Path(s)
    if p.exists() and p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    return json.loads(s)


def _parse_kv_pairs(pairs: list[str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in pairs or []:
        s = str(raw or "").strip()
        if not s:
            continue
        if "=" not in s:
            raise ValidationError(f"Invalid key=value pair: {s}")
        k, v = s.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            raise ValidationError(f"Invalid key=value pair (empty key): {s}")
        out[k] = v
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
    file_pairs: list[str] | None,
) -> dict[str, Any]:
    path_dict_from_json = _load_json_arg(path_json) or {}
    query_dict_from_json = _load_json_arg(query_json) or {}
    body_obj = _load_json_arg(body_json)

    if not isinstance(path_dict_from_json, dict):
        raise ValidationError("--path-json must be a JSON object (or a path to one)")
    if not isinstance(query_dict_from_json, dict):
        raise ValidationError("--query-json must be a JSON object (or a path to one)")
    if body_obj is not None and not isinstance(body_obj, dict):
        raise ValidationError("--body-json must be a JSON object (or a path to one)")

    path_dict = {str(k): str(v) for k, v in path_dict_from_json.items()}
    path_dict.update(_parse_kv_pairs(path_pairs))
    query_dict = {str(k): v for k, v in query_dict_from_json.items()}
    query_dict.update(_parse_kv_pairs(query_pairs))

    files: dict[str, str] = {}
    for raw in file_pairs or []:
        s = str(raw or "").strip()
        if not s:
            continue
        if "=" not in s:
            raise ValidationError(f"Invalid file pair (field=path): {s}")
        field, path = s.split("=", 1)
        field = field.strip()
        path = path.strip()
        if not field or not path:
            raise ValidationError(f"Invalid file pair (field=path): {s}")
        files[field] = path

    filled_path, missing_path = substitute_path_params(op.path, path_dict)
    url = join_base_url_and_path(base_url, filled_path)

    required_missing: list[dict[str, Any]] = []
    for name in op.required_path_params:
        if name not in path_dict:
            required_missing.append({"in": "path", "name": name})
    if op.required_request_body and body_obj is None:
        required_missing.append({"in": "body", "name": "requestBody"})

    required_missing_sorted = sorted(required_missing, key=lambda x: (x.get("in", ""), x.get("name", "")))

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
            "missing_path_params": missing_path,
        },
        "inputs": {
            "path": path_dict,
            "query": query_dict,
            "body": body_obj,
            "files": files,
        },
        "requirements": {
            "missing_required": required_missing_sorted,
        },
        "metadata": {
            "tags": list(op.tags),
            "beta_header": op.beta_header,
        },
    }
