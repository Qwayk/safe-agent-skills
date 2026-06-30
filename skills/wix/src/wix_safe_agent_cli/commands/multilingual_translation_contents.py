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


def _bool_param(raw: Any) -> bool | None:
    if raw is None:
        return None
    return str(raw).strip().lower() == "true"


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


def _validate_create_content(content: dict[str, Any], *, field: str) -> None:
    for key in ("schemaId", "entityId", "locale"):
        if not str(content.get(key) or "").strip():
            raise ValidationError(f"--{field} must include {key}")
    fields = content.get("fields")
    if not isinstance(fields, dict) or not fields:
        raise ValidationError(f"--{field} must include non-empty fields")


def _validate_update_content(content: dict[str, Any], *, field: str) -> str:
    content_id = str(content.get("id") or "").strip()
    if not content_id:
        raise ValidationError(f"--{field} must include id")
    if not str(content.get("schemaId") or "").strip():
        raise ValidationError(f"--{field} must include schemaId")
    return content_id


def _validate_key_content(content: dict[str, Any], *, field: str) -> None:
    for key in ("schemaId", "entityId", "locale"):
        if not str(content.get(key) or "").strip():
            raise ValidationError(f"--{field} must include {key}")


def _content_removes_fields(content: dict[str, Any]) -> bool:
    fields = content.get("fields")
    if not isinstance(fields, dict):
        return False
    return any(isinstance(value, dict) and not value for value in fields.values())


def _resolve_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="multilingual-translation-contents",
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


def _search_body(*, search_json: dict[str, Any] | None, cursor: str | None, limit: int | None) -> dict[str, Any]:
    body = dict(search_json) if isinstance(search_json, dict) and isinstance(search_json.get("search"), dict) else {"search": dict(search_json or {})}
    search = body["search"]
    if cursor or limit is not None:
        if limit is not None and (limit <= 0 or limit > 100):
            raise ValidationError("--limit must be between 1 and 100")
        paging = dict(search.get("cursorPaging") or {})
        if cursor:
            paging["cursor"] = cursor
        if limit is not None:
            paging["limit"] = int(limit)
        search["cursorPaging"] = paging
    return body


def _add_option_flags(body: dict[str, Any], args: Any, *, allow_return_entity: bool) -> None:
    force = _bool_param(getattr(args, "force_fields_timestamp_update", None))
    if force is not None:
        body["forceFieldsTimestampUpdate"] = force
    if allow_return_entity:
        return_entity = _bool_param(getattr(args, "return_entity", None))
        if return_entity is not None:
            body["returnEntity"] = return_entity


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
        "verification_plan": {"type": "provider-response", "notes": "Verify provider response and run multilingual-translation-contents get/query when live confirmation is needed."},
        "rollback": {"supported": False, "notes": "No automatic rollback is available for translation content changes."},
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
    if not reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="multilingual-translation-contents"):
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


def cmd_multilingual_translation_contents_create(args, ctx) -> int:
    try:
        content = _object_arg(getattr(args, "content_json", None), field="content-json")
        _validate_create_content(content, field="content-json")
        request = {"method": "POST", "path": "/translation-content/v1/contents", "body": {"content": content}}
        selector = {"kind": "wix-multilingual-translation-content", "operation": "create", "schema_id": content["schemaId"], "entity_id": content["entityId"], "locale": content["locale"]}
        return _write_command(method="multilingual-translation-contents.create", request=request, selector=selector, ctx=ctx, requires_ack=False, risk_reasons=["translation-content-create"])
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-translation-contents.create"}); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-contents.create"}); return 1


