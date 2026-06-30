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


def _coerce_non_negative_int(raw: Any, *, field: str, maximum: int | None = None) -> int | None:
    if raw is None:
        return None
    if not isinstance(raw, int):
        raise ValidationError(f"--{field} must be an integer")
    if raw < 0:
        raise ValidationError(f"--{field} must be 0 or greater")
    if maximum is not None and raw > maximum:
        raise ValidationError(f"--{field} must be at most {maximum}")
    return raw


def _coerce_custom_embed_payload(raw: Any, *, field: str) -> dict[str, Any]:
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _validate_position(value: Any, *, field: str) -> str:
    position = _coerce_non_empty_text(value, field=field)
    if position not in {"HEAD", "BODY_START", "BODY_END"}:
        raise ValidationError(f"--{field} position must be HEAD, BODY_START, or BODY_END")
    return position


def _validate_embed_data(raw: Any, *, field: str) -> dict[str, Any]:
    if not isinstance(raw, dict) or not raw:
        raise ValidationError(f"--{field} must be a JSON object")
    category = _coerce_non_empty_text(raw.get("category"), field=f"{field}.category")
    if category not in {"ESSENTIAL", "FUNCTIONAL", "ANALYTICS", "ADVERTISING", "DATA_TO_THIRD_PARTY"}:
        raise ValidationError(
            f"--{field}.category must be ESSENTIAL, FUNCTIONAL, ANALYTICS, ADVERTISING, or DATA_TO_THIRD_PARTY"
        )
    html = _coerce_non_empty_text(raw.get("html"), field=f"{field}.html")
    embed_data = dict(raw)
    embed_data["category"] = category
    embed_data["html"] = html
    return embed_data


def _normalize_create_payload(payload: dict[str, Any]) -> dict[str, Any]:
    name = _coerce_non_empty_text(payload.get("name"), field="custom-embed-json.name")
    position = _validate_position(payload.get("position"), field="custom-embed-json.position")
    embed_data = _validate_embed_data(payload.get("embedData"), field="custom-embed-json.embedData")
    normalized = dict(payload)
    normalized["name"] = name
    normalized["position"] = position
    normalized["embedData"] = embed_data
    return normalized


def _normalize_update_payload(payload: dict[str, Any], *, custom_embed_id: str) -> dict[str, Any]:
    revision = _coerce_non_empty_text(payload.get("revision"), field="custom-embed-json.revision")
    if "id" in payload and _coerce_non_empty_text(payload.get("id"), field="custom-embed-json.id") != custom_embed_id:
        raise SafetyError("Refused: custom embed id in payload does not match --custom-embed-id")
    normalized = dict(payload)
    normalized["id"] = custom_embed_id
    normalized["revision"] = revision
    if "position" in normalized:
        normalized["position"] = _validate_position(normalized.get("position"), field="custom-embed-json.position")
    if "embedData" in normalized:
        normalized["embedData"] = _validate_embed_data(
            normalized.get("embedData"), field="custom-embed-json.embedData"
        )
    if "name" in normalized:
        normalized["name"] = _coerce_non_empty_text(normalized.get("name"), field="custom-embed-json.name")
    return normalized


def _resolve_custom_embeds_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="custom-embeds",
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


