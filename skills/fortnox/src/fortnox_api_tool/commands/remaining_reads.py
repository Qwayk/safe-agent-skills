from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .. import api_runtime
from ..auth_runtime import resolve_access_token
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file

get_json = api_runtime.get_json
request_data = api_runtime.request_data
request_json = api_runtime.request_json


def _build_request_url(base_url: str, path: str) -> str:
    if path.startswith("https://") or path.startswith("http://"):
        return path
    if path.startswith("/api/"):
        parts = urlsplit(base_url)
        if not parts.scheme or not parts.netloc:
            raise ValidationError("FORTNOX_API_BASE_URL must be an absolute URL")
        return f"{parts.scheme}://{parts.netloc}{path}"
    return f"{base_url}{path}"


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _emit_read(ctx: dict[str, Any], *, audit_key: str, path: str, payload: dict[str, Any]) -> int:
    out = {
        "ok": True,
        "path": path,
        "http_status": payload["status"],
        "token_source": payload["token_source"],
        "token_expired": payload["token_expired"],
        "data": payload["body"],
    }
    ctx["audit"].write(
        audit_key,
        {
            "ok": True,
            "path": path,
            "http_status": payload["status"],
            "token_source": payload["token_source"],
            "token_expired": payload["token_expired"],
        },
    )
    ctx["out"].emit(out)
    return 0


def _emit_request_read(
    ctx: dict[str, Any],
    *,
    audit_key: str,
    path: str,
    query_params: dict[str, Any] | None = None,
    expect_json_object: bool = True,
) -> int:
    payload = request_data(
        ctx=ctx,
        method="GET",
        path=path,
        query_params=query_params,
        expect_json=True,
        expect_json_object=expect_json_object,
    )
    return _emit_read(ctx, audit_key=audit_key, path=path, payload=payload)


def _stream_request(ctx: dict[str, Any], *, path: str, query_params: dict[str, Any] | None = None) -> dict[str, Any]:
    cfg = ctx["cfg"]
    resolved = resolve_access_token(cfg=cfg, env_file=ctx["env_file"])
    if not resolved.token:
        raise ValidationError("No Fortnox access token is available. Run `fortnox-api-tool auth login` first.")
    if resolved.expired is True and resolved.source == "token_file":
        raise ValidationError("Stored Fortnox access token looks expired. Run `fortnox-api-tool auth refresh` first.")

    client = HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"{ctx['tool']}/{ctx['tool_version']}",
    )
    url = _build_request_url(cfg.base_url, path)
    resp = client.request(
        "GET",
        url,
        headers={
            "Authorization": f"Bearer {resolved.token}",
            "Accept": "application/octet-stream, text/plain;q=0.9, application/json;q=0.5",
        },
        params=query_params,
    )
    return {
        "status": resp.status,
        "url": resp.url,
        "token_source": resolved.source,
        "token_expired": resolved.expired,
        "content_type": resp.headers.get("content-type"),
        "body": resp.text(),
    }


def _string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    items = [str(value).strip() for value in values if str(value).strip()]
    return items


