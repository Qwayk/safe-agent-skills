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


def _coerce_sender_email_payload(raw: Any) -> dict[str, Any]:
    value = _read_json_arg(raw, field="sender-email-json")
    if not isinstance(value, dict) or not value:
        raise ValidationError("--sender-email-json must be a non-empty JSON object")
    payload = dict(value)
    sender_email = payload.get("senderEmail")
    if not isinstance(sender_email, dict) or not sender_email:
        raise ValidationError("--sender-email-json.senderEmail must be a non-empty JSON object")
    normalized_sender_email = dict(sender_email)
    normalized_sender_email["emailAddress"] = _coerce_non_empty_text(
        normalized_sender_email.get("emailAddress"),
        field="sender-email-json.senderEmail.emailAddress",
    )
    payload["senderEmail"] = normalized_sender_email
    return payload


def _coerce_verify_payload(code: Any) -> dict[str, Any]:
    verification_code = _coerce_non_empty_text(code, field="verification-code")
    if len(verification_code) < 3 or len(verification_code) > 10:
        raise ValidationError("--verification-code must be between 3 and 10 characters")
    return {"verificationCode": verification_code}


def _resolve_sender_emails_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="sender-emails",
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


def _extract_sender_email(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    sender_email = payload.get("senderEmail")
    if not isinstance(sender_email, dict):
        raise ValidationError(f"{operation} response did not include a senderEmail object")
    return sender_email


def _extract_sender_emails(payload: dict[str, Any], *, operation: str) -> list[dict[str, Any]]:
    sender_emails = payload.get("senderEmails")
    if not isinstance(sender_emails, list):
        raise ValidationError(f"{operation} response did not include a senderEmails array")
    return [item for item in sender_emails if isinstance(item, dict)]


def _find_sender_email_by_id(sender_emails: list[dict[str, Any]], sender_email_id: str) -> dict[str, Any] | None:
    for item in sender_emails:
        if isinstance(item.get("id"), str) and item.get("id") == sender_email_id:
            return item
    return None


def _find_sender_email_by_address(
    sender_emails: list[dict[str, Any]],
    email_address: str,
) -> dict[str, Any] | None:
    for item in sender_emails:
        if isinstance(item.get("emailAddress"), str) and item.get("emailAddress") == email_address:
            return item
    return None


def _list_sender_emails(
    *,
    email_address: str | None,
    limit: int | None,
    cursor: str | None,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {}
    if email_address:
        params["emailAddress"] = email_address
    if limit is not None:
        params["paging.limit"] = limit
    if cursor:
        params["paging.cursor"] = cursor
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path="/sender-emails/v1/sender-emails",
        headers=headers,
        params=params or None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_sender_emails(payload, operation="sender-emails.list")


def _get_sender_email(
    *,
    sender_email_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/sender-emails/v1/sender-emails/{sender_email_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_sender_email(payload, operation="sender-emails.get")


def _get_sender_email_optional(
    *,
    sender_email_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> tuple[dict[str, Any] | None, int | None]:
    try:
        return _get_sender_email(sender_email_id=sender_email_id, ctx=ctx, headers=headers), None
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
        "risk_reasons": ["sender-email-write"] + (["irreversible"] if requires_ack else []),
        "provider_notes": [
            "Sender emails must be verified before they can be used in sender details.",
            "Wix docs say the same scope is used for sender-email reads and writes: Access Verticals by Automations.",
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
                "Captured current sender email state before planning."
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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="sender-emails")


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: sender email state changed since plan was created")


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
            "notes": "Receipt stores sender email metadata only.",
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": "Recovery is manual only.",
        },
    }


def cmd_sender_emails_list(args, ctx) -> int:
    try:
        headers, auth_mode = _resolve_sender_emails_auth(ctx=ctx)
        email_address = _coerce_optional_non_empty_text(getattr(args, "email_address", None), field="email-address")
        limit = _coerce_paging_limit(getattr(args, "limit", None))
        cursor = _coerce_optional_non_empty_text(getattr(args, "cursor", None), field="cursor")
        sender_emails = _list_sender_emails(
            email_address=email_address,
            limit=limit,
            cursor=cursor,
            ctx=ctx,
            headers=headers,
        )
        params: dict[str, Any] = {}
        if email_address:
            params["emailAddress"] = email_address
        if limit is not None:
            params["paging.limit"] = limit
        if cursor:
            params["paging.cursor"] = cursor
        ctx["out"].emit(
            {
                "ok": True,
                "method": "sender-emails.list",
                "auth_mode": auth_mode,
                "request": {
                    "method": "GET",
                    "path": "/sender-emails/v1/sender-emails",
                    "params": params,
                },
                "response": {"senderEmails": sender_emails},
                "notes": [
                    "Sender email reads use Access Verticals by Automations in the official docs.",
                    "Use the verified flag before trying to create sender details from an email address.",
                ],
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "sender-emails.list"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "sender-emails.list"}
        )
        return 1


def cmd_sender_emails_get(args, ctx) -> int:
    try:
        sender_email_id = _coerce_non_empty_text(getattr(args, "sender_email_id", None), field="sender-email-id")
        headers, auth_mode = _resolve_sender_emails_auth(ctx=ctx)
        sender_email = _get_sender_email(sender_email_id=sender_email_id, ctx=ctx, headers=headers)
        ctx["out"].emit(
            {
                "ok": True,
                "method": "sender-emails.get",
                "auth_mode": auth_mode,
                "request": {
                    "method": "GET",
                    "path": f"/sender-emails/v1/sender-emails/{sender_email_id}",
                },
                "response": {"senderEmail": sender_email},
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "sender-emails.get"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "sender-emails.get"}
        )
        return 1


def cmd_sender_emails_create(args, ctx) -> int:
    try:
        payload = _coerce_sender_email_payload(getattr(args, "sender_email_json", None))
        email_address = payload["senderEmail"]["emailAddress"]
        headers, auth_mode = _resolve_sender_emails_auth(ctx=ctx)
        current_sender_emails = _list_sender_emails(
            email_address=email_address,
            limit=None,
            cursor=None,
            ctx=ctx,
            headers=headers,
        )
        if _find_sender_email_by_address(current_sender_emails, email_address) is not None:
            raise SafetyError("Refused: a sender email with this email address already exists")

        request = {
            "method": "POST",
            "path": "/sender-emails/v1/sender-emails",
            "body": payload,
        }
        selector = {"kind": "wix-sender-email", "operation": "create", "email_address": email_address}
        before_state = {"senderEmails": current_sender_emails}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="sender-emails.create",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="sender-emails.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "create", "emailAddress": email_address}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify the created sender email exists by id and emailAddress.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "sender-emails.create",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="sender-emails.create",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={
                "senderEmails": _list_sender_emails(
                    email_address=email_address,
                    limit=None,
                    cursor=None,
                    ctx=ctx,
                    headers=headers,
                )
            },
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/sender-emails/v1/sender-emails",
            headers=headers,
            params=None,
            json_body=payload,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_sender_email = _extract_sender_email(response, operation="sender-emails.create")
        created_id = _coerce_non_empty_text(created_sender_email.get("id"), field="response.senderEmail.id")
        after_sender_email = _get_sender_email(sender_email_id=created_id, ctx=ctx, headers=headers)
        verification = {
            "ok": after_sender_email.get("id") == created_id and after_sender_email.get("emailAddress") == email_address,
            "type": "read-after-write",
            "path": f"/sender-emails/v1/sender-emails/{created_id}",
            "method": "GET",
            "after": after_sender_email,
            "checks": [
                {"field": "id", "expected": created_id, "actual": after_sender_email.get("id")},
                {"field": "emailAddress", "expected": email_address, "actual": after_sender_email.get("emailAddress")},
            ],
        }
        receipt = _build_receipt(
            method="sender-emails.create",
            selector=selector,
            request=request,
            response={"senderEmail": created_sender_email},
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "sender-emails.create",
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
                "method": "sender-emails.create",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "sender-emails.create"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "sender-emails.create"}
        )
        return 1


def cmd_sender_emails_delete(args, ctx) -> int:
    try:
        sender_email_id = _coerce_non_empty_text(getattr(args, "sender_email_id", None), field="sender-email-id")
        headers, auth_mode = _resolve_sender_emails_auth(ctx=ctx)
        current_sender_email = _get_sender_email(sender_email_id=sender_email_id, ctx=ctx, headers=headers)
        request = {
            "method": "DELETE",
            "path": f"/sender-emails/v1/sender-emails/{sender_email_id}",
            "body": None,
        }
        selector = {"kind": "wix-sender-email", "operation": "delete", "sender_email_id": sender_email_id}
        before_state = {"senderEmail": current_sender_email}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="sender-emails.delete",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="sender-emails.delete",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "delete", "senderEmailId": sender_email_id}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify the sender email returns 404 after delete.",
                },
                requires_ack=True,
            )

        if not _should_apply(ctx, requires_ack=True):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "sender-emails.delete",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="sender-emails.delete",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={"senderEmail": _get_sender_email(sender_email_id=sender_email_id, ctx=ctx, headers=headers)},
        )
        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/sender-emails/v1/sender-emails/{sender_email_id}",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_sender_email, status = _get_sender_email_optional(sender_email_id=sender_email_id, ctx=ctx, headers=headers)
        verification = {
            "ok": after_sender_email is None and status == 404,
            "type": "read-after-write",
            "path": f"/sender-emails/v1/sender-emails/{sender_email_id}",
            "method": "GET",
            "before": current_sender_email,
            "after_status": status,
            "checks": [{"field": "status_code", "expected": 404, "actual": status}],
        }
        receipt = _build_receipt(
            method="sender-emails.delete",
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
                "method": "sender-emails.delete",
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
                "method": "sender-emails.delete",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "sender-emails.delete"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "sender-emails.delete"}
        )
        return 1


