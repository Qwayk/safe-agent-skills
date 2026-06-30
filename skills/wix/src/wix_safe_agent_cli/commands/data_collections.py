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

_ALLOWED_COLLECTION_ROLES = {"ADMIN", "SITE_MEMBER_AUTHOR", "SITE_MEMBER", "ANYONE"}


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


def _build_list_params(
    *,
    limit: int | None,
    offset: int | None,
    sort_field_name: str | None,
    sort_order: str | None,
    fields: list[str] | None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if limit is not None:
        params["paging.limit"] = int(limit)
    if offset is not None:
        params["paging.offset"] = int(offset)
    if sort_field_name:
        params["sort.fieldName"] = str(sort_field_name)
    if sort_order:
        params["sort.order"] = str(sort_order)
    if fields is not None:
        params["fields"] = fields
    return params


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _http_status_from_error(exc: RuntimeError) -> int | None:
    msg = str(exc)
    parts = msg.split()
    if len(parts) < 2 or parts[0] != "HTTP":
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def _read_collection_field(raw: Any, *, index: int) -> dict[str, Any]:
    value = _read_json_arg(raw, field=f"field-json[{index}]")
    if not isinstance(value, dict):
        raise ValidationError(f"--field-json[{index}] must be a JSON object")
    key = value.get("key")
    field_type = value.get("type")
    if not isinstance(key, str) or not key.strip():
        raise ValidationError(f"--field-json[{index}] must include a non-empty key")
    if not isinstance(field_type, str) or not field_type.strip():
        raise ValidationError(f"--field-json[{index}] must include a non-empty type")
    field: dict[str, Any] = {"key": key.strip(), "type": field_type.strip().upper()}
    display_name = value.get("displayName")
    if display_name is not None:
        if not isinstance(display_name, str) or not display_name.strip():
            raise ValidationError(f"--field-json[{index}].displayName must be a non-empty string when provided")
        field["displayName"] = display_name.strip()
    return field


def _coerce_permission(raw: Any, *, field: str) -> str:
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip().upper()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    if value not in _ALLOWED_COLLECTION_ROLES:
        allowed = ", ".join(sorted(_ALLOWED_COLLECTION_ROLES))
        raise ValidationError(f"--{field} must be one of: {allowed}")
    return value


def _build_collection_selector(*, collection_id: str, operation: str = "create") -> dict[str, Any]:
    return {"kind": "wix-data-collection", "operation": operation, "collection_id": collection_id}


def _extract_collection_object(payload: dict[str, Any] | None, *, data_collection_id: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValidationError("Unexpected collection response shape")
    collection = payload.get("collection", payload)
    if not isinstance(collection, dict):
        raise ValidationError("Unexpected collection response shape")
    if "id" in collection and str(collection.get("id")) != data_collection_id:
        raise ValidationError(f"Collection snapshot id mismatch: expected {data_collection_id}, got {collection.get('id')}")
    return collection


def _normalize_snapshot_collection_payload(collection: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {
        "id": collection.get("id"),
        "revision": collection.get("revision"),
        "fields": collection.get("fields"),
        "permissions": collection.get("permissions"),
    }
    if "displayName" in collection:
        normalized["displayName"] = collection.get("displayName")
    if "displayField" in collection:
        normalized["displayField"] = collection.get("displayField")
    if "plugins" in collection:
        normalized["plugins"] = collection.get("plugins")
    return normalized


def _build_collection_update_plan(
    *,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    before_state: dict[str, Any],
    proposed_changes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    baseline = {
        "env_fingerprint": ctx["cfg"].base_url,
        "selector": selector,
        "before_exists": True,
        "before_state": before_state,
    }
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "data-collections.update",
        "risk_level": "high",
        "risk_reasons": ["cms-data-collection-write", "collection-update"],
        "preconditions": ["env_fingerprint must match", "selector must match", "collection must exist", "revision must be preserved"],
        "selector": selector,
        "request": request,
        "baseline": baseline,
        "proposed_changes": proposed_changes or [{"operation": "update", "collection_id": selector.get("collection_id")}],
        "verification_plan": {"type": "read-after-write", "notes": "Verify by GET with consistentRead=true"},
        "rollback": {"supported": False, "notes": "No rollback available."},
    }


def _build_collection_patch_plan(
    *,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    before_state: dict[str, Any],
    proposed_changes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    baseline = {
        "env_fingerprint": ctx["cfg"].base_url,
        "selector": selector,
        "before_exists": True,
        "before_state": before_state,
    }
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "data-collections.patch",
        "risk_level": "high",
        "risk_reasons": ["cms-data-collection-write", "manage-data-collections", "collection-patch"],
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "collection must exist",
            "patch fields should be explicit",
        ],
        "selector": selector,
        "request": request,
        "baseline": baseline,
        "proposed_changes": proposed_changes or [{"operation": "patch", "collection_id": selector.get("collection_id")}],
        "verification_plan": {"type": "read-after-write", "notes": "Verify by GET with consistentRead=true"},
        "rollback": {"supported": False, "notes": "No rollback available."},
    }


def _assert_no_collection_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    baseline_state = baseline.get("before_state")
    if not isinstance(baseline_state, dict):
        raise SafetyError("Refused: plan missing before-state snapshot")
    if current_state != baseline_state:
        raise SafetyError("Refused: collection changed since plan was created")


def _build_collection_create_plan(
    *,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    proposed_changes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    baseline = {
        "env_fingerprint": ctx["cfg"].base_url,
        "selector": selector,
        "before_exists": False,
    }
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "data-collections.create",
        "risk_level": "high",
        "risk_reasons": ["cms-data-collection-write", "collection-create"],
        "preconditions": ["env_fingerprint must match", "selector must match", "collection must not exist"],
        "selector": selector,
        "request": request,
        "baseline": baseline,
        "proposed_changes": proposed_changes or [{"operation": "create", "collection_id": selector.get("collection_id")}],
        "verification_plan": {"type": "read-after-write", "notes": "Verify by GET with consistentRead=true"},
        "rollback": {"supported": False, "notes": "No rollback available."},
    }


def _build_collection_delete_plan(
    *,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    before_state: dict[str, Any],
    proposed_changes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    baseline = {
        "env_fingerprint": ctx["cfg"].base_url,
        "selector": selector,
        "before_exists": True,
        "before_state": before_state,
    }
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": "data-collections.delete",
        "risk_level": "high",
        "risk_reasons": [
            "cms-data-collection-write",
            "manage-data-collections",
            "collection-delete",
            "irreversible",
        ],
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "collection must exist",
            "before-state snapshot must use consistentRead",
            "collection should be exported/archived before delete",
            "deleted collections can only be restored for limited time",
            "live apply requires --yes and --ack-irreversible",
        ],
        "selector": selector,
        "request": request,
        "baseline": baseline,
        "proposed_changes": proposed_changes or [{"operation": "delete", "collection_id": selector.get("collection_id")}],
        "verification_plan": {
            "type": "read-after-delete",
            "notes": "Read collection via GET with consistentRead=true; 404 means removed",
        },
        "rollback": {"supported": False, "notes": "No rollback available."},
    }


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


def _should_apply(ctx: dict[str, Any], *, requires_ack: bool = False) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="data-collections")


