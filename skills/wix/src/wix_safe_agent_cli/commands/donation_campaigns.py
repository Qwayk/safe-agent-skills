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


def _ensure_non_empty_tag_change_lists(payload: dict[str, Any], *, field: str) -> None:
    assign_tags = payload.get("assignTags", [])
    unassign_tags = payload.get("unassignTags", [])
    if not isinstance(assign_tags, list):
        raise ValidationError(f"--{field} assignTags must be a JSON array")
    if not isinstance(unassign_tags, list):
        raise ValidationError(f"--{field} unassignTags must be a JSON array")
    if not assign_tags and not unassign_tags:
        raise ValidationError(f"--{field} must include at least one tag in assignTags or unassignTags")


def _extract_campaign_body(payload: dict[str, Any]) -> dict[str, Any]:
    campaign = payload.get("donationCampaign")
    if isinstance(campaign, dict):
        return campaign
    return payload


def _normalize_create_body(raw: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    body = _coerce_json_object(raw, field="donation-campaign-json")
    campaign = _extract_campaign_body(body)
    if not isinstance(campaign, dict) or not campaign:
        raise ValidationError("--donation-campaign-json must include a non-empty donation campaign object")
    if "customAmountEnabled" not in campaign and "predefinedDonationAmounts" not in campaign:
        raise ValidationError(
            "--donation-campaign-json must include customAmountEnabled, predefinedDonationAmounts, or both"
        )
    return body, campaign


def _normalize_update_body(raw: Any, *, donation_campaign_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    body = _coerce_json_object(raw, field="donation-campaign-json")
    campaign = _extract_campaign_body(body)
    if not isinstance(campaign, dict) or not campaign:
        raise ValidationError("--donation-campaign-json must include a non-empty donation campaign object")
    existing_id = campaign.get("id")
    if existing_id is not None and str(existing_id).strip() and str(existing_id).strip() != donation_campaign_id:
        raise ValidationError("--donation-campaign-json id does not match --donation-campaign-id")
    campaign["id"] = donation_campaign_id
    if "status" in campaign:
        raise ValidationError("Donation campaign status is calculated by Wix and can't be set manually")
    _coerce_non_empty_text(campaign.get("revision"), field="donation-campaign-json revision")
    if "customAmountEnabled" not in campaign and "predefinedDonationAmounts" not in campaign:
        raise ValidationError(
            "--donation-campaign-json must include customAmountEnabled, predefinedDonationAmounts, or both"
        )
    return body, campaign


def _normalize_query_body(raw: Any, *, field: str) -> dict[str, Any]:
    if raw is None:
        return {}
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    return payload


def _normalize_bulk_campaigns_body(
    raw: Any,
    *,
    field: str,
    require_revision: bool,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    payload = _read_json_arg(raw, field=field)
    if isinstance(payload, list):
        body = {"donationCampaigns": payload}
    elif isinstance(payload, dict):
        body = dict(payload)
    else:
        raise ValidationError(f"--{field} must be a JSON array or object")

    campaigns = body.get("donationCampaigns")
    if not isinstance(campaigns, list) or not campaigns:
        raise ValidationError(f"--{field} must include a non-empty donationCampaigns array")

    normalized: list[dict[str, Any]] = []
    ids: list[str] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(campaigns):
        if not isinstance(item, dict):
            raise ValidationError(f"--{field} donationCampaigns[{index}] must be a JSON object")
        campaign = _extract_campaign_body(item)
        if not isinstance(campaign, dict) or not campaign:
            raise ValidationError(f"--{field} donationCampaigns[{index}] must include a donation campaign object")
        if "customAmountEnabled" not in campaign and "predefinedDonationAmounts" not in campaign:
            raise ValidationError(
                f"--{field} donationCampaigns[{index}] must include customAmountEnabled, predefinedDonationAmounts, or both"
            )
        if "status" in campaign:
            raise ValidationError(f"--{field} donationCampaigns[{index}] cannot set status manually")
        raw_id = campaign.get("id")
        if raw_id is not None:
            donation_campaign_id = _coerce_non_empty_text(raw_id, field=f"{field} donationCampaigns[{index}].id")
            if donation_campaign_id in seen_ids:
                raise ValidationError(f"--{field} contains duplicate donation campaign id: {donation_campaign_id}")
            seen_ids.add(donation_campaign_id)
            ids.append(donation_campaign_id)
        elif require_revision:
            raise ValidationError(f"--{field} donationCampaigns[{index}] must include id")

        if require_revision:
            _coerce_non_empty_text(campaign.get("revision"), field=f"{field} donationCampaigns[{index}].revision")
        normalized.append(item if "donationCampaign" in item else campaign)

    body["donationCampaigns"] = normalized
    return body, normalized, ids


def _normalize_bulk_update_tags_body(raw: Any) -> tuple[dict[str, Any], list[str]]:
    payload = _coerce_json_object(raw, field="update-tags-json")
    ids = payload.get("ids")
    if not isinstance(ids, list) or not ids:
        raise ValidationError("--update-tags-json must include a non-empty ids array")
    normalized_ids: list[str] = []
    seen_ids: set[str] = set()
    for index, raw_id in enumerate(ids):
        donation_campaign_id = _coerce_non_empty_text(raw_id, field=f"update-tags-json ids[{index}]")
        if donation_campaign_id in seen_ids:
            raise ValidationError(f"--update-tags-json contains duplicate donation campaign id: {donation_campaign_id}")
        seen_ids.add(donation_campaign_id)
        normalized_ids.append(donation_campaign_id)
    _ensure_non_empty_tag_change_lists(payload, field="update-tags-json")
    return payload, normalized_ids


def _normalize_bulk_update_tags_by_filter_body(raw: Any) -> dict[str, Any]:
    payload = _coerce_json_object(raw, field="update-tags-json")
    _ensure_non_empty_tag_change_lists(payload, field="update-tags-json")
    filter_obj = payload.get("filter")
    if not isinstance(filter_obj, dict) or not filter_obj:
        raise ValidationError(
            "--update-tags-json must include a non-empty filter object; empty-filter all-campaign retagging is refused in this boundary"
        )
    return payload


def _resolve_donation_campaigns_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="donation-campaigns",
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


def _extract_campaign(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    campaign = payload.get("donationCampaign")
    if isinstance(campaign, dict):
        return campaign
    if isinstance(payload.get("id"), str):
        return payload
    raise ValidationError(f"{operation} response did not include a donationCampaign object")


def _extract_campaign_id(campaign: dict[str, Any], *, operation: str) -> str:
    raw_id = campaign.get("id")
    if not isinstance(raw_id, str) or not raw_id.strip():
        raise ValidationError(f"{operation} response did not include a usable donation campaign id")
    return raw_id.strip()


def _extract_campaigns(payload: dict[str, Any], *, operation: str) -> list[dict[str, Any]]:
    for key in ("donationCampaigns", "results", "items"):
        items = payload.get(key)
        if isinstance(items, list):
            campaigns = [item for item in items if isinstance(item, dict)]
            if campaigns:
                return campaigns
    raise ValidationError(f"{operation} response did not include a donationCampaigns list")


def _extract_job_id(payload: dict[str, Any], *, operation: str) -> str:
    raw_job_id = payload.get("jobId") or payload.get("id")
    if not isinstance(raw_job_id, str) or not raw_job_id.strip():
        raise ValidationError(f"{operation} response did not include a usable job id")
    return raw_job_id.strip()


def _get_campaign(*, donation_campaign_id: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/donation-campaigns/v2/donation-campaigns/{donation_campaign_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_campaign(payload, operation="donation-campaigns.get")


def _get_campaign_metrics(*, donation_campaign_id: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/donation-campaigns/v2/donation-campaigns/{donation_campaign_id}/metrics",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return payload


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
        "risk_reasons": ["wix-donation-campaign-write"] + (["irreversible"] if requires_ack else []),
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
                    else "No useful before-state snapshot exists for this create-style or async write."
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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="donation-campaigns")


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: donation campaign state changed since plan was created")


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
                else "No useful before-state snapshot was available for this create-style or async write."
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


def cmd_donation_campaigns_get(args, ctx) -> int:
    try:
        donation_campaign_id = _coerce_non_empty_text(
            getattr(args, "donation_campaign_id", None),
            field="donation-campaign-id",
        )
        headers, auth_mode = _resolve_donation_campaigns_auth(ctx=ctx)
        campaign = _get_campaign(donation_campaign_id=donation_campaign_id, ctx=ctx, headers=headers)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "donation-campaigns.get",
                "auth_mode": auth_mode,
                "request": {
                    "method": "GET",
                    "path": f"/donation-campaigns/v2/donation-campaigns/{donation_campaign_id}",
                },
                "response": {"donationCampaign": campaign},
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "donation-campaigns.get"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "donation-campaigns.get"})
        return 1


def cmd_donation_campaigns_get_metrics(args, ctx) -> int:
    try:
        donation_campaign_id = _coerce_non_empty_text(
            getattr(args, "donation_campaign_id", None),
            field="donation-campaign-id",
        )
        headers, auth_mode = _resolve_donation_campaigns_auth(ctx=ctx)
        metrics = _get_campaign_metrics(donation_campaign_id=donation_campaign_id, ctx=ctx, headers=headers)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "donation-campaigns.get-metrics",
                "auth_mode": auth_mode,
                "request": {
                    "method": "GET",
                    "path": f"/donation-campaigns/v2/donation-campaigns/{donation_campaign_id}/metrics",
                },
                "response": metrics,
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "donation-campaigns.get-metrics"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "donation-campaigns.get-metrics"})
        return 1


def cmd_donation_campaigns_query(args, ctx) -> int:
    try:
        body = _normalize_query_body(getattr(args, "query_json", None), field="query-json")
        headers, auth_mode = _resolve_donation_campaigns_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/donation-campaigns/v2/donation-campaigns/query",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        ctx["out"].emit(
            {
                "ok": True,
                "method": "donation-campaigns.query",
                "auth_mode": auth_mode,
                "request": {"method": "POST", "path": "/donation-campaigns/v2/donation-campaigns/query", "body": body},
                "response": payload,
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "donation-campaigns.query"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "donation-campaigns.query"})
        return 1


def cmd_donation_campaigns_create(args, ctx) -> int:
    try:
        body, campaign = _normalize_create_body(getattr(args, "donation_campaign_json", None))
        headers, auth_mode = _resolve_donation_campaigns_auth(ctx=ctx)
        request = {"method": "POST", "path": "/donation-campaigns/v2/donation-campaigns", "body": body}
        selector = {"kind": "wix-donation-campaign", "operation": "create"}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="donation-campaigns.create", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="donation-campaigns.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={},
                proposed_changes=[{"operation": "create", "campaign": campaign}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify create response id and reread the created donation campaign.",
                },
                rollback_notes="No automatic rollback. Donation campaign creation is manual-recovery only.",
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "donation-campaigns.create",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="donation-campaigns.create", expected_selector=selector, ctx=ctx)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/donation-campaigns/v2/donation-campaigns",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_campaign = _extract_campaign(response, operation="donation-campaigns.create")
        donation_campaign_id = _extract_campaign_id(created_campaign, operation="donation-campaigns.create")
        after_campaign = _get_campaign(donation_campaign_id=donation_campaign_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_campaign.get("id") or "") == donation_campaign_id,
            "type": "read-after-write",
            "path": f"/donation-campaigns/v2/donation-campaigns/{donation_campaign_id}",
            "method": "GET",
            "after": after_campaign,
            "checks": [{"field": "id", "expected": donation_campaign_id, "actual": after_campaign.get("id")}],
            "notes": "Create verification uses response id plus read-back get donation campaign.",
        }
        receipt = _build_receipt(
            method="donation-campaigns.create",
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
                "method": "donation-campaigns.create",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "donation-campaigns.create"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "donation-campaigns.create"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "donation-campaigns.create"})
        return 1


