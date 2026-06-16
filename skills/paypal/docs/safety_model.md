# Safety model

PayPal can touch orders, captures, refunds, payouts, invoices, webhooks, and account resources, so the safe path is to look first, plan second, and change last. Reads and dry-run plans are where the agent should do most of its thinking. Real changes should only happen after the plan is reviewed and the required approval flags are present.

That matters because the risky part is usually not the command syntax. It is choosing the wrong account, changing the wrong live resource, exposing sensitive output, or approving a change that cannot be cleanly undone.

A good safety ask is: "Read the order or transaction first, then review the plan before money-moving, refund, payout, invoice, or webhook changes."

## Core safety rules

- Dry-run by default; no writes unless `--apply`.
- Current write apply requires explicit no-snapshot approval before PayPal auth or HTTP until command-specific saved snapshot support is available.
- Refuse when unsure; do not guess.
- Some higher-risk actions require `--apply` and `--yes`, including both delete and non-delete actions. Use `docs/api_coverage.md` as the exact main reference.
- No current shipped PayPal command in this tool requires `--ack-irreversible`.
- Never log secrets.

## How to review risky work

There are two kinds of safety:

1. What the tool checks
- Write plans show the intended command, risk gates, `before_state`, and no-recovery contract.
- Apply gates run first, then current write apply requires explicit no-snapshot approval before PayPal auth or HTTP.

2. What a reviewer checks
- A reviewer checks that the planned change matches the goal and context.
- This is best done by a human or a smart agent (we recommend Codex).

The tool can check gates and outputs, but a person or reviewing agent still needs to check whether the change is the right change.

## Plan -> Review -> Apply Refusal

Recommended workflow for writes:

1) Generate a plan (dry-run).
2) Review the plan (human/Codex).
3) Request apply with `--apply` (and `--yes` for risky actions).
4) Confirm the tool requires explicit no-snapshot approval before PayPal auth or HTTP.

## Plans and refusals

For write-capable commands, treat the dry-run output as a **plan**:
- what will change
- what must be true to apply safely (preconditions)
- why current apply requires explicit no-snapshot approval before PayPal HTTP
- what recovery is available after apply

Current write apply outputs a safe **refusal** instead of a receipt because no PayPal write is sent.

Plans and refusals must never include secrets.

For this tool, write plans include a `recovery` block:
- `automatic_rollback: false`
- `snapshots: []`
- `backups: []`
- `rollback_plan: null`
- `verification_mode: "best-effort"`
- `restore_note` explains that recovery is not automatic and needs an explicit command

### Plan/refusal files (recommended v2 flags)

If a command supports writes, it should also support file outputs:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--plan-in <path>`: apply from a saved plan file (for high-risk/batch)
- `--receipt-out <path>`: writes an approved apply receipt when the supported write proceeds; missing approval or failed safety checks do not create a receipt

This makes the workflow repeatable in CI and easier to review.

## Run history (recommended for customer-ready tools)

For write-capable commands, this tool automatically writes a local run folder (gitignored):
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
- A safe refusal returns exit code `0` with `{"ok": true, "refused": true, ...}`.

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

## Rollback (recommended default)

- Do not auto-rollback silently.
- In this tool, no rollback plan is generated and no snapshots/backups are created.
- Current write apply requires explicit no-snapshot approval before PayPal auth or HTTP, so no rollback is needed for refused writes.
- Any future recovery must be done as a separate explicit action.