def _string_value(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _load_article_url_connection_payload_file(path_str: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    path = Path(path_str)
    if not path.exists():
        raise ValidationError(f"JSON file not found: {path}")
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError("JSON file must contain a top-level object")
    article_url_connection = obj.get("ArticleUrlConnection")
    if not isinstance(article_url_connection, dict):
        raise ValidationError("JSON file must contain a top-level ArticleUrlConnection object")
    if _string_value(article_url_connection.get("ArticleNumber")) is None:
        raise ValidationError("JSON file must contain ArticleUrlConnection.ArticleNumber")
    if _string_value(article_url_connection.get("URLConnection")) is None:
        raise ValidationError("JSON file must contain ArticleUrlConnection.URLConnection")
    return path, obj, article_url_connection


def _extract_article_url_connection_item(body: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(body, dict):
        return None
    article_url_connection = body.get("ArticleUrlConnection")
    if isinstance(article_url_connection, dict):
        return article_url_connection
    return None


def _extract_article_url_connection_id(item: dict[str, Any] | None) -> str | None:
    if not isinstance(item, dict):
        return None
    return _string_value(item.get("Id"))


def _extract_article_number(item: dict[str, Any] | None) -> str | None:
    if not isinstance(item, dict):
        return None
    return _string_value(item.get("ArticleNumber"))


def _extract_url_connection(item: dict[str, Any] | None) -> str | None:
    if not isinstance(item, dict):
        return None
    return _string_value(item.get("URLConnection"))


def _extract_article_url_connections(body: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(body, dict):
        return []
    items = body.get("ArticleUrlConnections")
    if isinstance(items, list):
        return [item for item in items if isinstance(item, dict)]
    article_url_connection = _extract_article_url_connection_item(body)
    if isinstance(article_url_connection, dict):
        return [article_url_connection]
    return []


def _verify_article_url_connection_get(*, ctx: dict[str, Any], target_id: str) -> dict[str, Any]:
    path = f"/articleurlconnections/{target_id}"
    try:
        payload = request_json(ctx=ctx, method="GET", path=path, expect_json=True)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "path": path, "target_id": target_id, "error": str(e)}
    item = _extract_article_url_connection_item(payload["body"])
    present = _extract_article_url_connection_id(item) == target_id
    verification = {
        "ok": present,
        "path": path,
        "http_status": payload["status"],
        "target_id": target_id,
        "data": payload["body"],
    }
    if not present:
        verification["error"] = "Expected article URL connection to be present after write verification"
    return verification


def _verify_article_url_connection_absent(*, ctx: dict[str, Any], target_id: str) -> dict[str, Any]:
    path = f"/articleurlconnections/{target_id}"
    try:
        payload = request_json(ctx=ctx, method="GET", path=path, expect_json=True)
    except Exception as e:  # noqa: BLE001
        if "HTTP 404" in str(e):
            return {"ok": True, "path": path, "expected_http_status": 404, "target_id": target_id}
        return {"ok": False, "path": path, "target_id": target_id, "error": str(e)}
    if payload["status"] == 404:
        return {"ok": True, "path": path, "expected_http_status": 404, "target_id": target_id}
    return {
        "ok": False,
        "path": path,
        "target_id": target_id,
        "http_status": payload["status"],
        "data": payload["body"],
        "error": "Expected article URL connection to be absent after delete verification",
    }


def _build_plan(
    *,
    action: str,
    selector: dict[str, Any],
    payload_file: Path | None,
    payload_obj: dict[str, Any] | None,
    risk_level: str,
    risk_reasons: list[str],
    verification_plan: dict[str, Any],
    rollback_notes: str,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    baseline: dict[str, Any] = {
        "env_fingerprint": ctx["cfg"].base_url,
        "action": action,
        "selector": selector,
    }
    if payload_file is not None:
        payload_sha256 = _sha256_file(payload_file)
        baseline["payload_sha256"] = payload_sha256
        baseline["json_file_sha256"] = payload_sha256
        baseline["payload_file"] = str(payload_file)
    return {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
        ] + (["payload_sha256 must match"] if payload_file is not None else []),
        "baseline": baseline,
        "proposed_changes": [
            {
                "action": action,
                "selector": selector,
                "payload": payload_obj,
            }
        ],
        "verification_plan": verification_plan,
        "rollback": {"supported": False, "notes": rollback_notes},
    }


def _validate_plan_for_apply(
    plan: dict[str, Any],
    *,
    action: str,
    selector: dict[str, Any],
    payload_file: Path | None,
    ctx: dict[str, Any],
) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("action") != action:
        raise SafetyError("Refused: plan action does not match the current command")
    if baseline.get("selector") != selector:
        raise SafetyError("Refused: plan selector does not match the current command")
    expected = str(baseline.get("payload_sha256") or "").strip()
    if payload_file is None:
        if expected:
            raise SafetyError("Refused: plan expects the original JSON payload file, but no --json-file was provided")
    else:
        actual = _sha256_file(payload_file)
        if not expected or expected != actual:
            raise SafetyError("Refused: payload file hash changed since plan creation (sha256 mismatch)")


def _load_plan_from_ctx(ctx: dict[str, Any]) -> dict[str, Any]:
    plan_in = str(ctx.get("plan_in") or "").strip()
    if not plan_in:
        raise SafetyError("Refused: this write command must be applied from a reviewed plan via --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    return plan


def _write_plan_if_requested(ctx: dict[str, Any], plan: dict[str, Any]) -> str | None:
    plan_out = str(ctx.get("plan_out") or "").strip()
    if not plan_out:
        return None
    return write_json_file(plan_out, plan)


def _write_receipt_if_requested(ctx: dict[str, Any], receipt: dict[str, Any]) -> str | None:
    receipt_out = str(ctx.get("receipt_out") or "").strip()
    if not receipt_out:
        return None
    return write_json_file(receipt_out, receipt)


def _verify_article_url_connection_present(
    *,
    ctx: dict[str, Any],
    article_number: str,
    target_id: str | None,
    target_url_connection: str,
) -> dict[str, Any]:
    if target_id is not None:
        return _verify_article_url_connection_get(ctx=ctx, target_id=target_id)

    path = "/articleurlconnections"
    query_params = {"articlenumber": article_number}
    try:
        payload = request_json(
            ctx=ctx,
            method="GET",
            path=path,
            query_params=query_params,
            expect_json=True,
        )
    except Exception as e:  # noqa: BLE001
        return {
            "ok": False,
            "path": path,
            "query_params": query_params,
            "target_article_number": article_number,
            "target_id": target_id,
            "target_url_connection": target_url_connection,
            "error": str(e),
        }
    matched_item = None
    for item in _extract_article_url_connections(payload["body"]):
        item_article_number = _extract_article_number(item)
        item_url_connection = _extract_url_connection(item)
        item_id = _extract_article_url_connection_id(item)
        if item_article_number != article_number or item_url_connection != target_url_connection:
            continue
        if target_id is not None and item_id != target_id:
            continue
        matched_item = item
        break
    verification = {
        "ok": matched_item is not None,
        "path": path,
        "query_params": query_params,
        "http_status": payload["status"],
        "target_article_number": article_number,
        "target_id": target_id,
        "target_url_connection": target_url_connection,
        "data": payload["body"],
    }
    if matched_item is not None:
        verification["matched_item"] = matched_item
    else:
        verification["error"] = "Expected article URL connection to be present after write verification"
    return verification


def cmd_article_url_connections_list(args: Any, ctx: dict[str, Any]) -> int:
    article_number = str(getattr(args, "article_number", "") or "").strip()
    query_params: dict[str, Any] | None = {"articlenumber": article_number} if article_number else None
    return _emit_request_read(
        ctx,
        audit_key="article_url_connections.list",
        path="/articleurlconnections",
        query_params=query_params,
    )


def cmd_article_url_connections_create(args: Any, ctx: dict[str, Any]) -> int:
    payload_file, payload_obj, article_url_connection = _load_article_url_connection_payload_file(
        str(getattr(args, "json_file", "") or "").strip()
    )
    article_number = _extract_article_number(article_url_connection)
    url_connection = _extract_url_connection(article_url_connection)
    assert article_number is not None
    assert url_connection is not None
    selector = {
        "kind": "article-url-connection",
        "action": "create",
        "path": "/articleurlconnections",
        "article_number": article_number,
    }
    plan = _build_plan(
        action="create",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "article-url-connection-create"],
        verification_plan={
            "type": "read-after-write",
            "path_template": "/articleurlconnections/{Id}",
            "fallback": {
                "type": "list-read-after-write",
                "path": "/articleurlconnections",
                "query_params": {"articlenumber": article_number},
                "match": {
                    "ArticleNumber": article_number,
                    "URLConnection": url_connection,
                },
            },
        },
        rollback_notes="No generic rollback. The current official rendered docs only document list and create for this family in this environment.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("article_url_connections.create.plan", {"plan_out": plan_path, "article_number": article_number})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="create", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(
        ctx=ctx,
        method="POST",
        path="/articleurlconnections",
        json_body=payload_obj,
        expect_json=True,
    )
    created_item = _extract_article_url_connection_item(payload["body"])
    verification = _verify_article_url_connection_present(
        ctx=ctx,
        article_number=article_number,
        target_id=_extract_article_url_connection_id(created_item),
        target_url_connection=url_connection,
    )
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_article_number": article_number,
        "target_url_connection": url_connection,
        "target_id": _extract_article_url_connection_id(created_item),
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(
        "article_url_connections.create.apply",
        {"receipt_out": receipt_path, "article_number": article_number, "verified": verification.get("ok")},
    )
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_article_url_connections_get(args: Any, ctx: dict[str, Any]) -> int:
    target_id = str(getattr(args, "id", "") or "").strip()
    path = f"/articleurlconnections/{target_id}"
    payload = get_json(ctx=ctx, path=path)
    return _emit_read(
        ctx,
        audit_key="article_url_connections.get",
        path=path,
        payload=payload,
    )


def cmd_article_url_connections_update(args: Any, ctx: dict[str, Any]) -> int:
    target_id = str(getattr(args, "id", "") or "").strip()
    payload_file, payload_obj, article_url_connection = _load_article_url_connection_payload_file(
        str(getattr(args, "json_file", "") or "").strip()
    )
    selector = {
        "kind": "article-url-connection",
        "action": "update",
        "path": f"/articleurlconnections/{target_id}",
        "id": target_id,
    }
    plan = _build_plan(
        action="update",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "article-url-connection-update"],
        verification_plan={"type": "read-after-write", "path": f"/articleurlconnections/{target_id}"},
        rollback_notes="No generic rollback. Re-run update with the prior values if you need to revert.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("article_url_connections.update.plan", {"plan_out": plan_path, "id": target_id})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="update", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(
        ctx=ctx,
        method="PUT",
        path=f"/articleurlconnections/{target_id}",
        json_body=payload_obj,
        expect_json=True,
    )
    created_item = _extract_article_url_connection_item(payload["body"]) or article_url_connection
    verification = _verify_article_url_connection_present(
        ctx=ctx,
        article_number=_extract_article_number(created_item) or "",
        target_id=target_id,
        target_url_connection=_extract_url_connection(created_item) or "",
    )
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_id": target_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("article_url_connections.update.apply", {"receipt_out": receipt_path, "id": target_id, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_article_url_connections_delete(args: Any, ctx: dict[str, Any]) -> int:
    target_id = str(getattr(args, "id", "") or "").strip()
    selector = {
        "kind": "article-url-connection",
        "action": "delete",
        "path": f"/articleurlconnections/{target_id}",
        "id": target_id,
    }
    plan = _build_plan(
        action="delete",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="high",
        risk_reasons=["fortnox-write", "article-url-connection-delete", "irreversible"],
        verification_plan={"type": "absence-check", "path": f"/articleurlconnections/{target_id}", "expected_http_status": 404},
        rollback_notes="No generic rollback. Recreate the article URL connection explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("article_url_connections.delete.plan", {"plan_out": plan_path, "id": target_id})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")) or not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refused: delete requires --yes --ack-irreversible together with --apply and a reviewed --plan-in")
    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="delete", selector=selector, payload_file=None, ctx=ctx)
    payload = request_json(
        ctx=ctx,
        method="DELETE",
        path=f"/articleurlconnections/{target_id}",
        expect_json=False,
    )
    verification = _verify_article_url_connection_absent(ctx=ctx, target_id=target_id)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_id": target_id,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("article_url_connections.delete.apply", {"receipt_out": receipt_path, "id": target_id, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_eu_vat_limit_regulation_get(args: Any, ctx: dict[str, Any]) -> int:
    year = getattr(args, "year", None)
    query_params: dict[str, Any] | None = {"year": int(year)} if year is not None else None
    return _emit_request_read(
        ctx,
        audit_key="eu_vat_limit_regulation.get",
        path="/euvatlimitregulation",
        query_params=query_params,
    )


