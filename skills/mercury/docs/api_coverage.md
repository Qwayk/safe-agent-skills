# API coverage (endpoints → CLI)

Purpose:
- Make “all capabilities” measurable (no guessing about what’s implemented).
- Give the Manager a single source of truth for review/approval.
- Help customers quickly see what the tool can and cannot do.

Rules:
- Keep this table honest. If something is missing, list it as missing.
- If behavior differs from the provider docs, note it and link `docs/references.md`.

## Summary

- Provider: Mercury
- API base URL (prod): `https://api.mercury.com/api/v1`
- API base URL (sandbox): `https://api-sandbox.mercury.com/api/v1`
- Auth method: API token via `Authorization: Bearer <token>` (default) or HTTP Basic (token as username, empty password)
- Last audited (UTC): 2026-01-29
- GET endpoint count: 33

## Endpoint coverage

Columns:
- Endpoint
- Capability
- CLI command(s)
- Safety gates (dry-run/apply/yes)
- Tests/examples
- Notes

| Endpoint | Capability | CLI command(s) | Safety gates | Tests/examples | Notes |
|---|---|---|---|---|---|
| `GET /accounts` | Get all accounts | `mercury-api-tool --output json accounts list` | Read-only | `tests/test_get_only_enforcement.py` | |
| `GET /account/{accountId}` | Get account by id | `mercury-api-tool --output json accounts get --account-id ...` | Read-only | `tests/test_cli_json_parse_errors.py` | |
| `GET /account/{accountId}/cards` | Get cards for account | `mercury-api-tool --output json accounts cards --account-id ...` | Read-only | `docs/command_reference.md` | |
| `GET /account/{accountId}/statements` | Get account statements | `mercury-api-tool --output json accounts statements --account-id ...` | Read-only | `docs/command_reference.md` | |
| `GET /account/{accountId}/transactions` | List account transactions | `mercury-api-tool --output json accounts transactions --account-id ...` | Read-only | `docs/command_reference.md` | Offset paging supported via `--offset` |
| `GET /account/{accountId}/transaction/{transactionId}` | Get transaction by id (account-scoped) | `mercury-api-tool --output json accounts transaction --account-id ... --transaction-id ...` | Read-only | `docs/command_reference.md` | |
| `GET /transactions` | List all transactions | `mercury-api-tool --output json transactions list` | Read-only | `docs/command_reference.md` | Page cursor supported via `page.nextPage` → `--start-after` |
| `GET /transaction/{transactionId}` | Get a transaction by ID | `mercury-api-tool --output json transactions get --transaction-id ...` | Read-only | `docs/command_reference.md` | |
| `GET /treasury` | Get all treasury accounts | `mercury-api-tool --output json treasury list` | Read-only | `docs/command_reference.md` | |
| `GET /treasury/{treasuryId}/transactions` | Get treasury transactions | `mercury-api-tool --output json treasury transactions --treasury-id ...` | Read-only | `docs/command_reference.md` | Cursor paging supported via `--cursor` |
| `GET /users` | Get all users | `mercury-api-tool --output json users list` | Read-only | `docs/command_reference.md` | |
| `GET /users/{userId}` | Get user by id | `mercury-api-tool --output json users get --user-id ...` | Read-only | `docs/command_reference.md` | |
| `GET /organization` | Get organization information | `mercury-api-tool --output json organization get` | Read-only | `docs/command_reference.md` | Used for `auth check` |
| `GET /categories` | List all categories | `mercury-api-tool --output json categories list` | Read-only | `docs/command_reference.md` | |
| `GET /credit` | List all credit accounts | `mercury-api-tool --output json credit list` | Read-only | `docs/command_reference.md` | |
| `GET /events` | Get all events | `mercury-api-tool --output json events list` | Read-only | `docs/command_reference.md` | |
| `GET /events/{eventId}` | Get event by id | `mercury-api-tool --output json events get --event-id ...` | Read-only | `docs/command_reference.md` | |
| `GET /recipients` | Get all recipients | `mercury-api-tool --output json recipients list` | Read-only | `docs/command_reference.md` | |
| `GET /recipient/{recipientId}` | Get recipient by id | `mercury-api-tool --output json recipients get --recipient-id ...` | Read-only | `docs/command_reference.md` | |
| `GET /recipients/attachments` | List all recipient attachments | `mercury-api-tool --output json recipients attachments` | Read-only | `docs/command_reference.md` | |
| `GET /request-send-money/{requestId}` | Get send money approval request by id | `mercury-api-tool --output json send-money approval-request --request-id ...` | Read-only | `docs/command_reference.md` | |
| `GET /ar/customers` | List all customers | `mercury-api-tool --output json customers list` | Read-only | `docs/command_reference.md` | |
| `GET /ar/customers/{customerId}` | Get a customer | `mercury-api-tool --output json customers get --customer-id ...` | Read-only | `docs/command_reference.md` | |
| `GET /ar/invoices` | List all invoices | `mercury-api-tool --output json invoices list` | Read-only | `docs/command_reference.md` | |
| `GET /ar/invoices/{invoiceId}` | Get an invoice | `mercury-api-tool --output json invoices get --invoice-id ...` | Read-only | `docs/command_reference.md` | |
| `GET /ar/invoices/{invoiceId}/attachments` | List invoice attachments | `mercury-api-tool --output json invoices attachments --invoice-id ...` | Read-only | `docs/command_reference.md` | |
| `GET /ar/attachments/{attachmentId}` | Get an attachment (metadata; signed URL redacted) | `mercury-api-tool --output json invoices attachment --attachment-id ...`<br>`mercury-api-tool --output json --apply [--yes] invoices download-attachment --attachment-id ... [--out ...]` | Read-only for metadata; local write requires `--apply`; overwrite requires `--yes` | `tests/test_signed_url_redaction.py`, `tests/test_file_write_gates.py` | Download uses the signed URL from this endpoint (URL redacted in JSON output) |
| `GET /ar/invoices/{invoiceId}/pdf` | Download invoice PDF | `mercury-api-tool --output json --apply [--yes] invoices download-pdf --invoice-id ...` | Local write requires `--apply`; overwrite requires `--yes` | `tests/test_file_write_gates.py` | Writes local PDF |
| `GET /statements/{statementId}/pdf` | Download account statement PDF | `mercury-api-tool --output json --apply [--yes] statements download-pdf --statement-id ...` | Local write requires `--apply`; overwrite requires `--yes` | `tests/test_file_write_gates.py` | Writes local PDF |
| `GET /webhooks` | Get webhook endpoints | `mercury-api-tool --output json webhooks list` | Read-only | `docs/command_reference.md` | |
| `GET /webhooks/{webhookEndpointId}` | Get webhook endpoint by id | `mercury-api-tool --output json webhooks get --webhook-endpoint-id ...` | Read-only | `docs/command_reference.md` | |
| `GET /journal-entries/{booksId}` | List all journal entries | `mercury-api-tool --output json books journal-entries --books-id ...` | Read-only | `docs/command_reference.md` | |
| `GET /journal-entry/{booksId}/{tealJournalEntryId}` | Retrieve a Journal Entry | `mercury-api-tool --output json books journal-entry --books-id ... --teal-journal-entry-id ...` | Read-only | `docs/command_reference.md` | |

