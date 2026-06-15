# Proof and verification

Mercury proof should answer a simple question: what has actually been checked for business banking balances, accounts, transactions, cards, recipients, and local exports, and what still needs live credentials, permissions, or reviewer judgment?

You do not need to run every command before using the skill. Start with the evidence that matters most: the last verified date, the smoke checks, the saved example outputs, and the known failure cases.

If you only check one thing, check account and transaction proof, then confirm no payment-moving workflow is claimed.

## What is already proved

- Mercury is read-only in this skill by design. Non-GET Mercury requests are refused.
- Local exports and downloads stay dry-run first and need `--apply` before any file write.
- Overwrites need `--yes`.
- Signed attachment URLs are redacted from JSON output and run artifacts.

## Last checked

- Local docs and contract alignment rechecked: **2026-06-11 UTC**
- Provider smoke evidence in committed examples: **2026-01-29 UTC**
- Tool version: `0.1.0`
- Provider API version: Mercury API v1

The provider smoke date is older because no live Mercury credentials are stored in this repo. The local suite and committed examples are the proof we can recheck safely here.

## Core smoke checks

Run inside the tool folder:

1. Create a venv and install:
   - `python3 -m venv .venv`
   - `.venv/bin/python -m pip install -e .`
2. Version check:
   - `mercury-api-tool --output json --version`
3. Auth and config check:
   - `mercury-api-tool --output json auth check`
4. One representative read:
   - `mercury-api-tool --output json accounts list`

## Committed example outputs

These redacted example files are committed and safe to inspect:

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/outputs/accounts_list.json`
- `docs/examples/outputs/transactions_list.json`
- `docs/examples/outputs/export_transactions_dry_run.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

## What can still go wrong

- invalid token or wrong base URL
- Mercury-side permission limits
- large exports with the wrong filters or too many pages
- wrong output path for a local export or download
- accidental overwrite of an existing local file

## How to verify the risky parts

- Invalid token or wrong environment: `auth check` should fail clearly, and nothing changes in Mercury.
- Export or download safety: local file writes must still require `--apply`, and overwrites must still require `--yes`.
- Signed URL secrecy: attachment URLs should stay redacted in outputs, plans, receipts, and logs.
- Pagination restraint: exports and reports should still respect their page or limit controls.

## Links

- [API coverage](api_coverage.md)
- [Source references](references.md)