def _extract_custom_embed(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    custom_embed = payload.get("customEmbed")
    if not isinstance(custom_embed, dict):
        raise ValidationError(f"{operation} response did not include a customEmbed object")
    return custom_embed


def _extract_custom_embed_id(custom_embed: dict[str, Any], *, operation: str) -> str:
    raw_id = custom_embed.get("id")
    if not isinstance(raw_id, str) or not raw_id.strip():
        raise ValidationError(f"{operation} response did not include a usable custom embed id")
    return raw_id.strip()


def _extract_custom_embeds(payload: dict[str, Any]) -> list[dict[str, Any]]:
    custom_embeds = payload.get("customEmbeds")
    if not isinstance(custom_embeds, list):
        raise ValidationError("custom-embeds.list response did not include a customEmbeds array")
    return [item for item in custom_embeds if isinstance(item, dict)]


def _list_custom_embeds(
    *,
    limit: int | None,
    offset: int | None,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {}
    if limit is not None:
        params["paging.limit"] = limit
    if offset is not None:
        params["paging.offset"] = offset
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path="/embeds/v1/custom-embeds",
        headers=headers,
        params=params or None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_custom_embeds(payload)


def _get_custom_embed(
    *,
    custom_embed_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/embeds/v1/custom-embeds/{custom_embed_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_custom_embed(payload, operation="custom-embeds.get")


def _get_custom_embed_optional(
    *,
    custom_embed_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> tuple[dict[str, Any] | None, int | None]:
    try:
        return _get_custom_embed(custom_embed_id=custom_embed_id, ctx=ctx, headers=headers), None
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
        "risk_reasons": ["custom-embed-write"] + (["irreversible"] if requires_ack else []),
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
                "Captured current custom embed state before planning."
                if has_before_state
                else "No useful before-state snapshot exists for this create-style write."
            ),
        },
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "rollback": {
            "supported": False,
            "notes": (
                "No automatic rollback. Use the saved before-state only as a manual reference."
                if has_before_state
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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="custom-embeds")


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: custom embed state changed since plan was created")


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


def _build_verification_checks(expected_embed: dict[str, Any], actual_embed: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for field in ("id", "name", "position", "enabled", "loadOnce", "domain", "pageFilter"):
        if field in expected_embed:
            checks.append({"field": field, "expected": expected_embed.get(field), "actual": actual_embed.get(field)})
    if "embedData" in expected_embed:
        checks.append(
            {
                "field": "embedData",
                "expected": expected_embed.get("embedData"),
                "actual": actual_embed.get("embedData"),
            }
        )
    return checks


def cmd_custom_embeds_list(args, ctx) -> int:
    try:
        limit = _coerce_non_negative_int(getattr(args, "limit", None), field="limit", maximum=100)
        offset = _coerce_non_negative_int(getattr(args, "offset", None), field="offset")
        headers, auth_mode = _resolve_custom_embeds_auth(ctx=ctx)
        custom_embeds = _list_custom_embeds(limit=limit, offset=offset, ctx=ctx, headers=headers)
        params: dict[str, Any] = {}
        if limit is not None:
            params["paging.limit"] = limit
        if offset is not None:
            params["paging.offset"] = offset
        out = {
            "ok": True,
            "method": "custom-embeds.list",
            "auth_mode": auth_mode,
            "request": {"method": "GET", "path": "/embeds/v1/custom-embeds", "params": params or None},
            "response": {"customEmbeds": custom_embeds},
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "custom-embeds.list"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "custom-embeds.list"}
        )
        return 1


def cmd_custom_embeds_get(args, ctx) -> int:
    try:
        custom_embed_id = _coerce_non_empty_text(getattr(args, "custom_embed_id", None), field="custom-embed-id")
        headers, auth_mode = _resolve_custom_embeds_auth(ctx=ctx)
        custom_embed = _get_custom_embed(custom_embed_id=custom_embed_id, ctx=ctx, headers=headers)
        out = {
            "ok": True,
            "method": "custom-embeds.get",
            "auth_mode": auth_mode,
            "request": {"method": "GET", "path": f"/embeds/v1/custom-embeds/{custom_embed_id}"},
            "response": {"customEmbed": custom_embed},
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "custom-embeds.get"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "custom-embeds.get"}
        )
        return 1


def cmd_custom_embeds_create(args, ctx) -> int:
    try:
        custom_embed = _normalize_create_payload(
            _coerce_custom_embed_payload(getattr(args, "custom_embed_json", None), field="custom-embed-json")
        )
        headers, auth_mode = _resolve_custom_embeds_auth(ctx=ctx)
        existing_custom_embeds = _list_custom_embeds(limit=None, offset=None, ctx=ctx, headers=headers)
        request = {"method": "POST", "path": "/embeds/v1/custom-embeds", "body": {"customEmbed": custom_embed}}
        selector = {
            "kind": "wix-custom-embed",
            "operation": "create",
            "name": custom_embed.get("name"),
            "position": custom_embed.get("position"),
        }
        before_state = {"customEmbeds": existing_custom_embeds}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="custom-embeds.create",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="custom-embeds.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[
                    {
                        "operation": "create",
                        "name": custom_embed.get("name"),
                        "position": custom_embed.get("position"),
                        "category": (custom_embed.get("embedData") or {}).get("category"),
                    }
                ],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify create response id and re-read the created custom embed.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "custom-embeds.create",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="custom-embeds.create",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={"customEmbeds": _list_custom_embeds(limit=None, offset=None, ctx=ctx, headers=headers)},
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/embeds/v1/custom-embeds",
            headers=headers,
            params=None,
            json_body={"customEmbed": custom_embed},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_custom_embed = _extract_custom_embed(response, operation="custom-embeds.create")
        created_id = _extract_custom_embed_id(created_custom_embed, operation="custom-embeds.create")
        after_custom_embed = _get_custom_embed(custom_embed_id=created_id, ctx=ctx, headers=headers)
        expected_after = dict(custom_embed)
        expected_after["id"] = created_id
        checks = _build_verification_checks(expected_after, after_custom_embed)
        verification = {
            "ok": all(check["expected"] == check["actual"] for check in checks),
            "type": "read-after-write",
            "path": f"/embeds/v1/custom-embeds/{created_id}",
            "method": "GET",
            "checks": checks,
            "after": after_custom_embed,
            "notes": "Create verification uses response id plus read-back get custom embed.",
        }
        receipt = _build_receipt(
            method="custom-embeds.create",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "custom-embeds.create",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "refused": True,
                "reasons": [str(exc)],
                "refusal_type": "SafetyError",
                "method": "custom-embeds.create",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "custom-embeds.create"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "custom-embeds.create"}
        )
        return 1


def cmd_custom_embeds_update(args, ctx) -> int:
    try:
        custom_embed_id = _coerce_non_empty_text(getattr(args, "custom_embed_id", None), field="custom-embed-id")
        custom_embed = _normalize_update_payload(
            _coerce_custom_embed_payload(getattr(args, "custom_embed_json", None), field="custom-embed-json"),
            custom_embed_id=custom_embed_id,
        )
        headers, auth_mode = _resolve_custom_embeds_auth(ctx=ctx)
        current_custom_embed = _get_custom_embed(custom_embed_id=custom_embed_id, ctx=ctx, headers=headers)
        request = {
            "method": "PATCH",
            "path": f"/embeds/v1/custom-embeds/{custom_embed_id}",
            "body": {"customEmbed": custom_embed},
        }
        selector = {"kind": "wix-custom-embed", "operation": "update", "custom_embed_id": custom_embed_id}
        before_state = {"customEmbed": current_custom_embed}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="custom-embeds.update",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="custom-embeds.update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[
                    {
                        "operation": "update",
                        "custom_embed_id": custom_embed_id,
                        "fields": sorted(custom_embed.keys()),
                    }
                ],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify changed fields by re-reading the custom embed.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "custom-embeds.update",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="custom-embeds.update",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={"customEmbed": _get_custom_embed(custom_embed_id=custom_embed_id, ctx=ctx, headers=headers)},
        )
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/embeds/v1/custom-embeds/{custom_embed_id}",
            headers=headers,
            params=None,
            json_body={"customEmbed": custom_embed},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_custom_embed = _get_custom_embed(custom_embed_id=custom_embed_id, ctx=ctx, headers=headers)
        expected_after = dict(custom_embed)
        checks = _build_verification_checks(expected_after, after_custom_embed)
        verification = {
            "ok": all(check["expected"] == check["actual"] for check in checks),
            "type": "read-after-write",
            "path": f"/embeds/v1/custom-embeds/{custom_embed_id}",
            "method": "GET",
            "before": current_custom_embed,
            "after": after_custom_embed,
            "checks": checks,
            "notes": "Update verification uses read-back get custom embed.",
        }
        receipt = _build_receipt(
            method="custom-embeds.update",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "custom-embeds.update",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "refused": True,
                "reasons": [str(exc)],
                "refusal_type": "SafetyError",
                "method": "custom-embeds.update",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "custom-embeds.update"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "custom-embeds.update"}
        )
        return 1


