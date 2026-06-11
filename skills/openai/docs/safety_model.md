# Safety model

Rules:
- Dry-run by default; no writes unless `--apply`.
- Writes require explicit no-snapshot approval before OpenAI HTTP when the command cannot save real before-state.
- Refuse when unsure; do not guess.
- Batch jobs require `--apply` and `--yes`.
- Never log secrets.

## Two-layer safety (recommended)

There are two kinds of safety:

1) Mechanical correctness (the tool)
- For writes, the tool requires explicit no-snapshot approval before provider HTTP when it cannot save the live before-state.
- Live reads still run only with `--live`, and binary or streaming responses are saved as local artifacts instead of printed raw.

2) Intent alignment (a reviewer)
- A reviewer checks that the planned change matches the goal and context.
- This is best done by a human or a smart agent (we recommend Codex).

The tool should stay deterministic; the review is outside the tool.

## Plan -> Review -> Apply Or Refuse For A Real Blocker

Current workflow for writes:

1) Generate a plan (dry-run).
2) Review the plan (human/Codex).
3) Try apply with the required gates (`--live --apply`, and the extra flags for spend-money or irreversible operations).
4) If no real before-state can be saved, the tool requires explicit no-snapshot approval before OpenAI API key use or HTTP. Approved supported writes proceed and create receipts; missing approval or failed safety checks refuse honestly.

## Plans, refusals, and receipts

For write-capable commands, treat the dry-run output as a **plan**:
- what will change
- what must be true to apply safely (preconditions)
- the `before_state` or no-snapshot contract
- why apply needs explicit no-snapshot approval before provider write when no useful before-copy can be saved

Approved supported writes create receipts. Refusals happen when approval is missing, the target is unclear or unsupported, credentials are missing, or a safety check fails.

Live read receipts still record what came back from OpenAI.

Plans/receipts must never include secrets.

### Plan/receipt files (recommended v2 flags)

If a command supports writes, it should also support file outputs:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--plan-in <path>`: apply from a saved plan file (for high-risk/batch)
- `--receipt-out <path>`: write a receipt when an approved supported command really runs; refusals for missing approval or failed safety checks do not create write receipts

This makes the workflow repeatable in CI and easier to review.

## Write gating requirements

- Any command that would hit the OpenAI network requires `--live`; the CLI stays plan-only without that flag.
- Write actions also demand `--apply`; without it the tool never executes mutations beyond the plan.
- Spend-money operations (model inference/generation, embeddings, images/audio, fine-tunes, batches, moderations, etc.) layer on `--plan-in <plan.json>`, `--yes`, and `--ack-spend-money` in addition to `--live --apply` so a saved plan can be audited before applying.
- Deletes and other irreversible actions additionally require `--ack-irreversible` on top of the write gates.
- After those gates pass, writes require explicit no-snapshot approval before OpenAI API key use or HTTP when command-specific saved snapshot support is not available.
- Reference `docs/examples/plan_spend_money.example.json` for a spend-money plan whose `classification.gates.plan_in`, `classification.gates.yes`, and `classification.gates.ack_spend_money` are all `true`, proving the emitted gate state.

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
- Plans/refusals/read receipts/audit logs are proof of what happened and how it was verified.

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

## Idempotency handling

The pinned OpenAI operation list does not mention an `OpenAI-Idempotency-Key` or a compatible idempotency header as part of the documented API surface. Because of that, the tool does not rely on a server-side idempotency guarantee. Instead, it keeps the plan hash in the plan payload and refuses if the inputs change.

## No-recovery contract for writes

- Do not auto-rollback silently.
- This tool does not provide automatic recovery.
- Write plans include `recovery` with:
  - `automatic_rollback: false`
  - `backups: []`
  - `snapshots: []`
  - `rollback_plan: null`
  - `restore_note` that points to the explicit restore path the operator must run if recovery is needed.

## Streaming and binary responses

- When `stream=true` appears in the request body or query, the tool treats the response as a streaming SSE feed. Streaming runs require `--live` plus a writable artifacts directory so the bytes can be captured safely (`.state/runs/<run_id>/…`). The `[DONE]` token or a max-bytes cap stops the stream, and receipts record the artifact path/sha256 without decoding the SSE payload.
- Binary responses (audio, video, files, etc.) are also written straight to artifacts so we never print raw bytes on stdout. Receipts include the artifact path, sha256, byte count, and declared `content_type` instead of leaking binary blobs.
- JSON responses are redacted before appearing in previews: keys containing `key`, `token`, `secret`, `password`, `authorization`, or `credential` become `<redacted>`, and string values that look like secret keys (`sk-`, `pk-`, `tok_`, `rtok-`) are replaced as well. This keeps the plan/receipt proofs safe for sharing.
