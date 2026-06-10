# Command reference

Use this page when you need the exact LinkedIn Ads command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `linkedin-ads-api-tool onboarding`  
  - Creates `.env` with placeholders when missing.
  - Writes comments and keys for local setup.

## Authentication

- `linkedin-ads-api-tool auth check`
  - Safe live check with `GET /adAccountUsers?q=authenticatedUser`.
- `linkedin-ads-api-tool auth token set --file token.json`
  - Save token from OAuth JSON.
- `linkedin-ads-api-tool auth token status`
  - Show token file status only (no token value).

- `linkedin-ads-api-tool --output json --version`
  - Show tool version in JSON output mode.

## Operations by family

Command shape:
`linkedin-ads-api-tool [global flags] <family> <operation> [options]`

Global flags such as `--output json`, `--plan-out`, `--plan-in`, and `--receipt-out`
must come before the family name.

Examples:
- `linkedin-ads-api-tool ad-account-users list-authenticated-user`
- `linkedin-ads-api-tool ad-campaigns search --ad-account-id 123456`
  - `linkedin-ads-api-tool ad-campaigns create --ad-account-id 123 --body-json '{"name":"Sample campaign"}'`

### Shared operation flags

- `--param key=value` (repeatable)
  - Adds extra query parameters.
- `--body-json '<json>'` and `--body-file path`
  - Attach request body for non-GET methods.
- `--apply`
  - Confirm the current safety gates for commands marked `write-apply` and `write-apply-yes`; current writes then require explicit no-snapshot approval before LinkedIn HTTP.
- `--ack-irreversible`
  - Required for every live LinkedIn write because this runtime does not provide snapshot restore.
- `--yes`
  - Required for `write-apply-yes` operations (delete, batch-write, permission changes).
- `--plan-out path` and `--plan-in path`
  - Save and validate saved plans before the current refusal.
- `--receipt-out path`
  - Reserved for future live receipts after saved snapshot support is available.
- `--output json`
  - Machine-readable output.
- `--verbose`
  - Show request line and timing details on stderr.

Path placeholders from the API path are required CLI flags automatically:
- `/adAccounts/{ad_account_id}/...` becomes `--ad-account-id`.

## Run history

- `linkedin-ads-api-tool runs list [--limit N]`
- `linkedin-ads-api-tool runs show --run-id <id>`

- `--run-id`
  - Set a custom run ID.
- `--artifacts-dir`
  - Override artifact directory for one run.

Write-capable commands that support it store run artifacts in `.state/runs/<run_id>/` and
append records to `.state/runs/index.jsonl`.
