from __future__ import annotations

import dataclasses
import re
from typing import Any, Iterable

from .errors import ValidationError
from .openapi_snapshot import OpenApiSnapshot, load_pinned_openapi_snapshot


_ALLOWED_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


@dataclasses.dataclass(frozen=True)
class OperationSpec:
    operation_id: str
    method: str
    path_template: str
    command_name: str
    path_params: tuple[str, ...]


def _operation_id_for(*, method: str, path: str, op_obj: dict[str, Any]) -> str:
    op_id = str(op_obj.get("operationId") or "").strip()
    if op_id:
        return op_id
    return f"{method.upper()} {path}"


_CAMEL_SPLIT_RE = re.compile(
    r"""
    (?<=[a-z0-9])(?=[A-Z])|
    (?<=[A-Z])(?=[A-Z][a-z])|
    (?<=[A-Za-z])(?=[0-9])|
    (?<=[0-9])(?=[A-Za-z])
    """,
    re.VERBOSE,
)


def operation_id_to_command_name(operation_id: str) -> str:
    """
    Deterministic mapping from OpenAPI operationId -> CLI command name (kebab-case).

    - Prefer operationId when present.
    - Fallback IDs like "GET /api/v2/foo/{id}" are normalized too.
    """
    op = operation_id.strip()
    if not op:
        raise ValidationError("Operation id is empty")
    if " " in op:
        op = op.replace("/", " ").replace("{", " ").replace("}", " ")
        op = re.sub(r"\s+", " ", op).strip()
    parts = [p for p in _CAMEL_SPLIT_RE.split(op) if p and p.strip()]
    raw = "-".join(parts).lower()
    raw = re.sub(r"[^a-z0-9\\-]+", "-", raw)
    raw = re.sub(r"-{2,}", "-", raw).strip("-")
    if not raw:
        raise ValidationError(f"Could not derive command name from operation id: {operation_id!r}")
    return raw


def _path_params_for(path_template: str) -> tuple[str, ...]:
    return tuple([m.group(1) for m in re.finditer(r"{([^}]+)}", path_template)])


def iter_operation_specs(snapshot: OpenApiSnapshot) -> Iterable[OperationSpec]:
    paths = snapshot.obj.get("paths") or {}
    if not isinstance(paths, dict):
        return []
    for path, methods in paths.items():
        if not isinstance(path, str) or not path.strip():
            continue
        if not isinstance(methods, dict):
            continue
        for method, op_obj in methods.items():
            m = str(method).lower().strip()
            if m not in _ALLOWED_METHODS:
                continue
            if not isinstance(op_obj, dict):
                continue
            op_id = _operation_id_for(method=m, path=path, op_obj=op_obj)
            yield OperationSpec(
                operation_id=op_id,
                method=m,
                path_template=path,
                command_name=operation_id_to_command_name(op_id),
                path_params=_path_params_for(path),
            )


def load_operation_specs(snapshot: OpenApiSnapshot | None = None) -> list[OperationSpec]:
    snap = snapshot or load_pinned_openapi_snapshot()
    specs = list(iter_operation_specs(snap))

    # Detect operation id collisions (safe default: refuse to claim 100% coverage).
    op_counts: dict[str, int] = {}
    cmd_counts: dict[str, int] = {}
    for s in specs:
        op_counts[s.operation_id] = op_counts.get(s.operation_id, 0) + 1
        cmd_counts[s.command_name] = cmd_counts.get(s.command_name, 0) + 1
    op_dupes = sorted([op_id for op_id, c in op_counts.items() if c > 1])
    if op_dupes:
        examples = ", ".join(op_dupes[:10])
        more = "" if len(op_dupes) <= 10 else f" (+{len(op_dupes) - 10} more)"
        raise ValidationError(
            "OpenAPI operationId collision(s) detected. "
            "Refusing because canonical inventories would be ambiguous. "
            f"Duplicates: {examples}{more}"
        )
    cmd_dupes = sorted([cmd for cmd, c in cmd_counts.items() if c > 1])
    if cmd_dupes:
        examples = ", ".join(cmd_dupes[:10])
        more = "" if len(cmd_dupes) <= 10 else f" (+{len(cmd_dupes) - 10} more)"
        raise ValidationError(
            "OpenAPI command-name collision(s) detected. "
            "Refusing because explicit CLI commands would be ambiguous. "
            f"Duplicates: {examples}{more}"
        )

    # Stable ordering: operation id, then method+path (tie-breaker).
    return sorted(specs, key=lambda s: (s.operation_id, s.method, s.path_template))


def operation_command_line(spec: OperationSpec) -> str:
    return f"api {spec.command_name}"
