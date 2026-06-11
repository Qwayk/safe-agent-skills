from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import ToolError, ValidationError


@dataclass(frozen=True)
class OperationSpec:
    area: str
    api_group: str
    operation_id: str
    op_key: str
    method: str
    path_template: str
    summary: str
    source_doc: str
    auth_scope: str
    input_style: str
    sensitivity: str
    read_like: bool
    body_required: bool
    deprecated: bool
    beta: bool
    gated: str | None
    fixed_form_fields: dict[str, str]
    fixed_query: dict[str, str]
    path_defaults: dict[str, str]
    notes: str | None

    @property
    def command(self) -> str:
        return f"cloudinary-safe-agent-cli operations {self.area} {self.op_key}"

    @property
    def is_write(self) -> bool:
        return self.method != "GET" and not self.read_like

    @property
    def requires_out(self) -> bool:
        return self.sensitivity in {"sensitive_read", "sensitive_write_result", "binary"}


_CACHE: dict[str, Any] = {}


def _tool_root() -> Path:
    return Path(__file__).resolve().parents[2]


def inventory_path() -> Path:
    return _tool_root() / "docs" / "_generated" / "cloudinary_rest_inventory.json"


def load_inventory_json() -> dict[str, Any]:
    cached = _CACHE.get("inventory_json")
    if isinstance(cached, dict):
        return dict(cached)
    path = inventory_path()
    if not path.exists():
        raise ToolError(
            "Cloudinary inventory JSON is missing. Run `python3 scripts/generate_cloudinary_rest_inventory.py`."
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise ToolError(f"Invalid Cloudinary inventory JSON: {path}: {type(exc).__name__}: {exc}") from exc
    ops = data.get("operations")
    if not isinstance(ops, list):
        raise ToolError(f"Cloudinary inventory JSON is missing an operations list: {path}")
    _CACHE["inventory_json"] = dict(data)
    return dict(data)


def _spec_from_dict(obj: dict[str, Any]) -> OperationSpec:
    return OperationSpec(
        area=str(obj.get("area") or "").strip(),
        api_group=str(obj.get("api_group") or "").strip(),
        operation_id=str(obj.get("operation_id") or "").strip(),
        op_key=str(obj.get("op_key") or "").strip(),
        method=str(obj.get("method") or "").strip().upper(),
        path_template=str(obj.get("path_template") or "").strip(),
        summary=str(obj.get("summary") or "").strip(),
        source_doc=str(obj.get("source_doc") or "").strip(),
        auth_scope=str(obj.get("auth_scope") or "").strip(),
        input_style=str(obj.get("input_style") or "").strip(),
        sensitivity=str(obj.get("sensitivity") or "none").strip(),
        read_like=bool(obj.get("read_like", False)),
        body_required=bool(obj.get("body_required", False)),
        deprecated=bool(obj.get("deprecated", False)),
        beta=bool(obj.get("beta", False)),
        gated=str(obj.get("gated")).strip() if obj.get("gated") is not None else None,
        fixed_form_fields={str(k): str(v) for k, v in dict(obj.get("fixed_form_fields") or {}).items()},
        fixed_query={str(k): str(v) for k, v in dict(obj.get("fixed_query") or {}).items()},
        path_defaults={str(k): str(v) for k, v in dict(obj.get("path_defaults") or {}).items()},
        notes=str(obj.get("notes")).strip() if obj.get("notes") else None,
    )


def load_operation_specs() -> list[OperationSpec]:
    cached = _CACHE.get("operation_specs")
    if isinstance(cached, list):
        return list(cached)
    data = load_inventory_json()
    specs = [_spec_from_dict(item) for item in data.get("operations") or [] if isinstance(item, dict)]
    specs.sort(key=lambda item: (item.area, item.op_key, item.method, item.path_template))
    _CACHE["operation_specs"] = list(specs)
    _CACHE["spec_by_area_op"] = {(spec.area, spec.op_key): spec for spec in specs}
    _CACHE["spec_by_method_path"] = {(spec.method, spec.path_template): spec for spec in specs}
    return list(specs)


def load_specs_by_area() -> dict[str, list[OperationSpec]]:
    grouped: dict[str, list[OperationSpec]] = {}
    for spec in load_operation_specs():
        grouped.setdefault(spec.area, []).append(spec)
    return grouped


def find_operation(*, area: str, op_key: str) -> OperationSpec | None:
    if not area or not op_key:
        return None
    load_operation_specs()
    by = _CACHE.get("spec_by_area_op")
    if isinstance(by, dict):
        return by.get((str(area).strip(), str(op_key).strip()))  # type: ignore[return-value]
    return None


def find_by_method_path(*, method: str, path_template: str) -> OperationSpec | None:
    if not method or not path_template:
        return None
    load_operation_specs()
    by = _CACHE.get("spec_by_method_path")
    key = (str(method).strip().upper(), str(path_template).strip())
    if isinstance(by, dict):
        return by.get(key)  # type: ignore[return-value]
    return None


def require_operation(*, area: str, op_key: str) -> OperationSpec:
    spec = find_operation(area=area, op_key=op_key)
    if spec is None:
        raise ValidationError(f"Operation not found in local allowlist: area={area!r} op={op_key!r}")
    return spec
