# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Initial template release.
- Added real ElevenLabs read commands for `models list` and `usage get`.
- Added plan-first coverage for the entire ElevenLabs non-legacy API (speech, media, workspace, ConvAI, tokens, audio-native, etc.), plus the general operation parser/test guard that enumerates every CLI command from `docs/api_coverage.md`.

### Changed
- Write applies now require explicit no-snapshot approval before ElevenLabs API key use or provider HTTP when the command cannot save real before-state before the provider write. Write plans include `no_snapshot_available` before_state metadata, and successful write receipts record the no-snapshot approval and recovery limit.
- Removed unsupported template-only CLI surface from the public command set (`auth token`, `jobs`, `demo`) so the tool now exposes only supported ElevenLabs workflows.
- Rewrote onboarding, command reference, and use-case docs to be ElevenLabs-specific and non-technical-first.

### Fixed
- CLI template: ensure argument/usage errors in `--output json` mode emit exactly one JSON error object (no argparse usage text).
- `auth check` no longer reports fake OAuth token state for an API-key-only integration.

### Removed
