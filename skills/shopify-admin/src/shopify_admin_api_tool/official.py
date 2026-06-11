from __future__ import annotations

import dataclasses
import json
import re
from importlib.resources import files
from typing import Any, Iterable

from .errors import ToolError, ValidationError


def camel_to_kebab(name: str) -> str:
    s = str(name or "").strip()
    if not s:
        raise ValidationError("Empty operation name")
    # Keep existing underscores as separators too (Shopify names are typically camelCase).
    s = s.replace("_", "-")
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s)
    s = re.sub(r"-{2,}", "-", s)
    return s.lower()


@dataclasses.dataclass(frozen=True)
class OperationArg:
    name: str
    gql_type: str
    required: bool


@dataclasses.dataclass(frozen=True)
class OperationDef:
    kind: str  # "query" | "mutation"
    name: str  # GraphQL field name (camelCase)
    kebab: str  # CLI command name
    return_gql_type: str
    return_doc_kind: str  # "objects" | "scalars" | "enums" | "interfaces" | "unions" | "input_objects" | "unknown"
    args: tuple[OperationArg, ...]


@dataclasses.dataclass(frozen=True)
class OfficialManifest:
    api_version: str
    generated_at_utc: str
    operations: tuple[OperationDef, ...]

    def by_kind(self, kind: str) -> tuple[OperationDef, ...]:
        k = str(kind or "").strip()
        return tuple([op for op in self.operations if op.kind == k])

    def find(self, kind: str, *, name: str | None = None, kebab: str | None = None) -> OperationDef | None:
        kind = str(kind or "").strip()
        if kind not in {"query", "mutation"}:
            return None
        if name:
            target = str(name).strip()
            for op in self.operations:
                if op.kind == kind and op.name == target:
                    return op
        if kebab:
            target = str(kebab).strip()
            for op in self.operations:
                if op.kind == kind and op.kebab == target:
                    return op
        return None


def _read_package_text(rel_path: str) -> str:
    try:
        p = files("shopify_admin_api_tool").joinpath(rel_path)
        return p.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        raise ToolError(f"Missing packaged data: {rel_path}") from e


def load_official_manifest() -> OfficialManifest:
    raw = json.loads(_read_package_text("data/official_manifest.json"))
    if not isinstance(raw, dict):
        raise ToolError("official_manifest.json must be a JSON object")
    api_version = str(raw.get("api_version") or "").strip()
    generated_at_utc = str(raw.get("generated_at_utc") or "").strip()
    ops_raw = raw.get("operations")
    if not api_version:
        raise ToolError("official_manifest.json missing api_version")
    if not generated_at_utc:
        raise ToolError("official_manifest.json missing generated_at_utc")
    if not isinstance(ops_raw, list):
        raise ToolError("official_manifest.json missing operations list")

    ops: list[OperationDef] = []
    for item in ops_raw:
        if not isinstance(item, dict):
            continue
        kind = str(item.get("kind") or "").strip()
        name = str(item.get("name") or "").strip()
        kebab = str(item.get("kebab") or "").strip() or camel_to_kebab(name)
        return_gql_type = str(item.get("return_gql_type") or "").strip()
        return_doc_kind = str(item.get("return_doc_kind") or "").strip() or "unknown"
        args_in = item.get("args")
        if kind not in {"query", "mutation"} or not name or not return_gql_type:
            continue
        args: list[OperationArg] = []
        if isinstance(args_in, list):
            for a in args_in:
                if not isinstance(a, dict):
                    continue
                an = str(a.get("name") or "").strip()
                at = str(a.get("gql_type") or "").strip()
                req = bool(a.get("required"))
                if an and at:
                    args.append(OperationArg(name=an, gql_type=at, required=req))
        ops.append(
            OperationDef(
                kind=kind,
                name=name,
                kebab=kebab,
                return_gql_type=return_gql_type,
                return_doc_kind=return_doc_kind,
                args=tuple(args),
            )
        )

    if not ops:
        raise ToolError("official_manifest.json contains no operations")

    return OfficialManifest(api_version=api_version, generated_at_utc=generated_at_utc, operations=tuple(ops))


def iter_official_operations_txt_lines(text: str) -> Iterable[str]:
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        yield line


def load_official_operations_list() -> list[str]:
    txt = _read_package_text("data/official_operations.txt")
    return list(iter_official_operations_txt_lines(txt))


def validate_manifest_matches_operations(manifest: OfficialManifest, operations: list[str]) -> None:
    expected = set(operations)
    have = set([f"{op.kind}:{op.name}" for op in manifest.operations])
    missing = sorted(list(expected - have))
    extra = sorted(list(have - expected))
    if missing or extra:
        raise ToolError(
            "Official manifest/operations mismatch: "
            + f"missing={len(missing)} extra={len(extra)}"
        )

