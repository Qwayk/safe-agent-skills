from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STABLE_DISCOVERY_FAMILIES: tuple[str, ...] = (
    "accounts_v1",
    "conversions_v1",
    "datasources_v1",
    "inventories_v1",
    "issueresolution_v1",
    "lfp_v1",
    "notifications_v1",
    "ordertracking_v1",
    "products_v1",
    "promotions_v1",
    "quota_v1",
    "reports_v1",
)

ACTIVE_ALPHA_DISCOVERY_FAMILIES: tuple[str, ...] = (
    "accounts_v1alpha",
    "productstudio_v1alpha",
    "reports_v1alpha",
    "reviews_v1alpha",
    "youtube_v1alpha",
)

RETIRED_BETA_DISCOVERY_FAMILIES: tuple[str, ...] = (
    "accounts_v1beta",
    "conversions_v1beta",
    "datasources_v1beta",
    "inventories_v1beta",
    "issueresolution_v1beta",
    "lfp_v1beta",
    "notifications_v1beta",
    "ordertracking_v1beta",
    "products_v1beta",
    "promotions_v1beta",
    "quota_v1beta",
    "reports_v1beta",
    "reviews_v1beta",
)

REFERENCE_ONLY_MANUAL_FAMILIES: tuple[str, ...] = (
    "loyaltycustomers_v1alpha",
    "youtubeshoppingcheckout_v1alpha",
    "youtubeshoppingcheckout_v1beta",
)

SHIPPED_DISCOVERY_FAMILIES: tuple[str, ...] = STABLE_DISCOVERY_FAMILIES + ACTIVE_ALPHA_DISCOVERY_FAMILIES
OFFICIAL_DISCOVERY_FAMILIES: tuple[str, ...] = SHIPPED_DISCOVERY_FAMILIES + RETIRED_BETA_DISCOVERY_FAMILIES
SHIPPED_MANUAL_FAMILIES: tuple[str, ...] = (
    "loyaltycustomers_v1alpha",
    "youtubeshoppingcheckout_v1alpha",
)
OFFICIAL_FAMILIES: tuple[str, ...] = OFFICIAL_DISCOVERY_FAMILIES + REFERENCE_ONLY_MANUAL_FAMILIES
SHIPPED_FAMILIES: tuple[str, ...] = SHIPPED_DISCOVERY_FAMILIES + SHIPPED_MANUAL_FAMILIES

_DISCOVERY_PREFIX = "merchantapi."
_DEFAULT_SCOPE = "https://www.googleapis.com/auth/content"


def _vendor_dir() -> Path:
    # .../src/google_merchant_api_tool/discovery.py -> src/google_merchant_api_tool/_vendor
    return Path(__file__).resolve().parent / "_vendor"


@dataclass(frozen=True)
class ParameterSpec:
    name: str
    location: str | None
    required: bool
    type: str | None
    repeated: bool
    description: str | None


@dataclass(frozen=True)
class MethodSpec:
    family: str
    method_id: str
    command_id: str
    http_method: str
    path: str
    description: str | None
    scopes: tuple[str, ...]
    has_request_body: bool
    parameters: tuple[ParameterSpec, ...]


@dataclass(frozen=True)
class _DiscoveryFamily:
    family: str
    expected_name: str
    expected_version: str
    vendor_filename: str


def family_parts(family: str) -> tuple[str, str]:
    raw = str(family or "").strip()
    for suffix in ("_v1alpha", "_v1beta", "_v1"):
        if raw.endswith(suffix):
            return raw[: -len(suffix)], suffix[1:]
    raise RuntimeError(f"Unrecognized Merchant family/version name: {family!r}")


def family_sub_api(family: str) -> str:
    sub_api, _ = family_parts(family)
    return sub_api


def family_version(family: str) -> str:
    _, version = family_parts(family)
    return version


def _family_specs(families: tuple[str, ...]) -> tuple[_DiscoveryFamily, ...]:
    return tuple(
        _DiscoveryFamily(
            family=family,
            expected_name="merchantapi",
            expected_version=family,
            vendor_filename=f"{family}_discovery.json",
        )
        for family in families
    )


