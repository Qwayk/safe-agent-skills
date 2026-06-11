# Command reference

Use this page when you need the exact Figma command, flag, or safety rule.
This is the technical reference for the skill.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Global flags

- `--version`: print the tool version and exit.
- `--config PATH`: load optional non-secret project defaults JSON.
- `--project-dir PATH`: override the project directory used for local state resolution.
- `--env-file PATH`: point to a specific env file.
- `--timeout-s N`: override the request timeout in seconds.
- `--output json|text` (default: json).
- `--verbose`: print HTTP timing details to stderr.
- `--debug`: include stack traces on failures.
- `--log-file PATH`: write audit events to a JSONL file.
- `--apply`, `--yes`, `--ack-irreversible`: apply and confirmation controls for writes.
- `--ack-no-snapshot`: approve a reviewed write when no saved snapshot is available.
- `--plan-out PATH`, `--plan-in PATH`, `--receipt-out PATH`.
- `--run-id ID`: attach a specific run id to this execution.
- `--artifacts-dir PATH`: override the local artifacts folder for this run.
- `--no-artifacts`: skip writing local run artifacts.

## Core commands

- `onboarding [--no-write-env]`
- `auth check [--skip-live]`
- `auth token set --file PATH`
- `auth token status`
- `runs list [--limit N]`
- `runs show --run-id <run-id>`
- `operations list [--area <area>] [--method GET|POST|PUT|DELETE] [--contains TEXT] [--include-writes]`
- `operations show <area> <op_key>`
- `operations <area> <op_key> [--named-flags ...]`

`auth check --skip-live` is useful when you want to confirm token discovery without calling `GET /v1/me`.

## `operations <area> <op_key>` flags

This is not a generic request bridge.

- There is no generic path/query wrapper flag.
- Use one explicit path/query flag per operation parameter, from the operation spec.
- Required path parameters appear as `--<path-param>` flags, for example `--file-key`.
- Optional query parameters appear as `--<query-param>` flags, for example `--ids`, `--user-id`.
- `--version` is a global flag, so `version` is exposed as `--version-id`.
- `--body-json-file PATH` is required for write operations that accept a body.
- `--out PATH` writes the response JSON (or raw body for non-JSON responses)
- `--overwrite` replaces existing `--out` files.

Read operations execute immediately.
Write operations stay in dry-run mode unless you add `--apply`, and irreversible writes also require `--ack-irreversible`. When no saved snapshot is available, current write applies then require explicit `--ack-no-snapshot` approval before Figma token use or provider HTTP.

## Example commands

- List available file operations:
  `figma-safe-agent-cli operations list --area files`
- Read one file:
  `figma-safe-agent-cli operations files get-file --file-key YOUR_FILE_KEY --version-id YOUR_VERSION_ID`
- Discovery window (read):
  `figma-safe-agent-cli operations discovery get-discovery --start-date 2026-01-01`
- Payment lookup by token:
  `figma-safe-agent-cli operations payments get-payments-by-plugin-payment-token --plugin-payment-token ...`
- Check auth config without live probe:
  `figma-safe-agent-cli auth check --skip-live`
- Safe write preview:
  `figma-safe-agent-cli operations comments post-comment --file-key YOUR_FILE_KEY --body-json-file body.json`
- Safe write apply:
  `figma-safe-agent-cli --apply --yes --ack-no-snapshot operations comments post-comment --file-key YOUR_FILE_KEY --body-json-file body.json`
  Current result after review: the tool may send the Figma write and can save a receipt.
