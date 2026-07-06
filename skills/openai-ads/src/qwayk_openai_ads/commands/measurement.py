from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from ..config import credential_fingerprint
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..sanitize import REDACTED, redact_url, redact_value


SUPPORTED_EVENTS = [
    {"event": "app_installed", "data_type": "customer_action", "use": "A user installs an app."},
    {"event": "app_opened", "data_type": "customer_action", "use": "A user opens an app."},
    {
        "event": "appointment_scheduled",
        "data_type": "customer_action",
        "use": "A user books a meeting, demo, or consultation.",
    },
    {"event": "checkout_started", "data_type": "contents", "use": "A user starts checkout."},
    {
        "event": "contents_viewed",
        "data_type": "contents",
        "use": "A user views a product, listing, article, or other content unit.",
    },
    {"event": "custom", "data_type": "custom", "use": "A user-defined event."},
    {
        "event": "items_added",
        "data_type": "contents",
        "use": "A user adds one or more items to a cart, bundle, or selection.",
    },
    {"event": "lead_created", "data_type": "customer_action", "use": "A user submits a lead form or requests contact."},
    {"event": "order_created", "data_type": "contents", "use": "A purchase is completed."},
    {"event": "page_viewed", "data_type": "contents", "use": "A user lands on or views an important page."},
    {
        "event": "registration_completed",
        "data_type": "customer_action",
        "use": "A user finishes an account or event registration flow.",
    },
    {"event": "subscription_created", "data_type": "plan_enrollment", "use": "A paid subscription starts."},
    {"event": "trial_started", "data_type": "plan_enrollment", "use": "A free trial starts."},
]


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _stable_sha256(value: Any) -> str | None:
    if value is None:
        return None
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_events(args: Any) -> list[dict[str, Any]]:
    if getattr(args, "events_file", None):
        payload = read_json_file(str(args.events_file))
    elif getattr(args, "events_json", None):
        try:
            payload = json.loads(str(args.events_json))
        except json.JSONDecodeError as e:
            raise ValidationError(f"--events-json is not valid JSON: {e.msg}") from None
    else:
        raise ValidationError("Provide --events-json or --events-file")

    events = payload.get("events") if isinstance(payload, dict) else payload
    if not isinstance(events, list):
        raise ValidationError("Events payload must be a JSON list or an object with an events list")
    for event in events:
        if not isinstance(event, dict):
            raise ValidationError("Each conversion event must be a JSON object")
    return events


def _pixel_id(ctx: dict[str, Any], args: Any) -> str:
    pixel_id = str(getattr(args, "pixel_id", "") or ctx["cfg"].pixel_id or "").strip()
    if not pixel_id:
        raise ValidationError("Missing pixel ID. Set OPENAI_ADS_PIXEL_ID or pass --pixel-id")
    return pixel_id


def _redacted_pixel_id(pixel_id: str) -> str:
    if len(pixel_id) <= 6:
        return REDACTED
    return pixel_id[:3] + "..." + pixel_id[-3:]


def _redact_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    redacted = []
    for event in events:
        safe = redact_value(event)
        if isinstance(safe, dict):
            for key in (
                "source_url",
                "oppref",
                "email",
                "emails",
                "external_id",
                "external_ids",
                "customer_id",
                "customer_ids",
                "hashed_email",
                "hashed_phone",
            ):
                if key in safe:
                    safe[key] = REDACTED
        redacted.append(safe)
    return redacted


def cmd_events_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    ctx["out"].emit(
        {
            "ok": True,
            "source": "https://developers.openai.com/ads/supported-events",
            "events": SUPPORTED_EVENTS,
            "count": len(SUPPORTED_EVENTS),
        }
    )
    return 0


