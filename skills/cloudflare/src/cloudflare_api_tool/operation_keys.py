from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Iterable

from .openapi_index import OperationSpec, load_allowlisted_operation_index


@dataclass(frozen=True)
class OperationCommand:
    area: str
    op_key: str
    method: str
    path_template: str
    operation_id: str | None
    summary: str
    tags: str
    deprecated: bool
    api_token_groups: str
    sensitivity: str  # "none" | "sensitive_read" | "sensitive_write_result"

    @property
    def command(self) -> str:
        return f"cloudflare-api-tool operations {self.area} {self.op_key}"


_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_MULTI_DASH_RE = re.compile(r"-{2,}")


def _slug(s: str) -> str:
    t = str(s or "").strip().lower()
    t = t.replace("_", "-").replace(".", "-").replace(":", "-")
    t = _NON_ALNUM_RE.sub("-", t)
    t = _MULTI_DASH_RE.sub("-", t).strip("-")
    return t


def _base_key_for_spec(spec: OperationSpec) -> str:
    if spec.operation_id:
        k = _slug(spec.operation_id)
        if k:
            return k

    # Fallback: method+path key. Keep placeholders readable.
    method = _slug(spec.method)
    parts: list[str] = []
    for seg in str(spec.path_template or "").strip().lstrip("/").split("/"):
        seg = str(seg or "").strip()
        if not seg:
            continue
        if seg.startswith("{") and seg.endswith("}"):
            seg = seg[1:-1]
        parts.append(_slug(seg))
    k = "-".join([method] + [p for p in parts if p])
    k = _MULTI_DASH_RE.sub("-", k).strip("-")
    return k or "op"


def _hash8(spec: OperationSpec) -> str:
    src = f"{spec.method} {spec.path_template} {spec.operation_id or ''}".encode("utf-8")
    return hashlib.sha256(src).hexdigest()[:8]


def derive_operation_commands(specs: Iterable[OperationSpec]) -> list[OperationCommand]:
    """
    Deterministically assigns an explicit, stable `op_key` per allowlisted operation.

    Uniqueness is enforced within a given `area`. If a slugified key collides (for example due
    to punctuation normalization), all colliding keys get a stable `-<hash8>` suffix derived
    from (method, path_template, operation_id).
    """
    spec_list = list(specs)

    base_by_spec: dict[OperationSpec, str] = {s: _base_key_for_spec(s) for s in spec_list}
    counts: dict[tuple[str, str], int] = {}
    for s in spec_list:
        counts[(s.area, base_by_spec[s])] = counts.get((s.area, base_by_spec[s]), 0) + 1

    out: list[OperationCommand] = []
    for s in spec_list:
        base = base_by_spec[s]
        if counts.get((s.area, base), 0) > 1:
            op_key = f"{base}-{_hash8(s)}"
        else:
            op_key = base
        out.append(
            OperationCommand(
                area=s.area,
                op_key=op_key,
                method=s.method,
                path_template=s.path_template,
                operation_id=s.operation_id,
                summary=s.summary,
                tags=s.tags,
                deprecated=s.deprecated,
                api_token_groups=s.api_token_groups,
                sensitivity=s.sensitivity,
            )
        )

    out.sort(key=lambda c: (c.area, c.op_key, c.method, c.path_template))
    return out


_CACHE: dict[str, object] = {}


def load_allowlisted_operation_commands() -> list[OperationCommand]:
    cached = _CACHE.get("allowlisted_operation_commands")
    if isinstance(cached, list):
        return list(cached)
    idx = load_allowlisted_operation_index()
    cmds = derive_operation_commands(idx.all_specs())
    _CACHE["allowlisted_operation_commands"] = list(cmds)
    _CACHE["by_method_path"] = {(c.method, c.path_template): c for c in cmds}
    _CACHE["by_operation_id"] = {c.operation_id: c for c in cmds if c.operation_id}
    return cmds


def allowlisted_operation_command_by_method_path(*, method: str, path_template: str) -> OperationCommand | None:
    """
    Lookup helper for coverage ledgers.

    Note: allowlisted operations are globally unique by (method, path_template) after the tool's
    deterministic de-duplication logic in `load_allowlisted_operation_index()`.
    """
    m = str(method or "").upper().strip()
    p = str(path_template or "").strip()
    if not m or not p:
        return None
    load_allowlisted_operation_commands()
    by = _CACHE.get("by_method_path")
    if isinstance(by, dict):
        return by.get((m, p))  # type: ignore[return-value]
    # Fallback: should not happen.
    for c in load_allowlisted_operation_commands():
        if c.method == m and c.path_template == p:
            return c
    return None


def allowlisted_operation_command_by_operation_id(operation_id: str) -> OperationCommand | None:
    op = str(operation_id or "").strip()
    if not op:
        return None
    load_allowlisted_operation_commands()
    by = _CACHE.get("by_operation_id")
    if isinstance(by, dict):
        return by.get(op)  # type: ignore[return-value]
    for c in load_allowlisted_operation_commands():
        if c.operation_id == op:
            return c
    return None
