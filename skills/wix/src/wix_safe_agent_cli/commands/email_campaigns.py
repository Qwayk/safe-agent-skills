from __future__ import annotations

import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested


_RECIPIENT_ACTIVITY_VALUES = (
    "DELIVERED",
    "OPENED",
    "CLICKED",
    "BOUNCED",
    "NOT_SENT",
    "SENT",
    "NOT_OPENED",
)
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _coerce_non_empty_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")

    value = raw.strip()
    if not value:
        raise ValidationError(f"Missing --{field}")
    return value


def _read_text_or_file(raw: Any, *, field: str) -> str:
    text = _coerce_non_empty_text(raw, field=field)
    if text.startswith("@"):
        path = Path(text[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            raise ValidationError(f"--{field} file is empty: {path}")
    return text


def _read_json_arg(raw: Any, *, field: str) -> Any:
    text = _read_text_or_file(raw, field=field).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc


def _coerce_campaign_id(raw: Any) -> str:
    return _coerce_non_empty_text(raw, field="campaign-id")


def _coerce_email_address(raw: Any, *, field: str) -> str:
    value = _coerce_non_empty_text(raw, field=field)
    if not _EMAIL_RE.fullmatch(value):
        raise ValidationError(f"--{field} must be a valid email address")
    return value


def _coerce_datetime_text(raw: Any, *, field: str) -> str:
    value = _coerce_non_empty_text(raw, field=field)
    candidate = value.replace("Z", "+00:00")
    try:
        datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValidationError(f"--{field} must be a valid RFC 3339 date-time string") from exc
    return value


def _coerce_publish_send_at(raw: Any) -> str:
    value = _coerce_datetime_text(raw, field="publish-json.emailDistributionOptions.sendAt")
    candidate = value.replace("Z", "+00:00")
    send_at = datetime.fromisoformat(candidate)
    if send_at.tzinfo is None or send_at.utcoffset() is None:
        raise ValidationError("--publish-json.emailDistributionOptions.sendAt must include a time zone offset")
    minimum_send_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    if send_at.astimezone(timezone.utc) < minimum_send_at:
        raise ValidationError("--publish-json.emailDistributionOptions.sendAt must be at least 30 minutes ahead")
    return value


def _coerce_limit(raw: Any, *, field: str, maximum: int) -> int | None:
    if raw is None:
        return None
    if not isinstance(raw, int):
        raise ValidationError(f"--{field} must be an integer")
    if raw < 0 or raw > maximum:
        raise ValidationError(f"--{field} must be between 0 and {maximum}")
    return raw


def _coerce_statuses(raw: Any, *, field: str) -> list[str] | None:
    if raw is None:
        return None
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, list) or not value:
        raise ValidationError(f"--{field} must be a non-empty JSON array")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValidationError(f"--{field} entries must be non-empty strings")
        normalized.append(item.strip())
    return normalized


def _coerce_string_list(raw: Any, *, field: str) -> list[str] | None:
    if raw is None:
        return None
    if not isinstance(raw, list):
        raise ValidationError(f"--{field} must be a JSON array")
    normalized: list[str] = []
    for item in raw:
        if not isinstance(item, str) or not item.strip():
            raise ValidationError(f"--{field} entries must be non-empty strings")
        normalized.append(item.strip())
    return normalized


def _coerce_campaign_ids(raw: Any) -> list[str]:
    value = _read_json_arg(raw, field="campaign-ids-json")
    if not isinstance(value, list) or not value:
        raise ValidationError("--campaign-ids-json must be a non-empty JSON array")
    if len(value) > 100:
        raise ValidationError("--campaign-ids-json supports at most 100 campaign IDs")

    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValidationError("--campaign-ids-json entries must be non-empty strings")
        normalized.append(item.strip())
    return normalized


def _coerce_publish_email_distribution_options(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict) or not raw:
        raise ValidationError("--publish-json.emailDistributionOptions must be a non-empty JSON object")

    allowed_fields = {"emailSubject", "labelIds", "contactIds", "sendAt"}
    unexpected_fields = sorted(set(raw) - allowed_fields)
    if unexpected_fields:
        raise ValidationError("--publish-json.emailDistributionOptions supports only: emailSubject, labelIds, contactIds, and sendAt")

    payload: dict[str, Any] = {}
    if "emailSubject" in raw:
        payload["emailSubject"] = _coerce_non_empty_text(
            raw.get("emailSubject"),
            field="publish-json.emailDistributionOptions.emailSubject",
        )
    if "labelIds" in raw:
        payload["labelIds"] = _coerce_string_list(raw.get("labelIds"), field="publish-json.emailDistributionOptions.labelIds")
    if "contactIds" in raw:
        payload["contactIds"] = _coerce_string_list(
            raw.get("contactIds"),
            field="publish-json.emailDistributionOptions.contactIds",
        )
    if "sendAt" in raw:
        payload["sendAt"] = _coerce_publish_send_at(raw.get("sendAt"))
    return payload


def _coerce_publish_request_body(raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    value = _read_json_arg(raw, field="publish-json")
    if not isinstance(value, dict):
        raise ValidationError("--publish-json must be a non-empty JSON object")
    if not value:
        return None

    direct_fields = {"emailSubject", "labelIds", "contactIds", "sendAt"}
    if "emailDistributionOptions" in value:
        unexpected_fields = sorted(set(value) - {"emailDistributionOptions"})
        if unexpected_fields:
            raise ValidationError("--publish-json supports only: emailDistributionOptions, emailSubject, labelIds, contactIds, and sendAt")
        email_distribution_options = value.get("emailDistributionOptions")
        if not isinstance(email_distribution_options, dict):
            raise ValidationError("--publish-json.emailDistributionOptions must be a non-empty JSON object")
        if not email_distribution_options:
            return None
        return {"emailDistributionOptions": _coerce_publish_email_distribution_options(email_distribution_options)}

    unexpected_fields = sorted(set(value) - direct_fields)
    if unexpected_fields:
        raise ValidationError("--publish-json supports only: emailDistributionOptions, emailSubject, labelIds, contactIds, and sendAt")
    return {"emailDistributionOptions": _coerce_publish_email_distribution_options(value)}


def _coerce_recipient_activity(raw: Any) -> str:
    activity = _coerce_non_empty_text(raw, field="activity").upper()
    if activity not in _RECIPIENT_ACTIVITY_VALUES:
        allowed = ", ".join(_RECIPIENT_ACTIVITY_VALUES)
        raise ValidationError(f"--activity must be one of: {allowed}")
    return activity


def _coerce_send_test_payload(raw: Any) -> dict[str, Any]:
    value = _read_json_arg(raw, field="send-test-json")
    if not isinstance(value, dict) or not value:
        raise ValidationError("--send-test-json must be a non-empty JSON object")
    payload = dict(value)
    payload["toEmailAddress"] = _coerce_email_address(payload.get("toEmailAddress"), field="toEmailAddress")
    email_subject = payload.get("emailSubject")
    if email_subject is not None:
        payload["emailSubject"] = _coerce_non_empty_text(email_subject, field="emailSubject")
    return payload


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
    if json_body is not None:
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


def _emit_success(
    *,
    method: str,
    auth_mode: str,
    request: dict[str, Any],
    response: dict[str, Any],
    ctx: dict[str, Any],
) -> None:
    payload = {
        "ok": True,
        "method": method,
        "auth_mode": auth_mode,
        "request": request,
        "response": response,
    }
    ctx["audit"].write(method, payload)
    ctx["out"].emit(payload)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _resolve_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="email-campaigns",
    )
    return auth["headers"], auth["mode"]


def _get_campaign(
    *,
    campaign_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/email-marketing/v1/campaigns/{campaign_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    campaign = payload.get("campaign")
    if not isinstance(campaign, dict):
        raise ValidationError("email-campaigns.get response did not include a campaign object")
    return campaign


def _get_campaign_optional(
    *,
    campaign_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> tuple[dict[str, Any] | None, int | None]:
    try:
        return _get_campaign(campaign_id=campaign_id, ctx=ctx, headers=headers), None
    except RuntimeError as exc:
        text = str(exc)
        status = None
        if text.startswith("HTTP "):
            pieces = text.split()
            if len(pieces) >= 2:
                try:
                    status = int(pieces[1])
                except ValueError:
                    status = None
        if status == 404:
            return None, 404
        raise


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
        "risk_level": "high" if requires_ack else "medium",
        "risk_reasons": ["email-campaign-write"] + (["irreversible"] if requires_ack else []),
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
                "Captured current campaign state before planning."
                if before_state_available
                else "No useful before-state snapshot is available for this command."
            ),
        },
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "rollback": {
            "supported": False,
            "notes": (
                "No automatic rollback. Use the saved campaign snapshot only as a manual reference."
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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="email-campaigns")


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: campaign state changed since plan was created")


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
                "Receipt stores the pre-apply campaign snapshot."
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


def cmd_email_campaigns_list(args, ctx) -> int:
    try:
        headers, auth_mode = _resolve_auth(ctx=ctx)
        params: dict[str, Any] = {}
        if bool(getattr(args, "include_statistics", False)):
            params["optionIncludeStatistics"] = "true"
        statuses = _coerce_statuses(getattr(args, "statuses_json", None), field="statuses-json")
        if statuses is not None:
            params["statuses"] = statuses
        visibility_statuses = _coerce_statuses(
            getattr(args, "visibility_statuses_json", None),
            field="visibility-statuses-json",
        )
        if visibility_statuses is not None:
            params["visibilityStatuses"] = visibility_statuses
        limit = _coerce_limit(getattr(args, "limit", None), field="limit", maximum=1000)
        if limit is not None:
            params["paging.limit"] = limit
        offset = _coerce_limit(getattr(args, "offset", None), field="offset", maximum=1000000)
        if offset is not None:
            params["paging.offset"] = offset

        request_path = "/email-marketing/v1/campaigns"
        response = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=headers,
            params=params or None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method="email-campaigns.list",
            auth_mode=auth_mode,
            request={"method": "GET", "path": request_path, "params": params or {}},
            response=response,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "email-campaigns.list"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "email-campaigns.list"})
        return 1


def cmd_email_campaigns_get(args, ctx) -> int:
    try:
        campaign_id = _coerce_campaign_id(getattr(args, "campaign_id", None))
        headers, auth_mode = _resolve_auth(ctx=ctx)
        params: dict[str, Any] = {}
        if bool(getattr(args, "include_statistics", False)):
            params["optionIncludeStatistics"] = "true"
        request_path = f"/email-marketing/v1/campaigns/{campaign_id}"
        response = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=headers,
            params=params or None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method="email-campaigns.get",
            auth_mode=auth_mode,
            request={"method": "GET", "path": request_path, "params": params or {}},
            response=response,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "email-campaigns.get"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "email-campaigns.get"})
        return 1


