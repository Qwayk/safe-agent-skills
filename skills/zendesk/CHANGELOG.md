# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Initial Zendesk Ticketing (Support) API tool.
  - Pinned official Ticketing OpenAPI snapshot (committed) with offline inventories.
  - Explicit per-operation `zendesk-api-tool api <operation>` commands for 100% snapshot coverage (no generic raw-request bridge).
  - Plan-first safety model for write-like operations: dry-run by default, `--apply` gating, and stricter flags for high-risk/irreversible actions.
- Added explicit `before_state` status to API, jobs, and demo write plans.

### Changed
- Changed write apply behavior so generated API writes, jobs with write actions, and demo writes require explicit no-snapshot approval before Zendesk HTTP or stub receipt output when safe before-state capture is not available.
- Updated docs, examples, proof, and skill guidance to treat Zendesk writes as plan-first with explicit no-snapshot approval when no saved snapshot is available.

### Fixed
- Fixed the old write apply paths that could produce receipts without a before-state snapshot or provider backup.
- CLI template: ensure argument/usage errors in `--output json` mode emit exactly one JSON error object (no argparse usage text).

### Removed
