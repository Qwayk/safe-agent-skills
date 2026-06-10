from __future__ import annotations

import re
from dataclasses import dataclass

from .discovery import (
    MethodSpec,
    family_version,
    load_official_methods,
    load_shipped_methods,
    load_stable_discovery_methods,
)


_DISCOVERY_PREFIX = "merchantapi."
_CLI_TOOL = "google-merchant-api-tool"
_CAMEL_BOUNDARY = re.compile(r"([a-z0-9])([A-Z])")


def to_kebab(token: str) -> str:
    raw = str(token or "").strip()
    if not raw:
        return ""
    raw = raw.replace("_", "-")
    raw = _CAMEL_BOUNDARY.sub(r"\1-\2", raw)
    raw = re.sub(r"[^A-Za-z0-9-]+", "-", raw)
    raw = re.sub(r"-{2,}", "-", raw).strip("-")
    return raw.lower()


def method_id_to_command_tokens(method_id: str, family: str | None = None) -> tuple[str, ...]:
    mid = str(method_id or "").strip()
    if not mid:
        return ()
    if mid.startswith(_DISCOVERY_PREFIX):
        mid = mid[len(_DISCOVERY_PREFIX) :]

    tokens: list[str] = []
    for part in mid.split("."):
        tok = to_kebab(part)
        if tok:
            tokens.append(tok)
    base = tuple(tokens)
    if family:
        version = family_version(family)
        if version != "v1":
            if not base:
                return (version,)
            return (base[0], version, *base[1:])
    return base


def method_id_to_cli_command(method_id: str, cli: str = _CLI_TOOL, family: str | None = None) -> str:
    tokens = method_id_to_command_tokens(method_id, family=family)
    return f"{cli} " + " ".join(tokens) if tokens else cli


def method_to_command_tokens(method: MethodSpec) -> tuple[str, ...]:
    return method_id_to_command_tokens(method.command_id, family=method.family)


def method_to_cli_command(method: MethodSpec, cli: str = _CLI_TOOL) -> str:
    tokens = method_to_command_tokens(method)
    return f"{cli} " + " ".join(tokens) if tokens else cli


@dataclass(frozen=True)
class InventoryRow:
    family: str
    version: str
    method_id: str
    http_method: str
    path: str
    command_tokens: tuple[str, ...]
    method: MethodSpec

    @property
    def command(self) -> str:
        return " ".join([_CLI_TOOL, *self.command_tokens])


def _row_for_method(method: MethodSpec) -> InventoryRow:
    return InventoryRow(
        family=method.family,
        version=family_version(method.family),
        method_id=method.command_id,
        http_method=method.http_method,
        path=method.path,
        command_tokens=method_to_command_tokens(method),
        method=method,
    )


def build_inventory(methods: tuple[MethodSpec, ...]) -> tuple[InventoryRow, ...]:
    out = tuple(_row_for_method(method) for method in methods)
    return tuple(sorted(out, key=lambda r: (r.family, r.method_id, r.command)))


def build_stable_inventory() -> tuple[InventoryRow, ...]:
    return build_inventory(load_stable_discovery_methods())


def build_shipped_inventory() -> tuple[InventoryRow, ...]:
    return build_inventory(load_shipped_methods())


def build_official_inventory() -> tuple[InventoryRow, ...]:
    return build_inventory(load_official_methods())


def stable_method_ids() -> list[str]:
    return [row.method_id for row in build_stable_inventory()]


def shipped_method_keys() -> list[tuple[str, str]]:
    return [(row.family, row.method_id) for row in build_shipped_inventory()]


def official_method_keys() -> list[tuple[str, str]]:
    return [(row.family, row.method_id) for row in build_official_inventory()]


def stable_cli_commands() -> list[str]:
    return [row.command for row in build_stable_inventory()]


def shipped_cli_commands() -> list[str]:
    return [row.command for row in build_shipped_inventory()]
