# Safety model

Rules:
- Dry-run by default; no writes unless `--apply`.
- Reads are plan-only by default; live GET/HEAD requires `--live`.
- Writes without saved before-state must disclose `before_state.status=no_snapshot_available`.
- Provider writes, DM sends, and auth local-state writes require `--apply --yes --ack-no-snapshot` before apply when no saved snapshot exists.
- DELETE additionally requires `--ack-irreversible`.
- Approved writes create receipts that record the no-snapshot approval and best available verification.
- Refuse when unsure; do not guess.
- Batch jobs require `--apply`, and write actions inside jobs also require `--yes`.
- Never log secrets.

## OpenAPI operations (explicit) (`x-api-tool api <operationId>`)

The tool exposes one explicit CLI subcommand per `operationId` in the pinned OpenAPI snapshot, and it can build a deterministic plan for each one.

Safety gates:
- GET/HEAD: requires `--live` to execute; otherwise it outputs a plan.
- Non-GET: outputs a plan by default. With `--apply --yes --ack-no-snapshot`, it can execute when no saved snapshot is available.
- DELETE: also requires `--ack-irreversible`.

The tool refuses (safe no-op) if an operation requires an auth mode the tool does not support.

## DMs (bulk policy)

Bulk DMs are high-risk. This tool refuses bulk sends unless:
- every row includes intent evidence (`intent_evidence` column), and
- an opt-out line is configured (`--opt-out-line`, non-empty), and
- recipients present in the local opt-out ledger are excluded.

Bulk pacing/backoff:
- `--min-delay-s` is used only after all required write approvals are present.
- The HTTP 429 backoff code is reached only after all required write approvals are present.

Local opt-out ledger:
- Stored under `.state/dm_opt_out.json` next to your `--env-file`.
- Manage it with `x-api-tool dm opt-out add/list`.
- `dm opt-out add` is the allowed protective local write because it prevents future sends to suppressed recipients.

## Two-layer safety (recommended)

There are two kinds of safety:

1) Mechanical correctness (the tool)
- Before a write, the tool records whether it has a saved snapshot.
- If no useful snapshot is available, the tool requires explicit no-snapshot approval and records that approval in the receipt.

2) Intent alignment (a reviewer)
- A reviewer checks that the planned change matches the goal and context.
- This is best done by a human or a smart agent (we recommend Codex).

The tool should stay deterministic; the review is outside the tool.

## Plan → Review → Apply → Receipt

Recommended workflow for writes:

1) Generate a plan (dry-run).
2) Review the plan (human/Codex).
3) Apply only with the required flags, including `--ack-no-snapshot` when the plan says no snapshot is available.
4) Review the receipt and provider response.

## Plans and receipts (recommended)

For write-capable commands, treat the dry-run output as a **plan**:
- what will change
- what must be true to apply safely (preconditions)
- how verification will happen (if available)

Apply outputs a **receipt**:
- what was attempted
- whether no-snapshot approval was acknowledged
- the provider or local-state result
- what verification was available

Plans, refusals, and future receipts must never include secrets.

### Plan/receipt files (recommended v2 flags)

If a command supports writes, it should also support file outputs:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--plan-in <path>`: apply from a saved plan file (for high-risk/batch)
- `--receipt-out <path>`: save the apply receipt JSON to a file

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
- Plans/refusals/audit logs are proof of what happened and why no write occurred.

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

## Rollback

- Do not auto-rollback silently.
- Most current commands in this tool do not have built-in rollback support.
- Current write families set `automatic_rollback=false`.
- If a future command adds real rollback support, require an explicit rollback plan and explicit apply.
- Otherwise, label the action as no-rollback/reasonably irreversible.
