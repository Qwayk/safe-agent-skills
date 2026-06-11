from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..api import PinterestApi, resolve_access_token
from ..write_framework import build_plan, build_receipt, require_write_allowed, write_operation


def _api(ctx: dict[str, Any]) -> PinterestApi:
    cfg = ctx["cfg"]
    access_token = "write-plan-or-refusal"
    if not bool(ctx.get("skip_auth_for_write_plan")):
        access_token = resolve_access_token(
            env_file=ctx["env_file"],
            env_access_token=cfg.access_token,
            env_refresh_token=cfg.refresh_token,
            app_id=cfg.app_id,
            app_secret=cfg.app_secret,
            base_url=cfg.base_url,
            http=ctx["http"],
        )
    return PinterestApi(
        base_url=cfg.base_url,
        http=ctx["http"],
        access_token=access_token,
    )


def _parse_kv_pairs(pairs: list[str] | None) -> dict[str, Any]:
    if not pairs:
        return {}
    out: dict[str, Any] = {}
    for raw in pairs:
        s = (raw or "").strip()
        if not s:
            continue
        if "=" not in s:
            raise RuntimeError(f"Invalid --param (expected key=value): {raw}")
        k, v = s.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            raise RuntimeError(f"Invalid --param (empty key): {raw}")
        if k in out:
            prev = out[k]
            if isinstance(prev, list):
                prev.append(v)
            else:
                out[k] = [prev, v]
        else:
            out[k] = v
    return out