def cmd_email_campaigns_get_audience(args, ctx) -> int:
    try:
        campaign_id = _coerce_campaign_id(getattr(args, "campaign_id", None))
        headers, auth_mode = _resolve_auth(ctx=ctx)
        request_path = f"/email-marketing/v1/campaigns/{campaign_id}/audience"
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method="email-campaigns.get-audience",
            auth_mode=auth_mode,
            request={"method": "POST", "path": request_path, "body": None},
            response=response,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "email-campaigns.get-audience"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "email-campaigns.get-audience"})
        return 1


def cmd_email_campaigns_list_statistics(args, ctx) -> int:
    try:
        campaign_ids = _coerce_campaign_ids(getattr(args, "campaign_ids_json", None))
        headers, auth_mode = _resolve_auth(ctx=ctx)
        request_path = "/email-marketing/v1/campaigns/statistics"
        params = {"campaignIds": campaign_ids}
        response = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=headers,
            params=params,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method="email-campaigns.list-statistics",
            auth_mode=auth_mode,
            request={"method": "GET", "path": request_path, "params": params},
            response=response,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "email-campaigns.list-statistics"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "email-campaigns.list-statistics"}
        )
        return 1


def cmd_email_campaigns_list_recipients(args, ctx) -> int:
    try:
        campaign_id = _coerce_campaign_id(getattr(args, "campaign_id", None))
        activity = _coerce_recipient_activity(getattr(args, "activity", None))
        limit = _coerce_limit(getattr(args, "limit", None), field="limit", maximum=1000)
        cursor = getattr(args, "cursor", None)
        if cursor is not None:
            cursor = _coerce_non_empty_text(cursor, field="cursor")

        headers, auth_mode = _resolve_auth(ctx=ctx)
        request_path = f"/email-marketing/v1/campaigns/{campaign_id}/statistics/recipients"
        params: dict[str, Any] = {"activity": activity}
        if limit is not None:
            params["paging.limit"] = limit
        if cursor is not None:
            params["paging.cursor"] = cursor
        response = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=headers,
            params=params,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method="email-campaigns.list-recipients",
            auth_mode=auth_mode,
            request={"method": "GET", "path": request_path, "params": params},
            response=response,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "email-campaigns.list-recipients"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "email-campaigns.list-recipients"}
        )
        return 1


