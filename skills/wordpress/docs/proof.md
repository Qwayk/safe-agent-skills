# Proof pack

Last verified (UTC): 2026-01-28

This folder is the customer-ready “proof pack” for `wordpress-api-tool`.

Note: you don’t need to run these commands yourself. They exist so you (or your reviewer/agent) can audit behavior and prove what happened.

## Smoke commands

Offline-only:

- Unit tests: `python3 -m unittest -q`
- CLI version output (no network): `wordpress-api-tool --output json --version`
- CLI help output (no network): `wordpress-api-tool --output json --help`
- Batch media download safety (no network; mocked): see `tests/test_media_download_batch.py`

Requires WordPress API access (read-only):

- Auth check: `wordpress-api-tool auth check`
- Basic reads:
  - `wordpress-api-tool discover post-types`
  - `wordpress-api-tool discover statuses`
  - `wordpress-api-tool discover taxonomies`
  - `wordpress-api-tool comments list --limit 1`
  - `wordpress-api-tool search query --query "test" --limit 1`
  - `wordpress-api-tool terms list --taxonomy categories --limit 1`
  - `wordpress-api-tool media find --limit 1`
  - `wordpress-api-tool post find --query "test" --limit 1`
  - `wordpress-api-tool media get --id 123`
  - (optional, permission-restricted) `wordpress-api-tool users list --limit 1`
  - (optional, often admin-only) `wordpress-api-tool settings get`

## What can go wrong

- Auth failures (missing/invalid Application Password) cause `auth check` and other API calls to fail.
- Some WordPress security/SEO plugins can alter REST API behavior; when unsure, the tool should refuse to write.
- Publishing/status changes are high risk; always dry-run first and prefer `--require-current`.
- Term assignment can be ambiguous when using slugs; the tool should refuse if a slug lookup returns multiple matches.
- In `--output json` mode, any extra stdout breaks downstream JSON parsing; tests enforce the “one JSON object” contract (including parse/usage/help/version flows).

## Verification

- Proof artifacts (committed): `docs/examples/plan.example.json`, `docs/examples/receipt.example.json`, `docs/examples/outputs/`.
- JSON contract tests: `tests/test_cli_json_output_contract.py` and `tests/test_v2_plan_receipt_exports.py`.
- Media updates: verification is a read-back of the edited fields after apply.
- The write families upgraded for this reset also save old state first under `.state/runs/<run-id>/before/`.
- Batch media downloads: verification is per-file existence + size > 0 after download.
- Post-body edits: verification is idempotence (re-running the same transform yields zero changes).
- Term assignment (`post set-terms`): verification is a read-back of the final term IDs (set equality; WordPress does not guarantee ordering).
- Rollback is still manual, but the upgraded write families now save the old state first and point to it in `before_state`.

## What to inspect

- API coverage: `docs/api_coverage.md`
- Use cases: `docs/use_cases.md`
- References: `docs/references.md`
- Safety model: `docs/safety_model.md`
- Example plans/receipts: `docs/examples/`
