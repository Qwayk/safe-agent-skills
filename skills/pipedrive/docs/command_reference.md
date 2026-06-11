# Command reference

Use this page when you need the exact Pipedrive command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Global command

- `--env-file <path>`
- `--output <json|text>`
- `--version`
- `--timeout-s <seconds>`
- `--verbose`
- `--debug` (prints stack traces to stderr on errors)
- `--log-file <path>` (writes redacted JSONL audit rows)
- `--config <path>` (JSON defaults for `base_url`, `api_domain`, `timeout_s`)

## Tool setup

- `qwayk-pipedrive-safe-agent-cli onboarding`
- `qwayk-pipedrive-safe-agent-cli auth check`

## Read commands

Commands follow the pattern:

- `qwayk-pipedrive-safe-agent-cli <group> <action> [flags...]`

All read commands in this tool come from `docs/api_coverage.md` and are shipped as `GET` methods.

Examples:

- `qwayk-pipedrive-safe-agent-cli users get-current`
- `qwayk-pipedrive-safe-agent-cli deals list --limit 5`
- `qwayk-pipedrive-safe-agent-cli goals search --type-name deals_won`
- `qwayk-pipedrive-safe-agent-cli files download --id 12345`

Notes:
- `files download` returns metadata only and does not download binary content.
- Unsupported actions are not shown as commands.
- Direct CLI parser errors return validation errors.
- If no shipped read command matches a request, a wrapper should say that clearly instead of inventing a command.
- `excluded by choice: read-only tool` applies only to documented excluded endpoints in `docs/api_coverage.md` or wrapper-level policy handling.
- For the full shipped surface, use `docs/api_coverage.md`.