def cmd_donation_campaigns_update(args, ctx) -> int:
    try:
        donation_campaign_id = _coerce_non_empty_text(
            getattr(args, "donation_campaign_id", None),
            field="donation-campaign-id",
        )
        body, campaign = _normalize_update_body(
            getattr(args, "donation_campaign_json", None),
            donation_campaign_id=donation_campaign_id,
        )
        headers, auth_mode = _resolve_donation_campaigns_auth(ctx=ctx)
        current_campaign = _get_campaign(donation_campaign_id=donation_campaign_id, ctx=ctx, headers=headers)
        request = {
            "method": "PATCH",
            "path": f"/donation-campaigns/v2/donation-campaigns/{donation_campaign_id}",
            "body": body,
        }
        selector = {
            "kind": "wix-donation-campaign",
            "operation": "update",
            "donation_campaign_id": donation_campaign_id,
        }
        before_state = {"donationCampaign": current_campaign}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="donation-campaigns.update", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="donation-campaigns.update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "update", "campaign": campaign}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify update by rereading the donation campaign and matching revision or requested fields.",
                },
                rollback_notes="No automatic rollback. Use the saved before-state snapshot for manual recovery only.",
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "donation-campaigns.update",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="donation-campaigns.update", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={"donationCampaign": _get_campaign(donation_campaign_id=donation_campaign_id, ctx=ctx, headers=headers)},
        )
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/donation-campaigns/v2/donation-campaigns/{donation_campaign_id}",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_campaign = _get_campaign(donation_campaign_id=donation_campaign_id, ctx=ctx, headers=headers)
        verification = {
            "ok": str(after_campaign.get("id") or "") == donation_campaign_id
            and str(after_campaign.get("revision") or "") != str(current_campaign.get("revision") or ""),
            "type": "read-after-write",
            "path": f"/donation-campaigns/v2/donation-campaigns/{donation_campaign_id}",
            "method": "GET",
            "before": current_campaign,
            "after": after_campaign,
            "checks": [
                {"field": "id", "expected": donation_campaign_id, "actual": after_campaign.get("id")},
                {
                    "field": "revision",
                    "expected": "changed",
                    "actual": {
                        "before": current_campaign.get("revision"),
                        "after": after_campaign.get("revision"),
                    },
                },
            ],
            "notes": "Update verification uses read-back get donation campaign and expects revision to change.",
        }
        receipt = _build_receipt(
            method="donation-campaigns.update",
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
                "method": "donation-campaigns.update",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "donation-campaigns.update"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "donation-campaigns.update"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "donation-campaigns.update"})
        return 1


