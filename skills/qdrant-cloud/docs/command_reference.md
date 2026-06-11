# Command reference

Use this page when you need the exact Qdrant Cloud command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do with Qdrant Cloud](use_cases.md), [Connect your Qdrant Cloud account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `qdrant-cloud-api-tool onboarding [--no-write-env]`

## Auth

- `qdrant-cloud-api-tool --output json --version`
- `qdrant-cloud-api-tool --output json auth check` (offline OK)
- `qdrant-cloud-api-tool --output json --live auth check` (validates credentials against the API)

## Qdrant Cloud API operations (explicit)

Every official RPC has a first-class command.
The canonical list is committed at `docs/official_commands_v1.txt`.

Common patterns:

- Read:
  - `qdrant-cloud-api-tool --output json --live account-v1 list-accounts`
- Read with path parameters:
  - `qdrant-cloud-api-tool --output json --live account-v1 get-account --account-id <id>`
- Write plan (dry-run; no network):
  - `qdrant-cloud-api-tool --output json account-v1 create-account --request-json request.json --plan-out plan.json`
- Ordinary write apply request (currently requires explicit no-snapshot approval before Qdrant Cloud HTTP when no saved snapshot is available):
  - `qdrant-cloud-api-tool --output json --live --apply account-v1 create-account --request-json request.json --plan-out plan.json --receipt-out receipt.json`
- Write plans include `safety.before_state` and `safety.recovery.contract`:
  - `no-recovery` for ordinary writes; current apply requires explicit no-snapshot approval before provider HTTP when no saved snapshot is available
  - `provider-backup-restore` for explicit `create-backup`, `restore-backup`, and `create-cluster-from-backup` workflows
- `no-recovery` means the tool does not offer implicit rollback. Current ordinary apply requires explicit no-snapshot approval when no operation-specific snapshot or provider backup is available.
- Provider-backup plan example:
  - `qdrant-cloud-api-tool --output json cluster-backup-v1 restore-backup --account-id <account-id> --backup-id <backup-id> --request-json request.json --plan-out plan.json`
- Provider-backup apply example:
  - `qdrant-cloud-api-tool --output json --live --apply cluster-backup-v1 restore-backup --account-id <account-id> --backup-id <backup-id> --request-json request.json --receipt-out receipt.json`
- Irreversible apply (DELETE):
  - `qdrant-cloud-api-tool --output json --live --apply --yes --ack-irreversible --plan-in plan.json account-v1 delete-account --account-id <id>`
- Money-moving/billing apply:
  - `qdrant-cloud-api-tool --output json --live --apply --yes --ack-spend-money --plan-in plan.json payment-v1 <command> ...`

Notes:
- For GET operations, `--request-json` is interpreted as query parameters.
- For non-GET operations, `--request-json` is interpreted as the JSON body.

## Runs (history)

Write-capable commands automatically save proof artifacts under `.state/runs/` and append an index row to `.state/runs/index.jsonl`.

These live next to your `--env-file` (usually next to your `.env` file), so they’re easy to find.

Optional flags:
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `qdrant-cloud-api-tool runs list [--limit 20]`
- `qdrant-cloud-api-tool runs show --run-id <run_id>`
