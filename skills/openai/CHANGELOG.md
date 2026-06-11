# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- More inventory refresh utilities and safety tests.
- OpenAI write plans now include a `no_snapshot_available` `before_state` contract and an explicit no-snapshot approval verification plan.

### Changed
- API writes, demo writes, and jobs with write rows now require explicit no-snapshot approval before OpenAI API key use, OpenAI HTTP, or stub receipt output when command-specific before-state support is not available.
- Existing spend-money, irreversible, `--live`, `--yes`, and `--plan-in` gates still run before the broader explicit no-snapshot approval.

### Fixed
- CLI template: ensure argument/usage errors in `--output json` mode emit exactly one JSON error object (no argparse usage text).

### Removed

## [0.1.0] - 2026-03-15

### Added
- pinned OpenAI operations inventory with explicit `api <operation>` commands tied to the official reference,
- deterministic plan/live/apply/verify/receipt gates plus spend-money and irreversible acknowledgements,
- explicit configuration, onboarding, agent extension, and safety docs tailored to OpenAI plus the first skills wrapper.
