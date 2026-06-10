# Command reference

Use this page when you need the exact TikTok Marketing command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Global flags

```bash
tiktok-marketing-api-tool --help
```

Global flags include:

- `--version`
- `--config`
- `--project-dir`
- `--env-file`
- `--timeout-s`
- `--live`
- `--verbose`
- `--debug`
- `--output {json,text}`
- `--log-file`
- `--apply`
- `--yes`
- `--plan-out`
- `--plan-in`
- `--receipt-out`
- `--ack-irreversible`
- `--run-id`
- `--artifacts-dir`
- `--no-artifacts`

## Onboarding

- `tiktok-marketing-api-tool --output json onboarding [--no-write-env]`

## Auth

- `tiktok-marketing-api-tool --output json auth check`
- `tiktok-marketing-api-tool --output json auth token set --file token.json`
- `tiktok-marketing-api-tool --output json auth token status`

## API operations

- `tiktok-marketing-api-tool --output json api ops list [--method GET] [--family campaign]`
- `tiktok-marketing-api-tool --output json api ops show --op oauth2-advertiser-get`
- `tiktok-marketing-api-tool --output json api ad-get --query-json path/to/query.json`
- `tiktok-marketing-api-tool --output json --live api ad-get --query-json path/to/query.json`
- `tiktok-marketing-api-tool --output json --live --apply --yes --plan-in plan.json --ack-irreversible api ad-create --query-json path/to/query.json --body-json path/to/body.json`

When a write command cannot save before-state, it must disclose the no-snapshot limit and require explicit no-snapshot approval before applying. Successful receipts must record the approval and recovery limit.

All operation commands from the pinned manifest are registered under `api`.
See `docs/api_coverage.md` for the full 240-command ledger.

## Runs (local history)

- `tiktok-marketing-api-tool --output json runs list [--limit 20]`
- `tiktok-marketing-api-tool --output json runs show --run-id 2026-01-19T104512Z_a3f91c`
