# Command reference

Exact CLI commands and arguments supported by this tool.

## Global flags

- `--version`
- `--env-file <path>` (default `.env`)
- `--output {json,text}` (default `json`)
- `--verbose`

## `onboarding`

```bash
giantpanda onboarding
```

Creates `.env` from `.env.example` when missing.

## `auth check`

```bash
giantpanda auth check
```

Local token readiness check, no network call.

## `domains stats`

```bash
giantpanda domains stats --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--page N] [--page-size N]
```

- `--start-date` and `--end-date` are required and strict format.
- optional pagination flags are positive integers.

## `domains add`

Dry-run (default):

```bash
giantpanda domains add --domain <name> [--domain <name>...] [--plan-out <path>]
```

Apply:

```bash
giantpanda domains add --apply --plan-in <path> --approve-plan <plan_id> --ack-no-snapshot --domain <name> [--domain <name>...] [--receipt-out <path>]
```

- `--dry-run` is optional and explicit.
- `--apply` and `--dry-run` are mutually exclusive.
- `--apply` requires all write gates in one command:
  - `--plan-in <path>`
  - `--approve-plan <plan_id>`
  - `--ack-no-snapshot`
- `--receipt-out` is optional.
