# Safety model

## Core safety rules

- Dry-run by default.
- All API calls start from a plan.
- Read-like operations (`GET`, `HEAD`) run only with `--live`.
- Write-like operations (`POST`, `PUT`, `PATCH`, `DELETE`) are plan-first and refuse execution unless all required flags are present:
  - `--live`
  - `--apply`
  - `--plan-in`
  - `--yes`
  - `--ack-irreversible`
- After those gates pass, API writes without saved before-state or provider backup require explicit no-snapshot approval and record `before_state.status="no_snapshot_available"`.
- Never send secrets in output.

## Refusal and failure behavior

- If required inputs are missing, the tool returns `refused` with clear reasons.
- Missing tokens or missing required fields fail before live reads. writes require explicit no-snapshot approval before provider HTTP.
- Apply paths require environment fingerprint and plan consistency checks.

## Verification

Write verification checks the receipt for recorded no-snapshot approval or confirms a missing-approval refusal.

- Missing-approval write refusals include `verification_plan.status="blocked_before_apply"`.
- A successful write receipt must not be emitted while before-state support is missing.
- If a command adds explicit read-back later, docs should be updated for that command.

## Rollback model

- Current TikTok Marketing write families should be treated as `irreversible_and_clearly_labeled`.
- The tool saves plans, refusal outputs, and run history for review, but it does not create rollback helpers, backups, snapshots, or provider restore flows.
- If a write apply is refused, confirm no provider HTTP happened and the receipt records no-snapshot approval, or missing approval refused before provider HTTP.

## Runs and audit artifacts

Run artifacts are real behavior for write-capable commands:

- `.state/runs/<run_id>/`
- `.state/runs/index.jsonl`

Set `--no-artifacts` to disable writing these files.

## Plan and receipt files

- `--plan-out <path>` writes a review plan.
- `--plan-in <path>` is required for write apply attempts.
- `--receipt-out <path>` is for approved write receipts; missing-approval refusals do not write it.

Plans and refusal outputs are redacted and must not include secret values.
