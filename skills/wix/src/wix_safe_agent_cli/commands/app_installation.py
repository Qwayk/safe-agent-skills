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

_REDACTED_TOKEN = "***REDACTED***"


def _read_json_arg(raw: Any, *, field: str, required: bool = False) -> Any | None:
    if raw is None:
        if required:
            raise ValidationError(f"Missing --{field}")
        return None
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
        if not text:
            raise ValidationError(f"--{field} file is empty: {path}")

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc


def _coerce_required_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"Missing --{field}")
    return value


def _coerce_optional_text(raw: Any, *, field: str) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_bool(raw: Any, *, field: str, default: bool | None = None) -> bool | None:
    if raw is None:
        return default
    if isinstance(raw, bool):
        return raw
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be true or false")
    value = raw.strip().lower()
    if value == "true":
        return True
    if value == "false":
        return False
    raise ValidationError(f"--{field} must be true or false")


def _coerce_tenant(raw: Any) -> dict[str, Any]:
    value = _read_json_arg(raw, field="tenant-json", required=True)
    if not isinstance(value, dict):
        raise ValidationError("--tenant-json must be a JSON object")

    tenant_id = _coerce_required_text(value.get("id"), field="tenant-json.id")
    tenant_type = _coerce_required_text(value.get("tenantType"), field="tenant-json.tenantType")
    tenant = dict(value)
    tenant["id"] = tenant_id
    tenant["tenantType"] = tenant_type
    return tenant


def _coerce_request_json(raw: Any) -> dict[str, Any]:
    value = _read_json_arg(raw, field="request-json", required=True)
    if not isinstance(value, dict):
        raise ValidationError("--request-json must be a JSON object")
    install_type = _coerce_required_text(value.get("installType"), field="request-json.installType")
    request = dict(value)
    request["installType"] = install_type
    return request


