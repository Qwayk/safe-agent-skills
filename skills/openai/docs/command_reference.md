# Command reference

Use this page when you need the exact OpenAI command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `openai-api-tool onboarding [--no-write-env]`

## Auth

- `openai-api-tool --output json --version`
- `openai-api-tool auth check`
- `openai-api-tool --output json auth check` (plan-only; add `--live` to call `/models` and emit `live_checked`, `live_ok`, and `live_status_code` for proof-of-key).

## API operations

- `openai-api-tool api ops list [--tag TAG]`
- `openai-api-tool api <operation_command> [--path-json PATH_JSON] [--query-json QUERY_JSON] [--body-json BODY_JSON] [--path field=value ...] [--query field=value ...] [--file field=/path]`

  Shared flags:

  - `--live`: allow real HTTP calls (all commands are plan-only by default)
  - `--apply`: attempt a write after review; writes require explicit no-snapshot approval before OpenAI HTTP when no saved snapshot is available
  - `--plan-out <file>` / `--plan-in <file>`: store or re-use deterministic plans (spend-money writes require `--plan-in`)
  - `--yes`: additional confirmation for high-risk/batch writes; spend-money operations need `--yes` plus `--plan-in`
  - `--receipt-out <file>`: capture a receipt when an approved supported command really runs; refusals for missing approval or failed safety checks do not create write receipts
  - `--ack-spend-money`: required for inference, embeddings, images/audio generation, fine-tunes, batches, moderations, etc.; spend-money operations demand `--live --apply --plan-in <plan.json> --yes --ack-spend-money`
  - `--ack-irreversible`: required for delete-like operations (combined with `--live --apply --plan-in <plan.json> --yes`)
  - `before_state` in current write plans is explicit: `required: true`, `supported: false`, `status: no_snapshot_available`.
  - `recovery` in write plans is explicit: `automatic_rollback: false`, `backups: []`, `snapshots: []`, `rollback_plan: null` (no automatic rollback).

Plans, read receipts, and refusal outputs are sanitized before they hit stdout or disk so Authorization headers, API keys, and tokens never leak, while plan hashes still let you detect drift.

## Jobs

- `openai-api-tool jobs run --file jobs.csv [--limit N] [--plan-out plan.json]`
- `openai-api-tool --apply --yes --plan-in plan.json jobs run --file jobs.csv` (currently requires explicit no-snapshot approval before write rows execute)

## Runs (history)

Write-capable commands automatically save proof artifacts under `.state/runs/` and append an index row to `.state/runs/index.jsonl`.

These live next to your `--env-file` (usually next to your `.env` file), so they’re easy to find.

Optional flags:

- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `openai-api-tool runs list [--limit 20]`
- `openai-api-tool runs show --run-id 2026-01-19T104512Z_a3f91c`

## Demo

- `openai-api-tool demo read`
- `openai-api-tool demo write --selector demo-resource [--plan-out plan.json]`
- `openai-api-tool --apply --plan-in plan.json --receipt-out receipt.json demo write --selector demo-resource` (currently requires explicit no-snapshot approval before stub receipt output)
