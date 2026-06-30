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


def _coerce_required_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_body_json(raw: Any, *, field: str = "body-json") -> dict[str, Any]:
    body = _read_json_arg(raw, field)
    if not isinstance(body, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not body:
        raise ValidationError(f"--{field} cannot be empty")
    return body


def _quote_path(value: str) -> str:
    return quote(value, safe="")


def _resolve_resellers_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="resellers",
    )
    return auth["headers"], auth["mode"]


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
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
        params=None,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _emit_read_success(*, method: str, auth_mode: str, request: dict[str, Any], response: dict[str, Any], ctx: dict[str, Any]) -> None:
    out = {
        "ok": True,
        "method": method,
        "auth_mode": auth_mode,
        "request": request,
        "response": response,
    }
    ctx["audit"].write(method, out)
    ctx["out"].emit(out)


def _query_body(*, query_json: dict[str, Any] | None, filter_json: dict[str, Any] | None, sort_json: Any, cursor: str | None, limit: int | None) -> dict[str, Any]:
    if query_json is None:
        body: dict[str, Any] = {"query": {}}
    elif "query" in query_json and isinstance(query_json.get("query"), dict):
        body = dict(query_json)
    else:
        body = {"query": dict(query_json)}
    query = body.get("query")
    if not isinstance(query, dict):
        raise ValidationError("Query payload must include a query object")
    if filter_json is not None:
        if not isinstance(filter_json, dict):
            raise ValidationError("--filter-json must be an object")
        if "filter" not in query:
            query["filter"] = filter_json
    if sort_json is not None:
        if not isinstance(sort_json, (dict, list)):
            raise ValidationError("--sort-json must be an object or array")
        if "sort" not in query:
            query["sort"] = sort_json
    if limit is not None or cursor:
        if limit is not None and (limit <= 0 or limit > 100):
            raise ValidationError("--limit must be between 1 and 100")
        paging = dict(query.get("cursorPaging") or {})
        if cursor:
            paging["cursor"] = cursor
        if limit is not None:
            paging["limit"] = int(limit)
        query["cursorPaging"] = paging
    return body


def _build_selector(*, operation: str, ids: dict[str, str]) -> dict[str, Any]:
    return {"kind": "wix-reseller-package", "operation": operation, **ids}


def _build_plan(
    *,
    method: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    ctx: dict[str, Any],
    risk_level: str,
    risk_reasons: list[str],
    requires_ack: bool,
) -> dict[str, Any]:
    preconditions = [
        "env_fingerprint must match",
        "selector must match",
        "apply requires --apply and --yes",
    ]
    if requires_ack:
        preconditions.append("apply requires --ack-irreversible")
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "selector": selector,
        },
        "proposed_changes": [{"operation": selector.get("operation"), **{k: v for k, v in selector.items() if k not in {"kind", "operation"}}}],
        "verification_plan": {
            "type": "provider-response",
            "notes": "Verify the provider response and, when possible, run resellers get or query for the affected package.",
        },
        "rollback": {"supported": False, "notes": "No generic rollback is available for reseller package changes."},
    }


def _load_plan(*, plan_in: str | None, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan.get("method") or "") != expected_method:
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


def _should_apply(ctx: dict[str, Any], *, requires_ack: bool) -> bool:
    return reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label="resellers")


def _build_receipt(*, method: str, request: dict[str, Any], response: dict[str, Any], selector: dict[str, Any], plan: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    verification = {
        "ok": True,
        "type": "provider-response",
        "notes": "Provider returned an object response. Run resellers get or query to verify current package state where applicable.",
        "response": response,
    }
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
    risk_level: str,
    risk_reasons: list[str],
    requires_ack: bool = False,
) -> int:
    auth_headers, auth_mode = _resolve_resellers_auth(ctx=ctx)
    plan_in = ctx.get("plan_in")
    if plan_in:
        plan = _load_plan(plan_in=str(plan_in), expected_method=method, expected_selector=selector, ctx=ctx)
    else:
        plan = _build_plan(
            method=method,
            request=request,
            selector=selector,
            ctx=ctx,
            risk_level=risk_level,
            risk_reasons=risk_reasons,
            requires_ack=requires_ack,
        )

    if not _should_apply(ctx, requires_ack=requires_ack):
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "method": method,
                "auth_mode": auth_mode,
                "plan": plan,
                "plan_out": _plan_out_if_needed(ctx, plan=plan),
            }
        )
        return 0

    loaded_plan = _load_plan(
        plan_in=str(plan_in),
        expected_method=method,
        expected_selector=selector,
        ctx=ctx,
    ) if plan_in else plan
    response = _request_json(
        method=request["method"],
        base_url=ctx["cfg"].base_url,
        path=request["path"],
        headers=auth_headers,
        json_body=request.get("body"),
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    receipt = _build_receipt(method=method, request=request, response=response, selector=selector, plan=loaded_plan, ctx=ctx)
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": False,
            "method": method,
            "auth_mode": auth_mode,
            "receipt": receipt,
            "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt),
        }
    )
    return 0


