# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- New tool: Shopify Admin SafeCLI (`shopify-admin-api-tool`) with pinned Admin GraphQL API version `2026-01`.
- Official inventory snapshots and extracted canonical operation list (queries + mutations).
- Explicit CLI command surface for every top-level query/mutation in the pinned inventory.

### Changed
- Mutation live apply now requires operation-specific before-state capture or explicit no-snapshot approval before Shopify HTTP. Dry-run plans still work and include the before-state limitation.

### Fixed
- Ensure argument/usage errors in `--output json` mode emit exactly one JSON error object (no argparse usage text).

### Removed
