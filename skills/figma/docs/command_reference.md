# Command reference

Use [Quickstart](quickstart.md) to open a file or preview a comment. See [Connect Figma](onboarding.md) for settings and permissions.

## Global flags

- `--version`: print the tool version and exit.
- `--config PATH`: load optional non-secret project defaults JSON.
- `--project-dir PATH`: override the project directory used for local state resolution.
- `--env-file PATH`: point to a specific env file.
- `--timeout-s N` overrides the profile check timeout in seconds. Set `FIGMA_TIMEOUT_S` for operation requests.
- `--output json|text` (default: json).
- `--verbose`: print HTTP timing details to stderr.
- `--debug`: include stack traces on failures.
- `--log-file PATH`: write audit events to a JSONL file.
- `--apply`, `--yes`, `--ack-irreversible`: apply and confirmation controls for writes.
- `--ack-no-snapshot`: approve a reviewed write when no saved snapshot is available.
- `--plan-out PATH` saves the preview. `--plan-in PATH` loads the reviewed plan for a write. `--receipt-out PATH` saves the result.
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

- Use the named options shown by `operations show` or the command's `--help`.
- Required path parameters appear as `--<path-param>` flags, for example `--file-key`.
- Optional query parameters appear as `--<query-param>` flags, for example `--ids`, `--user-id`.
- `--version` is a global flag, so `version` is exposed as `--version-id`.
- `--body-json-file PATH` is required for write operations that accept a body.
- `--out PATH` writes the response body. For image renders, it saves the JSON with temporary links. The command's result lists which node IDs got links and which failed.
- `--overwrite` replaces existing `--out` files.

Read operations run when requested. Writes preview by default and need a matching saved plan, approval, and the flags in [Approve and check changes](safety_model.md).

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
- Save a comment preview
  `figma-safe-agent-cli --plan-out comment-plan.json operations comments post-comment --file-key YOUR_FILE_KEY --body-json-file body.json`
- Post the approved comment
  `figma-safe-agent-cli --plan-in comment-plan.json --apply --yes --ack-no-snapshot --receipt-out comment-receipt.json operations comments post-comment --file-key YOUR_FILE_KEY --body-json-file body.json`

## Where commands are defined

In `src/figma_safe_agent_cli/`, `operation_specs.py` lists the named API operations. `cli.py` builds their options. `commands/operations.py` prepares requests, checks plans, and reads the results. Settings come from `config.py` and requests go through `http.py`. `runs.py` and `audit_log.py` handle saved runs and logs. JSON mode returns one result object.
