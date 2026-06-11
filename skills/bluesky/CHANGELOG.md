# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- New `bluesky-safe-cli` package for the official Bluesky API surface.
- Pinned official Bluesky inventory files generated from the official atproto lexicons and Bluesky HTTP reference pages.
- Explicit `api <operation_command>` command surface for 304 official callable lexicons.
- `api ops list` inventory command and pinned coverage ledger in `docs/api_coverage.md`.
- Real Bluesky session helpers: `auth check`, `auth login`, `auth refresh`, `auth logout`, `auth token set`, and `auth token status`.
- Live public read execution for query endpoints and raw websocket frame capture for subscription endpoints.
- Added or updated the customer-ready agent skill prompt.

### Changed
- Switched the user-facing CLI command name to `bluesky-safe-cli`.
- Replaced generic API base/token onboarding with Bluesky handle or DID plus app-password onboarding.
- Replaced starter example outputs with real tool outputs in `docs/examples/`.
- Removed starter-only `jobs` and `demo` commands from the shipped CLI.
- Removed global `--plan-in` flag and related context plumbing.
- Kept write-capable behavior on real shipped commands (`api` + `auth`) while dropping unsupported workflow paths.

### Fixed
- `--output json` parse errors still emit exactly one JSON error object.
- Dry-run plans now redact password and token fields before output or file writes.

### Removed
