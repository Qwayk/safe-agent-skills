# Safety model

Instantly can touch campaigns, leads, accounts, inboxes, analytics, and send-related workflows, so the safe path is to look first, plan second, and change last. Reads and dry-run plans are where the agent should do most of its thinking. Real changes should only happen after the plan is reviewed and the required approval flags are present.

That matters because the risky part is usually not the command syntax. It is choosing the wrong account, changing the wrong live resource, exposing sensitive output, or approving a change that cannot be cleanly undone.

A good safety ask is: "Read the campaign or lead state first, then review the plan before sends, lead changes, campaign changes, or bulk work."

## Core safety rules

Instantly work can touch live campaigns, leads, accounts, replies, deliverability tests, webhooks, and workspace settings, so this tool is built to slow down before risky actions.

## Default behavior

- Dry-run by default; no writes unless `--apply`.
- Verify after write when the API exposes a safe read-back path.
- Refuse when unsure instead of guessing.
- Sensitive reads and returned secrets stay file-only instead of chat or stdout.
- Supported live writes capture before-state under `.state/runs/<run_id>/before/` before applying.
- This tool does not have a machine rollback or restore path.
- Never log secrets.

## Extra approval for riskier actions

- High-risk or batch writes require `--apply` and `--yes`.
- Delete and irreversible apply require a reviewed plan file via `--plan-in`.
- Irreversible writes require `--apply --yes --ack-irreversible` where live apply is supported.
- Unsupported live writes need explicit no-snapshot approval before HTTP when a safe pre-read does not exist yet.

## How to review risky work

There are two kinds of safety:

1. What the tool checks
- After a write, the tool verifies the API state.
- When verification is not possible, the tool should label it as best-effort and explain.

2. What a reviewer checks
- A reviewer checks that the planned change matches the goal and context.
- This is best done by a human or a smart agent (we recommend Codex).

The tool can check gates and outputs, but a person or reviewing agent still needs to check whether the change is the right change.

## Plan → Review → Apply → Verify

Recommended workflow for writes:

1) Generate a plan (dry-run).
2) Review the plan (human/Codex).
3) Apply with `--apply` (and `--yes` for risky actions).
4) Verify after write and produce a receipt for review.

## Plans and receipts (recommended)

For write-capable commands, treat the dry-run output as a **plan**:
- what will change
- what must be true to apply safely (preconditions)
- how verification will happen

After apply, output a **receipt**:
- what actually changed
- where before-state evidence was saved, when supported
- what verification ran and whether it passed
- no automatic restore is run by the tool

Plans/receipts must never include secrets.

## Secret-bearing outputs (file-only + gated)

Some endpoints can return secrets (API keys, passwords). This tool never prints those values to stdout/stderr, and never writes them to plans/receipts/audit logs.

Instead, the raw secret-bearing response is stored locally under `.state/sensitive/` next to your `--env-file` (gitignored), and stdout includes only:
- the secret file path
- a SHA-256 fingerprint
- non-secret metadata (when available)

Safety gates:
- `api-keys create` apply requires `--ack-store-secret-locally` (and `--plan-in` on apply).
- `dfy-email-account-orders list-accounts --with-passwords` requires `--ack-store-secret-locally`.

### Plan/receipt files (recommended v2 flags)

If a command supports writes, it should also support file outputs:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--plan-in <path>`: apply from a saved plan file (for high-risk/batch)
- `--receipt-out <path>`: write the post-apply receipt JSON to a file (for audit)

This makes the workflow repeatable in CI and easier to review.

## Run history (recommended for customer-ready tools)

For write-capable commands, this template automatically writes a local run folder (gitignored):
- `.state/runs/<run_id>/`

Supported live writes also save the previous API response before applying:
- `.state/runs/<run_id>/before/`

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

## Rollback (this tool currently)

- Do not claim rollback or restore support.
- Do not auto-rollback.
- Before-state files are evidence for review and manual repair, not a rollback engine.
- This tool does not have a machine rollback or restore path.
