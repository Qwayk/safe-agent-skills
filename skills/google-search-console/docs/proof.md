# Proof and verification

Google Search Console proof should answer a simple question: what has actually been checked for sites, search analytics, sitemaps, URL inspection, and ownership data, and what still needs live credentials, permissions, or reviewer judgment?

You do not need to run every command before using the skill. Start with the evidence that matters most: the last verified date, the smoke checks, the saved example outputs, and the known failure cases.

If you only check one thing, check property/report proof and sitemap or ownership plan evidence before trusting Search Console work.

## Last verified (offline)

- Date (UTC): 2026-03-05
- Tool version: 0.1.0
- Provider API: Google Search Console API v1 (pinned discovery snapshot)

## Smoke checks

Run inside the tool folder:

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e '.[dev]'`

2) Version (no `.env` required):
- `gsc-api-tool --output json --version`

3) Coverage validation (offline):
- `gsc-api-tool --output json operations validate`

4) Representative write dry-run (offline; creates a plan only):
- `gsc-api-tool --output json --env-file .env.example --run-id 2026-03-05T000000Z_example sites add --site-url https://example.com/`

## Example outputs (committed, redacted)

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

## What can go wrong

- Missing/invalid credentials → verify with `gsc-api-tool auth check` failing without printing token values.
- Wrong OAuth scopes (read-only vs write) → verify write methods refuse or error cleanly; confirm no writes occurred when `--apply` is absent.
- Write safety drift → verify deletes refuse without `--apply --yes --ack-irreversible --plan-in`.
- Inventory drift (Google changes the API) → verify `gsc-api-tool operations validate` fails with a clear reason and method count.

## Links

- Sources: `docs/references.md`
- Coverage mapping: `docs/api_coverage.md`
- Example outputs: `docs/examples/`
