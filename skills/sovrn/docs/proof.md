# Proof and verification

Sovrn proof should answer a simple question: what has actually been checked for publisher commerce, advertising reports, merchants, links, and performance data, and what still depends on account access, provider permissions, public API limits, or reviewer judgment?

You do not need to run every command before using the skill. Start with the evidence that matters most: the last verified date, the smoke checks, the saved example outputs, and the known failure cases.

If you only check one thing, check merchant/report proof and saved output examples before trusting publisher performance summaries.

## Last verified

- Date (UTC): `2026-06-08`
- Verified by: `Codex`
- Tool version: `0.1.0`
- Provider API version (if applicable): `See the live endpoint docs in docs/references.md`
- Environment: `Local build review only. Live vendor proof not captured yet.`

## Smoke checks

Run inside the tool folder:

1. Create venv and install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2. Version check with no `.env` required:
- `sovrn-safe-cli --output json --version`

3. Local auth check:
- `sovrn-safe-cli --output json auth check`

4. One representative Commerce read query:
- `sovrn-safe-cli --output json commerce campaigns get --search PRIMARY`

5. One representative Advertising read query:
- `sovrn-safe-cli --output json advertising reports account get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions auction`

## Example outputs (redacted)

These committed redacted examples already exist:

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/outputs/commerce_campaigns_invalid_secret.json`

Current meaning:

- the version example proves the shipped CLI identity and version output shape
- the auth example proves the real local config-check shape
- the campaigns 401 example proves the live official endpoint path and redacted error handling
- a positive live-success example still needs a real Sovrn credential set
- use `docs/live_proof_capture.md` to capture the missing success examples when credentials are available

Planned success-example paths, once credentials are available:

- `docs/examples/outputs/commerce_campaigns_success.json`
- `docs/examples/outputs/commerce_links_check_success.json`
- `docs/examples/outputs/commerce_comparisons_success.json`
- `docs/examples/outputs/advertising_account_success.json`

## What can go wrong

- **Wrong auth shape** → verify the command fails with a clear message about the missing Commerce secret key, site key, Advertising API key, or publisher ID.
- **Rate limiting** → verify the CLI surfaces a non-secret retry/backoff hint; confirm it does not loop/retry-storm.
- **Pagination surprises** → verify results include paging metadata or clear “next page” hints in JSON/text mode.
- **Coverage drift** → verify any new command family appears in `docs/api_coverage.md` before it is presented as shipped.

## Links

- Sources used: `docs/references.md`
- Coverage main reference: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`
