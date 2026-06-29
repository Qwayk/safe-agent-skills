from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ApiOperation:
    group: str
    command: str
    operation_id: str
    method: str
    path: str
    summary: str
    description: str
    base_url_ref: str
    path_params: list[str]
    required_query_params: list[str]
    request_body: bool
    needs_plan: bool

    @property
    def is_write(self) -> bool:
        return self.method.upper() in {"POST", "PUT", "PATCH", "DELETE"}

    @property
    def is_high_risk(self) -> bool:
        if self.needs_plan:
            return True
        if self.method.upper() in {"DELETE", "PATCH"}:
            return True
        marker = (self.command + " " + self.operation_id).lower()
        return any(term in marker for term in ("execute", "run", "send", "delete", "create-authentication", "authorize", "pause", "resume", "destroy", "release", "acknowledge", "lease", "app-health"))

    @property
    def needs_ack(self) -> bool:
        if self.is_high_risk:
            return True
        return self.method.upper() == "DELETE" or "ack" in self.command.lower()


_RAW_OPERATIONS_PATH = Path(__file__).with_name("operations_data.json")


def load_operations() -> list[ApiOperation]:
    raw = json.loads(_RAW_OPERATIONS_PATH.read_text(encoding="utf-8"))
    out: list[ApiOperation] = []
    for item in raw:
        out.append(
            ApiOperation(
                group=str(item.get("group", "")),
                command=str(item.get("command", "")),
                operation_id=str(item.get("operation_id", "")),
                method=str(item.get("method", "GET")).upper(),
                path=str(item.get("path", "")),
                summary=str(item.get("summary", "")),
                description=str(item.get("description", "")),
                base_url_ref=str(item.get("base_url_ref", "partner")),
                path_params=list(item.get("path_params", []) or []),
                required_query_params=list(item.get("required_query_params", []) or []),
                request_body=bool(item.get("request_body", False)),
                needs_plan=bool(item.get("needs_plan", False)),
            )
        )
    return out


def by_group() -> dict[str, list[ApiOperation]]:
    groups: dict[str, list[ApiOperation]] = {}
    for op in load_operations():
        groups.setdefault(op.group, []).append(op)
    return groups
