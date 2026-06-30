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


def _coerce_secret_payload(raw: Any, *, field: str, for_patch: bool) -> dict[str, Any]:
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, dict) or not value:
        raise ValidationError(f"--{field} must be a non-empty JSON object")

    payload = dict(value)
    if for_patch:
        allowed = {"name", "description", "value"}
        unknown = sorted(set(payload) - allowed)
        if unknown:
            raise ValidationError(f"--{field} contains unsupported field(s): {', '.join(unknown)}")
        if "name" in payload:
            payload["name"] = _coerce_non_empty_text(payload.get("name"), field=f"{field}.name")
        if "description" in payload and payload.get("description") is not None:
            payload["description"] = _coerce_non_empty_text(
                payload.get("description"), field=f"{field}.description"
            )
        if "value" in payload:
            payload["value"] = _coerce_non_empty_text(payload.get("value"), field=f"{field}.value")
        if not any(key in payload for key in ("name", "description", "value")):
            raise ValidationError(f"--{field} must include at least one of name, description, or value")
        return payload

    payload["name"] = _coerce_non_empty_text(payload.get("name"), field=f"{field}.name")
    payload["value"] = _coerce_non_empty_text(payload.get("value"), field=f"{field}.value")
    if "description" in payload and payload.get("description") is not None:
        payload["description"] = _coerce_non_empty_text(payload.get("description"), field=f"{field}.description")
    return payload


def _redact_secret_payload(payload: dict[str, Any]) -> dict[str, Any]:
    sanitized = dict(payload)
    if "value" in sanitized:
        sanitized["value"] = "[redacted]"
    return sanitized


def _redact_secret_info(secret: dict[str, Any]) -> dict[str, Any]:
    sanitized = dict(secret)
    if "value" in sanitized:
        sanitized["value"] = "[redacted]"
    return sanitized


def _resolve_secrets_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="secrets",
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


def _extract_secrets(payload: dict[str, Any], *, operation: str) -> list[dict[str, Any]]:
    secrets = payload.get("secrets")
    if not isinstance(secrets, list):
        raise ValidationError(f"{operation} response did not include a secrets array")
    return [item for item in secrets if isinstance(item, dict)]


def _find_secret_by_name(secrets: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    for item in secrets:
        if isinstance(item.get("name"), str) and item.get("name") == name:
            return item
    return None


def _find_secret_by_id(secrets: list[dict[str, Any]], secret_id: str) -> dict[str, Any] | None:
    for item in secrets:
        if isinstance(item.get("id"), str) and item.get("id") == secret_id:
            return item
    return None


def _list_secret_info(*, ctx: dict[str, Any], headers: dict[str, str]) -> list[dict[str, Any]]:
    payload = _request_json(
        method="GET",
        base_url=ctx["cfg"].base_url,
        path="/_api/cloud-secrets-vault-server/api/v1/secrets",
        headers=headers,
        params=None,
        json_body=None,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    return _extract_secrets(payload, operation="secrets.list")


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
        "risk_reasons": ["secret-write"] + (["breaks-code-using-secret"] if "value" in json.dumps(request) or "name" in json.dumps(request) else []) + (["irreversible"] if requires_ack else []),
        "provider_notes": [
            "Wix docs say create or manage secrets requires the Wix Members Area app installed on the site.",
            "Never expose secret values in frontend code or anonymous web methods.",
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
            "before_state_available": has_before_state,
            "notes": "Captured secret metadata only. Secret values are never stored in plans or receipts.",
        },
        "proposed_changes": proposed_changes,
        "verification_plan": verification_plan,
        "rollback": {
            "supported": False,
            "notes": "No automatic rollback. Delete is irreversible, and create or patch never stores secret values for rollback.",
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
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="secrets")


def _assert_no_state_drift(*, plan: dict[str, Any], current_state: dict[str, Any]) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if baseline.get("before_state") != current_state:
        raise SafetyError("Refused: secret metadata changed since plan was created")


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
            "notes": "Receipt stores secret metadata only. Secret values are never saved in receipts.",
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": "Recovery is manual only. Delete is irreversible, and this tool never stores secret values in receipts.",
        },
    }


def cmd_secrets_list(args, ctx) -> int:
    try:
        headers, auth_mode = _resolve_secrets_auth(ctx=ctx)
        secrets = [_redact_secret_info(item) for item in _list_secret_info(ctx=ctx, headers=headers)]
        ctx["out"].emit(
            {
                "ok": True,
                "method": "secrets.list",
                "auth_mode": auth_mode,
                "request": {"method": "GET", "path": "/_api/cloud-secrets-vault-server/api/v1/secrets"},
                "response": {"secrets": secrets},
                "notes": [
                    "Secret values are never returned by this list method.",
                    "Wix docs say create or manage secrets requires the Wix Members Area app installed on the site.",
                ],
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "secrets.list"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "secrets.list"})
        return 1


