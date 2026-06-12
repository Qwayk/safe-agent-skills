# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Initial Hacker News read-only CLI with explicit named commands for the full documented v0 HTTP read surface:
  - `auth check`
  - `onboarding`
  - `items get`
  - `users get`
  - `stories top`
  - `stories new`
  - `stories best`
  - `stories ask`
  - `stories show`
  - `stories jobs`
  - `maxitem get`
  - `updates get`
- Deterministic JSON output contract and JSON-safe argparse errors.
- Customer-ready docs, coverage ledger, proof pack, skill wrapper, and committed example outputs.

### Changed
- Rebuilt the README and front-door docs into the public skill pattern so Hacker News now opens with a reader-friendly promise, a clear safe first ask, and honest read-only limits instead of the old internal tool layout.
- Rewrote the README opening again to remove template-sounding safety language and lead with the real user value: understanding what people are discussing on Hacker News.

### Fixed

### Removed
