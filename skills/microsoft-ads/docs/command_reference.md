# Command reference

Use this page when you need the exact Microsoft Ads command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `msads-api-tool onboarding [--no-write-env]`

## Auth

- `msads-api-tool --output json --version`
- `msads-api-tool auth check` (offline local checks only)
- `msads-api-tool --live auth check` (live SOAP call; read-only)
- `msads-api-tool auth token set --file token.json`
- `msads-api-tool auth token show` (redacted)
- `msads-api-tool auth token status`
- `msads-api-tool --live auth token refresh` (updates `.state/token.json`; never prints token values)

## Microsoft Ads v13 operations (explicit commands)

All audited v13 operations are available as explicit commands:
- `msads-api-tool <service> <operation-kebab> [--request-json request.json]`
For live reads, add `--live`. Writes still require `--apply`, then require explicit no-snapshot approval before SOAP HTTP until before-state capture support exists.

Services:
- `campaign-management`
- `bulk`
- `reporting`
- `ad-insight`
- `customer-management`

Full mapping (source of truth):
- `docs/api_coverage.md`

## Jobs

- `msads-api-tool jobs run --file jobs.csv [--limit N] [--plan-out plan.json]`
- `msads-api-tool --apply --yes --plan-in plan.json jobs run --file jobs.csv` requires explicit no-snapshot approval for write actions and records it in approved receipts.

## Runs (history)

Write-capable commands automatically save proof artifacts under `.state/runs/` and append an index row to `.state/runs/index.jsonl`.

These live next to your `--env-file` (usually next to your `.env` file), so they’re easy to find.

Optional flags:
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `msads-api-tool runs list [--limit 20]`
- `msads-api-tool runs show --run-id 2026-01-19T104512Z_a3f91c`

## Demo (plan and approval workflow examples)

- `msads-api-tool demo read`
- `msads-api-tool demo write --selector demo-resource [--plan-out plan.json]`
- `msads-api-tool --apply --plan-in plan.json demo write --selector demo-resource` requires explicit no-snapshot approval and records it in approved receipts.
