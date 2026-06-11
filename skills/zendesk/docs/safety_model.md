# Safety model

Rules:
- Dry-run by default.
- No network calls by default. API operations require `--live` to execute.
- Reads can execute with `api --live`.
- API write apply currently requires explicit no-snapshot approval before Zendesk HTTP when safe before-state capture is not available.
- Refuse when unsure; do not guess.
- Batch jobs with write actions are still stub-only and refuse honestly instead of sending real Zendesk writes.
- Never log secrets.

Core contract for write-capable commands:
- Plan-first, then proof-first.
- API write plans must show the no-snapshot limit clearly until safe saved snapshot support is available.
- No automatic rollback.
- No snapshots.
- No backups.
- Restore actions are separate explicit commands when exposed by the API operation.

## Two-layer safety (recommended)

There are two kinds of safety:

1) Mechanical correctness (the tool)
- Reads can run live with explicit `--live`.
- API writes can run after a reviewed plan and explicit no-snapshot approval.
- Demo write and jobs write rows stay stub-only refusals because they do not execute real Zendesk provider writes.

2) Intent alignment (a reviewer)
- A reviewer checks that the planned change matches the goal and context.
- This is best done by a human or a smart agent (we recommend Codex).

The tool should stay deterministic; the review is outside the tool.

## Plan → Review → Apply Or Refuse

Recommended workflow for writes:

1) Generate a plan (dry-run).
2) Review the plan (human/Codex).
3) For API writes, confirm the no-snapshot limit and add `--ack-no-snapshot` only if you approve it.
4) For demo write and jobs write rows, stop at the refusal because those surfaces are still stubs.

## Plans, approvals, and safe refusals

For write-capable commands, treat the dry-run output as a **plan**:
- what will change
- what must be true to apply safely (preconditions)
- how verification happens for API writes today
- before-state status
- no-recovery statement: `automatic_rollback=false`, `backups=[]`, `snapshots=[]`, `rollback_plan=null`

API write applies can output a successful write receipt after explicit no-snapshot approval. Demo write and jobs write rows still output a **safe refusal** because they do not execute real Zendesk provider writes.

Plans, refusal output, and future receipts must never include secrets.

### Plan/refusal files

If a command supports writes, it should also support file outputs:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--plan-in <path>`: validate a saved plan file for high-risk/batch writes
- `--receipt-out <path>` writes API apply receipts; stub-only demo/jobs refusals do not create one

This makes the workflow repeatable in CI and easier to review.

## Run history (recommended for customer-ready tools)

For write-capable commands, this tool automatically writes a local run folder (gitignored):
- `.state/runs/<run_id>/`

It also appends a simple history row to:
- `.state/runs/index.jsonl`

These live next to your `--env-file` (usually next to your `.env` file), so you can always find them.

This is designed for vibe coders:
- You can ask your agent “what happened last time?” and it can use `runs list/show`.
- You don’t need to manually browse folders.

Rules:
- These artifacts must never include secrets.
- Plans, safe refusals, and audit logs are proof of what happened.

## Risk levels (guideline)

- Low: create new drafts; small safe edits.
- Medium: edit an existing draft; single-resource updates.
- High: edit published content; status changes; deletes; batch.
- Irreversible: actions that cannot realistically be undone (example: analytics events, licensing downloads).

High/irreversible actions should require an explicit plan + confirmation.

For irreversible actions, consider an extra acknowledgement flag:
- `--ack-irreversible`

## Drift detection (recommended for future plan apply)

If you support applying from a saved plan file, refuse if the target changed since the plan was created.
Examples:
- `updated_at` / `modified_gmt`
- a content hash

## Recovery (recommended default for this tool)

- Recovery is explicit only.
- Add to every write plan and future receipt:
  - `automatic_rollback: false`
  - `backups: []`
  - `snapshots: []`
  - `rollback_plan: null`
- If a restore command exists for the operation, run that separate command as a second explicit step.
