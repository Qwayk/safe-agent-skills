# Architecture

## Runtime shape

- `cli.py`: top-level flags, subcommands, local run context, and error handling
- `config.py`: Cloudinary `.env` parsing, host defaults, auth-header building, and base URL routing
- `inventory.py`: loads the generated Cloudinary allowlist JSON and exposes `OperationSpec`
- `commands/operations.py`: discovery command handlers and operation list/show views
- `commands/operation_runner.py`: resolves params, builds plans, runs reads, and refuses writes before Cloudinary HTTP when no saved snapshot is available
- `http.py`: thin `requests` wrapper with optional verbose timing
- `runs.py`: `.state/runs/` artifacts and index helpers
- `audit_log.py`: JSONL audit trail with redaction

## Active CLI surface

The shipped command surface is limited to:
- `onboarding`
- `auth check`
- `runs list`
- `runs show`
- `operations list`
- `operations show`
- `operations <area> <op_key>`

## Generated allowlist

The CLI parser is built from `docs/_generated/cloudinary_rest_inventory.json`.
That file also drives `docs/api_coverage.md`.
When Cloudinary coverage changes, regenerate both in one run.

## Auth routing

- product v1 base: upload and admin
- product video v2 base: live streaming, player profiles, video config
- product analysis v2 base: analyze
- account provisioning base: provisioning
- account root base: permissions
- public permissions endpoints: no credentials
