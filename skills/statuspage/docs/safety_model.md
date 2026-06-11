# Safety model

This page explains the simple safety promise for this skill.
It is built to check a public page and stay out of private account actions.

This skill is read-only:

- It only performs `GET` requests to public Statuspage API endpoints.
- It does not sign in or call private admin actions.
- It does not implement `--apply`, `--yes`, or plan/receipt flows because there are no writes here.
- The main safety question is whether you pointed the agent at the right public page, not whether a risky change might run.

## Output contract

- `--output json` prints exactly one JSON object to stdout.
- Errors are rendered as JSON with `ok=false` and an `error_type`.
