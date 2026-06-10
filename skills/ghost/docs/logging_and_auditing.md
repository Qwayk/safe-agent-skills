# Logging and auditing

## Verbose HTTP logs (`--verbose`)

`--verbose` prints:
- request start line: `METHOD URL (start)`
- request end line: `METHOD URL -> status (ms)`

It does not print `Authorization` headers.

## Audit log (`--log-file`)

`--log-file PATH` writes JSONL records for key operations.
Secrets are redacted.

v2 fields:
- Each row includes `tool`, `version`, `command`, `apply`, `yes`, `env_fingerprint`, and `run_id` (when applicable).
- The tool can also write a per-run audit log under `.state/runs/<run_id>/audit.jsonl` for write-capable commands.

This is intentionally “not pretty”: it’s designed to help you debug quickly.

## Backup snapshots (`backup-snapshots/`)

Snapshot-backed write families write JSON snapshots under `backup-snapshots/` next to your `--env-file` (a "before" snapshot, and then an "after" or "error" snapshot).
The saved plan and receipt expose this as `recovery.end_state = snapshot_plus_restore`.

Clearly labeled irreversible families do not claim those snapshot files as a restore path.
Important dry-run-only examples are `webhook ...`, `theme ...`, `jobs run`, `image upload`, and create/copy or resource-create families.
Webhook proof is stored in `.state/webhooks/index.jsonl`.

## Manual restore (using snapshots)

If a snapshot-backed write did something you don’t want, you can restore manually using the `__before.json` snapshot:

1) Open the snapshot file and copy only the fields you want to roll back (example fields: `title`, `custom_excerpt`, `feature_image`, `feature_image_alt`, `feature_image_caption`, `lexical`, `mobiledoc`, `html`).
2) Put those fields into a new patch file (a JSON object).
3) Dry-run:
   - Post: `ghost-api-tool post patch --id POST_ID --file restore.patch.json`
   - Page: `ghost-api-tool page patch --id PAGE_ID --file restore.patch.json`
4) Apply: re-run the same command with `--apply`.

Notes:
- The tool handles `updated_at` internally (you don’t need to include it in the patch file).
- Restoring tag/author arrays is possible but risky (Ghost replaces arrays). Prefer restoring only the fields you actually changed.
