from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote

from ..authz import resolve_auth_mode
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested


def _read_json_arg(raw: Any, field: str) -> Any:
    if raw is None:
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
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc


def _required_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _bool_param(raw: Any) -> bool | None:
    if raw is None:
        return None
    return str(raw).strip().lower() == "true"


def _quote_path(value: str) -> str:
    return quote(value, safe="")


def _object_arg(raw: Any, *, field: str) -> dict[str, Any]:
    value = _read_json_arg(raw, field)
    if not isinstance(value, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _array_arg(raw: Any, *, field: str, max_items: int = 100) -> list[Any]:
    value = _read_json_arg(raw, field)
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON array")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    if len(value) > max_items:
        raise ValidationError(f"--{field} supports at most {max_items} items")
    return value


def _validate_locale_for_create(locale: dict[str, Any]) -> None:
    if not str(locale.get("languageCode") or "").strip():
        raise ValidationError("--locale-json must include languageCode")


def _validate_locale_for_update(locale: dict[str, Any]) -> None:
    if not str(locale.get("id") or "").strip():
        raise ValidationError("--locale-json must include id")
    if not str(locale.get("revision") or "").strip():
        raise ValidationError("--locale-json must include revision")


def _resolve_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="multilingual-locales",
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


def _query_body(*, query_json: dict[str, Any] | None, filter_json: dict[str, Any] | None, sort_json: Any, cursor: str | None, limit: int | None) -> dict[str, Any]:
    body = dict(query_json) if isinstance(query_json, dict) and isinstance(query_json.get("query"), dict) else {"query": dict(query_json or {})}
    query = body["query"]
    if filter_json is not None:
        if not isinstance(filter_json, dict):
            raise ValidationError("--filter-json must be an object")
        query.setdefault("filter", filter_json)
    if sort_json is not None:
        if not isinstance(sort_json, (dict, list)):
            raise ValidationError("--sort-json must be an object or array")
        query.setdefault("sort", sort_json)
    if cursor or limit is not None:
        if limit is not None and (limit <= 0 or limit > 100):
            raise ValidationError("--limit must be between 1 and 100")
        paging = dict(query.get("cursorPaging") or {})
        if cursor:
            paging["cursor"] = cursor
        if limit is not None:
            paging["limit"] = int(limit)
        query["cursorPaging"] = paging
    return body


def _build_plan(*, method: str, request: dict[str, Any], selector: dict[str, Any], ctx: dict[str, Any], requires_ack: bool, risk_reasons: list[str]) -> dict[str, Any]:
    preconditions = ["env_fingerprint must match", "selector must match", "apply requires --apply and --yes"]
    if requires_ack:
        preconditions.append("apply requires --ack-irreversible")
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "critical" if requires_ack else "high",
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector},
        "proposed_changes": [{"operation": selector.get("operation"), **{k: v for k, v in selector.items() if k not in {"kind", "operation"}}}],
        "verification_plan": {"type": "provider-response", "notes": "Verify provider response and run multilingual-locales get/query when live confirmation is needed."},
        "rollback": {"supported": False, "notes": "No automatic rollback is available for locale changes."},
    }