def _request_collection_snapshot(*, data_collection_id: str, token: str, ctx: dict[str, Any]) -> dict[str, Any]:
    params = {"consistentRead": True}
    return _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/wix-data/v2/collections/{data_collection_id}",
        token=token,
        params=params,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )


def _safe_get_collection_for_verification(
    *,
    data_collection_id: str,
    token: str,
    ctx: dict[str, Any],
    allow_not_found: bool,
) -> tuple[dict[str, Any] | None, int | None]:
    try:
        return _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx), None
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if allow_not_found and status == 404:
            return None, 404
        raise


def _collection_exists(*, data_collection_id: str, token: str, ctx: dict[str, Any]) -> bool:
    try:
        _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx)
        return True
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            return False
        raise


def _coerce_collection_update_permissions(
    *,
    current_permissions: dict[str, Any],
    permission_insert: Any,
    permission_update: Any,
    permission_remove: Any,
    permission_read: Any,
) -> dict[str, str]:
    permissions: dict[str, str] = {}
    permission_map = [
        ("insert", permission_insert),
        ("update", permission_update),
        ("remove", permission_remove),
        ("read", permission_read),
    ]
    for key, raw in permission_map:
        if raw is None:
            current_value = current_permissions.get(key)
            if not isinstance(current_value, str) or not current_value.strip():
                raise ValidationError(f"Current collection is missing required permission: {key}")
            permissions[key] = str(current_value).strip().upper()
            continue
        permissions[key] = _coerce_permission(raw, field=f"permission-{key}")
    return permissions


def _coerce_collection_patch_permissions(
    *,
    current_permissions: dict[str, Any],
    permission_insert: Any,
    permission_update: Any,
    permission_remove: Any,
    permission_read: Any,
) -> dict[str, str] | None:
    if all(raw is None for raw in (permission_insert, permission_update, permission_remove, permission_read)):
        return None

    permissions: dict[str, str] = {}
    permission_map = [
        ("insert", permission_insert),
        ("update", permission_update),
        ("remove", permission_remove),
        ("read", permission_read),
    ]
    for key, raw in permission_map:
        if raw is None:
            current_value = current_permissions.get(key)
            if not isinstance(current_value, str) or not current_value.strip():
                raise ValidationError(f"Current collection is missing required permission: {key}")
            permissions[key] = str(current_value).strip().upper()
            continue
        permissions[key] = _coerce_permission(raw, field=f"permission-{key}")
    return permissions


def _coerce_collection_update_fields(
    *,
    raw_fields: Any,
    current_fields: Any,
) -> list[dict[str, Any]]:
    if raw_fields is None:
        if not isinstance(current_fields, list) or len(current_fields) == 0:
            raise ValidationError("Current collection snapshot is missing fields")
        return current_fields
    if not isinstance(raw_fields, list) or len(raw_fields) == 0:
        raise ValidationError("--field-json must be repeated at least once")
    fields = [_read_collection_field(item, index=idx) for idx, item in enumerate(raw_fields)]
    return fields


