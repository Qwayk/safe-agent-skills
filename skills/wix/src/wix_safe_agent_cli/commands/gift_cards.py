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


def _normalize_create_body(raw: Any) -> dict[str, Any]:
    payload = _coerce_json_object(raw, field="gift-card-json")
    if "giftCard" in payload or "idempotencyKey" in payload:
        body = dict(payload)
    else:
        body = {"giftCard": payload}

    gift_card = body.get("giftCard")
    if not isinstance(gift_card, dict) or not gift_card:
        raise ValidationError("--gift-card-json must include a non-empty giftCard object")

    initial_value = gift_card.get("initialValue")
    if not isinstance(initial_value, dict) or not initial_value:
        raise ValidationError("--gift-card-json giftCard.initialValue must be a JSON object")
    _coerce_non_empty_text(initial_value.get("amount"), field="gift-card-json giftCard.initialValue.amount")
    _coerce_non_empty_text(gift_card.get("currency"), field="gift-card-json giftCard.currency")
    _coerce_non_empty_text(gift_card.get("source"), field="gift-card-json giftCard.source")
    return body


def _normalize_count_body(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _read_json_arg(raw, field="filter-json")
    if not isinstance(payload, dict):
        raise ValidationError("--filter-json must be a JSON object")
    if "filter" in payload:
        return payload
    return {"filter": payload}


def _normalize_optional_body(raw: Any, *, field: str) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    return payload


def _normalize_send_email_body(args: Any) -> dict[str, Any]:
    recipient_email = getattr(args, "recipient_email", None)
    if recipient_email is None:
        return {}
    return {"recipientEmail": _coerce_non_empty_text(recipient_email, field="recipient-email")}


def _resolve_gift_cards_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="gift-cards",
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


def _extract_gift_card(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    gift_card = payload.get("giftCard")
    if not isinstance(gift_card, dict):
        raise ValidationError(f"{operation} response did not include a giftCard object")
    return gift_card


def _extract_gift_card_id(gift_card: dict[str, Any], *, operation: str) -> str:
    raw_id = gift_card.get("id")
    if not isinstance(raw_id, str) or not raw_id.strip():
        raise ValidationError(f"{operation} response did not include a usable gift card id")
    return raw_id.strip()


def _get_gift_card(*, gift_card_id: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/gift-cards/v1/gift-cards/{gift_card_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_gift_card(payload, operation="gift-cards.get")


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
        "risk_reasons": ["wix-gift-card-write"] + (["irreversible"] if requires_ack else []),
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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="gift-cards")


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: gift card state changed since plan was created")


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


def cmd_gift_cards_get(args, ctx) -> int:
    try:
        gift_card_id = _coerce_non_empty_text(getattr(args, "gift_card_id", None), field="gift-card-id")
        headers, auth_mode = _resolve_gift_cards_auth(ctx=ctx)
        gift_card = _get_gift_card(gift_card_id=gift_card_id, ctx=ctx, headers=headers)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "gift-cards.get",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": f"/gift-cards/v1/gift-cards/{gift_card_id}"},
                "response": {"giftCard": gift_card},
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "gift-cards.get"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "gift-cards.get"})
        return 1


def cmd_gift_cards_query(args, ctx) -> int:
    try:
        body = _normalize_optional_body(getattr(args, "query_json", None), field="query-json")
        headers, auth_mode = _resolve_gift_cards_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/gift-cards/v1/gift-cards/query",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "gift-cards.query",
                "auth_mode": auth_mode,
                "request": {"method": "POST", "path": "/gift-cards/v1/gift-cards/query", "body": body},
                "response": payload,
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "gift-cards.query"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "gift-cards.query"})
        return 1


def cmd_gift_cards_search(args, ctx) -> int:
    try:
        body = _normalize_optional_body(getattr(args, "search_json", None), field="search-json")
        headers, auth_mode = _resolve_gift_cards_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/gift-cards/v1/gift-cards/search",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "gift-cards.search",
                "auth_mode": auth_mode,
                "request": {"method": "POST", "path": "/gift-cards/v1/gift-cards/search", "body": body},
                "response": payload,
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "gift-cards.search"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "gift-cards.search"})
        return 1


def cmd_gift_cards_count(args, ctx) -> int:
    try:
        body = _normalize_count_body(getattr(args, "filter_json", None))
        headers, auth_mode = _resolve_gift_cards_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/gift-cards/v1/gift-cards/count",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "gift-cards.count",
                "auth_mode": auth_mode,
                "request": {"method": "POST", "path": "/gift-cards/v1/gift-cards/count", "body": body},
                "response": payload,
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "gift-cards.count"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "gift-cards.count"})
        return 1


