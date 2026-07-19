from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any


def load_manual_contracts() -> dict[tuple[str, str], dict[str, Any]]:
    """Load and validate the reviewed supplements for the 81 incomplete upstream schemas."""

    from .manual_contracts_a import CONTRACTS as CONTRACTS_A
    from .manual_contracts_b import CONTRACTS as CONTRACTS_B

    overlap = set(CONTRACTS_A) & set(CONTRACTS_B)
    if overlap:
        raise ValueError(f"Duplicate manual Twilio contracts: {sorted(overlap)}")
    contracts = {**CONTRACTS_A, **CONTRACTS_B}
    if len(contracts) != 81:
        raise ValueError(f"Expected 81 audited manual Twilio contracts, found {len(contracts)}")

    allowed_dispositions = {
        "canonical_duplicate",
        "command",
        "developer_preview",
        "legacy_eol",
        "private_or_unavailable",
    }
    for key, contract in contracts.items():
        if contract.get("disposition") not in allowed_dispositions:
            raise ValueError(f"Invalid manual disposition for {key}: {contract.get('disposition')}")
        sources = contract.get("sources")
        if not isinstance(sources, tuple) or not sources:
            raise ValueError(f"Manual contract has no official sources: {key}")
        if not all(
            isinstance(source, str)
            and (
                source.startswith("https://www.twilio.com/")
                or source.startswith("https://github.com/twilio/")
            )
            for source in sources
        ):
            raise ValueError(f"Manual contract has a non-Twilio source: {key}")
        if not str(contract.get("reason") or "").strip():
            raise ValueError(f"Manual contract has no reason: {key}")
    return contracts


def apply_request_contract(
    request: dict[str, Any] | None,
    contract: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Apply reviewed path-level schema patches without changing the pinned source schema."""

    if request is None:
        if contract.get("schema_patches") or contract.get("drop_paths"):
            raise ValueError("Manual request patches target an operation without a request body")
        return None

    patched = copy.deepcopy(request)
    for media_type, patches in (contract.get("schema_patches") or {}).items():
        schema_entry = patched.get("schemas", {}).get(media_type)
        if not isinstance(schema_entry, dict):
            raise ValueError(f"Manual contract targets missing media type: {media_type}")
        resolved = schema_entry.get("resolved_schema")
        if not isinstance(resolved, dict):
            raise ValueError(f"Manual contract targets missing resolved schema: {media_type}")
        for path, replacement in patches:
            schema_entry["resolved_schema"] = _replace_path(
                schema_entry["resolved_schema"],
                tuple(path),
                replacement,
            )

    for media_type, paths in (contract.get("drop_paths") or {}).items():
        schema_entry = patched.get("schemas", {}).get(media_type)
        if not isinstance(schema_entry, dict):
            raise ValueError(f"Manual contract drops a field from missing media type: {media_type}")
        for path in paths:
            _drop_path(schema_entry["resolved_schema"], tuple(path))
    return patched


def apply_parameter_contract(
    parameters: list[dict[str, Any]],
    contract: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Apply reviewed requiredness and schema changes to named operation parameters."""

    patched = copy.deepcopy(parameters)
    for target, replacement in (contract.get("parameter_patches") or {}).items():
        location, name = target
        matches = [
            parameter
            for parameter in patched
            if parameter.get("in") == location and parameter.get("name") == name
        ]
        if len(matches) != 1:
            raise ValueError(f"Manual parameter patch target is not unique: {location}.{name}")
        matches[0].update(copy.deepcopy(replacement))
        if "schema" in replacement:
            matches[0]["resolved_schema"] = copy.deepcopy(replacement["schema"])
    return patched


def public_manual_metadata(contract: Mapping[str, Any]) -> dict[str, Any]:
    """Return the compact evidence record stored with a generated operation."""

    return {
        "reason": str(contract["reason"]),
        "restrictions": list(contract.get("restrictions") or ()),
        "sources": list(contract["sources"]),
    }


def _path_text(path: tuple[Any, ...]) -> str:
    return ".".join(str(part) for part in path)


def _child(container: Any, part: Any, path: tuple[Any, ...]) -> Any:
    if isinstance(container, dict) and part in container:
        return container[part]
    if isinstance(container, list) and isinstance(part, int) and 0 <= part < len(container):
        return container[part]
    raise ValueError(f"Manual schema path does not exist: {_path_text(path)}")


def _replace_path(schema: dict[str, Any], path: tuple[Any, ...], replacement: Any) -> dict[str, Any]:
    if not path:
        if not isinstance(replacement, dict):
            raise ValueError("A root request-schema replacement must be an object")
        return copy.deepcopy(replacement)
    cursor: Any = schema
    for part in path[:-1]:
        cursor = _child(cursor, part, path)
    final = path[-1]
    if isinstance(cursor, dict):
        cursor[final] = copy.deepcopy(replacement)
    elif isinstance(cursor, list) and isinstance(final, int) and 0 <= final < len(cursor):
        cursor[final] = copy.deepcopy(replacement)
    else:
        raise ValueError(f"Manual schema patch target does not exist: {_path_text(path)}")
    return schema


def _drop_path(schema: dict[str, Any], path: tuple[Any, ...]) -> None:
    if not path:
        raise ValueError("A manual contract cannot drop the entire request schema")
    cursor: Any = schema
    for part in path[:-1]:
        cursor = _child(cursor, part, path)
    final = path[-1]
    if isinstance(cursor, dict) and final in cursor:
        del cursor[final]
    elif isinstance(cursor, list) and isinstance(final, int) and 0 <= final < len(cursor):
        del cursor[final]
    else:
        raise ValueError(f"Manual schema drop target does not exist: {_path_text(path)}")
