from __future__ import annotations

from pathlib import Path
from typing import Any

from ..freepik_api import FreepikApi
from ..http import HttpClient
from ..jobs_csv import write_jobs_csv
from ..shortlist import shape_search_shortlist


def _parse_params(params: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in params:
        if "=" not in p:
            raise RuntimeError(f"Invalid --param (expected key=value): {p}")
        k, v = p.split("=", 1)
        out[k] = v
    return out


def _detail_data(detail: Any) -> dict[str, Any]:
    if not isinstance(detail, dict):
        return {}
    d = detail.get("data")
    return d if isinstance(d, dict) else detail


def _search_data_list(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    data = payload.get("data")
    if not isinstance(data, list):
        return []
    return [x for x in data if isinstance(x, dict)]


def _shape_shortlist_output(
    *,
    payload: Any,
    query: str,
    page: int,
    limit: int,
    jobs_csv: dict[str, Any] | None,
) -> dict[str, Any]:
    items = _search_data_list(payload)
    out: dict[str, Any] = {
        "ok": True,
        "mode": "search_shortlist",
        "query": query,
        "page": page,
        "limit": limit,
        "count": len(items),
        "items": shape_search_shortlist(items=items)["items"],
    }
    if jobs_csv:
        out["jobs_csv"] = jobs_csv
    if isinstance(payload, dict) and payload.get("tool"):
        out["tool"] = payload["tool"]
    return out


def _maybe_write_jobs_csv(*, args: Any, payload: Any) -> dict[str, Any] | None:
    path = (str(getattr(args, "write_jobs", "") or "")).strip()
    if not path:
        return None

    items = _search_data_list(payload)
    ids = [str(x.get("id") or "") for x in items if x.get("id") is not None]

    fmt = str(getattr(args, "job_format", "jpg") or "jpg")
    image_size = (str(getattr(args, "job_image_size", "") or "")).strip() or None
    result = write_jobs_csv(Path(path), resource_ids=ids, fmt=fmt, image_size=image_size)
    return {"path": result.path, "rows": result.rows, "columns": result.columns}


def _cmd_search(
    args: Any,
    ctx: dict[str, Any],
    *,
    default_params: dict[str, str] | None = None,
) -> int:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"], user_agent="freepik-api-tool/0.1")
    api = FreepikApi(cfg=cfg, http=http)

    extra: dict[str, str] = {}
    if default_params:
        extra.update(default_params)
    extra.update(_parse_params(args.param))
    payload = api.get_resources(
        query=args.query,
        page=int(args.page),
        limit=int(args.limit),
        extra_params=extra,
    )

    if getattr(args, "exclude_ai", False):
        if not isinstance(payload, dict):
            raise RuntimeError("Refused: search response is not a JSON object")
        data = payload.get("data")
        if not isinstance(data, list):
            raise RuntimeError("Refused: search response missing data list")

        kept: list[dict[str, Any]] = []
        removed_ids: list[str] = []
        unknown = 0
        checked = 0

        for item in data:
            if not isinstance(item, dict):
                unknown += 1
                continue
            rid = item.get("id")
            if rid is None:
                unknown += 1
                continue

            checked += 1
            detail = api.get_resource(str(rid))
            dd = _detail_data(detail)
            if dd.get("id") is not None and str(dd["id"]) != str(rid):
                removed_ids.append(str(rid))
                unknown += 1
                continue
            is_ai = dd.get("is_ai_generated") is True
            has_prompt = dd.get("has_prompt") is True
            if is_ai or has_prompt:
                removed_ids.append(str(rid))
                continue
            if dd.get("is_ai_generated") is False and dd.get("has_prompt") is False:
                kept.append(item)
            else:
                removed_ids.append(str(rid))
                unknown += 1

        payload = dict(payload)
        payload["data"] = kept
        payload["tool"] = {
            "exclude_ai": True,
            "checked": checked,
            "removed": len(data) - len(kept),
            "removed_ids": removed_ids,
            "unknown": unknown,
            "kept": len(kept),
            "note": (
                "Only assets with both is_ai_generated and has_prompt set to false are included."
            ),
        }

    jobs_csv = _maybe_write_jobs_csv(args=args, payload=payload)
    if getattr(args, "shortlist", False):
        ctx["out"].emit(
            _shape_shortlist_output(
                payload=payload,
                query=str(args.query),
                page=int(args.page),
                limit=int(args.limit),
                jobs_csv=jobs_csv,
            )
        )
        return 0

    if jobs_csv and isinstance(payload, dict):
        out_payload = dict(payload)
        tool_meta: dict[str, Any] = {}
        existing_tool = out_payload.get("tool")
        if isinstance(existing_tool, dict):
            tool_meta.update(existing_tool)
        tool_meta["jobs_csv"] = jobs_csv
        out_payload["tool"] = tool_meta
        payload = out_payload

    ctx["out"].emit(payload)
    return 0


def cmd_search_images(args: Any, ctx: dict[str, Any]) -> int:
    return _cmd_search(args, ctx)


def cmd_search_photos(args: Any, ctx: dict[str, Any]) -> int:
    default_params = {"filters[content_type][]": "photo"}
    return _cmd_search(args, ctx, default_params=default_params)
