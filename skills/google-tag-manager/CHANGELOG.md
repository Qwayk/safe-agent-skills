# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Scaffolded `gtm-api-tool` (Google Tag Manager API v2) from the Python API tool template.
- Add default request throttling and read-only retries (`GTM_MIN_DELAY_S`, `GTM_READ_RETRIES`).
- Add `docs/risk_gates.md` (explicit risk → flag mapping).

### Changed
- Default `GTM_SCOPES` to the full scope set from the pinned discovery snapshot (override for least-privilege).
- Write safety gates now match risk levels:
  - medium writes: `--apply` (plan-in optional)
  - high/irreversible writes: `--apply --yes --plan-in` (+ `--ack-irreversible` for irreversible)

### Fixed
- Ensure argument/usage errors in `--output json` mode emit exactly one JSON error object (no argparse usage text).
- Make `--timeout-s` affect real HTTP requests.

### Removed
