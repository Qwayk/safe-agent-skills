# Safety model

Rules:
- Dry-run by default; write-capable commands make reviewable plans first.
- Confirmed write apply requires real before-state, provider-backup data, or explicit no-snapshot approval before the write.
- Refuse when unsure; do not guess.
- Batch write jobs require `--apply` and `--yes`, then refuse for the same before-state reason.
- Never log secrets.
- For API methods, use explicit per-method commands: `youtube-api-tool api <resource.method>` (no generic dispatcher).
- For media downloads, save to a file (never dump raw/binary bodies into JSON output).

## Two-layer safety (recommended)

There are two kinds of safety:

1) Mechanical correctness (the tool)
- For write-capable commands, the tool now stops before provider writes, uploads, token writes, demo/job writes, or receipt output unless saved snapshot support is available.
- The refusal includes a verification plan that proves nothing was changed.

2) Intent alignment (a reviewer)
- A reviewer checks that the planned change matches the goal and context.
- This is best done by a human or a smart agent (we recommend Codex).

The tool should stay deterministic; the review is outside the tool.

## Plan -> Review -> Approve No-Snapshot When Needed

Recommended workflow for writes:

1) Generate a plan (dry-run).
2) Review the plan (human/Codex).
3) If a user confirms apply, the tool requires explicit no-snapshot approval before the write unless command-specific before-state/provider backup support exists.
4) Review the refusal and confirm there was no provider write, upload, token write, or success receipt.

## Plans and receipts (recommended)

For write-capable commands, treat the dry-run output as a **plan**:
- what will change
- what must be true to apply safely (preconditions)
- how verification will happen
- recovery contract for post-change handling

After a blocked apply, output a **refusal**:
- why nothing changed
- the plan that would have been applied
- how to verify that no provider write, upload, token write, or success receipt happened
- recovery contract for what is not recoverable in this runtime

Plans, refusals, receipts, and audit logs must never include secrets.

### Plan/receipt files (recommended v2 flags)

If a command supports writes, it should also support file outputs:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--plan-in <path>`: attempt from a saved plan file (currently refuses for write-capable commands when no saved snapshot is available)
- `--receipt-out <path>`: write a post-apply receipt only for flows that actually apply; blocked write applies must not create a success receipt

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
- Plans/refusals/receipts/audit logs are proof of what happened and how it was verified.

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
- If verification fails and automatic recovery is possible, generate a recovery plan and require explicit apply.
- If automatic recovery is not possible, mark the action as irreversible and state that contract explicitly.

In this runtime, write actions require explicit no-snapshot approval before apply and remain explicit no-recovery:
- `end_state` is `irreversible_and_clearly_labeled`
- `automatic_rollback` is false
- `backups`, `snapshots`, and `rollback_plan` are empty/`null`
- no provider restore is available
