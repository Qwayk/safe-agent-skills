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


def _require_revision(raw: Any, *, field: str = "product-json") -> None:
    if raw is None:
        raise ValidationError(f"--{field} product.revision is required for update")
    if isinstance(raw, str) and not raw.strip():
        raise ValidationError(f"--{field} product.revision cannot be empty")


def _normalize_query_body(raw: Any, *, field: str, wrapper_key: str) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if wrapper_key in payload:
        nested = payload.get(wrapper_key)
        if not isinstance(nested, dict):
            raise ValidationError(f"--{field} {wrapper_key} must be a JSON object")
        return payload
    return {wrapper_key: payload}


def _normalize_count_body(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _read_json_arg(raw, field="filter-json")
    if not isinstance(payload, dict):
        raise ValidationError("--filter-json must be a JSON object")
    if "filter" in payload:
        return payload
    return {"filter": payload}


def _normalize_create_body(raw: Any) -> dict[str, Any]:
    payload = _coerce_json_object(raw, field="product-json")
    body = dict(payload) if "product" in payload else {"product": payload}
    product = body.get("product")
    if not isinstance(product, dict) or not product:
        raise ValidationError("--product-json must include a non-empty product object")
    return body


def _normalize_update_body(raw: Any, *, product_id: str) -> dict[str, Any]:
    payload = _coerce_json_object(raw, field="product-json")
    body = dict(payload) if "product" in payload else {"product": payload}
    product = body.get("product")
    if not isinstance(product, dict) or not product:
        raise ValidationError("--product-json must include a non-empty product object")
    payload_id = product.get("id")
    if payload_id is not None and str(payload_id).strip() != product_id:
        raise SafetyError("Refused: product id in body does not match --product-id")
    product.setdefault("id", product_id)
    _require_revision(product.get("revision"))
    return body


def _normalize_products_body(raw: Any, *, field: str, require_revision: bool = False) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if isinstance(payload, dict):
        body = dict(payload)
        products = body.get("products")
    elif isinstance(payload, list):
        products = payload
        body = {"products": products}
    else:
        raise ValidationError(f"--{field} must be a JSON object or array")
    if not isinstance(products, list) or not products:
        raise ValidationError(f"--{field} must include a non-empty products array")
    if require_revision:
        for index, product in enumerate(products):
            if not isinstance(product, dict):
                raise ValidationError(f"--{field} products[{index}] must be an object")
            try:
                _require_revision(product.get("revision"), field=field)
            except ValidationError as exc:
                raise ValidationError(f"--{field} products[{index}].revision is required for bulk update") from exc
    return body


def _normalize_request_body(raw: Any, *, field: str = "request-json") -> dict[str, Any]:
    payload = _coerce_json_object(raw, field=field)
    return dict(payload)


def _resolve_stores_products_v3_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="stores-products-v3",
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


def _extract_product(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    product = payload.get("product")
    if not isinstance(product, dict):
        raise ValidationError(f"{operation} response did not include a product object")
    return product


def _extract_product_id(product: dict[str, Any], *, operation: str) -> str:
    raw_id = product.get("id")
    if not isinstance(raw_id, str) or not raw_id.strip():
        raise ValidationError(f"{operation} response did not include a usable product id")
    return raw_id.strip()


def _get_product(*, product_id: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/stores/v3/products/{product_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_product(payload, operation="stores-products-v3.get")


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
    state_capture_notes: str | None = None,
    rollback_notes: str | None = None,
    requires_ack: bool = False,
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
        "risk_reasons": ["wix-stores-product-write"],
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
                    "Captured current product state before planning."
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
                    "No automatic rollback. Use the reviewed plan snapshot as a manual reference."
                    if has_before_state
                    else "No automatic rollback and no useful before-state snapshot."
                )
            ),
        },
    }


def _load_plan(*, plan_in: str | None, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
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


def _should_apply(ctx: dict[str, Any], *, requires_ack: bool = False) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="stores-products-v3")


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: product state changed since plan was created")


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