def cmd_pixel_guide(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    ctx["out"].emit(
        {
            "ok": True,
            "source": "https://developers.openai.com/ads/measurement-pixel",
            "summary": "Install the JavaScript Pixel only after required consent is handled on the site.",
            "steps": [
                "Create or locate the Pixel ID in Ads Manager conversions.",
                "Install the OpenAI Ads JavaScript Pixel on the event pages.",
                "Send only supported event names and documented data shapes.",
                "Use the same event id when pairing browser events with server-side Conversions API events.",
            ],
        }
    )
    return 0


def cmd_image_tag_build(args: Any, ctx: dict[str, Any]) -> int:
    pixel_id = _pixel_id(ctx, args)
    event = str(getattr(args, "event", "") or "page_viewed").strip()
    data_type = str(getattr(args, "data_type", "") or "contents").strip()
    params = {"pid": pixel_id, "event": event, "data[type]": data_type}
    if getattr(args, "event_id", None):
        params["event_id"] = str(args.event_id)
    if getattr(args, "custom_event_name", None):
        params["custom_event_name"] = str(args.custom_event_name)
    for raw in getattr(args, "data", None) or []:
        if "=" not in raw:
            raise ValidationError("--data values must use name=value")
        key, value = raw.split("=", 1)
        if not key.strip():
            raise ValidationError("--data name cannot be empty")
        params[f"data[{key.strip()}]"] = value
    url = ctx["cfg"].conversions_base_url.rstrip("/") + "/sdk/events?" + urlencode(params)
    safe_url = redact_url(url).replace(pixel_id, _redacted_pixel_id(pixel_id))
    tag = f'<img src="{safe_url}" width="1" height="1" style="display:none" alt="" />'
    if bool(getattr(args, "noscript", False)):
        tag = f"<noscript>{tag}</noscript>"
    ctx["out"].emit(
        {
            "ok": True,
            "source": "https://developers.openai.com/ads/image-tag",
            "pixel_id": _redacted_pixel_id(pixel_id),
            "event": event,
            "url": safe_url,
            "html": tag,
            "notes": [
                "URL-encode all dynamic values before use.",
                "Render only after required measurement consent is handled.",
                "For browser/server deduplication, reuse the image tag event_id in the server event id.",
            ],
        }
    )
    return 0


def _build_conversion_plan(ctx: dict[str, Any], *, pixel_id: str, events: list[dict[str, Any]], validate_only: bool) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].conversions_base_url,
        "credential_fingerprint": credential_fingerprint(ctx["cfg"].conversions_api_key),
        "command": ctx.get("command_str"),
        "operation": {
            "family": "measurement",
            "command": "conversions-send",
            "method": "POST",
            "url": ctx["cfg"].conversions_base_url.rstrip("/") + "/events?pid=" + _redacted_pixel_id(pixel_id),
            "source": "https://developers.openai.com/ads/conversions-api",
        },
        "target": {"pixel_id": _redacted_pixel_id(pixel_id)},
        "target_sha256": _stable_sha256({"pixel_id": pixel_id}),
        "request_body": {"validate_only": validate_only, "events": _redact_events(events)},
        "request_body_sha256": _stable_sha256({"validate_only": validate_only, "events": events}),
        "risk_level": "high",
        "risk_reasons": ["measurement-change", "conversion-event-send", "no-snapshot"],
        "snapshot": {"available": False, "warning": "Conversions API events cannot be safely snapshotted before send."},
        "preconditions": [
            "review redacted event count and event types",
            "apply must use this saved plan with --plan-in",
            "Conversions API credential fingerprint must match",
            "real event send requires --apply --yes --ack-irreversible --ack-no-snapshot",
        ],
        "verification_plan": {
            "type": "provider-response",
            "notes": "OpenAI returns the Conversions API response. Follow Ads Manager reporting later for delivery effects.",
        },
        "rollback": {"supported": False, "notes": "Conversion events cannot be unsent by this CLI."},
    }