def cmd_sender_emails_get_or_create(args, ctx) -> int:
    try:
        email_address = _coerce_non_empty_text(getattr(args, "email_address", None), field="email-address")
        headers, auth_mode = _resolve_sender_emails_auth(ctx=ctx)
        current_sender_emails = _list_sender_emails(
            email_address=email_address,
            limit=None,
            cursor=None,
            ctx=ctx,
            headers=headers,
        )
        existing_sender_email = _find_sender_email_by_address(current_sender_emails, email_address)
        request = {
            "method": "POST",
            "path": "/sender-emails/v1/sender-emails/get-or-create",
            "body": {"emailAddress": email_address},
        }
        selector = {"kind": "wix-sender-email", "operation": "get-or-create", "email_address": email_address}
        before_state = {"senderEmail": existing_sender_email} if existing_sender_email else {}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="sender-emails.get-or-create",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            proposed_changes = [{"operation": "get-or-create", "emailAddress": email_address}]
            if existing_sender_email is not None:
                proposed_changes.append({"note": "Existing sender email already found. Live apply should be idempotent."})
            plan = _build_plan(
                method="sender-emails.get-or-create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=proposed_changes,
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify the sender email exists after apply by id and emailAddress.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "sender-emails.get-or-create",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="sender-emails.get-or-create",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={
                "senderEmail": _find_sender_email_by_address(
                    _list_sender_emails(
                        email_address=email_address,
                        limit=None,
                        cursor=None,
                        ctx=ctx,
                        headers=headers,
                    ),
                    email_address,
                )
            }
            if existing_sender_email is not None
            else {},
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/sender-emails/v1/sender-emails/get-or-create",
            headers=headers,
            params=None,
            json_body={"emailAddress": email_address},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        sender_email = _extract_sender_email(response, operation="sender-emails.get-or-create")
        sender_email_id = _coerce_non_empty_text(sender_email.get("id"), field="response.senderEmail.id")
        after_sender_email = _get_sender_email(sender_email_id=sender_email_id, ctx=ctx, headers=headers)
        verification = {
            "ok": after_sender_email.get("emailAddress") == email_address,
            "type": "read-after-write",
            "path": f"/sender-emails/v1/sender-emails/{sender_email_id}",
            "method": "GET",
            "before": existing_sender_email,
            "after": after_sender_email,
            "checks": [
                {"field": "emailAddress", "expected": email_address, "actual": after_sender_email.get("emailAddress")}
            ],
        }
        receipt = _build_receipt(
            method="sender-emails.get-or-create",
            selector=selector,
            request=request,
            response={"senderEmail": sender_email},
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "sender-emails.get-or-create",
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
                "method": "sender-emails.get-or-create",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "sender-emails.get-or-create"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "sender-emails.get-or-create"}
        )
        return 1


