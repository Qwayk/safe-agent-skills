# Safety model

Amazon Creators can touch creator storefront and product-catalog work, so the safe path is to look first, plan second, and change last. Reads and dry-run plans are where the agent should do most of its thinking. Real changes should only happen after the plan is reviewed and the required approval flags are present.

That matters because the risky part is usually not the command syntax. It is choosing the wrong account, changing the wrong live resource, exposing sensitive output, or approving a change that cannot be cleanly undone.

A good safety ask is: "Run one catalog read first, confirm the marketplace and partner tag, and stop before any local credential or token write."

## Core safety rules

- Keep catalog commands read-only against Amazon.
- Run catalog commands in dry-run mode by default; they emit a plan but do not hit the API.
- Keep local write helpers plan-first and require explicit no-snapshot approval when no saved snapshot is available:
  - `onboarding` apply requires explicit no-snapshot approval before `.env` creation.
  - `auth token set` and `auth token fetch` apply require explicit no-snapshot approval before token-cache writes or token endpoint calls.
- `.state/runs/` metadata is still recorded for write-capable commands unless you pass `--no-artifacts`.
- Verify catalog read outputs when possible.
- Refuse when unsure; do not guess.
- Never log secrets.

## How to review risky work

There are two kinds of safety:

1. What the tool checks
- Build a deterministic plan first.
- For catalog commands, run the remote request only after `--apply`.
- For local write helpers, emit a plan first, then require explicit no-snapshot approval before local file writes, token endpoint calls, demo/job writes, or success receipt output.
- When verification is not possible, label it clearly and explain.

2. What a reviewer checks
- A reviewer checks that the request selector matches the goal.
- This is best done by a human or an AI reviewer (we recommend Codex).

The tool stays deterministic; the review is outside the tool.

## Plan -> Review -> Apply Or Refuse

Recommended workflow for catalog reads:
1) Generate a plan (dry-run).
2) Review the plan (human/Codex).
3) Apply with `--apply`.
4) Verify output and review the receipt.

Recommended workflow for local write helpers:
1) Generate a plan (dry-run).
2) Review the plan.
3) A confirmed apply requires explicit no-snapshot approval before local writes when no saved snapshot is available.
4) Review the receipt for approved helper writes, or the refusal when approval or another safety gate is missing.

## Plans and receipts

For catalog commands, treat dry-run output as a **plan**:
- operation, locale, resources, request payload
- preconditions needed before apply
- validation checks

After catalog apply, output a **receipt**:
- request details and request outcome
- verification result
- local artifact paths (`plan`, `receipt`, run logs)

For write helpers (`onboarding`, `auth token set`, `auth token fetch`, demo writes, jobs write rows), dry-run plans are used first. Approved supported writes create receipts; missing approval or failed safety gates create refusal output.

Plans, refusals, receipts, and audit logs must never include secrets.

### Plan/receipt files

If a command supports plans/receipts, include file outputs:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--receipt-out <path>`: write a receipt only when a real catalog read apply succeeds

`--plan-in <path>` is currently reserved and has no effect on this shipped surface.

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
- Plans/refusals/receipts/audit logs are proof of what happened and how it was verified.

## Risk levels (guideline)

- Low: catalog reads and token status checks.
- Medium: catalog reads with larger locale/resource combinations.
- High: broad catalog queries that return many rows.
- Irreversible: local writes with no restore path.

High/irreversible actions should require an explicit plan + confirmation.

`--yes` and `--ack-irreversible` are parsed for future high-risk write flows.
They are currently not required for catalog reads, and local write helpers require explicit no-snapshot approval before writes.

## Drift detection (recommended for plan apply)

If you support applying from a saved plan file, refuse if the target changed since the plan was created.
Examples:
- `updated_at` / `modified_gmt`
- a content hash
