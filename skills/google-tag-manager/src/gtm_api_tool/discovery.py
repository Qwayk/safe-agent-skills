from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any, Iterable


@dataclasses.dataclass(frozen=True)
class ParameterSpec:
    name: str
    location: str  # "path" | "query" (discovery uses these)
    required: bool
    type: str | None


@dataclasses.dataclass(frozen=True)
class MethodSpec:
    method_id: str
    http_method: str
    path: str
    description: str | None
    parameters: tuple[ParameterSpec, ...]
    request_ref: str | None
    response_ref: str | None


def vendored_discovery_path() -> Path:
    return Path(__file__).resolve().parent / "_vendor" / "tagmanager_v2_discovery.json"


def load_discovery_doc() -> dict[str, Any]:
    p = vendored_discovery_path()
    obj = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError("Vendored discovery doc must be a JSON object")
    if str(obj.get("name") or "") != "tagmanager":
        raise RuntimeError("Vendored discovery doc mismatch: expected name=tagmanager")
    if str(obj.get("version") or "") != "v2":
        raise RuntimeError("Vendored discovery doc mismatch: expected version=v2")
    return obj


def discovery_oauth_scopes(doc: dict[str, Any] | None = None) -> list[str]:
    d = doc or load_discovery_doc()
    scopes = (((d.get("auth") or {}).get("oauth2") or {}).get("scopes") or {})
    if not isinstance(scopes, dict):
        return []
    out: list[str] = []
    for k in scopes.keys():
        if isinstance(k, str) and k.strip():
            out.append(k.strip())
    return sorted(set(out))


def iter_methods(doc: dict[str, Any] | None = None) -> list[MethodSpec]:
    d = doc or load_discovery_doc()
    resources = d.get("resources") or {}
    if not isinstance(resources, dict):
        raise RuntimeError("Discovery doc missing resources dict")

    out: list[MethodSpec] = []

    def walk(res: dict[str, Any]) -> None:
        methods = res.get("methods") or {}
        if isinstance(methods, dict):
            for _name, m in methods.items():
                if not isinstance(m, dict):
                    continue
                method_id = str(m.get("id") or "").strip()
                http_method = str(m.get("httpMethod") or "").strip().upper()
                path = str(m.get("path") or "").strip()
                if not method_id or not http_method or not path:
                    continue

                params_obj = m.get("parameters") or {}
                params: list[ParameterSpec] = []
                if isinstance(params_obj, dict):
                    for pname, pobj in params_obj.items():
                        if not isinstance(pname, str) or not pname.strip():
                            continue
                        if not isinstance(pobj, dict):
                            continue
                        params.append(
                            ParameterSpec(
                                name=pname.strip(),
                                location=str(pobj.get("location") or "query").strip(),
                                required=bool(pobj.get("required")),
                                type=str(pobj.get("type")).strip() if pobj.get("type") is not None else None,
                            )
                        )

                req_ref = None
                if isinstance(m.get("request"), dict):
                    req_ref = str((m.get("request") or {}).get("$ref") or "").strip() or None
                resp_ref = None
                if isinstance(m.get("response"), dict):
                    resp_ref = str((m.get("response") or {}).get("$ref") or "").strip() or None

                out.append(
                    MethodSpec(
                        method_id=method_id,
                        http_method=http_method,
                        path=path,
                        description=str(m.get("description")).strip() if m.get("description") else None,
                        parameters=tuple(sorted(params, key=lambda p: (p.location, p.required is False, p.name))),
                        request_ref=req_ref,
                        response_ref=resp_ref,
                    )
                )

        children = res.get("resources") or {}
        if isinstance(children, dict):
            for _child_name, child in children.items():
                if isinstance(child, dict):
                    walk(child)

    for _rname, r in resources.items():
        if isinstance(r, dict):
            walk(r)

    # Stable order for inventories/tests.
    out.sort(key=lambda m: m.method_id)
    return out


def method_by_id(method_id: str, doc: dict[str, Any] | None = None) -> MethodSpec | None:
    mid = str(method_id or "").strip()
    if not mid:
        return None
    for m in iter_methods(doc):
        if m.method_id == mid:
            return m
    return None


def all_method_ids(doc: dict[str, Any] | None = None) -> list[str]:
    return [m.method_id for m in iter_methods(doc)]


def required_path_params(method: MethodSpec) -> list[str]:
    out: list[str] = []
    for p in method.parameters:
        if p.location == "path" and p.required:
            out.append(p.name)
    return out


def optional_query_params(method: MethodSpec) -> list[str]:
    out: list[str] = []
    for p in method.parameters:
        if p.location == "query":
            out.append(p.name)
    return sorted(set(out))


def iter_methods_by_http(doc: dict[str, Any] | None = None) -> dict[str, list[MethodSpec]]:
    buckets: dict[str, list[MethodSpec]] = {}
    for m in iter_methods(doc):
        buckets.setdefault(m.http_method, []).append(m)
    for k in list(buckets.keys()):
        buckets[k].sort(key=lambda m: m.method_id)
    return buckets


def iter_method_specs(doc: dict[str, Any] | None = None) -> Iterable[MethodSpec]:
    return iter_methods(doc)

