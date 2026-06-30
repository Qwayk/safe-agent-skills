from __future__ import annotations

import time
from typing import Any

from . import online_programs_programs as _shared
from ..authz import resolve_auth_mode
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested


CACHE_FAMILY = "viewer-cache"
SEO_FAMILY = "viewer-seo-tags"
CACHE_PATH = "/ssr/v1/invalidate-cache"
SEO_ITEM_PATH = "/promote/seo/v1/resolve-item-seo-tags"
SEO_STATIC_PATH = "/promote/seo/v1/resolve-static-page-seo-tags"

ValidationError = _shared.ValidationError
SafetyError = _shared.SafetyError


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _resolve_auth(ctx: dict[str, Any], *, family: str) -> dict[str, Any]:
    return resolve_auth_mode(cfg=ctx["cfg"], env_file=str(ctx["env_file"]), verbose=bool(ctx.get("verbose")), command_family=family)


def _request_json(*, method: str, path: str, headers: dict[str, str], params: dict[str, Any] | None, body: dict[str, Any] | None, ctx: dict[str, Any]) -> dict[str, Any]:
    request_headers = dict(headers)
    if body is not None:
        request_headers["Content-Type"] = "application/json"
    client = HttpClient(timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")), user_agent="wix-safe-agent-cli")
    response = client.request(method=method, url=ctx["cfg"].base_url.rstrip("/") + "/" + path.lstrip("/"), headers=request_headers, params=params, json_body=body)
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _invalidation_body(raw: Any) -> dict[str, Any]:
    methods = _shared._array_arg(raw, field="invalidation-methods-json", max_items=100)
    for item in methods:
        if not isinstance(item, dict) or not str(item.get("tag") or "").strip():
            raise ValidationError("--invalidation-methods-json items must be objects with tag")
        if len(str(item["tag"])) > 500:
            raise ValidationError("--invalidation-methods-json tag values must be at most 500 characters")
    return {"invalidationMethods": methods}


def _query_params(args: Any, *, static: bool) -> dict[str, Any]:
    params: dict[str, Any] = {}
    page_url = getattr(args, "page_url", None)
    if not isinstance(page_url, str) or not page_url.strip():
        raise ValidationError("Missing --page-url")
    params["pageUrl"] = page_url.strip()
    if static:
        page_name = getattr(args, "page_name", None)
        if not isinstance(page_name, str) or not page_name.strip():
            raise ValidationError("Missing --page-name")
        params["pageName"] = page_name.strip()
    else:
        slug = getattr(args, "slug", None)
        item_type = getattr(args, "item_type", None)
        if not isinstance(slug, str) or not slug.strip():
            raise ValidationError("Missing --slug")
        if not isinstance(item_type, str) or not item_type.strip():
            raise ValidationError("Missing --item-type")
        params["slug"] = slug.strip()
        params["itemType"] = item_type.strip()
    seo_data = getattr(args, "seo_data_json", None)
    if seo_data:
        params["seoData"] = _shared._object_arg(seo_data, field="seo-data-json", allow_empty=True)
    return params


def _read(method_name: str, path: str, params: dict[str, Any], ctx: dict[str, Any]) -> int:
    auth = _resolve_auth(ctx, family=SEO_FAMILY)
    response = _request_json(method="GET", path=path, headers=auth["headers"], params=params, body=None, ctx=ctx)
    out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": {"method": "GET", "path": path, "params": params}, "response": response}
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _plan(method_name: str, request: dict[str, Any], selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "risk_level": "medium",
        "risk_reasons": ["viewer-cache-invalidation", "site-cache-state-change"],
        "preconditions": ["env_fingerprint must match", "selector must match", "apply requires --plan-in, --apply, and --yes"],
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {"before_state_available": False, "notes": "Wix cache state is not readable before invalidation."},
        "proposed_changes": [{"operation": method_name, "selector": selector}],
        "verification_plan": {"type": "provider-response", "notes": "Provider returns an empty object on success; affected web method/router cache entries are not directly readable by this CLI."},
        "rollback": {"supported": False, "notes": "Cache invalidation cannot be rolled back. Cache warms naturally on later site requests."},
    }


def _load_plan(plan_in: str | None, *, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if plan.get("method") != expected_method:
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict) or baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    return plan


def cmd_viewer_cache_invalidate(args, ctx) -> int:
    method = f"{CACHE_FAMILY}.invalidate"
    try:
        body = _invalidation_body(getattr(args, "invalidation_methods_json", None))
        selector = {"tags": [item["tag"] for item in body["invalidationMethods"]]}
        auth = _resolve_auth(ctx, family=CACHE_FAMILY)
        request = {"method": "POST", "path": CACHE_PATH, "body": body}
        plan = _plan(method, request, selector, ctx)
        if not reviewed_plan_apply_requested(ctx, requires_ack=False, command_label=method):
            out = {"ok": True, "dry_run": True, "method": method, "auth_mode": auth["mode"], "plan": plan}
            if not ctx.get("apply") and ctx.get("plan_out"):
                out["plan_out"] = write_json_file(ctx["plan_out"], plan)
            ctx["audit"].write(f"{method}.plan", out)
            ctx["out"].emit(out)
            return 0
        loaded_plan = _load_plan(ctx.get("plan_in"), expected_method=method, expected_selector=selector, ctx=ctx)
        response = _request_json(method="POST", path=CACHE_PATH, headers=auth["headers"], params=None, body=body, ctx=ctx)
        receipt = {"ok": True, "dry_run": False, "method": method, "auth_mode": auth["mode"], "request": request, "response": response, "verified": {"type": "provider-response"}, "diff_applied": loaded_plan.get("proposed_changes") or []}
        if ctx.get("receipt_out"):
            receipt["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
        ctx["audit"].write(f"{method}.apply", receipt)
        ctx["out"].emit(receipt)
        return 0
    except (ValidationError, SafetyError, RuntimeError) as exc:
        return _shared._emit_error(ctx, method=method, exc=exc)


def cmd_viewer_seo_tags_resolve_item(args, ctx) -> int:
    method = f"{SEO_FAMILY}.resolve-item"
    try:
        return _read(method, SEO_ITEM_PATH, _query_params(args, static=False), ctx)
    except (ValidationError, RuntimeError) as exc:
        return _shared._emit_error(ctx, method=method, exc=exc)


def cmd_viewer_seo_tags_resolve_static(args, ctx) -> int:
    method = f"{SEO_FAMILY}.resolve-static"
    try:
        return _read(method, SEO_STATIC_PATH, _query_params(args, static=True), ctx)
    except (ValidationError, RuntimeError) as exc:
        return _shared._emit_error(ctx, method=method, exc=exc)
