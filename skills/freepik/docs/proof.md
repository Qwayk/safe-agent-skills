# Proof pack

Last verified (UTC): 2026-06-11

This folder is the customer-ready “proof pack” for `freepik-api-tool`.

Note: you don’t need to run these commands yourself. They exist so you (or your reviewer/agent) can audit behavior and prove what happened.

## Smoke commands

Offline-only:

- Unit tests: `python3 -m unittest -q`
- CLI version output (no network): `freepik-api-tool --output json --version`

Requires API access (read-only):

- Auth check: `freepik-api-tool auth check`
- Search (read): `freepik-api-tool search images --query "turkey" --limit 1`
- Search photos shortlist (read): `freepik-api-tool search photos --query "turkey" --limit 5 --shortlist`
- Write jobs CSV (local-only): `freepik-api-tool search photos --query "turkey" --limit 5 --write-jobs jobs.csv --job-format jpg --job-image-size 2000px`
- Shoot-pack IDs + jobs generation: `freepik-api-tool resource shoot-pack --id RESOURCE_ID --write-jobs jobs.csv --job-format jpg --job-image-size 2000px`

## What can go wrong

- Auth failures (missing/invalid API key) cause `auth check` and other read calls to fail.
- Freepik API field changes (missing `is_ai_generated` / `has_prompt`) trigger fail-closed refusals for `download`.
- Current `download --apply` requires explicit no-snapshot approval before the Freepik download/license endpoint, binary fetch, destination file write, or inventory row write.
- `download` refuses re-downloading an asset already in the inventory unless `--force`.
- In `--output json` mode, any extra stdout breaks downstream JSON parsing; tests enforce the “one JSON object” contract (including parse/usage errors).

## Verification

- Proof artifacts (committed): `docs/examples/plan.example.json`, `docs/examples/receipt.example.json`, `docs/examples/outputs/`.
- JSON contract: see `docs/examples/outputs/parse_error.json` and `tests/test_cli_json_output_contract.py`.
- Download safety: see `docs/examples/outputs/download.dry_run.json`, `docs/examples/receipt.example.json`, `tests/test_download_image_size.py`, `tests/test_download_overwrite_guard.py`, and `tests/test_download_ack_no_snapshot.py`.
- Dry-run proof: confirm the output has `before_state.status=no_snapshot_available` and `before_state.approval_required=--ack-no-snapshot`.
- Approved apply proof: confirm the output has `ok=true`, `no_snapshot_approval.acknowledged=true`, `verification.ok=true`, and a row with `file_path`, `sha256`, `download_url`, and `license_url`.
- Missing approval proof: confirm that omitting `--ack-no-snapshot` returns `refused=true` before any licensed download endpoint, destination file write, or inventory row write.
- Confirm outputs include `recovery`: `strategy=no_inverse`, `rollback_ready=false`, `automatic_rollback=false`, `backups=[]`, `snapshots=[]`, `rollback_plan=null`.
- Local helper writes (for example `--write-jobs`, `preview --save-preview`) are not rolled back by this CLI; delete those files manually if needed.

## What to inspect

- API coverage: `docs/api_coverage.md`
- References: `docs/references.md`
- Safety model: `docs/safety_model.md`
- Example plans/receipts: `docs/examples/`
