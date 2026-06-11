from __future__ import annotations

import dataclasses
import json
from pathlib import Path


@dataclasses.dataclass(frozen=True)
class OperationSpec:
    operation_command: str
    method: str
    path: str
    doc_url: str
    tags: tuple[str, ...] = ()
    subtag: str = ""
    required_path_params: tuple[str, ...] = ()
    required_request_body: bool = False
    requires_company_id: bool = False
    content_types: tuple[str, ...] = ()
    has_multipart_request: bool = False
    operation_aliases: tuple[str, ...] = ()


def _as_tuple_str_values(obj: object) -> tuple[str, ...]:
    if not isinstance(obj, list):
        return ()
    out: list[str] = []
    for item in obj:
        value = str(item or "").strip()
        if value:
            out.append(value)
    return tuple(sorted(set(out)))


def tool_root_path() -> Path:
    return Path(__file__).resolve().parents[2]


def pinned_operations_path() -> Path:
    docs = tool_root_path() / "docs"
    candidates = sorted(docs.glob("official_operations_v1_*.json"))
    if not candidates:
        raise RuntimeError(f"Missing pinned official operations JSON under {docs}")
    return candidates[-1]


def load_official_operations_file(path: Path) -> list[OperationSpec]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"Invalid official operations file {path}: {type(e).__name__}: {e}") from None

    ops = payload.get("operations")
    if not isinstance(ops, list):
        raise RuntimeError(f"Malformed official operations file {path}: missing operations list")

    parsed: list[OperationSpec] = []
    for idx, item in enumerate(ops, start=1):
        if not isinstance(item, dict):
            raise RuntimeError(f"Invalid operation #{idx} in {path}: expected object")

        operation_command = str(item.get("operation_command") or "").strip()
        method = str(item.get("method") or "").strip().upper()
        path = str(item.get("path") or "").strip()
        doc_url = str(item.get("doc_url") or "").strip()
        if not operation_command or not method or not path or not doc_url:
            raise RuntimeError(f"Invalid operation #{idx} in {path}: missing command/method/path/doc_url")

        parsed.append(
            OperationSpec(
                operation_command=operation_command,
                method=method,
                path=path,
                doc_url=doc_url,
                tags=_as_tuple_str_values(item.get("tags")),
                subtag=str(item.get("subtag") or ""),
                required_path_params=_as_tuple_str_values(item.get("required_path_params")),
                required_request_body=bool(item.get("required_request_body") or False),
                requires_company_id=bool(item.get("requires_company_id") or False),
                content_types=_as_tuple_str_values(item.get("content_types")),
                has_multipart_request=bool(item.get("has_multipart_request") or False),
                operation_aliases=_as_tuple_str_values(item.get("operation_aliases")),
            )
        )

    return sorted(parsed, key=lambda op: (op.operation_command, op.method, op.path))


def load_operations_from_pinned_snapshot() -> list[OperationSpec]:
    path = pinned_operations_path()
    if not path.exists():
        raise RuntimeError(f"Missing pinned operations file: {path}")
    return load_official_operations_file(path)