def _emit_safety_refusal(ctx: dict[str, Any], *, method: str, exc: SafetyError) -> int:
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


def _run_provider_response_write(
    *,
    method_name: str,
    http_method: str,
    path: str,
    body: dict[str, Any] | None,
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    ctx: dict[str, Any],
    requires_ack: bool = False,
    verification_notes: str = "Provider-response-only in this boundary. Run follow-up product reads or searches for live verification.",
) -> int:
    headers, auth_mode = _resolve_stores_products_v3_auth(ctx=ctx)
    request = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    plan_in = ctx.get("plan_in")
    if bool(ctx.get("apply")) and bool(ctx.get("yes")):
        apply_allowed = _should_apply(ctx, requires_ack=requires_ack)
    else:
        apply_allowed = False
    if plan_in:
        plan = _load_plan(plan_in=str(plan_in), expected_method=method_name, expected_selector=selector, ctx=ctx)
    else:
        plan = _build_plan(
            method=method_name,
            request=request,
            selector=selector,
            ctx=ctx,
            before_state={},
            proposed_changes=proposed_changes,
            verification_plan={"type": "provider-response", "notes": verification_notes},
            state_capture_notes="No useful before-state snapshot exists for this Products V3 write in the current boundary.",
            rollback_notes="No automatic rollback. Recovery is manual and may require new reviewed product plans.",
            requires_ack=requires_ack,
        )
    if not apply_allowed:
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "method": method_name,
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
        )
        return 0
    loaded_plan = _load_plan(plan_in=str(plan_in), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(
        method=http_method,
        base_url=ctx["cfg"].base_url,
        path=path,
        headers=headers,
        params=None,
        json_body=body,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    verification = {"ok": True, "type": "provider-response", "notes": verification_notes}
    receipt = _build_receipt(
        method=method_name,
        selector=selector,
        request=request,
        response=response,
        verification=verification,
        plan=loaded_plan,
        ctx=ctx,
    )
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": False,
            "method": method_name,
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
    )
    return 0


def _write_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, SafetyError):
        return _emit_safety_refusal(ctx, method=method, exc=exc)
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def cmd_stores_products_v3_delete(args, ctx) -> int:
    method = "stores-products-v3.delete"
    try:
        product_id = _coerce_non_empty_text(getattr(args, "product_id", None), field="product-id")
        return _run_provider_response_write(
            method_name=method,
            http_method="DELETE",
            path=f"/stores/v3/products/{product_id}",
            body=None,
            selector={"kind": "wix-stores-product-v3", "operation": "delete", "product_id": product_id},
            proposed_changes=[{"operation": "delete", "product_id": product_id}],
            ctx=ctx,
            requires_ack=True,
            verification_notes="Provider accepted product deletion. A follow-up get should return not found.",
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_stores_products_v3_bulk_create(args, ctx) -> int:
    method = "stores-products-v3.bulk-create"
    try:
        body = _normalize_products_body(getattr(args, "products_json", None), field="products-json")
        return _run_provider_response_write(
            method_name=method,
            http_method="POST",
            path="/stores/v3/bulk/products/create",
            body=body,
            selector={"kind": "wix-stores-product-v3", "operation": "bulk-create"},
            proposed_changes=[{"operation": "bulk-create", "body": body}],
            ctx=ctx,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_stores_products_v3_bulk_delete(args, ctx) -> int:
    method = "stores-products-v3.bulk-delete"
    try:
        body = _normalize_request_body(getattr(args, "request_json", None))
        return _run_provider_response_write(
            method_name=method,
            http_method="POST",
            path="/stores/v3/bulk/products/delete",
            body=body,
            selector={"kind": "wix-stores-product-v3", "operation": "bulk-delete"},
            proposed_changes=[{"operation": "bulk-delete", "body": body}],
            ctx=ctx,
            requires_ack=True,
            verification_notes="Provider accepted bulk product deletion. Follow-up gets/searches are recommended.",
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_stores_products_v3_bulk_update(args, ctx) -> int:
    method = "stores-products-v3.bulk-update"
    try:
        body = _normalize_products_body(getattr(args, "products_json", None), field="products-json", require_revision=True)
        return _run_provider_response_write(
            method_name=method,
            http_method="POST",
            path="/stores/v3/bulk/products/update",
            body=body,
            selector={"kind": "wix-stores-product-v3", "operation": "bulk-update"},
            proposed_changes=[{"operation": "bulk-update", "body": body}],
            ctx=ctx,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_stores_products_v3_create_with_inventory(args, ctx) -> int:
    method = "stores-products-v3.create-with-inventory"
    try:
        body = _normalize_create_body(getattr(args, "product_json", None))
        return _run_provider_response_write(
            method_name=method,
            http_method="POST",
            path="/stores/v3/products-with-inventory",
            body=body,
            selector={"kind": "wix-stores-product-v3", "operation": "create-with-inventory"},
            proposed_changes=[{"operation": "create-with-inventory", "body": body}],
            ctx=ctx,
            verification_notes="Provider accepted product-with-inventory creation. Follow-up product and inventory reads are recommended.",
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_stores_products_v3_update_with_inventory(args, ctx) -> int:
    method = "stores-products-v3.update-with-inventory"
    try:
        product_id = _coerce_non_empty_text(getattr(args, "product_id", None), field="product-id")
        body = _normalize_update_body(getattr(args, "product_json", None), product_id=product_id)
        return _run_provider_response_write(
            method_name=method,
            http_method="PATCH",
            path=f"/stores/v3/products-with-inventory/{product_id}",
            body=body,
            selector={"kind": "wix-stores-product-v3", "operation": "update-with-inventory", "product_id": product_id},
            proposed_changes=[{"operation": "update-with-inventory", "product_id": product_id, "body": body}],
            ctx=ctx,
            verification_notes="Provider accepted product-with-inventory update. Follow-up product and inventory reads are recommended.",
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_stores_products_v3_bulk_create_with_inventory(args, ctx) -> int:
    method = "stores-products-v3.bulk-create-with-inventory"
    try:
        body = _normalize_products_body(getattr(args, "products_json", None), field="products-json")
        return _run_provider_response_write(
            method_name=method,
            http_method="POST",
            path="/stores/v3/bulk/products-with-inventory/create",
            body=body,
            selector={"kind": "wix-stores-product-v3", "operation": "bulk-create-with-inventory"},
            proposed_changes=[{"operation": "bulk-create-with-inventory", "body": body}],
            ctx=ctx,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_stores_products_v3_bulk_update_with_inventory(args, ctx) -> int:
    method = "stores-products-v3.bulk-update-with-inventory"
    try:
        body = _normalize_products_body(getattr(args, "products_json", None), field="products-json", require_revision=True)
        return _run_provider_response_write(
            method_name=method,
            http_method="POST",
            path="/stores/v3/bulk/products-with-inventory/update",
            body=body,
            selector={"kind": "wix-stores-product-v3", "operation": "bulk-update-with-inventory"},
            proposed_changes=[{"operation": "bulk-update-with-inventory", "body": body}],
            ctx=ctx,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


_PRODUCTS_REQUEST_OPERATIONS = {
    "bulk-add-info-sections": (
        "stores-products-v3.bulk-add-info-sections",
        "/stores/v3/bulk/products/add-info-sections",
        False,
    ),
    "bulk-add-info-sections-by-filter": (
        "stores-products-v3.bulk-add-info-sections-by-filter",
        "/stores/v3/bulk/products/add-info-sections-by-filter",
        False,
    ),
    "bulk-add-to-categories-by-filter": (
        "stores-products-v3.bulk-add-to-categories-by-filter",
        "/stores/v3/bulk/products/add-to-categories-by-filter",
        False,
    ),
    "bulk-adjust-variants-by-filter": (
        "stores-products-v3.bulk-adjust-variants-by-filter",
        "/stores/v3/bulk/products/adjust-variants-by-filter",
        False,
    ),
    "bulk-delete-by-filter": (
        "stores-products-v3.bulk-delete-by-filter",
        "/stores/v3/bulk/products/delete-by-filter",
        True,
    ),
    "bulk-remove-info-sections": (
        "stores-products-v3.bulk-remove-info-sections",
        "/stores/v3/bulk/products/remove-info-sections",
        True,
    ),
    "bulk-remove-info-sections-by-filter": (
        "stores-products-v3.bulk-remove-info-sections-by-filter",
        "/stores/v3/bulk/products/remove-info-sections-by-filter",
        True,
    ),
    "bulk-remove-from-categories-by-filter": (
        "stores-products-v3.bulk-remove-from-categories-by-filter",
        "/stores/v3/bulk/products/remove-from-categories-by-filter",
        True,
    ),
    "bulk-update-variants-by-filter": (
        "stores-products-v3.bulk-update-variants-by-filter",
        "/stores/v3/bulk/products/update-variants-by-filter",
        False,
    ),
    "bulk-update-by-filter": (
        "stores-products-v3.bulk-update-by-filter",
        "/stores/v3/bulk/products/update-by-filter",
        False,
    ),
}


def _run_products_request_operation(args, ctx, *, operation: str) -> int:
    method, path, requires_ack = _PRODUCTS_REQUEST_OPERATIONS[operation]
    try:
        body = _normalize_request_body(getattr(args, "request_json", None))
        return _run_provider_response_write(
            method_name=method,
            http_method="POST",
            path=path,
            body=body,
            selector={"kind": "wix-stores-product-v3", "operation": operation},
            proposed_changes=[{"operation": operation, "body": body}],
            ctx=ctx,
            requires_ack=requires_ack,
        )
    except (SafetyError, ValidationError, RuntimeError) as exc:
        return _write_error(ctx, method=method, exc=exc)


def cmd_stores_products_v3_bulk_add_info_sections(args, ctx) -> int:
    return _run_products_request_operation(args, ctx, operation="bulk-add-info-sections")


def cmd_stores_products_v3_bulk_add_info_sections_by_filter(args, ctx) -> int:
    return _run_products_request_operation(args, ctx, operation="bulk-add-info-sections-by-filter")


def cmd_stores_products_v3_bulk_add_to_categories_by_filter(args, ctx) -> int:
    return _run_products_request_operation(args, ctx, operation="bulk-add-to-categories-by-filter")


def cmd_stores_products_v3_bulk_adjust_variants_by_filter(args, ctx) -> int:
    return _run_products_request_operation(args, ctx, operation="bulk-adjust-variants-by-filter")


def cmd_stores_products_v3_bulk_delete_by_filter(args, ctx) -> int:
    return _run_products_request_operation(args, ctx, operation="bulk-delete-by-filter")


def cmd_stores_products_v3_bulk_remove_info_sections(args, ctx) -> int:
    return _run_products_request_operation(args, ctx, operation="bulk-remove-info-sections")


def cmd_stores_products_v3_bulk_remove_info_sections_by_filter(args, ctx) -> int:
    return _run_products_request_operation(args, ctx, operation="bulk-remove-info-sections-by-filter")


def cmd_stores_products_v3_bulk_remove_from_categories_by_filter(args, ctx) -> int:
    return _run_products_request_operation(args, ctx, operation="bulk-remove-from-categories-by-filter")


def cmd_stores_products_v3_bulk_update_variants_by_filter(args, ctx) -> int:
    return _run_products_request_operation(args, ctx, operation="bulk-update-variants-by-filter")


def cmd_stores_products_v3_bulk_update_by_filter(args, ctx) -> int:
    return _run_products_request_operation(args, ctx, operation="bulk-update-by-filter")


def cmd_stores_products_v3_get(args, ctx) -> int:
    try:
        product_id = _coerce_non_empty_text(getattr(args, "product_id", None), field="product-id")
        headers, auth_mode = _resolve_stores_products_v3_auth(ctx=ctx)
        product = _get_product(product_id=product_id, ctx=ctx, headers=headers)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "stores-products-v3.get",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": f"/stores/v3/products/{product_id}"},
                "response": {"product": product},
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-products-v3.get"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-products-v3.get"}
        )
        return 1


def cmd_stores_products_v3_get_by_slug(args, ctx) -> int:
    try:
        slug = _coerce_non_empty_text(getattr(args, "slug", None), field="slug")
        headers, auth_mode = _resolve_stores_products_v3_auth(ctx=ctx)
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=f"/stores/v3/products/slug/{slug}",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        product = _extract_product(payload, operation="stores-products-v3.get-by-slug")
        ctx["out"].emit(
            {
                "ok": True,
                "method": "stores-products-v3.get-by-slug",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": f"/stores/v3/products/slug/{slug}"},
                "response": {"product": product},
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-products-v3.get-by-slug"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "stores-products-v3.get-by-slug",
            }
        )
        return 1


def cmd_stores_products_v3_get_all_products_category(args, ctx) -> int:
    _ = args
    try:
        headers, auth_mode = _resolve_stores_products_v3_auth(ctx=ctx)
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/stores/v3/all-products-category",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "stores-products-v3.get-all-products-category",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": "/stores/v3/all-products-category"},
                "response": payload,
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "stores-products-v3.get-all-products-category",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "stores-products-v3.get-all-products-category",
            }
        )
        return 1


def _emit_read_result(*, ctx: dict[str, Any], method: str, path: str, body: dict[str, Any], payload: dict[str, Any], auth_mode: str) -> int:
    ctx["out"].emit(
        {
            "ok": True,
            "method": method,
            "auth_mode": auth_mode,
            "request": {"method": "POST", "path": path, "body": body},
            "response": payload,
        }
    )
    return 0


def cmd_stores_products_v3_query(args, ctx) -> int:
    try:
        body = _normalize_query_body(getattr(args, "query_json", None), field="query-json", wrapper_key="query")
        headers, auth_mode = _resolve_stores_products_v3_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/stores/v3/products/query",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        return _emit_read_result(
            ctx=ctx,
            method="stores-products-v3.query",
            path="/stores/v3/products/query",
            body=body,
            payload=payload,
            auth_mode=auth_mode,
        )
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-products-v3.query"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-products-v3.query"}
        )
        return 1


