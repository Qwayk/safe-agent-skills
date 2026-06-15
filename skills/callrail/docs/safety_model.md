# Safety model

CallRail can touch calls, forms, companies, trackers, messages, and account settings, so the safe path is to look first, plan second, and change last. Reads and dry-run plans are where the agent should do most of its thinking. Real changes should only happen after the plan is reviewed and the required approval flags are present.

That matters because the risky part is usually not the command syntax. It is choosing the wrong account, changing the wrong live resource, exposing sensitive output, or approving a change that cannot be cleanly undone.

A good safety ask is: "Start with one company or call read, then require the full approval flags before any tracker, SMS, call, or account change."

## Core safety rules

- Dry-run by default; no writes unless `--apply --yes` and any required approval flags are present.
- Write paths without saved before-state require `--ack-no-snapshot` before apply.
- Write commands can only run when they include explicit review intent.
- Verify after write (read-back when available).
- Refuse when unsure; do not guess.
- Never log secrets.
- Plans and receipts default to file outputs when artifacts are enabled.
- `calls create-outbound` and `text-messages send` require `--ack-irreversible` in addition to `--apply --yes --ack-no-snapshot`.
- `integrations create` and `integrations update` payloads must use `payload.type` of `webhooks` or `custom`.
- Only the explicit CLI command families in `docs/api_coverage.md` are shipped.

## How to review risky work

There are two kinds of safety:

1. What the tool checks
- After a write, the tool records the request and provider response.
- When read-back verification is not available yet, the tool should label the receipt as response-based and explain that clearly.

2. What a reviewer checks
- A reviewer checks that the planned change matches the goal and context.
- This is best done by a human or a smart agent (we recommend Codex).

The tool can check gates and outputs, but a person or reviewing agent still needs to check whether the change is the right change.

## Plan → Review → Apply → Verify

Recommended workflow for writes:

1) Generate a plan (dry-run).
2) Review the plan (human/Codex).
3) Apply with `--apply --yes --ack-no-snapshot` while no saved snapshot exists (plus `--ack-irreversible` where required).
4) Verify after write and produce a receipt for review.
   - When a command does not yet support read-back verification, keep the receipt and provider response and treat it as best-effort evidence, not full state proof.

## Plans and receipts (recommended)

For write-capable commands, treat the dry-run output as a **plan**:
- what will change
- what must be true to apply safely (preconditions)
- how verification will happen

After apply, output a **receipt**:
- what actually changed
- what verification ran and whether it passed
- pointers to backups/snapshots when available
- no-snapshot approval when no useful before-state was saved

Plans/receipts must never include secrets.

### Plan/receipt files (recommended v2 flags)

If a command supports writes, it should also support file outputs:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--plan-in <path>`: apply from a saved plan file (for high-risk/batch)
- `--receipt-out <path>`: write the post-apply receipt JSON to a file (for audit)

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
- Plans/receipts/audit logs are proof of what happened and how it was verified.

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
- If verification fails and rollback is possible, generate a rollback plan and require explicit apply.
- If rollback is not possible, label the action as irreversible.
