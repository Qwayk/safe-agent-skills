from __future__ import annotations

from .api_helpers import (
    build_access_token_query,
    build_bearer_headers,
    filtered_publisher_accounts,
    fetch_accounts,
    safe_query_meta,
)


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    http = ctx["http_client"]
    accounts, status = fetch_accounts(cfg, http)
    publisher_accounts, non_publisher_accounts = filtered_publisher_accounts(accounts)
    headers = build_bearer_headers(cfg.token or "")
    params = build_access_token_query(cfg.token or "")

    out = {
        "ok": True,
        "auth_check": {
            "endpoint": f"{cfg.api_host}/accounts",
            "auth_mode": "bearer",
            "required_query": ["accessToken"],
            "safe_query": safe_query_meta(params),
            "headers": {"Authorization": "<redacted>"},
        },
        "publisher_accounts_only": True,
        "publisher_accounts_count": len(publisher_accounts),
        "publisher_accounts": publisher_accounts,
        "non_publisher_accounts_count": len(non_publisher_accounts),
        "total_accounts_returned": len(accounts),
        "request": {
            "method": "GET",
            "endpoint": f"{cfg.api_host}/accounts",
            "header_keys": sorted(headers.keys()),
            "response_status": status,
        },
    }

    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0