def cmd_donation_campaigns_bulk_create(args, ctx) -> int:
    try:
        body, campaigns, _ = _normalize_bulk_campaigns_body(
            getattr(args, "donation_campaigns_json", None),
            field="donation-campaigns-json",
            require_revision=False,
        )
        headers, auth_mode = _resolve_donation_campaigns_auth(ctx=ctx)
        request = {"method": "POST", "path": "/donation-campaigns/v2/bulk/donation-campaigns/create", "body": body}
        selector = {"kind": "wix-donation-campaign", "operation": "bulk-create"}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="donation-campaigns.bulk-create", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="donation-campaigns.bulk-create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={},
                proposed_changes=[{"operation": "bulk-create", "count": len(campaigns)}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify response IDs and reread the created donation campaigns when the provider returns IDs.",
                },
                rollback_notes="No automatic rollback. Bulk create is manual-recovery only.",
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "donation-campaigns.bulk-create",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="donation-campaigns.bulk-create", expected_selector=selector, ctx=ctx)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/donation-campaigns/v2/bulk/donation-campaigns/create",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_campaigns = _extract_campaigns(response, operation="donation-campaigns.bulk-create")
        created_ids = [_extract_campaign_id(campaign, operation="donation-campaigns.bulk-create") for campaign in created_campaigns]
        after_campaigns = [_get_campaign(donation_campaign_id=campaign_id, ctx=ctx, headers=headers) for campaign_id in created_ids]
        verification = {
            "ok": bool(created_ids) and len(after_campaigns) == len(created_ids),
            "type": "read-after-write",
            "paths": [f"/donation-campaigns/v2/donation-campaigns/{campaign_id}" for campaign_id in created_ids],
            "method": "GET",
            "after": after_campaigns,
            "checks": [
                {"field": "ids", "expected_count": len(created_ids), "actual_count": len(after_campaigns)},
            ],
            "notes": "Bulk create verification uses returned IDs plus read-back get donation campaign.",
        }
        receipt = _build_receipt(
            method="donation-campaigns.bulk-create",
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
                "method": "donation-campaigns.bulk-create",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "donation-campaigns.bulk-create"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "donation-campaigns.bulk-create"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "donation-campaigns.bulk-create"})
        return 1


