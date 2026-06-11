from __future__ import annotations

import time
from typing import Any, Callable

from ..errors import SafetyError, ValidationError
from ..json_files import write_json_file
from ..pagination import PER_PAGE_MAX_DEFAULT, validate_page, validate_per_page
from ..unsplash_client import UnsplashClient, validate_positive_int, validate_username


def _validate_sleep_ms(value: Any, *, field: str = "--sleep-ms") -> int:
    if value is None:
        return 0
    try:
        n = int(value)
    except Exception:
        raise ValidationError(f"{field} must be an integer") from None
    if n < 0:
        raise ValidationError(f"{field} must be >= 0")
    return n


def _export_pages(
    *,
    endpoint: str,
    path: str,
    base_params: dict[str, Any],
    out_path: str,
    start_page: int,
    max_pages: int,
    per_page: int,
    sleep_ms: int,
    item_extractor: Callable[[Any], list[Any]],
    ctx: dict[str, Any],
) -> int:
    if max_pages > 1 and not bool(ctx.get("yes")):
        raise SafetyError("Refused: export with --max-pages > 1 requires --yes")

    client: UnsplashClient = ctx["client"]
    pages: list[dict[str, Any]] = []
    items: list[Any] = []

    for page in range(start_page, start_page + max_pages):
        params = {**base_params, "page": page, "per_page": per_page}
        data = client.get(path, params=params)
        pages.append({"page": page, "data": data})
        items.extend(item_extractor(data))
        if sleep_ms:
            time.sleep(sleep_ms / 1000.0)

    export_obj = {
        "endpoint": endpoint,
        "path": path,
        "params": {
            **base_params,
            "start_page": start_page,
            "max_pages": max_pages,
            "per_page": per_page,
            "per_page_max": PER_PAGE_MAX_DEFAULT,
        },
        "pages": pages,
        "items": items,
    }
    out_file = write_json_file(out_path, export_obj)

    summary = {
        "ok": True,
        "wrote": True,
        "out_path": out_file,
        "pages_fetched": len(pages),
        "items_written": len(items),
        "endpoint": endpoint,
        "params": export_obj["params"],
    }
    ctx["audit"].write(
        "export.wrote",
        {
            "endpoint": endpoint,
            "path": path,
            "out_path": out_file,
            "start_page": start_page,
            "max_pages": max_pages,
            "per_page": per_page,
            "items_written": len(items),
        },
    )
    ctx["out"].emit(summary)
    return 0


def _parse_common_export_args(args: Any) -> tuple[str, int, int, int, int]:
    out_path = str(getattr(args, "out", "") or "").strip()
    if not out_path:
        raise ValidationError("Missing --out")
    start_page = validate_page(getattr(args, "start_page", None), field="--start-page")
    max_pages = validate_positive_int(getattr(args, "max_pages", None), field="--max-pages")
    per_page = validate_per_page(getattr(args, "per_page", None), field="--per-page")
    sleep_ms = _validate_sleep_ms(getattr(args, "sleep_ms", None), field="--sleep-ms")
    return out_path, start_page, max_pages, per_page, sleep_ms


def _extract_list_items(data: Any) -> list[Any]:
    if isinstance(data, list):
        return data
    return [data]


def _extract_search_results(data: Any) -> list[Any]:
    if isinstance(data, dict) and isinstance(data.get("results"), list):
        return list(data["results"])
    return [data]


def cmd_export_photos_search(args: Any, ctx: dict[str, Any]) -> int:
    query = str(getattr(args, "query", "") or "").strip()
    if not query:
        raise ValidationError("Missing --query")

    out_path, start_page, max_pages, per_page, sleep_ms = _parse_common_export_args(args)
    order_by = str(getattr(args, "order_by", "") or "").strip() or None
    if order_by not in {None, "relevant", "latest"}:
        raise ValidationError("--order-by must be one of: relevant, latest")

    base_params = {"query": query, **({} if order_by is None else {"order_by": order_by})}
    return _export_pages(
        endpoint="GET /search/photos",
        path="/search/photos",
        base_params=base_params,
        out_path=out_path,
        start_page=start_page,
        max_pages=max_pages,
        per_page=per_page,
        sleep_ms=sleep_ms,
        item_extractor=_extract_search_results,
        ctx=ctx,
    )


