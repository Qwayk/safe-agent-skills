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


def _normalize_label_payload(raw: Any, *, field: str) -> dict[str, Any]:
    payload = _read_json_arg(raw, field=field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not payload:
        raise ValidationError(f"--{field} cannot be empty")

    normalized = dict(payload)
    if normalized.get("displayName") is None and isinstance(normalized.get("name"), str):
        normalized["displayName"] = normalized["name"].strip()

    display_name = normalized.get("displayName")
    if not isinstance(display_name, str) or not display_name.strip():
        raise ValidationError(f"--{field} must include a non-empty displayName")
    normalized["displayName"] = display_name.strip()
    normalized.pop("name", None)
    return normalized


def _resolve_contact_labels_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="contact-labels",
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


def _extract_label(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    label = payload.get("label")
    if not isinstance(label, dict):
        raise ValidationError(f"{operation} response did not include a label object")
    return label


def _extract_label_key(label: dict[str, Any], *, operation: str) -> str:
    raw_key = label.get("key")
    if not isinstance(raw_key, str) or not raw_key.strip():
        raise ValidationError(f"{operation} response did not include a usable label key")
    return raw_key.strip()


def _get_label(
    *,
    key: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/contacts/v4/labels/{key}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_label(payload, operation="contact-labels.get")


def _get_label_optional(
    *,
    key: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> tuple[dict[str, Any] | None, int | None]:
    try:
        return _get_label(key=key, ctx=ctx, headers=headers), None
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            return None, 404
        raise


def _normalize_query_payload(query_json: dict[str, Any]) -> dict[str, Any]:
    if "query" in query_json and isinstance(query_json["query"], dict):
        return query_json
    return {"query": query_json}


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
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": ["wix-contact-label-write"] + (["irreversible"] if requires_ack else []),
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "apply requires --plan-in, --apply, and --yes",
        ],
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "before_state": before_state,
        },
        "state_capture": {"before_state_available": bool(before_state)},
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "rollback": {
            "supported": False,
            "notes": "No automatic rollback. Use the saved before-state snapshot as a manual reference.",
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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="contact-labels")


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: contact-label state changed since plan was created")


def _build_verification(
    *,
    path: str,
    requested: dict[str, Any],
    after: dict[str, Any],
    method: str,
    response_id_field: str,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for field, expected in requested.items():
        if field == response_id_field:
            continue
        checks.append({"field": field, "expected": expected, "actual": after.get(field)})
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
                "Receipt is linked to a reviewed plan snapshot."
                if before_state
                else "Receipt is linked to a reviewed plan with no usable before-state snapshot."
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


def cmd_contact_labels_query(args, ctx) -> int:
    try:
        query_json = _read_json_arg(getattr(args, "query_json", None), field="query-json")
        if not isinstance(query_json, dict):
            raise ValidationError("--query-json must be a JSON object")
        query_payload = _normalize_query_payload(query_json)

        headers, auth_mode = _resolve_contact_labels_auth(ctx=ctx)
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/contacts/v4/labels/query",
            headers=headers,
            params=None,
            json_body=query_payload,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "contact-labels.query",
            "auth_mode": auth_mode,
            "request": {
                "method": "POST",
                "path": "/contacts/v4/labels/query",
                "body": query_payload,
            },
            "response": payload,
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "contact-labels.query"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "contact-labels.query"})
        return 1


def cmd_contact_labels_list(args, ctx) -> int:
    try:
        _ = args  # kept for parity with parser-only args pattern
        headers, auth_mode = _resolve_contact_labels_auth(ctx=ctx)
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/contacts/v4/labels",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "contact-labels.list",
            "auth_mode": auth_mode,
            "request": {"method": "GET", "path": "/contacts/v4/labels"},
            "response": payload,
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "contact-labels.list"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "contact-labels.list"})
        return 1


def cmd_contact_labels_get(args, ctx) -> int:
    try:
        key = _coerce_non_empty_text(getattr(args, "key", None), field="key")
        headers, auth_mode = _resolve_contact_labels_auth(ctx=ctx)
        label = _get_label(key=key, ctx=ctx, headers=headers)
        out = {
            "ok": True,
            "method": "contact-labels.get",
            "auth_mode": auth_mode,
            "request": {"method": "GET", "path": f"/contacts/v4/labels/{key}"},
            "response": {"label": label},
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "contact-labels.get"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "contact-labels.get"})
        return 1