def cmd_multilingual_translation_contents_get(args, ctx) -> int:
    try:
        content_id = _required_text(getattr(args, "content_id", None), field="content-id")
        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        path = f"/translation-content/v1/contents/{_quote_path(content_id)}"
        response = _request_json(method="GET", base_url=ctx["cfg"].base_url, path=path, headers=auth_headers, params=None, json_body=None, timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")))
        _emit_read(method="multilingual-translation-contents.get", request={"method": "GET", "path": path}, response=response, auth_mode=auth_mode, ctx=ctx); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-contents.get"}); return 1


def cmd_multilingual_translation_contents_update(args, ctx) -> int:
    try:
        content = _object_arg(getattr(args, "content_json", None), field="content-json")
        content_id = _validate_update_content(content, field="content-json")
        removes_fields = _content_removes_fields(content)
        body = {"content": content}
        _add_option_flags(body, args, allow_return_entity=False)
        request = {"method": "PATCH", "path": f"/translation-content/v1/contents/{_quote_path(content_id)}", "body": body}
        selector = {"kind": "wix-multilingual-translation-content", "operation": "update", "content_id": content_id, "schema_id": content["schemaId"]}
        reasons = ["translation-content-update"]
        if removes_fields:
            reasons.extend(["content-field-removal", "field-unavailable", "irreversible"])
        return _write_command(method="multilingual-translation-contents.update", request=request, selector=selector, ctx=ctx, requires_ack=removes_fields, risk_reasons=reasons)
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-translation-contents.update"}); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-contents.update"}); return 1


def cmd_multilingual_translation_contents_delete(args, ctx) -> int:
    try:
        content_id = _required_text(getattr(args, "content_id", None), field="content-id")
        request = {"method": "DELETE", "path": f"/translation-content/v1/contents/{_quote_path(content_id)}", "body": {}}
        selector = {"kind": "wix-multilingual-translation-content", "operation": "delete", "content_id": content_id}
        return _write_command(method="multilingual-translation-contents.delete", request=request, selector=selector, ctx=ctx, requires_ack=True, risk_reasons=["translation-content-delete", "irreversible"])
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-translation-contents.delete"}); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-contents.delete"}); return 1


def cmd_multilingual_translation_contents_query(args, ctx) -> int:
    try:
        query_json = _read_json_arg(getattr(args, "query_json", None), "query-json")
        if query_json is not None and not isinstance(query_json, dict):
            raise ValidationError("--query-json must be an object")
        body = _query_body(query_json=query_json, filter_json=_read_json_arg(getattr(args, "filter_json", None), "filter-json"), sort_json=_read_json_arg(getattr(args, "sort_json", None), "sort-json"), cursor=str(getattr(args, "cursor", "") or "").strip() or None, limit=getattr(args, "limit", None))
        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        path = "/translation-content/v1/contents/query"
        response = _request_json(method="POST", base_url=ctx["cfg"].base_url, path=path, headers=auth_headers, params=None, json_body=body, timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")))
        _emit_read(method="multilingual-translation-contents.query", request={"method": "POST", "path": path, "body": body}, response=response, auth_mode=auth_mode, ctx=ctx); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-contents.query"}); return 1


def cmd_multilingual_translation_contents_search(args, ctx) -> int:
    try:
        search_json = _read_json_arg(getattr(args, "search_json", None), "search-json")
        if search_json is not None and not isinstance(search_json, dict):
            raise ValidationError("--search-json must be an object")
        body = _search_body(search_json=search_json, cursor=str(getattr(args, "cursor", "") or "").strip() or None, limit=getattr(args, "limit", None))
        auth_headers, auth_mode = _resolve_auth(ctx=ctx)
        path = "/translation-content/v1/contents/search"
        response = _request_json(method="POST", base_url=ctx["cfg"].base_url, path=path, headers=auth_headers, params=None, json_body=body, timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")))
        _emit_read(method="multilingual-translation-contents.search", request={"method": "POST", "path": path, "body": body}, response=response, auth_mode=auth_mode, ctx=ctx); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-contents.search"}); return 1


def cmd_multilingual_translation_contents_bulk_create(args, ctx) -> int:
    try:
        contents = _array_arg(getattr(args, "contents_json", None), field="contents-json")
        for item in contents:
            if not isinstance(item, dict):
                raise ValidationError("--contents-json items must be objects")
            _validate_create_content(item, field="contents-json")
        body = {"contents": contents}
        _add_option_flags(body, args, allow_return_entity=True)
        request = {"method": "POST", "path": "/translation-content/v1/bulk/contents/create", "body": body}
        selector = {"kind": "wix-multilingual-translation-content", "operation": "bulk-create", "count": len(contents)}
        return _write_command(method="multilingual-translation-contents.bulk-create", request=request, selector=selector, ctx=ctx, requires_ack=False, risk_reasons=["translation-content-bulk-create"])
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-translation-contents.bulk-create"}); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-contents.bulk-create"}); return 1


