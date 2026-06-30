from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_RE = re.compile(r"^\+[1-9]\d{6,14}$")
_VALID_STATES = {"UNKNOWN_STATE", "NEVER_CONFIRMED", "REVOKED", "PENDING", "CONFIRMED"}


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


def _coerce_optional_non_empty_text(raw: Any, *, field: str) -> str | None:
    if raw is None:
        return None
    return _coerce_non_empty_text(raw, field=field)


def _coerce_email(raw: Any) -> str:
    value = _coerce_non_empty_text(raw, field="email")
    if not _EMAIL_RE.fullmatch(value):
        raise ValidationError("--email must be a valid email address")
    return value


def _coerce_phone(raw: Any) -> str:
    value = _coerce_non_empty_text(raw, field="phone")
    if not _PHONE_RE.fullmatch(value):
        raise ValidationError("--phone must be a valid E.164 phone number")
    return value


def _coerce_type(raw: Any) -> str:
    value = _coerce_non_empty_text(raw, field="type")
    if value not in {"EMAIL", "PHONE"}:
        raise ValidationError("--type must be EMAIL or PHONE")
    return value


def _unwrap_marketing_consent_payload(payload: dict[str, Any]) -> dict[str, Any]:
    nested = payload.get("marketingConsent")
    if isinstance(nested, dict) and len(payload) == 1:
        return dict(nested)
    return dict(payload)


def _normalize_details(details: Any) -> dict[str, Any]:
    if not isinstance(details, dict) or not details:
        raise ValidationError("--marketing-consent-json.details must be a non-empty JSON object")

    normalized = dict(details)
    consent_type = _coerce_type(normalized.get("type"))
    email = normalized.get("email")
    phone = normalized.get("phone")
    has_email = email is not None
    has_phone = phone is not None
    if has_email == has_phone:
        raise ValidationError("--marketing-consent-json.details must include exactly one of email or phone")
    if consent_type == "EMAIL":
        if not has_email:
            raise ValidationError("--marketing-consent-json.details.email is required when type is EMAIL")
        normalized["email"] = _coerce_email(email)
        normalized.pop("phone", None)
    else:
        if not has_phone:
            raise ValidationError("--marketing-consent-json.details.phone is required when type is PHONE")
        normalized["phone"] = _coerce_phone(phone)
        normalized.pop("email", None)
    normalized["type"] = consent_type
    return normalized