def cmd_secrets_get_value(args, ctx) -> int:
    try:
        name = _coerce_non_empty_text(getattr(args, "name", None), field="name")
        headers, auth_mode = _resolve_secrets_auth(ctx=ctx)
        response = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=f"/_api/cloud-secrets-vault-server/api/v1/secrets/name/{name}",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        value = _coerce_non_empty_text(response.get("value"), field="response.value")
        ctx["out"].emit(
            {
                "ok": True,
                "method": "secrets.get-value",
                "auth_mode": auth_mode,
                "request": {
                    "method": "GET",
                    "path": f"/_api/cloud-secrets-vault-server/api/v1/secrets/name/{name}",
                },
                "response": {"value": value},
                "notes": [
                    "Use secret values only in backend code.",
                    "Wix docs say the Members Area app is not required for this get-value method.",
                ],
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "secrets.get-value"}
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "secrets.get-value"})
        return 1


def cmd_secrets_create(args, ctx) -> int:
    try:
        payload = _coerce_secret_payload(getattr(args, "secret_json", None), field="secret-json", for_patch=False)
        headers, auth_mode = _resolve_secrets_auth(ctx=ctx)
        current_secrets = _list_secret_info(ctx=ctx, headers=headers)
        if _find_secret_by_name(current_secrets, payload["name"]) is not None:
            raise SafetyError("Refused: a secret with this name already exists")

        sanitized_request = {"secret": _redact_secret_payload(payload)}
        request = {
            "method": "POST",
            "path": "/_api/cloud-secrets-vault-server/api/v1/secrets",
            "body": sanitized_request,
        }
        selector = {"kind": "wix-secret", "operation": "create", "name": payload["name"]}
        before_state = {"secrets": [_redact_secret_info(item) for item in current_secrets]}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="secrets.create", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="secrets.create",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "create", "name": payload["name"], "description": payload.get("description")}],
                verification_plan={"type": "read-after-write", "notes": "Verify the created secret exists in secret metadata list by id and name."},
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "secrets.create",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="secrets.create", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={"secrets": [_redact_secret_info(item) for item in _list_secret_info(ctx=ctx, headers=headers)]},
        )
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/_api/cloud-secrets-vault-server/api/v1/secrets",
            headers=headers,
            params=None,
            json_body={"secret": payload},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        created_id = _coerce_non_empty_text(response.get("id"), field="response.id")
        after_secrets = _list_secret_info(ctx=ctx, headers=headers)
        created_secret = _find_secret_by_id(after_secrets, created_id)
        if created_secret is None:
            raise ValidationError("Create verification could not find the created secret in secret metadata list")
        checks = [
            {"field": "id", "expected": created_id, "actual": created_secret.get("id")},
            {"field": "name", "expected": payload["name"], "actual": created_secret.get("name")},
        ]
        if "description" in payload:
            checks.append(
                {"field": "description", "expected": payload.get("description"), "actual": created_secret.get("description")}
            )
        verification = {
            "ok": all(check["expected"] == check["actual"] for check in checks),
            "type": "read-after-write",
            "path": "/_api/cloud-secrets-vault-server/api/v1/secrets",
            "method": "GET",
            "checks": checks,
            "after": _redact_secret_info(created_secret),
            "notes": "Secret create verification uses metadata readback only. Secret values are never stored in receipts.",
        }
        receipt = _build_receipt(
            method="secrets.create",
            selector=selector,
            request=request,
            response={"id": created_id},
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "secrets.create",
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
                "method": "secrets.create",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "secrets.create"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "secrets.create"})
        return 1