## Read-only exports (non-API writes)

| Export | Capability | CLI command(s) | Safety gates | Tests/examples | Notes |
|---|---|---|---|---|---|
| Transactions export | Export `/transactions` into JSON/CSV for reporting | `mercury-api-tool --output json --apply [--yes] export transactions --format json|csv --out ...` | Local write requires `--apply`; overwrite requires `--yes` | `tests/test_file_write_gates.py` | Paginates via `page.nextPage` (bounded by `--max-pages`) |

## Read-only reports

| Report | Capability | CLI command(s) | Safety gates | Tests/examples | Notes |
|---|---|---|---|---|---|
| Transactions summary | Summarize `/transactions` (count + totals by kind/category) | `mercury-api-tool --output json report transactions-summary [--max-pages N]` | Read-only | `docs/command_reference.md` | Computes locally from paginated `GET /transactions` results |

## Out of scope (non-GET endpoints refused by design)

This tool intentionally does not implement any non-GET Mercury API endpoints. From the v1 OpenAPI spec:

- `POST /account/{accountId}/request-send-money`
- `POST /account/{accountId}/transactions`
- `POST /ar/customers`
- `POST /ar/customers/{customerId}`
- `DELETE /ar/customers/{customerId}`
- `POST /ar/invoices`
- `POST /ar/invoices/{invoiceId}`
- `POST /ar/invoices/{invoiceId}/cancel`
- `POST /journal-entries/{booksId}`
- `PUT /journal-entries/{booksId}`
- `DELETE /journal-entries/{booksId}`
- `POST /recipient/{recipientId}`
- `POST /recipient/{recipientId}/attachments`
- `POST /recipients`
- `PATCH /transaction/{transactionId}`
- `POST /transaction/{transactionId}/attachments`
- `POST /transfer`
- `POST /webhooks`
- `POST /webhooks/{webhookEndpointId}`
- `POST /webhooks/{webhookEndpointId}/verify`
- `DELETE /webhooks/{webhookEndpointId}`

## Known gaps (explicit)

- None (GET coverage is 100% as-of 2026-01-29).