def _coerce_app_instance_item(raw: Any, *, field: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValidationError(f"Each item in --{field} must be an object")

    app_def_id = _coerce_required_text(raw.get("appDefId"), field=f"{field}.appDefId")
    item: dict[str, Any] = {"appDefId": app_def_id}

    if "version" in raw and raw["version"] is not None:
        item["version"] = _coerce_required_text(raw.get("version"), field=f"{field}.version")
    if "enabled" in raw:
        item["enabled"] = _coerce_bool(raw.get("enabled"), field=f"{field}.enabled", default=True)
    return item


def _coerce_app_instances(raw: Any) -> list[dict[str, Any]]:
    value = _read_json_arg(raw, field="app-instances-json", required=True)
    if not isinstance(value, list):
        raise ValidationError("--app-instances-json must be a JSON array")
    if len(value) > 20:
        raise ValidationError("--app-instances-json cannot contain more than 20 items")

    items = [_coerce_app_instance_item(item, field="app-instances-json") for item in value]
    return items


def _coerce_app_def_ids(raw: Any) -> list[str]:
    value = _read_json_arg(raw, field="app-def-ids-json", required=True)
    if not isinstance(value, list):
        raise ValidationError("--app-def-ids-json must be a JSON array")
    if len(value) > 20:
        raise ValidationError("--app-def-ids-json cannot contain more than 20 items")

    ids: list[str] = []
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(f"--app-def-ids-json[{i}] must be a string")
        app_def_id = item.strip()
        if not app_def_id:
            raise ValidationError(f"--app-def-ids-json[{i}] cannot be empty")
        ids.append(app_def_id)
    return ids


def _sanitize_app_tokens(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            if str(key).lower() == "apptoken":
                sanitized[key] = _REDACTED_TOKEN
            else:
                sanitized[key] = _sanitize_app_tokens(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_app_tokens(item) for item in value]
    return value


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
    allow_empty: bool = False,
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
    try:
        payload = response.json()
    except Exception as exc:  # noqa: BLE001
        if allow_empty:
            return {}
        raise ValidationError("Wix API returned a non-object JSON response") from exc
    if payload is None:
        if allow_empty:
            return {}
        raise ValidationError("Wix API returned a non-object JSON response")
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _resolve_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="app-installation",
    )
    return auth["headers"], auth["mode"]


def _build_selector(*, operation: str, tenant: dict[str, Any], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    selector = {"kind": "wix-app-installation", "operation": operation, "tenant": tenant}
    if extra:
        selector.update(extra)
    return selector


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    verification_notes: str,
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "high",
        "risk_reasons": ["wix-app-installation-write", "manual-recovery-needed"],
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "apply requires --plan-in, --apply, --yes, and --ack-irreversible",
        ],
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
            "note": "No before-state snapshot is guaranteed for arbitrary tenant context.",
        },
        "state_capture": {
            "before_state_available": False,
            "notes": "No before-state snapshot is guaranteed for arbitrary tenant context; recovery may be manual.",
        },
        "proposed_changes": proposed_changes,
        "verification_plan": {
            "type": "provider-response",
            "notes": verification_notes,
        },
        "rollback": {
            "supported": False,
            "notes": "No automatic rollback. Before-state snapshot is not guaranteed for arbitrary tenant context, so recovery may be manual.",
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


def _should_apply(ctx: dict[str, Any]) -> bool:
    if bool(ctx.get("apply")) and bool(ctx.get("yes")) and not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refused: app-installation live apply requires --ack-irreversible")

    review_ctx = dict(ctx)
    review_ctx["enforce_reviewed_plan"] = True
    return reviewed_plan_apply_requested(review_ctx, requires_ack=True, command_label="app-installation")


def _collect_app_instances(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        app_instance = value.get("appInstance")
        if isinstance(app_instance, dict):
            found.append(app_instance)
        for item in value.values():
            found.extend(_collect_app_instances(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(_collect_app_instances(item))
    return found


def _verify_single_install_response(*, response: dict[str, Any], expected_app_def_id: str) -> dict[str, Any]:
    app_instance = response.get("appInstance")
    if not isinstance(app_instance, dict):
        return {
            "ok": False,
            "type": "provider-response",
            "notes": "Provider response did not include an appInstance object.",
            "response": response,
        }

    app_instance_id = str(app_instance.get("id") or "").strip()
    app_def_id = str(app_instance.get("appDefId") or "").strip()
    if not app_instance_id:
        return {
            "ok": False,
            "type": "provider-response",
            "notes": "Provider response did not include appInstance.id.",
            "response": response,
        }
    if not app_def_id:
        return {
            "ok": False,
            "type": "provider-response",
            "notes": "Provider response did not include appInstance.appDefId.",
            "response": response,
        }
    if app_def_id != expected_app_def_id:
        return {
            "ok": False,
            "type": "provider-response",
            "notes": "Provider response appInstance.appDefId did not match the requested appDefId.",
            "response": response,
        }
    return {
        "ok": True,
        "type": "provider-response",
        "notes": "Provider response included appInstance.id and appInstance.appDefId.",
        "response": response,
    }


def _verify_install_from_share_url_response(*, response: dict[str, Any]) -> dict[str, Any]:
    app_instance = response.get("appInstance")
    if not isinstance(app_instance, dict):
        return {
            "ok": False,
            "type": "provider-response",
            "notes": "Provider response did not include an appInstance object.",
            "response": response,
        }

    app_instance_id = str(app_instance.get("id") or "").strip()
    app_def_id = str(app_instance.get("appDefId") or "").strip()
    if not app_instance_id or not app_def_id:
        return {
            "ok": False,
            "type": "provider-response",
            "notes": "Provider response did not include appInstance.id and appInstance.appDefId.",
            "response": response,
        }
    return {
        "ok": True,
        "type": "provider-response",
        "notes": "Provider response included appInstance.id and appInstance.appDefId.",
        "response": response,
    }


def _verify_bulk_install_response(*, response: dict[str, Any], expected_app_def_ids: list[str]) -> dict[str, Any]:
    instances = _collect_app_instances(response)
    if not instances:
        return {
            "ok": False,
            "type": "provider-response",
            "notes": "Provider response did not include any appInstance objects.",
            "response": response,
        }

    returned_ids: list[str] = []
    for instance in instances:
        app_instance_id = str(instance.get("id") or "").strip()
        app_def_id = str(instance.get("appDefId") or "").strip()
        if not app_instance_id or not app_def_id:
            return {
                "ok": False,
                "type": "provider-response",
                "notes": "Provider response included an appInstance missing id or appDefId.",
                "response": response,
            }
        returned_ids.append(app_def_id)

    expected_set = set(expected_app_def_ids)
    returned_set = set(returned_ids)
    if not expected_set.issubset(returned_set):
        return {
            "ok": False,
            "type": "provider-response",
            "notes": "Provider response did not include every requested appDefId.",
            "response": response,
        }

    bulk_meta = response.get("bulkActionMetadata")
    if isinstance(bulk_meta, dict):
        total_failures = bulk_meta.get("totalFailures")
        if isinstance(total_failures, int) and total_failures > 0:
            return {
                "ok": False,
                "type": "provider-response",
                "notes": "Provider response reported bulk failures.",
                "response": response,
            }

    return {
        "ok": True,
        "type": "provider-response",
        "notes": "Provider response included appInstance.id and appInstance.appDefId for the requested items.",
        "response": response,
    }


def _verify_uninstall_response(*, response: dict[str, Any]) -> dict[str, Any]:
    if not response:
        return {
            "ok": True,
            "type": "provider-response",
            "notes": "Provider response was empty, which this endpoint allows.",
            "response": response,
        }
    return {
        "ok": True,
        "type": "provider-response",
        "notes": "Provider response was returned and should be reviewed manually.",
        "response": response,
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
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "selector": selector,
        "request": request,
        "response": _sanitize_app_tokens(response),
        "changed": bool(verification.get("ok")),
        "verification": verification,
        "state_capture": {
            "before_state_available": False,
            "notes": "No before-state snapshot is guaranteed for arbitrary tenant context; recovery may be manual.",
        },
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {
            "automatic": False,
            "notes": "Recovery is manual only. No before-state snapshot is guaranteed for arbitrary tenant context.",
        },
    }


def cmd_app_installation_get_installed(args, ctx) -> int:
    try:
        _ = args
        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        response = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/apps-installer-service/v1/app-instances",
            headers=auth_headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "app-installation.get-installed",
            "auth_mode": auth_mode,
            "request": {
                "method": "GET",
                "path": "/apps-installer-service/v1/app-instances",
            },
            "response": _sanitize_app_tokens(response),
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "app-installation.get-installed"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "app-installation.get-installed"})
        return 1


def cmd_app_installation_is_permitted(args, ctx) -> int:
    try:
        request = _coerce_request_json(getattr(args, "request_json", None))
        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/apps-installer-service/v1/app-instance/is-permitted-to-install",
            headers=auth_headers,
            params=None,
            json_body=request,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "app-installation.is-permitted",
            "auth_mode": auth_mode,
            "request": {
                "method": "POST",
                "path": "/apps-installer-service/v1/app-instance/is-permitted-to-install",
                "body": request,
            },
            "response": _sanitize_app_tokens(response),
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "app-installation.is-permitted"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "app-installation.is-permitted"})
        return 1


