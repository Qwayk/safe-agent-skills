# Command reference

Use this page when you need the exact Zendesk command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `zendesk-api-tool onboarding [--no-write-env]`

## Auth

- `zendesk-api-tool --output json --version`
- `zendesk-api-tool auth check`
- `zendesk-api-tool --live auth check`
- `zendesk-api-tool auth token set --file token.json`
- `zendesk-api-tool auth token status`

## Jobs

- `zendesk-api-tool jobs run --file jobs.csv [--limit N] [--plan-out plan.json]`
- `zendesk-api-tool --apply --yes --plan-in plan.json jobs run --file jobs.csv` requires explicit no-snapshot approval for write rows when no saved snapshot is available.

## API (explicit per-operation commands)

This tool pins the official Zendesk Ticketing OpenAPI snapshot and exposes one explicit command per operation:
- `zendesk-api-tool api <operation> [flags...]`

By default, `api` commands are **plan-first** (dry-run, no network). To execute:
- Add `--live` for reads
- Write commands are plan-first. With `--live --apply`, required gates, and `--plan-in`, they require explicit no-snapshot approval before Zendesk HTTP when no saved snapshot is available.
- plans are proof-first: always review them, and do not expect live writes yet

Recovery behavior is explicit:
- no automatic rollback
- no snapshots
- no backups
- if a restore action is available, use that restore command in a later explicit command

Tip: open the canonical list:
- `docs/official_commands_ticketing_2026-03-05.txt`

## Runs (history)

Write-capable commands automatically save proof artifacts under `.state/runs/` and append an index row to `.state/runs/index.jsonl`.

These live next to your `--env-file` (usually next to your `.env` file), so they’re easy to find.

Optional flags:
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `zendesk-api-tool runs list [--limit 20]`
- `zendesk-api-tool runs show --run-id 2026-01-19T104512Z_a3f91c`

## Demo (plan/refusal workflow examples)

- `zendesk-api-tool demo read`
- `zendesk-api-tool demo write --selector demo-resource [--plan-out plan.json]`
- `zendesk-api-tool --apply --plan-in plan.json demo write --selector demo-resource` returns a safe refusal.
