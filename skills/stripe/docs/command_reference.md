# Command reference

Use this page when you need the exact Stripe command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `stripe-api-tool onboarding [--no-write-env]`

## Auth

- `stripe-api-tool --output json --version`
- `stripe-api-tool auth check`
- `stripe-api-tool auth token set --file token.json`
- `stripe-api-tool auth token status`

## Jobs

- `stripe-api-tool jobs run --file examples/jobs.csv [--limit N] [--plan-out plan.json]`
- `stripe-api-tool --apply --yes --plan-in plan.json jobs run --file examples/jobs.csv`

## Runs (history)

Write-capable commands automatically save proof artifacts under `.state/runs/` and append an index row to `.state/runs/index.jsonl`.

These live next to your `--env-file` (usually next to your `.env` file), so they’re easy to find.

Optional flags:
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `stripe-api-tool runs list [--limit 20]`
- `stripe-api-tool runs show --run-id 2026-01-19T104512Z_a3f91c`

## Demo (plan/receipt workflow examples)

- `stripe-api-tool demo read`
- `stripe-api-tool demo write --selector demo-resource [--plan-out plan.json]`
- `stripe-api-tool --apply --plan-in plan.json --receipt-out receipt.json demo write --selector demo-resource`

## Inventory (pinned OpenAPI; offline)

These commands prove what “100% coverage” means for this tool:

- `stripe-api-tool inventory operations list`
- `stripe-api-tool inventory operations validate`
- `stripe-api-tool inventory commands list`
- `stripe-api-tool inventory commands validate`
- `stripe-api-tool inventory validate`

Maintainers only (rewrite the committed inventories):
- `stripe-api-tool inventory operations write`
- `stripe-api-tool inventory commands write`

## API (explicit per-operation commands)

Shape:
- `stripe-api-tool api <operation-command> [--path-flags...] [--query k=v] [--expand field] [--data k=v] [--upload field=path]`

Notes:
- Every operation from the pinned OpenAPI snapshot is registered as a named subcommand under `api`.
- Path params are explicit required flags (example: `--customer cus_...`).
- `--query` is repeatable and uses `k=v` strings.
- `--expand` is repeatable and is serialized as `expand[]` query params.
- `--data` is repeatable and is sent as Stripe's default form-encoded body.
- `--upload` is repeatable and sends multipart form data (for file upload endpoints).

Execution:
- Default is plan-only output (no network calls).
- Add `--live` to execute read-only API calls.
- Write-like API commands still require `--apply` and their risk gates, but live apply requires explicit no-snapshot approval before Stripe HTTP when no saved snapshot or provider backup is available.
- API write plans include `before_state` and `rollback` blocks that state no before-state snapshot and no automatic rollback are available.
