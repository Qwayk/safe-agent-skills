# Command reference

Use this page when you need the exact Klaviyo command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `klaviyo-safe-agent-cli onboarding [--no-write-env]`

## Auth

- `klaviyo-safe-agent-cli auth check`

## API operation discovery

- `klaviyo-safe-agent-cli api ops list [--method GET|POST|PATCH|DELETE] [--tag <tag>]`
- `klaviyo-safe-agent-cli api ops show --op <operation_command>`

## API operations (all 308 stable commands)

Each stable operation is a direct subcommand:

- `klaviyo-safe-agent-cli api <operation_command> [--path|--query|--body-json|--file ...]`

`--path` and `--query` take `key=value` pairs and can be repeated.
`--path-json` and `--query-json` accept JSON objects or file paths to JSON objects.
`--body-json` accepts a JSON object or file path for request body.

`--file field=path` is used for multipart upload operations.

## Safety and run flags for API operations

- `--live` is required before any real HTTP call.
- Reads can run live with `--live`.
- `--apply` is required for writes, but current write apply attempts require explicit no-snapshot approval before Klaviyo HTTP when no saved snapshot is available.
- High-impact write operations also require `--plan-in` and `--yes`.
- Plan-first and proof-first: create plan output with `--plan-out` first, review it, and do not expect live writes yet.
- This tool does not create snapshots, provider backups, or automatic rollback for writes.
- Dry-run plans include `before_state` and `plan.no_recovery`.

## Runs (history)

- `klaviyo-safe-agent-cli runs list [--limit 20]`
- `klaviyo-safe-agent-cli runs show --run-id <id>`
- `--run-id <id>`: set a specific run id.
- `--artifacts-dir <path>`: override run artifacts directory.
- `--no-artifacts`: disable artifact writing.
