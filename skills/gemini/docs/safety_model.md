# Safety Model

The Gemini API can read models, generate content, count tokens, upload files, create caches, manage corpora, change permissions, and delete resources. This tool keeps those jobs separated so an agent can inspect first and change later.

## Runs Directly

These commands do not change Gemini account state:

- `models list` and `models get`
- generation and streaming generation
- embedding and token counting
- operation polling
- file, generated-file, document, corpus, cache, and file-search reads

The tool still redacts `GEMINI_API_KEY` from command output and receipts.

## Requires A Plan First

These commands create a dry-run plan unless `--apply` is used with a reviewed plan:

- file uploads, file registration, and file deletes
- cached content create, patch, and delete
- corpora create/delete and permission changes
- tuned model create, patch, delete, permission changes, and ownership transfer
- file search store create, import, upload, document delete, and store delete
- batch cancel, batch delete, and batch update operations

## Apply Rules

A live state-changing apply requires:

- `--plan-in <plan.json>`
- `--apply`
- `--yes`
- `--ack-no-snapshot` when Gemini has no safe before-state snapshot
- `--ack-irreversible` for destructive, cancel, delete, or ownership-transfer operations

Receipts are written when `--receipt-out` or run artifacts are enabled. The receipt records the redacted request and provider response. It does not claim rollback unless a command really has a rollback path.

## Private Data

Prompts, uploaded files, cached content, and generated output can contain private data. Keep request JSON files local, review them before sending, and do not paste secrets into chat.
