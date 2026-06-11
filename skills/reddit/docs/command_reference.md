# Command reference

Use this page when you need the exact Reddit command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `qwayk-reddit-safe-agent-cli onboarding [--no-write-env]`

## Auth

- `qwayk-reddit-safe-agent-cli auth check`
- `qwayk-reddit-safe-agent-cli --live auth check`
- `qwayk-reddit-safe-agent-cli auth login [--duration permanent|temporary] [--scopes "identity read"]`
- `qwayk-reddit-safe-agent-cli --live auth exchange-code --redirect-url 'http://127.0.0.1:8080/callback?...'`
- `qwayk-reddit-safe-agent-cli --live auth exchange-code --code <code> --state <state>`
- `qwayk-reddit-safe-agent-cli --live auth refresh`
- `qwayk-reddit-safe-agent-cli auth token set --file token.json`
- `qwayk-reddit-safe-agent-cli auth token status`

## API inventory

- `qwayk-reddit-safe-agent-cli api ops list`
- `qwayk-reddit-safe-agent-cli api ops list --section account`
- `qwayk-reddit-safe-agent-cli api ops list --method POST --scope submit`

## API operations

Every pinned Reddit operation is exposed as:

- `qwayk-reddit-safe-agent-cli api <operation_command>`

Shared flags:

- `--path-json <json-or-file>`
- `--query-json <json-or-file>`
- `--body-json <json-or-file>`
- `--path key=value`
- `--query key=value`
- `--body key=value`
- `--file field=/path/to/file`
- `--body-format form|json`

Read examples:

- `qwayk-reddit-safe-agent-cli --live api get-api-v1-me`
- `qwayk-reddit-safe-agent-cli --live api get-top --path subreddit=python --query limit=10`

Write examples:

- `qwayk-reddit-safe-agent-cli api post-api-vote --body id=t3_abc123 --body dir=1 --plan-out vote-plan.json`
- `qwayk-reddit-safe-agent-cli --live --apply --plan-in vote-plan.json --yes api post-api-vote --body id=t3_abc123 --body dir=1`
- `qwayk-reddit-safe-agent-cli api delete-api-filter-filterpath --path filterpath=example --plan-out delete-plan.json`
- `qwayk-reddit-safe-agent-cli --live --apply --plan-in delete-plan.json --yes --ack-irreversible api delete-api-filter-filterpath --path filterpath=example`

When a write command cannot save before-state, it must disclose the no-snapshot limit and require explicit no-snapshot approval before applying. Successful receipts must record the approval and recovery limit.

## Runs

Write-capable commands save local proof under `.state/runs/`.

- `qwayk-reddit-safe-agent-cli runs list [--limit 20]`
- `qwayk-reddit-safe-agent-cli runs show --run-id <run_id>`

## Template helpers

These generic helpers still exist, but they are not part of Reddit API coverage:

- `qwayk-reddit-safe-agent-cli jobs run --file jobs.csv`
- `qwayk-reddit-safe-agent-cli demo read`
- `qwayk-reddit-safe-agent-cli demo write --selector demo-resource`