def _load_plan(*, plan_in: str | None, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if plan.get("method") != expected_method:
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan missing baseline")
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


def _build_receipt(*, method: str, request: dict[str, Any], response: dict[str, Any], selector: dict[str, Any], plan: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    verification = {"ok": True, "type": "provider-response", "notes": "Provider returned an object response.", "response": response}
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "selector": selector,
        "request": request,
        "response": response,
        "changed": True,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }


def _write_command(*, method: str, request: dict[str, Any], selector: dict[str, Any], ctx: dict[str, Any], requires_ack: bool, risk_reasons: list[str]) -> int:
    auth_headers, auth_mode = _resolve_auth(ctx=ctx)
    plan_in = ctx.get("plan_in")
    if plan_in:
        plan = _load_plan(plan_in=str(plan_in), expected_method=method, expected_selector=selector, ctx=ctx)
    else:
        plan = _build_plan(method=method, request=request, selector=selector, ctx=ctx, requires_ack=requires_ack, risk_reasons=risk_reasons)
    if not reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="multilingual-locales"):
        ctx["out"].emit({"ok": True, "dry_run": True, "method": method, "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)})
        return 0
    loaded_plan = _load_plan(plan_in=str(plan_in), expected_method=method, expected_selector=selector, ctx=ctx) if plan_in else plan
    response = _request_json(method=request["method"], base_url=ctx["cfg"].base_url, path=request["path"], headers=auth_headers, params=request.get("params"), json_body=request.get("body"), timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")))
    receipt = _build_receipt(method=method, request=request, response=response, selector=selector, plan=loaded_plan, ctx=ctx)
    ctx["out"].emit({"ok": True, "dry_run": False, "method": method, "auth_mode": auth_mode, "receipt": receipt, "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt)})
    return 0


def _emit_read(*, method: str, request: dict[str, Any], response: dict[str, Any], auth_mode: str, ctx: dict[str, Any]) -> None:
    out = {"ok": True, "method": method, "auth_mode": auth_mode, "request": request, "response": response}
    ctx["audit"].write(method, out)
    ctx["out"].emit(out)


def cmd_multilingual_locales_create(args, ctx) -> int:
    try:
        locale = _object_arg(getattr(args, "locale_json", None), field="locale-json")
        _validate_locale_for_create(locale)
        request = {"method": "POST", "path": "/locales/v2/locale", "body": {"locale": locale}}
        selector = {"kind": "wix-multilingual-locale", "operation": "create", "languageCode": locale["languageCode"], "regionCode": locale.get("regionCode")}
        return _write_command(method="multilingual-locales.create", request=request, selector=selector, ctx=ctx, requires_ack=False, risk_reasons=["locale-create", "multilingual-site-change"])
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-locales.create"}); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-locales.create"}); return 1


def cmd_multilingual_locales_get(args, ctx) -> int:
    try:
        locale_id = _required_text(getattr(args, "locale_id", None), field="locale-id")
        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        path = f"/locales/v2/locale/{_quote_path(locale_id)}"
        response = _request_json(method="GET", base_url=ctx["cfg"].base_url, path=path, headers=auth_headers, params=None, json_body=None, timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")))
        _emit_read(method="multilingual-locales.get", request={"method": "GET", "path": path}, response=response, auth_mode=auth_mode, ctx=ctx); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-locales.get"}); return 1


def cmd_multilingual_locales_update(args, ctx) -> int:
    try:
        locale = _object_arg(getattr(args, "locale_json", None), field="locale-json")
        _validate_locale_for_update(locale)
        locale_id = str(locale["id"]).strip()
        request = {"method": "PATCH", "path": f"/locales/v2/locale/{_quote_path(locale_id)}", "body": {"locale": locale}}
        selector = {"kind": "wix-multilingual-locale", "operation": "update", "locale_id": locale_id, "revision": str(locale["revision"]).strip()}
        return _write_command(method="multilingual-locales.update", request=request, selector=selector, ctx=ctx, requires_ack=False, risk_reasons=["locale-update", "multilingual-site-change"])
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-locales.update"}); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-locales.update"}); return 1


def cmd_multilingual_locales_delete(args, ctx) -> int:
    try:
        locale_id = _required_text(getattr(args, "locale_id", None), field="locale-id")
        request = {"method": "DELETE", "path": f"/locales/v2/locale/{_quote_path(locale_id)}", "body": {}}
        selector = {"kind": "wix-multilingual-locale", "operation": "delete", "locale_id": locale_id}
        return _write_command(method="multilingual-locales.delete", request=request, selector=selector, ctx=ctx, requires_ack=True, risk_reasons=["locale-delete", "translated-content-removal", "irreversible"])
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-locales.delete"}); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-locales.delete"}); return 1


def cmd_multilingual_locales_query(args, ctx) -> int:
    try:
        query_json = _read_json_arg(getattr(args, "query_json", None), "query-json")
        if query_json is not None and not isinstance(query_json, dict):
            raise ValidationError("--query-json must be an object")
        body = _query_body(query_json=query_json, filter_json=_read_json_arg(getattr(args, "filter_json", None), "filter-json"), sort_json=_read_json_arg(getattr(args, "sort_json", None), "sort-json"), cursor=str(getattr(args, "cursor", "") or "").strip() or None, limit=getattr(args, "limit", None))
        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        path = "/locales/v2/locale/query"
        response = _request_json(method="POST", base_url=ctx["cfg"].base_url, path=path, headers=auth_headers, params=None, json_body=body, timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")))
        _emit_read(method="multilingual-locales.query", request={"method": "POST", "path": path, "body": body}, response=response, auth_mode=auth_mode, ctx=ctx); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-locales.query"}); return 1


def cmd_multilingual_locales_bulk_create(args, ctx) -> int:
    try:
        locales = _array_arg(getattr(args, "locales_json", None), field="locales-json")
        for item in locales:
            if not isinstance(item, dict): raise ValidationError("--locales-json items must be objects")
            _validate_locale_for_create(item)
        body = {"locales": locales}
        return_entity = _bool_param(getattr(args, "return_entity", None))
        if return_entity is not None: body["returnEntity"] = return_entity
        request = {"method": "POST", "path": "/locales/v2/bulk/locale/create", "body": body}
        selector = {"kind": "wix-multilingual-locale", "operation": "bulk-create", "count": len(locales)}
        return _write_command(method="multilingual-locales.bulk-create", request=request, selector=selector, ctx=ctx, requires_ack=False, risk_reasons=["locale-bulk-create", "multilingual-site-change"])
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-locales.bulk-create"}); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-locales.bulk-create"}); return 1


