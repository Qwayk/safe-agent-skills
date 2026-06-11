# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Vendored GA4 discovery snapshots + committed method/command inventories.
- Explicit discovery-derived CLI commands: `admin v1alpha`, `data v1beta`, `data v1alpha`.
- Risk classification + apply gates + plan/refusal workflow for discovery methods.
- Secret redaction for stdout JSON, plans/refusals, and audit logs (includes GA4 `secretValue`).
- Added customer-ready agent skill packaging and install guidance.
- Write dry-run plans now include an explicit `before_state` contract.

### Changed
- Updated docs from template to GA4-specific usage and coverage definition.
- GA4 discovery writes, demo writes, and jobs write actions now require explicit no-snapshot approval before provider HTTP or stub receipt output when operation-specific before-state capture support is not available.

### Fixed
- N/A

### Removed
