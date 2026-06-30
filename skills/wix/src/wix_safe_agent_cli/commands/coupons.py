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

_COUPON_TYPE_FIELDS = (
    "moneyOffAmount",
    "percentOffRate",
    "freeShipping",
    "fixedPriceAmount",
    "buyXGetY",
)
_REQUIRED_INSTALLED_APPS = ("stores", "bookings", "events", "pricingPlans")


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


def _extract_specification(payload: dict[str, Any], *, field: str) -> dict[str, Any]:
    specification = payload.get("specification")
    if isinstance(specification, dict):
        return specification
    coupon = payload.get("coupon")
    if isinstance(coupon, dict) and isinstance(coupon.get("specification"), dict):
        return coupon["specification"]
    raise ValidationError(f"--{field} must include a specification object")


def _active_coupon_type_fields(specification: dict[str, Any]) -> list[str]:
    active: list[str] = []
    for name in _COUPON_TYPE_FIELDS:
        if name in specification and specification.get(name) is not None:
            active.append(name)
    return active


def _validate_create_coupon_payload(payload: dict[str, Any], *, field: str) -> None:
    specification = _extract_specification(payload, field=field)
    for required in ("name", "code", "startTime"):
        value = specification.get(required)
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(f"--{field} specification.{required} must be a non-empty string")
    type_fields = _active_coupon_type_fields(specification)
    if len(type_fields) != 1:
        raise ValidationError(
            f"--{field} specification must include exactly one coupon type field: {', '.join(_COUPON_TYPE_FIELDS)}"
        )
    coupon_type = type_fields[0]
    has_scope = specification.get("scope") is not None
    has_minimum_subtotal = specification.get("minimumSubtotal") is not None
    if coupon_type == "freeShipping":
        if has_scope:
            raise ValidationError(f"--{field} freeShipping coupons cannot include specification.scope")
    elif not has_scope and not has_minimum_subtotal:
        raise ValidationError(
            f"--{field} specification must include scope or minimumSubtotal for non-freeShipping coupons"
        )


def _detect_coupon_type(coupon: dict[str, Any]) -> str | None:
    specification = _extract_coupon_specification(coupon)
    if not specification:
        return None
    active = _active_coupon_type_fields(specification)
    if len(active) == 1:
        return active[0]
    return None


def _extract_coupon_specification(coupon: dict[str, Any]) -> dict[str, Any] | None:
    specification = coupon.get("specification")
    if isinstance(specification, dict):
        return specification
    return None


def _validate_update_coupon_payload(
    payload: dict[str, Any],
    *,
    current_coupon: dict[str, Any],
    field: str,
) -> None:
    specification = _extract_specification(payload, field=field)
    active = _active_coupon_type_fields(specification)
    mentioned_type_fields = [name for name in _COUPON_TYPE_FIELDS if name in specification]
    if len(active) > 1:
        raise ValidationError(
            f"--{field} specification can update at most one coupon type field: {', '.join(_COUPON_TYPE_FIELDS)}"
        )
    if mentioned_type_fields:
        current_type = _detect_coupon_type(current_coupon)
        if current_type is None:
            raise SafetyError("Refused: current coupon type could not be determined safely")
        if len(active) != 1 or active[0] != current_type:
            raise SafetyError("Refused: updating a coupon cannot change the coupon type")


def _normalize_query_body(raw: Any, *, field: str) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    return payload


def _normalize_bulk_create_body(raw: Any, *, field: str) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if isinstance(payload, list):
        if not payload:
            raise ValidationError(f"--{field} cannot be an empty array")
        for index, item in enumerate(payload):
            if not isinstance(item, dict):
                raise ValidationError(f"--{field}[{index}] must be a JSON object")
            _validate_create_coupon_payload(item, field=field)
        return {"coupons": payload}
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON array or object")
    coupons = payload.get("coupons")
    if not isinstance(coupons, list) or not coupons:
        raise ValidationError(f"--{field} must include a non-empty coupons array")
    for index, item in enumerate(coupons):
        if not isinstance(item, dict):
            raise ValidationError(f"--{field} coupons[{index}] must be a JSON object")
        _validate_create_coupon_payload(item, field=field)
    return payload


