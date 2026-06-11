# Safety model

Rules:
- No network by default; add `--live` to allow any real HTTP request.
- Dry-run by default; ordinary writes produce plans and then require explicit no-snapshot approval before Qdrant Cloud HTTP.
- Provider backup/restore commands can apply live after the normal gates because they are explicit recovery workflows.
- Refuse when unsure; do not guess.
- Higher-risk writes require `--yes` and additional acknowledgements.
- Never log secrets.

## Two-layer safety (recommended)

There are two kinds of safety:

1) Mechanical correctness (the tool)
- Plans show the request, risk gates, recovery contract, and `safety.before_state`.
- Ordinary write apply requires explicit no-snapshot approval before provider HTTP when no saved snapshot is available until before-state or provider-backup capture exists.
- Provider backup/restore receipts show the explicit provider workflow and best-effort verification.

2) Intent alignment (a reviewer)
- A reviewer checks that the planned change matches the goal and context.
- This is best done by a human or a smart agent (we recommend Codex).

The tool should stay deterministic; the review is outside the tool.

## Plan -> Review -> Apply Refusal

Recommended workflow for ordinary writes:

1) Generate a plan (dry-run).
2) Review the plan (human/Codex).
3) Request apply with `--live --apply` (and `--yes` for risky actions).
4) Confirm the tool requires explicit no-snapshot approval before Qdrant Cloud HTTP when no saved snapshot is available.

For provider backup/restore workflows, review the plan first, then apply only the explicit backup/restore command.

## Plans, refusals, and provider receipts

For write-capable commands, treat the dry-run output as a **plan**:
- what will change
- what must be true to apply safely (preconditions)
- whether `safety.before_state` is supported for this operation

Current ordinary write apply outputs a safe **refusal** instead of a receipt because no Qdrant Cloud write is sent.

Provider backup/restore apply can output a **receipt**:
- which backup/restore action was requested
- what verification ran and whether it passed
- the explicit recovery contract

Plans, refusals, and receipts must never include secrets.

### Plan/refusal/receipt files (recommended v2 flags)

If a command supports writes, it should also support file outputs:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--plan-in <path>`: apply from a saved plan file (for high-risk/batch)
- `--receipt-out <path>`: write provider backup/restore receipts; ordinary write apply refuses and does not create a receipt

This makes the workflow repeatable in CI and easier to review.

## Run history (recommended for customer-ready tools)

For write-capable commands, this template automatically writes a local run folder (gitignored):
- `.state/runs/<run_id>/`

It also appends a simple history row to:
- `.state/runs/index.jsonl`

These live next to your `--env-file` (usually next to your `.env` file), so you can always find them.

This is designed for vibe coders:
- You can ask your agent “what happened last time?” and it can use `runs list/show`.
- You don’t need to manually browse folders.

Rules:
- These artifacts must never include secrets.
- Plans, refusals, provider receipts, and audit logs are proof of what happened.

## Risk levels (guideline)

- Low: create new drafts; small safe edits.
- Medium: edit an existing draft; single-resource updates.
- High: edit published content; status changes; deletes; batch.
- Irreversible: actions that cannot realistically be undone (example: analytics events, licensing downloads).

High/irreversible actions should require an explicit plan + confirmation.

For irreversible actions, consider an extra acknowledgement flag:
- `--ack-irreversible`

For money-moving / billing actions, require an explicit acknowledgement:
- `--ack-spend-money`

## Drift detection (recommended for plan apply)

If you support applying from a saved plan file, refuse if the target changed since the plan was created.
Examples:
- `updated_at` / `modified_gmt`
- a content hash

## Recovery contract (recommended default)

- Every write now includes a recovery contract so the output is explicit.
- `no-recovery`: ordinary writes are not paired with automatic or implicit recovery, and current ordinary apply requires explicit no-snapshot approval before provider HTTP when no saved snapshot is available.
- `provider-backup-restore`: backup/restore calls are provider-native recovery commands and must be run explicitly.
- For any contract, do not run recovery implicitly. If recovery is needed, follow the explicit workflow.