def cmd_app_installation_install(args, ctx) -> int:
    try:
        tenant = _coerce_tenant(getattr(args, "tenant_json", None))
        app_def_id = _coerce_required_text(getattr(args, "app_def_id", None), field="app-def-id")
        enabled = _coerce_bool(getattr(args, "enabled", None), field="enabled", default=True)
        version = _coerce_optional_text(getattr(args, "version", None), field="version")

        app_instance: dict[str, Any] = {"appDefId": app_def_id, "enabled": bool(enabled)}
        if version is not None:
            app_instance["version"] = version

        request = {
            "method": "POST",
            "path": "/apps-installer-service/v1/app-instance/install",
            "body": {"tenant": tenant, "appInstance": app_instance},
        }
        selector = _build_selector(
            operation="install",
            tenant=tenant,
            extra={"appDefId": app_def_id, "enabled": bool(enabled), "version": version},
        )

        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="app-installation.install", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="app-installation.install",
                request=request,
                selector=selector,
                ctx=ctx,
                proposed_changes=[{"operation": "install", "appDefId": app_def_id, "enabled": bool(enabled), "version": version}],
                verification_notes="Verify the provider response returns appInstance.id and appInstance.appDefId.",
            )

        if not _should_apply(ctx):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "app-installation.install",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="app-installation.install",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request["path"],
            headers=auth_headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = _verify_single_install_response(response=response, expected_app_def_id=app_def_id)
        receipt = _build_receipt(
            method="app-installation.install",
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
            "method": "app-installation.install",
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
                "method": "app-installation.install",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "app-installation.install"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "app-installation.install"})
        return 1


