from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from typing import Any, Iterable


@dataclass(frozen=True)
class ParameterSpec:
    name: str
    location: str | None
    required: bool
    type: str | None
    repeated: bool
    enum: tuple[str, ...]


@dataclass(frozen=True)
class MethodSpec:
    api_name: str
    api_version: str
    method_id: str
    http_method: str
    path: str
    resource_chain: tuple[str, ...]
    method_name: str
    parameters: tuple[ParameterSpec, ...]
    has_request_body: bool


@dataclass(frozen=True)
class DiscoveryDocSpec:
    expected_name: str
    expected_version: str
    vendor_filename: str


def load_vendored_discovery_doc(spec: DiscoveryDocSpec) -> dict[str, Any]:
    vendored_path = files("ga4_api_tool").joinpath("_vendor").joinpath(spec.vendor_filename)
    raw = vendored_path.read_text(encoding="utf-8")
    doc = json.loads(raw)

    name = str(doc.get("name") or "")
    version = str(doc.get("version") or "")
    if name != spec.expected_name:
        raise ValueError(f"Unexpected discovery doc name: {name!r} (expected {spec.expected_name!r})")
    if version != spec.expected_version:
        raise ValueError(f"Unexpected discovery doc version: {version!r} (expected {spec.expected_version!r})")
    return doc


def extract_oauth_scopes(doc: dict[str, Any]) -> list[str]:
    scopes_obj: dict[str, Any] = (
        doc.get("auth", {}).get("oauth2", {}).get("scopes", {})  # type: ignore[assignment]
        or {}
    )
    scopes = [str(k) for k in scopes_obj.keys()]
    scopes.sort()
    return scopes


def _iter_methods(
    *,
    api_name: str,
    api_version: str,
    resources: dict[str, Any] | None,
    chain: tuple[str, ...],
) -> Iterable[MethodSpec]:
    if not resources:
        return

    for resource_name in sorted(resources.keys()):
        resource = resources.get(resource_name) or {}

        methods: dict[str, Any] = resource.get("methods") or {}
        for method_name in sorted(methods.keys()):
            m = methods.get(method_name) or {}

            method_id = str(m.get("id") or "")
            http_method = str(m.get("httpMethod") or "")
            path = str(m.get("path") or "")
            if not method_id or not http_method or not path:
                # Skip malformed entries rather than failing CLI init.
                continue

            params: dict[str, Any] = m.get("parameters") or {}
            param_specs: list[ParameterSpec] = []
            for param_name in sorted(params.keys()):
                p = params.get(param_name) or {}
                enum_vals = tuple(str(x) for x in (p.get("enum") or []))
                param_specs.append(
                    ParameterSpec(
                        name=str(param_name),
                        location=(str(p.get("location")) if p.get("location") is not None else None),
                        required=bool(p.get("required")),
                        type=(str(p.get("type")) if p.get("type") is not None else None),
                        repeated=bool(p.get("repeated")),
                        enum=enum_vals,
                    )
                )

            has_request_body = bool(m.get("request"))

            yield MethodSpec(
                api_name=api_name,
                api_version=api_version,
                method_id=method_id,
                http_method=http_method.upper(),
                path=path,
                resource_chain=chain + (resource_name,),
                method_name=method_name,
                parameters=tuple(param_specs),
                has_request_body=has_request_body,
            )

        nested: dict[str, Any] | None = resource.get("resources") or None
        yield from _iter_methods(
            api_name=api_name,
            api_version=api_version,
            resources=nested,
            chain=chain + (resource_name,),
        )


def extract_method_specs(doc: dict[str, Any]) -> list[MethodSpec]:
    api_name = str(doc.get("name") or "")
    api_version = str(doc.get("version") or "")
    methods = list(
        _iter_methods(
            api_name=api_name,
            api_version=api_version,
            resources=doc.get("resources") or None,
            chain=(),
        )
    )
    methods.sort(key=lambda m: m.method_id)
    return methods

