# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Initial Sovrn scaffold with the locked official coverage ledger and auth split.
- Real named `commerce` and `advertising` command trees for the mapped official Sovrn endpoint surface.
- Shipped skill wrapper files under `skills/sovrn-safe-cli/`.
- Redacted proof examples for version output, local auth shape, and a live invalid-secret Commerce response.
- Expanded validation coverage to 31 passing tests, including command wiring, auth honesty, redaction, rate-limit hint checks, and coverage-sync protection.
- A live-proof capture guide for the remaining success-example step.

### Changed
- Scaffold docs and runtime now use the real Sovrn auth split instead of the old generic token model.
- Coverage docs now mark the mapped CLI surface as implemented, not only planned.
- `auth check` now reports real command-bundle readiness instead of treating any single configured value as enough.
- Front-door docs, proof paths, and examples now match the shipped read-only Sovrn surface and use the repo-standard `docs/examples/outputs/` layout.

### Fixed
- Base CLI runtime: ensure argument/usage errors in `--output json` mode emit exactly one JSON error object (no argparse usage text).
- Redacted comparison site-key path segments, bid-check user-sensitive request fields, and Advertising publisher-presence fingerprints.
- Added a clear 429 retry hint in HTTP error messages without exposing secrets.

### Removed