def _coerce_collection_field_payload(
    *,
    raw_field: Any,
    field: str,
    allow_partial: bool,
) -> dict[str, Any]:
    value = _read_json_arg(raw_field, field=field)
    if not isinstance(value, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    key = value.get("key")
    if not isinstance(key, str) or not key.strip():
        raise ValidationError(f"--{field}[key] must be a non-empty string")
    field_payload: dict[str, Any] = {"key": key.strip()}
    if not allow_partial:
        field_type = value.get("type")
        if not isinstance(field_type, str) or not field_type.strip():
            raise ValidationError(f"--{field}[type] must be a non-empty string")
        field_payload["type"] = field_type.strip().upper()
    elif "type" in value:
        if not isinstance(value.get("type"), str) or not str(value.get("type")).strip():
            raise ValidationError(f"--{field}[type] must be a non-empty string")
        field_payload["type"] = str(value.get("type")).strip().upper()
    for key_name, key_value in value.items():
        if key_name in {"key", "type"}:
            continue
        field_payload[key_name] = key_value
    return field_payload


def _coerce_collection_plugin_payload(*, raw_plugin: Any, field: str) -> dict[str, Any]:
    value = _read_json_arg(raw_plugin, field=field)
    if not isinstance(value, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_plugin_type(raw: Any, field: str) -> str:
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _lookup_current_field(*, fields: Any, key: str) -> dict[str, Any] | None:
    if not isinstance(fields, list):
        return None
    for item in fields:
        if not isinstance(item, dict):
            continue
        if str(item.get("key") or "") == key:
            return item
    return None


def _is_noop_field_update(*, requested: dict[str, Any], current_state: dict[str, Any]) -> bool:
    key = requested.get("key")
    if not isinstance(key, str) or not key.strip():
        return False
    current_field = _lookup_current_field(fields=current_state.get("fields"), key=key)
    if current_field is None:
        return False
    for field_name, field_value in requested.items():
        if current_field.get(field_name) != field_value:
            return False
    return True


def _is_noop_field_update_full(*, requested: dict[str, Any], current_state: dict[str, Any]) -> bool:
    key = requested.get("key")
    if not isinstance(key, str) or not key.strip():
        return False
    current_field = _lookup_current_field(fields=current_state.get("fields"), key=key)
    if current_field is None:
        return False
    return requested == current_field


def _build_collection_field_plan(
    *,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    before_state: dict[str, Any],
    method: str,
    requires_ack: bool = False,
    proposed_changes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    baseline = {
        "env_fingerprint": ctx["cfg"].base_url,
        "selector": selector,
        "before_exists": True,
        "before_state": before_state,
    }
    preconditions = ["env_fingerprint must match", "selector must match", "collection must exist"]
    if requires_ack:
        preconditions.append("live apply requires --ack-irreversible")
    risk_reasons = ["cms-data-collection-write", "collection-field-plugin"]
    if requires_ack:
        risk_reasons.append("irreversible")
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": baseline,
        "proposed_changes": proposed_changes or [{"operation": method, "collection_id": selector.get("collection_id")}],
        "verification_plan": {"type": "read-after-write", "notes": "Verify by GET with consistentRead=true"},
        "rollback": {"supported": False, "notes": "No rollback available."},
    }


def _coerce_collection_patch_request(
    *,
    data_collection_id: str,
    current_state: dict[str, Any],
    display_name: Any,
    display_field: Any,
    permission_insert: Any,
    permission_update: Any,
    permission_remove: Any,
    permission_read: Any,
) -> dict[str, Any]:
    current_permissions = current_state.get("permissions")
    if not isinstance(current_permissions, dict):
        raise ValidationError("Current collection snapshot is missing permissions")

    collection_payload: dict[str, Any] = {"id": data_collection_id}

    requested_display_name = str(display_name or "").strip()
    if requested_display_name:
        collection_payload["displayName"] = requested_display_name

    requested_display_field = str(display_field or "").strip()
    if requested_display_field:
        collection_payload["displayField"] = requested_display_field

    permissions = _coerce_collection_patch_permissions(
        current_permissions=current_permissions,
        permission_insert=permission_insert,
        permission_update=permission_update,
        permission_remove=permission_remove,
        permission_read=permission_read,
    )
    if permissions is not None:
        collection_payload["permissions"] = permissions

    if len(collection_payload) == 1:
        raise SafetyError("Refused: no supported patch fields requested")

    return collection_payload


def _is_noop_collection_patch(*, requested: dict[str, Any], current_state: dict[str, Any]) -> bool:
    for key, value in requested.items():
        if key == "id":
            continue
        if key == "permissions":
            if current_state.get("permissions") != value:
                return False
            continue
        if current_state.get(key) != value:
            return False
    return True


def _coerce_collection_update_request(
    *,
    data_collection_id: str,
    current_state: dict[str, Any],
    raw_fields: Any,
    display_name: Any,
    display_field: Any,
    permission_insert: Any,
    permission_update: Any,
    permission_remove: Any,
    permission_read: Any,
) -> dict[str, Any]:
    revision = current_state.get("revision")
    if not isinstance(revision, str) or not revision.strip():
        raise ValidationError("Current collection snapshot is missing revision")

    fields = _coerce_collection_update_fields(
        raw_fields=raw_fields, current_fields=current_state.get("fields")
    )
    current_permissions = current_state.get("permissions")
    if not isinstance(current_permissions, dict):
        raise ValidationError("Current collection snapshot is missing permissions")
    permissions = _coerce_collection_update_permissions(
        current_permissions=current_permissions,
        permission_insert=permission_insert,
        permission_update=permission_update,
        permission_remove=permission_remove,
        permission_read=permission_read,
    )

    collection_payload: dict[str, Any] = {
        "id": data_collection_id,
        "revision": revision,
        "fields": fields,
        "permissions": permissions,
    }

    requested_display_name = str(display_name or "").strip()
    if requested_display_name:
        collection_payload["displayName"] = requested_display_name
    elif "displayName" in current_state:
        current_display_name = current_state.get("displayName")
        if current_display_name is not None:
            collection_payload["displayName"] = current_display_name

    requested_display_field = str(display_field or "").strip()
    if requested_display_field:
        collection_payload["displayField"] = requested_display_field
    elif "displayField" in current_state:
        current_display_field = current_state.get("displayField")
        if current_display_field is not None:
            collection_payload["displayField"] = current_display_field

    if "plugins" in current_state:
        collection_payload["plugins"] = current_state["plugins"]

    return collection_payload


def _is_noop_update(*, requested: dict[str, Any], current_state: dict[str, Any]) -> bool:
    normalized_current = _normalize_snapshot_collection_payload(current_state)
    return requested == normalized_current


def cmd_data_collections_list(args, ctx) -> int:
    try:
        fields = _read_str_list(getattr(args, "fields_json", None), field="fields-json")
        params = _build_list_params(
            limit=getattr(args, "limit", None),
            offset=getattr(args, "offset", None),
            sort_field_name=getattr(args, "sort_field_name", None),
            sort_order=getattr(args, "sort_order", None),
            fields=fields,
        )
        if bool(getattr(args, "consistent_read", False)):
            params["consistentRead"] = True

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/collections",
            token=token,
            params=params,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "data-collections.list",
            "request": {"method": "GET", "path": "/wix-data/v2/collections", "params": params},
            "response": payload,
        }
        ctx["audit"].write("data-collections.list", out)
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


def cmd_data_collections_get(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        fields = _read_str_list(getattr(args, "fields_json", None), field="fields-json")
        params: dict[str, Any] = {}
        if fields is not None:
            params["fields"] = fields
        if bool(getattr(args, "consistent_read", False)):
            params["consistentRead"] = True

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=f"/wix-data/v2/collections/{data_collection_id}",
            token=token,
            params=params,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "data-collections.get",
            "request": {"method": "GET", "path": f"/wix-data/v2/collections/{data_collection_id}", "params": params},
            "response": payload,
        }
        ctx["audit"].write("data-collections.get", out)
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


def cmd_data_collections_delete(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        snapshot_payload = _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx)
        current_state = _extract_collection_object(snapshot_payload, data_collection_id=data_collection_id)

        selector = _build_collection_selector(collection_id=data_collection_id, operation="delete")
        request = {
            "method": "DELETE",
            "path": f"/wix-data/v2/collections/{data_collection_id}",
        }

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-collections.delete",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_collection_delete_plan(
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=current_state,
                proposed_changes=[{"operation": "delete", "collection_id": data_collection_id}],
            )

        if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not bool(ctx.get("ack_irreversible")):
            raise SafetyError("Refused: live collection delete requires --ack-irreversible")

        if not _should_apply(ctx, requires_ack=True):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-collections.delete",
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("data-collections.delete.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            str(ctx.get("plan_in")),
            expected_method="data-collections.delete",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        _assert_no_collection_drift(plan=loaded_plan, current_state=current_state)

        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/wix-data/v2/collections/{data_collection_id}",
            token=token,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        verification_payload, verification_status = _safe_get_collection_for_verification(
            data_collection_id=data_collection_id,
            token=token,
            ctx=ctx,
            allow_not_found=True,
        )
        if verification_status == 404:
            verification = {
                "ok": True,
                "type": "read-after-delete",
                "path": f"/wix-data/v2/collections/{data_collection_id}",
                "method": "GET",
                "removed": True,
                "notes": "Collection not found after delete (consistent with 404)",
            }
        else:
            verification = {
                "ok": False,
                "type": "read-after-delete",
                "path": f"/wix-data/v2/collections/{data_collection_id}",
                "method": "GET",
                "response": verification_payload,
                "removed": False,
                "notes": "Collection still exists after delete",
            }

        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-collections.delete",
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
            "method": "data-collections.delete",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-collections.delete.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": not bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "data-collections.delete",
        }
        ctx["audit"].write("data-collections.delete.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-collections.delete"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            out = {
                "ok": True,
                "dry_run": not bool(ctx.get("apply")),
                "refused": True,
                "reasons": [f"Refused: collection does not exist: {data_collection_id}"],
                "refusal_type": "SafetyError",
                "method": "data-collections.delete",
            }
            ctx["audit"].write("data-collections.delete.refused", out)
            ctx["out"].emit(out)
            return 0
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "data-collections.delete",
        }
        ctx["out"].emit(out)
        return 1


