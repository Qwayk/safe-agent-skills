# Safety model

This tool is designed so you can safely let an AI agent operate your Dynadot account.

Bottom line:
- It shows a preview first (a plan).
- It refuses to make changes unless you explicitly approve.
- Write apply requires explicit no-snapshot approval before Dynadot HTTP when command-specific saved snapshot support is not available.

Rules:
- Dry-run by default; no writes unless `--apply`.
- Most writes also require `--yes` and a reviewed `--plan-in`.
- Write plans include `before_state.required: true`, `before_state.supported: false`, and `before_state.status: no_snapshot_available`.
- Refuse when unsure; do not guess parameters.
- Never log secrets.

## Two-layer safety (recommended)

There are two kinds of safety:

1) Mechanical correctness (the tool)
- The tool shows the planned target, requires the right approvals, and records the no-snapshot limit when no useful before-state can be saved.
- A dry-run plan and read-back after apply are not treated as before-state.

2) Intent alignment (a reviewer)
- A reviewer checks that the planned change matches the goal and context.
- This is best done by a human or a smart agent (we recommend Codex).

The tool should stay deterministic; the review is outside the tool.

## Plan -> Review -> Approve No-Snapshot When Needed

Recommended workflow for writes:

1) Generate a plan (dry-run).
2) Review the plan (human/Codex).
3) Try apply only after approval.
4) When no useful before-state can be saved, the tool explains the no-snapshot limit and requires explicit approval before supported writes proceed.

## What verification means in this tool (Dynadot)

Dynadot API3 is command-based. Many write commands do not have a perfect "get exactly this setting" endpoint.
Because of that, write plans must be clear about the no-snapshot limit and require explicit approval before supported writes proceed.

Old read-back plans are still useful design notes, and some plans keep them as `post_apply_verification_plan`.
They help verify the result, but they are not restoreable backups.

## Recovery contract

All current Dynadot write families in this CLI are `irreversible_and_clearly_labeled`.

That means:
- `recovery.end_state` is `irreversible_and_clearly_labeled`.
- write plans include `recovery`
- `recovery.backups` is `[]`
- `recovery.snapshots` is `[]`
- `recovery.rollback_plan` is `null`
- approved supported writes create receipts that record the no-snapshot approval and recovery limit

## Plans and refusals (how to trust what happened)

For write-capable commands, treat the dry-run output as a **plan**:
- what will change
- what must be true to apply safely (preconditions)
- whether apply needs a saved before-state, explicit no-snapshot approval, or a true blocker reason

When apply is attempted with the required gates, output a receipt for approved supported writes or a safe refusal for a real blocker:
- missing approval
- unclear target
- missing credentials
- unsupported API action
- failed safety check

Plans/refusals must never include secrets.

Some bulk write-capable commands still support pacing/limiting flags in their plans.
Those flags matter for pacing, limiting, and clear receipts on approved supported writes.

## Safe resume (recommended for large runs)

Some write commands can still plan from an older receipt with `--resume-from-receipt <receipt.json>`:
- The tool skips items that were already completed in the previous receipt.
- The new plan records the resume receipt file hash (`resume_receipt_sha256`).
- Resume apply still requires explicit no-snapshot approval before Dynadot HTTP when no useful before-state can be saved.

### Plan/refusal files (recommended v2 flags)

If a command supports writes, it should also support file outputs:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--plan-in <path>`: apply from a saved plan file (for high-risk/batch)
- `--receipt-out <path>`: writes an approved apply receipt when the supported write proceeds; missing approval or failed safety checks do not write it

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
- Plans/refusals/audit logs are proof of what was reviewed and why no write happened.

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
- If future verification fails after before-state support is added, do not invent rollback.
- Keep the write labeled as `irreversible_and_clearly_labeled` unless the tool gains a real restore path later.
