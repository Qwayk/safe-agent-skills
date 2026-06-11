# Safety model

Rules:
- Dry-run by default; live API write attempts need `--live --apply`.
- API write attempts without saved before-state or provider backup use `before_state.status="no_snapshot_available"` and require explicit no-snapshot approval; missing approval refuses before provider HTTP.
- Refuse when unclear; do not guess.
- Never log secrets.

## Two-layer safety

There are two safety layers:

1) Mechanical checks (the tool)
- The tool checks required inputs before execution.
- For writes, missing no-snapshot approval stops before provider HTTP and marks verification as `blocked_before_apply`; approved no-snapshot writes may proceed through the normal apply path.

2) Human or AI review
- A reviewer checks that the planned change matches the goal and context.
- Keep this as a normal step before `--apply`.

The tool is deterministic; reviewers are still needed.

## Plan -> Review -> Refusal

Recommended flow for writes:

1) Build a plan (dry-run).
2) Review the plan.
3) Attempt apply with `--live --apply` and required safety flags for API writes.
4) Confirm the explicit no-snapshot approval and that the receipt records no-snapshot approval, or missing approval refused before provider HTTP.

## Plans and receipts

For API write commands this tool writes plan files when enabled:

- `--plan-out <path>`: save dry-run plan JSON
- `--receipt-out <path>`: reserved for receipts from approved applies; missing-approval write refusals must not write it unless apply is approved

Saved-plan apply is not supported in this release.
Local auth storage helpers write local state directly and do not use plan or receipt files.

## Run history (recommended for customer-ready tools)

For write-capable commands, this tool writes run artifacts:

- `.state/runs/<run_id>/`
- `.state/runs/index.jsonl`

Run artifacts stay next to your `--env-file`.

Rules:
- The tool must never write secrets into local artifacts.
- Plans and refusal outputs are proof for review and audits.

## Rollback model

- Current Bluesky write families should be treated as `irreversible_and_clearly_labeled`.
- This tool does not create rollback helpers, backups, snapshots, or provider restore flows.
- If a write apply is refused, confirm no provider HTTP happened and the receipt records no-snapshot approval, or missing approval refused before provider HTTP.

## Risk levels (guideline)

- Low: create new drafts, small edits.
- Medium: edit an existing draft.
- High: status changes, deletions, and multi-step updates.
- Irreversible: actions that cannot be undone.

High/irreversible actions should need explicit safety flags.

For irreversible actions, the tool uses:
- `--ack-irreversible`
