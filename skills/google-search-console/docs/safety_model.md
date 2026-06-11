# Safety model

Rules:
- Dry-run by default; no writes unless `--apply`.
- Verify after write (read-back or idempotence).
- Refuse when unsure; do not guess.
- Never log secrets.

Write-capable methods (GSC):
- `sites add`, `sites delete`
- `sitemaps submit`, `sitemaps delete`

Deletes are treated as **irreversible** and require extra acknowledgements.

## Two-layer safety (recommended)

There are two kinds of safety:

1) Mechanical correctness (the tool)
- After a write, the tool verifies the API state.
- When verification is not possible, the tool should label it as best-effort and explain.

2) Intent alignment (a reviewer)
- A reviewer checks that the planned change matches the goal and context.
- This is best done by a human or a smart agent (we recommend Codex).

The tool should stay deterministic; the review is outside the tool.

## Plan → Review → Apply → Verify

Recommended workflow for writes:

1) Generate a plan (dry-run).
2) Review the plan (human/Codex).
3) Apply with `--apply` (and `--yes` for risky actions).
4) Verify after write and produce a receipt for review.

### Plan and receipt recovery contract

For write methods, dry-run output includes `plan.recovery`.
For apply output includes `receipt.recovery`.
Dry-run and apply also include a live pre-state snapshot in `before_state`.
When run artifacts are enabled, `before_state_path` points to `before_state.json`.

Allowed `end_state` values:
- `rollback_by_inverse_action`
- `irreversible_and_clearly_labeled`

### Risk gates table (GSC)

| Command | Risk | Dry-run default | Apply gates | Recovery |
|---|---|---|---|---|
| `sites add` | high | Plan output | `--apply` | `rollback_by_inverse_action` (via `webmasters.sites.delete`) |
| `sitemaps submit` | high | Plan output | `--apply` | `rollback_by_inverse_action` (via `webmasters.sitemaps.delete`) |
| `sites delete` | irreversible | Refuses apply without gates | `--apply --yes --ack-irreversible --plan-in` | `irreversible_and_clearly_labeled` |
| `sitemaps delete` | irreversible | Refuses apply without gates | `--apply --yes --ack-irreversible --plan-in` | `irreversible_and_clearly_labeled` |

## Plans and receipts (recommended)

For write-capable commands, treat the dry-run output as a **plan**:
- what will change
- what must be true to apply safely (preconditions)
- how verification will happen
- what resource state existed before the write (`before_state`)

After apply, output a **receipt**:
- what actually changed
- what verification ran and whether it passed
- pointers to backups/snapshots when available (`before_state_path`)

Plans/receipts must never include secrets.

### Plan/receipt files (recommended v2 flags)

If a command supports writes, it should also support file outputs:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--plan-in <path>`: apply from a saved plan file (for high-risk/batch)
- `--receipt-out <path>`: write the post-apply receipt JSON to a file (for audit)

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
- Plans/receipts/audit logs are proof of what happened and how it was verified.

## Risk levels (guideline)

- Low: create new drafts; small safe edits.
- Medium: edit an existing draft; single-resource updates.
- High: edit published content; status changes; deletes; batch.
- Irreversible: actions that cannot realistically be undone (example: analytics events, licensing downloads).

High/irreversible actions should require an explicit plan + confirmation.

For irreversible actions, consider an extra acknowledgement flag:
- `--ack-irreversible`

## Drift detection (recommended for plan apply)

If you support applying from a saved plan file, refuse if the target changed since the plan was created.
Examples:
- `updated_at` / `modified_gmt`
- a content hash

## Rollback (recommended default)

- Do not auto-rollback silently.
- If verification fails and rollback is possible, generate a rollback plan and require explicit apply.
- If rollback is not possible, keep `end_state` set to `irreversible_and_clearly_labeled` and label the action as irreversible.
