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
    tags: tuple[str, ...] = ()
    required_path_params: tuple[str, ...] = ()
    required_request_body: bool = False
    beta_header: str | None = None


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
        if not operation_command or not method or not path or not doc_url:
            raise RuntimeError(f"Invalid official operations line (empty fields): {line}")

        tags: tuple[str, ...] = ()
        required_path_params: tuple[str, ...] = ()
        required_request_body = False
        beta_header: str | None = None

        for extra in parts[4:]:
            extra = (extra or "").strip()
            if not extra:
                continue
            m = _BRACKET_FIELD_RE.match(extra)
            if not m:
                continue
            key = str(m.group("key") or "").strip()
            value = str(m.group("value") or "")
            if key == "tags":
                items = [t.strip() for t in value.split(",") if t.strip()]
                tags = tuple(sorted(set(items)))
            elif key == "required_path":
                items = [t.strip() for t in value.split(",") if t.strip()]
                required_path_params = tuple(sorted(set(items)))
            elif key == "required_body":
                required_request_body = str(value).strip() in {"1", "true", "True", "yes", "YES"}
            elif key == "beta":
                v = str(value).strip()
                beta_header = v if v else None

        ops.append(
            OperationSpec(
                operation_command=operation_command,
                method=method,
                path=path,
                doc_url=doc_url,
                tags=tags,
                required_path_params=required_path_params,
                required_request_body=required_request_body,
                beta_header=beta_header,
            )
        )

    # Deterministic order
    return sorted(ops, key=lambda o: (o.operation_command, o.method, o.path))


def load_official_operations_file(path: Path) -> list[OperationSpec]:
    return parse_official_operations_text(path.read_text(encoding="utf-8"))
