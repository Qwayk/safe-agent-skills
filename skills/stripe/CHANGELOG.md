# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Pinned Stripe OpenAPI snapshot inventories (`official_operations_*.txt`, `official_commands_*.txt`) with offline validation.
- Explicit `stripe-api-tool api ...` command surface (one subcommand per pinned OpenAPI operation).
- Stripe safety model enforcement: dry-run plans, apply gates, money-moving acknowledgements, connected account allowlists, and deterministic idempotency keys.

### Changed
- Stripe API write operations now require explicit no-snapshot approval before HTTP when safe before-state capture or provider backup support is not available. Dry-run plans, idempotency, drift checks, connected-account allowlists, and read-only live calls still work.

### Fixed
- CLI template: ensure argument/usage errors in `--output json` mode emit exactly one JSON error object (no argparse usage text).

### Removed