def cmd_export_photos_list(args: Any, ctx: dict[str, Any]) -> int:
    out_path, start_page, max_pages, per_page, sleep_ms = _parse_common_export_args(args)
    order_by = str(getattr(args, "order_by", "") or "").strip() or None
    if order_by not in {None, "latest", "oldest", "popular"}:
        raise ValidationError("--order-by must be one of: latest, oldest, popular")

    base_params = {} if order_by is None else {"order_by": order_by}
    return _export_pages(
        endpoint="GET /photos",
        path="/photos",
        base_params=base_params,
        out_path=out_path,
        start_page=start_page,
        max_pages=max_pages,
        per_page=per_page,
        sleep_ms=sleep_ms,
        item_extractor=_extract_list_items,
        ctx=ctx,
    )


def cmd_export_collections_photos(args: Any, ctx: dict[str, Any]) -> int:
    collection_id = validate_positive_int(getattr(args, "id", None), field="--id")
    orientation = str(getattr(args, "orientation", "") or "").strip() or None
    if orientation not in {None, "landscape", "portrait", "squarish"}:
        raise ValidationError("--orientation must be one of: landscape, portrait, squarish")

    out_path, start_page, max_pages, per_page, sleep_ms = _parse_common_export_args(args)
    base_params = {} if orientation is None else {"orientation": orientation}
    return _export_pages(
        endpoint="GET /collections/:id/photos",
        path=f"/collections/{collection_id}/photos",
        base_params=base_params,
        out_path=out_path,
        start_page=start_page,
        max_pages=max_pages,
        per_page=per_page,
        sleep_ms=sleep_ms,
        item_extractor=_extract_list_items,
        ctx=ctx,
    )


def cmd_export_topics_photos(args: Any, ctx: dict[str, Any]) -> int:
    topic_id = str(getattr(args, "id", "") or "").strip()
    if not topic_id:
        raise ValidationError("Missing --id")
    orientation = str(getattr(args, "orientation", "") or "").strip() or None
    if orientation not in {None, "landscape", "portrait", "squarish"}:
        raise ValidationError("--orientation must be one of: landscape, portrait, squarish")

    out_path, start_page, max_pages, per_page, sleep_ms = _parse_common_export_args(args)
    base_params = {} if orientation is None else {"orientation": orientation}
    return _export_pages(
        endpoint="GET /topics/:id/photos",
        path=f"/topics/{topic_id}/photos",
        base_params=base_params,
        out_path=out_path,
        start_page=start_page,
        max_pages=max_pages,
        per_page=per_page,
        sleep_ms=sleep_ms,
        item_extractor=_extract_list_items,
        ctx=ctx,
    )


def cmd_export_users_photos(args: Any, ctx: dict[str, Any]) -> int:
    username = validate_username(str(getattr(args, "username", "") or ""))
    order_by = str(getattr(args, "order_by", "") or "").strip() or None
    if order_by not in {None, "latest", "oldest", "popular", "views", "downloads"}:
        raise ValidationError("--order-by must be one of: latest, oldest, popular, views, downloads")
    orientation = str(getattr(args, "orientation", "") or "").strip() or None
    if orientation not in {None, "landscape", "portrait", "squarish"}:
        raise ValidationError("--orientation must be one of: landscape, portrait, squarish")

    out_path, start_page, max_pages, per_page, sleep_ms = _parse_common_export_args(args)
    base_params = {
        **({} if order_by is None else {"order_by": order_by}),
        **({} if orientation is None else {"orientation": orientation}),
    }
    return _export_pages(
        endpoint="GET /users/:username/photos",
        path=f"/users/{username}/photos",
        base_params=base_params,
        out_path=out_path,
        start_page=start_page,
        max_pages=max_pages,
        per_page=per_page,
        sleep_ms=sleep_ms,
        item_extractor=_extract_list_items,
        ctx=ctx,
    )