def cmd_data_collections_update(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        snapshot_payload = _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx)
        current_state = _extract_collection_object(snapshot_payload, data_collection_id=data_collection_id)

        collection_payload = _coerce_collection_update_request(
            data_collection_id=data_collection_id,
            current_state=current_state,
            raw_fields=getattr(args, "field_json", None),
            display_name=getattr(args, "display_name", None),
            display_field=getattr(args, "display_field", None),
            permission_insert=getattr(args, "permission_insert", None),
            permission_update=getattr(args, "permission_update", None),
            permission_remove=getattr(args, "permission_remove", None),
            permission_read=getattr(args, "permission_read", None),
        )

        request_body = {"collection": collection_payload}
        request = {
            "method": "PUT",
            "path": "/wix-data/v2/collections",
            "body": request_body,
        }
        selector = _build_collection_selector(collection_id=data_collection_id, operation="update")

        if _is_noop_update(requested=collection_payload, current_state=current_state):
            raise SafetyError("Refused: no material changes requested")

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-collections.update",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_collection_update_plan(
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=current_state,
                proposed_changes=[{"operation": "update", "collection_id": data_collection_id}],
            )

        if not _should_apply(ctx):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-collections.update",
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("data-collections.update.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            str(ctx.get("plan_in")),
            expected_method="data-collections.update",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        _assert_no_collection_drift(plan=loaded_plan, current_state=current_state)

        response = _request_json(
            method="PUT",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/collections",
            token=token,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        verification = {
            "ok": True,
            "type": "read-after-write",
            "path": f"/wix-data/v2/collections/{data_collection_id}",
            "method": "GET",
            "response": _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx),
        }
        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-collections.update",
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
            "method": "data-collections.update",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-collections.update.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": not bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "data-collections.update",
        }
        ctx["audit"].write("data-collections.update.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-collections.update"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            out = {
                "ok": True,
                "dry_run": not bool(ctx.get("apply")),
                "refused": True,
                "reasons": [f"Refused: collection does not exist: {data_collection_id}"],
                "refusal_type": "SafetyError",
                "method": "data-collections.update",
            }
            ctx["audit"].write("data-collections.update.refused", out)
            ctx["out"].emit(out)
            return 0
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "data-collections.update",
        }
        ctx["out"].emit(out)
        return 1


