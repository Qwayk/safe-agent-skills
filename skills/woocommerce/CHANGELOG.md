# Changelog

All notable changes to this tool will be documented in this file.

## [Unreleased]

### Added
- Initial WooCommerce REST API v3 tool scaffold with explicit command coverage for the official v3 docs index.
- Coverage-first operation catalog and generated `docs/api_coverage.md`.
- Safe plan-first writes with local run artifacts and plan files.
- WooCommerce onboarding, auth check, and operations inventory commands.
- Write dry-run plans now include an explicit `before_state` contract.

### Changed
- WooCommerce live write apply now requires operation-specific before-state capture or explicit no-snapshot approval before provider HTTP, and approved supported writes emit receipts with recovery limits.
