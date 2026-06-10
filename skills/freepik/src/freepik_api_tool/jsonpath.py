from __future__ import annotations

from typing import Any


def jsonpath_get(data: Any, path: str) -> Any:
    """
    Minimal JSONPath-ish getter:
    - dot notation: a.b.c
    - bracket numeric indices: items[0].url

    This is intentionally tiny (no full JSONPath language).
    """
    cur: Any = data
    for raw_part in path.split("."):
        part = raw_part.strip()
        if not part:
            continue
        while True:
            if "[" in part and part.endswith("]"):
                name, idx_s = part[:-1].split("[", 1)
                name = name.strip()
                if name:
                    if not isinstance(cur, dict) or name not in cur:
                        raise KeyError(f"Missing key: {name}")
                    cur = cur[name]
                idx = int(idx_s)
                if not isinstance(cur, list):
                    raise TypeError(f"Expected list at {raw_part}")
                cur = cur[idx]
                part = ""
                continue
            break
        if part:
            if not isinstance(cur, dict) or part not in cur:
                raise KeyError(f"Missing key: {part}")
            cur = cur[part]
    return cur


def find_first_url(value: Any) -> str | None:
    if isinstance(value, str) and value.startswith("http"):
        return value
    if isinstance(value, dict):
        for k, v in value.items():
            if isinstance(v, str) and v.startswith("http") and ("license" in k.lower() or "url" in k.lower()):
                return v
        for v in value.values():
            u = find_first_url(v)
            if u:
                return u
    if isinstance(value, list):
        for v in value:
            u = find_first_url(v)
            if u:
                return u
    return None


def find_url_by_keywords(value: Any, *, include: tuple[str, ...], exclude: tuple[str, ...] = ()) -> str | None:
    """
    Best-effort URL finder for responses we haven't fully modeled yet.
    Prefers dict keys that contain any of `include` keywords and none of `exclude`.
    """
    inc = tuple(k.lower() for k in include)
    exc = tuple(k.lower() for k in exclude)
    if isinstance(value, dict):
        for k, v in value.items():
            key = k.lower()
            if any(w in key for w in inc) and not any(w in key for w in exc):
                if isinstance(v, str) and v.startswith("http"):
                    return v
                nested = find_first_url(v)
                if nested:
                    return nested
        for v in value.values():
            u = find_url_by_keywords(v, include=include, exclude=exclude)
            if u:
                return u
    if isinstance(value, list):
        for v in value:
            u = find_url_by_keywords(v, include=include, exclude=exclude)
            if u:
                return u
    if isinstance(value, str) and value.startswith("http") and include == ("url",):
        return value
    return None