def cmd_email_campaigns_pause_scheduling(args, ctx) -> int:
    try:
        campaign_id = _coerce_campaign_id(getattr(args, "campaign_id", None))
        if bool(ctx.get("apply")) and not ctx.get("plan_in") and not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "refused": True,
                    "reasons": ["Refused: reviewed apply requires --plan-in from a prior reviewed dry-run"],
                    "refusal_type": "SafetyError",
                    "method": "email-campaigns.pause-scheduling",
                }
            )
            return 0
        headers, auth_mode = _resolve_auth(ctx=ctx)
        current_campaign = _get_campaign(campaign_id=campaign_id, ctx=ctx, headers=headers)
        request = {
            "method": "POST",
            "path": f"/email-marketing/v1/campaigns/{campaign_id}/pause-scheduling",
            "body": None,
        }
        selector = {"kind": "wix-email-campaign", "operation": "pause-scheduling", "campaign_id": campaign_id}
        before_state = {"campaign": current_campaign}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="email-campaigns.pause-scheduling",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="email-campaigns.pause-scheduling",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "pause-scheduling", "campaignId": campaign_id}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Read back the campaign and expect distributionStatus PAUSED when the provider exposes it.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "email-campaigns.pause-scheduling",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="email-campaigns.pause-scheduling",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(plan=loaded_plan, current_state={"campaign": current_campaign})
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=f"/email-marketing/v1/campaigns/{campaign_id}/pause-scheduling",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_campaign = _get_campaign(campaign_id=campaign_id, ctx=ctx, headers=headers)
        actual_status = after_campaign.get("distributionStatus")
        verification = {
            "ok": actual_status == "PAUSED",
            "type": "read-after-write",
            "path": f"/email-marketing/v1/campaigns/{campaign_id}",
            "method": "GET",
            "after": after_campaign,
            "checks": [{"field": "distributionStatus", "expected": "PAUSED", "actual": actual_status}],
        }
        receipt = _build_receipt(
            method="email-campaigns.pause-scheduling",
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
                "method": "email-campaigns.pause-scheduling",
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
                "method": "email-campaigns.pause-scheduling",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "email-campaigns.pause-scheduling"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "email-campaigns.pause-scheduling"})
        return 1


