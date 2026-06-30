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


def _coerce_tag_payload(raw: Any, *, field: str) -> dict[str, Any]:
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _resolve_tags_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="tags",
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


def _extract_tag(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    tag = payload.get("tag")
    if not isinstance(tag, dict):
        raise ValidationError(f"{operation} response did not include a tag object")
    return tag


def _extract_tag_id(tag: dict[str, Any], *, operation: str) -> str:
    raw_id = tag.get("id")
    if not isinstance(raw_id, str) or not raw_id.strip():
        raise ValidationError(f"{operation} response did not include a usable tag id")
    return raw_id.strip()


def _get_tag(
    *,
    tag_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path=f"/tags/v1/tags/{tag_id}",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_tag(payload, operation="tags.get")


def _get_tag_optional(
    *,
    tag_id: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> tuple[dict[str, Any] | None, int | None]:
    try:
        return _get_tag(tag_id=tag_id, ctx=ctx, headers=headers), None
    except RuntimeError as exc:
        status = _http_status_from_error(exc)
        if status == 404:
            return None, 404
        raise


def _list_tags_for_fqdn(
    *,
    fqdn: str,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> list[dict[str, Any]]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path="/tags/v1/tags",
        headers=headers,
        params={"fqdn": fqdn},
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    tags = payload.get("tags")
    if not isinstance(tags, list):
        raise ValidationError("tags.list response did not include a tags array")
    normalized: list[dict[str, Any]] = []
    for item in tags:
        if isinstance(item, dict):
            normalized.append(item)
    return normalized


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
        "risk_reasons": ["wix-tag-write"] + (["irreversible"] if requires_ack else []),
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
                "Captured current provider state before planning."
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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="tags")


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: tag state changed since plan was created")


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


def cmd_tags_list(args, ctx) -> int:
    try:
        fqdn = _coerce_non_empty_text(getattr(args, "fqdn", None), field="fqdn")
        headers, auth_mode = _resolve_tags_auth(ctx=ctx)
        tags = _list_tags_for_fqdn(fqdn=fqdn, ctx=ctx, headers=headers)
        out = {
            "ok": True,
            "method": "tags.list",
            "auth_mode": auth_mode,
            "request": {"method": "GET", "path": "/tags/v1/tags", "params": {"fqdn": fqdn}},
            "response": {"tags": tags},
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "tags.list"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "tags.list"})
        return 1


def cmd_tags_get(args, ctx) -> int:
    try:
        tag_id = _coerce_non_empty_text(getattr(args, "tag_id", None), field="tag-id")
        headers, auth_mode = _resolve_tags_auth(ctx=ctx)
        tag = _get_tag(tag_id=tag_id, ctx=ctx, headers=headers)
        out = {
            "ok": True,
            "method": "tags.get",
            "auth_mode": auth_mode,
            "request": {"method": "GET", "path": f"/tags/v1/tags/{tag_id}"},
            "response": {"tag": tag},
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "tags.get"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "tags.get"})
        return 1


def cmd_tags_create(args, ctx) -> int:
    try:
        tag_payload = _coerce_tag_payload(getattr(args, "tag_json", None), field="tag-json")
        fqdn = _coerce_non_empty_text(tag_payload.get("fqdn"), field="tag-json.fqdn")
        name = _coerce_non_empty_text(tag_payload.get("name"), field="tag-json.name")
        headers, auth_mode = _resolve_tags_auth(ctx=ctx)
        existing_tags = _list_tags_for_fqdn(fqdn=fqdn, ctx=ctx, headers=headers)
        if len(existing_tags) >= 100:
            raise SafetyError(f"Refused: Wix docs say each FQDN can have at most 100 tags: {fqdn}")
        for item in existing_tags:
            if str(item.get("name") or "").strip() == name:
                raise SafetyError(f"Refused: tag already exists for fqdn {fqdn}: {name}")

        request = {"method": "POST", "path": "/tags/v1/tags", "body": {"tag": {"fqdn": fqdn, "name": name}}}
        selector = {"kind": "wix-tag", "operation": "create", "fqdn": fqdn, "name": name}
        before_state = {"fqdn": fqdn, "tags": existing_tags}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="tags.create", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="tags.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "create", "tag": {"fqdn": fqdn, "name": name}}],
                verification_plan={"type": "read-after-write", "notes": "Verify create response id and read back the new tag."},
            )

        if not _should_apply(ctx):
            out = {"ok": True, "dry_run": True, "method": "tags.create", "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)}
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="tags.create", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(plan=loaded_plan, current_state={"fqdn": fqdn, "tags": _list_tags_for_fqdn(fqdn=fqdn, ctx=ctx, headers=headers)})
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/tags/v1/tags",
            headers=headers,
            params=None,
            json_body={"tag": {"fqdn": fqdn, "name": name}},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_tag = _extract_tag(response, operation="tags.create")
        created_id = _extract_tag_id(created_tag, operation="tags.create")
        after_tag = _get_tag(tag_id=created_id, ctx=ctx, headers=headers)
        verification = {
            "ok": after_tag.get("id") == created_id and after_tag.get("name") == name and after_tag.get("fqdn") == fqdn,
            "type": "read-after-write",
            "path": f"/tags/v1/tags/{created_id}",
            "method": "GET",
            "checks": [
                {"field": "id", "expected": created_id, "actual": after_tag.get("id")},
                {"field": "name", "expected": name, "actual": after_tag.get("name")},
                {"field": "fqdn", "expected": fqdn, "actual": after_tag.get("fqdn")},
            ],
            "after": after_tag,
            "notes": "Create verification uses response id plus read-back get tag.",
        }
        receipt = _build_receipt(
            method="tags.create",
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
            "method": "tags.create",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "tags.create"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "tags.create"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "tags.create"})
        return 1


