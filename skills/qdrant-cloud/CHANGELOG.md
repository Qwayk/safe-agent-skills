# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Initial Qdrant Cloud safe CLI (`qdrant-cloud-api-tool`).
- Vendored `qdrant-cloud-public-api` protos (pinned commit) + generator for canonical inventories.
- Explicit per-RPC commands with `--live` gate, plan-first ordinary write refusals, provider backup/restore receipts, and risk acknowledgements.
- Write plans now include `safety.before_state` so ordinary writes clearly show the before-state blocker.

### Changed
- Clarified setup docs and agent instructions to quote `QDRANT_CLOUD_API_KEY` when needed and prefer `--env-file` when the real `.env` lives outside the tool folder.
- Ordinary write apply now requires operation-specific before-state, provider-backup capture, or explicit no-snapshot approval before Qdrant Cloud HTTP.
- The provider backup/restore live exception is narrowed to `create-backup`, `restore-backup`, and `create-cluster-from-backup`.

### Fixed

### Removed
