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


def _coerce_non_empty_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_json_object(raw: Any, *, field: str) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _extract_item_body(payload: dict[str, Any]) -> dict[str, Any]:
    item = payload.get("item")
    if isinstance(item, dict):
        return item
    return payload


def _normalize_create_body(raw: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    body = _coerce_json_object(raw, field="item-json")
    item = _extract_item_body(body)
    if not isinstance(item, dict) or not item:
        raise ValidationError("--item-json must include a non-empty item object")
    return body, item


def _normalize_update_body(raw: Any, *, item_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    body = _coerce_json_object(raw, field="item-json")
    item = _extract_item_body(body)
    if not isinstance(item, dict) or not item:
        raise ValidationError("--item-json must include a non-empty item object")
    existing_id = item.get("id")
    if existing_id is not None and str(existing_id).strip() and str(existing_id).strip() != item_id:
        raise ValidationError("--item-json id does not match --item-id")
    item["id"] = item_id
    _coerce_non_empty_text(item.get("revision"), field="item-json revision")
    return body, item


def _normalize_query_body(raw: Any, *, field: str) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    return payload


def _normalize_count_body(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _read_json_arg(raw, field="filter-json")
    if not isinstance(payload, dict):
        raise ValidationError("--filter-json must be a JSON object")
    if "filter" in payload:
        return payload
    return {"filter": payload}


def _normalize_bulk_items_body(
    raw: Any,
    *,
    field: str,
    require_revision: bool,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    payload = _read_json_arg(raw, field=field)
    if isinstance(payload, list):
        body = {"items": payload}
    elif isinstance(payload, dict):
        body = dict(payload)
    else:
        raise ValidationError(f"--{field} must be a JSON array or object")

    items = body.get("items")
    if not isinstance(items, list) or not items:
        raise ValidationError(f"--{field} must include a non-empty items array")

    normalized: list[dict[str, Any]] = []
    ids: list[str] = []
    seen_ids: set[str] = set()
    for index, item_payload in enumerate(items):
        if not isinstance(item_payload, dict):
            raise ValidationError(f"--{field} items[{index}] must be a JSON object")
        item = _extract_item_body(item_payload)
        if not isinstance(item, dict) or not item:
            raise ValidationError(f"--{field} items[{index}] must include a non-empty item object")
        if require_revision:
            item_id = _coerce_non_empty_text(item.get("id"), field=f"{field} items[{index}].id")
            if item_id in seen_ids:
                raise ValidationError(f"--{field} contains duplicate item id: {item_id}")
            seen_ids.add(item_id)
            ids.append(item_id)
            _coerce_non_empty_text(item.get("revision"), field=f"{field} items[{index}].revision")
        normalized.append(item_payload if "item" in item_payload else item)

    body["items"] = normalized
    return body, normalized, ids


def _normalize_id_list_body(raw: Any) -> tuple[dict[str, Any], list[str]]:
    payload = _read_json_arg(raw, field="item-ids-json")
    raw_ids: list[Any] | None = None
    if isinstance(payload, list):
        raw_ids = payload
        body = {"ids": payload}
    elif isinstance(payload, dict):
        body = dict(payload)
        for key in ("ids", "itemIds"):
            value = body.get(key)
            if isinstance(value, list):
                raw_ids = value
                break
    else:
        raise ValidationError("--item-ids-json must be a JSON array or object")

    if not isinstance(raw_ids, list) or not raw_ids:
        raise ValidationError("--item-ids-json must include a non-empty ids or itemIds array")

    ids: list[str] = []
    seen_ids: set[str] = set()
    for index, raw_id in enumerate(raw_ids):
        item_id = _coerce_non_empty_text(raw_id, field=f"item-ids-json[{index}]")
        if item_id in seen_ids:
            raise ValidationError(f"--item-ids-json contains duplicate item id: {item_id}")
        seen_ids.add(item_id)
        ids.append(item_id)
    body["ids"] = ids
    return body, ids


def _normalize_delete_by_filter_body(raw: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = _coerce_json_object(raw, field="filter-json")
    body = dict(payload) if "filter" in payload else {"filter": payload}
    filter_obj = body.get("filter")
    if not isinstance(filter_obj, dict) or not filter_obj:
        raise ValidationError(
            "--filter-json must include a non-empty filter object; empty-filter bulk delete is refused in this boundary"
        )
    return body, filter_obj


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


def _has_pricing_plans_app(payload: dict[str, Any]) -> bool:
    site = payload.get("site")
    if not isinstance(site, dict):
        return False
    installed = site.get("installedWixApps")
    if not isinstance(installed, list):
        return False
    installed_values = {str(value).strip().lower() for value in installed if isinstance(value, str)}
    return "pricingplans" in installed_values


def _resolve_benefit_items_auth_and_preflight(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="benefit-items",
    )
    instance_payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path="/apps/v1/instance",
        headers=auth["headers"],
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    if not _has_pricing_plans_app(instance_payload):
        raise ValidationError("Required installed Wix app missing for benefit-items. Expected pricingPlans.")
    return auth["headers"], auth["mode"]


def _extract_item(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    item = payload.get("item")
    if isinstance(item, dict):
        return item
    if isinstance(payload.get("id"), str):
        return payload
    raise ValidationError(f"{operation} response did not include an item object")


def _extract_items(payload: dict[str, Any], *, operation: str) -> list[dict[str, Any]]:
    for key in ("items", "results"):
        raw_items = payload.get(key)
        if isinstance(raw_items, list):
            items = [item for item in raw_items if isinstance(item, dict)]
            if items or raw_items == []:
                return items
    raise ValidationError(f"{operation} response did not include an items list")


def _extract_item_id(item: dict[str, Any], *, operation: str) -> str:
    raw_id = item.get("id")
    if not isinstance(raw_id, str) or not raw_id.strip():
        raise ValidationError(f"{operation} response did not include a usable item id")
    return raw_id.strip()


def _http_status_from_error(exc: RuntimeError) -> int | None:
    text = str(exc)
    if not text.startswith("HTTP "):
        return None
    parts = text.split()
    if len(parts) < 2:
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def _get_item(*, item_id: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/benefit-programs/v1/items/{item_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_item(payload, operation="benefit-items.get")


def _count_items(*, body: dict[str, Any], ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    return _request_json(
        method="POST",
        base_url=ctx["cfg"].base_url,
        path="/benefit-programs/v1/items/count",
        headers=headers,
        params=None,
        json_body=body,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )


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
    requires_ack: bool = False,
    state_capture_notes: str | None = None,
    rollback_notes: str | None = None,
) -> dict[str, Any]:
    has_before_state = bool(before_state)
    preconditions = [
        "env_fingerprint must match",
        "selector must match",
        "apply requires --plan-in, --apply, and --yes",
    ]
    if requires_ack:
        preconditions.append("apply also requires --ack-irreversible")

    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": ["wix-benefit-item-write"] + (["irreversible"] if requires_ack else []),
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        },
        "state_capture": {
            "before_state_available": has_before_state,
            "notes": (
                state_capture_notes
                or (
                    "Captured current provider state before planning."
                    if has_before_state
                    else "No useful before-state snapshot exists for this create-style write."
                )
            ),
        },
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "rollback": {
            "supported": False,
            "notes": (
                rollback_notes
                or (
                    "No automatic rollback. Use the saved before-state only as a manual reference."
                    if has_before_state
                    else "No automatic rollback and no useful before-state snapshot."
                )
            ),
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


def _should_apply(ctx: dict[str, Any], *, command_label: str, requires_ack: bool = False) -> bool:
    if bool(ctx.get("apply")) and bool(ctx.get("yes")) and requires_ack and not bool(ctx.get("ack_irreversible")):
        raise SafetyError(f"Refused: {command_label} live apply requires --ack-irreversible")
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=command_label)


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any], label: str) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError(f"Refused: {label} state changed since plan was created")


def _build_receipt(
    *,
    method: str,
    selector: dict[str, Any],
    request: dict[str, Any],
    response: dict[str, Any],
    verification: dict[str, Any],
    plan: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    baseline = plan.get("baseline") if isinstance(plan, dict) else None
    before_state = baseline.get("before_state") if isinstance(baseline, dict) else None
    has_before_state = bool(before_state)
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "selector": selector,
        "request": request,
        "response": response,
        "changed": bool(verification.get("ok")),
        "verification": verification,
        "state_capture": {
            "before_state_available": has_before_state,
            "notes": (
                "Receipt is linked to a saved before-state snapshot from the reviewed plan."
                if has_before_state
                else "No useful before-state snapshot was available for this create-style write."
            ),
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": (
                "Recovery is manual only. Use the reviewed plan snapshot as a reference."
                if has_before_state
                else "Recovery is manual only and no useful before-state snapshot was available."
            ),
        },
    }


def _emit_validation_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _emit_refusal(ctx: dict[str, Any], *, method: str, exc: SafetyError) -> int:
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": True,
            "refused": True,
            "reasons": [str(exc)],
            "refusal_type": "SafetyError",
            "method": method,
        }
    )
    return 0


def cmd_benefit_items_get(args, ctx) -> int:
    try:
        item_id = _coerce_non_empty_text(getattr(args, "item_id", None), field="item-id")
        headers, auth_mode = _resolve_benefit_items_auth_and_preflight(ctx=ctx)
        item = _get_item(item_id=item_id, ctx=ctx, headers=headers)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "benefit-items.get",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": f"/benefit-programs/v1/items/{item_id}"},
                "response": {"item": item},
            }
        )
        return 0
    except (ValidationError, RuntimeError) as exc:
        return _emit_validation_error(ctx, method="benefit-items.get", exc=exc)


