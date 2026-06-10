# Instagram Login Tool Safety model

Rules:
- Dry-run by default.
- Write apply attempts without saved before-state or provider backup use `before_state.status="no_snapshot_available"` and require explicit no-snapshot approval; missing approval refuses before provider HTTP.
- Refuse when unsure; do not guess.
- Risky writes still require `--yes` before the explicit no-snapshot approval is returned.
- Comment delete still requires `--ack-irreversible` before the explicit no-snapshot approval is returned.
- Never log secrets.

## What counts as a write

These command groups can change Instagram state or local token state:

- `media create-container`
- `media publish`
- `media comments set`
- `comments create`
- `comments replies create`
- `comments hide`
- `comments delete`
- `mentions reply-media`
- `mentions reply-comment`
- `messages send`
- `messages private-reply`
- `auth code exchange`
- `auth token set`
- `auth token exchange-long`
- `auth token refresh`

They create reviewable dry-run plans. confirmed applies require explicit no-snapshot approval; missing approval refuses before Instagram provider HTTP, local token-file writes, and receipt output.

## Risk levels

- Medium: token writes, comment replies, comment hide or unhide, message send
- High: publish media, delete comment
- Irreversible: comment delete without an API rollback path

High-risk commands require `--yes`.
Irreversible commands also require `--ack-irreversible`.

## Plan, review, and refusal

Recommended flow:

1. run the command without `--apply`
2. review the JSON plan
3. attempt apply with the required extra flags only after review
4. confirm missing approval is clearly labeled before apply
5. for approved applies, confirm the receipt records the no-snapshot approval; for missing approval, confirm no provider or local token write happened

 `--receipt-out` is reserved for receipts from approved applies. missing-approval write refusals must not write that file unless apply is approved.

## Verification limits

The tool does not yet save live before-state before any write family.
Because of that, it gives:

- an explicit plan before apply
- refusal gates for risky actions
- `before_state.status="no_snapshot_available"` in write plans
- a receipt for approved applies, or a refusal output when approval is missing
- redacted local run artifacts under `.state/runs/`

If you need to use read commands, configure auth through `.env` or an already prepared local token state. Do not use the write helpers to change token state when no saved snapshot is available.

## No batch runner in the shipped CLI

This tool does not ship the scaffold `jobs` command.
For batch work, run repeated explicit CLI commands from your agent or your own wrapper script so each call still keeps the same safety gates.

## Run history

Write-capable commands save local proof under:

- `.state/runs/<run_id>/plan.json`
- `.state/runs/<run_id>/audit.jsonl`
- `.state/runs/<run_id>/summary.md`
- `.state/runs/index.jsonl`

Rules:
- These artifacts must never include secrets.
- Plans and refusal outputs are your local proof trail.
- missing-approval write refusals do not create `.state/runs/<run_id>/receipt.json`.