def cmd_gift_cards_create(args, ctx) -> int:
    try:
        body = _normalize_create_body(getattr(args, "gift_card_json", None))
        headers, auth_mode = _resolve_gift_cards_auth(ctx=ctx)

        request = {"method": "POST", "path": "/gift-cards/v1/gift-cards", "body": body}
        selector = {"kind": "wix-gift-card", "operation": "create"}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="gift-cards.create", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="gift-cards.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={},
                proposed_changes=[{"operation": "create", "body": body}],
                verification_plan={"type": "read-after-write", "notes": "Verify create response id and reread the created gift card."},
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "gift-cards.create",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="gift-cards.create", expected_selector=selector, ctx=ctx)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/gift-cards/v1/gift-cards",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_gift_card = _extract_gift_card(response, operation="gift-cards.create")
        gift_card_id = _extract_gift_card_id(created_gift_card, operation="gift-cards.create")
        after_gift_card = _get_gift_card(gift_card_id=gift_card_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_gift_card.get("id") or "") == gift_card_id,
            "type": "read-after-write",
            "path": f"/gift-cards/v1/gift-cards/{gift_card_id}",
            "method": "GET",
            "after": after_gift_card,
            "checks": [{"field": "id", "expected": gift_card_id, "actual": after_gift_card.get("id")}],
            "notes": "Create verification uses response id plus read-back get gift card.",
        }
        receipt = _build_receipt(
            method="gift-cards.create",
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
                "method": "gift-cards.create",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "gift-cards.create"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "gift-cards.create"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "gift-cards.create"})
        return 1


def cmd_gift_cards_disable(args, ctx) -> int:
    try:
        gift_card_id = _coerce_non_empty_text(getattr(args, "gift_card_id", None), field="gift-card-id")
        headers, auth_mode = _resolve_gift_cards_auth(ctx=ctx)
        current_gift_card = _get_gift_card(gift_card_id=gift_card_id, ctx=ctx, headers=headers)
        request = {"method": "POST", "path": f"/gift-cards/v1/gift-cards/{gift_card_id}/disable", "body": {}}
        selector = {"kind": "wix-gift-card", "operation": "disable", "gift_card_id": gift_card_id}
        before_state = {"giftCard": current_gift_card}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="gift-cards.disable", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="gift-cards.disable",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "disable", "gift_card_id": gift_card_id}],
                verification_plan={"type": "read-after-write", "notes": "Verify disable by rereading the gift card and checking disabledDate."},
                requires_ack=True,
                rollback_notes="No automatic rollback. Disabled gift cards cannot be re-enabled and their balance becomes inaccessible.",
            )

        if not _should_apply(ctx, requires_ack=True):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "gift-cards.disable",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="gift-cards.disable", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={"giftCard": _get_gift_card(gift_card_id=gift_card_id, ctx=ctx, headers=headers)},
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=f"/gift-cards/v1/gift-cards/{gift_card_id}/disable",
            headers=headers,
            params=None,
            json_body={},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_gift_card = _get_gift_card(gift_card_id=gift_card_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_gift_card.get("id") or "") == gift_card_id and bool(after_gift_card.get("disabledDate")),
            "type": "read-after-write",
            "path": f"/gift-cards/v1/gift-cards/{gift_card_id}",
            "method": "GET",
            "before": current_gift_card,
            "after": after_gift_card,
            "checks": [
                {"field": "id", "expected": gift_card_id, "actual": after_gift_card.get("id")},
                {"field": "disabledDate", "expected": "non-empty", "actual": after_gift_card.get("disabledDate")},
            ],
            "notes": "Disable verification uses read-back get gift card. Disable is irreversible.",
        }
        receipt = _build_receipt(
            method="gift-cards.disable",
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
                "method": "gift-cards.disable",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "gift-cards.disable"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "gift-cards.disable"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "gift-cards.disable"})
        return 1


def cmd_gift_cards_send_email(args, ctx) -> int:
    try:
        gift_card_id = _coerce_non_empty_text(getattr(args, "gift_card_id", None), field="gift-card-id")
        body = _normalize_send_email_body(args)
        headers, auth_mode = _resolve_gift_cards_auth(ctx=ctx)
        current_gift_card = _get_gift_card(gift_card_id=gift_card_id, ctx=ctx, headers=headers)
        request = {"method": "POST", "path": f"/gift-cards/v1/gift-cards/{gift_card_id}/send-email", "body": body}
        selector = {"kind": "wix-gift-card", "operation": "send-email", "gift_card_id": gift_card_id}
        before_state = {"giftCard": current_gift_card}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="gift-cards.send-email", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="gift-cards.send-email",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "send-email", "gift_card_id": gift_card_id, "body": body}],
                verification_plan={"type": "provider-response-plus-readback", "notes": "Verify the gift card still exists after send; email delivery itself is provider-side and out of band."},
                rollback_notes="No automatic rollback. Email delivery is provider-side and may require a premium site plan.",
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "gift-cards.send-email",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="gift-cards.send-email", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={"giftCard": _get_gift_card(gift_card_id=gift_card_id, ctx=ctx, headers=headers)},
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=f"/gift-cards/v1/gift-cards/{gift_card_id}/send-email",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_gift_card = _get_gift_card(gift_card_id=gift_card_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_gift_card.get("id") or "") == gift_card_id,
            "type": "provider-response-plus-readback",
            "path": f"/gift-cards/v1/gift-cards/{gift_card_id}",
            "method": "GET",
            "before": current_gift_card,
            "after": after_gift_card,
            "checks": [{"field": "id", "expected": gift_card_id, "actual": after_gift_card.get("id")}],
            "notes": "Premium site is required for delivery. This verification proves request acceptance and read-back existence, not inbox delivery.",
        }
        receipt = _build_receipt(
            method="gift-cards.send-email",
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
                "method": "gift-cards.send-email",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "gift-cards.send-email"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "gift-cards.send-email"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "gift-cards.send-email"})
        return 1