def cmd_custom_embeds_delete(args, ctx) -> int:
    try:
        custom_embed_id = _coerce_non_empty_text(getattr(args, "custom_embed_id", None), field="custom-embed-id")
        headers, auth_mode = _resolve_custom_embeds_auth(ctx=ctx)
        current_custom_embed = _get_custom_embed(custom_embed_id=custom_embed_id, ctx=ctx, headers=headers)
        request = {"method": "DELETE", "path": f"/embeds/v1/custom-embeds/{custom_embed_id}"}
        selector = {"kind": "wix-custom-embed", "operation": "delete", "custom_embed_id": custom_embed_id}
        before_state = {"customEmbed": current_custom_embed}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="custom-embeds.delete",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="custom-embeds.delete",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[
                    {
                        "operation": "delete",
                        "custom_embed_id": custom_embed_id,
                        "name": current_custom_embed.get("name"),
                        "position": current_custom_embed.get("position"),
                    }
                ],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify delete by expecting get custom embed to return 404.",
                },
                requires_ack=True,
            )

        if not _should_apply(ctx, requires_ack=True):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "custom-embeds.delete",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="custom-embeds.delete",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={"customEmbed": _get_custom_embed(custom_embed_id=custom_embed_id, ctx=ctx, headers=headers)},
        )
        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/embeds/v1/custom-embeds/{custom_embed_id}",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_custom_embed, after_status = _get_custom_embed_optional(
            custom_embed_id=custom_embed_id,
            ctx=ctx,
            headers=headers,
        )
        verification = {
            "ok": after_status == 404 and after_custom_embed is None,
            "type": "read-after-write",
            "path": f"/embeds/v1/custom-embeds/{custom_embed_id}",
            "method": "GET",
            "before": current_custom_embed,
            "after": after_custom_embed,
            "expected_http_status": 404,
            "actual_http_status": after_status,
            "notes": "Delete verification expects get custom embed to return 404.",
        }
        receipt = _build_receipt(
            method="custom-embeds.delete",
            selector=selector,
            request=request,
            response=response,
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        out = {
            "ok": bool(verification.get("ok")),
            "dry_run": False,
            "method": "custom-embeds.delete",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "refused": True,
                "reasons": [str(exc)],
                "refusal_type": "SafetyError",
                "method": "custom-embeds.delete",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "custom-embeds.delete"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "custom-embeds.delete"}
        )
        return 1
