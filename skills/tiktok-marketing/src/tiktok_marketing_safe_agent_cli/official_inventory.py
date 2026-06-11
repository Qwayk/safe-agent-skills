from __future__ import annotations

import dataclasses
import json
import re
from pathlib import Path
from typing import Any


@dataclasses.dataclass(frozen=True)
class OperationSpec:
    operation_command: str
    method: str
    path: str
    doc_url: str
    family: str | None = None
    required_path_params: tuple[str, ...] = ()
    body_mode: str = "none"
    content_types: tuple[str, ...] = ()
    collection_formats: tuple[tuple[str, str], ...] = ()
    file_param_names: tuple[str, ...] = ()
    form_field_names: tuple[str, ...] = ()
    header_param_sources: dict[str, str] = dataclasses.field(default_factory=dict)
    query_param_sources: dict[str, str] = dataclasses.field(default_factory=dict)
    required_header_params: tuple[str, ...] = ()
    required_query_params: tuple[str, ...] = ()
    required_request_body: bool = False
    source: str | None = None
    source_files: tuple[str, ...] = ()
    summary: str | None = None
    tags: tuple[str, ...] = ()


_PATH_PARAM_RE = re.compile(r"{([a-zA-Z0-9_\-]+)}")


def _path_param_names(path: str) -> tuple[str, ...]:
    return tuple(sorted({m.group(1) for m in _PATH_PARAM_RE.finditer(path or "")}))


def _to_str(value: Any) -> str:
    return str(value).strip()


def _normalize_mapping(value: dict[str, Any] | None) -> dict[str, str]:
    if not value:
        return {}
    return {k: _to_str(v) for k, v in value.items() if k is not None}


def _normalize_tuple(value: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(str(v) for v in value if str(v).strip())


def _to_sorted_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple, set)):
        return tuple(sorted({str(item) for item in value if str(item).strip()}))
    return tuple([str(value)])


def load_operations_from_text(path: Path) -> list[OperationSpec]:
    if not path.exists():
        raise RuntimeError(f"Missing official operations file: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Pinned operations file must be an object: {path}")
    entries = payload.get("operations")
    if not isinstance(entries, list):
        raise RuntimeError(f"Pinned operations file missing 'operations' list: {path}")

    ops: list[OperationSpec] = []
    for idx, raw in enumerate(entries, start=1):
        if not isinstance(raw, dict):
            raise RuntimeError(f"Invalid operation entry at index {idx} in {path}")
        operation_command = str(raw.get("operation_command") or "").strip()
        method = str(raw.get("method") or "").strip().upper()
        path_value = str(raw.get("path") or "").strip()
        doc_url = str(raw.get("doc_url") or "").strip()
        if not operation_command or not method or not path_value:
            raise RuntimeError(f"Invalid operation fields at index {idx} in {path}")

        body_mode = str(raw.get("body_mode") or "none").strip().lower() or "none"
        content_types = raw.get("content_types") or []
        collection_formats = raw.get("collection_formats") or {}
        header_sources = raw.get("header_param_sources") or {}
        query_sources = raw.get("query_param_sources") or {}
        tags = raw.get("tags") or ()
        if isinstance(tags, str):
            tags = tuple(t.strip() for t in tags.split(",") if t.strip())
        raw_required_path_params = raw.get("required_path_params") or []
        if not isinstance(raw_required_path_params, (list, tuple, set)):
            raise RuntimeError(f"Invalid required_path_params for {operation_command} at index {idx}")
        required_path_params = _to_sorted_tuple(raw_required_path_params)
        if not required_path_params:
            required_path_params = _path_param_names(path_value)

        if not isinstance(header_sources, dict):
            raise RuntimeError(f"Invalid header_param_sources for {operation_command} at index {idx}")
        if not isinstance(query_sources, dict):
            raise RuntimeError(f"Invalid query_param_sources for {operation_command} at index {idx}")

        if not isinstance(content_types, (list, tuple)):
            content_types = []
        if not isinstance(collection_formats, dict):
            collection_formats = {}

        ops.append(
            OperationSpec(
                operation_command=operation_command,
                method=method,
                path=path_value,
                doc_url=doc_url,
                family=(str(raw.get("family") or "") or None),
                body_mode=body_mode,
                required_path_params=required_path_params,
                content_types=_to_sorted_tuple(content_types),
                collection_formats=tuple(sorted((str(k), str(v)) for k, v in collection_formats.items() if str(k).strip())),
                file_param_names=_normalize_tuple(raw.get("file_param_names")),
                form_field_names=_normalize_tuple(raw.get("form_field_names")),
                header_param_sources=_normalize_mapping(header_sources),
                query_param_sources=_normalize_mapping(query_sources),
                required_header_params=_to_sorted_tuple(raw.get("required_header_params")),
                required_query_params=_to_sorted_tuple(raw.get("required_query_params")),
                required_request_body=bool(raw.get("required_request_body")),
                source=(str(raw.get("source") or "") or None),
                source_files=_normalize_tuple(raw.get("source_files")),
                summary=(str(raw.get("summary") or "") or None),
                tags=_to_sorted_tuple(tags),
            )
        )

    return sorted(ops, key=lambda op: (op.operation_command, op.method, op.path))


def load_official_operations_file(path: Path) -> list[OperationSpec]:
    return load_operations_from_text(path)