def cmd_sender_emails_send_verification_code(args, ctx) -> int:
    try:
        sender_email_id = _coerce_non_empty_text(getattr(args, "sender_email_id", None), field="sender-email-id")
        headers, auth_mode = _resolve_sender_emails_auth(ctx=ctx)
        current_sender_email = _get_sender_email(sender_email_id=sender_email_id, ctx=ctx, headers=headers)
        request = {
            "method": "POST",
            "path": f"/sender-emails/v1/sender-emails/{sender_email_id}/send-verification-code",
            "body": None,
        }
        selector = {
            "kind": "wix-sender-email",
            "operation": "send-verification-code",
            "sender_email_id": sender_email_id,
        }
        before_state = {"senderEmail": current_sender_email}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="sender-emails.send-verification-code",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="sender-emails.send-verification-code",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "send-verification-code", "senderEmailId": sender_email_id}],
                verification_plan={
                    "type": "provider-response",
                    "notes": "The API returns an empty object. Delivery to the inbox is outside this CLI.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "sender-emails.send-verification-code",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="sender-emails.send-verification-code",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={"senderEmail": _get_sender_email(sender_email_id=sender_email_id, ctx=ctx, headers=headers)},
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=f"/sender-emails/v1/sender-emails/{sender_email_id}/send-verification-code",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = {
            "ok": True,
            "type": "provider-response",
            "before": current_sender_email,
            "notes": "Wix confirms only the request acceptance here. The inbox delivery itself is out of band.",
        }
        receipt = _build_receipt(
            method="sender-emails.send-verification-code",
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
                "method": "sender-emails.send-verification-code",
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
                "method": "sender-emails.send-verification-code",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "sender-emails.send-verification-code",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "sender-emails.send-verification-code",
            }
        )
        return 1


