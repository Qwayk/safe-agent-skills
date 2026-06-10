# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Initial read-only Statuspage status checker tool scaffold.
- Agent Skills wrapper package (`skills/statuspage-api-safe-cli/`) and docs (`docs/skills_wrappers.md`).
- Public skill page source and example files for the mirror flow.

### Changed
- Source docs now own the public-ready Statuspage wording used for the first mirror proof.
- The wrapper skill prompt now matches the public `statuspage` skill behavior and wording.

### Fixed
- Keep `--output json` contract for argument/usage errors.

### Removed