def cmd_stores_products_v3_search(args, ctx) -> int:
    try:
        body = _normalize_query_body(getattr(args, "search_json", None), field="search-json", wrapper_key="search")
        headers, auth_mode = _resolve_stores_products_v3_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/stores/v3/products/search",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        return _emit_read_result(
            ctx=ctx,
            method="stores-products-v3.search",
            path="/stores/v3/products/search",
            body=body,
            payload=payload,
            auth_mode=auth_mode,
        )
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-products-v3.search"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-products-v3.search"}
        )
        return 1


def cmd_stores_products_v3_count(args, ctx) -> int:
    try:
        body = _normalize_count_body(getattr(args, "filter_json", None))
        headers, auth_mode = _resolve_stores_products_v3_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/stores/v3/products/count",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        return _emit_read_result(
            ctx=ctx,
            method="stores-products-v3.count",
            path="/stores/v3/products/count",
            body=body,
            payload=payload,
            auth_mode=auth_mode,
        )
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-products-v3.count"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-products-v3.count"}
        )
        return 1


def cmd_stores_products_v3_create(args, ctx) -> int:
    try:
        product_json = _normalize_create_body(getattr(args, "product_json", None))
        headers, auth_mode = _resolve_stores_products_v3_auth(ctx=ctx)
        request = {"method": "POST", "path": "/stores/v3/products", "body": product_json}
        selector = {"kind": "wix-stores-product-v3", "operation": "create"}
        plan_in = ctx.get("plan_in")
        apply_allowed = False
        if bool(ctx.get("apply")) and bool(ctx.get("yes")):
            apply_allowed = _should_apply(ctx)
        plan = (
            _load_plan(plan_in=str(plan_in), expected_method="stores-products-v3.create", expected_selector=selector, ctx=ctx)
            if plan_in
            else _build_plan(
                method="stores-products-v3.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={},
                proposed_changes=[{"operation": "create", "body": product_json}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify create response id and reread the created product.",
                },
                state_capture_notes="No useful before-state snapshot exists before a product is created.",
            )
        )
        if not apply_allowed:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "stores-products-v3.create",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0
        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="stores-products-v3.create",
            expected_selector=selector,
            ctx=ctx,
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/stores/v3/products",
            headers=headers,
            params=None,
            json_body=product_json,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_product = _extract_product(response, operation="stores-products-v3.create")
        created_id = _extract_product_id(created_product, operation="stores-products-v3.create")
        after_product = _get_product(product_id=created_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_product.get("id") or "") == created_id,
            "type": "read-after-write",
            "path": f"/stores/v3/products/{created_id}",
            "method": "GET",
            "after": after_product,
            "checks": [{"field": "id", "expected": created_id, "actual": after_product.get("id")}],
            "notes": "Create verification uses response id plus read-back get product.",
        }
        receipt = _build_receipt(
            method="stores-products-v3.create",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "stores-products-v3.create",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="stores-products-v3.create", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-products-v3.create"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-products-v3.create"}
        )
        return 1


