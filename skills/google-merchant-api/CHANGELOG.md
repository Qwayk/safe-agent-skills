# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added

- Added stable Merchant discovery loader/validator for the 12 requested stable `v1` families.
- Added method inventory support for explicit CLI tokens (`merchantapi.*` method IDs to kebab-case command tokens).
- Added `google-auth` dependency for service-account and OAuth credential loading.
- Added the currently published official Merchant `v1alpha` families and reference-only alpha methods to the shipped explicit surface.
- Added a full per-operation `docs/api_coverage.md` ledger and full shipped `docs/command_reference.md` reference generated from the live inventory.

### Changed

- Reworked auth config to support explicit modes:
  - `service_account_json`
  - `oauth_refresh_token`
  - `adc` (optional)
- Updated onboarding and operational docs with real auth fields and first runnable command examples.
- Removed public top-level `demo` and `jobs` command registrations from the shipped CLI surface.
- Migrated run history and audit-path tests to use real discovery-backed Merchant commands and removed stub-flow docs from customer-facing references.
- Kept the customer wrapper name `google-merchant-api-safe-cli` while intentionally retaining the internal package/binary names `google_merchant_api_tool` and `google-merchant-api-tool` for compatibility in this release.
- Upgraded write safety so high-risk and irreversible applies require matching `--plan-in`, and deletes also require `--ack-irreversible`.
- Added the Wave 3 before-state reset: write plans now mark before-state as required but unsupported, and live write attempts require explicit no-snapshot approval before credentials or provider HTTP when safe before-state capture is not available.
- Refreshed proof docs and committed redacted plan/refusal examples to match the current runtime output.

### Fixed

- Implemented real `auth check` as a safe read command that validates credentials and refreshes when needed.
- Wired nested explicit discovery commands into the parser so commands resolve like:
  - `accounts developer-registration get-account-for-gcp-registration`
  - `accounts list`
  - `accounts products list`
  - `accounts product-inputs insert --body-file product.json`
- Preserved dry-run-first behavior for write-capable methods with plan output when `--apply` is not set.
- Fixed Google path-template handling for placeholders like `{parent=accounts/*}` so manual alpha methods build valid request paths.
