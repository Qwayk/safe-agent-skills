from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested
from ..oauth_tokens import create_access_token, read_access_token_from_file, token_path_for_env_file


def _read_json_arg(raw: Any, field: str) -> Any:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a JSON string, JSON file path, or omitted")

    text = raw.strip()
    if not text:
        raise ValidationError(f"--{field} cannot be empty")

    if text.startswith("@"):
        path = Path(text[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        text = path.read_text(encoding="utf-8").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc


def _read_str_list(raw: Any, field: str) -> list[str] | None:
    if raw is None:
        return None
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON array")
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(f"--{field}[{i}] must be a string")
    return value


def _read_data_items(raw: Any, field: str) -> list[dict[str, Any]]:
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON array")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    if len(value) > 1000:
        raise ValidationError(f"--{field} can contain at most 1000 items")

    data_items: list[dict[str, Any]] = []
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValidationError(f"--{field}[{i}] must be a JSON object")
        data_items.append(item)
    return data_items


def _read_data_item_ids(raw: Any, field: str) -> list[str]:
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON array")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    if len(value) > 1000:
        raise ValidationError(f"--{field} can contain at most 1000 item IDs")

    item_ids: list[str] = []
    seen: set[str] = set()
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(f"--{field}[{i}] must be a string")
        item_id = item.strip()
        if not item_id:
            raise ValidationError(f"--{field}[{i}] cannot be empty")
        if item_id in seen:
            raise ValidationError(f"--{field} contains duplicate item ID: {item_id}")
        seen.add(item_id)
        item_ids.append(item_id)
    return item_ids


def _read_data_item_patches(raw: Any, field: str) -> list[dict[str, Any]]:
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON array")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    if len(value) > 100:
        raise ValidationError(f"--{field} can contain at most 100 items")

    patches: list[dict[str, Any]] = []
    seen_data_item_ids: set[str] = set()
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValidationError(f"--{field}[{i}] must be a JSON object")

        patch = dict(item)
        raw_data_item_id = patch.get("dataItemId")
        if raw_data_item_id is None:
            raise ValidationError(f"--{field}[{i}].dataItemId is required")

        data_item_id = str(raw_data_item_id).strip()
        if not data_item_id:
            raise ValidationError(f"--{field}[{i}].dataItemId cannot be empty")
        if data_item_id in seen_data_item_ids:
            raise ValidationError(f"--{field} contains duplicate dataItemId: {data_item_id}")
        seen_data_item_ids.add(data_item_id)

        field_modifications = patch.get("fieldModifications")
        if not isinstance(field_modifications, list):
            raise ValidationError(f"--{field}[{i}].fieldModifications must be a non-empty JSON array")
        if not field_modifications:
            raise ValidationError(f"--{field}[{i}].fieldModifications cannot be empty")

        patch["dataItemId"] = data_item_id
        patches.append(patch)
    return patches


def _normalize_sort(sort_value: Any, field: str) -> list[dict[str, Any]] | dict[str, Any] | None:
    if sort_value is None:
        return None
    if isinstance(sort_value, list):
        for i, item in enumerate(sort_value):
            if not isinstance(item, dict):
                raise ValidationError(f"Each item in --{field} must be an object")
            if not item:
                raise ValidationError(f"Item {i} in --{field} cannot be empty")
        return sort_value
    if isinstance(sort_value, dict):
        if not sort_value:
            raise ValidationError(f"--{field} cannot be empty")
        return sort_value
    raise ValidationError(f"--{field} must be an object or list of objects")


def _read_include_references(raw: Any, field: str) -> list[dict[str, Any]] | None:
    if raw is None:
        return None
    value = _read_json_arg(raw, field=field)
    if isinstance(value, dict):
        refs = [value]
    elif isinstance(value, list):
        refs = value
    else:
        raise ValidationError(f"--{field} must be a JSON object or array")

    for i, item in enumerate(refs):
        if not isinstance(item, dict):
            raise ValidationError(f"--{field}[{i}] must be an object")
        if not item:
            raise ValidationError(f"--{field}[{i}] cannot be empty")
    return refs


def _ensure_query_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {"query": {}}
    if not isinstance(payload, dict):
        raise ValidationError("--query-json must be an object")
    if isinstance(payload.get("query"), dict):
        return dict(payload)
    return {"query": payload}


def _coerce_cursor_paging(*, cursor: str | None, limit: int | None) -> dict[str, Any]:
    cursor_paging: dict[str, Any] = {}
    if cursor is not None:
        cursor_paging["cursor"] = cursor
    if limit is not None:
        cursor_paging["limit"] = int(limit)
    return cursor_paging


def _coerce_paging(*, limit: int | None, offset: int | None) -> dict[str, Any]:
    paging: dict[str, Any] = {}
    if limit is not None:
        paging["limit"] = int(limit)
    if offset is not None:
        paging["offset"] = int(offset)
    return paging


def _resolve_access_token(*, cfg, env_file: str, verbose: bool) -> str:
    token = getattr(cfg, "access_token", None)
    if token:
        return str(token).strip()

    token_file = token_path_for_env_file(env_file)
    token = read_access_token_from_file(token_file)
    if token:
        return token

    if not bool(getattr(cfg, "has_official_app_auth", False)):
        raise ValidationError(
            "Missing official Wix credentials and no access token source. Add WIX_ACCESS_TOKEN or app credentials."
        )

    token_response = create_access_token(
        base_url=cfg.base_url,
        app_id=cfg.app_id,
        app_secret=cfg.app_secret,
        instance_id=cfg.instance_id,
        timeout_s=cfg.timeout_s,
        verbose=verbose,
    )
    access_token = token_response.get("access_token") if isinstance(token_response, dict) else None
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValidationError("OAuth token response did not include access_token")
    return access_token.strip()


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    token: str,
    params: dict[str, Any] | None,
    json_body: dict[str, Any] | None,
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    headers = {"Authorization": token}
    if method.upper() != "GET":
        headers["Content-Type"] = "application/json"

    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=headers,
        params=params,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _http_status_from_error(exc: RuntimeError) -> int | None:
    msg = str(exc)
    parts = msg.split()
    if len(parts) < 2 or parts[0] != "HTTP":
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _read_json_object(raw: Any, *, field: str) -> dict[str, Any]:
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    return value


def _read_optional_json_object(raw: Any, *, field: str) -> dict[str, Any] | None:
    if raw is None:
        return None
    return _read_json_object(raw, field=field)


def _ensure_matching_item_id(
    *,
    payload: dict[str, Any],
    key: str,
    expected_id: str,
    field: str,
) -> dict[str, Any]:
    value = payload.get(key)
    if value is None:
        updated = dict(payload)
        updated[key] = expected_id
        return updated
    actual_id = str(value).strip()
    if not actual_id:
        raise ValidationError(f"--{field} {key} cannot be empty")
    if actual_id != expected_id:
        raise ValidationError(f"--{field} {key} must match --data-item-id")
    return payload


def _build_data_item_selector(
    *,
    operation: str,
    data_collection_id: str,
    data_item_id: str | None = None,
) -> dict[str, Any]:
    selector: dict[str, Any] = {
        "kind": "wix-data-item",
        "operation": operation,
        "data_collection_id": data_collection_id,
    }
    if data_item_id:
        selector["data_item_id"] = data_item_id
    return selector


def _build_bulk_data_items_selector(
    *,
    operation: str,
    data_collection_id: str,
    data_item_ids: list[str] | None,
) -> dict[str, Any]:
    selector: dict[str, Any] = {
        "kind": "wix-data-item-bulk",
        "operation": operation,
        "data_collection_id": data_collection_id,
    }
    if data_item_ids:
        selector["explicit_item_ids"] = data_item_ids
    return selector


def _build_data_items_bulk_insert_payload(
    *,
    data_collection_id: str,
    data_items: list[dict[str, Any]],
    app_options: dict[str, Any] | None,
    return_entity: bool,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "dataCollectionId": data_collection_id,
        "dataItems": data_items,
    }
    if app_options is not None:
        body["appOptions"] = app_options
    if return_entity:
        body["returnEntity"] = True
    return body


def _build_data_items_bulk_patch_payload(
    *,
    data_collection_id: str,
    patches: list[dict[str, Any]],
    condition: dict[str, Any] | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "dataCollectionId": data_collection_id,
        "patches": patches,
    }
    if condition is not None:
        body["condition"] = condition
    return body


def _build_data_items_save_payload(
    *,
    data_collection_id: str,
    data_item: dict[str, Any],
    app_options: dict[str, Any] | None,
    include_draft_items: bool,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "dataCollectionId": data_collection_id,
        "dataItem": data_item,
    }
    if app_options is not None:
        body["appOptions"] = app_options
    if include_draft_items:
        body["publishPluginOptions"] = {"includeDraftItems": True}
    return body


def _build_data_items_bulk_remove_payload(
    *,
    data_collection_id: str,
    data_item_ids: list[str],
    condition: dict[str, Any] | None,
    app_options: dict[str, Any] | None,
    include_draft_items: bool,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "dataCollectionId": data_collection_id,
        "dataItemIds": data_item_ids,
    }
    if condition is not None:
        body["condition"] = condition
    if app_options is not None:
        body["appOptions"] = app_options
    if include_draft_items:
        body["publishPluginOptions"] = {"includeDraftItems": True}
    return body


def _build_data_items_bulk_save_payload(
    *,
    data_collection_id: str,
    data_items: list[dict[str, Any]],
    app_options: dict[str, Any] | None,
    include_draft_items: bool,
    return_entity: bool,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "dataCollectionId": data_collection_id,
        "dataItems": data_items,
    }
    if app_options is not None:
        body["appOptions"] = app_options
    if include_draft_items:
        body["publishPluginOptions"] = {"includeDraftItems": True}
    if return_entity:
        body["returnEntity"] = True
    return body


def _build_data_items_bulk_update_payload(
    *,
    data_collection_id: str,
    data_items: list[dict[str, Any]],
    condition: dict[str, Any] | None,
    app_options: dict[str, Any] | None,
    include_draft_items: bool,
    return_entity: bool,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "dataCollectionId": data_collection_id,
        "dataItems": data_items,
    }
    if condition is not None:
        body["condition"] = condition
    if app_options is not None:
        body["appOptions"] = app_options
    if include_draft_items:
        body["publishPluginOptions"] = {"includeDraftItems": True}
    if return_entity:
        body["returnEntity"] = True
    return body


def _normalize_bulk_item_ids(data_items: list[dict[str, Any]]) -> tuple[list[str], bool, list[dict[str, Any]]]:
    explicit_ids: list[str] = []
    seen: set[str] = set()
    has_missing_ids = False
    normalized_items: list[dict[str, Any]] = []

    for i, item in enumerate(data_items):
        if not isinstance(item, dict):
            raise ValidationError(f"--data-items-json[{i}] must be a JSON object")

        item_copy = dict(item)
        raw_id = item_copy.get("id")
        if raw_id is None:
            has_missing_ids = True
            normalized_items.append(item_copy)
            continue

        data_item_id = str(raw_id).strip()
        if not data_item_id:
            raise ValidationError(f"--data-items-json[{i}].id cannot be empty")
        if data_item_id in seen:
            raise ValidationError(f"--data-items-json contains duplicate explicit item id: {data_item_id}")
        seen.add(data_item_id)
        explicit_ids.append(data_item_id)
        item_copy["id"] = data_item_id
        normalized_items.append(item_copy)

    return explicit_ids, has_missing_ids, normalized_items


def _read_data_item_ids(raw: Any, field: str) -> list[str]:
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON array")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    if len(value) > 1000:
        raise ValidationError(f"--{field} can contain at most 1000 items")

    data_item_ids: list[str] = []
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(f"--{field}[{i}] must be a string")
        data_item_id = item.strip()
        if not data_item_id:
            raise ValidationError(f"--{field}[{i}] cannot be empty")
        data_item_ids.append(data_item_id)
    return data_item_ids


def _read_data_item_references(raw: Any, field: str) -> list[dict[str, Any]]:
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON array")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    if len(value) > 1000:
        raise ValidationError(f"--{field} can contain at most 1000 items")

    references: list[dict[str, Any]] = []
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValidationError(f"--{field}[{i}] must be a JSON object")
        ref = dict(item)
        for key in ("referringItemFieldName", "referringItemId", "referencedItemId"):
            raw_value = ref.get(key)
            if raw_value is None:
                raise ValidationError(f"--{field}[{i}].{key} is required")
            value_text = str(raw_value).strip()
            if not value_text:
                raise ValidationError(f"--{field}[{i}].{key} cannot be empty")
            ref[key] = value_text
        references.append(ref)
    return references


def _build_data_items_save_payload(
    *,
    data_collection_id: str,
    data_item: dict[str, Any],
    app_options: dict[str, Any] | None,
    include_draft_items: bool,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "dataCollectionId": data_collection_id,
        "dataItem": data_item,
    }
    if app_options is not None:
        body["appOptions"] = app_options
    if include_draft_items:
        body["publishPluginOptions"] = {"includeDraftItems": True}
    return body


def _build_data_items_truncate_payload(*, data_collection_id: str) -> dict[str, Any]:
    return {"dataCollectionId": data_collection_id}


def _build_data_items_bulk_remove_payload(
    *,
    data_collection_id: str,
    data_item_ids: list[str],
    condition: dict[str, Any] | None,
    app_options: dict[str, Any] | None,
    include_draft_items: bool,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "dataCollectionId": data_collection_id,
        "dataItemIds": data_item_ids,
    }
    if condition is not None:
        body["condition"] = condition
    if app_options is not None:
        body["appOptions"] = app_options
    if include_draft_items:
        body["publishPluginOptions"] = {"includeDraftItems": True}
    return body


def _build_data_items_bulk_save_payload(
    *,
    data_collection_id: str,
    data_items: list[dict[str, Any]],
    app_options: dict[str, Any] | None,
    include_draft_items: bool,
    return_entity: bool,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "dataCollectionId": data_collection_id,
        "dataItems": data_items,
    }
    if app_options is not None:
        body["appOptions"] = app_options
    if include_draft_items:
        body["publishPluginOptions"] = {"includeDraftItems": True}
    if return_entity:
        body["returnEntity"] = True
    return body


def _build_data_items_bulk_update_payload(
    *,
    data_collection_id: str,
    data_items: list[dict[str, Any]],
    condition: dict[str, Any] | None,
    app_options: dict[str, Any] | None,
    include_draft_items: bool,
    return_entity: bool,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "dataCollectionId": data_collection_id,
        "dataItems": data_items,
    }
    if condition is not None:
        body["condition"] = condition
    if app_options is not None:
        body["appOptions"] = app_options
    if include_draft_items:
        body["publishPluginOptions"] = {"includeDraftItems": True}
    if return_entity:
        body["returnEntity"] = True
    return body


def _build_data_items_bulk_references_payload(
    *,
    data_collection_id: str,
    data_item_references: list[dict[str, Any]],
    return_entity: bool,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "dataCollectionId": data_collection_id,
        "dataItemReferences": data_item_references,
    }
    if return_entity:
        body["returnEntity"] = True
    return body


def _build_bulk_data_item_reference_selector(
    *,
    operation: str,
    data_collection_id: str,
    data_item_references: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "kind": "wix-data-item-reference-bulk",
        "operation": operation,
        "data_collection_id": data_collection_id,
        "data_item_references": data_item_references,
    }


def _coerce_optional_int(raw: Any) -> int | None:
    if isinstance(raw, bool) or raw is None:
        return None
    if isinstance(raw, int):
        return raw if raw >= 0 else None
    if isinstance(raw, str) and raw.strip().isdigit():
        return int(raw.strip())
    return None


def _extract_bulk_data_item_ids(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return []
    value: Any = payload.get("results")
    if not isinstance(value, list):
        value = payload.get("dataItems")
    if not isinstance(value, list):
        value = payload.get("items")
    if not isinstance(value, list):
        return []
    item_ids: list[str] = []
    for item in value:
        parsed_id = _extract_data_item_id(item)
        if parsed_id:
            item_ids.append(parsed_id)
    return item_ids


def _extract_count_total(payload: Any) -> int | None:
    if not isinstance(payload, dict):
        return None
    for key in ("totalCount", "count", "total"):
        value = payload.get(key)
        if isinstance(value, int) and value >= 0:
            return value
        if isinstance(value, str) and value.strip().isdigit():
            return int(value.strip())
    paging_metadata = payload.get("pagingMetadata")
    if isinstance(paging_metadata, dict):
        for key in ("count", "totalCount"):
            value = paging_metadata.get(key)
            if isinstance(value, int) and value >= 0:
                return value
            if isinstance(value, str) and value.strip().isdigit():
                return int(value.strip())
    return None


def _read_data_items_count(*, data_collection_id: str, token: str, ctx: dict[str, Any]) -> int:
    payload = _request_json(
        method="POST",
        base_url=ctx["cfg"].base_url,
        path="/wix-data/v2/items/count",
        token=token,
        params=None,
        json_body={"dataCollectionId": data_collection_id},
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    count_value = _extract_count_total(payload)
    if count_value is None:
        raise ValidationError("Unexpected count response from Wix API")
    return count_value


def _result_is_failure(result: dict[str, Any]) -> bool:
    if result.get("error") is not None:
        return True
    item_metadata = result.get("itemMetadata")
    if isinstance(item_metadata, dict) and item_metadata.get("error") is not None:
        return True
    status = result.get("status")
    if not isinstance(status, str):
        return False
    normalized_status = status.strip().lower()
    if normalized_status in {"error", "failed", "failure", "conflict", "skipped"}:
        return True
    if normalized_status in {"success", "succeeded", "inserted", "created", "ok"}:
        return False
    return False


def _build_bulk_insert_verification(
    *,
    response: dict[str, Any],
    explicit_item_ids: list[str],
    return_entity: bool,
    data_collection_id: str,
    token: str,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    metadata = response.get("bulkActionMetadata")
    bulk_ok = True
    failures: list[dict[str, Any]] = []

    if isinstance(metadata, dict):
        failure_count = _coerce_optional_int(metadata.get("failureCount"))
        if failure_count is None:
            failure_count = _coerce_optional_int(metadata.get("totalFailures"))
        if failure_count is None:
            failure_count = _coerce_optional_int(metadata.get("failures"))
        if failure_count is not None and failure_count > 0:
            bulk_ok = False

    results = response.get("results")
    if isinstance(results, list):
        for item in results:
            if not isinstance(item, dict):
                continue
            if _result_is_failure(item):
                bulk_ok = False
                failures.append(item)

    verification: dict[str, Any] = {
        "ok": bulk_ok,
        "type": "bulk-write",
        "path": "/wix-data/v2/bulk/items/insert",
        "method": "POST",
        "provider_response": response,
    }
    if metadata is not None:
        verification["bulkActionMetadata"] = metadata

    if failures:
        verification["failure_examples"] = failures[:10]

    if not return_entity and explicit_item_ids:
        read_back: list[dict[str, Any]] = []
        read_back_ok = True
        for item_id in explicit_item_ids:
            try:
                read_back_payload = _ensure_requesting_data_item_snapshot(
                    data_collection_id=data_collection_id,
                    data_item_id=item_id,
                    language=None,
                    token=token,
                    ctx=ctx,
                )
                read_back.append({"id": item_id, "response": read_back_payload})
            except RuntimeError as exc:
                read_back_ok = False
                read_back.append({"id": item_id, "error": str(exc)})

        verification["read_back"] = {
            "requested_ids": explicit_item_ids,
            "checks": read_back,
        }
        verification["ok"] = bool(verification.get("ok") and read_back_ok)

    return verification


def _build_bulk_patch_verification(
    *,
    response: dict[str, Any],
    patched_item_ids: list[str],
    data_collection_id: str,
    token: str,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    metadata = response.get("bulkActionMetadata")
    bulk_ok = True
    failures: list[dict[str, Any]] = []

    if isinstance(metadata, dict):
        total_failures = _coerce_optional_int(metadata.get("totalFailures"))
        if total_failures is None:
            total_failures = _coerce_optional_int(metadata.get("failureCount"))
        if total_failures is None:
            total_failures = _coerce_optional_int(metadata.get("failures"))
        if total_failures is not None and total_failures > 0:
            bulk_ok = False

    results = response.get("results")
    if isinstance(results, list):
        for item in results:
            if not isinstance(item, dict):
                continue
            if _result_is_failure(item):
                bulk_ok = False
                failures.append(item)

    verification: dict[str, Any] = {
        "ok": bulk_ok,
        "type": "bulk-write",
        "path": "/wix-data/v2/bulk/items/patch",
        "method": "POST",
        "provider_response": response,
    }
    if metadata is not None:
        verification["bulkActionMetadata"] = metadata
    if failures:
        verification["failure_examples"] = failures[:10]

    read_back: list[dict[str, Any]] = []
    read_back_ok = True
    for item_id in patched_item_ids:
        try:
            read_back_payload = _ensure_requesting_data_item_snapshot(
                data_collection_id=data_collection_id,
                data_item_id=item_id,
                language=None,
                token=token,
                ctx=ctx,
            )
            read_back.append({"id": item_id, "response": read_back_payload})
        except RuntimeError as exc:
            read_back_ok = False
            read_back.append({"id": item_id, "error": str(exc)})

    verification["read_back"] = {
        "requested_ids": patched_item_ids,
        "checks": read_back,
    }
    verification["ok"] = bool(verification.get("ok") and read_back_ok)
    return verification


def _find_existing_bulk_insert_ids(
    *,
    data_collection_id: str,
    explicit_item_ids: list[str],
    token: str,
    ctx: dict[str, Any],
) -> list[str]:
    existing_ids: list[str] = []
    for item_id in explicit_item_ids:
        payload, status = _safe_get_data_item_for_verification(
            data_collection_id=data_collection_id,
            data_item_id=item_id,
            language=None,
            token=token,
            ctx=ctx,
            allow_not_found=True,
        )
        if status == 404:
            continue
        if isinstance(payload, dict):
            existing_ids.append(item_id)
    return existing_ids


def _build_data_items_write_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    baseline_before: dict[str, Any] | None = None,
    proposed_changes: list[dict[str, Any]] | None = None,
    verification_plan: dict[str, Any] | None = None,
    rollback_notes: str | None = None,
) -> dict[str, Any]:
    baseline: dict[str, Any] = {
        "env_fingerprint": ctx["cfg"].base_url,
        "selector": selector,
    }
    if baseline_before is not None:
        baseline["before_state"] = baseline_before

    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": ["cms-data-item-write"],
        "preconditions": ["env_fingerprint must match", "selector must match"],
        "selector": selector,
        "request": request,
        "baseline": baseline,
        "proposed_changes": proposed_changes or [],
        "verification_plan": verification_plan or {"type": "read-after-write", "notes": "Verify by GET with consistentRead=true"},
        "rollback": {"supported": False, "notes": rollback_notes or "No rollback available."},
    }


def _ensure_requesting_data_item_snapshot(
    *,
    data_collection_id: str,
    data_item_id: str,
    language: str | None,
    token: str,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    params = _build_get_params(
        data_collection_id=data_collection_id,
        fields=None,
        include_references=None,
        consistent_read=True,
        language=language,
    )
    return _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/wix-data/v2/items/{data_item_id}",
        token=token,
        params=params,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )


def _safe_get_data_item_for_verification(
    *,
    data_collection_id: str,
    data_item_id: str,
    language: str | None,
    token: str,
    ctx: dict[str, Any],
    allow_not_found: bool,
) -> tuple[dict[str, Any] | None, int | None]:
    try:
        payload = _ensure_requesting_data_item_snapshot(
            data_collection_id=data_collection_id,
            data_item_id=data_item_id,
            language=language,
            token=token,
            ctx=ctx,
        )
        return payload, None
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if allow_not_found and status == 404:
            return None, 404
        raise


def _read_current_data_item_state(
    *,
    data_collection_id: str,
    data_item_id: str,
    language: str | None,
    token: str,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    payload, status = _safe_get_data_item_for_verification(
        data_collection_id=data_collection_id,
        data_item_id=data_item_id,
        language=language,
        token=token,
        ctx=ctx,
        allow_not_found=True,
    )
    if status == 404:
        return {"missing": True}
    if not isinstance(payload, dict):
        raise ValidationError("Unexpected data item response from Wix API")
    return payload


def _capture_data_item_states(
    *,
    data_collection_id: str,
    data_item_ids: list[str],
    language: str | None,
    token: str,
    ctx: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    states: dict[str, dict[str, Any]] = {}
    for data_item_id in data_item_ids:
        states[data_item_id] = _read_current_data_item_state(
            data_collection_id=data_collection_id,
            data_item_id=data_item_id,
            language=language,
            token=token,
            ctx=ctx,
        )
    return states


def _assert_no_data_item_state_drifts(
    *,
    plan: dict[str, Any],
    token: str,
    ctx: dict[str, Any],
    data_collection_id: str,
    data_item_ids: list[str],
    language: str | None,
) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    baseline_state = baseline.get("before_state")
    if not isinstance(baseline_state, dict):
        raise SafetyError("Refused: plan missing before-state snapshot")
    for data_item_id in data_item_ids:
        expected_state = baseline_state.get(data_item_id)
        if expected_state is None:
            continue
        current_state = _read_current_data_item_state(
            data_collection_id=data_collection_id,
            data_item_id=data_item_id,
            language=language,
            token=token,
            ctx=ctx,
        )
        if current_state != expected_state:
            raise SafetyError(f"Refused: item {data_item_id} changed since plan was created")


def _extract_data_item_id(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    item = payload
    if isinstance(payload.get("dataItem"), dict):
        item = payload["dataItem"]
    elif isinstance(payload.get("item"), dict):
        item = payload["item"]
    elif isinstance(payload.get("dataItemId"), str):
        item_id = payload.get("dataItemId").strip()
        return item_id or None
    value = item.get("id") if isinstance(item, dict) else None
    return str(value) if isinstance(value, str) and value else None


def _load_plan(plan_in: str | None, *, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan.get("method") or "") != expected_method:
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan missing baseline")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    return plan


def _plan_out_if_needed(ctx: dict[str, Any], *, plan: dict[str, Any]) -> str | None:
    plan_out = ctx.get("plan_out")
    if plan_out and not bool(ctx.get("apply")):
        return write_json_file(plan_out, plan)
    return None


def _receipt_out_if_needed(ctx: dict[str, Any], *, receipt: dict[str, Any]) -> str | None:
    receipt_out = ctx.get("receipt_out")
    if receipt_out:
        return write_json_file(receipt_out, receipt)
    return None


def _should_apply(ctx: dict[str, Any], *, requires_ack: bool) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="data-items")


def _assert_no_item_drift(*, plan: dict[str, Any], token: str, ctx: dict[str, Any], data_collection_id: str, data_item_id: str, language: str | None) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    baseline_state = baseline.get("before_state")
    if not isinstance(baseline_state, dict):
        raise SafetyError("Refused: plan missing before-state snapshot")
    current_state = _ensure_requesting_data_item_snapshot(
        data_collection_id=data_collection_id,
        data_item_id=data_item_id,
        language=language,
        token=token,
        ctx=ctx,
    )
    if current_state != baseline_state:
        raise SafetyError("Refused: item changed since plan was created")


def _assert_no_bulk_item_drifts(
    *,
    plan: dict[str, Any],
    token: str,
    ctx: dict[str, Any],
    data_collection_id: str,
    data_item_ids: list[str],
    language: str | None,
) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    baseline_state = baseline.get("before_state")
    if not isinstance(baseline_state, dict):
        raise SafetyError("Refused: plan missing before-state snapshot")
    for data_item_id in data_item_ids:
        snapshot = baseline_state.get(data_item_id)
        if not isinstance(snapshot, dict):
            raise SafetyError(f"Refused: plan missing before-state snapshot for {data_item_id}")
        current_state = _ensure_requesting_data_item_snapshot(
            data_collection_id=data_collection_id,
            data_item_id=data_item_id,
            language=language,
            token=token,
            ctx=ctx,
        )
        if current_state != snapshot:
            raise SafetyError(f"Refused: item {data_item_id} changed since plan was created")


def _read_collection_item_count(
    *,
    data_collection_id: str,
    token: str,
    ctx: dict[str, Any],
) -> int | None:
    payload = _request_json(
        method="POST",
        base_url=ctx["cfg"].base_url,
        path="/wix-data/v2/items/count",
        token=token,
        params=None,
        json_body=_build_count_payload(
            query_json=None,
            filter_json=None,
            data_collection_id=data_collection_id,
            consistent_read=True,
            language=None,
        ),
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    total_count = payload.get("totalCount")
    if isinstance(total_count, int) and total_count >= 0:
        return total_count
    return None


def _assert_no_truncate_count_drift(
    *,
    plan: dict[str, Any],
    data_collection_id: str,
    token: str,
    ctx: dict[str, Any],
) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    before_state = baseline.get("before_state")
    if not isinstance(before_state, dict):
        raise SafetyError("Refused: plan missing before-state snapshot")
    expected_count = before_state.get("total_count")
    if not isinstance(expected_count, int):
        raise SafetyError("Refused: plan missing collection item count snapshot")
    current_count = _read_collection_item_count(
        data_collection_id=data_collection_id,
        token=token,
        ctx=ctx,
    )
    if current_count != expected_count:
        raise SafetyError("Refused: collection item count changed since plan was created")


def _assert_save_snapshot_matches(
    *,
    plan: dict[str, Any],
    data_collection_id: str,
    data_item_id: str,
    token: str,
    ctx: dict[str, Any],
) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    before_state = baseline.get("before_state")
    if not isinstance(before_state, dict):
        raise SafetyError("Refused: plan missing before-state snapshot")
    if before_state.get("missing") is True:
        _, status = _safe_get_data_item_for_verification(
            data_collection_id=data_collection_id,
            data_item_id=data_item_id,
            language=None,
            token=token,
            ctx=ctx,
            allow_not_found=True,
        )
        if status != 404:
            raise SafetyError("Refused: item now exists but it was missing when the plan was created")
        return
    _assert_no_item_drift(
        plan=plan,
        token=token,
        ctx=ctx,
        data_collection_id=data_collection_id,
        data_item_id=data_item_id,
        language=None,
    )


def _build_query_body(
    *,
    query_json: dict[str, Any] | None,
    filter_json: dict[str, Any] | None,
    sort_value: Any,
    fields: list[str] | None,
    include_references: list[dict[str, Any]] | None,
    include_field_groups: list[str] | None,
    return_total_count: bool | None,
    cursor: str | None,
    limit: int | None,
    offset: int | None,
    data_collection_id: str,
    consistent_read: bool,
    language: str | None,
) -> dict[str, Any]:
    payload = _ensure_query_payload(query_json)
    if not isinstance(payload.get("query"), dict):
        raise ValidationError("Query payload must include a query object")
    query_obj = payload["query"]

    if filter_json is not None and "filter" not in query_obj:
        query_obj["filter"] = filter_json
    if sort_value is not None and "sort" not in query_obj:
        query_obj["sort"] = sort_value

    if cursor is not None:
        if offset is not None:
            raise ValidationError("Do not use --offset when --cursor is set")
        if "cursorPaging" not in query_obj:
            query_obj["cursorPaging"] = _coerce_cursor_paging(cursor=cursor, limit=limit)
    else:
        if (limit is not None or offset is not None) and "paging" not in query_obj:
            paging = _coerce_paging(limit=limit, offset=offset)
            if paging:
                query_obj["paging"] = paging

    if fields is not None:
        query_obj["fields"] = fields
    if include_references is not None:
        query_obj["includeReferences"] = include_references
    if include_field_groups is not None:
        query_obj["includeFieldGroups"] = include_field_groups
    if return_total_count is not None:
        query_obj["returnTotalCount"] = bool(return_total_count)

    payload["dataCollectionId"] = data_collection_id
    if consistent_read:
        payload["consistentRead"] = True
    if language:
        payload["language"] = language

    return payload


def _build_get_params(
    *,
    data_collection_id: str,
    fields: list[str] | None,
    include_references: list[dict[str, Any]] | None,
    consistent_read: bool,
    language: str | None,
) -> dict[str, Any]:
    params = {"dataCollectionId": data_collection_id}
    if fields is not None:
        params["fields"] = fields
    if include_references is not None:
        params["includeReferences"] = include_references
    if consistent_read:
        params["consistentRead"] = True
    if language:
        params["language"] = language
    return params


def _build_count_payload(
    *,
    query_json: dict[str, Any] | None,
    filter_json: dict[str, Any] | None,
    data_collection_id: str,
    consistent_read: bool,
    language: str | None,
) -> dict[str, Any]:
    if query_json is None:
        payload: dict[str, Any] = {"dataCollectionId": data_collection_id}
        if filter_json is not None:
            payload["filter"] = filter_json
    else:
        payload = dict(query_json)

    payload["dataCollectionId"] = data_collection_id
    if filter_json is not None and "filter" not in payload:
        payload["filter"] = filter_json
    if consistent_read:
        payload["consistentRead"] = True
    if language:
        payload["language"] = language
    return payload


def _build_query_referenced_payload(
    *,
    data_collection_id: str,
    referring_item_field_name: str,
    referring_item_id: str,
    fields: list[str] | None,
    language: str | None,
    order: str | None,
    limit: int | None,
    offset: int | None,
    cursor: str | None,
    return_total_count: bool,
    consistent_read: bool,
    include_draft_items: bool,
    include_hidden_products: bool,
    include_variants: bool,
) -> dict[str, Any]:
    if cursor is not None and offset is not None:
        raise ValidationError("Do not use --offset when --cursor is set")

    body: dict[str, Any] = {
        "dataCollectionId": data_collection_id,
        "referringItemFieldName": referring_item_field_name,
        "referringItemId": referring_item_id,
    }

    if fields is not None:
        body["fields"] = fields
    if language:
        body["language"] = language
    if order:
        body["order"] = str(order)
    if cursor is not None:
        body["cursorPaging"] = _coerce_cursor_paging(cursor=cursor, limit=limit)
    else:
        paging = _coerce_paging(limit=limit, offset=offset)
        if paging:
            body["paging"] = paging
    if return_total_count:
        body["returnTotalCount"] = True
    if consistent_read:
        body["consistentRead"] = True

    if include_draft_items:
        body["publishPluginOptions"] = {"includeDraftItems": True}

    if include_hidden_products or include_variants:
        app_options: dict[str, bool] = {}
        if include_hidden_products:
            app_options["includeHiddenProducts"] = True
        if include_variants:
            app_options["includeVariants"] = True
        body["appOptions"] = app_options

    return body


def _build_is_referenced_payload(
    *,
    data_collection_id: str,
    referring_item_field_name: str,
    referring_item_id: str,
    referenced_item_id: str,
    consistent_read: bool,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "dataCollectionId": data_collection_id,
        "referringItemFieldName": referring_item_field_name,
        "referringItemId": referring_item_id,
        "referencedItemId": referenced_item_id,
    }
    if consistent_read:
        body["consistentRead"] = True
    return body


def _build_insert_reference_payload(
    *,
    data_collection_id: str,
    referring_item_field_name: str,
    referring_item_id: str,
    referenced_item_id: str,
) -> dict[str, Any]:
    return {
        "dataCollectionId": data_collection_id,
        "dataItemReference": {
            "referringItemFieldName": referring_item_field_name,
            "referringItemId": referring_item_id,
            "referencedItemId": referenced_item_id,
        },
    }


def _build_replace_references_payload(
    *,
    data_collection_id: str,
    referring_item_field_name: str,
    referring_item_id: str,
    new_referenced_item_ids: list[str],
) -> dict[str, Any]:
    return {
        "dataCollectionId": data_collection_id,
        "referringItemFieldName": referring_item_field_name,
        "referringItemId": referring_item_id,
        "newReferencedItemIds": new_referenced_item_ids,
    }


def _build_data_item_reference_selector(
    *,
    operation: str,
    data_collection_id: str,
    referring_item_field_name: str,
    referring_item_id: str,
    referenced_item_id: str | None = None,
    new_referenced_item_ids: list[str] | None = None,
) -> dict[str, Any]:
    selector: dict[str, Any] = {
        "kind": "wix-data-item-reference",
        "operation": operation,
        "data_collection_id": data_collection_id,
        "referring_item_field_name": referring_item_field_name,
        "referring_item_id": referring_item_id,
    }
    if referenced_item_id is not None:
        selector["referenced_item_id"] = referenced_item_id
    if new_referenced_item_ids is not None:
        selector["new_referenced_item_ids"] = new_referenced_item_ids
    return selector


def _normalize_reference_ids(raw_ids: list[str]) -> list[str]:
    normalized: list[str] = []
    for raw_id in raw_ids:
        item_id = str(raw_id).strip()
        if not item_id:
            raise ValidationError("--new-referenced-item-ids-json contains an empty reference id")
        normalized.append(item_id)
    return normalized


def _read_reference_exists(
    *,
    data_collection_id: str,
    referring_item_field_name: str,
    referring_item_id: str,
    referenced_item_id: str,
    consistent_read: bool,
    token: str,
    ctx: dict[str, Any],
) -> bool:
    payload = _request_json(
        method="POST",
        base_url=ctx["cfg"].base_url,
        path="/wix-data/v2/items/is-referenced",
        token=token,
        params=None,
        json_body=_build_is_referenced_payload(
            data_collection_id=data_collection_id,
            referring_item_field_name=referring_item_field_name,
            referring_item_id=referring_item_id,
            referenced_item_id=referenced_item_id,
            consistent_read=consistent_read,
        ),
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    value = payload.get("isReferenced")
    if not isinstance(value, bool):
        raise ValidationError("Unexpected is-referenced response from Wix API")
    return value


def _extract_referenced_item_id(item: Any) -> str | None:
    if not isinstance(item, dict):
        return None
    if isinstance(item.get("id"), str):
        item_id = item.get("id").strip()
        return item_id or None
    if isinstance(item.get("dataItemId"), str):
        item_id = item.get("dataItemId").strip()
        return item_id or None
    data_item = item.get("dataItem")
    if isinstance(data_item, dict) and isinstance(data_item.get("id"), str):
        item_id = data_item.get("id").strip()
        return item_id or None
    data_item_record = item.get("item")
    if isinstance(data_item_record, dict) and isinstance(data_item_record.get("id"), str):
        item_id = data_item_record.get("id").strip()
        return item_id or None
    return None


def _extract_referenced_item_ids(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return []
    value: Any = payload.get("results")
    if not isinstance(value, list):
        value = payload.get("dataItems")
    if not isinstance(value, list):
        value = payload.get("items")
    if not isinstance(value, list):
        return []
    item_ids: list[str] = []
    for item in value:
        parsed_id = _extract_referenced_item_id(item)
        if parsed_id:
            item_ids.append(parsed_id)
    return item_ids


def _read_referenced_item_ids(
    *,
    data_collection_id: str,
    referring_item_field_name: str,
    referring_item_id: str,
    consistent_read: bool,
    token: str,
    ctx: dict[str, Any],
) -> list[str]:
    item_ids: list[str] = []
    cursor: str | None = None
    seen_cursors: set[str] = set()
    while True:
        body = _build_query_referenced_payload(
            data_collection_id=data_collection_id,
            referring_item_field_name=referring_item_field_name,
            referring_item_id=referring_item_id,
            fields=["id"],
            language=None,
            order=None,
            limit=100,
            offset=None,
            cursor=cursor,
            return_total_count=False,
            consistent_read=consistent_read,
            include_draft_items=False,
            include_hidden_products=False,
            include_variants=False,
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/items/query-referenced",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        item_ids.extend(_extract_referenced_item_ids(response))

        paging_metadata = response.get("pagingMetadata") if isinstance(response, dict) else None
        next_cursor = None
        if isinstance(paging_metadata, dict):
            value = paging_metadata.get("cursor")
            if value is None:
                value = paging_metadata.get("nextCursor")
            if isinstance(value, str):
                next_cursor = value.strip() or None
            elif value is not None:
                next_cursor = str(value)
            if paging_metadata.get("hasMore") is False:
                next_cursor = None
        if not next_cursor:
            break
        if next_cursor in seen_cursors:
            break
        seen_cursors.add(next_cursor)
        cursor = next_cursor
    return item_ids


def _capture_reference_states(
    *,
    data_collection_id: str,
    data_item_references: list[dict[str, Any]],
    consistent_read: bool,
    token: str,
    ctx: dict[str, Any],
) -> list[bool]:
    states: list[bool] = []
    for ref in data_item_references:
        states.append(
            _read_reference_exists(
                data_collection_id=data_collection_id,
                referring_item_field_name=str(ref["referringItemFieldName"]),
                referring_item_id=str(ref["referringItemId"]),
                referenced_item_id=str(ref["referencedItemId"]),
                consistent_read=consistent_read,
                token=token,
                ctx=ctx,
            )
        )
    return states


def _assert_no_reference_state_drifts(
    *,
    plan: dict[str, Any],
    token: str,
    ctx: dict[str, Any],
    data_collection_id: str,
    data_item_references: list[dict[str, Any]],
    consistent_read: bool,
) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    baseline_state = baseline.get("before_state")
    if not isinstance(baseline_state, list):
        raise SafetyError("Refused: plan missing before-state snapshot")
    current_state = _capture_reference_states(
        data_collection_id=data_collection_id,
        data_item_references=data_item_references,
        consistent_read=consistent_read,
        token=token,
        ctx=ctx,
    )
    if current_state != baseline_state:
        raise SafetyError("Refused: references changed since plan was created")


def cmd_data_items_get(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")
        data_item_id = str(getattr(args, "data_item_id", "") or "").strip()
        if not data_item_id:
            raise ValidationError("Missing --data-item-id")

        fields = _read_str_list(getattr(args, "fields_json", None), field="fields-json")
        include_references = _read_include_references(
            getattr(args, "include_references_json", None),
            field="include-references-json",
        )
        language = str(getattr(args, "language", "") or "").strip() or None
        params = _build_get_params(
            data_collection_id=data_collection_id,
            fields=fields,
            include_references=include_references,
            consistent_read=bool(getattr(args, "consistent_read", False)),
            language=language,
        )

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=f"/wix-data/v2/items/{data_item_id}",
            token=token,
            params=params,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "data-items.get",
            "request": {"method": "GET", "path": f"/wix-data/v2/items/{data_item_id}", "params": params},
            "response": payload,
        }
        ctx["audit"].write("data-items.get", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_query(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        query_json = _read_json_arg(getattr(args, "query_json", None), field="query-json")
        if query_json is not None and not isinstance(query_json, dict):
            raise ValidationError("--query-json must be an object")

        filter_json = _read_json_arg(getattr(args, "filter_json", None), field="filter-json")
        if filter_json is not None and not isinstance(filter_json, dict):
            raise ValidationError("--filter-json must be an object")

        sort_value = _normalize_sort(_read_json_arg(getattr(args, "sort_json", None), field="sort-json"), field="sort-json")
        fields = _read_str_list(getattr(args, "fields_json", None), field="fields-json")
        include_references = _read_include_references(
            getattr(args, "include_references_json", None),
            field="include-references-json",
        )
        include_field_groups = _read_str_list(
            getattr(args, "include_field_groups_json", None),
            field="include-field-groups-json",
        )
        language = str(getattr(args, "language", "") or "").strip() or None
        cursor = str(getattr(args, "cursor", "") or "").strip() or None
        return_total_count = bool(getattr(args, "return_total_count", False))

        body = _build_query_body(
            query_json=dict(query_json) if isinstance(query_json, dict) else None,
            filter_json=filter_json,
            sort_value=sort_value,
            fields=fields,
            include_references=include_references,
            include_field_groups=include_field_groups,
            return_total_count=return_total_count,
            cursor=cursor,
            limit=getattr(args, "limit", None),
            offset=getattr(args, "offset", None),
            data_collection_id=data_collection_id,
            consistent_read=bool(getattr(args, "consistent_read", False)),
            language=language,
        )

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/items/query",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "data-items.query",
            "request": {"method": "POST", "path": "/wix-data/v2/items/query", "body": body},
            "response": payload,
        }
        ctx["audit"].write("data-items.query", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_count(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        query_json = _read_json_arg(getattr(args, "query_json", None), field="query-json")
        if query_json is not None and not isinstance(query_json, dict):
            raise ValidationError("--query-json must be an object")
        filter_json = _read_json_arg(getattr(args, "filter_json", None), field="filter-json")
        if filter_json is not None and not isinstance(filter_json, dict):
            raise ValidationError("--filter-json must be an object")

        language = str(getattr(args, "language", "") or "").strip() or None

        body = _build_count_payload(
            query_json=dict(query_json) if isinstance(query_json, dict) else None,
            filter_json=filter_json,
            data_collection_id=data_collection_id,
            consistent_read=bool(getattr(args, "consistent_read", False)),
            language=language,
        )

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/items/count",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "data-items.count",
            "request": {"method": "POST", "path": "/wix-data/v2/items/count", "body": body},
            "response": payload,
        }
        ctx["audit"].write("data-items.count", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_aggregate(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        aggregation = _read_json_object(
            getattr(args, "aggregation_json", None),
            field="aggregation-json",
        )
        initial_filter_json = _read_optional_json_object(
            getattr(args, "initial_filter_json", None),
            field="initial-filter-json",
        )
        final_filter_json = _read_optional_json_object(
            getattr(args, "final_filter_json", None),
            field="final-filter-json",
        )
        sort_value = _normalize_sort(_read_json_arg(getattr(args, "sort_json", None), field="sort-json"), field="sort-json")
        app_options = _read_optional_json_object(
            getattr(args, "app_options_json", None),
            field="app-options-json",
        )
        language = str(getattr(args, "language", "") or "").strip() or None
        cursor = str(getattr(args, "cursor", "") or "").strip() or None
        include_draft_items = bool(getattr(args, "include_draft_items", False))

        body: dict[str, Any] = {
            "dataCollectionId": data_collection_id,
            "aggregation": aggregation,
        }
        if initial_filter_json is not None:
            body["initialFilter"] = initial_filter_json
        if final_filter_json is not None:
            body["finalFilter"] = final_filter_json
        if sort_value is not None:
            body["sort"] = sort_value
        if cursor is not None:
            if getattr(args, "offset", None) is not None:
                raise ValidationError("Do not use --offset when --cursor is set")
            body["cursorPaging"] = _coerce_cursor_paging(cursor=cursor, limit=getattr(args, "limit", None))
        else:
            paging = _coerce_paging(limit=getattr(args, "limit", None), offset=getattr(args, "offset", None))
            if paging:
                body["paging"] = paging
        if bool(getattr(args, "return_total_count", False)):
            body["returnTotalCount"] = True
        if bool(getattr(args, "consistent_read", False)):
            body["consistentRead"] = True
        if language:
            body["language"] = language
        if app_options is not None:
            body["appOptions"] = app_options
        if include_draft_items:
            body["publishPluginOptions"] = {"includeDraftItems": True}

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/items/aggregate",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "data-items.aggregate",
            "request": {"method": "POST", "path": "/wix-data/v2/items/aggregate", "body": body},
            "response": payload,
        }
        ctx["audit"].write("data-items.aggregate", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_aggregate_pipeline(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        pipeline = _read_json_object(
            getattr(args, "pipeline_json", None),
            field="pipeline-json",
        )
        app_options = _read_optional_json_object(
            getattr(args, "app_options_json", None),
            field="app-options-json",
        )
        language = str(getattr(args, "language", "") or "").strip() or None
        include_draft_items = bool(getattr(args, "include_draft_items", False))

        body: dict[str, Any] = {
            "dataCollectionId": data_collection_id,
            "pipeline": pipeline,
        }
        if bool(getattr(args, "return_total_count", False)):
            body["returnTotalCount"] = True
        if bool(getattr(args, "consistent_read", False)):
            body["consistentRead"] = True
        if language:
            body["language"] = language
        if app_options is not None:
            body["appOptions"] = app_options
        if include_draft_items:
            body["publishPluginOptions"] = {"includeDraftItems": True}

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/items/aggregate-pipeline",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "data-items.aggregate-pipeline",
            "request": {
                "method": "POST",
                "path": "/wix-data/v2/items/aggregate-pipeline",
                "body": body,
            },
            "response": payload,
        }
        ctx["audit"].write("data-items.aggregate-pipeline", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_distinct(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        field_name = str(getattr(args, "field_name", "") or "").strip()
        if not field_name:
            raise ValidationError("Missing --field-name")

        filter_json = _read_optional_json_object(getattr(args, "filter_json", None), field="filter-json")
        language = str(getattr(args, "language", "") or "").strip() or None
        cursor = str(getattr(args, "cursor", "") or "").strip() or None
        order = str(getattr(args, "order", "") or "").strip() or None
        include_draft_items = bool(getattr(args, "include_draft_items", False))

        body: dict[str, Any] = {
            "dataCollectionId": data_collection_id,
            "fieldName": field_name,
        }
        if filter_json is not None:
            body["filter"] = filter_json
        if order:
            body["order"] = order
        if cursor is not None:
            if getattr(args, "offset", None) is not None:
                raise ValidationError("Do not use --offset when --cursor is set")
            body["cursorPaging"] = _coerce_cursor_paging(cursor=cursor, limit=getattr(args, "limit", None))
        else:
            paging = _coerce_paging(limit=getattr(args, "limit", None), offset=getattr(args, "offset", None))
            if paging:
                body["paging"] = paging
        if bool(getattr(args, "return_total_count", False)):
            body["returnTotalCount"] = True
        if bool(getattr(args, "consistent_read", False)):
            body["consistentRead"] = True
        if language:
            body["language"] = language
        if include_draft_items:
            body["publishPluginOptions"] = {"includeDraftItems": True}

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/items/query-distinct-values",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "data-items.distinct",
            "request": {
                "method": "POST",
                "path": "/wix-data/v2/items/query-distinct-values",
                "body": body,
            },
            "response": payload,
        }
        ctx["audit"].write("data-items.distinct", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_search(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        search_payload = _read_json_object(
            getattr(args, "search_json", None),
            field="search-json",
        )
        search_request = dict(search_payload)
        include_references = _read_include_references(
            getattr(args, "include_references_json", None),
            field="include-references-json",
        )
        referenced_item_options = _read_include_references(
            getattr(args, "referenced_item_options_json", None),
            field="referenced-item-options-json",
        )
        include_draft_items = bool(getattr(args, "include_draft_items", False))

        body: dict[str, Any] = {
            "dataCollectionId": data_collection_id,
            "search": search_request,
        }
        if include_references is not None:
            body["includeReferences"] = include_references
        if referenced_item_options is not None:
            body["referencedItemOptions"] = referenced_item_options
        if include_draft_items:
            body["publishPluginOptions"] = {"includeDraftItems": True}

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/items/search",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "data-items.search",
            "request": {"method": "POST", "path": "/wix-data/v2/items/search", "body": body},
            "response": payload,
        }
        ctx["audit"].write("data-items.search", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_query_referenced(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        referring_item_field_name = str(getattr(args, "referring_item_field_name", "") or "").strip()
        if not referring_item_field_name:
            raise ValidationError("Missing --referring-item-field-name")

        referring_item_id = str(getattr(args, "referring_item_id", "") or "").strip()
        if not referring_item_id:
            raise ValidationError("Missing --referring-item-id")

        fields = _read_str_list(getattr(args, "fields_json", None), field="fields-json")
        language = str(getattr(args, "language", "") or "").strip() or None
        order = str(getattr(args, "order", "") or "").strip() or None
        if order and order not in {"ASC", "DESC"}:
            raise ValidationError("--order must be ASC or DESC")

        cursor = str(getattr(args, "cursor", "") or "").strip() or None

        body = _build_query_referenced_payload(
            data_collection_id=data_collection_id,
            referring_item_field_name=referring_item_field_name,
            referring_item_id=referring_item_id,
            fields=fields,
            language=language,
            order=order,
            limit=getattr(args, "limit", None),
            offset=getattr(args, "offset", None),
            cursor=cursor,
            return_total_count=bool(getattr(args, "return_total_count", False)),
            consistent_read=bool(getattr(args, "consistent_read", False)),
            include_draft_items=bool(getattr(args, "include_draft_items", False)),
            include_hidden_products=bool(getattr(args, "include_hidden_products", False)),
            include_variants=bool(getattr(args, "include_variants", False)),
        )

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/items/query-referenced",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "data-items.query-referenced",
            "request": {"method": "POST", "path": "/wix-data/v2/items/query-referenced", "body": body},
            "response": payload,
        }
        ctx["audit"].write("data-items.query-referenced", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_is_referenced(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        referring_item_field_name = str(getattr(args, "referring_item_field_name", "") or "").strip()
        if not referring_item_field_name:
            raise ValidationError("Missing --referring-item-field-name")

        referring_item_id = str(getattr(args, "referring_item_id", "") or "").strip()
        if not referring_item_id:
            raise ValidationError("Missing --referring-item-id")

        referenced_item_id = str(getattr(args, "referenced_item_id", "") or "").strip()
        if not referenced_item_id:
            raise ValidationError("Missing --referenced-item-id")

        body = _build_is_referenced_payload(
            data_collection_id=data_collection_id,
            referring_item_field_name=referring_item_field_name,
            referring_item_id=referring_item_id,
            referenced_item_id=referenced_item_id,
            consistent_read=bool(getattr(args, "consistent_read", False)),
        )

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/items/is-referenced",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "data-items.is-referenced",
            "request": {"method": "POST", "path": "/wix-data/v2/items/is-referenced", "body": body},
            "response": payload,
        }
        ctx["audit"].write("data-items.is-referenced", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_insert_reference(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        referring_item_field_name = str(getattr(args, "referring_item_field_name", "") or "").strip()
        if not referring_item_field_name:
            raise ValidationError("Missing --referring-item-field-name")

        referring_item_id = str(getattr(args, "referring_item_id", "") or "").strip()
        if not referring_item_id:
            raise ValidationError("Missing --referring-item-id")

        referenced_item_id = str(getattr(args, "referenced_item_id", "") or "").strip()
        if not referenced_item_id:
            raise ValidationError("Missing --referenced-item-id")

        consistent_read = bool(getattr(args, "consistent_read", False))
        selector = _build_data_item_reference_selector(
            operation="insert-reference",
            data_collection_id=data_collection_id,
            referring_item_field_name=referring_item_field_name,
            referring_item_id=referring_item_id,
            referenced_item_id=referenced_item_id,
        )
        body = _build_insert_reference_payload(
            data_collection_id=data_collection_id,
            referring_item_field_name=referring_item_field_name,
            referring_item_id=referring_item_id,
            referenced_item_id=referenced_item_id,
        )
        request = {
            "method": "POST",
            "path": "/wix-data/v2/items/insert-reference",
            "body": body,
        }

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-items.insert-reference",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            before_state = _ensure_requesting_data_item_snapshot(
                data_collection_id=data_collection_id,
                data_item_id=referring_item_id,
                language=None,
                token=token,
                ctx=ctx,
            )
            plan = _build_data_items_write_plan(
                method="data-items.insert-reference",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline_before=before_state,
                proposed_changes=[{"operation": "insert-reference", "dataItemReference": body["dataItemReference"]}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify inserted reference via is-referenced with consistentRead=true",
                },
            )

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-items.insert-reference",
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("data-items.insert-reference.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            str(ctx.get("plan_in")),
            expected_method="data-items.insert-reference",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        _assert_no_item_drift(
            plan=loaded_plan,
            token=token,
            ctx=ctx,
            data_collection_id=data_collection_id,
            data_item_id=referring_item_id,
            language=None,
        )

        already_referenced = _read_reference_exists(
            data_collection_id=data_collection_id,
            referring_item_field_name=referring_item_field_name,
            referring_item_id=referring_item_id,
            referenced_item_id=referenced_item_id,
            consistent_read=consistent_read,
            token=token,
            ctx=ctx,
        )
        if already_referenced:
            raise SafetyError("Refused: insert-reference would be a no-op because reference already exists")

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/items/insert-reference",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        after_state = _read_reference_exists(
            data_collection_id=data_collection_id,
            referring_item_field_name=referring_item_field_name,
            referring_item_id=referring_item_id,
            referenced_item_id=referenced_item_id,
            consistent_read=consistent_read,
            token=token,
            ctx=ctx,
        )
        verification = {
            "ok": after_state is True,
            "type": "read-after-write",
            "path": "/wix-data/v2/items/is-referenced",
            "method": "POST",
            "response": {"isReferenced": after_state},
        }

        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-items.insert-reference",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "diff_applied": plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
        }

        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "data-items.insert-reference",
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("data-items.insert-reference.apply", {"receipt": receipt})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "data-items.insert-reference",
        }
        ctx["audit"].write("data-items.insert-reference.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-items.insert-reference"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-items.insert-reference"}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_remove_reference(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        referring_item_field_name = str(getattr(args, "referring_item_field_name", "") or "").strip()
        if not referring_item_field_name:
            raise ValidationError("Missing --referring-item-field-name")

        referring_item_id = str(getattr(args, "referring_item_id", "") or "").strip()
        if not referring_item_id:
            raise ValidationError("Missing --referring-item-id")

        referenced_item_id = str(getattr(args, "referenced_item_id", "") or "").strip()
        if not referenced_item_id:
            raise ValidationError("Missing --referenced-item-id")

        consistent_read = bool(getattr(args, "consistent_read", False))
        selector = _build_data_item_reference_selector(
            operation="remove-reference",
            data_collection_id=data_collection_id,
            referring_item_field_name=referring_item_field_name,
            referring_item_id=referring_item_id,
            referenced_item_id=referenced_item_id,
        )
        body = _build_insert_reference_payload(
            data_collection_id=data_collection_id,
            referring_item_field_name=referring_item_field_name,
            referring_item_id=referring_item_id,
            referenced_item_id=referenced_item_id,
        )
        request = {
            "method": "POST",
            "path": "/wix-data/v2/items/remove-reference",
            "body": body,
        }

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-items.remove-reference",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            before_state = _ensure_requesting_data_item_snapshot(
                data_collection_id=data_collection_id,
                data_item_id=referring_item_id,
                language=None,
                token=token,
                ctx=ctx,
            )
            plan = _build_data_items_write_plan(
                method="data-items.remove-reference",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline_before=before_state,
                proposed_changes=[{"operation": "remove-reference", "dataItemReference": body["dataItemReference"]}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify removed reference via is-referenced with consistentRead=true",
                },
            )

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-items.remove-reference",
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("data-items.remove-reference.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            str(ctx.get("plan_in")),
            expected_method="data-items.remove-reference",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        _assert_no_item_drift(
            plan=loaded_plan,
            token=token,
            ctx=ctx,
            data_collection_id=data_collection_id,
            data_item_id=referring_item_id,
            language=None,
        )

        exists = _read_reference_exists(
            data_collection_id=data_collection_id,
            referring_item_field_name=referring_item_field_name,
            referring_item_id=referring_item_id,
            referenced_item_id=referenced_item_id,
            consistent_read=consistent_read,
            token=token,
            ctx=ctx,
        )
        if not exists:
            raise SafetyError("Refused: remove-reference would be a no-op because reference does not exist")

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/items/remove-reference",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        exists_after = _read_reference_exists(
            data_collection_id=data_collection_id,
            referring_item_field_name=referring_item_field_name,
            referring_item_id=referring_item_id,
            referenced_item_id=referenced_item_id,
            consistent_read=consistent_read,
            token=token,
            ctx=ctx,
        )
        verification = {
            "ok": exists_after is False,
            "type": "read-after-write",
            "path": "/wix-data/v2/items/is-referenced",
            "method": "POST",
            "response": {"isReferenced": exists_after},
        }

        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-items.remove-reference",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "diff_applied": plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
        }

        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "data-items.remove-reference",
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("data-items.remove-reference.apply", {"receipt": receipt})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "data-items.remove-reference",
        }
        ctx["audit"].write("data-items.remove-reference.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-items.remove-reference"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-items.remove-reference"}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_replace_references(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        referring_item_field_name = str(getattr(args, "referring_item_field_name", "") or "").strip()
        if not referring_item_field_name:
            raise ValidationError("Missing --referring-item-field-name")

        referring_item_id = str(getattr(args, "referring_item_id", "") or "").strip()
        if not referring_item_id:
            raise ValidationError("Missing --referring-item-id")

        raw_new_ids = _read_str_list(getattr(args, "new_referenced_item_ids_json", None), field="new-referenced-item-ids-json")
        new_referenced_item_ids: list[str] = _normalize_reference_ids(raw_new_ids or [])

        consistent_read = bool(getattr(args, "consistent_read", False))
        selector = _build_data_item_reference_selector(
            operation="replace-references",
            data_collection_id=data_collection_id,
            referring_item_field_name=referring_item_field_name,
            referring_item_id=referring_item_id,
            new_referenced_item_ids=new_referenced_item_ids,
        )
        body = _build_replace_references_payload(
            data_collection_id=data_collection_id,
            referring_item_field_name=referring_item_field_name,
            referring_item_id=referring_item_id,
            new_referenced_item_ids=new_referenced_item_ids,
        )
        request = {
            "method": "POST",
            "path": "/wix-data/v2/items/replace-references",
            "body": body,
        }

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-items.replace-references",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            before_state = _ensure_requesting_data_item_snapshot(
                data_collection_id=data_collection_id,
                data_item_id=referring_item_id,
                language=None,
                token=token,
                ctx=ctx,
            )
            plan = _build_data_items_write_plan(
                method="data-items.replace-references",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline_before=before_state,
                proposed_changes=[{"operation": "replace-references", "dataItemReferenceIds": new_referenced_item_ids}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify referenced item IDs via query-referenced with consistentRead=true",
                },
            )

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-items.replace-references",
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("data-items.replace-references.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            str(ctx.get("plan_in")),
            expected_method="data-items.replace-references",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        _assert_no_item_drift(
            plan=loaded_plan,
            token=token,
            ctx=ctx,
            data_collection_id=data_collection_id,
            data_item_id=referring_item_id,
            language=None,
        )

        before_references = _read_referenced_item_ids(
            data_collection_id=data_collection_id,
            referring_item_field_name=referring_item_field_name,
            referring_item_id=referring_item_id,
            consistent_read=consistent_read,
            token=token,
            ctx=ctx,
        )
        if before_references == new_referenced_item_ids:
            raise SafetyError("Refused: replace-references would be a no-op because references are already set as requested")

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/items/replace-references",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        after_references = _read_referenced_item_ids(
            data_collection_id=data_collection_id,
            referring_item_field_name=referring_item_field_name,
            referring_item_id=referring_item_id,
            consistent_read=consistent_read,
            token=token,
            ctx=ctx,
        )
        verification = {
            "ok": after_references == new_referenced_item_ids,
            "type": "read-after-write",
            "path": "/wix-data/v2/items/query-referenced",
            "method": "POST",
            "requested": new_referenced_item_ids,
            "response": after_references,
        }

        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-items.replace-references",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "diff_applied": plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
        }

        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "data-items.replace-references",
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("data-items.replace-references.apply", {"receipt": receipt})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "data-items.replace-references",
        }
        ctx["audit"].write("data-items.replace-references.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-items.replace-references"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-items.replace-references"}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_bulk_insert(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        data_items = _read_data_items(getattr(args, "data_items_json", None), field="data-items-json")
        explicit_item_ids, has_missing_ids, normalized_data_items = _normalize_bulk_item_ids(data_items)

        app_options = _read_json_arg(getattr(args, "app_options_json", None), field="app-options-json")
        if app_options is not None and not isinstance(app_options, dict):
            raise ValidationError("--app-options-json must be a JSON object")

        return_entity = bool(getattr(args, "return_entity", False))

        selector = _build_bulk_data_items_selector(
            operation="bulk-insert",
            data_collection_id=data_collection_id,
            data_item_ids=explicit_item_ids,
        )

        body = _build_data_items_bulk_insert_payload(
            data_collection_id=data_collection_id,
            data_items=normalized_data_items,
            app_options=app_options,
            return_entity=return_entity,
        )

        request = {
            "method": "POST",
            "path": "/wix-data/v2/bulk/items/insert",
            "body": body,
        }

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-items.bulk-insert",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_data_items_write_plan(
                method="data-items.bulk-insert",
                request=request,
                selector=selector,
                ctx=ctx,
                proposed_changes=[
                    {
                        "operation": "bulk-insert",
                        "item_count": len(normalized_data_items),
                        "data_item_ids": explicit_item_ids,
                    }
                ],
                verification_plan={
                    "type": "bulk-write",
                    "notes": "Verify bulk results using bulkActionMetadata and read-back when explicit IDs are available",
                },
            )

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {"ok": True, "dry_run": True, "method": "data-items.bulk-insert", "plan": plan, "plan_out": plan_out}
            ctx["audit"].write("data-items.bulk-insert.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        if has_missing_ids and not return_entity:
            raise SafetyError(
                "Refused: bulk-insert includes items without explicit IDs; use --return-entity to enable safe apply verification"
            )

        if plan_in:
            _load_plan(
                str(ctx.get("plan_in")),
                expected_method="data-items.bulk-insert",
                expected_selector=selector,
                ctx=ctx,
            )

        existing_ids = _find_existing_bulk_insert_ids(
            data_collection_id=data_collection_id,
            explicit_item_ids=explicit_item_ids,
            token=token,
            ctx=ctx,
        )
        if existing_ids:
            raise SafetyError(
                "Refused: bulk-insert explicit item IDs already exist: " + ", ".join(existing_ids)
            )

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/bulk/items/insert",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        verification = _build_bulk_insert_verification(
            response=response,
            explicit_item_ids=explicit_item_ids,
            return_entity=return_entity,
            data_collection_id=data_collection_id,
            token=token,
            ctx=ctx,
        )

        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-items.bulk-insert",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "diff_applied": plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
        }

        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "data-items.bulk-insert",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-items.bulk-insert.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "data-items.bulk-insert",
        }
        ctx["audit"].write("data-items.bulk-insert.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-items.bulk-insert"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-items.bulk-insert"}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_bulk_patch(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        patches = _read_data_item_patches(getattr(args, "patches_json", None), field="patches-json")
        condition = _read_json_arg(getattr(args, "condition_json", None), field="condition-json")
        if condition is not None and not isinstance(condition, dict):
            raise ValidationError("--condition-json must be a JSON object")

        patched_item_ids = [str(patch.get("dataItemId") or "").strip() for patch in patches]
        selector = _build_bulk_data_items_selector(
            operation="bulk-patch",
            data_collection_id=data_collection_id,
            data_item_ids=patched_item_ids,
        )

        body = _build_data_items_bulk_patch_payload(
            data_collection_id=data_collection_id,
            patches=patches,
            condition=condition,
        )
        request = {
            "method": "POST",
            "path": "/wix-data/v2/bulk/items/patch",
            "body": body,
        }

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-items.bulk-patch",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            before_state: dict[str, Any] = {}
            for item_id in patched_item_ids:
                before_state[item_id] = _ensure_requesting_data_item_snapshot(
                    data_collection_id=data_collection_id,
                    data_item_id=item_id,
                    language=None,
                    token=token,
                    ctx=ctx,
                )

            plan = _build_data_items_write_plan(
                method="data-items.bulk-patch",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline_before=before_state,
                proposed_changes=[
                    {
                        "operation": "bulk-patch",
                        "patch_count": len(patches),
                        "data_item_ids": patched_item_ids,
                    }
                ],
                verification_plan={
                    "type": "bulk-write",
                    "notes": "Verify by reading each patched item with consistentRead=true",
                },
            )

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {"ok": True, "dry_run": True, "method": "data-items.bulk-patch", "plan": plan, "plan_out": plan_out}
            ctx["audit"].write("data-items.bulk-patch.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            str(ctx.get("plan_in")),
            expected_method="data-items.bulk-patch",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan

        _assert_no_bulk_item_drifts(
            plan=loaded_plan,
            token=token,
            ctx=ctx,
            data_collection_id=data_collection_id,
            data_item_ids=patched_item_ids,
            language=None,
        )

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/bulk/items/patch",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        verification = _build_bulk_patch_verification(
            response=response,
            patched_item_ids=patched_item_ids,
            data_collection_id=data_collection_id,
            token=token,
            ctx=ctx,
        )

        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-items.bulk-patch",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "diff_applied": plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
        }

        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "data-items.bulk-patch",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-items.bulk-patch.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as e:
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": [str(e)],
            "refusal_type": "SafetyError",
            "method": "data-items.bulk-patch",
        }
        ctx["audit"].write("data-items.bulk-patch.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as e:
        out = {"ok": False, "error": str(e), "error_type": "ValidationError", "method": "data-items.bulk-patch"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as e:
        out = {"ok": False, "error": str(e), "error_type": e.__class__.__name__, "method": "data-items.bulk-patch"}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_insert(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        data_item = _read_json_object(getattr(args, "data_item_json", None), field="data-item-json")
        if not data_item:
            raise ValidationError("--data-item-json cannot be empty")

        language = str(getattr(args, "language", "") or "").strip() or None
        data_item_id = str(data_item.get("id") or "").strip() if isinstance(data_item, dict) else None
        if data_item_id:
            selector = _build_data_item_selector(operation="insert", data_collection_id=data_collection_id, data_item_id=data_item_id)
        else:
            selector = _build_data_item_selector(operation="insert", data_collection_id=data_collection_id)

        body = {
            "dataCollectionId": data_collection_id,
            "dataItem": data_item,
        }
        request = {"method": "POST", "path": "/wix-data/v2/items", "body": body}
        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )

        plan = _build_data_items_write_plan(
            method="data-items.insert",
            request=request,
            selector=selector,
            ctx=ctx,
            proposed_changes=[{"operation": "insert", "dataItem": data_item}],
            verification_plan={"type": "read-after-write", "notes": "Read inserted item via GET with consistentRead=true"},
        )

        if ctx.get("plan_in"):
            plan = _load_plan(
                str(ctx.get("plan_in")),
                expected_method="data-items.insert",
                expected_selector=selector,
                ctx=ctx,
            )

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-items.insert",
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("data-items.insert.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        if ctx.get("plan_in"):
            _load_plan(
                str(ctx.get("plan_in")),
                expected_method="data-items.insert",
                expected_selector=selector,
                ctx=ctx,
            )

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/items",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        created_id = _extract_data_item_id(response)
        verified_payload: dict[str, Any] = {
            "ok": False,
            "type": "read-after-write",
            "notes": "Insert verification skipped because inserted item id is missing from response",
        }
        if created_id:
            verified_payload = {
                "ok": False,
                "type": "read-after-write",
                "path": f"/wix-data/v2/items/{created_id}",
                "method": "GET",
                "response": _ensure_requesting_data_item_snapshot(
                    data_collection_id=data_collection_id,
                    data_item_id=created_id,
                    language=language,
                    token=token,
                    ctx=ctx,
                ),
            }
            verified_payload["ok"] = True

        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-items.insert",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verified_payload,
            "diff_applied": plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
        }

        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": bool(verified_payload.get("ok")),
            "dry_run": False,
            "method": "data-items.insert",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-items.insert.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as e:
        out = {"ok": True, "dry_run": False, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError", "method": "data-items.insert"}
        ctx["audit"].write("data-items.insert.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as e:
        out = {"ok": False, "error": str(e), "error_type": "ValidationError", "method": "data-items.insert"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as e:
        out = {"ok": False, "error": str(e), "error_type": e.__class__.__name__, "method": "data-items.insert"}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_update(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        data_item_id = str(getattr(args, "data_item_id", "") or "").strip()
        if not data_item_id:
            raise ValidationError("Missing --data-item-id")

        data_item = _read_json_object(getattr(args, "data_item_json", None), field="data-item-json")
        if not data_item:
            raise ValidationError("--data-item-json cannot be empty")

        condition = _read_json_arg(getattr(args, "condition_json", None), field="condition-json")
        if condition is not None and not isinstance(condition, dict):
            raise ValidationError("--condition-json must be a JSON object")

        language = str(getattr(args, "language", "") or "").strip() or None
        selector = _build_data_item_selector(operation="update", data_collection_id=data_collection_id, data_item_id=data_item_id)

        data_item = _ensure_matching_item_id(
            payload=data_item,
            key="id",
            expected_id=data_item_id,
            field="data-item-json",
        )

        body: dict[str, Any] = {
            "dataCollectionId": data_collection_id,
            "dataItem": data_item,
        }
        if condition is not None:
            body["condition"] = condition

        request = {
            "method": "PUT",
            "path": f"/wix-data/v2/items/{data_item_id}",
            "body": body,
        }

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-items.update",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            before_state = _ensure_requesting_data_item_snapshot(
                data_collection_id=data_collection_id,
                data_item_id=data_item_id,
                language=language,
                token=token,
                ctx=ctx,
            )
            plan = _build_data_items_write_plan(
                method="data-items.update",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline_before=before_state,
                proposed_changes=[{"operation": "update", "dataItem": data_item, "condition": condition}],
                verification_plan={"type": "read-after-write", "notes": "Read updated item via GET with consistentRead=true"},
            )

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {"ok": True, "dry_run": True, "method": "data-items.update", "plan": plan, "plan_out": plan_out}
            ctx["audit"].write("data-items.update.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            str(ctx.get("plan_in")),
            expected_method="data-items.update",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        _assert_no_item_drift(
            plan=loaded_plan,
            token=token,
            ctx=ctx,
            data_collection_id=data_collection_id,
            data_item_id=data_item_id,
            language=language,
        )

        response = _request_json(
            method="PUT",
            base_url=ctx["cfg"].base_url,
            path=f"/wix-data/v2/items/{data_item_id}",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        verification = {
            "ok": True,
            "type": "read-after-write",
            "path": f"/wix-data/v2/items/{data_item_id}",
            "method": "GET",
            "response": _ensure_requesting_data_item_snapshot(
                data_collection_id=data_collection_id,
                data_item_id=data_item_id,
                language=language,
                token=token,
                ctx=ctx,
            ),
        }

        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-items.update",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "diff_applied": plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
        }

        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": True,
            "dry_run": False,
            "method": "data-items.update",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-items.update.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0
    except SafetyError as e:
        out = {"ok": True, "dry_run": False, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError", "method": "data-items.update"}
        ctx["audit"].write("data-items.update.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as e:
        out = {"ok": False, "error": str(e), "error_type": "ValidationError", "method": "data-items.update"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as e:
        out = {"ok": False, "error": str(e), "error_type": e.__class__.__name__, "method": "data-items.update"}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_patch(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        data_item_id = str(getattr(args, "data_item_id", "") or "").strip()
        if not data_item_id:
            raise ValidationError("Missing --data-item-id")

        patch_payload = _read_json_object(getattr(args, "patch_json", None), field="patch-json")
        if not patch_payload:
            raise ValidationError("--patch-json cannot be empty")

        condition = _read_json_arg(getattr(args, "condition_json", None), field="condition-json")
        if condition is not None and not isinstance(condition, dict):
            raise ValidationError("--condition-json must be a JSON object")

        language = str(getattr(args, "language", "") or "").strip() or None
        selector = _build_data_item_selector(operation="patch", data_collection_id=data_collection_id, data_item_id=data_item_id)

        patch_payload = _ensure_matching_item_id(
            payload=patch_payload,
            key="dataItemId",
            expected_id=data_item_id,
            field="patch-json",
        )

        body: dict[str, Any] = {
            "dataCollectionId": data_collection_id,
            "patch": patch_payload,
        }
        if condition is not None:
            body["condition"] = condition

        request = {
            "method": "PATCH",
            "path": f"/wix-data/v2/items/{data_item_id}",
            "body": body,
        }

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-items.patch",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            before_state = _ensure_requesting_data_item_snapshot(
                data_collection_id=data_collection_id,
                data_item_id=data_item_id,
                language=language,
                token=token,
                ctx=ctx,
            )
            plan = _build_data_items_write_plan(
                method="data-items.patch",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline_before=before_state,
                proposed_changes=[{"operation": "patch", "patch": patch_payload, "condition": condition}],
                verification_plan={"type": "read-after-write", "notes": "Read patched item via GET with consistentRead=true"},
            )

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {"ok": True, "dry_run": True, "method": "data-items.patch", "plan": plan, "plan_out": plan_out}
            ctx["audit"].write("data-items.patch.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            str(ctx.get("plan_in")),
            expected_method="data-items.patch",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        _assert_no_item_drift(
            plan=loaded_plan,
            token=token,
            ctx=ctx,
            data_collection_id=data_collection_id,
            data_item_id=data_item_id,
            language=language,
        )

        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/wix-data/v2/items/{data_item_id}",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        verification = {
            "ok": True,
            "type": "read-after-write",
            "path": f"/wix-data/v2/items/{data_item_id}",
            "method": "GET",
            "response": _ensure_requesting_data_item_snapshot(
                data_collection_id=data_collection_id,
                data_item_id=data_item_id,
                language=language,
                token=token,
                ctx=ctx,
            ),
        }

        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-items.patch",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "diff_applied": plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
        }

        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": True,
            "dry_run": False,
            "method": "data-items.patch",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-items.patch.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0
    except SafetyError as e:
        out = {"ok": True, "dry_run": False, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError", "method": "data-items.patch"}
        ctx["audit"].write("data-items.patch.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as e:
        out = {"ok": False, "error": str(e), "error_type": "ValidationError", "method": "data-items.patch"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as e:
        out = {"ok": False, "error": str(e), "error_type": e.__class__.__name__, "method": "data-items.patch"}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_remove(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        data_item_id = str(getattr(args, "data_item_id", "") or "").strip()
        if not data_item_id:
            raise ValidationError("Missing --data-item-id")

        condition = _read_json_arg(getattr(args, "condition_json", None), field="condition-json")
        if condition is not None and not isinstance(condition, dict):
            raise ValidationError("--condition-json must be a JSON object")

        language = str(getattr(args, "language", "") or "").strip() or None
        selector = _build_data_item_selector(operation="remove", data_collection_id=data_collection_id, data_item_id=data_item_id)

        params = {"dataCollectionId": data_collection_id}
        body: dict[str, Any] | None = None
        if condition is not None:
            body = {"condition": condition}

        request = {
            "method": "DELETE",
            "path": f"/wix-data/v2/items/{data_item_id}",
            "params": params,
        }

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-items.remove",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            before_state = _ensure_requesting_data_item_snapshot(
                data_collection_id=data_collection_id,
                data_item_id=data_item_id,
                language=language,
                token=token,
                ctx=ctx,
            )
            plan = _build_data_items_write_plan(
                method="data-items.remove",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline_before=before_state,
                proposed_changes=[{"operation": "remove", "condition": condition}],
                verification_plan={"type": "read-after-delete", "notes": "Read removed item via GET with consistentRead=true; 404 means removed"},
            )

        if not _should_apply(ctx, requires_ack=True):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {"ok": True, "dry_run": True, "method": "data-items.remove", "plan": plan, "plan_out": plan_out}
            ctx["audit"].write("data-items.remove.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            str(ctx.get("plan_in")),
            expected_method="data-items.remove",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        _assert_no_item_drift(
            plan=loaded_plan,
            token=token,
            ctx=ctx,
            data_collection_id=data_collection_id,
            data_item_id=data_item_id,
            language=language,
        )

        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/wix-data/v2/items/{data_item_id}",
            token=token,
            params=params,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        verify_payload, verify_status = _safe_get_data_item_for_verification(
            data_collection_id=data_collection_id,
            data_item_id=data_item_id,
            language=language,
            token=token,
            ctx=ctx,
            allow_not_found=True,
        )
        if verify_status == 404:
            verification = {
                "ok": True,
                "type": "read-after-delete",
                "path": f"/wix-data/v2/items/{data_item_id}",
                "method": "GET",
                "notes": "Item not found after delete (consistent with 404)",
                "removed": True,
            }
        else:
            verification = {
                "ok": False,
                "type": "read-after-delete",
                "path": f"/wix-data/v2/items/{data_item_id}",
                "method": "GET",
                "response": verify_payload,
                "removed": False,
                "notes": "Item still exists after delete",
            }

        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-items.remove",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "diff_applied": plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
        }

        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "data-items.remove",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-items.remove.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as e:
        out = {"ok": True, "dry_run": False, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError", "method": "data-items.remove"}
        ctx["audit"].write("data-items.remove.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as e:
        out = {"ok": False, "error": str(e), "error_type": "ValidationError", "method": "data-items.remove"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as e:
        out = {"ok": False, "error": str(e), "error_type": e.__class__.__name__, "method": "data-items.remove"}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_save(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        data_item = _read_json_object(getattr(args, "data_item_json", None), field="data-item-json")
        if not data_item:
            raise ValidationError("--data-item-json cannot be empty")

        app_options = _read_optional_json_object(getattr(args, "app_options_json", None), field="app-options-json")
        include_draft_items = bool(getattr(args, "include_draft_items", False))
        data_item_id = str(data_item.get("id") or "").strip() if isinstance(data_item, dict) else None

        selector = _build_data_item_selector(
            operation="save",
            data_collection_id=data_collection_id,
            data_item_id=data_item_id if data_item_id else None,
        )
        if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not ctx.get("plan_in"):
            raise SafetyError(
                "Refused: data-items.save live apply requires a reviewed saved plan. "
                "First run with --plan-out, review the plan, then rerun with --plan-in --apply --yes."
            )

        body = _build_data_items_save_payload(
            data_collection_id=data_collection_id,
            data_item=data_item,
            app_options=app_options,
            include_draft_items=include_draft_items,
        )
        request = {
            "method": "POST",
            "path": "/wix-data/v2/items/save",
            "body": body,
        }

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-items.save",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            before_state = None
            if data_item_id:
                before_state = {
                    data_item_id: _read_current_data_item_state(
                        data_collection_id=data_collection_id,
                        data_item_id=data_item_id,
                        language=None,
                        token=token,
                        ctx=ctx,
                    )
                }
            plan = _build_data_items_write_plan(
                method="data-items.save",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline_before=before_state,
                proposed_changes=[{"operation": "save", "dataItem": data_item}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify by rereading the saved item id returned by Wix.",
                },
                rollback_notes="No automatic rollback. Save is an upsert and may replace existing item data.",
            )

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {"ok": True, "dry_run": True, "method": "data-items.save", "plan": plan, "plan_out": plan_out}
            ctx["audit"].write("data-items.save.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            str(ctx.get("plan_in")),
            expected_method="data-items.save",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan

        if data_item_id and isinstance(loaded_plan.get("baseline", {}).get("before_state"), dict):
            _assert_no_data_item_state_drifts(
                plan=loaded_plan,
                token=token,
                ctx=ctx,
                data_collection_id=data_collection_id,
                data_item_ids=[data_item_id],
                language=None,
            )

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/items/save",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        saved_id = _extract_data_item_id(response)
        if saved_id:
            after_state = _ensure_requesting_data_item_snapshot(
                data_collection_id=data_collection_id,
                data_item_id=saved_id,
                language=None,
                token=token,
                ctx=ctx,
            )
            verification = {
                "ok": _extract_data_item_id(after_state) == saved_id,
                "type": "read-after-write",
                "path": f"/wix-data/v2/items/{saved_id}",
                "method": "GET",
                "saved_id": saved_id,
                "response": after_state,
            }
        else:
            verification = {
                "ok": False,
                "type": "read-after-write",
                "notes": "Save verification skipped because Wix did not return a data item id.",
                "response": response,
            }

        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-items.save",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "diff_applied": plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
        }

        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "data-items.save",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-items.save.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as e:
        out = {"ok": True, "dry_run": False, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError", "method": "data-items.save"}
        ctx["audit"].write("data-items.save.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as e:
        out = {"ok": False, "error": str(e), "error_type": "ValidationError", "method": "data-items.save"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as e:
        out = {"ok": False, "error": str(e), "error_type": e.__class__.__name__, "method": "data-items.save"}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_truncate(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        selector = _build_bulk_data_items_selector(
            operation="truncate",
            data_collection_id=data_collection_id,
            data_item_ids=None,
        )
        body = _build_data_items_truncate_payload(data_collection_id=data_collection_id)
        request = {
            "method": "POST",
            "path": "/wix-data/v2/items/truncate",
            "body": body,
        }

        if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not ctx.get("plan_in"):
            raise SafetyError(
                "Refused: data-items.truncate live apply requires a reviewed saved plan. "
                "First run with --plan-out, review the plan, then rerun with --plan-in --apply --yes --ack-irreversible."
            )

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )

        before_count = _read_data_items_count(data_collection_id=data_collection_id, token=token, ctx=ctx)
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-items.truncate",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_data_items_write_plan(
                method="data-items.truncate",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline_before={"count": before_count},
                proposed_changes=[{"operation": "truncate", "before_count": before_count}],
                verification_plan={
                    "type": "count-after-write",
                    "notes": "Verify the collection count is 0 after truncate. No item-level snapshot exists.",
                },
                rollback_notes="No automatic rollback. Truncate deletes all items and no useful item-level snapshot exists.",
            )

        if not _should_apply(ctx, requires_ack=True):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {"ok": True, "dry_run": True, "method": "data-items.truncate", "plan": plan, "plan_out": plan_out}
            ctx["audit"].write("data-items.truncate.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            str(ctx.get("plan_in")),
            expected_method="data-items.truncate",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        baseline = loaded_plan.get("baseline")
        if not isinstance(baseline, dict) or not isinstance(baseline.get("before_state"), dict):
            raise SafetyError("Refused: plan missing before-state snapshot")
        expected_before_count = baseline["before_state"].get("count")
        if not isinstance(expected_before_count, int):
            raise SafetyError("Refused: plan missing before-state count")
        current_before_count = _read_data_items_count(data_collection_id=data_collection_id, token=token, ctx=ctx)
        if current_before_count != expected_before_count:
            raise SafetyError("Refused: collection count changed since plan was created")

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/items/truncate",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        after_count = _read_data_items_count(data_collection_id=data_collection_id, token=token, ctx=ctx)
        verification = {
            "ok": after_count == 0,
            "type": "count-after-write",
            "path": "/wix-data/v2/items/count",
            "method": "POST",
            "before_count": expected_before_count,
            "after_count": after_count,
            "response": {"totalCount": after_count},
        }

        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-items.truncate",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "diff_applied": plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
        }

        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "data-items.truncate",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-items.truncate.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as e:
        out = {"ok": True, "dry_run": False, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError", "method": "data-items.truncate"}
        ctx["audit"].write("data-items.truncate.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as e:
        out = {"ok": False, "error": str(e), "error_type": "ValidationError", "method": "data-items.truncate"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as e:
        out = {"ok": False, "error": str(e), "error_type": e.__class__.__name__, "method": "data-items.truncate"}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_bulk_remove(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        data_item_ids = _read_data_item_ids(getattr(args, "data_item_ids_json", None), field="data-item-ids-json")
        condition = _read_json_arg(getattr(args, "condition_json", None), field="condition-json")
        if condition is not None and not isinstance(condition, dict):
            raise ValidationError("--condition-json must be a JSON object")

        app_options = _read_optional_json_object(getattr(args, "app_options_json", None), field="app-options-json")
        include_draft_items = bool(getattr(args, "include_draft_items", False))
        selector = _build_bulk_data_items_selector(
            operation="bulk-remove",
            data_collection_id=data_collection_id,
            data_item_ids=data_item_ids,
        )
        body = _build_data_items_bulk_remove_payload(
            data_collection_id=data_collection_id,
            data_item_ids=data_item_ids,
            condition=condition,
            app_options=app_options,
            include_draft_items=include_draft_items,
        )
        request = {
            "method": "POST",
            "path": "/wix-data/v2/bulk/items/remove",
            "body": body,
        }

        if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not ctx.get("plan_in"):
            raise SafetyError(
                "Refused: data-items.bulk-remove live apply requires a reviewed saved plan. "
                "First run with --plan-out, review the plan, then rerun with --plan-in --apply --yes --ack-irreversible."
            )

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-items.bulk-remove",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            before_state = _capture_data_item_states(
                data_collection_id=data_collection_id,
                data_item_ids=data_item_ids,
                language=None,
                token=token,
                ctx=ctx,
            )
            plan = _build_data_items_write_plan(
                method="data-items.bulk-remove",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline_before=before_state,
                proposed_changes=[
                    {
                        "operation": "bulk-remove",
                        "data_item_ids": data_item_ids,
                        "condition": condition,
                    }
                ],
                verification_plan={
                    "type": "read-after-delete",
                    "notes": "Verify each removed id returns 404 after apply.",
                },
                rollback_notes="No automatic rollback. Bulk remove is irreversible and removed items cannot be restored.",
            )

        if not _should_apply(ctx, requires_ack=True):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {"ok": True, "dry_run": True, "method": "data-items.bulk-remove", "plan": plan, "plan_out": plan_out}
            ctx["audit"].write("data-items.bulk-remove.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            str(ctx.get("plan_in")),
            expected_method="data-items.bulk-remove",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        _assert_no_data_item_state_drifts(
            plan=loaded_plan,
            token=token,
            ctx=ctx,
            data_collection_id=data_collection_id,
            data_item_ids=data_item_ids,
            language=None,
        )

        current_states = _capture_data_item_states(
            data_collection_id=data_collection_id,
            data_item_ids=data_item_ids,
            language=None,
            token=token,
            ctx=ctx,
        )
        missing_ids = [item_id for item_id, state in current_states.items() if state.get("missing")]
        if missing_ids:
            raise SafetyError("Refused: bulk-remove target ids do not all exist: " + ", ".join(missing_ids))

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/bulk/items/remove",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        after_states = _capture_data_item_states(
            data_collection_id=data_collection_id,
            data_item_ids=data_item_ids,
            language=None,
            token=token,
            ctx=ctx,
        )
        verification = {
            "ok": all(state.get("missing") for state in after_states.values()),
            "type": "read-after-delete",
            "path": "/wix-data/v2/items/{dataItemId}",
            "method": "GET",
            "requested_ids": data_item_ids,
            "response": after_states,
        }

        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-items.bulk-remove",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "diff_applied": plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
        }

        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "data-items.bulk-remove",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-items.bulk-remove.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as e:
        out = {"ok": True, "dry_run": False, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError", "method": "data-items.bulk-remove"}
        ctx["audit"].write("data-items.bulk-remove.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as e:
        out = {"ok": False, "error": str(e), "error_type": "ValidationError", "method": "data-items.bulk-remove"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as e:
        out = {"ok": False, "error": str(e), "error_type": e.__class__.__name__, "method": "data-items.bulk-remove"}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_bulk_save(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        data_items = _read_data_items(getattr(args, "data_items_json", None), field="data-items-json")
        explicit_item_ids, has_missing_ids, normalized_data_items = _normalize_bulk_item_ids(data_items)
        app_options = _read_optional_json_object(getattr(args, "app_options_json", None), field="app-options-json")
        include_draft_items = bool(getattr(args, "include_draft_items", False))
        return_entity = bool(getattr(args, "return_entity", False))

        selector = _build_bulk_data_items_selector(
            operation="bulk-save",
            data_collection_id=data_collection_id,
            data_item_ids=explicit_item_ids,
        )
        body = _build_data_items_bulk_save_payload(
            data_collection_id=data_collection_id,
            data_items=normalized_data_items,
            app_options=app_options,
            include_draft_items=include_draft_items,
            return_entity=return_entity,
        )
        request = {
            "method": "POST",
            "path": "/wix-data/v2/bulk/items/save",
            "body": body,
        }

        if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not ctx.get("plan_in"):
            raise SafetyError(
                "Refused: data-items.bulk-save live apply requires a reviewed saved plan. "
                "First run with --plan-out, review the plan, then rerun with --plan-in --apply --yes."
            )

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-items.bulk-save",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            before_state = (
                _capture_data_item_states(
                    data_collection_id=data_collection_id,
                    data_item_ids=explicit_item_ids,
                    language=None,
                    token=token,
                    ctx=ctx,
                )
                if explicit_item_ids
                else None
            )
            plan = _build_data_items_write_plan(
                method="data-items.bulk-save",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline_before=before_state,
                proposed_changes=[
                    {
                        "operation": "bulk-save",
                        "item_count": len(normalized_data_items),
                        "data_item_ids": explicit_item_ids,
                    }
                ],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify explicit ids by rereading them after apply. Missing ids require --return-entity.",
                },
                rollback_notes="No automatic rollback. Bulk save is an upsert and may replace existing data.",
            )

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {"ok": True, "dry_run": True, "method": "data-items.bulk-save", "plan": plan, "plan_out": plan_out}
            ctx["audit"].write("data-items.bulk-save.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        if has_missing_ids and not return_entity:
            raise SafetyError(
                "Refused: bulk-save includes items without explicit IDs; use --return-entity to enable safe apply verification"
            )

        loaded_plan = _load_plan(
            str(ctx.get("plan_in")),
            expected_method="data-items.bulk-save",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        if explicit_item_ids:
            _assert_no_data_item_state_drifts(
                plan=loaded_plan,
                token=token,
                ctx=ctx,
                data_collection_id=data_collection_id,
                data_item_ids=explicit_item_ids,
                language=None,
            )

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/bulk/items/save",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        verify_ids = list(dict.fromkeys(explicit_item_ids + _extract_bulk_data_item_ids(response)))
        if not verify_ids:
            verification = {
                "ok": False,
                "type": "read-after-write",
                "notes": "Bulk save verification skipped because Wix did not return any item ids.",
                "response": response,
            }
        else:
            read_back: list[dict[str, Any]] = []
            verify_ok = True
            for item_id in verify_ids:
                state = _read_current_data_item_state(
                    data_collection_id=data_collection_id,
                    data_item_id=item_id,
                    language=None,
                    token=token,
                    ctx=ctx,
                )
                ok = not state.get("missing") and _extract_data_item_id(state) == item_id
                verify_ok = bool(verify_ok and ok)
                read_back.append({"id": item_id, "ok": ok, "response": state})
            verification = {
                "ok": verify_ok,
                "type": "read-after-write",
                "path": "/wix-data/v2/items/{dataItemId}",
                "method": "GET",
                "requested_ids": verify_ids,
                "response": read_back,
            }

        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-items.bulk-save",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "diff_applied": plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
        }

        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "data-items.bulk-save",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-items.bulk-save.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as e:
        out = {"ok": True, "dry_run": False, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError", "method": "data-items.bulk-save"}
        ctx["audit"].write("data-items.bulk-save.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as e:
        out = {"ok": False, "error": str(e), "error_type": "ValidationError", "method": "data-items.bulk-save"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as e:
        out = {"ok": False, "error": str(e), "error_type": e.__class__.__name__, "method": "data-items.bulk-save"}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_bulk_update(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        data_items = _read_data_items(getattr(args, "data_items_json", None), field="data-items-json")
        explicit_item_ids, has_missing_ids, normalized_data_items = _normalize_bulk_item_ids(data_items)
        if has_missing_ids:
            raise ValidationError("--data-items-json items must include id")

        condition = _read_json_arg(getattr(args, "condition_json", None), field="condition-json")
        if condition is not None and not isinstance(condition, dict):
            raise ValidationError("--condition-json must be a JSON object")

        app_options = _read_optional_json_object(getattr(args, "app_options_json", None), field="app-options-json")
        include_draft_items = bool(getattr(args, "include_draft_items", False))
        return_entity = bool(getattr(args, "return_entity", False))

        selector = _build_bulk_data_items_selector(
            operation="bulk-update",
            data_collection_id=data_collection_id,
            data_item_ids=explicit_item_ids,
        )
        body = _build_data_items_bulk_update_payload(
            data_collection_id=data_collection_id,
            data_items=normalized_data_items,
            condition=condition,
            app_options=app_options,
            include_draft_items=include_draft_items,
            return_entity=return_entity,
        )
        request = {
            "method": "POST",
            "path": "/wix-data/v2/bulk/items/update",
            "body": body,
        }

        if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not ctx.get("plan_in"):
            raise SafetyError(
                "Refused: data-items.bulk-update live apply requires a reviewed saved plan. "
                "First run with --plan-out, review the plan, then rerun with --plan-in --apply --yes."
            )

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-items.bulk-update",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            before_state = _capture_data_item_states(
                data_collection_id=data_collection_id,
                data_item_ids=explicit_item_ids,
                language=None,
                token=token,
                ctx=ctx,
            )
            plan = _build_data_items_write_plan(
                method="data-items.bulk-update",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline_before=before_state,
                proposed_changes=[
                    {
                        "operation": "bulk-update",
                        "item_count": len(normalized_data_items),
                        "data_item_ids": explicit_item_ids,
                        "condition": condition,
                    }
                ],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify explicit ids by rereading them after apply.",
                },
                rollback_notes="No automatic rollback. Bulk update fully replaces existing item data.",
            )

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {"ok": True, "dry_run": True, "method": "data-items.bulk-update", "plan": plan, "plan_out": plan_out}
            ctx["audit"].write("data-items.bulk-update.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            str(ctx.get("plan_in")),
            expected_method="data-items.bulk-update",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        _assert_no_data_item_state_drifts(
            plan=loaded_plan,
            token=token,
            ctx=ctx,
            data_collection_id=data_collection_id,
            data_item_ids=explicit_item_ids,
            language=None,
        )

        current_states = _capture_data_item_states(
            data_collection_id=data_collection_id,
            data_item_ids=explicit_item_ids,
            language=None,
            token=token,
            ctx=ctx,
        )
        missing_ids = [item_id for item_id, state in current_states.items() if state.get("missing")]
        if missing_ids:
            raise SafetyError("Refused: bulk-update target ids do not all exist: " + ", ".join(missing_ids))

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/bulk/items/update",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        verify_ids = list(dict.fromkeys(explicit_item_ids + _extract_bulk_data_item_ids(response)))
        read_back: list[dict[str, Any]] = []
        verify_ok = True
        for item_id in verify_ids:
            state = _read_current_data_item_state(
                data_collection_id=data_collection_id,
                data_item_id=item_id,
                language=None,
                token=token,
                ctx=ctx,
            )
            ok = not state.get("missing") and _extract_data_item_id(state) == item_id
            verify_ok = bool(verify_ok and ok)
            read_back.append({"id": item_id, "ok": ok, "response": state})
        verification = {
            "ok": verify_ok,
            "type": "read-after-write",
            "path": "/wix-data/v2/items/{dataItemId}",
            "method": "GET",
            "requested_ids": verify_ids,
            "response": read_back,
        }

        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-items.bulk-update",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "diff_applied": plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
        }

        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "data-items.bulk-update",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-items.bulk-update.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as e:
        out = {"ok": True, "dry_run": False, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError", "method": "data-items.bulk-update"}
        ctx["audit"].write("data-items.bulk-update.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as e:
        out = {"ok": False, "error": str(e), "error_type": "ValidationError", "method": "data-items.bulk-update"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as e:
        out = {"ok": False, "error": str(e), "error_type": e.__class__.__name__, "method": "data-items.bulk-update"}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_bulk_insert_references(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        data_item_references = _read_data_item_references(
            getattr(args, "data_item_references_json", None),
            field="data-item-references-json",
        )
        return_entity = bool(getattr(args, "return_entity", False))
        consistent_read = True

        selector = _build_bulk_data_item_reference_selector(
            operation="bulk-insert-references",
            data_collection_id=data_collection_id,
            data_item_references=data_item_references,
        )
        body = _build_data_items_bulk_references_payload(
            data_collection_id=data_collection_id,
            data_item_references=data_item_references,
            return_entity=return_entity,
        )
        request = {
            "method": "POST",
            "path": "/wix-data/v2/bulk/items/insert-references",
            "body": body,
        }

        if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not ctx.get("plan_in"):
            raise SafetyError(
                "Refused: data-items.bulk-insert-references live apply requires a reviewed saved plan. "
                "First run with --plan-out, review the plan, then rerun with --plan-in --apply --yes."
            )

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )

        before_state = _capture_reference_states(
            data_collection_id=data_collection_id,
            data_item_references=data_item_references,
            consistent_read=consistent_read,
            token=token,
            ctx=ctx,
        )
        if all(before_state):
            raise SafetyError("Refused: bulk-insert-references would be a no-op because all references already exist")

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-items.bulk-insert-references",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_data_items_write_plan(
                method="data-items.bulk-insert-references",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline_before=before_state,
                proposed_changes=[
                    {
                        "operation": "bulk-insert-references",
                        "reference_count": len(data_item_references),
                    }
                ],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify each reference exists after apply with is-referenced.",
                },
                rollback_notes="No automatic rollback. Reference relationships can be changed again, but no snapshot restore is available.",
            )

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-items.bulk-insert-references",
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("data-items.bulk-insert-references.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            str(ctx.get("plan_in")),
            expected_method="data-items.bulk-insert-references",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        _assert_no_reference_state_drifts(
            plan=loaded_plan,
            token=token,
            ctx=ctx,
            data_collection_id=data_collection_id,
            data_item_references=data_item_references,
            consistent_read=consistent_read,
        )

        current_state = _capture_reference_states(
            data_collection_id=data_collection_id,
            data_item_references=data_item_references,
            consistent_read=consistent_read,
            token=token,
            ctx=ctx,
        )
        if any(current_state):
            raise SafetyError("Refused: bulk-insert-references target refs already exist")

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/bulk/items/insert-references",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        after_state = _capture_reference_states(
            data_collection_id=data_collection_id,
            data_item_references=data_item_references,
            consistent_read=consistent_read,
            token=token,
            ctx=ctx,
        )
        verification = {
            "ok": all(after_state),
            "type": "read-after-write",
            "path": "/wix-data/v2/items/is-referenced",
            "method": "POST",
            "requested": after_state,
            "response": after_state,
        }

        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-items.bulk-insert-references",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "diff_applied": plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
        }

        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "data-items.bulk-insert-references",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-items.bulk-insert-references.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as e:
        out = {"ok": True, "dry_run": False, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError", "method": "data-items.bulk-insert-references"}
        ctx["audit"].write("data-items.bulk-insert-references.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as e:
        out = {"ok": False, "error": str(e), "error_type": "ValidationError", "method": "data-items.bulk-insert-references"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as e:
        out = {"ok": False, "error": str(e), "error_type": e.__class__.__name__, "method": "data-items.bulk-insert-references"}
        ctx["out"].emit(out)
        return 1


def cmd_data_items_bulk_remove_references(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        data_item_references = _read_data_item_references(
            getattr(args, "data_item_references_json", None),
            field="data-item-references-json",
        )
        consistent_read = True

        selector = _build_bulk_data_item_reference_selector(
            operation="bulk-remove-references",
            data_collection_id=data_collection_id,
            data_item_references=data_item_references,
        )
        body = _build_data_items_bulk_references_payload(
            data_collection_id=data_collection_id,
            data_item_references=data_item_references,
            return_entity=False,
        )
        request = {
            "method": "POST",
            "path": "/wix-data/v2/bulk/items/remove-references",
            "body": body,
        }

        if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not ctx.get("plan_in"):
            raise SafetyError(
                "Refused: data-items.bulk-remove-references live apply requires a reviewed saved plan. "
                "First run with --plan-out, review the plan, then rerun with --plan-in --apply --yes."
            )

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )

        before_state = _capture_reference_states(
            data_collection_id=data_collection_id,
            data_item_references=data_item_references,
            consistent_read=consistent_read,
            token=token,
            ctx=ctx,
        )
        if not any(before_state):
            raise SafetyError("Refused: bulk-remove-references would be a no-op because none of the references exist")

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-items.bulk-remove-references",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_data_items_write_plan(
                method="data-items.bulk-remove-references",
                request=request,
                selector=selector,
                ctx=ctx,
                baseline_before=before_state,
                proposed_changes=[
                    {
                        "operation": "bulk-remove-references",
                        "reference_count": len(data_item_references),
                    }
                ],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify each reference is absent after apply with is-referenced.",
                },
                rollback_notes="No automatic rollback. Reference relationships can be changed again, but no snapshot restore is available.",
            )

        if not _should_apply(ctx, requires_ack=False):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-items.bulk-remove-references",
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("data-items.bulk-remove-references.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            str(ctx.get("plan_in")),
            expected_method="data-items.bulk-remove-references",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        _assert_no_reference_state_drifts(
            plan=loaded_plan,
            token=token,
            ctx=ctx,
            data_collection_id=data_collection_id,
            data_item_references=data_item_references,
            consistent_read=consistent_read,
        )

        current_state = _capture_reference_states(
            data_collection_id=data_collection_id,
            data_item_references=data_item_references,
            consistent_read=consistent_read,
            token=token,
            ctx=ctx,
        )
        if not all(current_state):
            raise SafetyError("Refused: bulk-remove-references target refs do not all exist")

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/bulk/items/remove-references",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        after_state = _capture_reference_states(
            data_collection_id=data_collection_id,
            data_item_references=data_item_references,
            consistent_read=consistent_read,
            token=token,
            ctx=ctx,
        )
        verification = {
            "ok": not any(after_state),
            "type": "read-after-write",
            "path": "/wix-data/v2/items/is-referenced",
            "method": "POST",
            "requested": after_state,
            "response": after_state,
        }

        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-items.bulk-remove-references",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "diff_applied": plan.get("proposed_changes") or [],
            "backups": [],
            "rollback_plan": None,
        }

        receipt_out = _receipt_out_if_needed(ctx, receipt=receipt)
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "data-items.bulk-remove-references",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-items.bulk-remove-references.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as e:
        out = {"ok": True, "dry_run": False, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError", "method": "data-items.bulk-remove-references"}
        ctx["audit"].write("data-items.bulk-remove-references.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as e:
        out = {"ok": False, "error": str(e), "error_type": "ValidationError", "method": "data-items.bulk-remove-references"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as e:
        out = {"ok": False, "error": str(e), "error_type": e.__class__.__name__, "method": "data-items.bulk-remove-references"}
        ctx["out"].emit(out)
        return 1