def cmd_multilingual_locales_bulk_delete(args, ctx) -> int:
    try:
        ids = _array_arg(getattr(args, "locale_ids_json", None), field="locale-ids-json")
        locale_ids = [str(item).strip() for item in ids if str(item).strip()]
        if len(locale_ids) != len(ids): raise ValidationError("--locale-ids-json items must be non-empty")
        request = {"method": "POST", "path": "/locales/v2/bulk/locale/delete", "body": {"localeIds": locale_ids}}
        selector = {"kind": "wix-multilingual-locale", "operation": "bulk-delete", "locale_ids": locale_ids}
        return _write_command(method="multilingual-locales.bulk-delete", request=request, selector=selector, ctx=ctx, requires_ack=True, risk_reasons=["locale-bulk-delete", "translated-content-removal", "irreversible"])
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-locales.bulk-delete"}); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-locales.bulk-delete"}); return 1


def cmd_multilingual_locales_bulk_update(args, ctx) -> int:
    try:
        locales = _array_arg(getattr(args, "locales_json", None), field="locales-json")
        for item in locales:
            if not isinstance(item, dict) or not isinstance(item.get("locale"), dict):
                raise ValidationError("--locales-json items must include locale objects")
            _validate_locale_for_update(item["locale"])
        request = {"method": "POST", "path": "/locales/v2/bulk/locale/update", "body": {"locales": locales}}
        selector = {"kind": "wix-multilingual-locale", "operation": "bulk-update", "count": len(locales)}
        return _write_command(method="multilingual-locales.bulk-update", request=request, selector=selector, ctx=ctx, requires_ack=False, risk_reasons=["locale-bulk-update", "multilingual-site-change"])
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-locales.bulk-update"}); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-locales.bulk-update"}); return 1


def cmd_multilingual_locales_create_new_primary(args, ctx) -> int:
    try:
        primary = _object_arg(getattr(args, "primary_locale_json", None), field="primary-locale-json")
        _validate_locale_for_create(primary)
        request = {"method": "POST", "path": "/locales/v2/locale/change-primary", "body": {"primaryLocale": primary}}
        selector = {"kind": "wix-multilingual-locale", "operation": "create-new-primary", "languageCode": primary["languageCode"], "regionCode": primary.get("regionCode")}
        return _write_command(method="multilingual-locales.create-new-primary", request=request, selector=selector, ctx=ctx, requires_ack=True, risk_reasons=["primary-locale-change", "site-wide-language-change", "irreversible"])
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-locales.create-new-primary"}); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-locales.create-new-primary"}); return 1


def cmd_multilingual_locales_get_new_primary_status(args, ctx) -> int:
    try:
        token = _required_text(getattr(args, "token", None), field="token")
        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        path = "/locales/v2/locale/change-primary"
        response = _request_json(method="GET", base_url=ctx["cfg"].base_url, path=path, headers=auth_headers, params={"token": token}, json_body=None, timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")))
        _emit_read(method="multilingual-locales.get-new-primary-status", request={"method": "GET", "path": path, "params": {"token": token}}, response=response, auth_mode=auth_mode, ctx=ctx); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-locales.get-new-primary-status"}); return 1


def cmd_multilingual_locales_list_supported(args, ctx) -> int:
    try:
        params = {}
        for attr, key in [("include_all_locales", "includeAllLocales"), ("include_region_options", "includeRegionOptions")]:
            value = _bool_param(getattr(args, attr, None))
            if value is not None: params[key] = value
        language_code = str(getattr(args, "language_code", "") or "").strip()
        if language_code: params["languageCode"] = language_code
        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        path = "/locales/v2/locales/supported"
        response = _request_json(method="GET", base_url=ctx["cfg"].base_url, path=path, headers=auth_headers, params=params or None, json_body=None, timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")))
        _emit_read(method="multilingual-locales.list-supported", request={"method": "GET", "path": path, "params": params}, response=response, auth_mode=auth_mode, ctx=ctx); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-locales.list-supported"}); return 1


def cmd_multilingual_locales_set_visitor_primary(args, ctx) -> int:
    try:
        locale_id = _required_text(getattr(args, "locale_id", None), field="locale-id")
        request = {"method": "POST", "path": "/locales/v2/locale/set-visitor-primary", "body": {"localeId": locale_id}}
        selector = {"kind": "wix-multilingual-locale", "operation": "set-visitor-primary", "locale_id": locale_id}
        return _write_command(method="multilingual-locales.set-visitor-primary", request=request, selector=selector, ctx=ctx, requires_ack=False, risk_reasons=["visitor-primary-locale-change", "site-default-language-change"])
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-locales.set-visitor-primary"}); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-locales.set-visitor-primary"}); return 1
