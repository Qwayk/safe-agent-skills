from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested


def _read_json_arg(raw: Any, field: str) -> Any:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
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


def _coerce_text(raw: Any, *, field: str) -> str:
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_optional_int(raw: Any, *, field: str) -> int | None:
    if raw is None:
        return None
    if not isinstance(raw, int):
        raise ValidationError(f"--{field} must be an integer")
    return raw


def _resolve_indexes_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="data-indexes",
    )
    return auth["headers"], auth["mode"]


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
    params: dict[str, Any] | None,
    json_body: dict[str, Any] | None,
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
        request_headers["Content-Type"] = "application/json"

    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
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


def _normalize_index_field(raw: Any, *, field: str, allow_order: bool = True) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    path = _coerce_text(raw.get("path"), field=f"{field}.path")
    normalized: dict[str, Any] = {"path": path}
    order_raw = raw.get("order")
    if order_raw is not None:
        if not allow_order:
            raise ValidationError(f"--{field}.order is not supported here")
        if not isinstance(order_raw, str):
            raise ValidationError(f"--{field}.order must be a string when provided")
        order = order_raw.strip().upper()
        if order not in {"ASC", "DESC"}:
            raise ValidationError(f"--{field}.order must be ASC or DESC")
        normalized["order"] = order
    return normalized


def _coerce_index_payload(raw: Any, *, field: str) -> dict[str, Any]:
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")

    name = _coerce_text(value.get("name"), field=f"{field}.name")
    fields_raw = value.get("fields")
    if not isinstance(fields_raw, list):
        raise ValidationError(f"--{field}.fields must be a JSON array")
    if not fields_raw:
        raise ValidationError(f"--{field}.fields cannot be empty")
    if len(fields_raw) > 3:
        raise ValidationError("An index can have at most 3 fields")

    unique = value.get("unique")
    if unique is not None and not isinstance(unique, bool):
        raise ValidationError(f"--{field}.unique must be a boolean when provided")

    normalized_fields = [_normalize_index_field(item, field=f"{field}.fields[{idx}]") for idx, item in enumerate(fields_raw)]
    if unique and len(normalized_fields) > 1:
        raise ValidationError("Unique indexes can have only 1 field")

    normalized = dict(value)
    normalized["name"] = name
    normalized["fields"] = normalized_fields
    if unique is not None:
        normalized["unique"] = unique
    return normalized


def _extract_indexes(payload: dict[str, Any], *, operation: str) -> list[dict[str, Any]]:
    indexes = payload.get("indexes")
    if not isinstance(indexes, list):
        indexes = payload.get("dataIndexes")
    if not isinstance(indexes, list):
        raise ValidationError(f"{operation} response did not include an indexes array")
    normalized: list[dict[str, Any]] = []
    for item in indexes:
        if isinstance(item, dict):
            normalized.append(item)
    return normalized


def _find_index_by_name(indexes: list[dict[str, Any]], *, index_name: str) -> dict[str, Any] | None:
    for item in indexes:
        if str(item.get("name") or "").strip() == index_name:
            return item
    return None


def _index_status(index: dict[str, Any]) -> str:
    return str(index.get("status") or "").strip().upper()


def _index_source(index: dict[str, Any]) -> str:
    source = index.get("source")
    if source is None:
        source = index.get("kind")
    return str(source or "").strip().upper()


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    before_state: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    verification_plan: dict[str, Any],
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": ["cms-data-index-write", "manage-data-indexes"],
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "apply requires --plan-in, --apply, and --yes",
        ],
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        },
        "state_capture": {
            "before_state_available": True,
            "notes": "Captured the current index list before planning.",
        },
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "rollback": {
            "supported": False,
            "notes": "No automatic rollback. Use the saved before-state only as a manual reference.",
        },
    }


def _load_plan(
    *,
    plan_in: str | None,
    expected_method: str,
    expected_selector: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan.get("method") or "") != expected_method:
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    return plan