def cmd_integration_ratings_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    return _emit_request_read(
        ctx,
        audit_key="integration_ratings.list",
        path="/api/integration-developer/ratings-v1",
        expect_json_object=False,
    )


def cmd_sie_get(args: Any, ctx: dict[str, Any]) -> int:
    sie_type = str(getattr(args, "sie_type", "") or "").strip()
    query_params: dict[str, Any] = {}
    selection = str(getattr(args, "selection", "") or "").strip()
    if selection:
        query_params["selection"] = selection
    financial_year = getattr(args, "financial_year", None)
    if financial_year is not None:
        query_params["financialYear"] = int(financial_year)
    export_all = str(getattr(args, "export_all", "") or "").strip()
    if export_all:
        query_params["exportall"] = export_all
    from_date = str(getattr(args, "from_date", "") or "").strip()
    if from_date:
        query_params["fromdate"] = from_date
    to_date = str(getattr(args, "to_date", "") or "").strip()
    if to_date:
        query_params["todate"] = to_date
    path = f"/sie/{sie_type}"
    payload = _stream_request(ctx, path=path, query_params=query_params or None)
    out = {
        "ok": True,
        "path": path,
        "http_status": payload["status"],
        "token_source": payload["token_source"],
        "token_expired": payload["token_expired"],
        "content_type": payload["content_type"],
        "data": payload["body"],
    }
    ctx["audit"].write(
        "sie.get",
        {
            "ok": True,
            "path": path,
            "http_status": payload["status"],
            "content_type": payload["content_type"],
            "token_source": payload["token_source"],
            "token_expired": payload["token_expired"],
        },
    )
    ctx["out"].emit(out)
    return 0