def cmd_data_collections_patch(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        snapshot_payload = _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx)
        current_state = _extract_collection_object(snapshot_payload, data_collection_id=data_collection_id)

        collection_payload = _coerce_collection_patch_request(
            data_collection_id=data_collection_id,
            current_state=current_state,
            display_name=getattr(args, "display_name", None),
            display_field=getattr(args, "display_field", None),
            permission_insert=getattr(args, "permission_insert", None),
            permission_update=getattr(args, "permission_update", None),
            permission_remove=getattr(args, "permission_remove", None),
            permission_read=getattr(args, "permission_read", None),
        )

        request_body = {"dataCollection": collection_payload}
        request = {
            "method": "PATCH",
            "path": f"/wix-data/v2/collections/{data_collection_id}",
            "body": request_body,
        }
        selector = _build_collection_selector(collection_id=data_collection_id, operation="patch")

        if _is_noop_collection_patch(requested=collection_payload, current_state=current_state):
            raise SafetyError("Refused: no material changes requested")

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-collections.patch",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_collection_patch_plan(
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=current_state,
                proposed_changes=[{"operation": "patch", "collection_id": data_collection_id}],
            )

        if not _should_apply(ctx):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-collections.patch",
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("data-collections.patch.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            str(ctx.get("plan_in")),
            expected_method="data-collections.patch",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        _assert_no_collection_drift(plan=loaded_plan, current_state=current_state)

        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/wix-data/v2/collections/{data_collection_id}",
            token=token,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        verification = {
            "ok": True,
            "type": "read-after-write",
            "path": f"/wix-data/v2/collections/{data_collection_id}",
            "method": "GET",
            "response": _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx),
        }
        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-collections.patch",
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
            "method": "data-collections.patch",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-collections.patch.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": not bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "data-collections.patch",
        }
        ctx["audit"].write("data-collections.patch.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-collections.patch"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            out = {
                "ok": True,
                "dry_run": not bool(ctx.get("apply")),
                "refused": True,
                "reasons": [f"Refused: collection does not exist: {data_collection_id}"],
                "refusal_type": "SafetyError",
                "method": "data-collections.patch",
            }
            ctx["audit"].write("data-collections.patch.refused", out)
            ctx["out"].emit(out)
            return 0
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-collections.patch"}
        ctx["out"].emit(out)
        return 1


def cmd_data_collections_create_field(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        field = _coerce_collection_field_payload(
            raw_field=getattr(args, "field_json", None), field="field-json", allow_partial=False
        )
        request_body = {
            "dataCollectionId": data_collection_id,
            "field": field,
        }
        request = {
            "method": "POST",
            "path": "/wix-data/v2/collections/create-field",
            "body": request_body,
        }
        selector = _build_collection_selector(collection_id=data_collection_id, operation="create-field")
        should_apply = _should_apply(ctx)
        if not should_apply:
            token = _resolve_access_token(
                cfg=ctx["cfg"],
                env_file=str(ctx["env_file"]),
                verbose=bool(ctx.get("verbose")),
            )
            snapshot_payload = _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx)
            current_state = _extract_collection_object(snapshot_payload, data_collection_id=data_collection_id)

            plan_in = ctx.get("plan_in")
            if plan_in:
                plan = _load_plan(
                    str(plan_in),
                    expected_method="data-collections.create-field",
                    expected_selector=selector,
                    ctx=ctx,
                )
            else:
                plan = _build_collection_field_plan(
                    request=request,
                    selector=selector,
                    ctx=ctx,
                    before_state=current_state,
                    method="data-collections.create-field",
                    proposed_changes=[{"operation": "create_field", "collection_id": data_collection_id}],
                )
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-collections.create-field",
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("data-collections.create-field.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        snapshot_payload = _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx)
        current_state = _extract_collection_object(snapshot_payload, data_collection_id=data_collection_id)

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-collections.create-field",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_collection_field_plan(
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=current_state,
                method="data-collections.create-field",
                proposed_changes=[{"operation": "create_field", "collection_id": data_collection_id}],
            )
        _assert_no_collection_drift(plan=plan, current_state=current_state)

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/collections/create-field",
            token=token,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = {
            "ok": True,
            "type": "read-after-write",
            "path": f"/wix-data/v2/collections/{data_collection_id}",
            "method": "GET",
            "response": _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx),
        }
        out = {
            "ok": True,
            "dry_run": False,
            "method": "data-collections.create-field",
            "receipt": {
                "tool": ctx.get("tool") or "wix-safe-agent-cli",
                "version": ctx.get("tool_version") or None,
                "applied_at_utc": _utc_now(),
                "env_fingerprint": ctx["cfg"].base_url,
                "command": ctx.get("command_str") or None,
                "method": "data-collections.create-field",
                "selector": selector,
                "request": request,
                "response": response,
                "changed": True,
                "verification": verification,
                "diff_applied": plan.get("proposed_changes") or [],
                "backups": [],
                "rollback_plan": None,
            },
            "receipt_out": _receipt_out_if_needed(
                ctx,
                receipt={
                    "tool": ctx.get("tool") or "wix-safe-agent-cli",
                    "version": ctx.get("tool_version") or None,
                    "applied_at_utc": _utc_now(),
                    "env_fingerprint": ctx["cfg"].base_url,
                    "command": ctx.get("command_str") or None,
                    "method": "data-collections.create-field",
                    "selector": selector,
                    "request": request,
                    "response": response,
                    "changed": True,
                    "verification": verification,
                    "diff_applied": plan.get("proposed_changes") or [],
                    "backups": [],
                    "rollback_plan": None,
                },
            ),
        }
        ctx["audit"].write("data-collections.create-field.apply", {"receipt_out": out.get("receipt_out")})
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": not bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "data-collections.create-field",
        }
        ctx["audit"].write("data-collections.create-field.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-collections.create-field"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            out = {
                "ok": True,
                "dry_run": not bool(ctx.get("apply")),
                "refused": True,
                "reasons": [f"Refused: collection does not exist: {data_collection_id}"],
                "refusal_type": "SafetyError",
                "method": "data-collections.create-field",
            }
            ctx["audit"].write("data-collections.create-field.refused", out)
            ctx["out"].emit(out)
            return 0
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "data-collections.create-field",
        }
        ctx["out"].emit(out)
        return 1