def cmd_sender_emails_verify(args, ctx) -> int:
    try:
        sender_email_id = _coerce_non_empty_text(getattr(args, "sender_email_id", None), field="sender-email-id")
        payload = _coerce_verify_payload(getattr(args, "verification_code", None))
        headers, auth_mode = _resolve_sender_emails_auth(ctx=ctx)
        current_sender_email = _get_sender_email(sender_email_id=sender_email_id, ctx=ctx, headers=headers)
        request = {
            "method": "POST",
            "path": f"/sender-emails/v1/sender-emails/{sender_email_id}/verify",
            "body": payload,
        }
        selector = {"kind": "wix-sender-email", "operation": "verify", "sender_email_id": sender_email_id}
        before_state = {"senderEmail": current_sender_email}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="sender-emails.verify",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="sender-emails.verify",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "verify", "senderEmailId": sender_email_id}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": "Verify the sender email comes back with verified=true after apply.",
                },
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "sender-emails.verify",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="sender-emails.verify",
            expected_selector=selector,
            ctx=ctx,
        )
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={"senderEmail": _get_sender_email(sender_email_id=sender_email_id, ctx=ctx, headers=headers)},
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=f"/sender-emails/v1/sender-emails/{sender_email_id}/verify",
            headers=headers,
            params=None,
            json_body=payload,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_sender_email = _get_sender_email(sender_email_id=sender_email_id, ctx=ctx, headers=headers)
        verification = {
            "ok": bool(after_sender_email.get("verified")),
            "type": "read-after-write",
            "path": f"/sender-emails/v1/sender-emails/{sender_email_id}",
            "method": "GET",
            "before": current_sender_email,
            "after": after_sender_email,
            "checks": [{"field": "verified", "expected": True, "actual": after_sender_email.get("verified")}],
        }
        receipt = _build_receipt(
            method="sender-emails.verify",
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
                "method": "sender-emails.verify",
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
                "method": "sender-emails.verify",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "sender-emails.verify"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "sender-emails.verify"}
        )
        return 1
