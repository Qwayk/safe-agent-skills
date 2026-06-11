# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added

- Built the TikTok Marketing safe agent CLI with real operation coverage from the pinned official manifest (`240` operations).
- Added safety-first API flow: plan-first execution, run-aware history artifacts, and explicit write gates.
- Added auth helper commands (`auth check`, `auth token set`, `auth token status`) tied to TikTok token and app credentials.

### Changed

- API write applies require explicit no-snapshot approval before provider HTTP and receipt output when operation-specific before-state or provider-backup support is not available.
- Updated safety wording to match shipped behavior: write apply attempts require `--live`, `--apply`, `--plan-in`, `--yes`, `--ack-irreversible` when needed, and explicit no-snapshot approval when no before-state can be saved.
- Clarified that write verification is currently an explicit no-snapshot approval check.
- Public-facing README, docs index, onboarding, quickstart, safety copy, use cases, and proof docs were rebuilt into the newer user-first TikTok Marketing skill pattern, and the README contract test was added.

### Fixed

- Keep JSON output clean in `--output json` mode for CLI and runtime errors.

### Removed

- Removed leftover non-TikTok wording from user-facing docs and aligned the guidance to the live tool behavior.
