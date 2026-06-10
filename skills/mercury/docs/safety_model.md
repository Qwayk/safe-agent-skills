# Safety model

Rules:
- Mercury API requests are **GET-only** (any non-GET is refused by design).
- The tool **never changes anything inside Mercury**.
- Local file writes (exports/downloads) are **dry-run by default** and require `--apply`.
- Overwriting an existing output file requires `--yes`.
- Verify local outputs after apply (file exists and is non-empty).
- Never log secrets (tokens/Authorization headers).
- Signed download URLs (for attachments) are treated as sensitive:
  - They are redacted from JSON outputs, plans, receipts, and verbose logs.

## Two-layer safety (recommended)

There are two kinds of safety:

1) Mechanical correctness (the tool)
- For read-only API calls: the tool refuses to guess (it surfaces errors clearly).
- For local exports/downloads: the tool verifies the file(s) were written successfully.

2) Intent alignment (a reviewer)
- A reviewer checks that the planned change matches the goal and context.
- This is best done by a human or a smart agent (we recommend Codex).

The tool should stay deterministic; the review is outside the tool.

## Plan → Review → Apply → Verify

Recommended workflow for exports/downloads (local file writes):

1) Generate a plan (dry-run).
2) Review the plan (human/Codex).
3) Apply with `--apply` (and `--yes` for risky actions).
4) Verify the local file(s) were written and produce a receipt for review.

## Plans and receipts (recommended)

For exports/downloads, treat the dry-run output as a **plan**:
- what will change
- what must be true to apply safely (preconditions)
- how verification will happen

After apply, output a **receipt**:
- what actually changed
- what verification ran (local file checks) and whether it passed
- pointers to backups/snapshots when available

Plans/receipts must never include secrets.

### Plan/receipt files (recommended v2 flags)

Exports/downloads support file outputs:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--plan-in <path>`: apply from a saved plan file (for high-risk/batch)
- `--receipt-out <path>`: write the post-apply receipt JSON to a file (for audit)

This makes the workflow repeatable in CI and easier to review.

## Run history (recommended for customer-ready tools)

For exports/downloads (local file writes), this tool automatically writes a local run folder (gitignored):
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

- Low: read-only API queries (no side effects).
- Medium: write a new local export/download file.
- High: overwrite existing local files (requires `--yes`).

## Drift detection (recommended for plan apply)

If you support applying from a saved plan file, refuse if the current arguments/output path differ from the reviewed plan.
Examples:
- output path differs
- filters differ (date range, accountId, etc.)

## Rollback (recommended default)

- For local file writes: rollback is typically “delete the file(s)” (manual).