def cmd_data_collections_update_field(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        field = _coerce_collection_field_payload(
            raw_field=getattr(args, "field_json", None), field="field-json", allow_partial=False
        )
        request_body = {
            "dataCollectionId": data_collection_id,
            "field": field,
        }
        request = {
            "method": "POST",
            "path": "/wix-data/v2/collections/update-field",
            "body": request_body,
        }
        selector = _build_collection_selector(collection_id=data_collection_id, operation="update-field")

        should_apply = _should_apply(ctx)
        if not should_apply:
            token = _resolve_access_token(
                cfg=ctx["cfg"],
                env_file=str(ctx["env_file"]),
                verbose=bool(ctx.get("verbose")),
            )
            snapshot_payload = _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx)
            current_state = _extract_collection_object(snapshot_payload, data_collection_id=data_collection_id)
            if _is_noop_field_update_full(requested=field, current_state=current_state):
                raise SafetyError("Refused: no material changes requested")

            plan_in = ctx.get("plan_in")
            if plan_in:
                plan = _load_plan(
                    str(plan_in),
                    expected_method="data-collections.update-field",
                    expected_selector=selector,
                    ctx=ctx,
                )
            else:
                plan = _build_collection_field_plan(
                    request=request,
                    selector=selector,
                    ctx=ctx,
                    before_state=current_state,
                    method="data-collections.update-field",
                    proposed_changes=[{"operation": "update_field", "collection_id": data_collection_id}],
                )
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-collections.update-field",
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("data-collections.update-field.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        snapshot_payload = _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx)
        current_state = _extract_collection_object(snapshot_payload, data_collection_id=data_collection_id)
        if _is_noop_field_update_full(requested=field, current_state=current_state):
            raise SafetyError("Refused: no material changes requested")

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-collections.update-field",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_collection_field_plan(
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=current_state,
                method="data-collections.update-field",
                proposed_changes=[{"operation": "update_field", "collection_id": data_collection_id}],
            )
        _assert_no_collection_drift(plan=plan, current_state=current_state)

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/collections/update-field",
            token=token,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = {
            "ok": True,
            "type": "read-after-write",
            "path": f"/wix-data/v2/collections/{data_collection_id}",
            "method": "GET",
            "response": _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx),
        }
        out = {
            "ok": True,
            "dry_run": False,
            "method": "data-collections.update-field",
            "receipt": {
                "tool": ctx.get("tool") or "wix-safe-agent-cli",
                "version": ctx.get("tool_version") or None,
                "applied_at_utc": _utc_now(),
                "env_fingerprint": ctx["cfg"].base_url,
                "command": ctx.get("command_str") or None,
                "method": "data-collections.update-field",
                "selector": selector,
                "request": request,
                "response": response,
                "changed": True,
                "verification": verification,
                "diff_applied": plan.get("proposed_changes") or [],
                "backups": [],
                "rollback_plan": None,
            },
            "receipt_out": _receipt_out_if_needed(
                ctx,
                receipt={
                    "tool": ctx.get("tool") or "wix-safe-agent-cli",
                    "version": ctx.get("tool_version") or None,
                    "applied_at_utc": _utc_now(),
                    "env_fingerprint": ctx["cfg"].base_url,
                    "command": ctx.get("command_str") or None,
                    "method": "data-collections.update-field",
                    "selector": selector,
                    "request": request,
                    "response": response,
                    "changed": True,
                    "verification": verification,
                    "diff_applied": plan.get("proposed_changes") or [],
                    "backups": [],
                    "rollback_plan": None,
                },
            ),
        }
        ctx["audit"].write("data-collections.update-field.apply", {"receipt_out": out.get("receipt_out")})
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": not bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "data-collections.update-field",
        }
        ctx["audit"].write("data-collections.update-field.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": "ValidationError",
            "method": "data-collections.update-field",
        }
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            out = {
                "ok": True,
                "dry_run": not bool(ctx.get("apply")),
                "refused": True,
                "reasons": [f"Refused: collection does not exist: {data_collection_id}"],
                "refusal_type": "SafetyError",
                "method": "data-collections.update-field",
            }
            ctx["audit"].write("data-collections.update-field.refused", out)
            ctx["out"].emit(out)
            return 0
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "data-collections.update-field",
        }
        ctx["out"].emit(out)
        return 1


def cmd_data_collections_patch_field(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        field = _coerce_collection_field_payload(
            raw_field=getattr(args, "field_json", None), field="field-json", allow_partial=True
        )
        request_body = {"field": field}
        request = {
            "method": "PATCH",
            "path": f"/wix-data/v2/collections/{data_collection_id}/patch-field",
            "body": request_body,
        }
        selector = _build_collection_selector(collection_id=data_collection_id, operation="patch-field")

        should_apply = _should_apply(ctx)
        if not should_apply:
            token = _resolve_access_token(
                cfg=ctx["cfg"],
                env_file=str(ctx["env_file"]),
                verbose=bool(ctx.get("verbose")),
            )
            snapshot_payload = _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx)
            current_state = _extract_collection_object(snapshot_payload, data_collection_id=data_collection_id)
            if _is_noop_field_update(requested=field, current_state=current_state):
                raise SafetyError("Refused: no material changes requested")

            plan_in = ctx.get("plan_in")
            if plan_in:
                plan = _load_plan(
                    str(plan_in),
                    expected_method="data-collections.patch-field",
                    expected_selector=selector,
                    ctx=ctx,
                )
            else:
                plan = _build_collection_field_plan(
                    request=request,
                    selector=selector,
                    ctx=ctx,
                    before_state=current_state,
                    method="data-collections.patch-field",
                    proposed_changes=[{"operation": "patch_field", "collection_id": data_collection_id}],
                )
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-collections.patch-field",
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("data-collections.patch-field.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        snapshot_payload = _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx)
        current_state = _extract_collection_object(snapshot_payload, data_collection_id=data_collection_id)
        if _is_noop_field_update(requested=field, current_state=current_state):
            raise SafetyError("Refused: no material changes requested")

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-collections.patch-field",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_collection_field_plan(
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=current_state,
                method="data-collections.patch-field",
                proposed_changes=[{"operation": "patch_field", "collection_id": data_collection_id}],
            )
        _assert_no_collection_drift(plan=plan, current_state=current_state)

        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/wix-data/v2/collections/{data_collection_id}/patch-field",
            token=token,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = {
            "ok": True,
            "type": "read-after-write",
            "path": f"/wix-data/v2/collections/{data_collection_id}",
            "method": "GET",
            "response": _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx),
        }
        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-collections.patch-field",
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
            "method": "data-collections.patch-field",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-collections.patch-field.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": not bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "data-collections.patch-field",
        }
        ctx["audit"].write("data-collections.patch-field.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-collections.patch-field"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            out = {
                "ok": True,
                "dry_run": not bool(ctx.get("apply")),
                "refused": True,
                "reasons": [f"Refused: collection does not exist: {data_collection_id}"],
                "refusal_type": "SafetyError",
                "method": "data-collections.patch-field",
            }
            ctx["audit"].write("data-collections.patch-field.refused", out)
            ctx["out"].emit(out)
            return 0
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "data-collections.patch-field",
        }
        ctx["out"].emit(out)
        return 1


