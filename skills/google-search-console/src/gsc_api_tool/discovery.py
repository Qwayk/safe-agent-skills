from __future__ import annotations

import dataclasses
import json
import os
from pathlib import Path
from typing import Any


def _tool_root() -> Path:
    # `.../src/gsc_api_tool/discovery.py` -> tool root
    return Path(__file__).resolve().parents[2]


DEFAULT_DISCOVERY_SNAPSHOT = (
    _tool_root() / "docs" / "official_discovery_searchconsole_v1_2026-03-05.json"
)


@dataclasses.dataclass(frozen=True)
class ParameterSpec:
    name: str
    location: str  # path | query
    required: bool
    repeated: bool
    type: str | None
    enum: list[str] | None


@dataclasses.dataclass(frozen=True)
class MethodSpec:
    method_id: str
    http_method: str
    path: str
    description: str | None
    parameters: dict[str, ParameterSpec]
    has_request_body: bool


def load_discovery_snapshot(path: str | Path | None = None) -> dict[str, Any]:
    env_override = (os.environ.get("GSC_DISCOVERY_SNAPSHOT_PATH") or "").strip()
    if path is None and env_override:
        path = env_override
    p = Path(path) if path is not None else DEFAULT_DISCOVERY_SNAPSHOT
    if not p.exists():
        raise RuntimeError(f"Discovery snapshot not found: {p}")
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Discovery snapshot must be a JSON object")
    return data


def _collect_methods(discovery: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    def walk(node: dict[str, Any]) -> None:
        methods = node.get("methods") or {}
        if isinstance(methods, dict):
            for _name, method in methods.items():
                if isinstance(method, dict):
                    out.append(method)
        resources = node.get("resources") or {}
        if isinstance(resources, dict):
            for _name, sub in resources.items():
                if isinstance(sub, dict):
                    walk(sub)

    walk(discovery)
    return out


def list_method_ids(discovery: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for m in _collect_methods(discovery):
        mid = m.get("id")
        if isinstance(mid, str) and mid.strip():
            ids.append(mid.strip())
    return sorted(set(ids))


def load_methods(*, discovery: dict[str, Any] | None = None) -> dict[str, MethodSpec]:
    discovery = discovery or load_discovery_snapshot()
    methods: dict[str, MethodSpec] = {}
    for m in _collect_methods(discovery):
        mid = str(m.get("id") or "").strip()
        if not mid:
            continue

        http_method = str(m.get("httpMethod") or "").strip().upper()
        path = str(m.get("path") or "").strip()
        description = str(m.get("description") or "").strip() or None

        params: dict[str, ParameterSpec] = {}
        raw_params = m.get("parameters") or {}
        if isinstance(raw_params, dict):
            for pname, pdef in raw_params.items():
                if not isinstance(pname, str) or not isinstance(pdef, dict):
                    continue
                location = str(pdef.get("location") or "").strip()
                required = bool(pdef.get("required"))
                repeated = bool(pdef.get("repeated"))
                ptype = str(pdef.get("type") or "").strip() or None
                enum = pdef.get("enum")
                enum_list = [str(x) for x in enum] if isinstance(enum, list) else None
                params[pname] = ParameterSpec(
                    name=pname,
                    location=location,
                    required=required,
                    repeated=repeated,
                    type=ptype,
                    enum=enum_list,
                )

        has_request_body = isinstance(m.get("request"), dict)

        methods[mid] = MethodSpec(
            method_id=mid,
            http_method=http_method,
            path=path,
            description=description,
            parameters=params,
            has_request_body=has_request_body,
        )

    return dict(sorted(methods.items(), key=lambda kv: kv[0]))