def cmd_benefit_items_list(args, ctx) -> int:
    try:
        headers, auth_mode = _resolve_benefit_items_auth_and_preflight(ctx=ctx)
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/benefit-programs/v1/items",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "benefit-items.list",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": "/benefit-programs/v1/items"},
                "response": payload,
            }
        )
        return 0
    except (ValidationError, RuntimeError) as exc:
        return _emit_validation_error(ctx, method="benefit-items.list", exc=exc)


def cmd_benefit_items_query(args, ctx) -> int:
    try:
        body = _normalize_query_body(getattr(args, "query_json", None), field="query-json")
        headers, auth_mode = _resolve_benefit_items_auth_and_preflight(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/benefit-programs/v1/items/query",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "benefit-items.query",
                "auth_mode": auth_mode,
                "request": {"method": "POST", "path": "/benefit-programs/v1/items/query", "body": body},
                "response": payload,
            }
        )
        return 0
    except (ValidationError, RuntimeError) as exc:
        return _emit_validation_error(ctx, method="benefit-items.query", exc=exc)


def cmd_benefit_items_count(args, ctx) -> int:
    try:
        body = _normalize_count_body(getattr(args, "filter_json", None))
        headers, auth_mode = _resolve_benefit_items_auth_and_preflight(ctx=ctx)
        payload = _count_items(body=body, ctx=ctx, headers=headers)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "benefit-items.count",
                "auth_mode": auth_mode,
                "request": {"method": "POST", "path": "/benefit-programs/v1/items/count", "body": body},
                "response": payload,
            }
        )
        return 0
    except (ValidationError, RuntimeError) as exc:
        return _emit_validation_error(ctx, method="benefit-items.count", exc=exc)