def _assert_plan_state_matches(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: index list changed since the plan was created")


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


def _should_apply(ctx: dict[str, Any]) -> bool:
    return reviewed_plan_apply_requested(ctx, command_label="data-indexes")


def _list_indexes(
    *,
    data_collection_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
    limit: int | None = None,
    offset: int | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {"dataCollectionId": data_collection_id}
    if limit is not None:
        params["paging.limit"] = int(limit)
    if offset is not None:
        params["paging.offset"] = int(offset)
    return _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path="/wix-data/v2/indexes",
        headers=headers,
        params=params,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )


def _refuse_system_index(index_name: str) -> SafetyError:
    return SafetyError(f"Refused: index {index_name} is SYSTEM-generated and cannot be dropped")


def _build_readback(index: dict[str, Any] | None, *, index_name: str, dropped: bool = False) -> dict[str, Any]:
    if index is None:
        return {"found": False, "name": index_name, "status": "DROPPED" if dropped else "MISSING"}
    out = dict(index)
    out["found"] = True
    out["status"] = _index_status(index)
    return out


def cmd_data_indexes_list(args, ctx) -> int:
    try:
        data_collection_id = _coerce_text(getattr(args, "data_collection_id", None), field="data-collection-id")
        limit = _coerce_optional_int(getattr(args, "limit", None), field="limit")
        offset = _coerce_optional_int(getattr(args, "offset", None), field="offset")
        headers, auth_mode = _resolve_indexes_auth(ctx=ctx)
        payload = _list_indexes(
            data_collection_id=data_collection_id,
            ctx=ctx,
            headers=headers,
            limit=limit,
            offset=offset,
        )
        indexes = _extract_indexes(payload, operation="data-indexes.list")
        request: dict[str, Any] = {"method": "GET", "path": "/wix-data/v2/indexes", "params": {"dataCollectionId": data_collection_id}}
        if limit is not None:
            request["params"]["paging.limit"] = limit
        if offset is not None:
            request["params"]["paging.offset"] = offset
        out = {
            "ok": True,
            "method": "data-indexes.list",
            "auth_mode": auth_mode,
            "request": request,
            "response": payload,
            "indexes": indexes,
        }
        ctx["audit"].write("data-indexes.list", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-indexes.list"}
        ctx["audit"].write("data-indexes.list.error", out)
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-indexes.list"}
        ctx["audit"].write("data-indexes.list.error", out)
        ctx["out"].emit(out)
        return 1


def cmd_data_indexes_create(args, ctx) -> int:
    try:
        data_collection_id = _coerce_text(getattr(args, "data_collection_id", None), field="data-collection-id")
        index = _coerce_index_payload(getattr(args, "index_json", None), field="index-json")
        index_name = str(index.get("name") or "").strip()
        headers, auth_mode = _resolve_indexes_auth(ctx=ctx)
        before_payload = _list_indexes(data_collection_id=data_collection_id, ctx=ctx, headers=headers)
        before_indexes = _extract_indexes(before_payload, operation="data-indexes.create")
        selector = {"kind": "wix-data-index", "operation": "create", "data_collection_id": data_collection_id, "index_name": index_name}
        request = {
            "method": "POST",
            "path": "/wix-data/v2/indexes",
            "body": {"dataCollectionId": data_collection_id, "index": index},
        }
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="data-indexes.create", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="data-indexes.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_payload,
                proposed_changes=[{"operation": "create", "data_collection_id": data_collection_id, "index_name": index_name}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify by rereading the index list until the named index appears with status BUILDING or ACTIVE.",
                },
            )

        if not _should_apply(ctx):
            out = {"ok": True, "dry_run": True, "method": "data-indexes.create", "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan), "indexes": before_indexes}
            ctx["audit"].write("data-indexes.create.plan", out)
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="data-indexes.create", expected_selector=selector, ctx=ctx)
        _assert_plan_state_matches(plan=loaded_plan, current_state=before_payload)

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/indexes",
            headers=headers,
            params=None,
            json_body={"dataCollectionId": data_collection_id, "index": index},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_payload = _list_indexes(data_collection_id=data_collection_id, ctx=ctx, headers=headers)
        after_indexes = _extract_indexes(after_payload, operation="data-indexes.create")
        after_index = _find_index_by_name(after_indexes, index_name=index_name)
        if after_index is None:
            raise SafetyError("Refused: created index is not visible in list readback yet")
        after_status = _index_status(after_index)
        if after_status in {"FAILED", "INVALID"}:
            raise SafetyError(f"Refused: index creation reported terminal status {after_status}")
        if after_status not in {"BUILDING", "ACTIVE"}:
            raise SafetyError(f"Refused: index creation returned unexpected status {after_status}")

        verification = {
            "ok": True,
            "type": "read-after-write",
            "path": "/wix-data/v2/indexes",
            "method": "GET",
            "before": before_indexes,
            "after": _build_readback(after_index, index_name=index_name),
            "status": after_status,
            "notes": "Create verification reads the index list after apply and accepts BUILDING or ACTIVE.",
        }
        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-indexes.create",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "state_capture": {
                "before_state_available": True,
                "notes": "Receipt is linked to a saved before-state snapshot from the reviewed plan.",
            },
            "diff_applied": loaded_plan.get("proposed_changes") or [],
            "recovery": {
                "automatic": False,
                "notes": "Recovery is manual only. If creation failed, the failed index still occupies a slot until dropped.",
            },
        }
        out = {
            "ok": True,
            "dry_run": False,
            "method": "data-indexes.create",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("data-indexes.create.apply", out)
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "data-indexes.create"}
        ctx["audit"].write("data-indexes.create.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-indexes.create"}
        ctx["audit"].write("data-indexes.create.error", out)
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-indexes.create"}
        ctx["audit"].write("data-indexes.create.error", out)
        ctx["out"].emit(out)
        return 1