def cmd_data_collections_delete_field(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")
        field_key = str(getattr(args, "field_key", "") or "").strip()
        if not field_key:
            raise ValidationError("--field-key cannot be empty")

        if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not bool(ctx.get("ack_irreversible")):
            raise SafetyError("Refused: delete-field requires --ack-irreversible")

        request_body = {
            "dataCollectionId": data_collection_id,
            "fieldKey": field_key,
        }
        request = {
            "method": "POST",
            "path": "/wix-data/v2/collections/delete-field",
            "body": request_body,
        }
        selector = _build_collection_selector(collection_id=data_collection_id, operation="delete-field")
        should_apply = _should_apply(ctx, requires_ack=True)

        if not should_apply:
            token = _resolve_access_token(
                cfg=ctx["cfg"],
                env_file=str(ctx["env_file"]),
                verbose=bool(ctx.get("verbose")),
            )
            snapshot_payload = _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx)
            current_state = _extract_collection_object(snapshot_payload, data_collection_id=data_collection_id)

            if _lookup_current_field(fields=current_state.get("fields"), key=field_key) is None:
                raise SafetyError(f"Refused: field does not exist in collection: {field_key}")

            plan_in = ctx.get("plan_in")
            if plan_in:
                plan = _load_plan(
                    str(plan_in),
                    expected_method="data-collections.delete-field",
                    expected_selector=selector,
                    ctx=ctx,
                )
            else:
                plan = _build_collection_field_plan(
                    request=request,
                    selector=selector,
                    ctx=ctx,
                    before_state=current_state,
                    method="data-collections.delete-field",
                    requires_ack=True,
                    proposed_changes=[{"operation": "delete_field", "collection_id": data_collection_id}],
                )
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-collections.delete-field",
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("data-collections.delete-field.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        snapshot_payload = _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx)
        current_state = _extract_collection_object(snapshot_payload, data_collection_id=data_collection_id)
        if _lookup_current_field(fields=current_state.get("fields"), key=field_key) is None:
            raise SafetyError(f"Refused: field does not exist in collection: {field_key}")

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-collections.delete-field",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_collection_field_plan(
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=current_state,
                method="data-collections.delete-field",
                requires_ack=True,
                proposed_changes=[{"operation": "delete_field", "collection_id": data_collection_id}],
            )
        _assert_no_collection_drift(plan=plan, current_state=current_state)

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/collections/delete-field",
            token=token,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = {
            "ok": True,
            "type": "read-after-write",
            "path": f"/wix-data/v2/collections/{data_collection_id}",
            "method": "GET",
            "response": _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx),
        }
        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-collections.delete-field",
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
            "method": "data-collections.delete-field",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-collections.delete-field.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": not bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "data-collections.delete-field",
        }
        ctx["audit"].write("data-collections.delete-field.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-collections.delete-field"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            out = {
                "ok": True,
                "dry_run": not bool(ctx.get("apply")),
                "refused": True,
                "reasons": [f"Refused: collection does not exist: {data_collection_id}"],
                "refusal_type": "SafetyError",
                "method": "data-collections.delete-field",
            }
            ctx["audit"].write("data-collections.delete-field.refused", out)
            ctx["out"].emit(out)
            return 0
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "data-collections.delete-field",
        }
        ctx["out"].emit(out)
        return 1


def cmd_data_collections_add_plugin(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        plugin = _coerce_collection_plugin_payload(raw_plugin=getattr(args, "plugin_json", None), field="plugin-json")
        request_body = {
            "dataCollectionId": data_collection_id,
            "plugin": plugin,
        }
        request = {
            "method": "POST",
            "path": "/wix-data/v2/collections/add-plugin",
            "body": request_body,
        }
        selector = _build_collection_selector(collection_id=data_collection_id, operation="add-plugin")

        should_apply = _should_apply(ctx)
        if not should_apply:
            token = _resolve_access_token(
                cfg=ctx["cfg"],
                env_file=str(ctx["env_file"]),
                verbose=bool(ctx.get("verbose")),
            )
            snapshot_payload = _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx)
            current_state = _extract_collection_object(snapshot_payload, data_collection_id=data_collection_id)

            plan_in = ctx.get("plan_in")
            if plan_in:
                plan = _load_plan(
                    str(plan_in),
                    expected_method="data-collections.add-plugin",
                    expected_selector=selector,
                    ctx=ctx,
                )
            else:
                plan = _build_collection_field_plan(
                    request=request,
                    selector=selector,
                    ctx=ctx,
                    before_state=current_state,
                    method="data-collections.add-plugin",
                    proposed_changes=[{"operation": "add_plugin", "collection_id": data_collection_id}],
                )
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-collections.add-plugin",
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("data-collections.add-plugin.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        snapshot_payload = _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx)
        current_state = _extract_collection_object(snapshot_payload, data_collection_id=data_collection_id)

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-collections.add-plugin",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_collection_field_plan(
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=current_state,
                method="data-collections.add-plugin",
                proposed_changes=[{"operation": "add_plugin", "collection_id": data_collection_id}],
            )
        _assert_no_collection_drift(plan=plan, current_state=current_state)

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/collections/add-plugin",
            token=token,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = {
            "ok": True,
            "type": "read-after-write",
            "path": f"/wix-data/v2/collections/{data_collection_id}",
            "method": "GET",
            "response": _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx),
        }
        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-collections.add-plugin",
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
            "method": "data-collections.add-plugin",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-collections.add-plugin.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": not bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "data-collections.add-plugin",
        }
        ctx["audit"].write("data-collections.add-plugin.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-collections.add-plugin"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            out = {
                "ok": True,
                "dry_run": not bool(ctx.get("apply")),
                "refused": True,
                "reasons": [f"Refused: collection does not exist: {data_collection_id}"],
                "refusal_type": "SafetyError",
                "method": "data-collections.add-plugin",
            }
            ctx["audit"].write("data-collections.add-plugin.refused", out)
            ctx["out"].emit(out)
            return 0
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "data-collections.add-plugin",
        }
        ctx["out"].emit(out)
        return 1


