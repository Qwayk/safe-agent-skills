from __future__ import annotations

import dataclasses
import re
from pathlib import Path


@dataclasses.dataclass(frozen=True)
class OperationSpec:
    operation_command: str
    method: str
    path: str
    doc_url: str
    section: str
    oauth_scope: str
    required_path_params: tuple[str, ...] = ()


_BRACKET_FIELD_RE = re.compile(r"^\[(?P<key>[a-zA-Z0-9_\-]+)=(?P<value>.*)\]$")


def parse_official_operations_text(text: str) -> list[OperationSpec]:
    ops: list[OperationSpec] = []
    for raw in (text or "").splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            raise RuntimeError(f"Invalid official operations line (expected 4+ TSV fields): {line}")

        operation_command = parts[0].strip()
        method = parts[1].strip().upper()
        path = parts[2].strip()
        doc_url = parts[3].strip()
        section = ""
        oauth_scope = ""
        required_path_params: tuple[str, ...] = ()

        if not operation_command or not method or not path or not doc_url:
            raise RuntimeError(f"Invalid official operations line (empty fields): {line}")

        for extra in parts[4:]:
            extra = (extra or "").strip()
            if not extra:
                continue
            match = _BRACKET_FIELD_RE.match(extra)
            if not match:
                continue
            key = str(match.group("key") or "").strip()
            value = str(match.group("value") or "").strip()
            if key == "section":
                section = value
            elif key == "scope":
                oauth_scope = value
            elif key == "required_path":
                items = [item.strip() for item in value.split(",") if item.strip()]
                required_path_params = tuple(items)

        ops.append(
            OperationSpec(
                operation_command=operation_command,
                method=method,
                path=path,
                doc_url=doc_url,
                section=section,
                oauth_scope=oauth_scope,
                required_path_params=required_path_params,
            )
        )
    return ops


def load_official_operations_file(path: Path) -> list[OperationSpec]:
    return parse_official_operations_text(path.read_text(encoding="utf-8"))