def _validate_plan(plan: dict[str, Any], ctx: dict[str, Any], *, pixel_id: str, events: list[dict[str, Any]], validate_only: bool) -> None:
    if str(plan.get("env_fingerprint") or "") != ctx["cfg"].conversions_base_url:
        raise SafetyError("Refused: plan conversions base URL does not match current environment")
    if plan.get("credential_fingerprint") != credential_fingerprint(ctx["cfg"].conversions_api_key):
        raise SafetyError("Refused: current Conversions API key fingerprint does not match the reviewed plan")
    if plan.get("target_sha256") != _stable_sha256({"pixel_id": pixel_id}):
        raise SafetyError("Refused: pixel ID does not match the reviewed plan")
    if plan.get("request_body_sha256") != _stable_sha256({"validate_only": validate_only, "events": events}):
        raise SafetyError("Refused: conversion event payload does not match the reviewed plan")


def cmd_conversions_send(args: Any, ctx: dict[str, Any]) -> int:
    if not ctx["cfg"].conversions_api_key:
        raise ValidationError("Missing OPENAI_ADS_CONVERSIONS_API_KEY")
    pixel_id = _pixel_id(ctx, args)
    events = _load_events(args)
    validate_only = bool(getattr(args, "validate_only", True))
    if bool(getattr(args, "real_events", False)):
        validate_only = False
    plan = _build_conversion_plan(ctx, pixel_id=pixel_id, events=events, validate_only=validate_only)
    if not bool(ctx.get("apply")):
        if ctx.get("plan_out"):
            write_json_file(Path(str(ctx["plan_out"])), plan)
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_path": ctx.get("plan_out")})
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: Conversions API send requires --apply --yes")
    if not ctx.get("plan_in"):
        raise SafetyError("Refused: Conversions API send requires --plan-in from the reviewed dry-run plan")
    reviewed_plan = read_json_file(str(ctx["plan_in"]))
    _validate_plan(reviewed_plan, ctx, pixel_id=pixel_id, events=events, validate_only=validate_only)
    if not validate_only and not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refused: real conversion events require --ack-irreversible")
    if not bool(ctx.get("ack_no_snapshot")):
        raise SafetyError("Refused: Conversions API send has no before-state snapshot; add --ack-no-snapshot only after reviewing that risk")

    url = ctx["cfg"].conversions_base_url.rstrip("/") + "/events"
    response = HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"openai-ads-safe-agent-cli/{ctx.get('tool_version')}",
    ).request(
        "POST",
        url,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ctx['cfg'].conversions_api_key}",
        },
        params={"pid": pixel_id},
        json_body={"validate_only": validate_only, "events": events},
        retries=1,
        url_sanitizer=redact_url,
    )
    try:
        body = response.json()
    except Exception:
        body = {"text": response.text()}
    receipt = {
        "ok": True,
        "applied": True,
        "generated_at_utc": _utc_now(),
        "operation": plan["operation"],
        "target": plan["target"],
        "validate_only": validate_only,
        "event_count": len(events),
        "request_body_sha256": plan["request_body_sha256"],
        "response": {"status": response.status, "url": redact_url(response.url), "body": redact_value(body)},
        "verification": {"status": "response-captured"},
    }
    if ctx.get("receipt_out"):
        write_json_file(Path(str(ctx["receipt_out"])), receipt)
    ctx["out"].emit({"ok": True, "applied": True, "receipt": receipt, "receipt_path": ctx.get("receipt_out")})
    return 0


def cmd_product_feeds_guide(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    ctx["out"].emit(
        {
            "ok": True,
            "source": "https://developers.openai.com/ads/product-feeds",
            "summary": "Product-feed campaigns use the normal campaigns, ad groups, ads, and insights API commands. Feed connection and catalog upload happen in Ads Manager/SFTP, not this API.",
            "api_commands": [
                "api campaigns create-campaign",
                "api ad-groups create-ad-group",
                "api ads create-ad",
                "api insights get-ad-account-insights",
            ],
        }
    )
    return 0


def cmd_targeting_guide(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    ctx["out"].emit(
        {
            "ok": True,
            "source": "https://developers.openai.com/ads/campaign-targeting",
            "summary": "Use geo lookup to find country, region, or DMA IDs, then pass them in campaign targeting when creating or updating a campaign.",
            "first_command": "openai-ads-safe-agent-cli api targeting get-geo-lookup --query q='San Francisco' --query limit=5",
        }
    )
    return 0
