# Proof pack

## Last verified

- Date (UTC): `2026-06-04`
- Verified by: local command execution, generated redacted plan/refusal examples, and unit tests
- Tool version: `0.1.0`
- Blessed local validation: `.venv/bin/python -m unittest -q` -> `Ran 35 tests in 1.801s OK`
- Base URL target in committed examples: `http://example.invalid`

You do not need to run these commands yourself for normal customer use. They exist for auditing, proof, and repeatable review.

## What is proved now

- The official documented Merchant surface is accounted for in `docs/api_coverage.md`:
  - `353` official documented operations accounted for
  - `224` explicit commands shipped
  - `129` official operations documented but intentionally not shipped because they are `v1beta` migration-only surface
- The shipped command tree now includes:
  - stable `v1` families
  - active official `v1alpha` families still published in the current Merchant reference
  - the official reference-only `loyaltycustomers_v1alpha` and `youtubeshoppingcheckout_v1alpha` methods
- Write safety behavior is locally proved:
  - write commands stay dry-run by default
  - write plans mark before-state capture as required and currently unsupported
  - high-risk and irreversible applies require matching `--plan-in`
  - irreversible applies also require `--ack-irreversible`
  - plan drift is validated against family, method, path, query, body, risk level, and environment fingerprint
  - live write attempts require explicit no-snapshot approval when no saved snapshot is available, and missing-approval attempts say that no Google Merchant write was sent
- Google path templates with patterns like `{parent=accounts/*}` are handled correctly in the live request builder and are covered by tests.
- Redacted example outputs are current and committed:
  - `docs/examples/plan.example.json`
  - `docs/examples/receipt.example.json` (missing-approval refusal output; kept under the old filename for compatibility)
  - `docs/examples/outputs/version.json`
  - `docs/examples/outputs/auth_check.json`

## What is local-only or mocked

- `docs/examples/plan.example.json` is a local dry-run example against `http://example.invalid`.
- `docs/examples/receipt.example.json` is a local refusal example against `http://example.invalid`.
- The refusal example proves no provider write is sent when required no-snapshot approval is missing.

## What is not yet live-verified

- No live Merchant API read call has been executed in this workspace with real credentials.
- No live Merchant API write call has been executed in this workspace with real credentials.
- No live verification read-back has been recorded yet for the shipped alpha families.

## Next live checks to run when credentials are available

1. `google-merchant-api-tool --output json auth check`
2. `google-merchant-api-tool --output json accounts list`
3. one controlled dry-run for a medium-risk write and confirm the explicit no-snapshot approval
4. one controlled approved write only when recovery limits are acceptable, then verify with a follow-up read

## Important honesty notes

- This tool is customer-ready for explicit local planning, command discovery, documentation, and safe wrapper usage.
- It is not yet fully live-proved against Google’s production Merchant service in this workspace.
- `docs/api_coverage.md` is the source of truth for what ships, what is only accounted for, and why.
