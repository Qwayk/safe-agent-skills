# Command reference

These commands cover GA4 properties, reports, metadata, events, and write-like admin methods. Confirm the property before using report or admin commands.

For the guided path, start with [What you can do with Google Analytics](use_cases.md), [Connect your Google Analytics access](onboarding.md), and [Quickstart](quickstart.md).

## Global flags

- `--env-file PATH` (default: `.env`)
- `--output json|text` (default: `json`)
- `--verbose` (HTTP timing to stderr; never prints headers)
- `--debug` (stack traces on errors)
- `--apply` (request apply; write-like methods require explicit no-snapshot approval before GA4 HTTP when no saved snapshot is available)
- `--yes` (extra confirmation for high-risk/batch)
- `--ack-irreversible` (extra confirmation for deletes)
- `--plan-out PATH` (write plan JSON)
- `--plan-in PATH` (apply from a reviewed plan; required for high/irreversible)
- `--receipt-out PATH` (write approved apply receipts; missing-approval refusals do not write it)
- `--fields VALUE` (Google system parameter)
- `--quota-user VALUE` (Google system parameter)

For write-capable commands, the dry-run plan includes a no-recovery contract and a no-snapshot disclosure when needed:
- `recovery.automatic_rollback: false`
- `recovery.snapshots: []`
- `recovery.backups: []`
- `recovery.rollback_plan: null`
- `before_state.required: true`
- `before_state.supported: false`

## Onboarding

- `ga4-api-tool onboarding [--no-write-env]`

## Auth

- `ga4-api-tool --output json --version`
- `ga4-api-tool auth check` (local-only summary; no network)
- `ga4-api-tool --apply auth check` (refresh token / validate creds; network)
- `ga4-api-tool auth token set --file token.json` (writes `.state/token.json`; never prints token values)
- `ga4-api-tool auth token status`

## Runs (history; local)

- `ga4-api-tool runs list [--limit 20]`
- `ga4-api-tool runs show --run-id <id>`

## Jobs (template batch runner)

- `ga4-api-tool jobs run --file jobs.csv [--limit N]`

## GA4 discovery methods (explicit commands)

The canonical full list is committed in `docs/official_commands.txt`.

Command shape:
- `ga4-api-tool admin v1alpha <resource chain> <method> [flags...]`
- `ga4-api-tool data v1beta <resource chain> <method> [flags...]`
- `ga4-api-tool data v1alpha <resource chain> <method> [flags...]`

Examples:
- `ga4-api-tool admin v1alpha accounts list`
- `ga4-api-tool data v1beta properties run-report --property properties/123`

Write plans for GA4 writes do not promise built-in rollback, snapshots, or backups. Current write apply requires explicit no-snapshot approval before GA4 HTTP until before-state capture exists.
