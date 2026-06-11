from __future__ import annotations

from typing import Any

from ..context import build_mercury_client
from ..errors import ValidationError


def _clean_params(params: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in params.items():
        if v is None:
            continue
        if isinstance(v, list):
            vv = [x for x in v if x is not None and str(x).strip() != ""]
            if not vv:
                continue
            out[k] = vv
            continue
        if isinstance(v, str) and not v.strip():
            continue
        out[k] = v
    return out


def _redact_attachment_urls(obj: Any) -> Any:
    """
    Attachment metadata can include signed download URLs (credential-like).
    Redact `url` fields from output payloads.
    """
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            if k == "url" and isinstance(v, str) and v.strip():
                out["url_redacted"] = True
                continue
            out[k] = _redact_attachment_urls(v)
        return out
    if isinstance(obj, list):
        return [_redact_attachment_urls(x) for x in obj]
    return obj


def cmd_get_organization(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    client = build_mercury_client(ctx)
    obj = client.get_json("/organization")
    out = {"ok": True, "organization": obj}
    ctx["audit"].write("organization.get", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_list_accounts(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    client = build_mercury_client(ctx)
    obj = client.get_json("/accounts")
    out = {"ok": True, "accounts": obj}
    ctx["audit"].write("accounts.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_get_account(args: Any, ctx: dict[str, Any]) -> int:
    account_id = str(getattr(args, "account_id", "") or "").strip()
    if not account_id:
        raise ValidationError("Missing --account-id")
    client = build_mercury_client(ctx)
    obj = client.get_json(f"/account/{account_id}")
    out = {"ok": True, "account": obj}
    ctx["audit"].write("accounts.get", {"account_id": account_id})
    ctx["out"].emit(out)
    return 0


def cmd_list_account_cards(args: Any, ctx: dict[str, Any]) -> int:
    account_id = str(getattr(args, "account_id", "") or "").strip()
    if not account_id:
        raise ValidationError("Missing --account-id")
    client = build_mercury_client(ctx)
    obj = client.get_json(f"/account/{account_id}/cards")
    out = {"ok": True, "cards": obj}
    ctx["audit"].write("accounts.cards.list", {"account_id": account_id})
    ctx["out"].emit(out)
    return 0


def cmd_list_account_statements(args: Any, ctx: dict[str, Any]) -> int:
    account_id = str(getattr(args, "account_id", "") or "").strip()
    if not account_id:
        raise ValidationError("Missing --account-id")
    client = build_mercury_client(ctx)
    obj = client.get_json(f"/account/{account_id}/statements")
    out = {"ok": True, "statements": obj}
    ctx["audit"].write("accounts.statements.list", {"account_id": account_id})
    ctx["out"].emit(out)
    return 0


def cmd_list_account_transactions(args: Any, ctx: dict[str, Any]) -> int:
    account_id = str(getattr(args, "account_id", "") or "").strip()
    if not account_id:
        raise ValidationError("Missing --account-id")
    params = _clean_params(
        {
            "limit": getattr(args, "limit", None),
            "start": getattr(args, "start", None),
            "end": getattr(args, "end", None),
            "search": getattr(args, "search", None),
            "status": getattr(args, "status", None),
            "offset": getattr(args, "offset", None),
            "order": getattr(args, "order", None),
            "requestId": getattr(args, "request_id", None),
            "mercuryCategory": getattr(args, "mercury_category", None),
            "categoryId": getattr(args, "category_id", None),
        }
    )
    client = build_mercury_client(ctx)
    obj = client.get_json(f"/account/{account_id}/transactions", params=params)
    out = {"ok": True, "account_id": account_id, "response": obj}
    ctx["audit"].write("accounts.transactions.list", {"account_id": account_id, "params": params})
    ctx["out"].emit(out)
    return 0


def cmd_get_account_transaction(args: Any, ctx: dict[str, Any]) -> int:
    account_id = str(getattr(args, "account_id", "") or "").strip()
    transaction_id = str(getattr(args, "transaction_id", "") or "").strip()
    if not account_id:
        raise ValidationError("Missing --account-id")
    if not transaction_id:
        raise ValidationError("Missing --transaction-id")
    client = build_mercury_client(ctx)
    obj = client.get_json(f"/account/{account_id}/transaction/{transaction_id}")
    out = {"ok": True, "transaction": obj}
    ctx["audit"].write(
        "accounts.transactions.get",
        {"account_id": account_id, "transaction_id": transaction_id},
    )
    ctx["out"].emit(out)
    return 0


def cmd_list_transactions(args: Any, ctx: dict[str, Any]) -> int:
    params = _clean_params(
        {
            "status": getattr(args, "status", None),
            "search": getattr(args, "search", None),
            "start": getattr(args, "start", None),
            "end": getattr(args, "end", None),
            "postedStart": getattr(args, "posted_start", None),
            "postedEnd": getattr(args, "posted_end", None),
            "accountId": getattr(args, "account_id", None),
            "mercuryCategory": getattr(args, "mercury_category", None),
            "categoryId": getattr(args, "category_id", None),
            "start_at": getattr(args, "start_at", None),
            "start_after": getattr(args, "start_after", None),
            "end_before": getattr(args, "end_before", None),
            "limit": getattr(args, "limit", None),
            "order": getattr(args, "order", None),
        }
    )
    client = build_mercury_client(ctx)
    obj = client.get_json("/transactions", params=params)
    out = {"ok": True, "response": obj}
    ctx["audit"].write("transactions.list", {"params": params})
    ctx["out"].emit(out)
    return 0


def cmd_get_transaction(args: Any, ctx: dict[str, Any]) -> int:
    transaction_id = str(getattr(args, "transaction_id", "") or "").strip()
    if not transaction_id:
        raise ValidationError("Missing --transaction-id")
    client = build_mercury_client(ctx)
    obj = client.get_json(f"/transaction/{transaction_id}")
    out = {"ok": True, "transaction": obj}
    ctx["audit"].write("transactions.get", {"transaction_id": transaction_id})
    ctx["out"].emit(out)
    return 0


def cmd_list_treasury(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    client = build_mercury_client(ctx)
    obj = client.get_json("/treasury")
    out = {"ok": True, "treasury": obj}
    ctx["audit"].write("treasury.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_list_treasury_transactions(args: Any, ctx: dict[str, Any]) -> int:
    treasury_id = str(getattr(args, "treasury_id", "") or "").strip()
    if not treasury_id:
        raise ValidationError("Missing --treasury-id")
    params = _clean_params(
        {
            "limit": getattr(args, "limit", None),
            "order": getattr(args, "order", None),
            "cursor": getattr(args, "cursor", None),
        }
    )
    client = build_mercury_client(ctx)
    obj = client.get_json(f"/treasury/{treasury_id}/transactions", params=params)
    out = {"ok": True, "treasury_id": treasury_id, "response": obj}
    ctx["audit"].write("treasury.transactions.list", {"treasury_id": treasury_id, "params": params})
    ctx["out"].emit(out)
    return 0


def cmd_list_users(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    client = build_mercury_client(ctx)
    obj = client.get_json("/users")
    out = {"ok": True, "users": obj}
    ctx["audit"].write("users.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_get_user(args: Any, ctx: dict[str, Any]) -> int:
    user_id = str(getattr(args, "user_id", "") or "").strip()
    if not user_id:
        raise ValidationError("Missing --user-id")
    client = build_mercury_client(ctx)
    obj = client.get_json(f"/users/{user_id}")
    out = {"ok": True, "user": obj}
    ctx["audit"].write("users.get", {"user_id": user_id})
    ctx["out"].emit(out)
    return 0


def cmd_list_categories(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    client = build_mercury_client(ctx)
    obj = client.get_json("/categories")
    out = {"ok": True, "categories": obj}
    ctx["audit"].write("categories.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_list_credit(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    client = build_mercury_client(ctx)
    obj = client.get_json("/credit")
    out = {"ok": True, "credit": obj}
    ctx["audit"].write("credit.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_list_events(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    client = build_mercury_client(ctx)
    obj = client.get_json("/events")
    out = {"ok": True, "events": obj}
    ctx["audit"].write("events.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_get_event(args: Any, ctx: dict[str, Any]) -> int:
    event_id = str(getattr(args, "event_id", "") or "").strip()
    if not event_id:
        raise ValidationError("Missing --event-id")
    client = build_mercury_client(ctx)
    obj = client.get_json(f"/events/{event_id}")
    out = {"ok": True, "event": obj}
    ctx["audit"].write("events.get", {"event_id": event_id})
    ctx["out"].emit(out)
    return 0


def cmd_list_recipients(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    client = build_mercury_client(ctx)
    obj = client.get_json("/recipients")
    out = {"ok": True, "recipients": obj}
    ctx["audit"].write("recipients.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_get_recipient(args: Any, ctx: dict[str, Any]) -> int:
    recipient_id = str(getattr(args, "recipient_id", "") or "").strip()
    if not recipient_id:
        raise ValidationError("Missing --recipient-id")
    client = build_mercury_client(ctx)
    obj = client.get_json(f"/recipient/{recipient_id}")
    out = {"ok": True, "recipient": obj}
    ctx["audit"].write("recipients.get", {"recipient_id": recipient_id})
    ctx["out"].emit(out)
    return 0


def cmd_list_recipient_attachments(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    client = build_mercury_client(ctx)
    obj = client.get_json("/recipients/attachments")
    out = {"ok": True, "attachments": obj}
    ctx["audit"].write("recipients.attachments.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_get_send_money_approval_request(args: Any, ctx: dict[str, Any]) -> int:
    request_id = str(getattr(args, "request_id", "") or "").strip()
    if not request_id:
        raise ValidationError("Missing --request-id")
    client = build_mercury_client(ctx)
    obj = client.get_json(f"/request-send-money/{request_id}")
    out = {"ok": True, "approval_request": obj}
    ctx["audit"].write("send_money.approval_request.get", {"request_id": request_id})
    ctx["out"].emit(out)
    return 0


def cmd_list_customers(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    client = build_mercury_client(ctx)
    obj = client.get_json("/ar/customers")
    out = {"ok": True, "customers": obj}
    ctx["audit"].write("customers.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_get_customer(args: Any, ctx: dict[str, Any]) -> int:
    customer_id = str(getattr(args, "customer_id", "") or "").strip()
    if not customer_id:
        raise ValidationError("Missing --customer-id")
    client = build_mercury_client(ctx)
    obj = client.get_json(f"/ar/customers/{customer_id}")
    out = {"ok": True, "customer": obj}
    ctx["audit"].write("customers.get", {"customer_id": customer_id})
    ctx["out"].emit(out)
    return 0


def cmd_list_invoices(args: Any, ctx: dict[str, Any]) -> int:
    params = _clean_params(
        {
            "status": getattr(args, "status", None),
            "customerId": getattr(args, "customer_id", None),
            "limit": getattr(args, "limit", None),
            "startingAfter": getattr(args, "starting_after", None),
            "endingBefore": getattr(args, "ending_before", None),
            "search": getattr(args, "search", None),
        }
    )
    client = build_mercury_client(ctx)
    obj = client.get_json("/ar/invoices", params=params)
    out = {"ok": True, "response": obj}
    ctx["audit"].write("invoices.list", {"params": params})
    ctx["out"].emit(out)
    return 0


def cmd_get_invoice(args: Any, ctx: dict[str, Any]) -> int:
    invoice_id = str(getattr(args, "invoice_id", "") or "").strip()
    if not invoice_id:
        raise ValidationError("Missing --invoice-id")
    client = build_mercury_client(ctx)
    obj = client.get_json(f"/ar/invoices/{invoice_id}")
    out = {"ok": True, "invoice": obj}
    ctx["audit"].write("invoices.get", {"invoice_id": invoice_id})
    ctx["out"].emit(out)
    return 0


def cmd_list_invoice_attachments(args: Any, ctx: dict[str, Any]) -> int:
    invoice_id = str(getattr(args, "invoice_id", "") or "").strip()
    if not invoice_id:
        raise ValidationError("Missing --invoice-id")
    client = build_mercury_client(ctx)
    obj = client.get_json(f"/ar/invoices/{invoice_id}/attachments")
    out = {"ok": True, "invoice_id": invoice_id, "attachments": _redact_attachment_urls(obj)}
    ctx["audit"].write("invoices.attachments.list", {"invoice_id": invoice_id})
    ctx["out"].emit(out)
    return 0


def cmd_get_attachment(args: Any, ctx: dict[str, Any]) -> int:
    attachment_id = str(getattr(args, "attachment_id", "") or "").strip()
    if not attachment_id:
        raise ValidationError("Missing --attachment-id")
    client = build_mercury_client(ctx)
    obj = client.get_json(f"/ar/attachments/{attachment_id}")
    out = {"ok": True, "attachment": _redact_attachment_urls(obj)}
    ctx["audit"].write("invoices.attachment.get", {"attachment_id": attachment_id})
    ctx["out"].emit(out)
    return 0


def cmd_list_webhooks(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    client = build_mercury_client(ctx)
    obj = client.get_json("/webhooks")
    out = {"ok": True, "webhooks": obj}
    ctx["audit"].write("webhooks.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_get_webhook(args: Any, ctx: dict[str, Any]) -> int:
    webhook_endpoint_id = str(getattr(args, "webhook_endpoint_id", "") or "").strip()
    if not webhook_endpoint_id:
        raise ValidationError("Missing --webhook-endpoint-id")
    client = build_mercury_client(ctx)
    obj = client.get_json(f"/webhooks/{webhook_endpoint_id}")
    out = {"ok": True, "webhook": obj}
    ctx["audit"].write("webhooks.get", {"webhook_endpoint_id": webhook_endpoint_id})
    ctx["out"].emit(out)
    return 0


def cmd_list_books_journal_entries(args: Any, ctx: dict[str, Any]) -> int:
    books_id = str(getattr(args, "books_id", "") or "").strip()
    if not books_id:
        raise ValidationError("Missing --books-id")
    client = build_mercury_client(ctx)
    obj = client.get_json(f"/journal-entries/{books_id}")
    out = {"ok": True, "journal_entries": obj}
    ctx["audit"].write("books.journal_entries.list", {"books_id": books_id})
    ctx["out"].emit(out)
    return 0


def cmd_get_books_journal_entry(args: Any, ctx: dict[str, Any]) -> int:
    books_id = str(getattr(args, "books_id", "") or "").strip()
    teal_journal_entry_id = str(getattr(args, "teal_journal_entry_id", "") or "").strip()
    if not books_id:
        raise ValidationError("Missing --books-id")
    if not teal_journal_entry_id:
        raise ValidationError("Missing --teal-journal-entry-id")
    client = build_mercury_client(ctx)
    obj = client.get_json(f"/journal-entry/{books_id}/{teal_journal_entry_id}")
    out = {"ok": True, "journal_entry": obj}
    ctx["audit"].write(
        "books.journal_entry.get",
        {"books_id": books_id, "teal_journal_entry_id": teal_journal_entry_id},
    )
    ctx["out"].emit(out)
    return 0