def _normalize_marketing_consent_object(value: Any, *, operation: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not value:
        raise ValidationError("--marketing-consent-json must be a non-empty JSON object")

    consent = _unwrap_marketing_consent_payload(value)
    if not isinstance(consent, dict) or not consent:
        raise ValidationError("--marketing-consent-json must be a non-empty JSON object")

    normalized = dict(consent)
    normalized["details"] = _normalize_details(normalized.get("details"))

    state = normalized.get("state")
    if operation == "create":
        if state is None:
            normalized["state"] = "CONFIRMED"
        else:
            normalized["state"] = _coerce_non_empty_text(state, field="marketing-consent-json.state")
            if normalized["state"] != "CONFIRMED":
                raise ValidationError(
                    "Create Marketing Consent only supports a CONFIRMED state; use upsert for other states"
                )
    else:
        normalized["state"] = _coerce_non_empty_text(state, field="marketing-consent-json.state")
        if normalized["state"] not in _VALID_STATES:
            raise ValidationError("--marketing-consent-json.state must be a valid marketing consent state")

    if normalized["state"] in {"PENDING", "CONFIRMED"}:
        confirmation_activity = normalized.get("lastConfirmationActivity")
        if not isinstance(confirmation_activity, dict) or not confirmation_activity:
            raise ValidationError(
                "--marketing-consent-json.lastConfirmationActivity is required when state is PENDING or CONFIRMED"
            )
    if normalized["state"] == "REVOKED":
        revoke_activity = normalized.get("lastRevokeActivity")
        if not isinstance(revoke_activity, dict) or not revoke_activity:
            raise ValidationError("--marketing-consent-json.lastRevokeActivity is required when state is REVOKED")

    return normalized


def _normalize_marketing_consent_payload(raw: Any, *, operation: str) -> dict[str, Any]:
    value = _read_json_arg(raw, field="marketing-consent-json")
    return _normalize_marketing_consent_object(value, operation=operation)


def _normalize_marketing_consent_update_payload(raw: Any) -> tuple[str, dict[str, Any]]:
    marketing_consent = _normalize_marketing_consent_payload(raw, operation="upsert")
    marketing_consent_id = _coerce_non_empty_text(
        marketing_consent.get("id") or marketing_consent.get("marketingConsentId"),
        field="marketing-consent-json.id",
    )
    marketing_consent["id"] = marketing_consent_id
    marketing_consent.pop("marketingConsentId", None)
    return marketing_consent_id, marketing_consent


def _normalize_mask_payload(raw: Any) -> dict[str, Any]:
    value = _read_json_arg(raw, field="mask-json")
    if not isinstance(value, dict) or not value:
        raise ValidationError("--mask-json must be a non-empty JSON object")
    paths = value.get("paths")
    if not isinstance(paths, list) or not paths:
        raise ValidationError("--mask-json.paths must be a non-empty JSON array")
    normalized_paths: list[str] = []
    for item in paths:
        if not isinstance(item, str) or not item.strip():
            raise ValidationError("--mask-json.paths entries must be non-empty strings")
        normalized_paths.append(item.strip())
    return {"paths": normalized_paths}


def _normalize_bulk_marketing_consents_payload(raw: Any) -> list[dict[str, Any]]:
    value = _read_json_arg(raw, field="marketing-consents-json")
    if isinstance(value, list):
        info = value
    elif isinstance(value, dict):
        info = value.get("info")
    else:
        info = None
    if not isinstance(info, list) or not info:
        raise ValidationError(
            "--marketing-consents-json must be a non-empty JSON array or an object with a non-empty info array"
        )
    if len(info) > 500:
        raise ValidationError("--marketing-consents-json supports at most 500 items")
    return [_normalize_marketing_consent_object(item, operation="upsert") for item in info]


def _normalize_last_revoke_activity(raw: Any) -> dict[str, Any]:
    value = _read_json_arg(raw, field="last-revoke-activity-json")
    if not isinstance(value, dict) or not value:
        raise ValidationError("--last-revoke-activity-json must be a non-empty JSON object")
    return dict(value)


def _normalize_last_confirmation_activity(raw: Any) -> dict[str, Any]:
    value = _read_json_arg(raw, field="marketing-consent-json")
    if not isinstance(value, dict) or not value:
        raise ValidationError("--marketing-consent-json must be a non-empty JSON object")
    return dict(value)


def _normalize_query_payload(raw: Any) -> dict[str, Any]:
    value = _read_json_arg(raw, field="query-json")
    if not isinstance(value, dict) or not value:
        raise ValidationError("--query-json must be a non-empty JSON object")

    normalized = dict(value)
    if "query" in normalized and isinstance(normalized["query"], dict):
        query = dict(normalized["query"])
    else:
        query = dict(normalized)
        normalized = {"query": query}

    if "cursor_paging" in query and "cursorPaging" not in query:
        query["cursorPaging"] = query.pop("cursor_paging")
    normalized["query"] = query

    cursor_paging = query.get("cursorPaging")
    if isinstance(cursor_paging, dict):
        limit = cursor_paging.get("limit")
        if limit is not None:
            if not isinstance(limit, int):
                raise ValidationError("--query-json.cursorPaging.limit must be an integer")
            if limit < 0 or limit > 100:
                raise ValidationError("--query-json.cursorPaging.limit must be between 0 and 100")
    return normalized


def _resolve_marketing_consent_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="marketing-consent",
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
    pieces = text.split()
    if len(pieces) < 2:
        return None
    try:
        return int(pieces[1])
    except ValueError:
        return None


def _extract_marketing_consent(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    marketing_consent = payload.get("marketingConsent")
    if not isinstance(marketing_consent, dict):
        raise ValidationError(f"{operation} response did not include a marketingConsent object")
    return marketing_consent


def _extract_marketing_consents(payload: dict[str, Any], *, operation: str) -> list[dict[str, Any]]:
    marketing_consents = payload.get("marketingConsent")
    if not isinstance(marketing_consents, list):
        raise ValidationError(f"{operation} response did not include a marketingConsent array")
    return [item for item in marketing_consents if isinstance(item, dict)]


def _build_identifier_params(
    *,
    consent_type: str,
    email: str | None,
    phone: str | None,
    link_language: str | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {"type": consent_type}
    if email is not None:
        params["email"] = email
    if phone is not None:
        params["phone"] = phone
    if link_language is not None:
        params["linkLanguage"] = link_language
    return params


def _get_marketing_consent_by_id(*, marketing_consent_id: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/marketing-consent/v1/marketing-consent/{marketing_consent_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_marketing_consent(payload, operation="marketing-consent.get")


def _get_marketing_consent_by_id_optional(
    *,
    marketing_consent_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> tuple[dict[str, Any] | None, int | None]:
    try:
        return _get_marketing_consent_by_id(marketing_consent_id=marketing_consent_id, ctx=ctx, headers=headers), None
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            return None, 404
        raise


def _get_marketing_consent_by_identifier(
    *,
    consent_type: str,
    email: str | None,
    phone: str | None,
    link_language: str | None,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path="/marketing-consent/v1/marketing-consent/get-by",
        headers=headers,
        params=_build_identifier_params(
            consent_type=consent_type,
            email=email,
            phone=phone,
            link_language=link_language,
        ),
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_marketing_consent(payload, operation="marketing-consent.get-by-identifier")


def _get_marketing_consent_by_identifier_optional(
    *,
    consent_type: str,
    email: str | None,
    phone: str | None,
    link_language: str | None,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> tuple[dict[str, Any] | None, int | None]:
    try:
        return (
            _get_marketing_consent_by_identifier(
                consent_type=consent_type,
                email=email,
                phone=phone,
                link_language=link_language,
                ctx=ctx,
                headers=headers,
            ),
            None,
        )
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
    before_state: dict[str, Any] | None,
    proposed_changes: list[dict[str, Any]],
    verification_plan: dict[str, Any],
    requires_ack: bool = False,
) -> dict[str, Any]:
    before_state_available = bool(before_state)
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
        "risk_reasons": ["marketing-consent-write"],
        "provider_notes": [
            "Create is for single-confirmation consent only. Use upsert for double-confirmation or other states.",
            "Get-by-identifier uses the official get-by endpoint, but the docs portal renders the query params badly.",
        ],
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        },
        "state_capture": {
            "before_state_available": before_state_available,
            "notes": (
                "Captured current marketing consent state before planning."
                if before_state_available
                else "No useful before-state snapshot exists for this create-style write."
            ),
        },
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "rollback": {
            "supported": False,
            "notes": (
                "No automatic rollback. Use the saved before-state only as a manual reference."
                if before_state_available
                else "No automatic rollback and no useful before-state snapshot."
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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="marketing-consent")


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any] | None) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: marketing consent state changed since plan was created")


def _build_verification(
    *,
    path: str,
    requested_details: dict[str, Any],
    after: dict[str, Any],
    method: str,
    expected_state: str,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    after_details = after.get("details")
    if not isinstance(after_details, dict):
        raise ValidationError(f"{method} readback did not include details")

    for field, expected in requested_details.items():
        checks.append({"field": f"details.{field}", "expected": expected, "actual": after_details.get(field)})
    checks.append({"field": "state", "expected": expected_state, "actual": after.get("state")})
    if expected_state == "REVOKED" and "communicationEligibility" in after:
        communication_eligibility = after.get("communicationEligibility")
        granted = communication_eligibility.get("granted") if isinstance(communication_eligibility, dict) else None
        checks.append({"field": "communicationEligibility.granted", "expected": False, "actual": granted})
    return {
        "ok": all(item["expected"] == item["actual"] for item in checks),
        "type": "read-after-write",
        "path": path,
        "method": "GET",
        "checks": checks,
        "after": after,
    }


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
            "before_state_available": bool(before_state),
            "notes": (
                "Receipt stores the pre-apply marketing consent snapshot."
                if before_state
                else "Receipt stores no useful before-state snapshot."
            ),
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": (
                "Recovery is manual only. Use the reviewed plan snapshot as a reference."
                if before_state
                else "Recovery is manual only and no useful before-state snapshot was available."
            ),
        },
    }


def _build_identifier_selector(*, consent_type: str, email: str | None, phone: str | None) -> dict[str, Any]:
    selector = {"type": consent_type}
    if email is not None:
        selector["email"] = email
    if phone is not None:
        selector["phone"] = phone
    return selector


def _read_by_identifier_args(args) -> tuple[str, str | None, str | None, str | None]:
    consent_type = _coerce_type(getattr(args, "type", None))
    email = getattr(args, "email", None)
    phone = getattr(args, "phone", None)
    if (email is None) == (phone is None):
        raise ValidationError("Provide exactly one of --email or --phone")
    if consent_type == "EMAIL":
        if phone is not None:
            raise ValidationError("--phone cannot be used when --type is EMAIL")
        email_value = _coerce_email(email)
        return consent_type, email_value, None, _coerce_optional_non_empty_text(getattr(args, "link_language", None), field="link-language")
    if email is not None:
        raise ValidationError("--email cannot be used when --type is PHONE")
    phone_value = _coerce_phone(phone)
    return consent_type, None, phone_value, _coerce_optional_non_empty_text(getattr(args, "link_language", None), field="link-language")


def _write_request_body(marketing_consent: dict[str, Any]) -> dict[str, Any]:
    return {"marketingConsent": marketing_consent}


def _expected_state_for_upsert(*, requested_state: str, before_state: dict[str, Any] | None, consent_type: str) -> str:
    if requested_state == "UNKNOWN_STATE" and consent_type == "EMAIL" and before_state and before_state.get("state") != "UNKNOWN_STATE":
        return str(before_state.get("state"))
    return requested_state


def _effective_update_state(*, requested_state: str, current_state: dict[str, Any] | None, consent_type: str) -> str:
    if requested_state == "UNKNOWN_STATE" and consent_type == "EMAIL" and current_state and current_state.get("state") != "UNKNOWN_STATE":
        return str(current_state.get("state"))
    return requested_state


def _assert_required_activity_for_state(marketing_consent: dict[str, Any], *, effective_state: str) -> None:
    if effective_state in {"PENDING", "CONFIRMED"}:
        confirmation_activity = marketing_consent.get("lastConfirmationActivity")
        if not isinstance(confirmation_activity, dict) or not confirmation_activity:
            raise ValidationError(
                "--marketing-consent-json.lastConfirmationActivity is required when state is PENDING or CONFIRMED"
            )
    if effective_state == "REVOKED":
        revoke_activity = marketing_consent.get("lastRevokeActivity")
        if not isinstance(revoke_activity, dict) or not revoke_activity:
            raise ValidationError("--marketing-consent-json.lastRevokeActivity is required when state is REVOKED")


def _build_bulk_upsert_verification(*, response: dict[str, Any], expected_count: int) -> dict[str, Any]:
    results = response.get("results")
    metadata = response.get("metadata")
    if not isinstance(results, list):
        raise ValidationError("marketing-consent.bulk-upsert response did not include a results array")
    if not isinstance(metadata, dict):
        raise ValidationError("marketing-consent.bulk-upsert response did not include metadata")

    total_success = metadata.get("totalSuccess")
    total_failure = metadata.get("totalFailure")
    totals = metadata.get("totals")
    if isinstance(totals, dict):
        if total_success is None:
            total_success = totals.get("succeeded")
        if total_failure is None:
            total_failure = totals.get("failed")
    if not isinstance(total_success, int) or not isinstance(total_failure, int):
        raise ValidationError("marketing-consent.bulk-upsert response metadata did not include integer success/failure totals")

    result_errors = [item.get("error") for item in results if isinstance(item, dict) and item.get("error")]
    checks = [
        {"field": "metadata.totalSuccess", "expected": expected_count, "actual": total_success},
        {"field": "metadata.totalFailure", "expected": 0, "actual": total_failure},
        {"field": "results.length", "expected": expected_count, "actual": len(results)},
        {"field": "results.error_count", "expected": 0, "actual": len(result_errors)},
    ]
    return {
        "ok": all(item["expected"] == item["actual"] for item in checks),
        "type": "provider-response",
        "checks": checks,
        "after": response,
    }


def cmd_marketing_consent_get(args, ctx) -> int:
    try:
        marketing_consent_id = _coerce_non_empty_text(getattr(args, "marketing_consent_id", None), field="marketing-consent-id")
        headers, auth_mode = _resolve_marketing_consent_auth(ctx=ctx)
        marketing_consent = _get_marketing_consent_by_id(
            marketing_consent_id=marketing_consent_id,
            ctx=ctx,
            headers=headers,
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "marketing-consent.get",
                "auth_mode": auth_mode,
                "request": {
                    "method": "GET",
                    "path": f"/marketing-consent/v1/marketing-consent/{marketing_consent_id}",
                },
                "response": {"marketingConsent": marketing_consent},
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "marketing-consent.get"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "marketing-consent.get"}
        )
        return 1


def cmd_marketing_consent_get_by_identifier(args, ctx) -> int:
    try:
        consent_type, email, phone, link_language = _read_by_identifier_args(args)
        headers, auth_mode = _resolve_marketing_consent_auth(ctx=ctx)
        marketing_consent = _get_marketing_consent_by_identifier(
            consent_type=consent_type,
            email=email,
            phone=phone,
            link_language=link_language,
            ctx=ctx,
            headers=headers,
        )
        request_params = _build_identifier_params(
            consent_type=consent_type,
            email=email,
            phone=phone,
            link_language=link_language,
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "marketing-consent.get-by-identifier",
                "auth_mode": auth_mode,
                "request": {
                    "method": "GET",
                    "path": "/marketing-consent/v1/marketing-consent/get-by",
                    "params": request_params,
                },
                "response": {"marketingConsent": marketing_consent},
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "marketing-consent.get-by-identifier",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "marketing-consent.get-by-identifier",
            }
        )
        return 1


def cmd_marketing_consent_query(args, ctx) -> int:
    try:
        query_payload = _normalize_query_payload(getattr(args, "query_json", None))
        headers, auth_mode = _resolve_marketing_consent_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/marketing-consent/v1/marketing-consent/query",
            headers=headers,
            params=None,
            json_body=query_payload,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "marketing-consent.query",
                "auth_mode": auth_mode,
                "request": {
                    "method": "POST",
                    "path": "/marketing-consent/v1/marketing-consent/query",
                    "body": query_payload,
                },
                "response": payload,
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "marketing-consent.query"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "marketing-consent.query"}
        )
        return 1