def cmd_email_campaigns_reschedule(args, ctx) -> int:
    try:
        campaign_id = _coerce_campaign_id(getattr(args, "campaign_id", None))
        send_at = _coerce_datetime_text(getattr(args, "send_at", None), field="send-at")
        if bool(ctx.get("apply")) and not ctx.get("plan_in") and not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "refused": True,
                    "reasons": ["Refused: reviewed apply requires --plan-in from a prior reviewed dry-run"],
                    "refusal_type": "SafetyError",
                    "method": "email-campaigns.reschedule",
                }
            )
            return 0
        headers, auth_mode = _resolve_auth(ctx=ctx)
        current_campaign = _get_campaign(campaign_id=campaign_id, ctx=ctx, headers=headers)
        request_body = {"sendAt": send_at}
        request = {
            "method": "POST",
            "path": f"/email-marketing/v1/campaigns/{campaign_id}/reschedule",
            "body": request_body,
        }
        selector = {"kind": "wix-email-campaign", "operation": "reschedule", "campaign_id": campaign_id, "send_at": send_at}
        before_state = {"campaign": current_campaign}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="email-campaigns.reschedule",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="email-campaigns.reschedule",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "reschedule", "campaignId": campaign_id, "sendAt": send_at}],
                verification_plan={
                    "type": "provider-response",
                    "notes": "This endpoint returns an empty object and the current shipped read surface does not prove the scheduled timestamp directly, so verification stays provider-response-only here.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "email-campaigns.reschedule",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="email-campaigns.reschedule",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(plan=loaded_plan, current_state={"campaign": current_campaign})
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=f"/email-marketing/v1/campaigns/{campaign_id}/reschedule",
            headers=headers,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = {
            "ok": True,
            "type": "provider-response",
            "notes": "Provider accepted the reschedule request; no stable scheduled-time readback is documented in the current shipped read surface.",
            "after": response,
            "checks": [{"field": "response_type", "expected": "object", "actual": "object"}],
        }
        receipt = _build_receipt(
            method="email-campaigns.reschedule",
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
                "method": "email-campaigns.reschedule",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0
    except SafetyError as exc:
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "refused": True,
                "reasons": [str(exc)],
                "refusal_type": "SafetyError",
                "method": "email-campaigns.reschedule",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "email-campaigns.reschedule"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "email-campaigns.reschedule"})
        return 1


