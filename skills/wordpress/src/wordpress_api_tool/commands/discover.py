from __future__ import annotations

from typing import Any

from ..http import HttpClient
from ..wp_api import WordPressApi


def _get_str(obj: dict[str, Any], key: str) -> str | None:
    v = obj.get(key)
    return v if isinstance(v, str) else None


def _get_bool(obj: dict[str, Any], key: str) -> bool | None:
    v = obj.get(key)
    return v if isinstance(v, bool) else None


def _get_str_list(obj: dict[str, Any], key: str) -> list[str]:
    v = obj.get(key)
    if not isinstance(v, list):
        return []
    out: list[str] = []
    for item in v:
        if isinstance(item, str):
            out.append(item)
    return out


def _stable_discover_payload(*, results: list[dict[str, Any]], raw: dict[str, Any] | None) -> dict[str, Any]:
    payload: dict[str, Any] = {"ok": True, "count": len(results), "results": results}
    if raw is not None:
        payload["raw"] = raw
    return payload


def cmd_discover_post_types(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )
    raw = api.types(context=str(getattr(args, "context", "view")))
    results: list[dict[str, Any]] = []
    for slug in sorted(raw.keys(), key=str):
        v = raw.get(slug)
        if not isinstance(v, dict):
            continue
        results.append(
            {
                "slug": str(slug),
                "name": _get_str(v, "name"),
                "rest_base": _get_str(v, "rest_base"),
                "rest_namespace": _get_str(v, "rest_namespace"),
                "hierarchical": _get_bool(v, "hierarchical"),
                "taxonomies": _get_str_list(v, "taxonomies"),
            }
        )
    ctx["out"].emit(_stable_discover_payload(results=results, raw=raw if bool(args.include_raw) else None))
    return 0


def cmd_discover_statuses(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )
    raw = api.statuses(context=str(getattr(args, "context", "view")))
    results: list[dict[str, Any]] = []
    for slug in sorted(raw.keys(), key=str):
        v = raw.get(slug)
        if not isinstance(v, dict):
            continue
        results.append(
            {
                "slug": str(slug),
                "name": _get_str(v, "name"),
                "public": _get_bool(v, "public"),
                "protected": _get_bool(v, "protected"),
                "private": _get_bool(v, "private"),
                "show_in_list": _get_bool(v, "show_in_list"),
                "date_floating": _get_bool(v, "date_floating"),
            }
        )
    ctx["out"].emit(_stable_discover_payload(results=results, raw=raw if bool(args.include_raw) else None))
    return 0


def cmd_discover_taxonomies(args, ctx) -> int:
    api = WordPressApi.from_config(
        ctx["cfg"],
        HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"]),
    )
    raw = api.taxonomies(context=str(getattr(args, "context", "view")))
    results: list[dict[str, Any]] = []
    for slug in sorted(raw.keys(), key=str):
        v = raw.get(slug)
        if not isinstance(v, dict):
            continue
        results.append(
            {
                "slug": str(slug),
                "name": _get_str(v, "name"),
                "rest_base": _get_str(v, "rest_base"),
                "rest_namespace": _get_str(v, "rest_namespace"),
                "hierarchical": _get_bool(v, "hierarchical"),
                "types": _get_str_list(v, "types"),
            }
        )
    ctx["out"].emit(_stable_discover_payload(results=results, raw=raw if bool(args.include_raw) else None))
    return 0