def cmd_marketing_consent_create(args, ctx) -> int:
    try:
        marketing_consent = _normalize_marketing_consent_payload(getattr(args, "marketing_consent_json", None), operation="create")
        details = marketing_consent["details"]
        consent_type = str(details["type"])
        email = details.get("email")
        phone = details.get("phone")
        link_language = _coerce_optional_non_empty_text(getattr(args, "link_language", None), field="link-language")
        headers, auth_mode = _resolve_marketing_consent_auth(ctx=ctx)
        current_consent, _ = _get_marketing_consent_by_identifier_optional(
            consent_type=consent_type,
            email=email,
            phone=phone,
            link_language=link_language,
            ctx=ctx,
            headers=headers,
        )
        if current_consent is not None:
            raise SafetyError("Refused: a marketing consent already exists for this identifier; use upsert instead")

        request_body = _write_request_body(marketing_consent)
        request = {
            "method": "POST",
            "path": "/marketing-consent/v1/marketing-consent",
            "body": request_body,
        }
        selector = {
            "kind": "wix-marketing-consent",
            "operation": "create",
            "identifier": _build_identifier_selector(consent_type=consent_type, email=email, phone=phone),
        }
        before_state = current_consent
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="marketing-consent.create",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="marketing-consent.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[
                    {
                        "operation": "create",
                        "identifier": selector["identifier"],
                        "state": marketing_consent["state"],
                    }
                ],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Read back by identifier and compare details/type/state.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "marketing-consent.create",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="marketing-consent.create",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(plan=loaded_plan, current_state=before_state)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/marketing-consent/v1/marketing-consent",
            headers=headers,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        marketing_consent_response = _extract_marketing_consent(response, operation="marketing-consent.create")
        after_marketing_consent = _get_marketing_consent_by_identifier(
            consent_type=consent_type,
            email=email,
            phone=phone,
            link_language=link_language,
            ctx=ctx,
            headers=headers,
        )
        expected_state = marketing_consent["state"]
        verification = _build_verification(
            path="/marketing-consent/v1/marketing-consent/get-by",
            requested_details=details,
            after=after_marketing_consent,
            method="marketing-consent.create",
            expected_state=expected_state,
        )
        receipt = _build_receipt(
            method="marketing-consent.create",
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
                "method": "marketing-consent.create",
                "auth_mode": auth_mode,
                "response": {"marketingConsent": marketing_consent_response},
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
                "method": "marketing-consent.create",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "marketing-consent.create"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "marketing-consent.create"}
        )
        return 1


