# How this skill stays safe

This skill covers a broad X API v2 surface, so safety here means keeping every live action explicit, reviewable, and honest about its limits.

## What safety means here

- Live reads need explicit `--live`.
- Write-capable actions start as dry-run plans by default.
- When no useful before-state exists, applies need explicit `--ack-no-snapshot`.
- DELETE actions also need `--ack-irreversible`.
- The tool refuses when the auth mode is unsupported or the request is too risky for the current path.
- Secrets stay redacted in plans, receipts, logs, and errors.

## Explicit operation safety

The tool exposes one explicit CLI command per `operationId` from the pinned X API v2 snapshot.

That means:

- GET and HEAD calls stay plan-only unless you add `--live`
- non-GET calls stay plan-only unless you add the required apply flags
- DELETE calls need the same write approval plus `--ack-irreversible`
- the agent can show you the exact operation inventory with `x-api-tool api ops list`

## DM safety rules

Bulk DMs are high-risk, so this tool blocks them unless:

- every row includes intent evidence
- an opt-out line is provided
- recipients already present in the local opt-out ledger are excluded

The local opt-out ledger lives under `.state/dm_opt_out.json` next to your `--env-file`.
Manage it with `x-api-tool dm opt-out add` and `x-api-tool dm opt-out list`.

## Plan, review, apply, receipt

The recommended write flow is:

1. Build the dry-run plan first.
2. Review the target, auth mode, payload, and risk.
3. Apply only with the required approval flags.
4. Review the receipt and any available provider response.

Useful file outputs:

- `--plan-out <path>` saves the dry-run plan
- `--plan-in <path>` applies from a reviewed plan
- `--receipt-out <path>` saves the apply receipt

## Local run history

Write-capable commands can save local proof under:

- `.state/runs/<run_id>/`
- `.state/runs/index.jsonl`

Those files stay local and must never contain secrets.

## Honest limits

- Most current X write paths do not have automatic rollback.
- Demo writes and `jobs write.ping` stay template-only and refuse instead of pretending to write.
- DM reachability depends on recipient settings and your sender account status.
- Some X endpoints still depend on the right scopes, app review, or product access outside this repo.