def cmd_stock_status_get_stock_balance(args: Any, ctx: dict[str, Any]) -> int:
    item_ids = _string_list(getattr(args, "item_id", None))
    stock_point_codes = _string_list(getattr(args, "stock_point_code", None))
    query_params: dict[str, Any] = {}
    if item_ids:
        query_params["itemIds"] = ",".join(item_ids)
    if stock_point_codes:
        query_params["stockPointCodes"] = ",".join(stock_point_codes)
    return _emit_request_read(
        ctx,
        audit_key="stock_status.get_stock_balance",
        path="/api/warehouse/status-v1/stockbalance",
        query_params=query_params or None,
        expect_json_object=False,
    )


def cmd_tenant_get(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    return _emit_request_read(
        ctx,
        audit_key="tenant.get",
        path="/api/warehouse/tenants-v4",
    )


def cmd_users_fetch_user_information_for_a_single_published_integration_and_tenant(args: Any, ctx: dict[str, Any]) -> int:
    integration_id = str(getattr(args, "integration_id", "") or "").strip()
    tenant_id = str(getattr(args, "tenant_id", "") or "").strip()
    return _emit_request_read(
        ctx,
        audit_key="users.fetch_user_information_for_a_single_published_integration_and_tenant",
        path=f"/api/integration-developer/users/users-v1/{integration_id}/{tenant_id}",
        expect_json_object=False,
    )