def cmd_marketing_consent_upsert(args, ctx) -> int:
    try:
        marketing_consent = _normalize_marketing_consent_payload(getattr(args, "marketing_consent_json", None), operation="upsert")
        details = marketing_consent["details"]
        consent_type = str(details["type"])
        email = details.get("email")
        phone = details.get("phone")
        link_language = _coerce_optional_non_empty_text(getattr(args, "link_language", None), field="link-language")
        headers, auth_mode = _resolve_marketing_consent_auth(ctx=ctx)
        current_consent, _ = _get_marketing_consent_by_identifier_optional(
            consent_type=consent_type,
            email=email,
            phone=phone,
            link_language=link_language,
            ctx=ctx,
            headers=headers,
        )
        request_body = _write_request_body(marketing_consent)
        request = {
            "method": "POST",
            "path": "/marketing-consent/v1/marketing-consent/upsert",
            "body": request_body,
        }
        selector = {
            "kind": "wix-marketing-consent",
            "operation": "upsert",
            "identifier": _build_identifier_selector(consent_type=consent_type, email=email, phone=phone),
            "state": marketing_consent["state"],
        }
        before_state = current_consent
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="marketing-consent.upsert",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="marketing-consent.upsert",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[
                    {
                        "operation": "upsert",
                        "identifier": selector["identifier"],
                        "state": marketing_consent["state"],
                    }
                ],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Read back by identifier and compare details/type/state.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "marketing-consent.upsert",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="marketing-consent.upsert",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(plan=loaded_plan, current_state=before_state)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/marketing-consent/v1/marketing-consent/upsert",
            headers=headers,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        marketing_consent_response = _extract_marketing_consent(response, operation="marketing-consent.upsert")
        after_marketing_consent = _get_marketing_consent_by_identifier(
            consent_type=consent_type,
            email=email,
            phone=phone,
            link_language=link_language,
            ctx=ctx,
            headers=headers,
        )
        expected_state = _expected_state_for_upsert(
            requested_state=marketing_consent["state"],
            before_state=before_state,
            consent_type=consent_type,
        )
        verification = _build_verification(
            path="/marketing-consent/v1/marketing-consent/get-by",
            requested_details=details,
            after=after_marketing_consent,
            method="marketing-consent.upsert",
            expected_state=expected_state,
        )
        receipt = _build_receipt(
            method="marketing-consent.upsert",
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
                "method": "marketing-consent.upsert",
                "auth_mode": auth_mode,
                "response": {"marketingConsent": marketing_consent_response},
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
                "method": "marketing-consent.upsert",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "marketing-consent.upsert"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "marketing-consent.upsert"}
        )
        return 1


