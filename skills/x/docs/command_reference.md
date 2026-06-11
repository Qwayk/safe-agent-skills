# Command reference

Use this page when you need the exact X command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `x-api-tool onboarding [--no-write-env]`

## Auth

- `x-api-tool --output json --version`
- `x-api-tool auth check`
- `x-api-tool --live auth check` (optional live read: validates OAuth user token by calling `GET /2/users/me`)
- `x-api-tool auth token set --file token.json` (plan-only by default; apply with `--apply --yes --ack-no-snapshot`)
- `x-api-tool auth token status`
- `x-api-tool auth pkce start` (plan-only by default; apply with `--apply --yes --ack-no-snapshot`)
- `x-api-tool auth pkce finish --redirect-url '<paste redirect url here>'` (apply with `--apply --yes --ack-no-snapshot`)

## OpenAPI operations (explicit)

- `x-api-tool api ops list [--tag <tag>] [--security-scheme <scheme>]`
- `x-api-tool api <operationId> [--auth auto|app|user|none] [--path k=v] [--query k=v] [--body-json '{...}']`
- `x-api-tool --live api <operationId> ...` (GET/HEAD live)
- `x-api-tool --apply --yes --ack-no-snapshot api <operationId> ...` (write apply when no saved snapshot is available)
- `x-api-tool --apply --yes --ack-no-snapshot --ack-irreversible api <operationId> ...` (DELETE apply when no saved snapshot is available)

## Users

- `x-api-tool users resolve --username <name>`
- `x-api-tool --live users resolve --username <name> [--include-receives-your-dm]`

## DMs

- `x-api-tool --live dm can-send --to-username <name>`
  - Returns a simple yes/no style result for “does this user receive DMs from *your sender account* right now?”
- `x-api-tool dm send --to-user-id <id> --message 'hi' [--plan-out plan.json]`
- `x-api-tool --apply --yes --ack-no-snapshot dm send --to-user-id <id> --message 'hi'`
- `x-api-tool dm opt-out add --recipient <name-or-id> [--reason '...']`
- `x-api-tool dm opt-out list`
- `x-api-tool dm bulk-send --csv job.csv --opt-out-line 'Reply STOP to opt out.' [--plan-out plan.json]`
- `x-api-tool --apply --yes --ack-no-snapshot --plan-in plan.json dm bulk-send --csv job.csv --opt-out-line 'Reply STOP to opt out.' --min-delay-s 1.0`
  - `--min-delay-s` is used only after the required approvals and policy checks pass.

## Jobs

- `x-api-tool jobs run --file jobs.csv [--limit N] [--plan-out plan.json]`
- `x-api-tool --apply --yes --plan-in plan.json jobs run --file jobs.csv` (`write.ping` is template-only and refuses instead of pretending to write)

## Runs (history)

Write-capable commands automatically save proof artifacts under `.state/runs/` and append an index row to `.state/runs/index.jsonl`.

These live next to your `--env-file` (usually next to your `.env` file), so they’re easy to find.

Optional flags:
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `x-api-tool runs list [--limit 20]`
- `x-api-tool runs show --run-id 2026-01-19T104512Z_a3f91c`

## Demo (plan/refusal workflow examples)

- `x-api-tool demo read`
- `x-api-tool demo write --selector demo-resource [--plan-out plan.json]`
- `x-api-tool --apply --yes --plan-in plan.json --receipt-out receipt.json demo write --selector demo-resource` (template-only; refuses instead of pretending to write)