def _read_file(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    doc = json.loads(raw)
    if not isinstance(doc, dict):
        raise RuntimeError(f"Discovery snapshot is not a JSON object: {path}")
    return doc


def _vendor_search_paths() -> tuple[Path, ...]:
    root = _vendor_dir()
    return (root / "discovery", root)


def _read_discovery_doc(family: _DiscoveryFamily) -> dict[str, Any]:
    filename = family.vendor_filename
    paths = [_candidate / filename for _candidate in _vendor_search_paths()]
    chosen: Path | None = None
    for candidate in paths:
        if candidate.exists():
            chosen = candidate
            break
    if chosen is None:
        candidates = ", ".join(str(p) for p in paths)
        raise RuntimeError(f"Missing discovery snapshot for {family.family}. Tried: {candidates}")

    doc = _read_file(chosen)
    name = str(doc.get("name") or "").strip()
    version = str(doc.get("version") or "").strip()
    doc_id = str(doc.get("id") or "").strip()
    if name != family.expected_name:
        raise RuntimeError(
            f"Unexpected discovery name for {family.family}: {name!r} (expected {family.expected_name!r})"
        )
    if version != family.expected_version:
        raise RuntimeError(
            f"Unexpected discovery version for {family.family}: {version!r} (expected {family.expected_version!r})"
        )
    expected_id = f"{family.expected_name}:{family.expected_version}"
    if doc_id and doc_id != expected_id:
        raise RuntimeError(f"Unexpected discovery id for {family.family}: {doc_id!r} (expected {expected_id!r})")
    if not isinstance(doc.get("resources"), dict):
        raise RuntimeError(f"Discovery snapshot for {family.family} has no resources dict")
    return doc


def _normalize_method_id(raw: str) -> str:
    m = str(raw or "").strip()
    if not m:
        return ""
    if m.startswith(_DISCOVERY_PREFIX):
        m = m[len(_DISCOVERY_PREFIX) :]
    return m


def _walk_methods(
    *,
    family: str,
    node: dict[str, Any],
    methods: list[MethodSpec],
    method_prefix: str,
    default_scopes: tuple[str, ...],
) -> None:
    raw_methods = node.get("methods")
    if isinstance(raw_methods, dict):
        for method_name in sorted(raw_methods.keys()):
            raw_method = raw_methods.get(method_name)
            if not isinstance(raw_method, dict):
                continue

            raw_method_id = str(raw_method.get("id") or "").strip()
            if not raw_method_id:
                raw_method_id = f"{method_prefix}.{method_name}" if method_prefix else method_name
            command_id = _normalize_method_id(raw_method_id)
            if not command_id:
                continue

            http_method = str(raw_method.get("httpMethod") or "").strip().upper()
            path = str(raw_method.get("path") or "").strip()
            if not http_method or not path:
                continue

            parameters: list[ParameterSpec] = []
            raw_params = raw_method.get("parameters")
            if isinstance(raw_params, dict):
                for param_name in sorted(raw_params.keys()):
                    param_obj = raw_params.get(param_name)
                    if not isinstance(param_name, str) or not isinstance(param_obj, dict):
                        continue
                    parameters.append(
                        ParameterSpec(
                            name=param_name.strip(),
                            location=str(param_obj.get("location") or "query").strip() or "query",
                            required=bool(param_obj.get("required")),
                            type=str(param_obj.get("type") or "").strip() or None,
                            repeated=bool(param_obj.get("repeated")),
                            description=str(param_obj.get("description") or "").strip() or None,
                        )
                    )

            raw_scopes = raw_method.get("scopes")
            if isinstance(raw_scopes, list):
                scopes = tuple(sorted(str(x).strip() for x in raw_scopes if str(x).strip()))
            else:
                scopes = default_scopes

            methods.append(
                MethodSpec(
                    family=family,
                    method_id=command_id,
                    command_id=command_id,
                    http_method=http_method,
                    path=path,
                    description=str(raw_method.get("description") or "").strip() or None,
                    scopes=scopes,
                    has_request_body=bool(raw_method.get("request")),
                    parameters=tuple(sorted(parameters, key=lambda p: (p.location, p.name))),
                )
            )

    raw_resources = node.get("resources")
    if not isinstance(raw_resources, dict):
        return
    for resource_name in sorted(raw_resources.keys()):
        resource_obj = raw_resources.get(resource_name)
        if not isinstance(resource_obj, dict):
            continue
        child_prefix = f"{method_prefix}.{resource_name}" if method_prefix else resource_name
        _walk_methods(
            family=family,
            node=resource_obj,
            methods=methods,
            method_prefix=child_prefix,
            default_scopes=default_scopes,
        )


def _default_oauth_scopes() -> tuple[str, ...]:
    return (_DEFAULT_SCOPE,)


def _manual_method(
    *,
    family: str,
    command_id: str,
    http_method: str,
    path: str,
    description: str,
    path_params: tuple[str, ...],
    has_request_body: bool = True,
) -> MethodSpec:
    parameters = tuple(
        ParameterSpec(
            name=name,
            location="path",
            required=True,
            type="string",
            repeated=False,
            description=f"Path parameter: {name}",
        )
        for name in path_params
    )
    return MethodSpec(
        family=family,
        method_id=command_id,
        command_id=command_id,
        http_method=http_method,
        path=path,
        description=description,
        scopes=_default_oauth_scopes(),
        has_request_body=has_request_body,
        parameters=parameters,
    )


MANUAL_OFFICIAL_METHODS: tuple[MethodSpec, ...] = (
    _manual_method(
        family="loyaltycustomers_v1alpha",
        command_id="accounts.loyaltyCustomers.manage",
        http_method="POST",
        path="loyaltyCustomers/v1alpha/{parent=accounts/*}/loyaltyCustomers:manage",
        description="Create or update loyalty customer data for a merchant account.",
        path_params=("parent",),
    ),
    _manual_method(
        family="youtubeshoppingcheckout_v1alpha",
        command_id="accounts.orders.applyOrderUpdate",
        http_method="POST",
        path="youtubeshoppingcheckout/v1alpha/{parent=accounts/*/orders/*}:applyOrderUpdate",
        description="Process an order update for a store builder merchant order.",
        path_params=("parent",),
    ),
    _manual_method(
        family="youtubeshoppingcheckout_v1beta",
        command_id="accounts.orders.applyOrderUpdate",
        http_method="POST",
        path="youtubeshoppingcheckout/v1beta/{parent=accounts/*/orders/*}:applyOrderUpdate",
        description="Process an order update for a store builder merchant order.",
        path_params=("parent",),
    ),
)


def _dedupe_methods(methods: list[MethodSpec]) -> tuple[MethodSpec, ...]:
    deduped: dict[tuple[str, str], MethodSpec] = {}
    for method in methods:
        key = (method.family, method.command_id)
        existing = deduped.get(key)
        if existing is None:
            deduped[key] = method
            continue
        if existing != method:
            raise RuntimeError(
                f"Conflicting duplicate method id from discovery docs: {method.family}:{method.command_id}"
            )
    return tuple(sorted(deduped.values(), key=lambda m: (m.family, m.command_id)))


def load_discovery_methods(families: tuple[str, ...]) -> tuple[MethodSpec, ...]:
    methods: list[MethodSpec] = []
    for family_spec in _family_specs(families):
        doc = _read_discovery_doc(family_spec)
        resources = doc.get("resources")
        if not isinstance(resources, dict):
            raise RuntimeError(f"Discovery doc for {family_spec.family} has invalid resources")
        _walk_methods(
            family=family_spec.family,
            node=doc,
            methods=methods,
            method_prefix="",
            default_scopes=_default_oauth_scopes(),
        )
    out = _dedupe_methods(methods)
    if not out:
        raise RuntimeError("No Merchant discovery methods loaded")
    return out


def load_stable_discovery_methods() -> tuple[MethodSpec, ...]:
    return load_discovery_methods(STABLE_DISCOVERY_FAMILIES)


def load_shipped_discovery_methods() -> tuple[MethodSpec, ...]:
    return load_discovery_methods(SHIPPED_DISCOVERY_FAMILIES)


def load_official_discovery_methods() -> tuple[MethodSpec, ...]:
    return load_discovery_methods(OFFICIAL_DISCOVERY_FAMILIES)


def load_shipped_manual_methods() -> tuple[MethodSpec, ...]:
    return tuple(method for method in MANUAL_OFFICIAL_METHODS if method.family in SHIPPED_MANUAL_FAMILIES)


def load_official_manual_methods() -> tuple[MethodSpec, ...]:
    return MANUAL_OFFICIAL_METHODS


def load_shipped_methods() -> tuple[MethodSpec, ...]:
    return _dedupe_methods(list(load_shipped_discovery_methods()) + list(load_shipped_manual_methods()))


def load_official_methods() -> tuple[MethodSpec, ...]:
    return _dedupe_methods(list(load_official_discovery_methods()) + list(load_official_manual_methods()))


def get_method_by_command_id(command_id: str, methods: tuple[MethodSpec, ...] | None = None) -> MethodSpec | None:
    target = str(command_id or "").strip()
    if not target:
        return None
    method_rows = methods if methods is not None else load_shipped_methods()
    matches = [m for m in method_rows if m.command_id == target]
    if not matches:
        return None
    stable_matches = [m for m in matches if family_version(m.family) == "v1"]
    if len(stable_matches) == 1:
        return stable_matches[0]
    if len(matches) == 1:
        return matches[0]
    raise RuntimeError(f"Ambiguous command id across Merchant versions: {target}")


def method_command_list() -> list[str]:
    return [m.command_id for m in load_shipped_methods()]


def is_read_like_post(method: MethodSpec) -> bool:
    if str(method.http_method).upper() != "POST":
        return False
    last = method.command_id.rsplit(".", 1)[-1].lower()
    read_like_markers = ("search", "render", "retrieve", "find", "verifyself")
    for marker in read_like_markers:
        if last == marker:
            return True
        if last.startswith(marker):
            return True
        if last.endswith(marker):
            return True
    return False
