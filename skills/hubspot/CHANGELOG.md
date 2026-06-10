# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Added customer-facing alignment for the shipped HubSpot command surface and private app onboarding path.
- Added skill wrapper docs for real tool use:
  - `skills/AGENTS.md`
  - `skills/hubspot-safe-cli/SKILL.md`
- Added explicit `before_state` status to HubSpot dry-run plans.

### Changed
- Changed HubSpot write apply behavior so live writes require safe before-state capture or explicit no-snapshot approval before HubSpot HTTP.
- Updated docs, examples, and skill guidance to treat HubSpot writes as plan-first with explicit no-snapshot approval when no saved snapshot is available.
- Rewrote command reference to list real global flags, onboarding/auth/runs commands, and each HubSpot family with usage patterns and examples.
- Reworked authentication, onboarding, configuration, and safety docs from generic template text to HubSpot-specific instructions.
- Updated proof and engineering notes with concrete portfolio-build status and remaining live-auth dependency.
- Removed unshipped scaffold leftovers from the shipped tool folder and replaced the old jobs test with real HubSpot runtime coverage.

### Fixed
- Fixed the old apply path that could send HubSpot writes without a before-state snapshot or provider backup.
- CLI template: ensure argument/usage errors in `--output json` mode emit exactly one JSON error object (no argparse usage text).
- Deleted unsupported `demo` and `jobs` scaffold files, removed old jobs examples/docs, and aligned audit/test coverage to the real shipped HubSpot surface.