def cmd_resellers_get(args, ctx) -> int:
    try:
        package_id = _coerce_required_text(getattr(args, "package_id", None), field="package-id")
        auth_headers, auth_mode = _resolve_resellers_auth(ctx=ctx)
        path = f"/resellers/v1/packages/{_quote_path(package_id)}"
        response = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=path,
            headers=auth_headers,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_read_success(method="resellers.get", auth_mode=auth_mode, request={"method": "GET", "path": path}, response=response, ctx=ctx)
        return 0
    except (SafetyError, ValidationError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "resellers.get"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "resellers.get"})
        return 1


def cmd_resellers_query(args, ctx) -> int:
    try:
        query_json = _read_json_arg(getattr(args, "query_json", None), "query-json")
        if query_json is not None and not isinstance(query_json, dict):
            raise ValidationError("--query-json must be an object")
        filter_json = _read_json_arg(getattr(args, "filter_json", None), "filter-json")
        sort_json = _read_json_arg(getattr(args, "sort_json", None), "sort-json")
        cursor = str(getattr(args, "cursor", "") or "").strip() or None
        body = _query_body(
            query_json=query_json,
            filter_json=filter_json,
            sort_json=sort_json,
            cursor=cursor,
            limit=getattr(args, "limit", None),
        )
        auth_headers, auth_mode = _resolve_resellers_auth(ctx=ctx)
        path = "/resellers/v1/packages/query"
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=path,
            headers=auth_headers,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_read_success(method="resellers.query", auth_mode=auth_mode, request={"method": "POST", "path": path, "body": body}, response=response, ctx=ctx)
        return 0
    except (SafetyError, ValidationError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "resellers.query"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "resellers.query"})
        return 1


def cmd_resellers_create_package(args, ctx) -> int:
    try:
        body = _coerce_body_json(getattr(args, "body_json", None))
        request = {"method": "POST", "path": "/resellers/v2/packages", "body": body}
        selector = _build_selector(operation="create-package", ids={"external_id": str(body.get("externalId") or "")})
        return _write_command(
            method="resellers.create-package",
            request=request,
            selector=selector,
            ctx=ctx,
            risk_level="high",
            risk_reasons=["reseller-package-create", "account-level-api-key"],
        )
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "resellers.create-package"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "resellers.create-package"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "resellers.create-package"})
        return 1


def cmd_resellers_adjust_product_instance(args, ctx) -> int:
    try:
        instance_id = _coerce_required_text(getattr(args, "instance_id", None), field="instance-id")
        body = _coerce_body_json(getattr(args, "body_json", None))
        if not any(key in body for key in ("catalogProductId", "billingInfo")):
            raise ValidationError("--body-json must include catalogProductId or billingInfo")
        request = {"method": "PATCH", "path": f"/resellers/v1/packages/product-instances/{_quote_path(instance_id)}", "body": body}
        selector = _build_selector(operation="adjust-product-instance", ids={"instance_id": instance_id})
        return _write_command(
            method="resellers.adjust-product-instance",
            request=request,
            selector=selector,
            ctx=ctx,
            risk_level="high",
            risk_reasons=["reseller-product-instance-adjust", "customer-access-change", "account-level-api-key"],
        )
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "resellers.adjust-product-instance"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "resellers.adjust-product-instance"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "resellers.adjust-product-instance"})
        return 1


