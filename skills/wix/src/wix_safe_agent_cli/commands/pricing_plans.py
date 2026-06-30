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


def _resolve_pricing_plans_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="pricing-plans",
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


def _extract_plan(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    plan = payload.get("plan")
    if not isinstance(plan, dict):
        raise ValidationError(f"{operation} response did not include a plan object")
    return plan


def _extract_plan_id(plan: dict[str, Any], *, operation: str) -> str:
    raw_id = plan.get("id")
    if not isinstance(raw_id, str) or not raw_id.strip():
        raise ValidationError(f"{operation} response did not include a usable plan id")
    return raw_id.strip()


def _get_plan(*, plan_id: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/pricing-plans/v3/plans/{plan_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_plan(payload, operation="pricing-plans.get")


def _get_plan_optional(
    *,
    plan_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> tuple[dict[str, Any] | None, int | None]:
    try:
        return _get_plan(plan_id=plan_id, ctx=ctx, headers=headers), None
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            return None, 404
        raise


def _normalize_count_body(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _read_json_arg(raw, field="filter-json")
    if not isinstance(payload, dict):
        raise ValidationError("--filter-json must be a JSON object")
    if "filter" in payload:
        return payload
    return {"filter": payload}


def _normalize_bulk_update_body(raw: Any, *, field: str) -> tuple[dict[str, Any], list[str]]:
    payload = _read_json_arg(raw, field=field)
    if isinstance(payload, list):
        body = {"plans": payload}
    elif isinstance(payload, dict):
        body = dict(payload)
    else:
        raise ValidationError(f"--{field} must be a JSON array or object")

    raw_plans = body.get("plans")
    if not isinstance(raw_plans, list) or not raw_plans:
        raise ValidationError(f"--{field} must include a non-empty plans array")
    if len(raw_plans) > 100:
        raise ValidationError(f"--{field} plans array cannot include more than 100 plans")

    normalized_plans: list[dict[str, Any]] = []
    plan_ids: list[str] = []
    seen_ids: set[str] = set()

    for index, item in enumerate(raw_plans):
        if not isinstance(item, dict):
            raise ValidationError(f"--{field} plans[{index}] must be a JSON object")
        plan_obj = item.get("plan") if isinstance(item.get("plan"), dict) else item
        if not isinstance(plan_obj, dict) or not plan_obj:
            raise ValidationError(f"--{field} plans[{index}] must include a non-empty plan object")

        plan_id = _coerce_non_empty_text(plan_obj.get("id"), field=f"{field} plans[{index}].plan.id")
        _coerce_non_empty_text(plan_obj.get("revision"), field=f"{field} plans[{index}].plan.revision")
        if plan_id in seen_ids:
            raise ValidationError(f"--{field} contains duplicate plan id: {plan_id}")
        seen_ids.add(plan_id)
        plan_ids.append(plan_id)

        if "name" in plan_obj:
            raise ValidationError(
                f"--{field} plans[{index}].plan.name is not supported by Bulk Update Plans; "
                "use pricing-plans update to rename one plan"
            )

        pricing_variants = plan_obj.get("pricingVariants")
        if not isinstance(pricing_variants, list) or not pricing_variants:
            raise ValidationError(f"--{field} plans[{index}].plan.pricingVariants must be a non-empty array")
        for variant_index, variant in enumerate(pricing_variants):
            if not isinstance(variant, dict):
                raise ValidationError(
                    f"--{field} plans[{index}].plan.pricingVariants[{variant_index}] must be a JSON object"
                )
            _coerce_non_empty_text(
                variant.get("id"),
                field=f"{field} plans[{index}].plan.pricingVariants[{variant_index}].id",
            )
            _coerce_non_empty_text(
                variant.get("name"),
                field=f"{field} plans[{index}].plan.pricingVariants[{variant_index}].name",
            )
            billing_terms = variant.get("billingTerms")
            if not isinstance(billing_terms, dict) or not billing_terms:
                raise ValidationError(
                    f"--{field} plans[{index}].plan.pricingVariants[{variant_index}].billingTerms must be an object"
                )
            _coerce_non_empty_text(
                billing_terms.get("startType"),
                field=f"{field} plans[{index}].plan.pricingVariants[{variant_index}].billingTerms.startType",
            )
            _coerce_non_empty_text(
                billing_terms.get("endType"),
                field=f"{field} plans[{index}].plan.pricingVariants[{variant_index}].billingTerms.endType",
            )
            billing_cycle = billing_terms.get("billingCycle")
            if billing_cycle is not None:
                if not isinstance(billing_cycle, dict):
                    raise ValidationError(
                        f"--{field} plans[{index}].plan.pricingVariants[{variant_index}].billingTerms.billingCycle must be an object"
                    )
                _coerce_non_empty_text(
                    billing_cycle.get("period"),
                    field=f"{field} plans[{index}].plan.pricingVariants[{variant_index}].billingTerms.billingCycle.period",
                )
            pricing_strategies = variant.get("pricingStrategies")
            if not isinstance(pricing_strategies, list) or not pricing_strategies:
                raise ValidationError(
                    f"--{field} plans[{index}].plan.pricingVariants[{variant_index}].pricingStrategies must be a non-empty array"
                )

        normalized_plans.append({"plan": plan_obj})

    body["plans"] = normalized_plans
    body.setdefault("returnEntity", True)
    return body, plan_ids


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
        "risk_reasons": ["wix-pricing-plan-write"] + (["irreversible"] if requires_ack else []),
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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="pricing-plans")


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: pricing plan state changed since plan was created")


def _get_plans_by_id(*, plan_ids: list[str], ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    return {plan_id: _get_plan(plan_id=plan_id, ctx=ctx, headers=headers) for plan_id in plan_ids}


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


def cmd_pricing_plans_get(args, ctx) -> int:
    try:
        plan_id = _coerce_non_empty_text(getattr(args, "plan_id", None), field="plan-id")
        headers, auth_mode = _resolve_pricing_plans_auth(ctx=ctx)
        plan = _get_plan(plan_id=plan_id, ctx=ctx, headers=headers)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "pricing-plans.get",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": f"/pricing-plans/v3/plans/{plan_id}"},
                "response": {"plan": plan},
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "pricing-plans.get"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "pricing-plans.get"})
        return 1


def cmd_pricing_plans_query(args, ctx) -> int:
    try:
        query_json = getattr(args, "query_json", None)
        if query_json is None:
            body = {}
        else:
            body = _read_json_arg(query_json, field="query-json")
            if not isinstance(body, dict):
                raise ValidationError("--query-json must be a JSON object")
        headers, auth_mode = _resolve_pricing_plans_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/pricing-plans/v3/plans/query",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "pricing-plans.query",
                "auth_mode": auth_mode,
                "request": {"method": "POST", "path": "/pricing-plans/v3/plans/query", "body": body},
                "response": payload,
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "pricing-plans.query"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "pricing-plans.query"})
        return 1


def cmd_pricing_plans_search(args, ctx) -> int:
    try:
        search_json = getattr(args, "search_json", None)
        if search_json is None:
            body = {}
        else:
            body = _read_json_arg(search_json, field="search-json")
            if not isinstance(body, dict):
                raise ValidationError("--search-json must be a JSON object")
        headers, auth_mode = _resolve_pricing_plans_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/pricing-plans/v3/plans/search",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "pricing-plans.search",
                "auth_mode": auth_mode,
                "request": {"method": "POST", "path": "/pricing-plans/v3/plans/search", "body": body},
                "response": payload,
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "pricing-plans.search"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "pricing-plans.search"})
        return 1


