# Proof and verification

Ghost proof should answer a simple question: what has actually been checked for posts, pages, members, newsletters, offers, themes, and webhooks, and what still needs live credentials, permissions, or reviewer judgment?

You do not need to run every command before using the skill. Start with the evidence that matters most: the last verified date, the smoke checks, the saved example outputs, and the known failure cases.

If you only check one thing, check read proof and write-plan refusals before trusting live content, member, theme, or webhook changes.

## Current proof summary

Last verified (UTC): 2026-06-11

## Smoke commands

Offline-only:

- Unit tests: `python3 -m unittest -q`
- CLI version output (no network): `ghost-api-tool --output json --version`
- CLI help output (no network): `ghost-api-tool --output json --help`

Requires Ghost Admin API access:

- Auth check: `ghost-api-tool auth check`
- Basic reads:
  - `ghost-api-tool tag list --limit 5`
  - `ghost-api-tool tier list --limit 5`
  - `ghost-api-tool offer list --limit 5`
  - `ghost-api-tool post find --limit 1`

Requires Ghost Content API access:

- Content API settings (no Admin key needed): `ghost-api-tool content settings get`
- Content API browse (small page size): `ghost-api-tool content posts list --limit 1 --page 1`
- Content API read by slug: `ghost-api-tool content posts get --slug welcome`

## What can go wrong

- Auth failures (bad Admin API key, wrong API URL, wrong `Accept-Version`) cause `auth check` and other API calls to fail.
- Content API failures (missing Content API key or wrong Content API URL) cause `ghost-api-tool content ...` calls to fail.
- Some posts are `lexical` (modern) and some are `mobiledoc` (older imports). Always inspect first and use the correct command family.
- Write commands are dry-run by default; applying without reviewing a plan can cause unwanted edits. Prefer:
  - dry-run → review → apply → verify
- Theme activation is high-impact, so apply must have either saved before-state or explicit no-snapshot approval plus clear receipt evidence.
- Ghost does not provide a webhook get/list endpoint. Webhook create/update/delete therefore need explicit no-snapshot approval where apply is supported, or a safe refusal when the tool cannot verify or execute the action safely. The tool still uses the local `.state/webhooks/index.jsonl` ledger as proof (secrets redacted).
- Webhook, theme, standalone image upload, wrapper job runs, and create-only families need plan-first review, explicit no-snapshot approval where apply is supported, and a safe refusal only for real blockers.
- In `--output json` mode, any extra stdout breaks downstream parsing; unit tests enforce the “one JSON object” contract.

## Verification

- Snapshot-backed apply receipts now expose `recovery.end_state = snapshot_plus_restore` together with concrete snapshot evidence (`backups`, `snapshots`, and `rollback_plan.meta_paths`).
- Clearly labeled irreversible families now expose `recovery.end_state = irreversible_and_clearly_labeled` instead of generic rollback wording.
- Snapshot-backed apply families save before/after snapshots under `backup-snapshots/` next to your `--env-file`.
- Run artifacts: write-capable commands save plan/receipt/audit under `.state/runs/<run_id>/` (see `ghost-api-tool runs list` / `ghost-api-tool runs show`).
- Proof artifacts (committed, redacted): `docs/examples/plan.example.json`, `docs/examples/receipt.example.json`, `docs/examples/outputs/`.

## What to inspect

- Command reference: `docs/command_reference.md`
- Safety model: `docs/safety_model.md`
- API coverage: `docs/api_coverage.md`
- References: `docs/references.md`
- Engineering notes: `docs/engineering_notes.md`
