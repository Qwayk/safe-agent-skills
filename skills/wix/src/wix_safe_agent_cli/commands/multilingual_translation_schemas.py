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


def _quote_path(value: str) -> str:
    return quote(value, safe="")


def _object_arg(raw: Any, *, field: str) -> dict[str, Any]:
    value = _read_json_arg(raw, field)
    if not isinstance(value, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _validate_schema_for_create(schema: dict[str, Any]) -> None:
    key = schema.get("key")
    if not isinstance(key, dict):
        raise ValidationError("--schema-json must include key")
    for field_name in ("entityType", "scope"):
        if not str(key.get(field_name) or "").strip():
            raise ValidationError(f"--schema-json key must include {field_name}")
    fields = schema.get("fields")
    if not isinstance(fields, dict) or not fields:
        raise ValidationError("--schema-json must include non-empty fields")


def _validate_schema_for_update(schema: dict[str, Any]) -> tuple[str, str]:
    schema_id = str(schema.get("id") or "").strip()
    if not schema_id:
        raise ValidationError("--schema-json must include id")
    revision = str(schema.get("revision") or "").strip()
    if not revision:
        raise ValidationError("--schema-json must include revision")
    return schema_id, revision


def _schema_update_removes_fields(schema: dict[str, Any]) -> bool:
    fields = schema.get("fields")
    if not isinstance(fields, dict):
        return False
    return any(isinstance(value, dict) and not value for value in fields.values())


def _resolve_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="multilingual-translation-schemas",
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


def _query_body(
    *,
    query_json: dict[str, Any] | None,
    filter_json: dict[str, Any] | None,
    sort_json: Any,
    cursor: str | None,
    limit: int | None,
) -> dict[str, Any]:
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


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    requires_ack: bool,
    risk_reasons: list[str],
) -> dict[str, Any]:
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
        "verification_plan": {
            "type": "provider-response",
            "notes": "Verify provider response and run multilingual-translation-schemas get/query when live confirmation is needed.",
        },
        "rollback": {"supported": False, "notes": "No automatic rollback is available for translation schema changes."},
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


