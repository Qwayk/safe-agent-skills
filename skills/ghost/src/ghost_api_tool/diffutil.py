from __future__ import annotations

import difflib
import json
from collections.abc import Iterable
from typing import Any


def unified_diff(before: str, after: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile="before",
            tofile="after",
            lineterm="",
        )
    )


def diff_dict(before: dict[str, Any], after: dict[str, Any], *, keys: Iterable[str]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for k in keys:
        if before.get(k) != after.get(k):
            changes.append({"field": k, "before": before.get(k), "after": after.get(k)})
    return changes


def stable_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2)
