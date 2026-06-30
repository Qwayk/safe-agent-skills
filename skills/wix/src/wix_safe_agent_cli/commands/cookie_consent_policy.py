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


COMMAND_FAMILY = "cookie-consent-policy"
COOKIE_BANNER_PATH = "/cookie-consent/v1/cookie-banner-settings"
CMP_CONFIG_PATH = "/consent/cmp/v2/cmp-configs"
CONSENT_CONFIG_PATH = "/consent/consent-config/v1/consent-configs"


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_json_arg(raw: Any, *, field: str, allow_empty: bool = False) -> dict[str, Any]:
    value = _coerce_text(raw, field=field)
    if value.startswith("@"):
        path = Path(value[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        value = path.read_text(encoding="utf-8").strip()
    try:
        payload = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not allow_empty and not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
    )


def _request_json(
    *,
    method: str,
    path: str,
    headers: dict[str, str],
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
        request_headers["Content-Type"] = "application/json"
    client = HttpClient(
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
        user_agent="wix-safe-agent-cli",
    )
    response = client.request(
        method=method,
        url=ctx["cfg"].base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=params,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _emit_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, SafetyError):
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "refused": True,
                "reasons": [str(exc)],
                "refusal_type": "SafetyError",
                "method": method,
            }
        )
        return 0
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _run_read(
    *,
    method_name: str,
    http_method: str,
    path: str,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
    ctx: dict[str, Any],
) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(
        method=http_method,
        path=path,
        headers=auth["headers"],
        params=params,
        json_body=body,
        ctx=ctx,
    )
    request: dict[str, Any] = {"method": http_method, "path": path}
    if params:
        request["params"] = params
    if body is not None:
        request["body"] = body
    out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": request, "response": response}
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _build_plan(
    *,
    method_name: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    ctx: dict[str, Any],
    requires_ack: bool,
    risk_reasons: list[str],
    verification_notes: str,
) -> dict[str, Any]:
    preconditions = ["env_fingerprint must match", "selector must match", "apply requires --plan-in, --apply, and --yes"]
    if requires_ack:
        preconditions.append("apply also requires --ack-irreversible")
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "risk_level": "high" if requires_ack else "medium",
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {
            "before_state_available": False,
            "notes": "Cookie Consent Policy plans use provider-response verification in this slice.",
        },
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {
            "supported": False,
            "notes": "No automatic rollback. Verify with the matching read command and create a new reviewed plan if recovery is needed.",
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


def _run_write(
    *,
    method_name: str,
    http_method: str,
    path: str,
    body: dict[str, Any] | None,
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    ctx: dict[str, Any],
    requires_ack: bool = False,
    risk_reasons: list[str] | None = None,
    verification_notes: str = "Provider response confirms Wix accepted the request.",
) -> int:
    auth = _resolve_auth(ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    plan = _build_plan(
        method_name=method_name,
        request=request,
        selector=selector,
        proposed_changes=proposed_changes,
        ctx=ctx,
        requires_ack=requires_ack,
        risk_reasons=(risk_reasons or [f"{COMMAND_FAMILY}-write"]) + (["irreversible"] if requires_ack else []),
        verification_notes=verification_notes,
    )
    apply_allowed = reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=method_name)
    if not apply_allowed:
        out = {"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth["mode"], "plan": plan}
        if not ctx.get("apply") and ctx.get("plan_out"):
            out["plan_out"] = write_json_file(ctx["plan_out"], plan)
        ctx["audit"].write(f"{method_name}.plan", out)
        ctx["out"].emit(out)
        return 0
    loaded_plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], json_body=body, ctx=ctx)
    receipt = {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "selector": selector,
        "request": request,
        "response": response,
        "changed": True,
        "verification": {"ok": True, "type": "provider-response", "notes": verification_notes},
        "diff_applied": loaded_plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {"automatic": False, "notes": "Recovery is manual only."},
    }
    out = {"ok": True, "dry_run": False, "method": method_name, "auth_mode": auth["mode"], "receipt": receipt}
    if ctx.get("receipt_out"):
        out["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
    ctx["audit"].write(f"{method_name}.apply", out)
    ctx["out"].emit(out)
    return 0


def _require_revision(payload: dict[str, Any], *, root: str, field: str) -> None:
    target = payload.get(root)
    if not isinstance(target, dict):
        raise ValidationError(f"--{field}.{root} must be a JSON object")
    if not isinstance(target.get("revision"), str) or not target.get("revision", "").strip():
        raise ValidationError(f"--{field}.{root}.revision is required for updates")


def cmd_cookie_consent_policy_get_cookie_banner_settings(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-cookie-banner-settings"
    try:
        params = None
        language_code = getattr(args, "language_code", None)
        if language_code:
            params = {"languageCode": _coerce_text(language_code, field="language-code")}
        return _run_read(method_name=method, http_method="GET", path=COOKIE_BANNER_PATH, params=params, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_cookie_consent_policy_update_cookie_banner_settings(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update-cookie-banner-settings"
    try:
        body = _read_json_arg(getattr(args, "settings_json", None), field="settings-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"{COOKIE_BANNER_PATH}/update",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "update-cookie-banner-settings"},
            proposed_changes=[{"operation": "update-cookie-banner-settings", "body": body}],
            ctx=ctx,
            risk_reasons=["cookie-banner-settings-write", "changes-site-cookie-banner-display"],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_cookie_consent_policy_get_cmp_config(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-cmp-config"
    try:
        return _run_read(method_name=method, http_method="GET", path=CMP_CONFIG_PATH, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_cookie_consent_policy_update_cmp_config(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update-cmp-config"
    try:
        body = _read_json_arg(getattr(args, "cmp_config_json", None), field="cmp-config-json")
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=CMP_CONFIG_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "update-cmp-config"},
            proposed_changes=[{"operation": "update-cmp-config", "body": body}],
            ctx=ctx,
            risk_reasons=["cmp-config-write", "changes-privacy-component-visibility"],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_cookie_consent_policy_create_consent_config(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create-consent-config"
    try:
        body = _read_json_arg(getattr(args, "consent_config_json", None), field="consent-config-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=CONSENT_CONFIG_PATH,
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "create-consent-config"},
            proposed_changes=[{"operation": "create-consent-config", "body": body}],
            ctx=ctx,
            risk_reasons=["consent-config-create", "changes-app-embed-consent-settings"],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_cookie_consent_policy_get_consent_config(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-consent-config"
    try:
        consent_config_id = _coerce_text(getattr(args, "consent_config_id", None), field="consent-config-id")
        return _run_read(method_name=method, http_method="GET", path=f"{CONSENT_CONFIG_PATH}/{consent_config_id}", ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_cookie_consent_policy_update_consent_config(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update-consent-config"
    try:
        body = _read_json_arg(getattr(args, "consent_config_json", None), field="consent-config-json")
        _require_revision(body, root="consentConfig", field="consent-config-json")
        consent_config = body["consentConfig"]
        consent_config_id = _coerce_text(consent_config.get("id"), field="consent-config-json.consentConfig.id")
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=f"{CONSENT_CONFIG_PATH}/{consent_config_id}",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "update-consent-config", "consent_config_id": consent_config_id},
            proposed_changes=[{"operation": "update-consent-config", "consent_config_id": consent_config_id, "body": body}],
            ctx=ctx,
            risk_reasons=["consent-config-update", "requires-current-revision"],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_cookie_consent_policy_delete_consent_config(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete-consent-config"
    try:
        consent_config_id = _coerce_text(getattr(args, "consent_config_id", None), field="consent-config-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=f"{CONSENT_CONFIG_PATH}/{consent_config_id}",
            body=None,
            selector={"kind": COMMAND_FAMILY, "operation": "delete-consent-config", "consent_config_id": consent_config_id},
            proposed_changes=[{"operation": "delete-consent-config", "consent_config_id": consent_config_id}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["consent-config-delete", "permanently-deletes-consent-config"],
            verification_notes="Provider response confirms Wix accepted the Delete Consent Config request.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_cookie_consent_policy_query_consent_configs(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query-consent-configs"
    try:
        body = _read_json_arg(getattr(args, "query_json", None), field="query-json", allow_empty=True)
        return _run_read(method_name=method, http_method="POST", path=f"{CONSENT_CONFIG_PATH}/query", body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_cookie_consent_policy_bulk_create_consent_configs(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-create-consent-configs"
    try:
        body = _read_json_arg(getattr(args, "bulk_json", None), field="bulk-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/consent/consent-config/v1/bulk/consent-configs/create",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "bulk-create-consent-configs"},
            proposed_changes=[{"operation": "bulk-create-consent-configs", "body": body}],
            ctx=ctx,
            risk_reasons=["consent-config-bulk-create", "multi-consent-config-write"],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_cookie_consent_policy_bulk_delete_consent_configs(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-delete-consent-configs"
    try:
        body = _read_json_arg(getattr(args, "bulk_json", None), field="bulk-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/consent/consent-config/v1/bulk/consent-configs/delete",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "bulk-delete-consent-configs"},
            proposed_changes=[{"operation": "bulk-delete-consent-configs", "body": body}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["consent-config-bulk-delete", "multi-consent-config-delete"],
            verification_notes="Provider response confirms Wix accepted the Bulk Delete Consent Configs request.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_cookie_consent_policy_bulk_update_consent_configs(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update-consent-configs"
    try:
        body = _read_json_arg(getattr(args, "bulk_json", None), field="bulk-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/consent/consent-config/v1/bulk/consent-configs/update",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "bulk-update-consent-configs"},
            proposed_changes=[{"operation": "bulk-update-consent-configs", "body": body}],
            ctx=ctx,
            risk_reasons=["consent-config-bulk-update", "developer-preview", "multi-consent-config-write"],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_cookie_consent_policy_bulk_update_consent_config_tags(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update-consent-config-tags"
    try:
        body = _read_json_arg(getattr(args, "tags_json", None), field="tags-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/consent/consent-config/v1/bulk/consent-configs/update-tags",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "bulk-update-consent-config-tags"},
            proposed_changes=[{"operation": "bulk-update-consent-config-tags", "body": body}],
            ctx=ctx,
            risk_reasons=["consent-config-tag-bulk-update", "multi-consent-config-tag-change"],
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_cookie_consent_policy_bulk_update_consent_config_tags_by_filter(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update-consent-config-tags-by-filter"
    try:
        body = _read_json_arg(getattr(args, "tags_json", None), field="tags-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/consent/consent-config/v1/bulk/consent-configs/update-tags-by-filter",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "bulk-update-consent-config-tags-by-filter"},
            proposed_changes=[{"operation": "bulk-update-consent-config-tags-by-filter", "body": body}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=[
                "consent-config-tag-bulk-update-by-filter",
                "empty-filter-can-update-all-consent-configs",
                "async-large-scale-tag-change",
            ],
            verification_notes="Provider response confirms Wix accepted the async tag update-by-filter request.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_cookie_consent_policy_list_apps_and_storage(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list-apps-and-storage"
    try:
        body = _read_json_arg(getattr(args, "query_json", None), field="query-json", allow_empty=True)
        return _run_read(
            method_name=method,
            http_method="POST",
            path="/consent/consent-config/v1/site-apps-and-storage",
            body=body,
            ctx=ctx,
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