def cmd_marketing_consent_update(args, ctx) -> int:
    try:
        marketing_consent_id, marketing_consent = _normalize_marketing_consent_update_payload(
            getattr(args, "marketing_consent_json", None)
        )
        mask = _normalize_mask_payload(getattr(args, "mask_json", None))
        if bool(ctx.get("apply")) and not ctx.get("plan_in") and not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "refused": True,
                    "reasons": ["Refused: reviewed apply requires --plan-in from a prior reviewed dry-run"],
                    "refusal_type": "SafetyError",
                    "method": "marketing-consent.update",
                }
            )
            return 0
        details = marketing_consent["details"]
        headers, auth_mode = _resolve_marketing_consent_auth(ctx=ctx)
        current_consent = _get_marketing_consent_by_id(
            marketing_consent_id=marketing_consent_id,
            ctx=ctx,
            headers=headers,
        )
        effective_state = _effective_update_state(
            requested_state=marketing_consent["state"],
            current_state=current_consent,
            consent_type=str(details["type"]),
        )
        _assert_required_activity_for_state(marketing_consent, effective_state=effective_state)

        request_body = {"marketingConsent": marketing_consent, "mask": mask}
        request = {
            "method": "PATCH",
            "path": f"/marketing-consent/v1/marketing-consent/{marketing_consent_id}",
            "body": request_body,
        }
        selector = {
            "kind": "wix-marketing-consent",
            "operation": "update",
            "marketing_consent_id": marketing_consent_id,
            "mask": mask["paths"],
        }
        before_state = {"marketingConsent": current_consent}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="marketing-consent.update",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="marketing-consent.update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[
                    {
                        "operation": "update",
                        "marketingConsentId": marketing_consent_id,
                        "mask": mask["paths"],
                        "state": effective_state,
                    }
                ],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Read back by id and compare details/type/state after apply.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "marketing-consent.update",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="marketing-consent.update",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={"marketingConsent": current_consent},
        )
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/marketing-consent/v1/marketing-consent/{marketing_consent_id}",
            headers=headers,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        marketing_consent_response = _extract_marketing_consent(response, operation="marketing-consent.update")
        after_marketing_consent = _get_marketing_consent_by_id(
            marketing_consent_id=marketing_consent_id,
            ctx=ctx,
            headers=headers,
        )
        verification = _build_verification(
            path=f"/marketing-consent/v1/marketing-consent/{marketing_consent_id}",
            requested_details=details,
            after=after_marketing_consent,
            method="marketing-consent.update",
            expected_state=effective_state,
        )
        receipt = _build_receipt(
            method="marketing-consent.update",
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
                "method": "marketing-consent.update",
                "auth_mode": auth_mode,
                "response": {"marketingConsent": marketing_consent_response},
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
                "method": "marketing-consent.update",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "marketing-consent.update"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "marketing-consent.update"}
        )
        return 1


