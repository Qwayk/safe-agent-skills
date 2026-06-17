from __future__ import annotations

from typing import Any

from ..api_runtime import request_json


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


def _emit_request_read(ctx: dict[str, Any], *, audit_key: str, path: str) -> int:
    payload = request_json(
        ctx=ctx,
        method="GET",
        path=path,
        expect_json=True,
    )
    return _emit_read(ctx, audit_key=audit_key, path=path, payload=payload)


def cmd_integration_sales_get_by_app_id(args: Any, ctx: dict[str, Any]) -> int:
    app_id = str(getattr(args, "app_id", "") or "").strip()
    return _emit_request_read(
        ctx,
        audit_key="integration_sales.get_by_app_id",
        path=f"/api/integration-partner/apps/sales-v1/{app_id}",
    )


def cmd_integration_sales_get_by_app_id_and_tenant(args: Any, ctx: dict[str, Any]) -> int:
    app_id = str(getattr(args, "app_id", "") or "").strip()
    tenant_id = str(getattr(args, "tenant_id", "") or "").strip()
    return _emit_request_read(
        ctx,
        audit_key="integration_sales.get_by_app_id_and_tenant",
        path=f"/api/integration-partner/apps/sales-v1/{app_id}/{tenant_id}",
    )


def cmd_integration_sales_resolves_sales_information_of_an_integration(args: Any, ctx: dict[str, Any]) -> int:
    integration_id = str(getattr(args, "integration_id", "") or "").strip()
    return _emit_request_read(
        ctx,
        audit_key="integration_sales.resolves_sales_information_of_an_integration",
        path=f"/api/integration-developer/sales-v1/{integration_id}",
    )
