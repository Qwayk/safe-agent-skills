# Safety model

Rules:
- Dry-run by default.
- Real calls need `--live`.
- Reads can run live with `--live`.
- Writes also need `--apply`, then require explicit no-snapshot approval before Klaviyo HTTP when safe before-state capture is not available.
- High-impact writes also need `--plan-in` and `--yes`, then still require explicit no-snapshot approval before Klaviyo HTTP.
- No secrets in output, audit logs, or artifacts.
- Plans always include `plan.no_recovery`.
- Write plans include `before_state.required: true` and `before_state.supported: false` when safe saved snapshot support is not available.
- No automatic rollback is available for writes; there are no snapshots, no provider backups, and no automatic restore in this tool.

## Safe operation flow

1) Build plan first (default)
2) Review plan output and proof artifacts
3) Require explicit no-snapshot approval when no useful before-state can be saved
4) Apply approved supported writes, or refuse only for a real blocker such as missing approval, unclear target, missing credentials, or failed safety checks
5) Store the plan, receipt or refusal summary, and proof artifacts

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