def _normalize_bulk_delete_body(raw: Any, *, field: str) -> tuple[dict[str, Any], list[str]]:
    payload = _read_json_arg(raw, field=field)
    ids: list[str]
    if isinstance(payload, list):
        ids = [_coerce_non_empty_text(value, field=field) for value in payload]
        if not ids:
            raise ValidationError(f"--{field} cannot be an empty array")
        return {"ids": ids}, ids
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON array or object")
    raw_ids = payload.get("ids")
    if raw_ids is None:
        raw_ids = payload.get("couponIds")
    if not isinstance(raw_ids, list) or not raw_ids:
        raise ValidationError(f"--{field} must include a non-empty ids or couponIds array")
    ids = [_coerce_non_empty_text(value, field=field) for value in raw_ids]
    return payload, ids


def _resolve_coupons_auth_and_preflight(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="coupons",
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
    if not _app_has_required_coupon_app(payload=instance_payload):
        allowed = ", ".join(_REQUIRED_INSTALLED_APPS)
        raise ValidationError(f"Required installed Wix app missing for coupons. Expected one of: {allowed}.")
    return auth["headers"], auth["mode"]


def _app_has_required_coupon_app(*, payload: dict[str, Any]) -> bool:
    if not isinstance(payload, dict):
        return False
    site = payload.get("site")
    if not isinstance(site, dict):
        return False
    installed = site.get("installedWixApps")
    if not isinstance(installed, list):
        return False
    installed_set = {name for name in installed if isinstance(name, str)}
    return any(name in installed_set for name in _REQUIRED_INSTALLED_APPS)


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


def _extract_coupon(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    coupon = payload.get("coupon")
    if isinstance(coupon, dict):
        return coupon
    if isinstance(payload.get("id"), str):
        return payload
    raise ValidationError(f"{operation} response did not include a coupon object")


def _extract_coupon_optional(payload: dict[str, Any]) -> dict[str, Any] | None:
    try:
        return _extract_coupon(payload, operation="coupons")
    except ValidationError:
        return None


def _extract_coupon_id(coupon: dict[str, Any], *, operation: str) -> str:
    raw_id = coupon.get("id")
    if not isinstance(raw_id, str) or not raw_id.strip():
        raise ValidationError(f"{operation} response did not include a usable coupon id")
    return raw_id.strip()


def _extract_coupons_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    coupons = payload.get("coupons")
    if not isinstance(coupons, list):
        return []
    return [item for item in coupons if isinstance(item, dict)]


def _get_coupon(*, coupon_id: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/stores/v2/coupons/{coupon_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_coupon(payload, operation="coupons.get")


def _get_coupon_optional(
    *,
    coupon_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> tuple[dict[str, Any] | None, int | None]:
    try:
        return _get_coupon(coupon_id=coupon_id, ctx=ctx, headers=headers), None
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            return None, 404
        raise


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
        "risk_reasons": ["wix-coupon-write"] + (["irreversible"] if requires_ack else []),
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


def _should_apply(ctx: dict[str, Any], *, requires_ack: bool = False) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="coupons")


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: coupon state changed since plan was created")


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


def cmd_coupons_get(args, ctx) -> int:
    try:
        coupon_id = _coerce_non_empty_text(getattr(args, "coupon_id", None), field="coupon-id")
        headers, auth_mode = _resolve_coupons_auth_and_preflight(ctx=ctx)
        coupon = _get_coupon(coupon_id=coupon_id, ctx=ctx, headers=headers)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "coupons.get",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": f"/stores/v2/coupons/{coupon_id}"},
                "response": {"coupon": coupon},
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "coupons.get"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "coupons.get"})
        return 1


def cmd_coupons_query(args, ctx) -> int:
    try:
        body = _normalize_query_body(getattr(args, "query_json", None), field="query-json")
        headers, auth_mode = _resolve_coupons_auth_and_preflight(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/stores/v2/coupons/query",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "coupons.query",
                "auth_mode": auth_mode,
                "request": {"method": "POST", "path": "/stores/v2/coupons/query", "body": body},
                "response": payload,
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "coupons.query"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "coupons.query"})
        return 1


def cmd_coupons_create(args, ctx) -> int:
    try:
        coupon_json = _coerce_json_object(getattr(args, "coupon_json", None), field="coupon-json")
        _validate_create_coupon_payload(coupon_json, field="coupon-json")
        headers, auth_mode = _resolve_coupons_auth_and_preflight(ctx=ctx)
        request = {"method": "POST", "path": "/stores/v2/coupons", "body": coupon_json}
        selector = {"kind": "wix-coupon", "operation": "create"}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="coupons.create", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="coupons.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={},
                proposed_changes=[{"operation": "create", "body": coupon_json}],
                verification_plan={"type": "best-effort-read-after-write", "notes": "Verify with created coupon id when the provider response includes it."},
            )
        if not _should_apply(ctx):
            ctx["out"].emit({"ok": True, "dry_run": True, "method": "coupons.create", "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)})
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="coupons.create", expected_selector=selector, ctx=ctx)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/stores/v2/coupons",
            headers=headers,
            params=None,
            json_body=coupon_json,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_coupon = _extract_coupon_optional(response)
        created_id = None
        after_coupon = None
        verification: dict[str, Any]
        if created_coupon is not None:
            created_id = _extract_coupon_id(created_coupon, operation="coupons.create")
            after_coupon = _get_coupon(coupon_id=created_id, ctx=ctx, headers=headers)
            verification = {
                "ok": str(after_coupon.get("id") or "") == created_id,
                "type": "read-after-write",
                "path": f"/stores/v2/coupons/{created_id}",
                "method": "GET",
                "after": after_coupon,
                "checks": [{"field": "id", "expected": created_id, "actual": after_coupon.get("id")}],
                "notes": "Create verification uses response id plus read-back get coupon.",
            }
        else:
            verification = {
                "ok": True,
                "type": "provider-response-only",
                "notes": "Provider response did not expose a created coupon object for read-back verification in this boundary.",
            }
        receipt = _build_receipt(
            method="coupons.create",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit({"ok": bool(verification.get("ok")), "dry_run": False, "method": "coupons.create", "auth_mode": auth_mode, "receipt": receipt, "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt)})
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "coupons.create"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "coupons.create"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "coupons.create"})
        return 1


def cmd_coupons_update(args, ctx) -> int:
    try:
        coupon_id = _coerce_non_empty_text(getattr(args, "coupon_id", None), field="coupon-id")
        coupon_json = _coerce_json_object(getattr(args, "coupon_json", None), field="coupon-json")
        headers, auth_mode = _resolve_coupons_auth_and_preflight(ctx=ctx)
        current_coupon = _get_coupon(coupon_id=coupon_id, ctx=ctx, headers=headers)
        _validate_update_coupon_payload(coupon_json, current_coupon=current_coupon, field="coupon-json")

        request = {"method": "PATCH", "path": f"/stores/v2/coupons/{coupon_id}", "body": coupon_json}
        selector = {"kind": "wix-coupon", "operation": "update", "coupon_id": coupon_id}
        before_state = {"coupon": current_coupon}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="coupons.update", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="coupons.update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "update", "coupon_id": coupon_id, "body": coupon_json}],
                verification_plan={"type": "read-after-write", "notes": "Verify the updated coupon by rereading the same coupon id."},
            )
        if not _should_apply(ctx):
            ctx["out"].emit({"ok": True, "dry_run": True, "method": "coupons.update", "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)})
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="coupons.update", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(plan=loaded_plan, current_state={"coupon": _get_coupon(coupon_id=coupon_id, ctx=ctx, headers=headers)})
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/stores/v2/coupons/{coupon_id}",
            headers=headers,
            params=None,
            json_body=coupon_json,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_coupon = _get_coupon(coupon_id=coupon_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_coupon.get("id") or "") == coupon_id,
            "type": "read-after-write",
            "path": f"/stores/v2/coupons/{coupon_id}",
            "method": "GET",
            "before": current_coupon,
            "after": after_coupon,
            "checks": [{"field": "id", "expected": coupon_id, "actual": after_coupon.get("id")}],
            "notes": "Update verification uses read-back get coupon.",
        }
        receipt = _build_receipt(
            method="coupons.update",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit({"ok": bool(verification.get("ok")), "dry_run": False, "method": "coupons.update", "auth_mode": auth_mode, "receipt": receipt, "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt)})
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "coupons.update"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "coupons.update"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "coupons.update"})
        return 1


def cmd_coupons_delete(args, ctx) -> int:
    try:
        coupon_id = _coerce_non_empty_text(getattr(args, "coupon_id", None), field="coupon-id")
        headers, auth_mode = _resolve_coupons_auth_and_preflight(ctx=ctx)
        current_coupon = _get_coupon(coupon_id=coupon_id, ctx=ctx, headers=headers)
        request = {"method": "DELETE", "path": f"/stores/v2/coupons/{coupon_id}"}
        selector = {"kind": "wix-coupon", "operation": "delete", "coupon_id": coupon_id}
        before_state = {"coupon": current_coupon}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="coupons.delete", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="coupons.delete",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "delete", "coupon_id": coupon_id}],
                verification_plan={"type": "read-after-write", "notes": "Verify delete by expecting get coupon to return 404."},
                requires_ack=True,
            )
        if not _should_apply(ctx, requires_ack=True):
            ctx["out"].emit({"ok": True, "dry_run": True, "method": "coupons.delete", "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)})
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="coupons.delete", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(plan=loaded_plan, current_state={"coupon": _get_coupon(coupon_id=coupon_id, ctx=ctx, headers=headers)})
        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/stores/v2/coupons/{coupon_id}",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_coupon, after_status = _get_coupon_optional(coupon_id=coupon_id, ctx=ctx, headers=headers)
        verification = {
            "ok": after_status == 404 and after_coupon is None,
            "type": "read-after-write",
            "path": f"/stores/v2/coupons/{coupon_id}",
            "method": "GET",
            "before": current_coupon,
            "after": after_coupon,
            "expected_http_status": 404,
            "actual_http_status": after_status,
            "notes": "Delete verification expects get coupon to return 404.",
        }
        receipt = _build_receipt(
            method="coupons.delete",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit({"ok": bool(verification.get("ok")), "dry_run": False, "method": "coupons.delete", "auth_mode": auth_mode, "receipt": receipt, "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt)})
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "coupons.delete"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "coupons.delete"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "coupons.delete"})
        return 1


def cmd_coupons_bulk_create(args, ctx) -> int:
    try:
        body = _normalize_bulk_create_body(getattr(args, "coupons_json", None), field="coupons-json")
        headers, auth_mode = _resolve_coupons_auth_and_preflight(ctx=ctx)
        coupons = body.get("coupons", [])
        request = {"method": "POST", "path": "/stores/v2/bulk/coupons/create", "body": body}
        selector = {"kind": "wix-coupon", "operation": "bulk-create", "count": len(coupons)}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="coupons.bulk-create", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="coupons.bulk-create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={},
                proposed_changes=[{"operation": "bulk-create", "count": len(coupons), "codes": [item.get("specification", {}).get("code") for item in coupons if isinstance(item, dict)]}],
                verification_plan={"type": "best-effort-read-after-write", "notes": "Verify created coupon ids when the provider response exposes them."},
            )
        if not _should_apply(ctx):
            ctx["out"].emit({"ok": True, "dry_run": True, "method": "coupons.bulk-create", "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)})
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="coupons.bulk-create", expected_selector=selector, ctx=ctx)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/stores/v2/bulk/coupons/create",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_coupons = _extract_coupons_from_payload(response)
        created_ids = [coupon.get("id") for coupon in created_coupons if isinstance(coupon.get("id"), str)]
        if created_ids:
            after_coupons = []
            for coupon_id in created_ids:
                after_coupons.append(_get_coupon(coupon_id=str(coupon_id), ctx=ctx, headers=headers))
            verification = {
                "ok": len(after_coupons) == len(created_ids),
                "type": "read-after-write",
                "method": "GET",
                "paths": [f"/stores/v2/coupons/{coupon_id}" for coupon_id in created_ids],
                "after": after_coupons,
                "notes": "Bulk create verification rereads every created coupon id returned by the provider.",
            }
        else:
            verification = {
                "ok": True,
                "type": "provider-response-only",
                "notes": "Provider response did not expose created coupon ids for read-back verification in this boundary.",
            }
        receipt = _build_receipt(
            method="coupons.bulk-create",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit({"ok": bool(verification.get("ok")), "dry_run": False, "method": "coupons.bulk-create", "auth_mode": auth_mode, "receipt": receipt, "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt)})
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "coupons.bulk-create"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "coupons.bulk-create"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "coupons.bulk-create"})
        return 1


def cmd_coupons_bulk_delete(args, ctx) -> int:
    try:
        body, coupon_ids = _normalize_bulk_delete_body(getattr(args, "coupon_ids_json", None), field="coupon-ids-json")
        headers, auth_mode = _resolve_coupons_auth_and_preflight(ctx=ctx)
        before_coupons = [_get_coupon(coupon_id=coupon_id, ctx=ctx, headers=headers) for coupon_id in coupon_ids]
        request = {"method": "POST", "path": "/stores/v2/bulk/coupons/delete", "body": body}
        selector = {"kind": "wix-coupon", "operation": "bulk-delete", "coupon_ids": coupon_ids}
        before_state = {"coupons": before_coupons}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="coupons.bulk-delete", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="coupons.bulk-delete",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "bulk-delete", "coupon_ids": coupon_ids}],
                verification_plan={"type": "read-after-write", "notes": "Verify bulk delete by expecting every get coupon call to return 404."},
                requires_ack=True,
            )
        if not _should_apply(ctx, requires_ack=True):
            ctx["out"].emit({"ok": True, "dry_run": True, "method": "coupons.bulk-delete", "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)})
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="coupons.bulk-delete", expected_selector=selector, ctx=ctx)
        current_state = {"coupons": [_get_coupon(coupon_id=coupon_id, ctx=ctx, headers=headers) for coupon_id in coupon_ids]}
        _assert_no_state_drift(plan=loaded_plan, current_state=current_state)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/stores/v2/bulk/coupons/delete",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        checks = []
        ok = True
        for coupon_id in coupon_ids:
            after_coupon, after_status = _get_coupon_optional(coupon_id=coupon_id, ctx=ctx, headers=headers)
            checks.append(
                {
                    "coupon_id": coupon_id,
                    "expected_http_status": 404,
                    "actual_http_status": after_status,
                    "after": after_coupon,
                }
            )
            if after_status != 404 or after_coupon is not None:
                ok = False
        verification = {
            "ok": ok,
            "type": "read-after-write",
            "method": "GET",
            "checks": checks,
            "notes": "Bulk delete verification expects every coupon get call to return 404.",
        }
        receipt = _build_receipt(
            method="coupons.bulk-delete",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit({"ok": bool(verification.get("ok")), "dry_run": False, "method": "coupons.bulk-delete", "auth_mode": auth_mode, "receipt": receipt, "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt)})
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "coupons.bulk-delete"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "coupons.bulk-delete"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "coupons.bulk-delete"})
        return 1
