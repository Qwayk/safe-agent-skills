# Safety model

This page explains the simple safety promise for this tool.
It is built to check a public page and stay out of private account actions.

This tool is read-only:
- It only performs `GET` requests to public Status API endpoints.
- It does not implement `--apply/--yes` or plan/receipt flows.

## Output contract

- `--output json` prints exactly one JSON object to stdout.
- Errors are rendered as JSON with `ok=false` and an `error_type`.
