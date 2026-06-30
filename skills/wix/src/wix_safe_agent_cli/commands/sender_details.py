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


def _coerce_optional_non_empty_text(raw: Any, *, field: str) -> str | None:
    if raw is None:
        return None
    return _coerce_non_empty_text(raw, field=field)


def _coerce_paging_limit(raw: Any) -> int | None:
    if raw is None:
        return None
    if not isinstance(raw, int):
        raise ValidationError("--limit must be an integer")
    if raw < 0 or raw > 100:
        raise ValidationError("--limit must be between 0 and 100")
    return raw


def _coerce_sender_details_payload(raw: Any, *, sender_details_id: str | None = None) -> dict[str, Any]:
    value = _read_json_arg(raw, field="sender-details-json")
    if not isinstance(value, dict) or not value:
        raise ValidationError("--sender-details-json must be a non-empty JSON object")
    payload = dict(value)
    sender_details = payload.get("senderDetails")
    if not isinstance(sender_details, dict) or not sender_details:
        raise ValidationError("--sender-details-json.senderDetails must be a non-empty JSON object")
    normalized = dict(sender_details)
    if sender_details_id is not None:
        payload_id = normalized.get("id")
        if payload_id is not None and _coerce_non_empty_text(payload_id, field="sender-details-json.senderDetails.id") != sender_details_id:
            raise ValidationError("--sender-details-json.senderDetails.id must match --sender-details-id")
        normalized["id"] = sender_details_id
    if "fromName" in normalized:
        normalized["fromName"] = _coerce_non_empty_text(
            normalized.get("fromName"),
            field="sender-details-json.senderDetails.fromName",
        )
    if "fromEmailAddress" in normalized:
        normalized["fromEmailAddress"] = _coerce_non_empty_text(
            normalized.get("fromEmailAddress"),
            field="sender-details-json.senderDetails.fromEmailAddress",
        )
    if sender_details_id is None:
        if "fromName" not in normalized:
            raise ValidationError("--sender-details-json.senderDetails.fromName is required")
        if "fromEmailAddress" not in normalized:
            raise ValidationError("--sender-details-json.senderDetails.fromEmailAddress is required")
    if sender_details_id is not None and set(normalized) <= {"id"}:
        raise ValidationError("--sender-details-json must include at least one field besides id for update")
    payload["senderDetails"] = normalized
    return payload


def _resolve_sender_details_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="sender-details",
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


