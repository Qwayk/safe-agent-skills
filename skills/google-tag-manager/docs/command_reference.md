# Command reference

Use this page when you need the exact Google Tag Manager command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Global flags (all commands)

- `--version`: print tool version and exit
- `--config <path>`: load optional non-secret project defaults
- `--project-dir <path>`: project directory for optional defaults
- `--env-file <path>`: load secrets from env file (default: `.env`)
- `--timeout-s <seconds>`: override request timeout
- `--verbose`: verbose HTTP logging to stderr
- `--debug`: show Python stack traces on unexpected errors
- `--output json|text`: output format (default: `json`)
- `--log-file <path>`: write JSONL audit log
- `--apply`: apply writes (default is dry-run for writes)
- `--yes`: required for high-risk and irreversible writes
- `--plan-out <path>`: write plan JSON
- `--plan-in <path>`: use plan JSON for apply
- `--receipt-out <path>`: write receipt JSON
- `--ack-irreversible`: required for irreversible writes
- `--run-id <id>`: custom run id
- `--artifacts-dir <path>`: override run artifact directory
- `--no-artifacts`: disable run artifacts

## Onboarding

- `gtm-api-tool onboarding [--no-write-env]`

## Auth

- `gtm-api-tool --output json --version`
- `gtm-api-tool --env-file .env auth check`

## Runs (history)

Write-capable runs can write files in `.state/runs/<run_id>/` and add rows to `.state/runs/index.jsonl`.

- `gtm-api-tool runs list [--limit 20]`
- `gtm-api-tool runs show --run-id <run-id>`

## Method commands from discovery

- Canonical command list:
  - `docs/official_methods_v2.txt`
  - `docs/official_commands_v2.txt`

Discovery method IDs map to nested commands.

- `tagmanager.accounts.containers.workspaces.tags.create`
- `gtm-api-tool accounts containers workspaces tags create`

### Method flags

- Path params become required CLI flags.
  - `{+path}` => `--path`
  - `{+parent}` => `--parent`
- Query params become optional CLI flags.
- Write commands require exactly one request-body input:
  - `--body-json '{"name":".."}'`
  - `--body-file ./body.json`

System query params:
- `--fields`
- `--quota-user`
- `--pretty-print`

### Examples

Read:
- `gtm-api-tool --env-file .env accounts list --fields "account(name,path)"`

Write (dry-run plan):
- `gtm-api-tool --env-file .env --plan-out plan.json accounts containers workspaces create --parent "accounts/0000000000/containers/0000000000" --body-json '{"name":"Example Workspace"}'`
- For supported methods (update/delete/publish/set_latest), dry-run also reads the current live target first and writes it to `before_state.json` in the run artifacts directory when enabled.
- Some mutating families have no safe `GET` pre-read path. These are dry-run reviewable, and live apply requires explicit no-snapshot approval.

Write (apply from plan):
- `gtm-api-tool --env-file .env --apply --plan-in plan.json --receipt-out receipt.json accounts containers workspaces create --parent "accounts/0000000000/containers/0000000000" --body-json '{"name":"Example Workspace"}'`
- For supported methods (update/delete/publish/set_latest), apply output keeps the same `before_state` evidence in the receipt and the run artifacts directory.
- For families without safe pre-state read, live apply requires explicit no-snapshot approval after the required write flags are set.

High/irreversible write:
- `gtm-api-tool --env-file .env --plan-out delete.plan.json accounts containers delete --path "accounts/0000000000/containers/0000000000"`
- `gtm-api-tool --env-file .env --apply --plan-in delete.plan.json --yes --ack-irreversible --receipt-out delete.receipt.json accounts containers delete --path "accounts/0000000000/containers/0000000000"`

Run-review points:
- Risk and recovery are separate.
- Recovery is shown as `rollback_by_inverse_action` or `irreversible_and_clearly_labeled`.
- If recovery is `rollback_by_inverse_action`, review `recovery.strategy`, `recovery.rollback_ready`, and `recovery.rollback_plan` before apply.