def cmd_email_campaigns_send_test(args, ctx) -> int:
    try:
        campaign_id = _coerce_campaign_id(getattr(args, "campaign_id", None))
        send_test_payload = _coerce_send_test_payload(getattr(args, "send_test_json", None))
        if bool(ctx.get("apply")) and not ctx.get("plan_in") and not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "refused": True,
                    "reasons": ["Refused: reviewed apply requires --plan-in from a prior reviewed dry-run"],
                    "refusal_type": "SafetyError",
                    "method": "email-campaigns.send-test",
                }
            )
            return 0
        headers, auth_mode = _resolve_auth(ctx=ctx)
        current_campaign = _get_campaign(campaign_id=campaign_id, ctx=ctx, headers=headers)
        request = {
            "method": "POST",
            "path": f"/email-marketing/v1/campaigns/{campaign_id}/test",
            "body": send_test_payload,
        }
        selector = {
            "kind": "wix-email-campaign",
            "operation": "send-test",
            "campaign_id": campaign_id,
            "to_email_address": send_test_payload["toEmailAddress"],
        }
        before_state = {"campaign": current_campaign}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="email-campaigns.send-test",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="email-campaigns.send-test",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "send-test", "campaignId": campaign_id, "toEmailAddress": send_test_payload["toEmailAddress"]}],
                verification_plan={
                    "type": "provider-response",
                    "notes": "This endpoint is rate-limited and inbox delivery is out of band, so verification stays provider-response-only.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "email-campaigns.send-test",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="email-campaigns.send-test",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(plan=loaded_plan, current_state={"campaign": current_campaign})
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=f"/email-marketing/v1/campaigns/{campaign_id}/test",
            headers=headers,
            params=None,
            json_body=send_test_payload,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = {
            "ok": True,
            "type": "provider-response",
            "notes": "Provider accepted the send-test request; inbox delivery proof is outside this CLI.",
            "after": response,
            "checks": [{"field": "response_type", "expected": "object", "actual": "object"}],
        }
        receipt = _build_receipt(
            method="email-campaigns.send-test",
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
                "method": "email-campaigns.send-test",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0
    except SafetyError as exc:
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "refused": True,
                "reasons": [str(exc)],
                "refusal_type": "SafetyError",
                "method": "email-campaigns.send-test",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "email-campaigns.send-test"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "email-campaigns.send-test"})
        return 1


