# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Changed
- Added standard read-only global flags: `--config`, `--log-file`, and `--debug`.
- Onboarding output now separates required, one-of, and optional environment values.
- Wrapper docs and skill text now distinguish unknown requests from documented excluded endpoints.

### Fixed
- Binary metadata output now reports the real HTTP method used for `files download`.
- Proof docs and committed example outputs now match the live runtime shape.

## [0.1.0] - 2026-05-21

### Added
- Read-only Pipedrive CLI built from local endpoint catalog.
- Read commands for shipped `GET` operations across `api_coverage.md`.
- `onboarding` and `auth check` runtime commands.
- Local catalog lookup so runtime does not require internet.
- Metadata-only handling for `files/{id}/download`.

### Changed
- Runtime is clear read-only by design in all docs and wrappers.
- Runtime defaults prefer v2 when both v1 and v2 rows exist for the same command token.
- Output is deterministic one JSON object in all paths.

### Fixed
- CLI config bootstrap and endpoint parsing now return safe JSON errors.
- `PIPEDRIVE_API_DOMAIN` handling now builds `https://<slug>.pipedrive.com` when needed.
- `/api/{version}` URL assembly and cursor pagination extraction now match Pipedrive behavior.

### Removed
