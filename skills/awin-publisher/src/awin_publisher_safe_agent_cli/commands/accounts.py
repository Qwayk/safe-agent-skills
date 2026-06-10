from __future__ import annotations

from .api_helpers import (
    build_access_token_query,
    build_bearer_headers,
    fetch_accounts,
    filtered_publisher_accounts,
    safe_query_meta,
)


def cmd_accounts_list(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    http = ctx["http_client"]
    accounts, status = fetch_accounts(cfg, http)
    publisher_accounts, non_publisher_accounts = filtered_publisher_accounts(accounts)

    params = build_access_token_query(cfg.token or "")
    headers = build_bearer_headers(cfg.token or "")

    out = {
        "ok": True,
        "operation": "accounts.list",
        "accounts": publisher_accounts,
        "request": {
            "method": "GET",
            "endpoint": f"{cfg.api_host}/accounts",
            "header_keys": sorted(headers.keys()),
            "query": {
                "required": ["accessToken"],
                "safe_query": safe_query_meta(params),
            },
            "response_status": status,
        },
        "metadata": {
            "auth_mode": "bearer",
            "publisher_accounts_only": True,
            "publisher_accounts_count": len(publisher_accounts),
            "non_publisher_accounts_count": len(non_publisher_accounts),
            "total_accounts_returned": len(accounts),
        },
    }

    ctx["audit"].write("accounts.list", out)
    ctx["out"].emit(out)
    return 0
