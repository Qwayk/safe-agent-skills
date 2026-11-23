# Changelog

All notable changes to this tool are documented here.

## Unreleased

- Added the exact-domain price check for registrations, renewals, and transfers.
- Saved plans check the account. A private receipt records the attempt before sending a change.
- New transfers and SafePay deals can proceed after review when there is no earlier record. SafePay receipts check the domain and terms and show who still needs to confirm.
- Setup keeps the chosen settings file private. Shorter guides keep the August command list and test evidence.

## [0.1.0] - 2026-08-01

### Added
- Write command plan-first flow with credentials-free planning mode.
- No-network behavior for unavailable/plan-only write commands when credentials are not configured.
- All 38 stable operation commands and two local HTTP-501 refusals.
- Fixed-host authentication, encoded path values, 204 and 202 response handling, private-data masking, financial preflight warnings, and reliable-readback limits.

### Changed
- Public docs, examples, coverage, and the tracked `spaceship` wrapper now match the shipped command and safety behavior.
- API coverage availability wording now marks `HTTP-501` entries as developer-preview unavailable.

### Fixed
- `load_config` now supports optional credential enforcement.
- CLI command routing now only enforces auth for commands that need it.
- Prevented credentialless write plans from forcing preflight network calls.

### Limits
- No live Spaceship credential or provider request was used for this source build.