def cmd_contact_labels_find_or_create(args, ctx) -> int:
    try:
        label_payload = _normalize_label_payload(getattr(args, "label_json", None), field="label-json")
        key_requested = _coerce_non_empty_text(label_payload.get("displayName"), field="label-json.displayName")
        headers, auth_mode = _resolve_contact_labels_auth(ctx=ctx)

        request_body = {"label": label_payload}
        request = {"method": "POST", "path": "/contacts/v4/labels", "body": request_body}
        selector = {"kind": "wix-contact-label", "operation": "find-or-create", "display_name": key_requested}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="contact-labels.find-or-create", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="contact-labels.find-or-create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state={},
                proposed_changes=[{"operation": "find_or_create", "display_name": key_requested}],
                verification_plan={"type": "read-after-write", "notes": "Verify response label key and read-back label."},
            )

        if not _should_apply(ctx):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "contact-labels.find-or-create",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="contact-labels.find-or-create", expected_selector=selector, ctx=ctx)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/contacts/v4/labels",
            headers=headers,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        label = _extract_label(response, operation="contact-labels.find-or-create")
        label_key = _extract_label_key(label, operation="contact-labels.find-or-create")
        after_label = _get_label(key=label_key, ctx=ctx, headers=headers)
        verification = _build_verification(
            path=f"/contacts/v4/labels/{label_key}",
            requested={"displayName": label_payload.get("displayName")},
            after=after_label,
            method="contact-labels.find-or-create",
            response_id_field="key",
        )
        receipt = _build_receipt(
            method="contact-labels.find-or-create",
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
            "method": "contact-labels.find-or-create",
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
                "method": "contact-labels.find-or-create",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "contact-labels.find-or-create"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "contact-labels.find-or-create"})
        return 1


def cmd_contact_labels_update(args, ctx) -> int:
    try:
        key = _coerce_non_empty_text(getattr(args, "key", None), field="key")
        label_payload = _normalize_label_payload(getattr(args, "label_json", None), field="label-json")
        label_payload_key = label_payload.get("key")
        if label_payload_key is not None and str(label_payload_key).strip() != key:
            raise SafetyError("Refused: label key in body does not match --key")

        headers, auth_mode = _resolve_contact_labels_auth(ctx=ctx)
        current_label = _get_label(key=key, ctx=ctx, headers=headers)
        label_payload["key"] = key

        request_body = {"label": label_payload}
        request = {"method": "PATCH", "path": f"/contacts/v4/labels/{key}", "body": request_body}
        selector = {"kind": "wix-contact-label", "operation": "update", "key": key}
        before_state = {"label": current_label}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="contact-labels.update", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="contact-labels.update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "update", "key": key}],
                verification_plan={"type": "read-after-write", "notes": "Verify each requested label field after read-back."},
            )

        if not _should_apply(ctx):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "contact-labels.update",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="contact-labels.update", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(plan=loaded_plan, current_state={"label": _get_label(key=key, ctx=ctx, headers=headers)})
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/contacts/v4/labels/{key}",
            headers=headers,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_label = _get_label(key=key, ctx=ctx, headers=headers)
        checks = {field: value for field, value in label_payload.items() if field != "key"}
        verification = _build_verification(
            path=f"/contacts/v4/labels/{key}",
            requested=checks,
            after=after_label,
            method="contact-labels.update",
            response_id_field="key",
        )
        verification["before"] = current_label
        receipt = _build_receipt(
            method="contact-labels.update",
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
            "method": "contact-labels.update",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "contact-labels.update"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "contact-labels.update"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "contact-labels.update"})
        return 1


def cmd_contact_labels_delete(args, ctx) -> int:
    try:
        key = _coerce_non_empty_text(getattr(args, "key", None), field="key")
        headers, auth_mode = _resolve_contact_labels_auth(ctx=ctx)
        current_label = _get_label(key=key, ctx=ctx, headers=headers)
        request = {"method": "DELETE", "path": f"/contacts/v4/labels/{key}"}
        selector = {"kind": "wix-contact-label", "operation": "delete", "key": key}
        before_state = {"label": current_label}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="contact-labels.delete", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="contact-labels.delete",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "delete", "key": key, "display_name": current_label.get("displayName")}],
                verification_plan={
                    "type": "read-after-write",
                    "notes": (
                        "Verify delete by expecting GET to return 404. "
                        "Deleting a label removes it from all contacts and triggers label events."
                    ),
                },
                requires_ack=True,
            )

        if not _should_apply(ctx, requires_ack=True):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "contact-labels.delete",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="contact-labels.delete", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(plan=loaded_plan, current_state={"label": _get_label(key=key, ctx=ctx, headers=headers)})
        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/contacts/v4/labels/{key}",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_label, after_status = _get_label_optional(key=key, ctx=ctx, headers=headers)
        verification = {
            "ok": after_status == 404 and after_label is None,
            "type": "read-after-write",
            "path": f"/contacts/v4/labels/{key}",
            "method": "GET",
            "before": current_label,
            "after": after_label,
            "expected_http_status": 404,
            "actual_http_status": after_status,
            "checks": [{"field": "key", "expected": key, "actual": None}],
            "notes": "Delete verification expects label GET to return 404.",
        }
        receipt = _build_receipt(
            method="contact-labels.delete",
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
            "method": "contact-labels.delete",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "contact-labels.delete"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "contact-labels.delete"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "contact-labels.delete"})
        return 1