def cmd_email_campaigns_publish(args, ctx) -> int:
    try:
        campaign_id = _coerce_campaign_id(getattr(args, "campaign_id", None))
        publish_body = _coerce_publish_request_body(getattr(args, "publish_json", None))
        if bool(ctx.get("apply")) and not ctx.get("plan_in") and not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "refused": True,
                    "reasons": ["Refused: reviewed apply requires --plan-in from a prior reviewed dry-run"],
                    "refusal_type": "SafetyError",
                    "method": "email-campaigns.publish",
                }
            )
            return 0
        headers, auth_mode = _resolve_auth(ctx=ctx)
        current_campaign = _get_campaign(campaign_id=campaign_id, ctx=ctx, headers=headers)
        request = {
            "method": "POST",
            "path": f"/email-marketing/v1/campaigns/{campaign_id}/publish",
            "body": publish_body,
        }
        selector = {
            "kind": "wix-email-campaign",
            "operation": "publish",
            "campaign_id": campaign_id,
            "publish_json": publish_body,
        }
        before_state = {"campaign": current_campaign}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="email-campaigns.publish",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="email-campaigns.publish",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[
                    {
                        "operation": "publish",
                        "campaignId": campaign_id,
                        "publishJson": publish_body,
                        "landingPageOnly": publish_body is None,
                    }
                ],
                verification_plan={
                    "type": "read-after-write",
                    "notes": (
                        "Verify publishingData.datePublished and publishingData.landingPageUrl from the provider response, then read the campaign back for the same published state."
                    ),
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "email-campaigns.publish",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="email-campaigns.publish",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(plan=loaded_plan, current_state={"campaign": current_campaign})
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=f"/email-marketing/v1/campaigns/{campaign_id}/publish",
            headers=headers,
            params=None,
            json_body=publish_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        response_publishing_data = response.get("publishingData")
        if not isinstance(response_publishing_data, dict):
            raise ValidationError("email-campaigns.publish response did not include publishingData")
        after_campaign = _get_campaign(campaign_id=campaign_id, ctx=ctx, headers=headers)
        after_publishing_data = after_campaign.get("publishingData")
        if not isinstance(after_publishing_data, dict):
            raise ValidationError("email-campaigns.publish readback did not include publishingData")
        verification = {
            "ok": bool(response_publishing_data.get("datePublished"))
            and response_publishing_data.get("datePublished") == after_publishing_data.get("datePublished"),
            "type": "read-after-write",
            "path": f"/email-marketing/v1/campaigns/{campaign_id}",
            "method": "GET",
            "before": current_campaign,
            "after": after_campaign,
            "response_publishing_data": response_publishing_data,
            "checks": [
                {
                    "field": "publishingData.datePublished",
                    "expected": response_publishing_data.get("datePublished"),
                    "actual": after_publishing_data.get("datePublished"),
                },
                {
                    "field": "publishingData.landingPageUrl",
                    "expected": response_publishing_data.get("landingPageUrl"),
                    "actual": after_publishing_data.get("landingPageUrl"),
                },
            ],
        }
        receipt = _build_receipt(
            method="email-campaigns.publish",
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
                "method": "email-campaigns.publish",
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
                "method": "email-campaigns.publish",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "email-campaigns.publish"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "email-campaigns.publish"})
        return 1


def cmd_email_campaigns_reuse(args, ctx) -> int:
    try:
        campaign_id = _coerce_campaign_id(getattr(args, "campaign_id", None))
        if bool(ctx.get("apply")) and not ctx.get("plan_in") and not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "refused": True,
                    "reasons": ["Refused: reviewed apply requires --plan-in from a prior reviewed dry-run"],
                    "refusal_type": "SafetyError",
                    "method": "email-campaigns.reuse",
                }
            )
            return 0
        headers, auth_mode = _resolve_auth(ctx=ctx)
        current_campaign = _get_campaign(campaign_id=campaign_id, ctx=ctx, headers=headers)
        request = {"method": "POST", "path": f"/email-marketing/v1/campaigns/{campaign_id}/reuse", "body": None}
        selector = {"kind": "wix-email-campaign", "operation": "reuse", "campaign_id": campaign_id}
        before_state = {"campaign": current_campaign}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="email-campaigns.reuse",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="email-campaigns.reuse",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "reuse", "campaignId": campaign_id, "createsNewCampaignCopy": True}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify by returned campaignId and reread the new campaign when the readback is available.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "email-campaigns.reuse",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="email-campaigns.reuse",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(plan=loaded_plan, current_state={"campaign": current_campaign})
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=f"/email-marketing/v1/campaigns/{campaign_id}/reuse",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        new_campaign = response.get("campaign")
        if not isinstance(new_campaign, dict):
            raise ValidationError("email-campaigns.reuse response did not include a campaign object")
        new_campaign_id = new_campaign.get("campaignId")
        if not isinstance(new_campaign_id, str) or not new_campaign_id.strip():
            raise ValidationError("email-campaigns.reuse response did not include a campaignId")
        readback_campaign, readback_status = _get_campaign_optional(campaign_id=new_campaign_id, ctx=ctx, headers=headers)
        verification = {
            "ok": True,
            "type": "read-after-write" if readback_campaign is not None else "provider-response",
            "path": f"/email-marketing/v1/campaigns/{new_campaign_id}",
            "method": "GET",
            "before": current_campaign,
            "after": new_campaign,
            "readback_status": readback_status,
            "checks": [
                {
                    "field": "campaign.campaignId",
                    "expected": new_campaign_id,
                    "actual": new_campaign.get("campaignId"),
                }
            ],
        }
        if readback_campaign is not None:
            verification["readback"] = readback_campaign
            verification["checks"].append(
                {
                    "field": "readback.campaignId",
                    "expected": new_campaign_id,
                    "actual": readback_campaign.get("campaignId"),
                }
            )
            verification["ok"] = readback_campaign.get("campaignId") == new_campaign_id
        receipt = _build_receipt(
            method="email-campaigns.reuse",
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
                "method": "email-campaigns.reuse",
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
                "method": "email-campaigns.reuse",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "email-campaigns.reuse"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "email-campaigns.reuse"})
        return 1