def cmd_pricing_plans_count(args, ctx) -> int:
    try:
        body = _normalize_count_body(getattr(args, "filter_json", None))
        headers, auth_mode = _resolve_pricing_plans_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/pricing-plans/v3/plans/count",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "pricing-plans.count",
                "auth_mode": auth_mode,
                "request": {"method": "POST", "path": "/pricing-plans/v3/plans/count", "body": body},
                "response": payload,
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "pricing-plans.count"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "pricing-plans.count"})
        return 1


def cmd_pricing_plans_create(args, ctx) -> int:
    try:
        pricing_plan_json = _coerce_json_object(getattr(args, "pricing_plan_json", None), field="pricing-plan-json")
        headers, auth_mode = _resolve_pricing_plans_auth(ctx=ctx)

        request = {"method": "POST", "path": "/pricing-plans/v3/plans", "body": pricing_plan_json}
        selector = {"kind": "wix-pricing-plan", "operation": "create"}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="pricing-plans.create", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="pricing-plans.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={},
                proposed_changes=[{"operation": "create", "body": pricing_plan_json}],
                verification_plan={"type": "read-after-write", "notes": "Verify create response id and reread the created plan."},
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "pricing-plans.create",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="pricing-plans.create", expected_selector=selector, ctx=ctx)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/pricing-plans/v3/plans",
            headers=headers,
            params=None,
            json_body=pricing_plan_json,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_plan = _extract_plan(response, operation="pricing-plans.create")
        created_id = _extract_plan_id(created_plan, operation="pricing-plans.create")
        after_plan = _get_plan(plan_id=created_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_plan.get("id") or "") == created_id,
            "type": "read-after-write",
            "path": f"/pricing-plans/v3/plans/{created_id}",
            "method": "GET",
            "after": after_plan,
            "checks": [{"field": "id", "expected": created_id, "actual": after_plan.get("id")}],
            "notes": "Create verification uses response id plus read-back get plan.",
        }
        receipt = _build_receipt(
            method="pricing-plans.create",
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
                "method": "pricing-plans.create",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "pricing-plans.create"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "pricing-plans.create"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "pricing-plans.create"})
        return 1


