# Safety model

Google Analytics can touch GA4 properties, reports, audiences, links, and admin settings, so the safe path is to look first, plan second, and change last. Reads and dry-run plans are where the agent should do most of its thinking. Real changes should only happen after the plan is reviewed and the required approval flags are present.

That matters because the risky part is usually not the command syntax. It is choosing the wrong account, changing the wrong live resource, exposing sensitive output, or approving a change that cannot be cleanly undone.

A good safety ask is: "Run one report or property read first, then review the plan before audience, link, conversion, or admin changes."

## Core safety rules

- Dry-run by default; write-like commands produce plans.
- Current write apply requires explicit no-snapshot approval before GA4 HTTP until before-state capture exists.
- Refuse when unsure; do not guess.
- Batch jobs with write actions require `--apply` and `--yes`, then require explicit no-snapshot approval before write.
- Never log secrets.

## How to review risky work

There are two kinds of safety:

1. What the tool checks
- Write plans show the intended request, risk, no-recovery contract, and before-state blocker.
- Apply gates and plan drift checks run before the refusal.

2. What a reviewer checks
- A reviewer checks that the planned change matches the goal and context.
- This is best done by a human or a smart agent (we recommend Codex).

The tool can check gates and outputs, but a person or reviewing agent still needs to check whether the change is the right change.

## Plan -> Review -> Apply Refusal

Recommended workflow for writes:

1) Generate a plan (dry-run).
2) Review the plan (human/Codex).
3) Request apply with `--apply` (and `--yes` / `--ack-irreversible` for risky actions).
4) Confirm the tool requires explicit no-snapshot approval before GA4 HTTP until before-state capture exists.

## Plans and refusals

For write-capable commands, treat the dry-run output as a **plan**:
- what will change
- what must be true to apply safely (preconditions)
- why current apply requires explicit no-snapshot approval before provider HTTP

Current write apply outputs a safe **refusal** instead of a receipt because no GA4 write is sent.

Plans/refusals must never include secrets.

### Plan/receipt files (recommended v2 flags)

If a command supports writes, it should also support file outputs:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--plan-in <path>`: apply from a saved plan file (for high-risk/batch)
- `--receipt-out <path>`: write approved apply receipts; missing-approval refusals do not write it

This makes the workflow repeatable in CI and easier to review.

## Run history (recommended for customer-ready tools)

For write-capable commands, this template automatically writes a local run folder (gitignored):
- `.state/runs/<run_id>/`

It also appends a simple history row to:
- `.state/runs/index.jsonl`

These live next to your `--env-file` (usually next to your `.env` file), so you can always find them.

This makes later review easier:
- You can ask your agent “what happened last time?” and it can use `runs list/show`.
- You don’t need to manually browse folders.

Keep these local files private:
- These artifacts must never include secrets.
- Plans, refusals, and audit logs are proof of what happened.

## Risk levels (guideline)

- Low: create new drafts; small safe edits.
- Medium: edit an existing draft; single-resource updates.
- High: edit published content; status changes; deletes; batch.
- Irreversible: actions that cannot realistically be undone (example: analytics events, licensing downloads).

High/irreversible actions should require an explicit plan + confirmation.

Irreversible actions should require `--ack-irreversible`.

## Drift detection (recommended for plan apply)

If you support applying from a saved plan file, refuse if the target changed since the plan was created.
Examples:
- `updated_at` / `modified_gmt`
- a content hash

## Recovery contract (GA4 tool)

- Do not auto-rollback.
- Plans include a shared `recovery` block with:
  - `automatic_rollback: false`
  - `snapshots: []`
  - `backups: []`
  - `rollback_plan: null`
  - a `restore_note` that points to a separate explicit restore command if available
- Current write apply requires explicit no-snapshot approval before provider HTTP when no saved snapshot is available, so there is no receipt and no rollback need for the refused write.