def cmd_resellers_assign_product_instance(args, ctx) -> int:
    try:
        instance_id = _coerce_required_text(getattr(args, "instance_id", None), field="instance-id")
        site_id = _coerce_required_text(getattr(args, "site_id", None), field="site-id")
        request = {"method": "PATCH", "path": f"/resellers/v1/packages/product-instances/{_quote_path(instance_id)}/{_quote_path(site_id)}", "body": {}}
        selector = _build_selector(operation="assign-product-instance", ids={"instance_id": instance_id, "site_id": site_id})
        return _write_command(
            method="resellers.assign-product-instance",
            request=request,
            selector=selector,
            ctx=ctx,
            risk_level="high",
            risk_reasons=["reseller-product-instance-assign", "customer-access-change", "account-level-api-key"],
        )
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "resellers.assign-product-instance"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "resellers.assign-product-instance"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "resellers.assign-product-instance"})
        return 1


def cmd_resellers_unassign_product_instance(args, ctx) -> int:
    try:
        instance_id = _coerce_required_text(getattr(args, "instance_id", None), field="instance-id")
        request = {"method": "PATCH", "path": f"/resellers/v1/packages/product-instances/{_quote_path(instance_id)}/unassign", "body": {}}
        selector = _build_selector(operation="unassign-product-instance", ids={"instance_id": instance_id})
        return _write_command(
            method="resellers.unassign-product-instance",
            request=request,
            selector=selector,
            ctx=ctx,
            risk_level="high",
            risk_reasons=["reseller-product-instance-unassign", "customer-access-change", "account-level-api-key"],
        )
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "resellers.unassign-product-instance"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "resellers.unassign-product-instance"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "resellers.unassign-product-instance"})
        return 1


def cmd_resellers_update_package_external_id(args, ctx) -> int:
    try:
        package_id = _coerce_required_text(getattr(args, "package_id", None), field="package-id")
        external_id = _coerce_required_text(getattr(args, "external_id", None), field="external-id")
        if len(external_id) > 100:
            raise ValidationError("--external-id must be 100 characters or less")
        request = {"method": "PATCH", "path": f"/resellers/v1/packages/update/{_quote_path(package_id)}/{_quote_path(external_id)}", "body": {}}
        selector = _build_selector(operation="update-package-external-id", ids={"package_id": package_id, "external_id": external_id})
        return _write_command(
            method="resellers.update-package-external-id",
            request=request,
            selector=selector,
            ctx=ctx,
            risk_level="medium",
            risk_reasons=["reseller-package-external-id-update", "account-level-api-key"],
        )
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "resellers.update-package-external-id"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "resellers.update-package-external-id"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "resellers.update-package-external-id"})
        return 1


def cmd_resellers_cancel_package(args, ctx) -> int:
    try:
        package_id = _coerce_required_text(getattr(args, "package_id", None), field="package-id")
        request = {"method": "DELETE", "path": f"/resellers/v1/packages/{_quote_path(package_id)}", "body": {}}
        selector = _build_selector(operation="cancel-package", ids={"package_id": package_id})
        return _write_command(
            method="resellers.cancel-package",
            request=request,
            selector=selector,
            ctx=ctx,
            risk_level="critical",
            risk_reasons=["reseller-package-cancel", "customer-access-removal", "irreversible", "account-level-api-key"],
            requires_ack=True,
        )
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "resellers.cancel-package"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "resellers.cancel-package"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "resellers.cancel-package"})
        return 1


def cmd_resellers_cancel_product_instance(args, ctx) -> int:
    try:
        instance_id = _coerce_required_text(getattr(args, "instance_id", None), field="instance-id")
        request = {"method": "DELETE", "path": f"/resellers/v1/packages/product-instances/{_quote_path(instance_id)}", "body": {}}
        selector = _build_selector(operation="cancel-product-instance", ids={"instance_id": instance_id})
        return _write_command(
            method="resellers.cancel-product-instance",
            request=request,
            selector=selector,
            ctx=ctx,
            risk_level="critical",
            risk_reasons=["reseller-product-instance-cancel", "customer-access-removal", "irreversible", "account-level-api-key"],
            requires_ack=True,
        )
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "resellers.cancel-product-instance"})
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "resellers.cancel-product-instance"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "resellers.cancel-product-instance"})
        return 1
