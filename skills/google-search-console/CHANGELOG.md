# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Initial `gsc-api-tool` release for Google Search Console API v1.
- Pinned official discovery snapshot + derived inventories and offline validation (`operations validate`).
- One explicit CLI command per discovery method (11 total), plus plan/apply safety gates for writes.
- Customer-ready docs + proof pack + `skills/gsc/SKILL.md`.

### Changed

### Fixed
- JSON output contract: argument/usage errors emit exactly one JSON error object (no argparse usage text).

### Removed
