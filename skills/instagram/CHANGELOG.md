# Instagram Tool Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Initial scaffold of `instagram-api-tool` from `python-api-tool`.
- Added a blocked before-state contract to every write plan.

### Changed
- Renamed package namespace to `instagram_api_tool`.
- Renamed CLI script and project name to `instagram-api-tool`.
- Write apply now requires command-specific before-state support or explicit no-snapshot approval before Instagram provider writes, local token-file writes, or receipt output.

### Fixed

### Removed