def cmd_data_collections_delete_plugin(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "data_collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --data-collection-id")

        plugin_type = _coerce_plugin_type(getattr(args, "plugin_type", None), field="plugin-type")
        request_body = {
            "dataCollectionId": data_collection_id,
            "pluginType": plugin_type,
        }
        request = {
            "method": "POST",
            "path": "/wix-data/v2/collections/delete-plugin",
            "body": request_body,
        }
        selector = _build_collection_selector(collection_id=data_collection_id, operation="delete-plugin")

        should_apply = _should_apply(ctx)
        if not should_apply:
            token = _resolve_access_token(
                cfg=ctx["cfg"],
                env_file=str(ctx["env_file"]),
                verbose=bool(ctx.get("verbose")),
            )
            snapshot_payload = _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx)
            current_state = _extract_collection_object(snapshot_payload, data_collection_id=data_collection_id)

            plan_in = ctx.get("plan_in")
            if plan_in:
                plan = _load_plan(
                    str(plan_in),
                    expected_method="data-collections.delete-plugin",
                    expected_selector=selector,
                    ctx=ctx,
                )
            else:
                plan = _build_collection_field_plan(
                    request=request,
                    selector=selector,
                    ctx=ctx,
                    before_state=current_state,
                    method="data-collections.delete-plugin",
                    proposed_changes=[{"operation": "delete_plugin", "collection_id": data_collection_id}],
                )
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-collections.delete-plugin",
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("data-collections.delete-plugin.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        snapshot_payload = _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx)
        current_state = _extract_collection_object(snapshot_payload, data_collection_id=data_collection_id)

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-collections.delete-plugin",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_collection_field_plan(
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=current_state,
                method="data-collections.delete-plugin",
                proposed_changes=[{"operation": "delete_plugin", "collection_id": data_collection_id}],
            )
        _assert_no_collection_drift(plan=plan, current_state=current_state)

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/collections/delete-plugin",
            token=token,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = {
            "ok": True,
            "type": "read-after-write",
            "path": f"/wix-data/v2/collections/{data_collection_id}",
            "method": "GET",
            "response": _request_collection_snapshot(data_collection_id=data_collection_id, token=token, ctx=ctx),
        }
        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-collections.delete-plugin",
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
            "method": "data-collections.delete-plugin",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-collections.delete-plugin.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": not bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "data-collections.delete-plugin",
        }
        ctx["audit"].write("data-collections.delete-plugin.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-collections.delete-plugin"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            out = {
                "ok": True,
                "dry_run": not bool(ctx.get("apply")),
                "refused": True,
                "reasons": [f"Refused: collection does not exist: {data_collection_id}"],
                "refusal_type": "SafetyError",
                "method": "data-collections.delete-plugin",
            }
            ctx["audit"].write("data-collections.delete-plugin.refused", out)
            ctx["out"].emit(out)
            return 0
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "data-collections.delete-plugin",
        }
        ctx["out"].emit(out)
        return 1


def cmd_data_collections_create(args, ctx) -> int:
    try:
        data_collection_id = str(getattr(args, "collection_id", "") or "").strip()
        if not data_collection_id:
            raise ValidationError("Missing --collection-id")

        raw_fields = getattr(args, "field_json", None)
        if not isinstance(raw_fields, list) or len(raw_fields) == 0:
            raise ValidationError("--field-json is required and must be repeated at least once")
        fields = [_read_collection_field(item, index=idx) for idx, item in enumerate(raw_fields)]

        permissions = {
            "insert": _coerce_permission(getattr(args, "permission_insert", "ADMIN"), field="permission-insert"),
            "update": _coerce_permission(getattr(args, "permission_update", "ADMIN"), field="permission-update"),
            "remove": _coerce_permission(getattr(args, "permission_remove", "ADMIN"), field="permission-remove"),
            "read": _coerce_permission(getattr(args, "permission_read", "ADMIN"), field="permission-read"),
        }

        collection_payload: dict[str, Any] = {
            "id": data_collection_id,
            "fields": fields,
            "permissions": permissions,
        }
        display_name = str(getattr(args, "display_name", "") or "").strip()
        if display_name:
            collection_payload["displayName"] = display_name
        display_field = str(getattr(args, "display_field", "") or "").strip()
        if display_field:
            collection_payload["displayField"] = display_field

        request_body = {"collection": collection_payload}
        request = {
            "method": "POST",
            "path": "/wix-data/v2/collections",
            "body": request_body,
        }
        selector = _build_collection_selector(collection_id=data_collection_id)
        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        collection_exists = _collection_exists(data_collection_id=data_collection_id, token=token, ctx=ctx)

        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-collections.create",
                expected_selector=selector,
                ctx=ctx,
            )
            if collection_exists:
                raise SafetyError(f"Refused: collection already exists: {data_collection_id}")
        else:
            plan = _build_collection_create_plan(
                request=request,
                selector=selector,
                ctx=ctx,
                proposed_changes=[{"operation": "create", "collection": collection_payload}],
            )

        if collection_exists:
            raise SafetyError(f"Refused: collection already exists: {data_collection_id}")

        if not _should_apply(ctx):
            plan_out = _plan_out_if_needed(ctx, plan=plan)
            out = {
                "ok": True,
                "dry_run": True,
                "method": "data-collections.create",
                "plan": plan,
                "plan_out": plan_out,
            }
            ctx["audit"].write("data-collections.create.plan", {"plan_out": plan_out})
            ctx["out"].emit(out)
            return 0

        if plan_in:
            plan = _load_plan(
                str(plan_in),
                expected_method="data-collections.create",
                expected_selector=selector,
                ctx=ctx,
            )

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/collections",
            token=token,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = {
            "ok": True,
            "type": "read-after-write",
            "path": f"/wix-data/v2/collections/{data_collection_id}",
            "method": "GET",
            "response": _request_collection_snapshot(
                data_collection_id=data_collection_id,
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
            "method": "data-collections.create",
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
            "method": "data-collections.create",
            "receipt": receipt,
            "receipt_out": receipt_out,
        }
        ctx["audit"].write("data-collections.create.apply", {"receipt_out": receipt_out})
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {
            "ok": True,
            "dry_run": not bool(ctx.get("apply")),
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": "data-collections.create",
        }
        ctx["audit"].write("data-collections.create.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-collections.create"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-collections.create"}
        ctx["out"].emit(out)
        return 1
