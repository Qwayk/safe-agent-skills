# Safety model

This tool is safe-by-default:
- Cloudflare API writes are **dry-run by default** (no writes unless `--apply --yes`).
- Destructive/batch actions require `--apply --yes` (and `--ack-irreversible` for irreversible actions).
- Sensitive reads (code/KV values/PII-like outputs) require `--apply` and explicit file output; the tool never prints sensitive content to stdout.
- Some Cloudflare APIs use **non-GET** methods for **read-like** operations (example: KV bulk get, Queues pull). These are treated as sensitive file-only reads: apply requires `--apply` + `--out`, and they do **not** require `--yes`.
- Browser Run named wrappers are read-like file-output commands: `browser-run markdown|links|scrape|screenshot|crawl|crawl-result` require `--apply --out`; `--yes` is accepted but not required.
- Dangerous writes should save live before-state before apply when practical. If this tool cannot save useful before-state for a supported write family, apply requires explicit no-snapshot approval; unsupported, ambiguous, or failed safety-check cases still stop.
- `auth zone-create-check` is a safe auth preflight. It sends an intentionally invalid create-zone payload so Cloudflare can prove or refuse the permission without creating a zone.

Rules:
- Read-only by default; refuse when unsure; do not guess.
- Never log secrets.

## Two-layer safety (recommended)

There are two kinds of safety:

1) Mechanical correctness (the tool)
- After a write, the tool verifies the API state.
- When verification is not possible, the tool should label it as best-effort and explain.

2) Intent alignment (a reviewer)
- A reviewer checks that the planned change matches the goal and context.
- This is best done by a human or a smart agent (we recommend Codex).

The tool should stay deterministic; the review is outside the tool.

## Plan/apply

The CLI already reserves `--apply/--yes/--plan-out/--receipt-out` flags to match the API Tool Standard v2,
and it implements plan/apply/verify/receipt workflows for:
- the standard, human-friendly command families (example: `workers routes ensure`)
- the Browser Run quick-action family (`browser-run markdown|links|scrape|screenshot|crawl|crawl-result`)
- the explicit per-operation `operations <area> <op_key>` command surface, which can execute any allowlisted operation derived from the in-repo snapshot extracts.

Named remote-write helpers are currently dry-run-only unless they are local-only or read-like file-output commands. The generic `operations` surface is the supported live-write path when it can save before-state when possible.

### Advanced: per-operation commands (full allowlisted coverage)

`cloudflare-api-tool operations <area> <op_key>` is designed for “full coverage” and agent-led work:
- For **writes**, it is dry-run by default and emits a deterministic plan.
- For dangerous writes with a matching read path, that dry-run plan also reads and saves the current live state first in `before_state` / `before_state_path`.
- For **read-only (GET)** operations, it executes immediately (no `--apply` needed).
- Writes require `--apply --yes`.
- Writes that cannot save before-state when possible require explicit no-snapshot approval for live apply.
- Sensitive outputs (tokens, script code, KV values, temporary upload JWTs, PII-like outputs) are written to a local file via `--out` (never printed).
- Some operations may return a secret/token only once; these require `--ack-irreversible` and `--out`.
- Read-like non-GET operations that return sensitive bodies require `--apply` + `--out` but do not require `--yes`; receipts report `changed=false`.
- Verification is best-effort: when a matching GET exists in the snapshot, the tool attempts a read-back; otherwise it records API response success and documents the limitation in the receipt.

## Plans and receipts

For write-capable commands, treat the dry-run output as a **plan**:
- what will change
- what must be true to apply safely (preconditions)
- how verification will happen
- where the saved old state lives when the write family can read it safely first

After apply, output a **receipt**:
- what actually changed
- what verification ran and whether it passed
- the same saved old-state reference when it was captured before apply

Plans/receipts must never include secrets.

### Plan/receipt files (recommended v2 flags)

If a command supports writes, it should also support file outputs:
- `--plan-out <path>`: write the dry-run plan JSON to a file (for review)
- `--plan-in <path>`: apply from a saved plan file (for high-risk/batch)
- `--receipt-out <path>`: write the post-apply receipt JSON to a file (for audit)

This makes the workflow repeatable in CI and easier to review.

## Run history (local proof)

Local-write commands (example: saving a default account id) can write a run folder under:
- `.state/runs/<run_id>/` (gitignored; next to your `--env-file`)

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

- Low: read-only inventory (GET) and local-only bookkeeping (example: saving a default account id).
- Medium: single-resource, reversible configuration updates (future phases; example: update a Workers route for a non-production zone).
- High: production-impacting changes or bulk edits (future phases; example: upload and deploy a new Worker script version, change production routes, or batch-delete KV keys).
- Irreversible: actions that cannot realistically be undone (future phases; example: delete a Worker, delete a route/zone resource, or purge data in a way that cannot be reconstructed).

High/irreversible actions should require an explicit plan + confirmation (when write commands are added).

For irreversible actions, consider an extra acknowledgement flag:
- `--ack-irreversible`

## Drift detection (recommended for plan apply)

If you support applying from a saved plan file, refuse if the target changed since the plan was created.
Examples:
- `updated_at` / `modified_gmt`
- a content hash

## Rollback and recovery

- Do not auto-rollback silently.
- For the broad `operations` write surface, this tool can now save live old-state before many writes, but it still does not provide automatic rollback or restore.
- If a command emits a `rollback_plan` in its receipt, use it as a **manual** guide for next steps; it is not automatic rollback.
- If there is no rollback path, label the action as irreversible and ask for manual recovery planning.