def cmd_donation_campaigns_bulk_update(args, ctx) -> int:
    try:
        body, _, donation_campaign_ids = _normalize_bulk_campaigns_body(
            getattr(args, "donation_campaigns_json", None),
            field="donation-campaigns-json",
            require_revision=True,
        )
        headers, auth_mode = _resolve_donation_campaigns_auth(ctx=ctx)
        current_campaigns = [
            _get_campaign(donation_campaign_id=campaign_id, ctx=ctx, headers=headers)
            for campaign_id in donation_campaign_ids
        ]
        request = {"method": "POST", "path": "/donation-campaigns/v2/bulk/donation-campaigns/update", "body": body}
        selector = {
            "kind": "wix-donation-campaign",
            "operation": "bulk-update",
            "donation_campaign_ids": donation_campaign_ids,
        }
        before_state = {"donationCampaigns": current_campaigns}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="donation-campaigns.bulk-update", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="donation-campaigns.bulk-update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "bulk-update", "ids": donation_campaign_ids}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify by rereading each donation campaign and checking revision changes.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "donation-campaigns.bulk-update",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="donation-campaigns.bulk-update", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={
                "donationCampaigns": [
                    _get_campaign(donation_campaign_id=campaign_id, ctx=ctx, headers=headers)
                    for campaign_id in donation_campaign_ids
                ]
            },
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/donation-campaigns/v2/bulk/donation-campaigns/update",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_campaigns = [
            _get_campaign(donation_campaign_id=campaign_id, ctx=ctx, headers=headers)
            for campaign_id in donation_campaign_ids
        ]
        verification = {
            "ok": len(after_campaigns) == len(current_campaigns)
            and all(
                str(after.get("revision") or "") != str(before.get("revision") or "")
                for before, after in zip(current_campaigns, after_campaigns)
            ),
            "type": "read-after-write",
            "paths": [f"/donation-campaigns/v2/donation-campaigns/{campaign_id}" for campaign_id in donation_campaign_ids],
            "method": "GET",
            "before": current_campaigns,
            "after": after_campaigns,
            "checks": [
                {"field": "ids", "expected_count": len(donation_campaign_ids), "actual_count": len(after_campaigns)},
            ],
            "notes": "Bulk update verification rereads each donation campaign and expects revision changes.",
        }
        receipt = _build_receipt(
            method="donation-campaigns.bulk-update",
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
                "method": "donation-campaigns.bulk-update",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "donation-campaigns.bulk-update"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "donation-campaigns.bulk-update"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "donation-campaigns.bulk-update"})
        return 1