def cmd_app_installation_install_from_share_url(args, ctx) -> int:
    try:
        tenant = _coerce_tenant(getattr(args, "tenant_json", None))
        share_url_id = _coerce_required_text(getattr(args, "share_url_id", None), field="share-url-id")
        dev_override_id = _coerce_optional_text(getattr(args, "dev_override_id", None), field="dev-override-id")

        body: dict[str, Any] = {"tenant": tenant, "shareUrlId": share_url_id}
        if dev_override_id is not None:
            body["devOverrideId"] = dev_override_id

        request = {
            "method": "POST",
            "path": "/apps-installer-service/v1/app-share-url/install",
            "body": body,
        }
        selector = _build_selector(
            operation="install-from-share-url",
            tenant=tenant,
            extra={"shareUrlId": share_url_id, "devOverrideId": dev_override_id},
        )

        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="app-installation.install-from-share-url",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="app-installation.install-from-share-url",
                request=request,
                selector=selector,
                ctx=ctx,
                proposed_changes=[{"operation": "install-from-share-url", "shareUrlId": share_url_id, "devOverrideId": dev_override_id}],
                verification_notes="Verify the provider response returns appInstance.id and appInstance.appDefId.",
            )

        if not _should_apply(ctx):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "app-installation.install-from-share-url",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="app-installation.install-from-share-url",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request["path"],
            headers=auth_headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = _verify_install_from_share_url_response(response=response)
        receipt = _build_receipt(
            method="app-installation.install-from-share-url",
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
            "method": "app-installation.install-from-share-url",
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
                "method": "app-installation.install-from-share-url",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": "ValidationError",
                "method": "app-installation.install-from-share-url",
            }
        )
        return 1
    except RuntimeError as exc:
        ctx["out"].emit(
            {
                "ok": False,
                "error": str(exc),
                "error_type": exc.__class__.__name__,
                "method": "app-installation.install-from-share-url",
            }
        )
        return 1


def cmd_app_installation_uninstall(args, ctx) -> int:
    try:
        tenant = _coerce_tenant(getattr(args, "tenant_json", None))
        app_def_id = _coerce_required_text(getattr(args, "app_def_id", None), field="app-def-id")

        request = {
            "method": "POST",
            "path": "/apps-installer-service/v1/app-instance/uninstall",
            "body": {"tenant": tenant, "appDefId": app_def_id},
        }
        selector = _build_selector(operation="uninstall", tenant=tenant, extra={"appDefId": app_def_id})

        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(plan_in=str(plan_in), expected_method="app-installation.uninstall", expected_selector=selector, ctx=ctx)
        else:
            plan = _build_plan(
                method="app-installation.uninstall",
                request=request,
                selector=selector,
                ctx=ctx,
                proposed_changes=[{"operation": "uninstall", "appDefId": app_def_id}],
                verification_notes="Provider response may be empty; success is based on a successful HTTP response.",
            )

        if not _should_apply(ctx):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "app-installation.uninstall",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="app-installation.uninstall",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request["path"],
            headers=auth_headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
            allow_empty=True,
        )
        verification = _verify_uninstall_response(response=response)
        receipt = _build_receipt(
            method="app-installation.uninstall",
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
            "method": "app-installation.uninstall",
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
                "method": "app-installation.uninstall",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "app-installation.uninstall"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "app-installation.uninstall"})
        return 1