def cmd_tags_update(args, ctx) -> int:
    try:
        tag_id = _coerce_non_empty_text(getattr(args, "tag_id", None), field="tag-id")
        tag_payload = _coerce_tag_payload(getattr(args, "tag_json", None), field="tag-json")
        revision = _coerce_non_empty_text(tag_payload.get("revision"), field="tag-json.revision")
        name = _coerce_non_empty_text(tag_payload.get("name"), field="tag-json.name")
        headers, auth_mode = _resolve_tags_auth(ctx=ctx)
        current_tag = _get_tag(tag_id=tag_id, ctx=ctx, headers=headers)
        fqdn = str(current_tag.get("fqdn") or "").strip()
        if not fqdn:
            raise ValidationError("Current tag readback did not include fqdn")
        payload_fqdn = tag_payload.get("fqdn")
        if payload_fqdn is not None and str(payload_fqdn).strip() != fqdn:
            raise SafetyError("Refused: tag fqdn is immutable and does not match the current tag")

        request_body = {"tag": {"id": tag_id, "revision": revision, "name": name, "fqdn": fqdn}}
        request = {"method": "PATCH", "path": f"/tags/v1/tags/{tag_id}", "body": request_body}
        selector = {"kind": "wix-tag", "operation": "update", "tag_id": tag_id}
        before_state = {"tag": current_tag}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="tags.update", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="tags.update",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "update", "tag_id": tag_id, "name": name, "revision": revision}],
                verification_plan={"type": "read-after-write", "notes": "Verify updated name and revision by re-reading the tag."},
            )

        if not _should_apply(ctx):
            out = {"ok": True, "dry_run": True, "method": "tags.update", "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)}
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="tags.update", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(plan=loaded_plan, current_state={"tag": _get_tag(tag_id=tag_id, ctx=ctx, headers=headers)})
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/tags/v1/tags/{tag_id}",
            headers=headers,
            params=None,
            json_body=request_body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_tag = _get_tag(tag_id=tag_id, ctx=ctx, headers=headers)
        verification = {
            "ok": after_tag.get("name") == name,
            "type": "read-after-write",
            "path": f"/tags/v1/tags/{tag_id}",
            "method": "GET",
            "before": current_tag,
            "after": after_tag,
            "checks": [{"field": "name", "expected": name, "actual": after_tag.get("name")}],
            "notes": "Update verification uses read-back get tag.",
        }
        receipt = _build_receipt(
            method="tags.update",
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
            "method": "tags.update",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "tags.update"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "tags.update"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "tags.update"})
        return 1


def cmd_tags_delete(args, ctx) -> int:
    try:
        tag_id = _coerce_non_empty_text(getattr(args, "tag_id", None), field="tag-id")
        headers, auth_mode = _resolve_tags_auth(ctx=ctx)
        current_tag = _get_tag(tag_id=tag_id, ctx=ctx, headers=headers)
        request = {"method": "DELETE", "path": f"/tags/v1/tags/{tag_id}"}
        selector = {"kind": "wix-tag", "operation": "delete", "tag_id": tag_id}
        before_state = {"tag": current_tag}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="tags.delete", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="tags.delete",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "delete", "tag_id": tag_id, "name": current_tag.get("name"), "fqdn": current_tag.get("fqdn")}],
                verification_plan={"type": "read-after-write", "notes": "Verify delete by expecting get tag to return 404."},
                requires_ack=True,
            )

        if not _should_apply(ctx, requires_ack=True):
            out = {"ok": True, "dry_run": True, "method": "tags.delete", "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)}
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="tags.delete", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(plan=loaded_plan, current_state={"tag": _get_tag(tag_id=tag_id, ctx=ctx, headers=headers)})
        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/tags/v1/tags/{tag_id}",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_tag, after_status = _get_tag_optional(tag_id=tag_id, ctx=ctx, headers=headers)
        verification = {
            "ok": after_status == 404 and after_tag is None,
            "type": "read-after-write",
            "path": f"/tags/v1/tags/{tag_id}",
            "method": "GET",
            "before": current_tag,
            "after": after_tag,
            "expected_http_status": 404,
            "actual_http_status": after_status,
            "notes": "Delete verification expects get tag to return 404.",
        }
        receipt = _build_receipt(
            method="tags.delete",
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
            "method": "tags.delete",
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
        ctx["out"].emit(out)
        return 0 if out["ok"] else 1
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "tags.delete"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "tags.delete"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "tags.delete"})
        return 1