def cmd_pricing_plans_update(args, ctx) -> int:
    try:
        plan_id = _coerce_non_empty_text(getattr(args, "plan_id", None), field="plan-id")
        pricing_plan_json = _coerce_json_object(getattr(args, "pricing_plan_json", None), field="pricing-plan-json")
        payload_plan_id = pricing_plan_json.get("id")
        if payload_plan_id is not None and str(payload_plan_id).strip() != plan_id:
            raise SafetyError("Refused: pricing plan id in body does not match --plan-id")

        headers, auth_mode = _resolve_pricing_plans_auth(ctx=ctx)
        current_plan = _get_plan(plan_id=plan_id, ctx=ctx, headers=headers)
        pricing_plan_json["id"] = plan_id

        request = {"method": "PATCH", "path": f"/pricing-plans/v3/plans/{plan_id}", "body": pricing_plan_json}
        selector = {"kind": "wix-pricing-plan", "operation": "update", "plan_id": plan_id}
        before_state = {"plan": current_plan}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="pricing-plans.update", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="pricing-plans.update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "update", "plan_id": plan_id, "body": pricing_plan_json}],
                verification_plan={"type": "read-after-write", "notes": "Verify the updated plan by rereading the same plan id."},
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "pricing-plans.update",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="pricing-plans.update", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(plan=loaded_plan, current_state={"plan": _get_plan(plan_id=plan_id, ctx=ctx, headers=headers)})
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/pricing-plans/v3/plans/{plan_id}",
            headers=headers,
            params=None,
            json_body=pricing_plan_json,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_plan = _get_plan(plan_id=plan_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_plan.get("id") or "") == plan_id,
            "type": "read-after-write",
            "path": f"/pricing-plans/v3/plans/{plan_id}",
            "method": "GET",
            "before": current_plan,
            "after": after_plan,
            "checks": [{"field": "id", "expected": plan_id, "actual": after_plan.get("id")}],
            "notes": "Update verification uses read-back get plan.",
        }
        receipt = _build_receipt(
            method="pricing-plans.update",
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
                "method": "pricing-plans.update",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "pricing-plans.update"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "pricing-plans.update"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "pricing-plans.update"})
        return 1


