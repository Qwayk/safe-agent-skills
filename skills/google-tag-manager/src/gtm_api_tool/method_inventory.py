from __future__ import annotations

import re
from dataclasses import dataclass

from .discovery import MethodSpec, iter_methods


_CAMEL_BOUNDARY = re.compile(r"([a-z0-9])([A-Z])")


def to_kebab(token: str) -> str:
    t = str(token or "").strip()
    if not t:
        return ""
    t = t.replace("_", "-")
    t = _CAMEL_BOUNDARY.sub(r"\1-\2", t)
    t = re.sub(r"[^a-zA-Z0-9-]+", "-", t)
    t = re.sub(r"-{2,}", "-", t).strip("-")
    return t.lower()


def method_id_to_command_tokens(method_id: str) -> list[str]:
    mid = str(method_id or "").strip()
    if not mid:
        return []
    if mid.startswith("tagmanager."):
        mid = mid[len("tagmanager.") :]
    return [to_kebab(t) for t in mid.split(".") if to_kebab(t)]


def method_id_to_command(method_id: str) -> str:
    toks = method_id_to_command_tokens(method_id)
    return "gtm-api-tool " + " ".join(toks) if toks else "gtm-api-tool"


@dataclass(frozen=True)
class InventoryRow:
    method_id: str
    http_method: str
    path: str
    command_tokens: tuple[str, ...]

    @property
    def command(self) -> str:
        return "gtm-api-tool " + " ".join(self.command_tokens)


def build_inventory() -> list[InventoryRow]:
    rows: list[InventoryRow] = []
    for m in iter_methods():
        rows.append(
            InventoryRow(
                method_id=m.method_id,
                http_method=m.http_method,
                path=m.path,
                command_tokens=tuple(method_id_to_command_tokens(m.method_id)),
            )
        )
    rows.sort(key=lambda r: r.method_id)
    return rows


def official_method_ids() -> list[str]:
    return [r.method_id for r in build_inventory()]


def official_commands() -> list[str]:
    return [r.command for r in build_inventory()]


def method_specs() -> list[MethodSpec]:
    return iter_methods()

