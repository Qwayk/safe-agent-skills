# Proof pack (publish-ready evidence)

Date (UTC): 2026-06-04

Last verified (UTC): 2026-06-04

Note: you don’t need to run these commands yourself. They exist so you (or your reviewer/agent) can audit behavior and prove what happened.

Verification method in this repo:
- No live Unsplash API calls are performed in unit tests.
- All HTTP is mocked; tests do assert the URL paths and required headers.

## Smoke commands (no network)

Run inside the tool folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
unsplash-api-tool --output json --version
unsplash-api-tool --output json onboarding --no-write-env
```

## Example live commands (read-only; not run in CI)

Note: These are examples for a customer/auditor. They were not executed as part of this repo’s unit tests (this task run is `plan_only`).

```bash
# New public read endpoints
unsplash-api-tool --output json users collections --username "example_user" --per-page 10
unsplash-api-tool --output json users statistics --username "example_user"
unsplash-api-tool --output json users likes --username "example_user" --per-page 10
unsplash-api-tool --output json search collections --query "minimal" --per-page 5
unsplash-api-tool --output json topics list --per-page 5 --order-by latest
unsplash-api-tool --output json collections list --per-page 5
unsplash-api-tool --output json stats total
unsplash-api-tool --output json stats month

# Deterministic export (multi-page requires --yes)
unsplash-api-tool --output json --yes export photos-list --out exports/photos_page_1_2.json --start-page 1 --max-pages 2 --per-page 10
```

## What can go wrong (and how to verify)

- Missing or wrong access key
  - Symptom: `auth check` fails (HTTP 401 or similar)
  - Verification: run `unsplash-api-tool --output json auth check` (safe, read-only)
- Download compliance
  - `photos download` must not call the tracking endpoint in dry-run mode
  - Current `photos download --apply` also requires explicit no-snapshot approval before the tracking endpoint when no saved snapshot is available
  - Verification: unit tests in `tests/test_unsplash_commands.py`
- Tracked write recovery contract
  - `photos download`, `jobs run`, and `demo write` plans include `no_snapshot_available` before_state metadata and `recovery.strategy = "no_inverse"`.
  - Current apply outputs `refused=true` instead of a successful write receipt.
  - Verification: unit tests in `tests/test_unsplash_commands.py` and `tests/test_jobs.py`
- Local file safety
  - `photos download --dest ...` refuses to overwrite without `--overwrite --apply --yes`
  - Verification: unit tests in `tests/test_unsplash_commands.py`
- Local immediate writes
  - `export ... --out ...`, `auth key set`, and `onboarding` write local files immediately.
  - There is no `--apply` rollback path for these commands; cleanup is manual.
  - Verification: unit tests in `tests/test_unsplash_commands.py` and `tests/test_onboarding_command.py`
- Batch exports (local JSON)
  - Multi-page exports require `--yes` (safe refusal otherwise)
  - `--per-page` is capped at 30 (per official Unsplash pagination maximum)
  - Verification: unit tests in `tests/test_unsplash_commands.py`

## Committed examples (redacted)

- Plans/refusals: `docs/examples/plan.example.json`, `docs/examples/receipt.example.json`
- Outputs: `docs/examples/outputs/version.json`, `docs/examples/outputs/auth_check.json`
