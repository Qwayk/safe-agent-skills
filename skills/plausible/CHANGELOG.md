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

- Traffic results show when more rows are available. With `--all`, an early end before Plausible's stated total returns an incomplete result.
- `stats validate` works without credentials. The connection check rejects replies without Stats results, and HTTP errors hide the configured keys.
- A site update checks the requested values before marking them verified.
- The source archive includes the skill, settings example, query examples and guides.

- Fix `NameError: Path is not defined` crash when running the CLI.

### Changed

- The weekly report covers pages, sources and goals. Use the membership report for membership counts. Missing goals show as unavailable.

- In `--output json`, usage/parse errors now return exactly one JSON object to stdout.
- `--version` now respects `--output` (machine-readable in JSON mode).
- Support Python >=3.11 runtime (was >=3.12).
- Rewrote the public Plausible README so the first screen leads with real jobs, safety, and the first user action instead of internal tool wording.
- Aligned Plausible docs with the live event-send safety contract, including explicit no-snapshot approval and best-effort verification wording.