def cmd_marketing_consent_delete(args, ctx) -> int:
    try:
        marketing_consent_id = _coerce_non_empty_text(getattr(args, "marketing_consent_id", None), field="marketing-consent-id")
        if bool(ctx.get("apply")) and not ctx.get("plan_in") and not _should_apply(ctx, requires_ack=True):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "refused": True,
                    "reasons": ["Refused: reviewed apply requires --plan-in from a prior reviewed dry-run"],
                    "refusal_type": "SafetyError",
                    "method": "marketing-consent.delete",
                }
            )
            return 0
        headers, auth_mode = _resolve_marketing_consent_auth(ctx=ctx)
        current_consent = _get_marketing_consent_by_id(
            marketing_consent_id=marketing_consent_id,
            ctx=ctx,
            headers=headers,
        )
        request = {
            "method": "DELETE",
            "path": f"/marketing-consent/v1/marketing-consent/{marketing_consent_id}",
            "body": None,
        }
        selector = {
            "kind": "wix-marketing-consent",
            "operation": "delete",
            "marketing_consent_id": marketing_consent_id,
        }
        before_state = {"marketingConsent": current_consent}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="marketing-consent.delete",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="marketing-consent.delete",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "delete", "marketingConsentId": marketing_consent_id}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify the marketing consent returns 404 after delete.",
                },
                requires_ack=True,
            )

        if not _should_apply(ctx, requires_ack=True):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "marketing-consent.delete",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="marketing-consent.delete",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={"marketingConsent": current_consent},
        )
        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/marketing-consent/v1/marketing-consent/{marketing_consent_id}",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_marketing_consent, status = _get_marketing_consent_by_id_optional(
            marketing_consent_id=marketing_consent_id,
            ctx=ctx,
            headers=headers,
        )
        verification = {
            "ok": after_marketing_consent is None and status == 404,
            "type": "read-after-write",
            "path": f"/marketing-consent/v1/marketing-consent/{marketing_consent_id}",
            "method": "GET",
            "before": current_consent,
            "expected_http_status": 404,
            "actual_http_status": status,
            "checks": [{"field": "status_code", "expected": 404, "actual": status}],
        }
        receipt = _build_receipt(
            method="marketing-consent.delete",
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
                "method": "marketing-consent.delete",
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
                "method": "marketing-consent.delete",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "marketing-consent.delete"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "marketing-consent.delete"}
        )
        return 1