def cmd_donation_campaigns_bulk_update_tags(args, ctx) -> int:
    try:
        body, donation_campaign_ids = _normalize_bulk_update_tags_body(getattr(args, "update_tags_json", None))
        headers, auth_mode = _resolve_donation_campaigns_auth(ctx=ctx)
        current_campaigns = [
            _get_campaign(donation_campaign_id=campaign_id, ctx=ctx, headers=headers)
            for campaign_id in donation_campaign_ids
        ]
        request = {
            "method": "POST",
            "path": "/donation-campaigns/v2/bulk/donation-campaigns/update-tags",
            "body": body,
        }
        selector = {
            "kind": "wix-donation-campaign",
            "operation": "bulk-update-tags",
            "donation_campaign_ids": donation_campaign_ids,
        }
        before_state = {"donationCampaigns": current_campaigns}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="donation-campaigns.bulk-update-tags", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="donation-campaigns.bulk-update-tags",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "bulk-update-tags", "ids": donation_campaign_ids, "body": body}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify by rereading the campaigns and checking tag membership when tags are returned.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "donation-campaigns.bulk-update-tags",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="donation-campaigns.bulk-update-tags", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={
                "donationCampaigns": [
                    _get_campaign(donation_campaign_id=campaign_id, ctx=ctx, headers=headers)
                    for campaign_id in donation_campaign_ids
                ]
            },
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/donation-campaigns/v2/bulk/donation-campaigns/update-tags",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_campaigns = [
            _get_campaign(donation_campaign_id=campaign_id, ctx=ctx, headers=headers)
            for campaign_id in donation_campaign_ids
        ]
        assign_tags = set(tag for tag in body.get("assignTags", []) if isinstance(tag, str))
        unassign_tags = set(tag for tag in body.get("unassignTags", []) if isinstance(tag, str))
        checks: list[dict[str, Any]] = []
        ok = len(after_campaigns) == len(donation_campaign_ids)
        for campaign in after_campaigns:
            tags = campaign.get("tags", [])
            if isinstance(tags, list):
                tag_values = {tag for tag in tags if isinstance(tag, str)}
                checks.append(
                    {
                        "field": "tags",
                        "campaign_id": campaign.get("id"),
                        "assigned_present": sorted(assign_tags.intersection(tag_values)),
                        "unassigned_absent": sorted(unassign_tags.difference(tag_values)),
                    }
                )
                ok = ok and assign_tags.issubset(tag_values) and tag_values.isdisjoint(unassign_tags)
        verification = {
            "ok": ok,
            "type": "read-after-write",
            "paths": [f"/donation-campaigns/v2/donation-campaigns/{campaign_id}" for campaign_id in donation_campaign_ids],
            "method": "GET",
            "before": current_campaigns,
            "after": after_campaigns,
            "checks": checks,
            "notes": "Bulk tag verification rereads each donation campaign and checks assignTags/unassignTags when tags are returned.",
        }
        receipt = _build_receipt(
            method="donation-campaigns.bulk-update-tags",
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
                "method": "donation-campaigns.bulk-update-tags",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "donation-campaigns.bulk-update-tags"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "donation-campaigns.bulk-update-tags"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "donation-campaigns.bulk-update-tags"})
        return 1