def cmd_benefit_items_create(args, ctx) -> int:
    try:
        body, item = _normalize_create_body(getattr(args, "item_json", None))
        should_apply = _should_apply(ctx, command_label="benefit-items")
        headers, auth_mode = _resolve_benefit_items_auth_and_preflight(ctx=ctx)
        request = {"method": "POST", "path": "/benefit-programs/v1/items", "body": body}
        selector = {"kind": "wix-benefit-item", "operation": "create"}
        plan = (
            _load_plan(plan_in=str(ctx.get("plan_in")), expected_method="benefit-items.create", expected_selector=selector, ctx=ctx)
            if ctx.get("plan_in")
            else _build_plan(
                method="benefit-items.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={},
                proposed_changes=[{"operation": "create", "item": item}],
                verification_plan={"type": "read-after-write", "notes": "Verify create response id and reread the created item."},
                rollback_notes="No automatic rollback. Benefit item creation is manual-recovery only.",
            )
        )
        if not should_apply:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "benefit-items.create",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/benefit-programs/v1/items",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_item = _extract_item(response, operation="benefit-items.create")
        item_id = _extract_item_id(created_item, operation="benefit-items.create")
        after_item = _get_item(item_id=item_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_item.get("id") or "") == item_id,
            "type": "read-after-write",
            "path": f"/benefit-programs/v1/items/{item_id}",
            "method": "GET",
            "after": after_item,
            "checks": [{"field": "id", "expected": item_id, "actual": after_item.get("id")}],
            "notes": "Create verification uses response id plus read-back get item.",
        }
        receipt = _build_receipt(
            method="benefit-items.create",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "benefit-items.create",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_refusal(ctx, method="benefit-items.create", exc=exc)
    except (ValidationError, RuntimeError) as exc:
        return _emit_validation_error(ctx, method="benefit-items.create", exc=exc)


def cmd_benefit_items_update(args, ctx) -> int:
    try:
        item_id = _coerce_non_empty_text(getattr(args, "item_id", None), field="item-id")
        body, item = _normalize_update_body(getattr(args, "item_json", None), item_id=item_id)
        should_apply = _should_apply(ctx, command_label="benefit-items")
        headers, auth_mode = _resolve_benefit_items_auth_and_preflight(ctx=ctx)
        current_item = _get_item(item_id=item_id, ctx=ctx, headers=headers)
        request = {"method": "PATCH", "path": f"/benefit-programs/v1/items/{item_id}", "body": body}
        selector = {"kind": "wix-benefit-item", "operation": "update", "item_id": item_id}
        plan = (
            _load_plan(plan_in=str(ctx.get("plan_in")), expected_method="benefit-items.update", expected_selector=selector, ctx=ctx)
            if ctx.get("plan_in")
            else _build_plan(
                method="benefit-items.update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={"item": current_item},
                proposed_changes=[{"operation": "update", "item": item}],
                verification_plan={"type": "read-after-write", "notes": "Verify update by rereading the item and checking revision changed."},
            )
        )
        if not should_apply:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "benefit-items.update",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        _assert_no_state_drift(
            plan=plan,
            current_state={"item": _get_item(item_id=item_id, ctx=ctx, headers=headers)},
            label="benefit item",
        )
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/benefit-programs/v1/items/{item_id}",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_item = _get_item(item_id=item_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_item.get("id") or "") == item_id
            and str(after_item.get("revision") or "") != str(current_item.get("revision") or ""),
            "type": "read-after-write",
            "path": f"/benefit-programs/v1/items/{item_id}",
            "method": "GET",
            "before": current_item,
            "after": after_item,
            "checks": [
                {"field": "id", "expected": item_id, "actual": after_item.get("id")},
                {
                    "field": "revision",
                    "expected": "changed",
                    "actual": {"before": current_item.get("revision"), "after": after_item.get("revision")},
                },
            ],
            "notes": "Update verification uses read-back get item and expects revision to change.",
        }
        receipt = _build_receipt(
            method="benefit-items.update",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "benefit-items.update",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_refusal(ctx, method="benefit-items.update", exc=exc)
    except (ValidationError, RuntimeError) as exc:
        return _emit_validation_error(ctx, method="benefit-items.update", exc=exc)


def cmd_benefit_items_delete(args, ctx) -> int:
    try:
        item_id = _coerce_non_empty_text(getattr(args, "item_id", None), field="item-id")
        should_apply = _should_apply(ctx, command_label="benefit-items.delete", requires_ack=True)
        headers, auth_mode = _resolve_benefit_items_auth_and_preflight(ctx=ctx)
        current_item = _get_item(item_id=item_id, ctx=ctx, headers=headers)
        request = {"method": "POST", "path": f"/benefit-programs/v1/items/{item_id}/delete", "body": {}}
        selector = {"kind": "wix-benefit-item", "operation": "delete", "item_id": item_id}
        plan = (
            _load_plan(plan_in=str(ctx.get("plan_in")), expected_method="benefit-items.delete", expected_selector=selector, ctx=ctx)
            if ctx.get("plan_in")
            else _build_plan(
                method="benefit-items.delete",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={"item": current_item},
                proposed_changes=[{"operation": "delete", "item_id": item_id}],
                verification_plan={"type": "read-after-delete", "notes": "Verify delete by expecting get item to return 404."},
                requires_ack=True,
                state_capture_notes="Captured the current item before planning. Deleting a benefit item removes the association immediately and may affect active pools.",
                rollback_notes="No automatic rollback. Recreate the association manually if needed.",
            )
        )
        if not should_apply:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "benefit-items.delete",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        _assert_no_state_drift(
            plan=plan,
            current_state={"item": _get_item(item_id=item_id, ctx=ctx, headers=headers)},
            label="benefit item",
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=f"/benefit-programs/v1/items/{item_id}/delete",
            headers=headers,
            params=None,
            json_body={},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        try:
            _get_item(item_id=item_id, ctx=ctx, headers=headers)
            verification = {
                "ok": False,
                "type": "read-after-delete",
                "path": f"/benefit-programs/v1/items/{item_id}",
                "method": "GET",
                "before": current_item,
                "notes": "Delete verification expected a 404 read-back but the item still resolved.",
            }
        except RuntimeError as exc:
            verification = {
                "ok": _http_status_from_error(exc) == 404,
                "type": "read-after-delete",
                "path": f"/benefit-programs/v1/items/{item_id}",
                "method": "GET",
                "before": current_item,
                "after_error": str(exc),
                "notes": "Delete verification expects get item to return 404 after delete.",
            }
        receipt = _build_receipt(
            method="benefit-items.delete",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "benefit-items.delete",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_refusal(ctx, method="benefit-items.delete", exc=exc)
    except (ValidationError, RuntimeError) as exc:
        return _emit_validation_error(ctx, method="benefit-items.delete", exc=exc)


def cmd_benefit_items_bulk_create(args, ctx) -> int:
    try:
        body, items, _ids = _normalize_bulk_items_body(getattr(args, "items_json", None), field="items-json", require_revision=False)
        should_apply = _should_apply(ctx, command_label="benefit-items")
        headers, auth_mode = _resolve_benefit_items_auth_and_preflight(ctx=ctx)
        request = {"method": "POST", "path": "/benefit-programs/v1/bulk/items/create", "body": body}
        selector = {"kind": "wix-benefit-item", "operation": "bulk-create"}
        plan = (
            _load_plan(plan_in=str(ctx.get("plan_in")), expected_method="benefit-items.bulk-create", expected_selector=selector, ctx=ctx)
            if ctx.get("plan_in")
            else _build_plan(
                method="benefit-items.bulk-create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={},
                proposed_changes=[{"operation": "bulk-create", "count": len(items), "items": items}],
                verification_plan={"type": "read-after-write", "notes": "Verify returned item ids and reread each created item."},
                rollback_notes="No automatic rollback. Benefit item creation is manual-recovery only.",
            )
        )
        if not should_apply:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "benefit-items.bulk-create",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/benefit-programs/v1/bulk/items/create",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_items = _extract_items(response, operation="benefit-items.bulk-create")
        created_ids = [_extract_item_id(item, operation="benefit-items.bulk-create") for item in created_items]
        after_items = [_get_item(item_id=item_id, ctx=ctx, headers=headers) for item_id in created_ids]
        verification = {
            "ok": bool(created_ids) and all(str(item.get("id") or "") in created_ids for item in after_items),
            "type": "read-after-write",
            "paths": [f"/benefit-programs/v1/items/{item_id}" for item_id in created_ids],
            "method": "GET",
            "after": after_items,
            "checks": [{"field": "created_ids", "expected_count": len(created_ids), "actual_count": len(after_items)}],
            "notes": "Bulk create verification uses returned ids plus read-back get item calls.",
        }
        receipt = _build_receipt(
            method="benefit-items.bulk-create",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "benefit-items.bulk-create",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_refusal(ctx, method="benefit-items.bulk-create", exc=exc)
    except (ValidationError, RuntimeError) as exc:
        return _emit_validation_error(ctx, method="benefit-items.bulk-create", exc=exc)


def cmd_benefit_items_bulk_update(args, ctx) -> int:
    try:
        body, items, ids = _normalize_bulk_items_body(getattr(args, "items_json", None), field="items-json", require_revision=True)
        should_apply = _should_apply(ctx, command_label="benefit-items")
        headers, auth_mode = _resolve_benefit_items_auth_and_preflight(ctx=ctx)
        current_items = {item_id: _get_item(item_id=item_id, ctx=ctx, headers=headers) for item_id in ids}
        request = {"method": "POST", "path": "/benefit-programs/v1/bulk/items/update", "body": body}
        selector = {"kind": "wix-benefit-item", "operation": "bulk-update", "item_ids": ids}
        plan = (
            _load_plan(plan_in=str(ctx.get("plan_in")), expected_method="benefit-items.bulk-update", expected_selector=selector, ctx=ctx)
            if ctx.get("plan_in")
            else _build_plan(
                method="benefit-items.bulk-update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={"items": current_items},
                proposed_changes=[{"operation": "bulk-update", "count": len(items), "items": items}],
                verification_plan={"type": "read-after-write", "notes": "Verify each item rereads and its revision changes."},
            )
        )
        if not should_apply:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "benefit-items.bulk-update",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        _assert_no_state_drift(
            plan=plan,
            current_state={"items": {item_id: _get_item(item_id=item_id, ctx=ctx, headers=headers) for item_id in ids}},
            label="benefit items",
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/benefit-programs/v1/bulk/items/update",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_items = {item_id: _get_item(item_id=item_id, ctx=ctx, headers=headers) for item_id in ids}
        verification = {
            "ok": all(str(after_items[item_id].get("revision") or "") != str(current_items[item_id].get("revision") or "") for item_id in ids),
            "type": "read-after-write",
            "paths": [f"/benefit-programs/v1/items/{item_id}" for item_id in ids],
            "method": "GET",
            "before": current_items,
            "after": after_items,
            "checks": [
                {
                    "field": "revision",
                    "expected": "changed",
                    "actual": {
                        item_id: {
                            "before": current_items[item_id].get("revision"),
                            "after": after_items[item_id].get("revision"),
                        }
                        for item_id in ids
                    },
                }
            ],
            "notes": "Bulk update verification rereads each item and expects revisions to change.",
        }
        receipt = _build_receipt(
            method="benefit-items.bulk-update",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "benefit-items.bulk-update",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_refusal(ctx, method="benefit-items.bulk-update", exc=exc)
    except (ValidationError, RuntimeError) as exc:
        return _emit_validation_error(ctx, method="benefit-items.bulk-update", exc=exc)


def cmd_benefit_items_bulk_delete(args, ctx) -> int:
    try:
        body, ids = _normalize_id_list_body(getattr(args, "item_ids_json", None))
        should_apply = _should_apply(ctx, command_label="benefit-items.bulk-delete", requires_ack=True)
        headers, auth_mode = _resolve_benefit_items_auth_and_preflight(ctx=ctx)
        current_items = {item_id: _get_item(item_id=item_id, ctx=ctx, headers=headers) for item_id in ids}
        request = {"method": "POST", "path": "/benefit-programs/v1/bulk/items/delete", "body": body}
        selector = {"kind": "wix-benefit-item", "operation": "bulk-delete", "item_ids": ids}
        plan = (
            _load_plan(plan_in=str(ctx.get("plan_in")), expected_method="benefit-items.bulk-delete", expected_selector=selector, ctx=ctx)
            if ctx.get("plan_in")
            else _build_plan(
                method="benefit-items.bulk-delete",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={"items": current_items},
                proposed_changes=[{"operation": "bulk-delete", "item_ids": ids}],
                verification_plan={"type": "read-after-delete", "notes": "Verify each deleted item returns 404."},
                requires_ack=True,
                state_capture_notes="Captured the current items before planning. Deleting benefit items removes their associations immediately and may affect active pools.",
                rollback_notes="No automatic rollback. Recreate deleted associations manually if needed.",
            )
        )
        if not should_apply:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "benefit-items.bulk-delete",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        _assert_no_state_drift(
            plan=plan,
            current_state={"items": {item_id: _get_item(item_id=item_id, ctx=ctx, headers=headers) for item_id in ids}},
            label="benefit items",
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/benefit-programs/v1/bulk/items/delete",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_errors: dict[str, str] = {}
        ok = True
        for item_id in ids:
            try:
                _get_item(item_id=item_id, ctx=ctx, headers=headers)
                ok = False
            except RuntimeError as exc:
                after_errors[item_id] = str(exc)
                if _http_status_from_error(exc) != 404:
                    ok = False
        verification = {
            "ok": ok,
            "type": "read-after-delete",
            "paths": [f"/benefit-programs/v1/items/{item_id}" for item_id in ids],
            "method": "GET",
            "before": current_items,
            "after_errors": after_errors,
            "notes": "Bulk delete verification expects get item to return 404 for each deleted item.",
        }
        receipt = _build_receipt(
            method="benefit-items.bulk-delete",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "benefit-items.bulk-delete",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_refusal(ctx, method="benefit-items.bulk-delete", exc=exc)
    except (ValidationError, RuntimeError) as exc:
        return _emit_validation_error(ctx, method="benefit-items.bulk-delete", exc=exc)


def cmd_benefit_items_bulk_delete_by_filter(args, ctx) -> int:
    try:
        body, filter_obj = _normalize_delete_by_filter_body(getattr(args, "filter_json", None))
        should_apply = _should_apply(ctx, command_label="benefit-items.bulk-delete-by-filter", requires_ack=True)
        headers, auth_mode = _resolve_benefit_items_auth_and_preflight(ctx=ctx)
        before_count = _count_items(body={"filter": filter_obj}, ctx=ctx, headers=headers)
        request = {"method": "POST", "path": "/benefit-programs/v1/bulk/items/delete-by-filter", "body": body}
        selector = {"kind": "wix-benefit-item", "operation": "bulk-delete-by-filter", "filter": filter_obj}
        plan = (
            _load_plan(plan_in=str(ctx.get("plan_in")), expected_method="benefit-items.bulk-delete-by-filter", expected_selector=selector, ctx=ctx)
            if ctx.get("plan_in")
            else _build_plan(
                method="benefit-items.bulk-delete-by-filter",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={"count": before_count, "filter": filter_obj},
                proposed_changes=[{"operation": "bulk-delete-by-filter", "filter": filter_obj}],
                verification_plan={"type": "count-after-delete", "notes": "Verify the matching item count drops to 0 after delete-by-filter."},
                requires_ack=True,
                state_capture_notes="Captured the matching item count before planning. Full item snapshots are not guaranteed for filter-based deletes in this boundary.",
                rollback_notes="No automatic rollback. Recreate deleted associations manually if needed.",
            )
        )
        if not should_apply:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "benefit-items.bulk-delete-by-filter",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        _assert_no_state_drift(
            plan=plan,
            current_state={"count": _count_items(body={"filter": filter_obj}, ctx=ctx, headers=headers), "filter": filter_obj},
            label="benefit item filter",
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/benefit-programs/v1/bulk/items/delete-by-filter",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_count = _count_items(body={"filter": filter_obj}, ctx=ctx, headers=headers)
        count_value = after_count.get("count")
        verification = {
            "ok": isinstance(count_value, int) and count_value == 0,
            "type": "count-after-delete",
            "path": "/benefit-programs/v1/items/count",
            "method": "POST",
            "before": before_count,
            "after": after_count,
            "checks": [{"field": "count", "expected": 0, "actual": count_value}],
            "notes": "Delete-by-filter verification rereads the official item count for the same filter and expects 0 matches.",
        }
        receipt = _build_receipt(
            method="benefit-items.bulk-delete-by-filter",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "benefit-items.bulk-delete-by-filter",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_refusal(ctx, method="benefit-items.bulk-delete-by-filter", exc=exc)
    except (ValidationError, RuntimeError) as exc:
        return _emit_validation_error(ctx, method="benefit-items.bulk-delete-by-filter", exc=exc)
