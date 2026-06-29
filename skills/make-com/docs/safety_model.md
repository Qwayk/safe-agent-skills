# Safety model

## Core rule

All read calls are direct, but all writes are review-first.

## API auth

- Token authentication is used.
- Token header: `Authorization: Token <value>`.
- Base URL is made safe against the Make zones and is always sent under `/api/v2`.
- Write plans include a one-way credential fingerprint. Apply refuses if the current Make credential does not match the reviewed plan.

## What counts as write

Any operation from the inventory with non-`GET` style HTTP intent is treated as write-capable. For write commands:

1. A first call without `--apply` creates a plan.
2. The tool does not mutate state until `--apply` is used.
3. The apply step requires the reviewed plan file and confirmation flags.

## Required flags for writes

- `--plan-in` must point to the reviewed plan JSON.
- `--apply` is required to execute.
- `--yes` is required for confirmation.
- `--ack-no-snapshot` is required when the operation is marked `no_snapshot` in inventory.
- `--ack-irreversible` is required for destructive operations.

## What happens if checks are missed

The command returns a clear safety refusal and makes no change.

## Audit safety

- Plans and receipts are JSON and can be stored in artifacts.
- Logs redact known secret fields.
- Receipt includes `plan` details, verification status, and snapshot warning when applicable.
- Stored command text redacts inline `--body-json` values, `--body-file` paths, and secret-looking `--path-param` / `--query` values before the command is saved in plans, receipts, run summaries, run indexes, or audit logs.
- Plan target records redact secret-looking path and query values. Exact apply validation uses non-secret target fingerprints instead of storing those raw values.
- Receipt response URLs redact secret-looking path and query values before they are saved.
- HTTP verbose output, request exception text, HTTP error text, and provider error bodies are redacted before they reach stderr, stdout, audit logs, run summaries, or run indexes.