def cmd_stores_products_v3_update(args, ctx) -> int:
    try:
        product_id = _coerce_non_empty_text(getattr(args, "product_id", None), field="product-id")
        product_json = _normalize_update_body(getattr(args, "product_json", None), product_id=product_id)
        headers, auth_mode = _resolve_stores_products_v3_auth(ctx=ctx)
        request = {"method": "PATCH", "path": f"/stores/v3/products/{product_id}", "body": product_json}
        selector = {"kind": "wix-stores-product-v3", "operation": "update", "product_id": product_id}
        plan_in = ctx.get("plan_in")
        apply_allowed = False
        if bool(ctx.get("apply")) and bool(ctx.get("yes")):
            apply_allowed = _should_apply(ctx)
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="stores-products-v3.update",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            current_product = _get_product(product_id=product_id, ctx=ctx, headers=headers)
            plan = _build_plan(
                method="stores-products-v3.update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={"product": current_product},
                proposed_changes=[{"operation": "update", "product_id": product_id, "body": product_json}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify the updated product by rereading the same product id.",
                },
            )
        if not apply_allowed:
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "stores-products-v3.update",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0
        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="stores-products-v3.update",
            expected_selector=selector,
            ctx=ctx,
        )
        current_product = _get_product(product_id=product_id, ctx=ctx, headers=headers)
        _assert_no_state_drift(plan=loaded_plan, current_state={"product": current_product})
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/stores/v3/products/{product_id}",
            headers=headers,
            params=None,
            json_body=product_json,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_product = _get_product(product_id=product_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_product.get("id") or "") == product_id,
            "type": "read-after-write",
            "path": f"/stores/v3/products/{product_id}",
            "method": "GET",
            "before": current_product,
            "after": after_product,
            "checks": [{"field": "id", "expected": product_id, "actual": after_product.get("id")}],
            "notes": "Update verification uses read-back get product.",
        }
        receipt = _build_receipt(
            method="stores-products-v3.update",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "stores-products-v3.update",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        return _emit_safety_refusal(ctx, method="stores-products-v3.update", exc=exc)
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "stores-products-v3.update"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "stores-products-v3.update"}
        )
        return 1
