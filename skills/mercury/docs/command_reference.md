# Command reference

Use this page when you need the exact Mercury command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `mercury-api-tool onboarding [--no-write-env]`

## Auth

- `mercury-api-tool --output json --version`
- `mercury-api-tool auth check`

## Read-only API commands (GET-only)

- `mercury-api-tool organization get`
- `mercury-api-tool accounts list`
- `mercury-api-tool accounts get --account-id ...`
- `mercury-api-tool accounts cards --account-id ...`
- `mercury-api-tool accounts statements --account-id ...`
- `mercury-api-tool accounts transactions --account-id ... [--start ... --end ... --limit N --offset N]`
- `mercury-api-tool accounts transaction --account-id ... --transaction-id ...`
- `mercury-api-tool transactions list [--status ... --account-id ... --start ... --end ... --limit N]`
- `mercury-api-tool transactions get --transaction-id ...`
- `mercury-api-tool treasury list`
- `mercury-api-tool treasury transactions --treasury-id ... [--cursor N --limit N]`
- `mercury-api-tool users list`
- `mercury-api-tool users get --user-id ...`
- `mercury-api-tool categories list`
- `mercury-api-tool credit list`
- `mercury-api-tool events list`
- `mercury-api-tool events get --event-id ...`
- `mercury-api-tool recipients list`
- `mercury-api-tool recipients get --recipient-id ...`
- `mercury-api-tool recipients attachments`
- `mercury-api-tool send-money approval-request --request-id ...`
- `mercury-api-tool customers list`
- `mercury-api-tool customers get --customer-id ...`
- `mercury-api-tool invoices list [--status ... --customer-id ... --limit N]`
- `mercury-api-tool invoices get --invoice-id ...`
- `mercury-api-tool invoices attachments --invoice-id ...`
- `mercury-api-tool invoices attachment --attachment-id ...`
- `mercury-api-tool webhooks list`
- `mercury-api-tool webhooks get --webhook-endpoint-id ...`
- `mercury-api-tool books journal-entries --books-id ...`
- `mercury-api-tool books journal-entry --books-id ... --teal-journal-entry-id ...`

## Exports and downloads (local file writes)

All local file writes are gated behind `--apply` (and `--yes` for overwrite).

- `mercury-api-tool export transactions --format json|csv --out ... [--max-pages N]`
- `mercury-api-tool invoices download-pdf --invoice-id ... --out ...`
- `mercury-api-tool invoices download-attachment --attachment-id ... [--out ...]`
- `mercury-api-tool statements download-pdf --statement-id ... --out ...`

## Reports (read-only)

- `mercury-api-tool report transactions-summary [--max-pages N]`

## Runs (history)

Write-capable commands automatically save proof artifacts under `.state/runs/` and append an index row to `.state/runs/index.jsonl`.

These live next to your `--env-file` (usually next to your `.env` file), so they’re easy to find.

Note:
- Read-only API commands (GET-only) do not create run folders.
- Exports/downloads (local file writes) create run folders in dry-run/apply/refusal paths.

Optional flags:
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `mercury-api-tool runs list [--limit 20]`
- `mercury-api-tool runs show --run-id 2026-01-19T104512Z_a3f91c`
