# Command reference

Use this page when you need the exact Bluesky command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Global behavior

- Command name: `bluesky-safe-cli`
- Output defaults to JSON unless you set `--output text`.
- API calls are dry-run plans by default.
- Use `--live` only when you want real execution.

## Safety gates

- `auth` and `onboarding` run quick checks.
- API operations are explicit subcommands:
  - read ops: `bluesky-safe-cli api <operation_command> --live` (no `--apply`)
  - write ops: `bluesky-safe-cli --live --apply api <operation_command> ...`
  - risky write ops: add `--yes`
  - irreversible write ops: add `--yes --ack-irreversible`
- There is no `--plan-in` flag in this tool.
- When a write command cannot save before-state, it must disclose the no-snapshot limit and require explicit no-snapshot approval before applying. Successful receipts must record the approval and recovery limit.

## Onboarding

- `bluesky-safe-cli onboarding [--no-write-env]`
- `bluesky-safe-cli --output json onboarding`

## Auth

- `bluesky-safe-cli --output json auth check`
- `bluesky-safe-cli --output json auth login`
- `bluesky-safe-cli --output json auth refresh`
- `bluesky-safe-cli --output json auth logout`
- `bluesky-safe-cli --output json auth token set --file token.json`
- `bluesky-safe-cli --output json auth token status`

## API inventory

- `bluesky-safe-cli api ops list [--method GET|POST|WS] [--namespace app.bsky|com.atproto|chat.bsky|tools.ozone] [--kind query|procedure|subscription] [--docs-source http-reference|lexicon-only] [--stability stable|unspecced|temp|active-development]`
- `bluesky-safe-cli api <operation_command> [--query-json '{"key":"value"}'] [--body-json '{"key":"value"}'] [--query key=value --query ...] [--body key=value --body ...]`

Common shared API flags:
- `--live`
- `--apply`
- `--plan-out path`
- `--receipt-out path`
- `--service-url override`
- `--query-json`, `--body-json`
- `--query`, `--body`
- `--input-file`, `--input-content-type`
- `--event-limit` and `--idle-timeout-s` for subscription commands

Examples:

```bash
bluesky-safe-cli api ops list --kind query --docs-source http-reference
bluesky-safe-cli api app-bsky-actor-get-profile --query-json '{"actor":"alice.bsky.social"}'
bluesky-safe-cli --live api app-bsky-actor-get-profile --query-json '{"actor":"alice.bsky.social"}'
bluesky-safe-cli --live --apply api com-atproto-repo-create-record --body-json '{"repo":"did:plc:...", "collection":"app.bsky.feed.post", "record":{"$type":"app.bsky.feed.post","text":"Hello"}}'
```

## Runs

- `bluesky-safe-cli runs list [--limit 20]`
- `bluesky-safe-cli runs show --run-id 2026-01-19T104512Z_a3f91c`