def cmd_marketing_consent_bulk_upsert(args, ctx) -> int:
    try:
        info = _normalize_bulk_marketing_consents_payload(getattr(args, "marketing_consents_json", None))
        if bool(ctx.get("apply")) and not ctx.get("plan_in") and not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "refused": True,
                    "reasons": ["Refused: reviewed apply requires --plan-in from a prior reviewed dry-run"],
                    "refusal_type": "SafetyError",
                    "method": "marketing-consent.bulk-upsert",
                }
            )
            return 0
        headers, auth_mode = _resolve_marketing_consent_auth(ctx=ctx)
        request_body = {"info": info}
        request = {
            "method": "POST",
            "path": "/marketing-consent/v1/bulk/marketing-consent/upsert",
            "body": request_body,
        }
        selector = {
            "kind": "wix-marketing-consent",
            "operation": "bulk-upsert",
            "count": len(info),
            "body_signature": json.dumps(request_body, sort_keys=True),
        }
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="marketing-consent.bulk-upsert",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="marketing-consent.bulk-upsert",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=None,
                proposed_changes=[{"operation": "bulk-upsert", "count": len(info)}],
                verification_plan={
                    "type": "provider-response",
                    "notes": "Verify provider metadata totals and per-result errors because no useful bulk before-state snapshot exists here.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "marketing-consent.bulk-upsert",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="marketing-consent.bulk-upsert",
            expected_selector=selector,
            ctx=ctx,
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/marketing-consent/v1/bulk/marketing-consent/upsert",
            headers=headers,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = _build_bulk_upsert_verification(response=response, expected_count=len(info))
        receipt = _build_receipt(
            method="marketing-consent.bulk-upsert",
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
                "method": "marketing-consent.bulk-upsert",
                "auth_mode": auth_mode,
                "response": response,
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
                "method": "marketing-consent.bulk-upsert",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "marketing-consent.bulk-upsert"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "marketing-consent.bulk-upsert"}
        )
        return 1


