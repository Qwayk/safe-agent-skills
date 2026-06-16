# Proof and verification

Microsoft Ads proof should answer a simple question: what has actually been checked for accounts, campaigns, budgets, ads, keywords, audiences, and reports, and what still needs live credentials, permissions, or reviewer judgment?

You do not need to run every command before using the skill. Start with the evidence that matters most: the last verified date, the smoke checks, the saved example outputs, and the known failure cases.

If you only check one thing, check account/campaign proof and budget, ad, keyword, or batch-plan evidence before trusting ad changes.

## Last verified

- Date (UTC): 2026-03-04
- Verified by: local command execution and unit tests
- Tool version: 0.1.0
- Provider API version (if applicable): Microsoft Advertising API v13
- Environment: local `prod` config with SOAP writes requires explicit no-snapshot approval before provider HTTP; endpoint docs remain in `docs/official_web_service_addresses_bingads-13_2026-03-04.md`
- Blessed local validation: `.venv/bin/python -m unittest -q` -> `Ran 28 tests in 0.907s OK`

## Smoke checks

Run inside the tool folder:

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2) Version (no `.env` required):
- `msads-api-tool --output json --no-artifacts --env-file examples/example.env --version`

3) Auth/config check (read-only):
- `msads-api-tool --output json --no-artifacts --env-file examples/example.env auth check`

4) One representative read query:
- Offline plan (no network):
  - `msads-api-tool --output json --no-artifacts --env-file examples/example.env customer-management get-accounts-info`
- Live read (requires credentials + explicit opt-in):
  - `msads-api-tool --output json --no-artifacts --env-file examples/example.env --live customer-management get-accounts-info`

## Example outputs (redacted)

These files are committed (unlike `.state/`):
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json` (missing-approval refusal example; kept under the old filename for compatibility)

## What can go wrong

- **Invalid API key / wrong scopes** → verify with `--live auth check` returning `ok=false` and a clear error type; confirm no writes occurred.
- **Rate limiting** → verify the CLI surfaces a non-secret retry/backoff hint; confirm it does not loop/retry-storm.
- **Pagination surprises** → verify results include paging metadata or clear “next page” hints in JSON/text mode.
- **Write safety drift** → verify writes require `--apply` (and `--yes` / `--plan-in` / `--ack-irreversible` when risk requires), then require explicit no-snapshot approval before SOAP HTTP until before-state capture exists.

## Links

- Sources used: `docs/references.md`
- Coverage main reference: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`