def cmd_app_installation_bulk_install(args, ctx) -> int:
    try:
        tenant = _coerce_tenant(getattr(args, "tenant_json", None))
        app_instances = _coerce_app_instances(getattr(args, "app_instances_json", None))
        app_def_ids = [item["appDefId"] for item in app_instances]

        request = {
            "method": "POST",
            "path": "/apps-installer-service/v1/bulk/app-instance/install",
            "body": {"tenant": tenant, "appInstances": app_instances},
        }
        selector = _build_selector(operation="bulk-install", tenant=tenant, extra={"appDefIds": app_def_ids})

        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="app-installation.bulk-install",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="app-installation.bulk-install",
                request=request,
                selector=selector,
                ctx=ctx,
                proposed_changes=[{"operation": "bulk-install", "appDefIds": app_def_ids}],
                verification_notes="Verify the provider response returns appInstance.id and appInstance.appDefId for each requested app definition.",
            )

        if not _should_apply(ctx):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "app-installation.bulk-install",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="app-installation.bulk-install",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request["path"],
            headers=auth_headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        verification = _verify_bulk_install_response(response=response, expected_app_def_ids=app_def_ids)
        receipt = _build_receipt(
            method="app-installation.bulk-install",
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
            "method": "app-installation.bulk-install",
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
                "method": "app-installation.bulk-install",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "app-installation.bulk-install"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "app-installation.bulk-install"})
        return 1


def cmd_app_installation_bulk_uninstall(args, ctx) -> int:
    try:
        tenant = _coerce_tenant(getattr(args, "tenant_json", None))
        app_def_ids = _coerce_app_def_ids(getattr(args, "app_def_ids_json", None))

        request = {
            "method": "POST",
            "path": "/apps-installer-service/v1/bulk/app-instance/uninstall",
            "body": {"tenant": tenant, "appDefIds": app_def_ids},
        }
        selector = _build_selector(operation="bulk-uninstall", tenant=tenant, extra={"appDefIds": app_def_ids})

        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        plan_in = ctx.get("plan_in")
        if plan_in:
            plan = _load_plan(
                plan_in=str(plan_in),
                expected_method="app-installation.bulk-uninstall",
                expected_selector=selector,
                ctx=ctx,
            )
        else:
            plan = _build_plan(
                method="app-installation.bulk-uninstall",
                request=request,
                selector=selector,
                ctx=ctx,
                proposed_changes=[{"operation": "bulk-uninstall", "appDefIds": app_def_ids}],
                verification_notes="Provider response may be empty; success is based on a successful HTTP response.",
            )

        if not _should_apply(ctx):
            out = {
                "ok": True,
                "dry_run": True,
                "method": "app-installation.bulk-uninstall",
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
            ctx["out"].emit(out)
            return 0

        loaded_plan = _load_plan(
            plan_in=str(plan_in),
            expected_method="app-installation.bulk-uninstall",
            expected_selector=selector,
            ctx=ctx,
        ) if plan_in else plan
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request["path"],
            headers=auth_headers,
            params=None,
            json_body=request["body"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
            allow_empty=True,
        )
        verification = _verify_uninstall_response(response=response)
        receipt = _build_receipt(
            method="app-installation.bulk-uninstall",
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
            "method": "app-installation.bulk-uninstall",
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
                "method": "app-installation.bulk-uninstall",
            }
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "app-installation.bulk-uninstall"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "app-installation.bulk-uninstall"})
        return 1
