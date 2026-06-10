# Proof pack

Last verified (UTC): 2026-02-03

Notes:
- This proof pack is validated via unit tests only (no live Pinterest API calls are required for repo CI).
- Committed examples under `docs/examples/` are synthetic/redacted and are provided as shape references.

Note: you don’t need to run these commands yourself. They exist so you (or your reviewer/agent) can audit behavior and prove what happened.

## Smoke / validation

From the tool folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
```

## Output contract

- Default output mode is JSON: `--output json`.
- In JSON mode, every invocation emits exactly one JSON object to stdout (including usage errors and `--version`).

## Examples (committed, redacted)

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/error.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json` (current refusal shape, not a successful write receipt)

## What can go wrong

- Missing/insufficient scopes: inventory may work but analytics endpoints can fail depending on app permissions and account tier.
- Ads/catalogs access: ad account and shopping/catalog endpoints may require additional scopes, Business Access roles, and/or account tier.
- Audit snapshot optional exports: `--include-ads/--include-catalogs/--include-conversions` require `--ad-account-id`; `--include-business-access` requires `--business-id` (missing IDs become warnings; no guessing).
- Expired access tokens: use refresh-token auth or re-generate an access token as described in `docs/authentication.md`.
- Writes are safety gated and currently requires explicit no-snapshot approval before live changes: write families are dry-run by default, plans include blocked `before_state`, confirmed apply attempts require the normal flags and then require explicit no-snapshot approval before Pinterest writes or successful receipts.

Not covered (intentional): any write surface not documented in Pinterest API v5 (example: `catalogs update`).
