# Safety model

Rules:
- Keep the shipped surface honest about what the official Sovrn APIs really support.
- Never flatten the real auth split into one fake credential model.
- Never log secrets.
- Refuse when unsure; do not guess.

## What safety means in this tool today

Right now the official command surface is read-only. Safety mostly means:

- the command names match official Sovrn endpoints
- the auth rules match the official docs
- output and audit logs redact keys
- browser-only JavaScript docs and MCP beta docs are not over-claimed as shipped CLI coverage

## Read-only proof

For the current read-only commands, the main proof loop is:

1. Confirm local config with `auth check`.
2. Run a real endpoint command.
3. Inspect the returned JSON plus the official coverage ledger.
4. Save redacted examples in committed docs when they become stable.

## Future write-capable rule

If official write-capable Sovrn endpoints are ever added later, the tool must return to the normal repo pattern:

1. Dry-run by default.
2. Require explicit apply flags.
3. Verify after the change.
4. Save plans and receipts without secrets.

## Run history

The local run-history helpers remain in place for future write-capable additions:

- `.state/runs/<run_id>/`
- `.state/runs/index.jsonl`

These are for local audit and future proof work. Read-only commands do not create new run folders right now.
