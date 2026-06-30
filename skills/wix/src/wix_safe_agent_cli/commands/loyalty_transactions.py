from __future__ import annotations

from urllib.parse import quote

from . import community_groups as _groups


COMMAND_FAMILY = "loyalty-transactions"
BASE_PATH = "/loyalty-transactions/v1/loyalty-transactions"


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _transaction_id(raw) -> str:
    return _groups._coerce_text(raw, field="transaction-id")


def _query_body(raw) -> dict:
    return _object_body(raw, field="query-json", allow_empty=True)


def cmd_loyalty_transactions_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        transaction_id = _transaction_id(args.transaction_id)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/{quote(transaction_id, safe='')}",
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_transactions_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        body = _query_body(args.query_json)
        return _groups._run_read(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/query",
            params=None,
            body=body,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