def cmd_donation_campaigns_bulk_update_tags_by_filter(args, ctx) -> int:
    try:
        body = _normalize_bulk_update_tags_by_filter_body(getattr(args, "update_tags_json", None))
        headers, auth_mode = _resolve_donation_campaigns_auth(ctx=ctx)
        request = {
            "method": "POST",
            "path": "/donation-campaigns/v2/bulk/donation-campaigns/update-tags-by-filter",
            "body": body,
        }
        selector = {
            "kind": "wix-donation-campaign",
            "operation": "bulk-update-tags-by-filter",
            "filter": body.get("filter"),
        }
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="donation-campaigns.bulk-update-tags-by-filter", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="donation-campaigns.bulk-update-tags-by-filter",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={},
                proposed_changes=[{"operation": "bulk-update-tags-by-filter", "body": body}],
                verification_plan={
                    "type": "provider-response-plus-async-job",
                    "notes": "Verify returned jobId, then inspect progress with async-jobs get or list-items.",
                },
                state_capture_notes="No reliable before-state snapshot is captured here because the official method is async and may target a large filtered set.",
                rollback_notes="No automatic rollback. Review the returned async job and use a new corrective tag update if needed.",
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "donation-campaigns.bulk-update-tags-by-filter",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="donation-campaigns.bulk-update-tags-by-filter", expected_selector=selector, ctx=ctx)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/donation-campaigns/v2/bulk/donation-campaigns/update-tags-by-filter",
            headers=headers,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        job_id = _extract_job_id(response, operation="donation-campaigns.bulk-update-tags-by-filter")
        verification = {
            "ok": bool(job_id),
            "type": "provider-response-plus-async-job",
            "job_id": job_id,
            "checks": [{"field": "jobId", "expected": "non-empty", "actual": job_id}],
            "notes": "The official method is async. This verification proves job creation only; inspect progress with async-jobs.",
        }
        receipt = _build_receipt(
            method="donation-campaigns.bulk-update-tags-by-filter",
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
                "method": "donation-campaigns.bulk-update-tags-by-filter",
                "auth_mode": auth_mode,
                "receipt": receipt,
                "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
            }
        )
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "donation-campaigns.bulk-update-tags-by-filter"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "donation-campaigns.bulk-update-tags-by-filter"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "donation-campaigns.bulk-update-tags-by-filter"})
        return 1
