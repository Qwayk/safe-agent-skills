# Safety model

Rules:
- Dry-run by default; no writes unless `--apply`.
- Safety refusals are safe no-ops: `ok:true refused:true` with exit code `0`.
- Verify after write: re-fetch and assert.
- Refuse when unsure: no guessing edits.
- Batch jobs need plan-first review. Mixed row writes require saved before-state where practical, explicit no-snapshot approval where supported, or a safe refusal for real blockers.
- Destructive actions require `--apply` and `--yes` (example: deleting tags/pages/posts).
- Status changes require `--apply` and `--yes` (publishing/unpublishing/scheduling).
- Irreversible actions require `--apply --ack-irreversible` (example: actions that can trigger email delivery).
- Theme activation requires saved before-state where practical, or explicit no-snapshot approval with a clear receipt when no useful before-state can be saved.
- Webhook create/update/delete has no Ghost read-back endpoint. Where apply is supported, it needs explicit no-snapshot approval and local ledger proof; otherwise it should stop with a clear blocker reason.
- Snapshot-backed write families save JSON snapshots under `backup-snapshots/` next to your `--env-file`.
- Some write families need explicit no-snapshot approval or a real blocker reason because this CLI cannot always save the needed before-state.
- Never log secrets.
- Member emails are redacted in CLI output by default. Use `member ... --include-emails` or `member ... --raw` only when you explicitly need it.

## v2 plan/receipt + run artifacts

For write-capable commands (including dry-run planning), the tool creates a `run_id` and saves proof artifacts under `.state/` next to your `--env-file`:

- `.state/runs/<run_id>/plan.json` (always for write-capable commands)
- `.state/runs/<run_id>/receipt.json` (apply only)
- `.state/runs/<run_id>/audit.jsonl` (per-run audit; redacted)
- `.state/runs/<run_id>/summary.md`
- `.state/runs/index.jsonl` (append-only history)

Drift detection (recommended workflow):
1) Dry-run to generate a plan: run the write-capable command without `--apply` (or pass `--plan-out plan.json`)
2) Review the plan (human/Codex)
3) Apply with drift protection: re-run with `--apply --plan-in plan.json` (tool refuses if the recomputed plan differs)
4) Verify + review receipt: check `receipt.json` and the per-run `summary.md`

For `high` and `irreversible` risk applies, the tool requires `--plan-in` to enforce “plan → review → apply”.

Recovery contract:
- `snapshot_plus_restore`: the command keeps local snapshot evidence and the saved receipt points to the `__before.json` / `__after.json` / `__meta.json` files needed for a manual restore workflow.
- `irreversible_and_clearly_labeled`: the command stays plan-first and proof-first, but this CLI does not claim a direct restore path.

Current family split:
- Snapshot-backed examples: `post patch`, `page patch`, `post bodylex ...`, `post bodymob ...`, `post body ...`, `member update`, `newsletter update`, `tag update`, `tier update`, `offer update`.
- Dry-run-only examples: `webhook ...`, `theme upload`, `theme activate`, `jobs run`, `image upload`, and create/copy or resource-create families that still have no saved before-state path.
- Snapshot-backed delete examples: `post delete`, `page delete`, `tag delete`, `tag delete-zero`, and `tag merge`.

Ghost-specific:
- Post updates require `updated_at` (collision-safe). The tool always GETs the latest post before PUT.
- Post tag/author arrays are replaced, not merged. The tool always merges by GET first.
- Member/newsletter updates require `updated_at`. The tool always GETs first and verifies requested fields after the write.

## Post body edits

`post body set-captions` only operates in **HTML card mode** (lossless, predictable).
If the post body is not a single HTML card, the tool refuses and explains why.

Writes use `PUT /admin/posts/{id}/` with a `source=html` query param and the updated `html`.
After the write, the tool re-fetches the post and verifies that re-running the same transform would produce **zero further changes** (idempotence check).

Note: the vendored Ghost docs only show `source=html` for **creating** posts (`POST`), not for `PUT`. If your Ghost instance rejects `source=html` on update, the command will fail with the full HTTP error response.

## Post body edits (Lexical mode)

`post bodylex ...` commands operate on the post’s **Lexical** field (the normal Ghost editor format).

Rules:
- Dry-run by default; writes require `--apply`.
- By default, applying edits to a **non-draft** post is refused unless you pass `--allow-published` (or use `--require-current draft`).
- After a write, the tool re-fetches the post and verifies that re-running the same transform would produce **zero further changes** (idempotence check).

Current scope:
- Only “image” nodes are edited (replace `src`, set `alt`/`caption`/`title`, insert by cloning a template image node).
- `replace-many` applies multiple image swaps in one post update (faster), but still uses the same refusal + idempotence verification rules.
- `delete-by-src` removes matching image nodes (exact match, refuses on ambiguity).

### Paid link compliance (Lexical links)

Some affiliate/paid link compliance requires a link `rel` that includes:

`noreferrer noopener sponsored nofollow`

This tool supports safe, Lexical-only link rel updates:
- `post bodylex set-amazon-link-rel`: targets Amazon links only (Lexical link nodes).
- `post bodylex set-paid-link-rel`: targets paid links by host or by “all external” (Lexical link nodes).

Important:
- Only touches Lexical `type="link"` nodes (it does not modify links inside HTML cards).
- Preserves existing rel tokens and only adds missing tokens.
- Dry-run by default; applying is verified by idempotence.

## Converting Mobiledoc to Lexical

Some imported posts are `mobiledoc` (older Ghost editor format).

To convert a Mobiledoc post to the modern editor format (Lexical), the tool can re-send the post’s current `html` via `source=html`, which prompts Ghost to generate a Lexical document:
- Use `post convert-from-html --from-mobiledoc` (dry-run by default; writes require `--apply --yes`).
- This family is snapshot-backed on `--apply`, so the receipt points to the saved local snapshot files under `backup-snapshots/`.

## Audit (read-only)

`post audit` is a read-only checklist helper used during migration. It flags common issues:
- slug suffixes that look ID-like
- missing meta description
- feature image missing alt/caption
- body images still pointing at WordPress uploads
- missing alt/caption on body images
- duplicate body images

Optional (caption consistency):
- `--enforce-caption-policy` flags body captions that don’t end with either:
  - `(stock image; for illustration only).`
  - `(original infographic by the publisher).`
It also checks the feature image caption when a feature image is set.

## Tags (read-only + safe cleanup)

- `tag list` and `tag audit` are read-only.
- `tag delete` and `tag delete-zero` are destructive:
  - Dry-run by default; writes require `--apply`.
  - Bulk deletion requires `--apply` **and** `--yes`.
  - After a delete, the tool verifies the tag is gone by doing a GET and expecting `HTTP 404`.

## `source=html` verification (posts + pages)

Ghost normalizes HTML when you update with `source=html` (examples: `&` → `&amp;`, auto-added heading `id=...`, link `rel/target`, internal absolute ↔ relative URLs).

Strict string equality (`expected_html == returned_html`) can fail even when the update is correct.

For `post patch` / `page patch` with `--source html`, the tool verifies using a best-effort normalization:
- unescape HTML entities
- ignore auto-added heading IDs
- ignore auto-added `<a>` `rel`/`target`
- normalize internal absolute URLs to relative for `href`/`src`
- collapse whitespace

Extra safety:
- If the patch only changes `html` but normalized HTML is already equal, the tool treats it as a no-op and does not write.
- If verification fails, the tool does not print full HTML; it reports length + sha256 instead.
