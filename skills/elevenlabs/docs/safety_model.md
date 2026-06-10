# Safety model

Rules:
- Dry-run by default; no writes unless `--apply`.
- Record what verification to run after a write (read-back or idempotence hints) so reviewers know what to check.
- Refuse when unsure; do not guess.
- Spend-sensitive generation commands require `--ack-spend-money` in addition to the normal write gates.
- Streaming/transcribing, voice design/changer, music upload/stem separation, audio isolation, and forced-alignment workstreams are all treated as spend-sensitive: they refuse `--live --apply` without `--ack-spend-money`.
- Never log secrets.
- The CLI now covers every non-legacy ElevenLabs endpoint (see `docs/api_coverage.md`). Treat each command as plan-first; the plan exposes the HTTP request. write applies require explicit no-snapshot approval before ElevenLabs API key use or provider HTTP when command-specific before-state capture is not available.
- Binary or high-risk sensitive responses (media, transcripts, phone numbers, ConvAI content, webhook secrets) must go to `--out <path>`; those commands stay file-only even though safe read helpers can still emit JSON to stdout. This now includes the live payloads from `auth check` and `history list`, so adding `--live` forces you to also pass `--out <path>` (use `--overwrite` if you reuse the same file) so the CLI only emits the file fingerprint.
- Spend-sensitive or irreversible operations also demand `--ack-spend-money` and (where noted) `--ack-irreversible` before applying; refer to `docs/api_coverage.md` for the exact gates per command.

## Two-layer safety (recommended)

There are two kinds of safety:

1) Mechanical correctness (the tool)
- Write plans include the intended post-apply verification steps, but writes require explicit no-snapshot approval before provider apply because before-state capture is missing.
- When verification is not possible, the tool should label it as best-effort and explain.

2) Intent alignment (a reviewer)
- A reviewer checks that the planned change matches the goal and context.
- This is best done by a human or a smart agent (we recommend Codex).

The tool should stay deterministic; the review is outside the tool.

## Plan → Review → Apply → Verify

Recommended workflow for writes:

1) Generate a plan (dry-run).
2) Review the plan (human/Codex).
3) Try apply only with the required gates (`--live --apply`, `--ack-spend-money`, `--ack-irreversible`, `--yes` where needed).
4) Write applies require explicit no-snapshot approval when no saved before-state is available; approved applies must emit receipts that record the approval and recovery limit.

## Plans and receipts (recommended)

For write-capable commands, treat the dry-run output as a **plan**:
- what will change
- what must be true to apply safely (preconditions)
- how verification will happen

After a real apply is re-enabled, output a **receipt**:
- what actually changed
- what verification steps are expected (and any observed outcomes) so reviewers know what to check
- pointers to backups/snapshots when available

ElevenLabs writes require explicit no-snapshot approval when no saved before-state is available; approved applies must emit receipts that record the approval and recovery limit.

Plans/receipts must never include secrets.

### Plan/receipt files (recommended v2 flags)

If a command supports writes, it should also support file outputs:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--plan-in <path>`: apply from a saved plan file (for high-risk/batch)
- `--receipt-out <path>`: write the post-apply receipt JSON to a file only after saved snapshot support is available and provider writes are re-enabled

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
- Plans, refusals, receipts, and audit logs are proof of what happened. Approved supported writes emit receipts that record no-snapshot approval and recovery limits when no before-state can be saved.

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

## Recovery contract (recommended default)

- Include a structured `before_state` block and `recovery` contract in every write plan. write plans must show `before_state.status: no_snapshot_available`.
- If recovery is possible, describe the inverse strategy and set `recovery.rollback_ready` to `true`.
- If recovery is not possible, set `recovery.end_state` to `irreversible_and_clearly_labeled` and `recovery.strategy` to `no_inverse`; set `recovery.rollback_ready` to `false` and `recovery.restore_note` to the explicit no-recovery statement that manual cleanup is needed.
