from __future__ import annotations

from pathlib import Path
from typing import Any

from ..freepik_api import FreepikApi
from ..http import HttpClient
from ..jobs_csv import write_jobs_csv


def _detail_data(detail: Any) -> dict[str, Any]:
    if not isinstance(detail, dict):
        return {}
    d = detail.get("data")
    return d if isinstance(d, dict) else detail


def _extract_related_resource_groups(data: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    rr = data.get("related_resources")
    if not isinstance(rr, dict):
        return {}
    groups: dict[str, list[dict[str, Any]]] = {}
    for k, v in rr.items():
        if not isinstance(k, str) or not k:
            continue
        if not isinstance(v, list):
            continue
        items = [x for x in v if isinstance(x, dict)]
        if items:
            groups[k] = items
    return groups


def _ids_from_related_group(items: list[dict[str, Any]]) -> list[str]:
    out: set[str] = set()
    for item in items:
        rid = item.get("id") or item.get("resource_id") or item.get("resourceId")
        if rid is None:
            continue
        s = str(rid).strip()
        if s:
            out.add(s)
    return sorted(out)


def _build_fallback_query(data: dict[str, Any]) -> str:
    query = ""
    tags = data.get("tags")
    if isinstance(tags, list) and tags:
        parts: list[str] = []
        for t in tags[:5]:
            if isinstance(t, dict):
                name = t.get("name") or t.get("slug")
                if name:
                    parts.append(str(name))
            elif t:
                parts.append(str(t))
        query = " ".join(parts)
    if not query:
        query = str(data.get("title") or data.get("name") or "")
    return query.strip()


def cmd_resource_get(args: Any, ctx: dict[str, Any]) -> int:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"], user_agent="freepik-api-tool/0.1")
    api = FreepikApi(cfg=cfg, http=http)

    payload = api.get_resource(args.id)
    ctx["out"].emit(payload)
    return 0


def cmd_resource_related(args: Any, ctx: dict[str, Any]) -> int:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"], user_agent="freepik-api-tool/0.1")
    api = FreepikApi(cfg=cfg, http=http)

    rid = args.id
    limit = int(args.limit)

    detail = api.get_resource(rid)
    if not isinstance(detail, dict):
        raise RuntimeError("Refused: resource detail response is not a JSON object")
    data = _detail_data(detail)

    groups = _extract_related_resource_groups(data)
    related_groups: dict[str, list[str]] = {k: _ids_from_related_group(v)[:limit] for k, v in groups.items()}

    related_resources = []
    suggested_items = groups.get("suggested") or []
    if suggested_items:
        related_resources = suggested_items[:limit]

    related_tags = data.get("related_tags")
    out: dict[str, Any] = {
        "mode": "detail_related",
        "resource_id": rid,
        "related_resources": related_resources,
        "related_tags": related_tags,
    }
    if related_groups:
        out["related_groups"] = related_groups
    if related_resources:
        ctx["out"].emit(out)
        return 0

    # Fallback: build a search query from tags/title.
    query = _build_fallback_query(data)

    if not query:
        ctx["out"].emit(out)
        return 0

    results = api.get_resources(query=query, page=1, limit=limit, extra_params={})
    out["fallback_query"] = query
    out["fallback_search_results"] = results
    ctx["out"].emit(out)
    return 0


def cmd_resource_shoot_pack(args: Any, ctx: dict[str, Any]) -> int:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"], user_agent="freepik-api-tool/0.1")
    api = FreepikApi(cfg=cfg, http=http)

    rid = str(args.id)
    limit = int(args.limit)

    detail = api.get_resource(rid)
    if not isinstance(detail, dict):
        raise RuntimeError("Refused: resource detail response is not a JSON object")
    data = _detail_data(detail)

    groups = _extract_related_resource_groups(data)
    group_flags = {
        "same_series": bool(getattr(args, "same_series", False)),
        "same_collection": bool(getattr(args, "same_collection", False)),
        "same_author": bool(getattr(args, "same_author", False)),
        "suggested": bool(getattr(args, "suggested", False)),
    }
    selected_groups = [k for k, enabled in group_flags.items() if enabled]
    structured_groups_priority = ("same_series", "same_collection", "same_author")
    structured_groups_available = [k for k in structured_groups_priority if k in groups]
    structured = bool(structured_groups_available)
    if not selected_groups and structured_groups_available:
        selected_groups = [structured_groups_available[0]]
    ids: list[str] = []
    mode = "related_groups"
    details: dict[str, Any] = {}

    if structured:
        collected: set[str] = set()
        for g in selected_groups:
            items = groups.get(g) or []
            for i in _ids_from_related_group(items):
                if i != rid:
                    collected.add(i)
        ids = sorted(collected)[:limit]
        details = {"selected_groups": selected_groups, "available_groups": sorted(groups.keys())}
    else:
        # Fallback: prefer the legacy "suggested" list if present; otherwise search by tags/title.
        rr = data.get("related_resources")
        suggested_list: list[dict[str, Any]] = []
        if isinstance(rr, dict):
            raw_suggested = rr.get("suggested")
            if isinstance(raw_suggested, list):
                suggested_list = [x for x in raw_suggested if isinstance(x, dict)]
        if suggested_list:
            mode = "fallback_suggested"
            ids = [x for x in _ids_from_related_group(suggested_list) if x != rid][:limit]
        else:
            query = _build_fallback_query(data)
            if not query:
                mode = "fallback_none"
                ids = []
            else:
                results = api.get_resources(query=query, page=1, limit=limit, extra_params={})
                mode = "fallback_search"
                if isinstance(results, dict) and isinstance(results.get("data"), list):
                    found: set[str] = set()
                    for item in results["data"]:
                        if not isinstance(item, dict):
                            continue
                        i = item.get("id")
                        if i is None:
                            continue
                        s = str(i).strip()
                        if s and s != rid:
                            found.add(s)
                    ids = sorted(found)[:limit]
                details = {"fallback_query": query}

    jobs_csv: dict[str, Any] | None = None
    write_jobs_path = (str(getattr(args, "write_jobs", "") or "")).strip()
    if write_jobs_path:
        fmt = str(getattr(args, "job_format", "jpg") or "jpg")
        image_size = (str(getattr(args, "job_image_size", "") or "")).strip() or None
        result = write_jobs_csv(Path(write_jobs_path), resource_ids=ids, fmt=fmt, image_size=image_size)
        jobs_csv = {"path": result.path, "rows": result.rows, "columns": result.columns}

    out: dict[str, Any] = {"ok": True, "mode": mode, "resource_id": rid, "ids": ids, "count": len(ids)}
    out.update(details)
    if jobs_csv:
        out["jobs_csv"] = jobs_csv

    ctx["out"].emit(out)
    return 0