def cmd_marketing_consent_remove(args, ctx) -> int:
    try:
        consent_type, email, phone, _ = _read_by_identifier_args(args)
        last_revoke_activity = _normalize_last_revoke_activity(getattr(args, "last_revoke_activity_json", None))
        headers, auth_mode = _resolve_marketing_consent_auth(ctx=ctx)
        current_consent, _ = _get_marketing_consent_by_identifier_optional(
            consent_type=consent_type,
            email=email,
            phone=phone,
            link_language=None,
            ctx=ctx,
            headers=headers,
        )
        request_body = {
            "details": _build_identifier_selector(consent_type=consent_type, email=email, phone=phone),
            "lastRevokeActivity": last_revoke_activity,
        }
        request = {
            "method": "POST",
            "path": "/marketing-consent/v1/marketing-consent/remove",
            "body": request_body,
        }
        selector = {
            "kind": "wix-marketing-consent",
            "operation": "remove",
            "identifier": _build_identifier_selector(consent_type=consent_type, email=email, phone=phone),
        }
        before_state = current_consent
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="marketing-consent.remove",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="marketing-consent.remove",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[
                    {
                        "operation": "remove",
                        "identifier": selector["identifier"],
                        "state": "REVOKED",
                    }
                ],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Read back by identifier, expect REVOKED, and confirm communicationEligibility.granted is false when present.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "marketing-consent.remove",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="marketing-consent.remove",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(plan=loaded_plan, current_state=before_state)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/marketing-consent/v1/marketing-consent/remove",
            headers=headers,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        marketing_consent_response = _extract_marketing_consent(response, operation="marketing-consent.remove")
        after_marketing_consent = _get_marketing_consent_by_identifier(
            consent_type=consent_type,
            email=email,
            phone=phone,
            link_language=None,
            ctx=ctx,
            headers=headers,
        )
        verification = _build_verification(
            path="/marketing-consent/v1/marketing-consent/get-by",
            requested_details=request_body["details"],
            after=after_marketing_consent,
            method="marketing-consent.remove",
            expected_state="REVOKED",
        )
        receipt = _build_receipt(
            method="marketing-consent.remove",
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
                "method": "marketing-consent.remove",
                "auth_mode": auth_mode,
                "response": {"marketingConsent": marketing_consent_response},
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
                "method": "marketing-consent.remove",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "marketing-consent.remove"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "marketing-consent.remove"}
        )
        return 1
