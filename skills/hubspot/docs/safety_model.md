# Safety model

This tool uses a simple safety model.

## Core rules

- Read commands run normally.
- Write commands run as dry-run plans by default.
- Live write apply currently requires explicit no-snapshot approval before any HubSpot HTTP request when command-specific before-state capture is not available.
- Add `--yes` for batch or risky write actions.
- Add `--ack-irreversible` for actions marked as irreversible.
- This tool does not use snapshots, provider backups, or automatic rollback.
- Never print secrets.

## Safe workflow for writes

1. Run a plan without `--apply`.
2. Review `plan` output.
3. Check `before_state.required: true` and `before_state.supported: false`.
4. Treat the plan as review-first. Current `--apply` attempts require explicit no-snapshot approval before HubSpot HTTP when no saved snapshot is available; approved supported writes produce receipts with recovery limits.
5. Keep the run summary and audit log as proof of the plan or refusal.

## Run proof storage

- `.state/runs/<run_id>/plan.json` (optional)
- `.state/runs/<run_id>/receipt.json` is not written for current HubSpot write refusals.
- `.state/runs/<run_id>/summary.md`
- `.state/runs/<run_id>/audit.jsonl`
- `.state/runs/index.jsonl` (history index)

## Risk level guidance

- Read only: low risk
- One-off writes: medium risk
- Batch/replace/archive/delete: high risk

The tool flags high-risk paths with stronger requirements in `docs/api_coverage.md`.
