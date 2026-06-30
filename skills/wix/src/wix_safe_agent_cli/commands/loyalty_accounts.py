from __future__ import annotations

from urllib.parse import quote

from . import community_groups as _groups


COMMAND_FAMILY = "loyalty-accounts"
BASE_PATH = "/loyalty-accounts/v1/accounts"


def _object_body(raw, *, field: str, allow_empty: bool = False) -> dict:
    return _groups._read_object(raw, field=field, allow_empty=allow_empty)


def _account_id(raw) -> str:
    return _groups._coerce_text(raw, field="account-id")


def _query_body(raw) -> dict:
    return _object_body(raw, field="query-json", allow_empty=True)


def _params(raw) -> dict:
    return _object_body(raw, field="params-json", allow_empty=True)


def _search_body(raw) -> dict:
    return _object_body(raw, field="search-json", allow_empty=True)


def _count_body(raw) -> dict:
    return _object_body(raw, field="count-json", allow_empty=True)


def _secondary_id_params(*, contact_id, member_id) -> dict:
    contact = contact_id.strip() if isinstance(contact_id, str) else ""
    member = member_id.strip() if isinstance(member_id, str) else ""
    if bool(contact) == bool(member):
        raise _groups.ValidationError("Provide exactly one of --contact-id or --member-id")
    if contact:
        return {"contactId": contact}
    return {"memberId": member}


def _create_body(raw) -> dict:
    body = _object_body(raw, field="account-json")
    if not isinstance(body.get("contactId"), str) or not body["contactId"].strip():
        raise _groups.ValidationError("--account-json must include contactId")
    return body


def _balance_change_body(raw, *, field: str) -> dict:
    body = _object_body(raw, field=field)
    has_balance = "balance" in body
    has_amount = "amount" in body
    if has_balance == has_amount:
        raise _groups.ValidationError(f"--{field} must include exactly one of balance or amount")
    return body


def _adjust_body(raw) -> dict:
    body = _balance_change_body(raw, field="adjust-json")
    if "revision" not in body:
        raise _groups.ValidationError("--adjust-json must include revision")
    return body


def _bulk_adjust_body(raw) -> dict:
    body = _balance_change_body(raw, field="adjust-json")
    if not isinstance(body.get("search"), dict):
        raise _groups.ValidationError("--adjust-json must include search to select the affected accounts")
    return body


def _earn_body(raw) -> dict:
    body = _object_body(raw, field="earn-json")
    amount = body.get("amount")
    if not isinstance(amount, int) or amount <= 0:
        raise _groups.ValidationError("--earn-json must include a positive integer amount")
    for key in ("appId", "idempotencyKey"):
        if not isinstance(body.get(key), str) or not body[key].strip():
            raise _groups.ValidationError(f"--earn-json must include {key}")
    return body


def cmd_loyalty_accounts_list(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list"
    try:
        params = _params(args.params_json)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=BASE_PATH,
            params=params or None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_accounts_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        account_id = _account_id(args.account_id)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/{quote(account_id, safe='')}",
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_accounts_query(args, ctx) -> int:
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


def cmd_loyalty_accounts_search(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.search"
    try:
        body = _search_body(args.search_json)
        return _groups._run_read(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/search",
            params=None,
            body=body,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_accounts_count(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.count"
    try:
        body = _count_body(args.count_json)
        return _groups._run_read(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/count",
            params=None,
            body=body,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_accounts_get_program_totals(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-program-totals"
    try:
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/program-totals",
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_accounts_get_current_member_account(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-current-member-account"
    try:
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/my-account",
            params=None,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_accounts_get_by_secondary_id(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-by-secondary-id"
    try:
        params = _secondary_id_params(contact_id=args.contact_id, member_id=args.member_id)
        return _groups._run_read(
            method_name=method,
            http_method="GET",
            path=f"{BASE_PATH}/fetch-by",
            params=params,
            body=None,
            ctx=ctx,
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_accounts_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _create_body(args.account_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=BASE_PATH,
            body=body,
            selector={"operation": "create-loyalty-account", "contactId": body.get("contactId")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["create-loyalty-account"],
            verification_notes="Provider response only. Official docs say Create Account creates a loyalty account for a site contact and requires an active loyalty program.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_accounts_adjust_points(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.adjust-points"
    try:
        account_id = _account_id(args.account_id)
        body = _adjust_body(args.adjust_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{quote(account_id, safe='')}/adjust-points",
            body=body,
            selector={"accountId": account_id, "revision": body.get("revision")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["adjust-loyalty-account-points"],
            verification_notes="Provider response only. Official docs say Adjust Points changes a loyalty account's point balance and rejects changes that would create a negative balance.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_accounts_bulk_adjust_points(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-adjust-points"
    try:
        body = _bulk_adjust_body(args.adjust_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/bulk-adjust",
            body=body,
            selector={"operation": "bulk-adjust-loyalty-account-points", "search": body.get("search")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["bulk-adjust-loyalty-account-points"],
            verification_notes="Provider response returns an asyncJobId. Official docs say Bulk Adjust Points updates the points balance of multiple accounts; use the named async-jobs commands to inspect the returned job.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)


def cmd_loyalty_accounts_earn_points(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.earn-points"
    try:
        account_id = _account_id(args.account_id)
        body = _earn_body(args.earn_json)
        return _groups._run_write(
            method_name=method,
            http_method="POST",
            path=f"{BASE_PATH}/{quote(account_id, safe='')}/earn-points",
            body=body,
            selector={"accountId": account_id, "idempotencyKey": body.get("idempotencyKey")},
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["earn-loyalty-account-points"],
            verification_notes="Provider response only. Official docs say Earn Points adds a positive point amount and requires appId plus idempotencyKey.",
        )
    except Exception as exc:
        return _groups._emit_error(ctx, method=method, exc=exc)