def cmd_pricing_plans_delete(args, ctx) -> int:
    try:
        plan_id = _coerce_non_empty_text(getattr(args, "plan_id", None), field="plan-id")
        headers, auth_mode = _resolve_pricing_plans_auth(ctx=ctx)
        current_plan = _get_plan(plan_id=plan_id, ctx=ctx, headers=headers)
        request = {"method": "DELETE", "path": f"/pricing-plans/v3/plans/{plan_id}"}
        selector = {"kind": "wix-pricing-plan", "operation": "delete", "plan_id": plan_id}
        before_state = {"plan": current_plan}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="pricing-plans.delete", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="pricing-plans.delete",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "delete", "plan_id": plan_id}],
                verification_plan={"type": "read-after-write", "notes": "Verify delete by expecting get plan to return 404."},
                requires_ack=True,
            )

        if not _should_apply(ctx, requires_ack=True):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "pricing-plans.delete",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="pricing-plans.delete", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(plan=loaded_plan, current_state={"plan": _get_plan(plan_id=plan_id, ctx=ctx, headers=headers)})
        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/pricing-plans/v3/plans/{plan_id}",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_plan, after_status = _get_plan_optional(plan_id=plan_id, ctx=ctx, headers=headers)
        verification = {
            "ok": after_status == 404 and after_plan is None,
            "type": "read-after-write",
            "path": f"/pricing-plans/v3/plans/{plan_id}",
            "method": "GET",
            "before": current_plan,
            "after": after_plan,
            "expected_http_status": 404,
            "actual_http_status": after_status,
            "notes": "Delete verification expects get plan to return 404.",
        }
        receipt = _build_receipt(
            method="pricing-plans.delete",
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
                "method": "pricing-plans.delete",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "pricing-plans.delete"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "pricing-plans.delete"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "pricing-plans.delete"})
        return 1


def cmd_pricing_plans_bulk_update(args, ctx) -> int:
    try:
        bulk_update_json = getattr(args, "bulk_update_json", None)
        body, plan_ids = _normalize_bulk_update_body(bulk_update_json, field="bulk-update-json")
        headers, auth_mode = _resolve_pricing_plans_auth(ctx=ctx)
        current_plans = _get_plans_by_id(plan_ids=plan_ids, ctx=ctx, headers=headers)

        request = {"method": "POST", "path": "/pricing-plans/v3/bulk/plans/update", "body": body}
        selector = {"kind": "wix-pricing-plan", "operation": "bulk-update", "plan_ids": plan_ids}
        before_state = {"plans": current_plans}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="pricing-plans.bulk-update",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="pricing-plans.bulk-update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[
                    {
                        "operation": "bulk-update",
                        "plan_ids": plan_ids,
                        "body": body,
                    }
                ],
                verification_plan={
                    "type": "bulk-response-plus-readback",
                    "notes": "Verify bulkActionMetadata.totalFailures is 0 and reread each target plan id.",
                },
                rollback_notes="No automatic rollback. Use the saved before-state snapshots only as a manual reference.",
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "pricing-plans.bulk-update",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="pricing-plans.bulk-update",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={"plans": _get_plans_by_id(plan_ids=plan_ids, ctx=ctx, headers=headers)},
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/pricing-plans/v3/bulk/plans/update",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_plans = _get_plans_by_id(plan_ids=plan_ids, ctx=ctx, headers=headers)
        metadata = response.get("bulkActionMetadata")
        metadata_ok = (
            isinstance(metadata, dict)
            and isinstance(metadata.get("totalFailures"), int)
            and metadata.get("totalFailures") == 0
        )
        verification = {
            "ok": bool(metadata_ok) and set(after_plans) == set(plan_ids),
            "type": "bulk-response-plus-readback",
            "path": "/pricing-plans/v3/bulk/plans/update",
            "method": "POST",
            "before": current_plans,
            "after": after_plans,
            "bulkActionMetadata": metadata,
            "checks": [{"plan_id": plan_id, "actual_id": after_plans.get(plan_id, {}).get("id")} for plan_id in plan_ids],
            "notes": "Bulk update verification checks bulkActionMetadata.totalFailures and rereads each target plan id.",
        }
        receipt = _build_receipt(
            method="pricing-plans.bulk-update",
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
                "method": "pricing-plans.bulk-update",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "refused": True,
                "reasons": [str(exc)],
                "refusal_type": "SafetyError",
                "method": "pricing-plans.bulk-update",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "pricing-plans.bulk-update"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "pricing-plans.bulk-update"}
        )
        return 1
