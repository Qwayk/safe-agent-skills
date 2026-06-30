from __future__ import annotations

from typing import Any

from . import community_groups as _groups


COMMAND_FAMILY = "automation-storage-items"
BASE_PATH = "/storage-service/v1/storage-items"


def _object(raw: Any, *, field: str, allow_empty: bool = False) -> dict[str, Any]:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _text(raw: Any, *, field: str) -> str:
    return _groups._coerce_text(raw, field=field)


def _bool(raw: Any) -> bool | None:
    if raw is None:
        return None
    if isinstance(raw, bool):
        return raw
    value = str(raw).strip().lower()
    if value in {"1", "true", "yes"}:
        return True
    if value in {"0", "false", "no"}:
        return False
    raise _groups.ValidationError("--consistent-read must be true or false")


def _create_body(raw: Any) -> dict[str, Any]:
    body = _object(raw, field="storage-item-json")
    item = body.get("storageItem")
    if not isinstance(item, dict):
        raise _groups.ValidationError("--storage-item-json must include storageItem")
    for field in ("key", "displayName", "type"):
        if not isinstance(item.get(field), str) or not item[field].strip():
            raise _groups.ValidationError(f"--storage-item-json storageItem.{field} is required")
    return body


def _query_body(raw: Any) -> dict[str, Any]:
    return _object(raw, field="query-json", allow_empty=True)


def _tag_body(raw: Any, *, require_ids: bool, require_filter: bool) -> dict[str, Any]:
    body = _object(raw, field="tags-json")
    if require_ids:
        ids = body.get("storageItemIds")
        if not isinstance(ids, list) or not ids:
            raise _groups.ValidationError("--tags-json must include non-empty storageItemIds")
        if len(ids) > 100:
            raise _groups.ValidationError("--tags-json storageItemIds cannot include more than 100 IDs")
    if require_filter and "filter" not in body:
        raise _groups.ValidationError("--tags-json must include filter")
    if "assignTags" not in body and "unassignTags" not in body:
        raise _groups.ValidationError("--tags-json must include assignTags or unassignTags")
    return body


def _counter_body(raw: Any) -> dict[str, Any]:
    value = _text(raw, field="value")
    return {"value": value}


def _value_body(raw: Any) -> dict[str, Any]:
    body = _object(raw, field="value-json")
    choices = [key for key in ("stringValue", "booleanValue", "numberValue") if key in body]
    if len(choices) != 1:
        raise _groups.ValidationError("--value-json must include exactly one of stringValue, booleanValue, or numberValue")
    return body


def cmd_automation_storage_items_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _create_body(getattr(args, "storage_item_json", None))
        item = body["storageItem"]
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"key": item.get("key")},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-automation-storage-item-create"],
            verification_notes="Use automation-storage-items get with the storage item key and --consistent-read true.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_automation_storage_items_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        key = _text(getattr(args, "key", None), field="key")
        consistent_read = _bool(getattr(args, "consistent_read", None))
        params = {"consistentRead": consistent_read} if consistent_read is not None else None
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/{key}",
            params=params,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_automation_storage_items_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        body = _query_body(getattr(args, "query_json", None))
        return _groups._run_read(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/query",
            params=None,
            body=body,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_automation_storage_items_bulk_update_tags(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update-tags"
    try:
        body = _tag_body(getattr(args, "tags_json", None), require_ids=True, require_filter=False)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path="/storage-service/v1/bulk/storage-items/update-tags",
            body=body,
            selector={"storageItemIds": body["storageItemIds"]},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-automation-storage-item-tags"],
            verification_notes="Inspect provider result metadata, then query or get affected storage items.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_automation_storage_items_bulk_update_tags_by_filter(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update-tags-by-filter"
    try:
        body = _tag_body(getattr(args, "tags_json", None), require_ids=False, require_filter=True)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path="/storage-service/v1/bulk/storage-items/update-tags-by-filter",
            body=body,
            selector={"filter": body["filter"]},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["wix-automation-storage-item-tags-by-filter", "empty-filter-can-update-all-storage-items"],
            verification_notes="Inspect the returned jobId, then query matching storage items after the job completes.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_automation_storage_items_update_counter_by(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update-counter-by"
    try:
        key = _text(getattr(args, "key", None), field="key")
        body = _counter_body(getattr(args, "value", None))
        return _groups._run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{key}/update-counter-by",
            body=body,
            selector={"key": key, "value": body["value"]},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-automation-storage-counter-update"],
            verification_notes="Use automation-storage-items get with the same key and --consistent-read true.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_automation_storage_items_update_value(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update-value"
    try:
        key = _text(getattr(args, "key", None), field="key")
        body = _value_body(getattr(args, "value_json", None))
        return _groups._run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{BASE_PATH}/{key}/update-value",
            body=body,
            selector={"key": key},
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["wix-automation-storage-value-update"],
            verification_notes="Use automation-storage-items get with the same key and --consistent-read true.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
