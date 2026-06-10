# Changelog - qwayk-salesforce-platform-safe-agent-cli

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Initial Salesforce Platform REST API and Bulk API 2.0 command surface.
- Multipart manifest support for documented blob-upload flows.
- Customer-facing docs, proof pack, coverage ledger, and skill wrapper.
- Write dry-run plans now include an explicit `before_state` contract.

### Changed
- Replaced template onboarding, auth, and command references with Salesforce-specific content.
- Removed scaffold leftovers from the shipped command surface and updated environment and job documentation to match the real runtime.
- Salesforce live write apply now requires command-specific before-state capture or explicit no-snapshot approval before provider HTTP.

### Fixed
- JSON-mode argument errors emit exactly one JSON error object.

### Removed
- Archived scaffold docs and non-shipped legacy command modules.
- Generic starter CSV examples that did not reflect Salesforce runtime behavior.