def cmd_email_campaigns_delete(args, ctx) -> int:
    try:
        campaign_id = _coerce_campaign_id(getattr(args, "campaign_id", None))
        if bool(ctx.get("apply")) and not ctx.get("plan_in") and not _should_apply(ctx, requires_ack=True):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "refused": True,
                    "reasons": ["Refused: reviewed apply requires --plan-in from a prior reviewed dry-run"],
                    "refusal_type": "SafetyError",
                    "method": "email-campaigns.delete",
                }
            )
            return 0
        headers, auth_mode = _resolve_auth(ctx=ctx)
        current_campaign = _get_campaign(campaign_id=campaign_id, ctx=ctx, headers=headers)
        request = {"method": "DELETE", "path": f"/email-marketing/v1/campaigns/{campaign_id}", "body": None}
        selector = {"kind": "wix-email-campaign", "operation": "delete", "campaign_id": campaign_id}
        before_state = {"campaign": current_campaign}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="email-campaigns.delete",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="email-campaigns.delete",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "delete", "campaignId": campaign_id, "permanent": True}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify delete by expecting get campaign to return 404.",
                },
                requires_ack=True,
            )

        if not _should_apply(ctx, requires_ack=True):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "email-campaigns.delete",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="email-campaigns.delete",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(plan=loaded_plan, current_state={"campaign": current_campaign})
        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/email-marketing/v1/campaigns/{campaign_id}",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_campaign, after_status = _get_campaign_optional(campaign_id=campaign_id, ctx=ctx, headers=headers)
        verification = {
            "ok": after_campaign is None and after_status == 404,
            "type": "read-after-write",
            "path": f"/email-marketing/v1/campaigns/{campaign_id}",
            "method": "GET",
            "before": current_campaign,
            "after_status": after_status,
            "checks": [{"field": "status_code", "expected": 404, "actual": after_status}],
        }
        receipt = _build_receipt(
            method="email-campaigns.delete",
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
                "method": "email-campaigns.delete",
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
                "method": "email-campaigns.delete",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "email-campaigns.delete"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "email-campaigns.delete"})
        return 1


def cmd_email_campaigns_identify_sender_address(args, ctx) -> int:
    try:
        email_address = _coerce_non_empty_text(getattr(args, "email_address", None), field="email-address")
        headers, auth_mode = _resolve_auth(ctx=ctx)
        request_path = "/email-marketing/v1/identify-sender-address"
        body = {"emailAddress": email_address}
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method="email-campaigns.identify-sender-address",
            auth_mode=auth_mode,
            request={"method": "POST", "path": request_path, "body": body},
            response=response,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "email-campaigns.identify-sender-address"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "email-campaigns.identify-sender-address"}
        )
        return 1


def cmd_campaign_validation_validate_link(args, ctx) -> int:
    try:
        url = _coerce_non_empty_text(getattr(args, "url", None), field="url")
        headers, auth_mode = _resolve_auth(ctx=ctx)
        request_path = "/email-marketing/v1/campaign-validation/validate-link"
        body = {"url": url}
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method="campaign-validation.validate-link",
            auth_mode=auth_mode,
            request={"method": "POST", "path": request_path, "body": body},
            response=response,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "campaign-validation.validate-link"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "campaign-validation.validate-link"}
        )
        return 1


def cmd_campaign_validation_validate_html_links(args, ctx) -> int:
    try:
        html = _read_text_or_file(getattr(args, "html", None), field="html")
        headers, auth_mode = _resolve_auth(ctx=ctx)
        request_path = "/email-marketing/v1/campaign-validation/validate-html-links"
        body = {"html": html}
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method="campaign-validation.validate-html-links",
            auth_mode=auth_mode,
            request={"method": "POST", "path": request_path, "body": body},
            response=response,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "campaign-validation.validate-html-links"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "campaign-validation.validate-html-links"}
        )
        return 1