def cmd_data_indexes_drop(args, ctx) -> int:
    try:
        data_collection_id = _coerce_text(getattr(args, "data_collection_id", None), field="data-collection-id")
        index_name = _coerce_text(getattr(args, "index_name", None), field="index-name")
        headers, auth_mode = _resolve_indexes_auth(ctx=ctx)
        before_payload = _list_indexes(data_collection_id=data_collection_id, ctx=ctx, headers=headers)
        before_indexes = _extract_indexes(before_payload, operation="data-indexes.drop")
        target_index = _find_index_by_name(before_indexes, index_name=index_name)
        if target_index is None:
            raise SafetyError(f"Refused: index not found in collection {data_collection_id}: {index_name}")
        if _index_source(target_index) == "SYSTEM":
            raise _refuse_system_index(index_name)
        if _index_status(target_index) == "DROPPED":
            raise SafetyError(f"Refused: index is already dropped: {index_name}")

        selector = {"kind": "wix-data-index", "operation": "drop", "data_collection_id": data_collection_id, "index_name": index_name}
        request = {
            "method": "DELETE",
            "path": "/wix-data/v2/indexes",
            "params": {"dataCollectionId": data_collection_id, "indexName": index_name},
        }
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="data-indexes.drop", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="data-indexes.drop",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_payload,
                proposed_changes=[{"operation": "drop", "data_collection_id": data_collection_id, "index_name": index_name}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify by rereading the index list until the named index is absent or shows DROPPING/DROPPED.",
                },
            )

        if not _should_apply(ctx):
            out = {"ok": True, "dry_run": True, "method": "data-indexes.drop", "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan), "indexes": before_indexes}
            ctx["audit"].write("data-indexes.drop.plan", out)
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="data-indexes.drop", expected_selector=selector, ctx=ctx)
        _assert_plan_state_matches(plan=loaded_plan, current_state=before_payload)

        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path="/wix-data/v2/indexes",
            headers=headers,
            params={"dataCollectionId": data_collection_id, "indexName": index_name},
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_payload = _list_indexes(data_collection_id=data_collection_id, ctx=ctx, headers=headers)
        after_indexes = _extract_indexes(after_payload, operation="data-indexes.drop")
        after_index = _find_index_by_name(after_indexes, index_name=index_name)
        if after_index is None:
            verification_after = _build_readback(None, index_name=index_name, dropped=True)
            verification = {
                "ok": True,
                "type": "read-after-write",
                "path": "/wix-data/v2/indexes",
                "method": "GET",
                "before": before_indexes,
                "after": verification_after,
                "status": "DROPPED",
                "notes": "Drop verification accepts the index disappearing from the list or showing DROPPED/DROPPING.",
            }
        else:
            after_status = _index_status(after_index)
            if after_status not in {"DROPPING", "DROPPED"}:
                raise SafetyError(f"Refused: index drop returned unexpected status {after_status}")
            verification = {
                "ok": True,
                "type": "read-after-write",
                "path": "/wix-data/v2/indexes",
                "method": "GET",
                "before": before_indexes,
                "after": _build_readback(after_index, index_name=index_name),
                "status": after_status,
                "notes": "Drop verification accepts DROPPING/DROPPED or the index disappearing from the list.",
            }

        receipt = {
            "tool": ctx.get("tool") or "wix-safe-agent-cli",
            "version": ctx.get("tool_version") or None,
            "applied_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "method": "data-indexes.drop",
            "selector": selector,
            "request": request,
            "response": response,
            "changed": True,
            "verification": verification,
            "state_capture": {
                "before_state_available": True,
                "notes": "Receipt is linked to a saved before-state snapshot from the reviewed plan.",
            },
            "diff_applied": loaded_plan.get("proposed_changes") or [],
            "recovery": {
                "automatic": False,
                "notes": "Recovery is manual only. Recreate the index if you need it again.",
            },
        }
        out = {
            "ok": True,
            "dry_run": False,
            "method": "data-indexes.drop",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["audit"].write("data-indexes.drop.apply", out)
        ctx["out"].emit(out)
        return 0
    except SafetyError as exc:
        out = {"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "data-indexes.drop"}
        ctx["audit"].write("data-indexes.drop.refused", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "data-indexes.drop"}
        ctx["audit"].write("data-indexes.drop.error", out)
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "data-indexes.drop"}
        ctx["audit"].write("data-indexes.drop.error", out)
        ctx["out"].emit(out)
        return 1