def _build_receipt(
    *,
    method: str,
    request: dict[str, Any],
    response: dict[str, Any],
    selector: dict[str, Any],
    plan: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
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


def _write_command(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    requires_ack: bool,
    risk_reasons: list[str],
) -> int:
    auth_headers, auth_mode = _resolve_auth(ctx=ctx)
    plan_in = ctx.get("plan_in")
    if plan_in:
        plan = _load_plan(plan_in=str(plan_in), expected_method=method, expected_selector=selector, ctx=ctx)
    else:
        plan = _build_plan(method=method, request=request, selector=selector, ctx=ctx, requires_ack=requires_ack, risk_reasons=risk_reasons)
    if not reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="multilingual-translation-schemas"):
        ctx["out"].emit({"ok": True, "dry_run": True, "method": method, "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)})
        return 0
    loaded_plan = _load_plan(plan_in=str(plan_in), expected_method=method, expected_selector=selector, ctx=ctx) if plan_in else plan
    response = _request_json(
        method=request["method"],
        base_url=ctx["cfg"].base_url,
        path=request["path"],
        headers=auth_headers,
        params=request.get("params"),
        json_body=request.get("body"),
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    receipt = _build_receipt(method=method, request=request, response=response, selector=selector, plan=loaded_plan, ctx=ctx)
    ctx["out"].emit({"ok": True, "dry_run": False, "method": method, "auth_mode": auth_mode, "receipt": receipt, "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt)})
    return 0


def _emit_read(*, method: str, request: dict[str, Any], response: dict[str, Any], auth_mode: str, ctx: dict[str, Any]) -> None:
    out = {"ok": True, "method": method, "auth_mode": auth_mode, "request": request, "response": response}
    ctx["audit"].write(method, out)
    ctx["out"].emit(out)


def cmd_multilingual_translation_schemas_create(args, ctx) -> int:
    try:
        schema = _object_arg(getattr(args, "schema_json", None), field="schema-json")
        _validate_schema_for_create(schema)
        request = {"method": "POST", "path": "/translation-schema/v1/schemas", "body": {"schema": schema}}
        key = schema["key"]
        selector = {"kind": "wix-multilingual-translation-schema", "operation": "create", "entityType": key["entityType"], "scope": key["scope"]}
        return _write_command(method="multilingual-translation-schemas.create", request=request, selector=selector, ctx=ctx, requires_ack=False, risk_reasons=["translation-schema-create", "translation-structure-change"])
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-translation-schemas.create"})
        return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-schemas.create"})
        return 1


def cmd_multilingual_translation_schemas_get(args, ctx) -> int:
    try:
        schema_id = _required_text(getattr(args, "schema_id", None), field="schema-id")
        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        path = f"/translation-schema/v1/schemas/{_quote_path(schema_id)}"
        response = _request_json(method="GET", base_url=ctx["cfg"].base_url, path=path, headers=auth_headers, params=None, json_body=None, timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")))
        _emit_read(method="multilingual-translation-schemas.get", request={"method": "GET", "path": path}, response=response, auth_mode=auth_mode, ctx=ctx)
        return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-schemas.get"})
        return 1


def cmd_multilingual_translation_schemas_update(args, ctx) -> int:
    try:
        schema = _object_arg(getattr(args, "schema_json", None), field="schema-json")
        schema_id, revision = _validate_schema_for_update(schema)
        removes_fields = _schema_update_removes_fields(schema)
        request = {"method": "PATCH", "path": f"/translation-schema/v1/schemas/{_quote_path(schema_id)}", "body": {"schema": schema}}
        selector = {"kind": "wix-multilingual-translation-schema", "operation": "update", "schema_id": schema_id, "revision": revision}
        reasons = ["translation-schema-update", "translation-structure-change"]
        if removes_fields:
            reasons.extend(["schema-field-removal", "content-field-unavailable", "irreversible"])
        return _write_command(method="multilingual-translation-schemas.update", request=request, selector=selector, ctx=ctx, requires_ack=removes_fields, risk_reasons=reasons)
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-translation-schemas.update"})
        return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-schemas.update"})
        return 1


def cmd_multilingual_translation_schemas_delete(args, ctx) -> int:
    try:
        schema_id = _required_text(getattr(args, "schema_id", None), field="schema-id")
        request = {"method": "DELETE", "path": f"/translation-schema/v1/schemas/{_quote_path(schema_id)}", "body": {}}
        selector = {"kind": "wix-multilingual-translation-schema", "operation": "delete", "schema_id": schema_id}
        return _write_command(method="multilingual-translation-schemas.delete", request=request, selector=selector, ctx=ctx, requires_ack=True, risk_reasons=["translation-schema-delete", "translation-structure-removal", "irreversible"])
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-translation-schemas.delete"})
        return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-schemas.delete"})
        return 1


def cmd_multilingual_translation_schemas_query(args, ctx) -> int:
    try:
        query_json = _read_json_arg(getattr(args, "query_json", None), "query-json")
        if query_json is not None and not isinstance(query_json, dict):
            raise ValidationError("--query-json must be an object")
        body = _query_body(
            query_json=query_json,
            filter_json=_read_json_arg(getattr(args, "filter_json", None), "filter-json"),
            sort_json=_read_json_arg(getattr(args, "sort_json", None), "sort-json"),
            cursor=str(getattr(args, "cursor", "") or "").strip() or None,
            limit=getattr(args, "limit", None),
        )
        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        path = "/translation-schema/v1/schemas/query"
        response = _request_json(method="POST", base_url=ctx["cfg"].base_url, path=path, headers=auth_headers, params=None, json_body=body, timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")))
        _emit_read(method="multilingual-translation-schemas.query", request={"method": "POST", "path": path, "body": body}, response=response, auth_mode=auth_mode, ctx=ctx)
        return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-schemas.query"})
        return 1


def cmd_multilingual_translation_schemas_list_site(args, ctx) -> int:
    try:
        params: dict[str, Any] = {}
        for attr, key in (("app_id", "appId"), ("entity_type", "entityType"), ("scope", "scope")):
            value = str(getattr(args, attr, "") or "").strip()
            if value:
                params[key] = value
        limit = getattr(args, "limit", None)
        cursor = str(getattr(args, "cursor", "") or "").strip()
        if limit is not None:
            if limit < 0 or limit > 100:
                raise ValidationError("--limit must be between 0 and 100")
            params["paging.limit"] = int(limit)
        if cursor:
            params["paging.cursor"] = cursor
        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        path = "/translation-schema/v1/schemas/site"
        response = _request_json(method="GET", base_url=ctx["cfg"].base_url, path=path, headers=auth_headers, params=params or None, json_body=None, timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")))
        _emit_read(method="multilingual-translation-schemas.list-site", request={"method": "GET", "path": path, "params": params}, response=response, auth_mode=auth_mode, ctx=ctx)
        return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-schemas.list-site"})
        return 1


def cmd_multilingual_translation_schemas_get_by_key(args, ctx) -> int:
    try:
        app_id = _required_text(getattr(args, "app_id", None), field="app-id")
        entity_type = _required_text(getattr(args, "entity_type", None), field="entity-type")
        scope = _required_text(getattr(args, "scope", None), field="scope")
        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        path = f"/translation-schema/v1/schemas/app-id/{_quote_path(app_id)}/entity-type/{_quote_path(entity_type)}/scope/{_quote_path(scope)}"
        response = _request_json(method="GET", base_url=ctx["cfg"].base_url, path=path, headers=auth_headers, params=None, json_body=None, timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")))
        _emit_read(method="multilingual-translation-schemas.get-by-key", request={"method": "GET", "path": path}, response=response, auth_mode=auth_mode, ctx=ctx)
        return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-schemas.get-by-key"})
        return 1