def _extract_sender_details(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    sender_details = payload.get("senderDetails")
    if not isinstance(sender_details, dict):
        raise ValidationError(f"{operation} response did not include a senderDetails object")
    return sender_details


def _extract_sender_details_list(payload: dict[str, Any], *, operation: str) -> list[dict[str, Any]]:
    sender_details = payload.get("senderDetails")
    if not isinstance(sender_details, list):
        raise ValidationError(f"{operation} response did not include a senderDetails array")
    return [item for item in sender_details if isinstance(item, dict)]


def _find_sender_details_by_id(sender_details: list[dict[str, Any]], sender_details_id: str) -> dict[str, Any] | None:
    for item in sender_details:
        if isinstance(item.get("id"), str) and item.get("id") == sender_details_id:
            return item
    return None


def _list_sender_details(*, limit: int | None, cursor: str | None, ctx: dict[str, Any], headers: dict[str, str]) -> list[dict[str, Any]]:
    params: dict[str, Any] = {}
    if limit is not None:
        params["paging.limit"] = limit
    if cursor:
        params["paging.cursor"] = cursor
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path="/sender-details/v1/sender-details",
        headers=headers,
        params=params or None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_sender_details_list(payload, operation="sender-details.list")


def _get_sender_details(*, sender_details_id: str, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/sender-details/v1/sender-details/{sender_details_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_sender_details(payload, operation="sender-details.get")


def _get_sender_details_optional(
    *,
    sender_details_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> tuple[dict[str, Any] | None, int | None]:
    try:
        return _get_sender_details(sender_details_id=sender_details_id, ctx=ctx, headers=headers), None
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            return None, 404
        raise


def _get_default_sender_details(*, ctx: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path="/sender-details/v1/sender-details/default",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_sender_details(payload, operation="sender-details.get-default")


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
        "risk_level": "medium" if not requires_ack else "high",
        "risk_reasons": ["sender-details-write"] + (["irreversible"] if requires_ack else []),
        "provider_notes": [
            "Wix docs say sender details can only use verified sender email addresses.",
            "Wix docs say the same sender-details scope is Access Verticals by Automations.",
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
            "before_state_available": bool(before_state),
            "notes": (
                "Captured current sender details state before planning."
                if before_state
                else "No useful before-state snapshot exists for this create-style write."
            ),
        },
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "rollback": {
            "supported": False,
            "notes": (
                "No automatic rollback. Use the saved before-state only as a manual reference."
                if before_state
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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="sender-details")


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: sender details changed since plan was created")


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
            "notes": "Receipt stores sender details metadata only.",
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {"automatic": False, "notes": "Recovery is manual only."},
    }


def cmd_sender_details_list(args, ctx) -> int:
    try:
        headers, auth_mode = _resolve_sender_details_auth(ctx=ctx)
        limit = _coerce_paging_limit(getattr(args, "limit", None))
        cursor = _coerce_optional_non_empty_text(getattr(args, "cursor", None), field="cursor")
        sender_details = _list_sender_details(limit=limit, cursor=cursor, ctx=ctx, headers=headers)
        params: dict[str, Any] = {}
        if limit is not None:
            params["paging.limit"] = limit
        if cursor:
            params["paging.cursor"] = cursor
        ctx["out"].emit(
            {
                "ok": True,
                "method": "sender-details.list",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": "/sender-details/v1/sender-details", "params": params},
                "response": {"senderDetails": sender_details},
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "sender-details.list"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "sender-details.list"})
        return 1


def cmd_sender_details_get(args, ctx) -> int:
    try:
        sender_details_id = _coerce_non_empty_text(getattr(args, "sender_details_id", None), field="sender-details-id")
        headers, auth_mode = _resolve_sender_details_auth(ctx=ctx)
        sender_details = _get_sender_details(sender_details_id=sender_details_id, ctx=ctx, headers=headers)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "sender-details.get",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": f"/sender-details/v1/sender-details/{sender_details_id}"},
                "response": {"senderDetails": sender_details},
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "sender-details.get"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "sender-details.get"})
        return 1


def cmd_sender_details_create(args, ctx) -> int:
    try:
        payload = _coerce_sender_details_payload(getattr(args, "sender_details_json", None))
        headers, auth_mode = _resolve_sender_details_auth(ctx=ctx)
        request = {"method": "POST", "path": "/sender-details/v1/sender-details", "body": payload}
        selector = {
            "kind": "wix-sender-details",
            "operation": "create",
            "fromName": payload["senderDetails"]["fromName"],
            "fromEmailAddress": payload["senderDetails"]["fromEmailAddress"],
        }
        before_state = {}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="sender-details.create", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="sender-details.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[
                    {
                        "operation": "create",
                        "fromName": payload["senderDetails"]["fromName"],
                        "fromEmailAddress": payload["senderDetails"]["fromEmailAddress"],
                    }
                ],
                verification_plan={"type": "read-after-write", "notes": "Verify the created sender details by id."},
            )

        if not _should_apply(ctx):
            ctx["out"].emit({"ok": True, "dry_run": True, "method": "sender-details.create", "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)})
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="sender-details.create", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(plan=loaded_plan, current_state={})
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/sender-details/v1/sender-details",
            headers=headers,
            params=None,
            json_body=payload,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created = _extract_sender_details(response, operation="sender-details.create")
        created_id = _coerce_non_empty_text(created.get("id"), field="response.senderDetails.id")
        after = _get_sender_details(sender_details_id=created_id, ctx=ctx, headers=headers)
        verification = {
            "ok": after.get("id") == created_id,
            "type": "read-after-write",
            "path": f"/sender-details/v1/sender-details/{created_id}",
            "method": "GET",
            "after": after,
            "checks": [{"field": "id", "expected": created_id, "actual": after.get("id")}],
        }
        receipt = _build_receipt(method="sender-details.create", selector=selector, request=request, response={"senderDetails": created}, verification=verification, plan=loaded_plan, ctx=ctx)
        ctx["out"].emit({"ok": bool(verification.get("ok")), "dry_run": False, "method": "sender-details.create", "auth_mode": auth_mode, "receipt": receipt, "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt)})
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "sender-details.create"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "sender-details.create"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "sender-details.create"})
        return 1


def cmd_sender_details_update(args, ctx) -> int:
    try:
        sender_details_id = _coerce_non_empty_text(getattr(args, "sender_details_id", None), field="sender-details-id")
        payload = _coerce_sender_details_payload(
            getattr(args, "sender_details_json", None),
            sender_details_id=sender_details_id,
        )
        headers, auth_mode = _resolve_sender_details_auth(ctx=ctx)
        current = _get_sender_details(sender_details_id=sender_details_id, ctx=ctx, headers=headers)
        request = {
            "method": "PATCH",
            "path": f"/sender-details/v1/sender-details/{sender_details_id}",
            "body": payload,
        }
        selector = {"kind": "wix-sender-details", "operation": "update", "sender_details_id": sender_details_id}
        before_state = {"senderDetails": current}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="sender-details.update", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="sender-details.update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "update", "senderDetailsId": sender_details_id, "fields": sorted(payload["senderDetails"].keys())}],
                verification_plan={"type": "read-after-write", "notes": "Verify the updated sender details by id."},
            )

        if not _should_apply(ctx):
            ctx["out"].emit({"ok": True, "dry_run": True, "method": "sender-details.update", "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)})
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="sender-details.update", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(plan=loaded_plan, current_state={"senderDetails": _get_sender_details(sender_details_id=sender_details_id, ctx=ctx, headers=headers)})
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/sender-details/v1/sender-details/{sender_details_id}",
            headers=headers,
            params=None,
            json_body=payload,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after = _get_sender_details(sender_details_id=sender_details_id, ctx=ctx, headers=headers)
        checks = [{"field": "id", "expected": sender_details_id, "actual": after.get("id")}]
        for field in ("fromName", "fromEmailAddress"):
            if field in payload["senderDetails"]:
                checks.append({"field": field, "expected": payload["senderDetails"][field], "actual": after.get(field)})
        verification = {"ok": all(check["expected"] == check["actual"] for check in checks), "type": "read-after-write", "path": f"/sender-details/v1/sender-details/{sender_details_id}", "method": "GET", "before": current, "after": after, "checks": checks}
        receipt = _build_receipt(method="sender-details.update", selector=selector, request=request, response=response, verification=verification, plan=loaded_plan, ctx=ctx)
        ctx["out"].emit({"ok": bool(verification.get("ok")), "dry_run": False, "method": "sender-details.update", "auth_mode": auth_mode, "receipt": receipt, "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt)})
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "sender-details.update"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "sender-details.update"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "sender-details.update"})
        return 1


def cmd_sender_details_delete(args, ctx) -> int:
    try:
        sender_details_id = _coerce_non_empty_text(getattr(args, "sender_details_id", None), field="sender-details-id")
        headers, auth_mode = _resolve_sender_details_auth(ctx=ctx)
        current = _get_sender_details(sender_details_id=sender_details_id, ctx=ctx, headers=headers)
        request = {"method": "DELETE", "path": f"/sender-details/v1/sender-details/{sender_details_id}", "body": None}
        selector = {"kind": "wix-sender-details", "operation": "delete", "sender_details_id": sender_details_id}
        before_state = {"senderDetails": current}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="sender-details.delete", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="sender-details.delete",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "delete", "senderDetailsId": sender_details_id}],
                verification_plan={"type": "read-after-write", "notes": "Verify the sender details returns 404 after delete."},
                requires_ack=True,
            )

        if not _should_apply(ctx, requires_ack=True):
            ctx["out"].emit({"ok": True, "dry_run": True, "method": "sender-details.delete", "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)})
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="sender-details.delete", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(plan=loaded_plan, current_state={"senderDetails": _get_sender_details(sender_details_id=sender_details_id, ctx=ctx, headers=headers)})
        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/sender-details/v1/sender-details/{sender_details_id}",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after, status = _get_sender_details_optional(sender_details_id=sender_details_id, ctx=ctx, headers=headers)
        verification = {"ok": after is None and status == 404, "type": "read-after-write", "path": f"/sender-details/v1/sender-details/{sender_details_id}", "method": "GET", "before": current, "after_status": status, "checks": [{"field": "status_code", "expected": 404, "actual": status}]}
        receipt = _build_receipt(method="sender-details.delete", selector=selector, request=request, response=response, verification=verification, plan=loaded_plan, ctx=ctx)
        ctx["out"].emit({"ok": bool(verification.get("ok")), "dry_run": False, "method": "sender-details.delete", "auth_mode": auth_mode, "receipt": receipt, "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt)})
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "sender-details.delete"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "sender-details.delete"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "sender-details.delete"})
        return 1


def cmd_sender_details_get_default(args, ctx) -> int:
    try:
        _ = args
        headers, auth_mode = _resolve_sender_details_auth(ctx=ctx)
        sender_details = _get_default_sender_details(ctx=ctx, headers=headers)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "sender-details.get-default",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": "/sender-details/v1/sender-details/default"},
                "response": {"senderDetails": sender_details},
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "sender-details.get-default"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "sender-details.get-default"})
        return 1


def cmd_sender_details_mark_default(args, ctx) -> int:
    try:
        sender_details_id = _coerce_non_empty_text(getattr(args, "sender_details_id", None), field="sender-details-id")
        headers, auth_mode = _resolve_sender_details_auth(ctx=ctx)
        current = _get_sender_details(sender_details_id=sender_details_id, ctx=ctx, headers=headers)
        request = {"method": "POST", "path": f"/sender-details/v1/sender-details/{sender_details_id}/mark-as-default", "body": None}
        selector = {"kind": "wix-sender-details", "operation": "mark-default", "sender_details_id": sender_details_id}
        before_state = {"senderDetails": current}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="sender-details.mark-default", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="sender-details.mark-default",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "mark-default", "senderDetailsId": sender_details_id}],
                verification_plan={"type": "read-after-write", "notes": "Verify the current default sender matches the target id after apply."},
            )

        if not _should_apply(ctx):
            ctx["out"].emit({"ok": True, "dry_run": True, "method": "sender-details.mark-default", "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)})
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="sender-details.mark-default", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(plan=loaded_plan, current_state={"senderDetails": _get_sender_details(sender_details_id=sender_details_id, ctx=ctx, headers=headers)})
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=f"/sender-details/v1/sender-details/{sender_details_id}/mark-as-default",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        default_after = _get_default_sender_details(ctx=ctx, headers=headers)
        verification = {"ok": default_after.get("id") == sender_details_id and bool(default_after.get("default")), "type": "read-after-write", "path": "/sender-details/v1/sender-details/default", "method": "GET", "before": current, "after": default_after, "checks": [{"field": "id", "expected": sender_details_id, "actual": default_after.get("id")}, {"field": "default", "expected": True, "actual": default_after.get("default")}]}
        receipt = _build_receipt(method="sender-details.mark-default", selector=selector, request=request, response=response, verification=verification, plan=loaded_plan, ctx=ctx)
        ctx["out"].emit({"ok": bool(verification.get("ok")), "dry_run": False, "method": "sender-details.mark-default", "auth_mode": auth_mode, "receipt": receipt, "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt)})
        return 0 if verification.get("ok") else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "sender-details.mark-default"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "sender-details.mark-default"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "sender-details.mark-default"})
        return 1
