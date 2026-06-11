# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Initial Unsplash Photos API tool with safe-by-default CLI, mocked unit tests, and proof/docs pack.
- Public read endpoints: user collections (`GET /users/:username/collections`), user statistics (`GET /users/:username/statistics`), and global stats (`GET /stats/total`, `GET /stats/month`).
- Deterministic pagination exports that write local JSON files (`unsplash-api-tool export ...`) with a multi-page `--yes` guard.

### Changed
- Tracked write applies now require explicit no-snapshot approval before Unsplash download-tracking HTTP, local file writes, jobs write rows, or demo stub receipts when real before-state support is not available. Dry-run plans include `no_snapshot_available` before_state metadata.
- Docs: clarify scope as “photos-first” (includes collections/topics/users/search read endpoints).
- Pagination: enforce `--per-page <= 30` consistently across list/search/export commands (per Unsplash docs maximum).

### Fixed
- CLI: ensure argument/usage errors in `--output json` mode emit exactly one JSON error object (no argparse usage text).
