# Safety model

Use this page when you want the exact safety rules behind the Klaviyo skill.

## Core rules

- Dry-run by default.
- Real calls need `--live`.
- Reads can run live with `--live`.
- Writes also need `--apply`.
- High-impact writes also need `--plan-in` and `--yes`.
- Current Klaviyo write families do not save before-state snapshots, so approved live writes also need `--ack-no-snapshot`.
- No secrets are printed in output, audit logs, or artifacts.
- Plans always include `plan.no_recovery`.
- Write plans mark `before_state.required: true` and `before_state.supported: false`.
- No automatic rollback is available for writes. There are no snapshots, no provider backups, and no automatic restore in this tool.

## Safe operation flow

1. Build the plan first.
2. Review the plan output and proof artifacts.
3. Confirm the recovery limit when no useful before-state can be saved.
4. Apply only after the required gates are present.
5. Store the plan, receipt or refusal summary, and proof artifacts.

## Gate names used for every write

- `live`
- `apply`
- `plan_in` (high impact only)
- `yes` (high impact only)

## High-impact classification

Operations with path, command, or tags matching any of these
keywords are treated as high impact:

- `delete`, `bulk`, `send`, `cancel`, `suppress`, `unsubscribe`, `request_profile_deletion`
- `relationship` and `relationships`

These require `--yes` and `--plan-in` when running with `--live --apply`.

## Run history

For write-capable commands, local run artifacts can include:

- `plan.json`
- `receipt.json` is written for approved supported writes; refusals for missing approval or failed safety checks do not write it
- `audit.jsonl`
- `summary.md`

Artifacts are stored under a run folder and are safe by design: no keys or tokens.

## No-recovery contract

- `plan.no_recovery` is explicit in plan output for API calls.
- Approved supported writes output receipts; real blockers output safe refusals.
- Recovery is manual and comes from re-planning or manual fix actions only.
