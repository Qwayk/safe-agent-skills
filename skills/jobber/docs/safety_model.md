# Safety model

This page explains how the skill helps you move carefully: look first, think second, and change last.

It means plain reads are run early, plans are built for every write, and live writes only happen after your explicit confirm step.

## Before-state behavior

This tool does not capture automatic before-state snapshots before mutation execution.

- Every write plan includes `snapshot_status: "No snapshot available"`.
- Plans and receipts include recovery notes that say no useful before-state was saved.
- Recovery may be manual or impossible for some change paths.
- There is no automatic rollback promise for no-snapshot operations.

## What safe use looks like

- Reads can help you understand account state.
- Writes start as a plan and never execute live by default.
- Write execution needs `--apply --yes --plan-in <reviewed-plan.json>`.
- Jobs with write rows also require `--apply --yes --plan-in <reviewed-plan.json>` to run live.
- High-risk write operations also need `--ack-no-snapshot` before live apply.
- Irreversible mutations additionally need `--ack-irreversible`.
- Receipts and plans are emitted for review before and after change.
- Secrets never appear in plans, receipts, or logs.

## Why some operations are slower

Some operations are low risk and some are high risk. The CLI keeps a safer path for both:

- Unknown or missing settings are refused before execution.
- High-risk names and write commands stay in plan mode until approved.
- Batches with mixed actions are reviewed row by row and stop on the first error.

## Normal flow

1. Confirm connectivity with `auth check`.
2. Review `read` output to validate scope and assumptions.
3. Create a write plan using the command plus args.
4. Save and review `--plan-out`.
5. Apply only with `--apply --yes --plan-in <reviewed-plan.json>`.
6. Keep `--receipt-out` for audit review.

## Plans, receipts, and runs

Plans contain:
- Target operation
- Argument hash
- Proposed selection
- GraphQL document hash
- Jobber endpoint fingerprint
- Verification notes

Receipts contain:
- Applied result payload
- Verification status
- Runtime metadata
- Where proof files were written
- `snapshot_status` and recovery notes

Run records are tracked in `.state/runs/` and show what command was run, when, and whether it was dry-run, apply, or refused.

## Common safety rules

- Raw GraphQL bridge commands are not supported.
- OAuth settings and refresh are required for long-running token workflows.
- Webhook helpers are local verifiers; signature checks are explicit and secret-based.
- There is no automatic rollback path in this tool.
