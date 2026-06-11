# Changelog

## Unreleased

### Added

- API_TOOL_STANDARD v2 proof-pack docs under `docs/` (references, coverage, proof, examples).
- Added customer-ready agent guidance and safety contracts.
- Added customer-ready agent skill packaging and install guidance.
- `--plan-out`, `--receipt-out`, and `--ack-irreversible` flags for safer irreversible write workflows.
- Sites API v1 command family (`site` commands) with read-only reads and apply-gated writes (plans + receipts).
- `event send` optional fields: `--referrer` and `--revenue-currency/--revenue-amount` (PII-safe, refused when suspicious).

### Fixed

- Fix `NameError: Path is not defined` crash when running the CLI.

### Changed

- In `--output json`, usage/parse errors now return exactly one JSON object to stdout.
- `--version` now respects `--output` (machine-readable in JSON mode).
- Support Python >=3.11 runtime (was >=3.12).