def cmd_catalogs_list(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    params = _parse_kv_pairs(args.param)
    params["ad_account_id"] = ad_account_id
    items, bookmark, pages = api.list_all(
        "/catalogs",
        params=params,
        limit=int(args.limit),
        page_size=int(args.page_size),
        bookmark=(str(args.bookmark).strip() if args.bookmark else None),
    )
    out = {
        "ok": True,
        "ad_account_id": ad_account_id,
        "count": len(items),
        "pages": pages,
        "bookmark": bookmark,
        "items": items,
    }
    ctx["audit"].write("catalogs.list", {"ad_account_id": ad_account_id, "count": out["count"], "pages": pages})
    ctx["out"].emit(out)
    return 0


def cmd_catalogs_feeds_list(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    params = _parse_kv_pairs(args.param)
    params["ad_account_id"] = ad_account_id
    items, bookmark, pages = api.list_all(
        "/catalogs/feeds",
        params=params,
        limit=int(args.limit),
        page_size=int(args.page_size),
        bookmark=(str(args.bookmark).strip() if args.bookmark else None),
    )
    out = {
        "ok": True,
        "ad_account_id": ad_account_id,
        "count": len(items),
        "pages": pages,
        "bookmark": bookmark,
        "items": items,
    }
    ctx["audit"].write("catalogs.feeds.list", {"ad_account_id": ad_account_id, "count": out["count"], "pages": pages})
    ctx["out"].emit(out)
    return 0


def cmd_catalogs_feeds_get(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    feed_id = str(args.id).strip()
    if not feed_id:
        raise RuntimeError("--id is required")
    params = _parse_kv_pairs(args.param)
    params["ad_account_id"] = ad_account_id
    data = api.get(f"/catalogs/feeds/{feed_id}", params=params or None)
    out = {"ok": True, "ad_account_id": ad_account_id, "feed": data}
    ctx["audit"].write("catalogs.feeds.get", {"ad_account_id": ad_account_id, "feed_id": feed_id})
    ctx["out"].emit(out)
    return 0


def cmd_catalogs_feed_processing_results_list(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    feed_id = str(args.feed_id).strip()
    if not feed_id:
        raise RuntimeError("--feed-id is required")
    params = _parse_kv_pairs(args.param)
    params["ad_account_id"] = ad_account_id
    items, bookmark, pages = api.list_all(
        f"/catalogs/feeds/{feed_id}/processing_results",
        params=params,
        limit=int(args.limit),
        page_size=int(args.page_size),
        bookmark=(str(args.bookmark).strip() if args.bookmark else None),
    )
    out = {
        "ok": True,
        "ad_account_id": ad_account_id,
        "feed_id": feed_id,
        "count": len(items),
        "pages": pages,
        "bookmark": bookmark,
        "items": items,
    }
    ctx["audit"].write(
        "catalogs.feed_processing_results.list",
        {"ad_account_id": ad_account_id, "feed_id": feed_id, "count": out["count"], "pages": pages},
    )
    ctx["out"].emit(out)
    return 0


def cmd_catalogs_product_groups_list(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    params = _parse_kv_pairs(args.param)
    params["ad_account_id"] = ad_account_id
    items, bookmark, pages = api.list_all(
        "/catalogs/product_groups",
        params=params,
        limit=int(args.limit),
        page_size=int(args.page_size),
        bookmark=(str(args.bookmark).strip() if args.bookmark else None),
    )
    out = {
        "ok": True,
        "ad_account_id": ad_account_id,
        "count": len(items),
        "pages": pages,
        "bookmark": bookmark,
        "items": items,
    }
    ctx["audit"].write(
        "catalogs.product_groups.list",
        {"ad_account_id": ad_account_id, "count": out["count"], "pages": pages},
    )
    ctx["out"].emit(out)
    return 0


def cmd_catalogs_product_groups_get(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(args.ad_account_id).strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    product_group_id = str(args.id).strip()
    if not product_group_id:
        raise RuntimeError("--id is required")
    params = _parse_kv_pairs(args.param)
    params["ad_account_id"] = ad_account_id
    data = api.get(f"/catalogs/product_groups/{product_group_id}", params=params or None)
    out = {"ok": True, "ad_account_id": ad_account_id, "product_group": data}
    ctx["audit"].write(
        "catalogs.product_groups.get",
        {"ad_account_id": ad_account_id, "product_group_id": product_group_id},
    )
    ctx["out"].emit(out)
    return 0


def cmd_catalogs_product_group_products_list(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(getattr(args, "ad_account_id", "") or "").strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    product_group_id = str(getattr(args, "product_group_id", "") or "").strip()
    if not product_group_id:
        raise RuntimeError("--product-group-id is required")
    params = _parse_kv_pairs(args.param)
    params["ad_account_id"] = ad_account_id
    items, bookmark, pages = api.list_all(
        f"/catalogs/product_groups/{product_group_id}/products",
        params=params,
        limit=int(args.limit),
        page_size=int(args.page_size),
        bookmark=(str(args.bookmark).strip() if args.bookmark else None),
    )
    out = {
        "ok": True,
        "ad_account_id": ad_account_id,
        "product_group_id": product_group_id,
        "count": len(items),
        "pages": pages,
        "bookmark": bookmark,
        "items": items,
    }
    ctx["audit"].write(
        "catalogs.product_group_products.list",
        {"ad_account_id": ad_account_id, "product_group_id": product_group_id, "count": out["count"], "pages": pages},
    )
    ctx["out"].emit(out)
    return 0


def cmd_catalogs_processing_result_item_issues_list(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    processing_result_id = str(getattr(args, "processing_result_id", "") or "").strip()
    if not processing_result_id:
        raise RuntimeError("--processing-result-id is required")
    params = _parse_kv_pairs(args.param)
    ad_account_id = str(getattr(args, "ad_account_id", "") or "").strip()
    if ad_account_id:
        params["ad_account_id"] = ad_account_id
    items, bookmark, pages = api.list_all(
        f"/catalogs/processing_results/{processing_result_id}/item_issues",
        params=params,
        limit=int(args.limit),
        page_size=int(args.page_size),
        bookmark=(str(args.bookmark).strip() if args.bookmark else None),
    )
    out = {
        "ok": True,
        "ad_account_id": ad_account_id or None,
        "processing_result_id": processing_result_id,
        "count": len(items),
        "pages": pages,
        "bookmark": bookmark,
        "items": items,
    }
    ctx["audit"].write(
        "catalogs.item_issues.list",
        {"processing_result_id": processing_result_id, "count": out["count"], "pages": pages},
    )
    ctx["out"].emit(out)
    return 0


def cmd_catalogs_reports_list(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(getattr(args, "ad_account_id", "") or "").strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    params = _parse_kv_pairs(args.param)
    params["ad_account_id"] = ad_account_id
    items, bookmark, pages = api.list_all(
        "/catalogs/reports",
        params=params,
        limit=int(args.limit),
        page_size=int(args.page_size),
        bookmark=(str(args.bookmark).strip() if args.bookmark else None),
    )
    out = {
        "ok": True,
        "ad_account_id": ad_account_id,
        "count": len(items),
        "pages": pages,
        "bookmark": bookmark,
        "items": items,
    }
    ctx["audit"].write("catalogs.reports.list", {"ad_account_id": ad_account_id, "count": out["count"], "pages": pages})
    ctx["out"].emit(out)
    return 0


def cmd_catalogs_reports_stats(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(getattr(args, "ad_account_id", "") or "").strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    params = _parse_kv_pairs(args.param)
    params["ad_account_id"] = ad_account_id
    data = api.get("/catalogs/reports/stats", params=params or None)
    out = {"ok": True, "ad_account_id": ad_account_id, "params": params, "data": data}
    ctx["audit"].write("catalogs.reports.stats", {"ad_account_id": ad_account_id})
    ctx["out"].emit(out)
    return 0


def cmd_catalogs_available_filter_values(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    params = _parse_kv_pairs(getattr(args, "param", None))
    ad_account_id = str(getattr(args, "ad_account_id", "") or "").strip()
    if ad_account_id:
        params["ad_account_id"] = ad_account_id
    data = api.get("/catalogs/available_filter_values", params=params or None)
    out = {
        "ok": True,
        "ad_account_id": ad_account_id or None,
        "path": "/catalogs/available_filter_values",
        "params": params,
        "data": data,
    }
    ctx["audit"].write("catalogs.available_filter_values", {"ad_account_id": ad_account_id or None})
    ctx["out"].emit(out)
    return 0


def cmd_catalogs_product_group_product_counts(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    product_group_id = str(getattr(args, "product_group_id", "") or "").strip()
    if not product_group_id:
        raise RuntimeError("--product-group-id is required")
    params = _parse_kv_pairs(getattr(args, "param", None))
    ad_account_id = str(getattr(args, "ad_account_id", "") or "").strip()
    if ad_account_id:
        params["ad_account_id"] = ad_account_id
    path = f"/catalogs/product_groups/{product_group_id}/product_counts"
    data = api.get(path, params=params or None)
    out = {
        "ok": True,
        "ad_account_id": ad_account_id or None,
        "product_group_id": product_group_id,
        "path": path,
        "params": params,
        "data": data,
    }
    ctx["audit"].write(
        "catalogs.product_groups.product_counts",
        {"ad_account_id": ad_account_id or None, "product_group_id": product_group_id},
    )
    ctx["out"].emit(out)
    return 0


def cmd_catalogs_items_batch_get(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    batch_id = str(getattr(args, "batch_id", "") or "").strip()
    if not batch_id:
        raise RuntimeError("--batch-id is required")
    params = _parse_kv_pairs(getattr(args, "param", None))
    ad_account_id = str(getattr(args, "ad_account_id", "") or "").strip()
    if ad_account_id:
        params["ad_account_id"] = ad_account_id
    path = f"/catalogs/items/batch/{batch_id}"
    data = api.get(path, params=params or None)
    out = {
        "ok": True,
        "ad_account_id": ad_account_id or None,
        "batch_id": batch_id,
        "path": path,
        "params": params,
        "data": data,
    }
    ctx["audit"].write("catalogs.items.batch.get", {"ad_account_id": ad_account_id or None, "batch_id": batch_id})
    ctx["out"].emit(out)
    return 0


def _load_json_file(path: str) -> Any:
    p = Path(str(path)).expanduser().resolve()
    if not p.exists():
        raise RuntimeError(f"JSON file not found: {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise RuntimeError(f"Invalid JSON in file: {p}: {type(e).__name__}") from None


def _load_json_object_file(path: str) -> dict[str, Any]:
    body = _load_json_file(path)
    if not isinstance(body, dict):
        raise RuntimeError("JSON body must be an object")
    return body


def cmd_catalogs_create(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(getattr(args, "ad_account_id", "") or "").strip()
    body = _load_json_object_file(args.body_file)
    params: dict[str, Any] = {}
    if ad_account_id:
        params["ad_account_id"] = ad_account_id

    action = "catalogs.catalogs.create"
    request = write_operation(method="POST", path="/catalogs", params=(params or None), json_body=body)
    ops = [request]

    if not bool(ctx.get("apply")):
        out = build_plan(action=action, operations=ops, request=request)
        out.update({"resource": "catalogs", "operation": "create", "ad_account_id": ad_account_id or None})
        ctx["audit"].write(action, {"dry_run": True, "ad_account_id": ad_account_id or None})
        ctx["out"].emit(out)
        return 0

    require_write_allowed(ctx)

    created = api.post("/catalogs", json_body=body, params=params or None)
    created_id = str(created.get("id") or "").strip() if isinstance(created, dict) else ""
    if not created_id:
        raise RuntimeError("Catalog create response missing id; refusing to proceed without verification target")

    # No official GET /catalogs/{id} exists in v5 as of this tool version.
    verification = {
        "read_back": False,
        "verified_ids": [created_id],
        "note": "Pinterest API v5 does not expose GET /catalogs/{catalog_id}; verified by presence of id in create response.",
    }
    out = build_receipt(
        action=action,
        changed=True,
        operations=ops,
        request=request,
        before=None,
        write_result=created,
        after={"id": created_id},
    )
    out.update({"resource": "catalogs", "operation": "create", "ad_account_id": ad_account_id or None, "verification": verification})
    ctx["audit"].write(action, {"dry_run": False, "ad_account_id": ad_account_id or None, "catalog_id": created_id})
    ctx["out"].emit(out)
    return 0


def cmd_catalogs_feeds_create(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(getattr(args, "ad_account_id", "") or "").strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    body = _load_json_object_file(args.body_file)
    params: dict[str, Any] = {"ad_account_id": ad_account_id}
    action = "catalogs.feeds.create"
    request = write_operation(method="POST", path="/catalogs/feeds", params=params, json_body=body)
    ops = [request]
    if not bool(ctx.get("apply")):
        out = build_plan(action=action, operations=ops, request=request)
        out.update({"resource": "feeds", "operation": "create", "ad_account_id": ad_account_id})
        ctx["audit"].write(action, {"dry_run": True, "ad_account_id": ad_account_id})
        ctx["out"].emit(out)
        return 0

    require_write_allowed(ctx)

    created = api.post("/catalogs/feeds", json_body=body, params=params)
    if not isinstance(created, dict):
        raise RuntimeError("Unexpected feed create response (not an object)")
    feed_id = str(created.get("id") or "").strip()
    if not feed_id:
        raise RuntimeError("Feed create response missing id; refusing to proceed without verification target")

    after = api.get(f"/catalogs/feeds/{feed_id}", params=params)
    if not isinstance(after, dict):
        raise RuntimeError("Unexpected feed read-back response (not an object)")
    if str(after.get("id") or "").strip() != feed_id:
        raise RuntimeError(f"Verification failed: expected feed id {feed_id}, got {after.get('id')!r}")

    verification = {"read_back": True, "verified_ids": [feed_id]}
    out = build_receipt(
        action=action,
        changed=True,
        operations=ops,
        request=request,
        before=None,
        write_result=created,
        after=after,
    )
    out.update({"resource": "feeds", "operation": "create", "ad_account_id": ad_account_id, "verification": verification})
    ctx["audit"].write(action, {"dry_run": False, "ad_account_id": ad_account_id, "feed_id": feed_id})
    ctx["out"].emit(out)
    return 0


def cmd_catalogs_feeds_update(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(getattr(args, "ad_account_id", "") or "").strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    feed_id = str(getattr(args, "id", "") or "").strip()
    if not feed_id:
        raise RuntimeError("--id is required")
    body = _load_json_object_file(args.body_file)
    params: dict[str, Any] = {"ad_account_id": ad_account_id}
    path = f"/catalogs/feeds/{feed_id}"
    action = "catalogs.feeds.update"
    request = write_operation(method="PATCH", path=path, params=params, json_body=body)
    ops = [request]
    if not bool(ctx.get("apply")):
        out = build_plan(action=action, operations=ops, request=request)
        out.update({"resource": "feeds", "operation": "update", "ad_account_id": ad_account_id, "feed_id": feed_id})
        ctx["audit"].write(action, {"dry_run": True, "ad_account_id": ad_account_id, "feed_id": feed_id})
        ctx["out"].emit(out)
        return 0

    require_write_allowed(ctx)

    before = api.get(path, params=params)
    updated = api.patch(path, json_body=body, params=params)
    after = api.get(path, params=params)
    if not isinstance(after, dict):
        raise RuntimeError("Unexpected feed read-back response (not an object)")
    if str(after.get("id") or "").strip() != feed_id:
        raise RuntimeError(f"Verification failed: expected feed id {feed_id}, got {after.get('id')!r}")

    verification = {"read_back": True, "verified_ids": [feed_id]}
    out = build_receipt(
        action=action,
        changed=True,
        operations=ops,
        request=request,
        before=before,
        write_result=updated,
        after=after,
    )
    out.update({"resource": "feeds", "operation": "update", "ad_account_id": ad_account_id, "feed_id": feed_id, "verification": verification})
    ctx["audit"].write(action, {"dry_run": False, "ad_account_id": ad_account_id, "feed_id": feed_id})
    ctx["out"].emit(out)
    return 0


def cmd_catalogs_feeds_ingest(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    ad_account_id = str(getattr(args, "ad_account_id", "") or "").strip()
    if not ad_account_id:
        raise RuntimeError("--ad-account-id is required")
    feed_id = str(getattr(args, "id", "") or "").strip()
    if not feed_id:
        raise RuntimeError("--id is required")
    params: dict[str, Any] = {"ad_account_id": ad_account_id}
    path = f"/catalogs/feeds/{feed_id}/ingest"
    action = "catalogs.feeds.ingest"
    acks_required = ["ack-volume"]
    request = write_operation(method="POST", path=path, params=params, json_body=None)
    ops = [request]
    if not bool(ctx.get("apply")):
        out = build_plan(action=action, operations=ops, acks_required=acks_required, request=request)
        out.update({"resource": "feeds", "operation": "ingest", "ad_account_id": ad_account_id, "feed_id": feed_id})
        ctx["audit"].write(action, {"dry_run": True, "ad_account_id": ad_account_id, "feed_id": feed_id})
        ctx["out"].emit(out)
        return 0

    require_write_allowed(ctx, acks_required=acks_required)

    started = api.post(path, json_body=None, params=params)
    # Read-back verification: confirm feed still exists and matches id (ingest is async, not awaited).
    after = api.get(f"/catalogs/feeds/{feed_id}", params=params)
    if not isinstance(after, dict):
        raise RuntimeError("Unexpected feed read-back response (not an object)")
    if str(after.get("id") or "").strip() != feed_id:
        raise RuntimeError(f"Verification failed: expected feed id {feed_id}, got {after.get('id')!r}")

    verification = {
        "read_back": True,
        "verified_ids": [feed_id],
        "note": "Feed ingest is asynchronous; verified by read-back that the feed exists and id matches.",
    }
    out = build_receipt(
        action=action,
        changed=True,
        operations=ops,
        acks_required=acks_required,
        request=request,
        before=None,
        write_result=started,
        after=after,
    )
    out.update({"resource": "feeds", "operation": "ingest", "ad_account_id": ad_account_id, "feed_id": feed_id, "verification": verification})
    ctx["audit"].write(action, {"dry_run": False, "ad_account_id": ad_account_id, "feed_id": feed_id})
    ctx["out"].emit(out)
    return 0