def cmd_multilingual_translation_contents_bulk_delete(args, ctx) -> int:
    try:
        ids = _array_arg(getattr(args, "content_ids_json", None), field="content-ids-json")
        content_ids = [str(item).strip() for item in ids if str(item).strip()]
        if len(content_ids) != len(ids):
            raise ValidationError("--content-ids-json items must be non-empty")
        request = {"method": "POST", "path": "/translation-content/v1/bulk/contents/delete", "body": {"contentIds": content_ids}}
        selector = {"kind": "wix-multilingual-translation-content", "operation": "bulk-delete", "content_ids": content_ids}
        return _write_command(method="multilingual-translation-contents.bulk-delete", request=request, selector=selector, ctx=ctx, requires_ack=True, risk_reasons=["translation-content-bulk-delete", "irreversible"])
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-translation-contents.bulk-delete"}); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-contents.bulk-delete"}); return 1


def cmd_multilingual_translation_contents_bulk_update(args, ctx) -> int:
    try:
        contents = _array_arg(getattr(args, "contents_json", None), field="contents-json")
        removes_fields = False
        for item in contents:
            if not isinstance(item, dict) or not isinstance(item.get("content"), dict):
                raise ValidationError("--contents-json items must include content objects")
            _validate_update_content(item["content"], field="contents-json")
            removes_fields = removes_fields or _content_removes_fields(item["content"])
        body = {"contents": contents}
        _add_option_flags(body, args, allow_return_entity=True)
        request = {"method": "POST", "path": "/translation-content/v1/bulk/contents/update", "body": body}
        selector = {"kind": "wix-multilingual-translation-content", "operation": "bulk-update", "count": len(contents)}
        reasons = ["translation-content-bulk-update"]
        if removes_fields:
            reasons.extend(["content-field-removal", "field-unavailable", "irreversible"])
        return _write_command(method="multilingual-translation-contents.bulk-update", request=request, selector=selector, ctx=ctx, requires_ack=removes_fields, risk_reasons=reasons)
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-translation-contents.bulk-update"}); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-contents.bulk-update"}); return 1


def cmd_multilingual_translation_contents_update_by_key(args, ctx) -> int:
    try:
        content = _object_arg(getattr(args, "content_json", None), field="content-json")
        _validate_key_content(content, field="content-json")
        removes_fields = _content_removes_fields(content)
        body = {"content": content}
        _add_option_flags(body, args, allow_return_entity=False)
        request = {"method": "PATCH", "path": "/translation-content/v1/contents/by-key", "body": body}
        selector = {"kind": "wix-multilingual-translation-content", "operation": "update-by-key", "schema_id": content["schemaId"], "entity_id": content["entityId"], "locale": content["locale"]}
        reasons = ["translation-content-update-by-key"]
        if removes_fields:
            reasons.extend(["content-field-removal", "field-unavailable", "irreversible"])
        return _write_command(method="multilingual-translation-contents.update-by-key", request=request, selector=selector, ctx=ctx, requires_ack=removes_fields, risk_reasons=reasons)
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-translation-contents.update-by-key"}); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-contents.update-by-key"}); return 1


def cmd_multilingual_translation_contents_bulk_update_by_key(args, ctx) -> int:
    try:
        contents = _array_arg(getattr(args, "contents_json", None), field="contents-json")
        removes_fields = False
        for item in contents:
            if not isinstance(item, dict) or not isinstance(item.get("content"), dict):
                raise ValidationError("--contents-json items must include content objects")
            _validate_key_content(item["content"], field="contents-json")
            removes_fields = removes_fields or _content_removes_fields(item["content"])
        body = {"contents": contents}
        _add_option_flags(body, args, allow_return_entity=True)
        request = {"method": "POST", "path": "/translation-content/v1/bulk/contents/update-by-key", "body": body}
        selector = {"kind": "wix-multilingual-translation-content", "operation": "bulk-update-by-key", "count": len(contents)}
        reasons = ["translation-content-bulk-update-by-key"]
        if removes_fields:
            reasons.extend(["content-field-removal", "field-unavailable", "irreversible"])
        return _write_command(method="multilingual-translation-contents.bulk-update-by-key", request=request, selector=selector, ctx=ctx, requires_ack=removes_fields, risk_reasons=reasons)
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-translation-contents.bulk-update-by-key"}); return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-translation-contents.bulk-update-by-key"}); return 1