def cmd_secrets_patch(args, ctx) -> int:
    try:
        secret_id = _coerce_non_empty_text(getattr(args, "secret_id", None), field="secret-id")
        payload = _coerce_secret_payload(getattr(args, "secret_json", None), field="secret-json", for_patch=True)
        headers, auth_mode = _resolve_secrets_auth(ctx=ctx)
        current_secrets = _list_secret_info(ctx=ctx, headers=headers)
        current_secret = _find_secret_by_id(current_secrets, secret_id)
        if current_secret is None:
            raise SafetyError("Refused: current secret metadata was not found")
        if "name" in payload:
            existing_with_name = _find_secret_by_name(current_secrets, payload["name"])
            if existing_with_name is not None and existing_with_name.get("id") != secret_id:
                raise SafetyError("Refused: another secret already uses this name")

        sanitized_request = {"secret": _redact_secret_payload(payload)}
        request = {
            "method": "PATCH",
            "path": f"/_api/cloud-secrets-vault-server/api/v1/secrets/{secret_id}",
            "body": sanitized_request,
        }
        selector = {"kind": "wix-secret", "operation": "patch", "secret_id": secret_id}
        before_state = {"secret": _redact_secret_info(current_secret)}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="secrets.patch", expected_selector=selector, ctx=ctx)
        else:
            proposed_changes = [{"operation": "patch", "secret_id": secret_id, "fields": sorted(payload.keys())}]
            if "name" in payload or "value" in payload:
                proposed_changes.append(
                    {
                        "note": "Wix docs say changing a secret name or value breaks code using that secret.",
                    }
                )
            plan = _build_plan(
                method="secrets.patch",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=proposed_changes,
                verification_plan={"type": "read-after-write", "notes": "Verify patched secret metadata by id after apply."},
            )

        if not _should_apply(ctx):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "secrets.patch",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="secrets.patch", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={"secret": _redact_secret_info(_find_secret_by_id(_list_secret_info(ctx=ctx, headers=headers), secret_id) or {})},
        )
        response = _request_json(
            method="PATCH",
            base_url=ctx["cfg"].base_url,
            path=f"/_api/cloud-secrets-vault-server/api/v1/secrets/{secret_id}",
            headers=headers,
            params=None,
            json_body={"secret": payload},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_secret = _find_secret_by_id(_list_secret_info(ctx=ctx, headers=headers), secret_id)
        if after_secret is None:
            raise ValidationError("Patch verification could not find the secret metadata after apply")
        checks = [{"field": "id", "expected": secret_id, "actual": after_secret.get("id")}]
        for field in ("name", "description"):
            if field in payload:
                checks.append({"field": field, "expected": payload.get(field), "actual": after_secret.get(field)})
        verification = {
            "ok": all(check["expected"] == check["actual"] for check in checks),
            "type": "read-after-write",
            "path": "/_api/cloud-secrets-vault-server/api/v1/secrets",
            "method": "GET",
            "before": _redact_secret_info(current_secret),
            "after": _redact_secret_info(after_secret),
            "checks": checks,
            "notes": "Secret patch verification uses metadata readback only. Secret values are never stored in receipts.",
        }
        receipt = _build_receipt(
            method="secrets.patch",
            selector=selector,
            request=request,
            response=_redact_secret_info(response),
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "secrets.patch",
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
                "method": "secrets.patch",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "secrets.patch"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "secrets.patch"})
        return 1


def cmd_secrets_delete(args, ctx) -> int:
    try:
        secret_id = _coerce_non_empty_text(getattr(args, "secret_id", None), field="secret-id")
        headers, auth_mode = _resolve_secrets_auth(ctx=ctx)
        current_secrets = _list_secret_info(ctx=ctx, headers=headers)
        current_secret = _find_secret_by_id(current_secrets, secret_id)
        if current_secret is None:
            raise SafetyError("Refused: current secret metadata was not found")

        request = {
            "method": "DELETE",
            "path": f"/_api/cloud-secrets-vault-server/api/v1/secrets/{secret_id}",
        }
        selector = {"kind": "wix-secret", "operation": "delete", "secret_id": secret_id}
        before_state = {"secret": _redact_secret_info(current_secret)}
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="secrets.delete", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="secrets.delete",
                request=request,
                selector=selector,
                ctx=ctx,
                before_state=before_state,
                proposed_changes=[{"operation": "delete", "secret_id": secret_id, "name": current_secret.get("name")}],
                verification_plan={"type": "read-after-write", "notes": "Verify deleted secret id is absent from secret metadata list after apply."},
                requires_ack=True,
            )

        if not _should_apply(ctx, requires_ack=True):
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "method": "secrets.delete",
                    "auth_mode": auth_mode,
                    "plan": plan,
                    "plan_out": _plan_out_if_needed(ctx, plan=plan),
                }
            )
            return 0

        loaded_plan = _load_plan(plan_in=str(plan_in), expected_method="secrets.delete", expected_selector=selector, ctx=ctx)
        _assert_no_state_drift(
            plan=loaded_plan,
            current_state={"secret": _redact_secret_info(_find_secret_by_id(_list_secret_info(ctx=ctx, headers=headers), secret_id) or {})},
        )
        response = _request_json(
            method="DELETE",
            base_url=ctx["cfg"].base_url,
            path=f"/_api/cloud-secrets-vault-server/api/v1/secrets/{secret_id}",
            headers=headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        after_secret = _find_secret_by_id(_list_secret_info(ctx=ctx, headers=headers), secret_id)
        verification = {
            "ok": after_secret is None,
            "type": "read-after-write",
            "path": "/_api/cloud-secrets-vault-server/api/v1/secrets",
            "method": "GET",
            "before": _redact_secret_info(current_secret),
            "checks": [{"field": "secret_id_absent", "expected": True, "actual": after_secret is None}],
            "notes": "Secret delete verification uses metadata readback only. Delete is irreversible.",
        }
        receipt = _build_receipt(
            method="secrets.delete",
            selector=selector,
            request=request,
            response=_redact_secret_info(response),
            verification=verification,
            plan=loaded_plan,
            ctx=ctx,
        )
        ctx["out"].emit(
            {
                "ok": bool(verification.get("ok")),
                "dry_run": False,
                "method": "secrets.delete",
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
                "method": "secrets.delete",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "secrets.delete"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "secrets.delete"})
        return 1
