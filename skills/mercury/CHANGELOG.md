# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Mercury API v1 read-only CLI (GET-only) with full v1 GET coverage ledger.
- Safe local exports: transactions export to JSON/CSV (file writes gated by `--apply`/`--yes`).
- Safe local downloads: statement PDFs, invoice PDFs, and invoice attachments (file writes gated by `--apply`/`--yes`).
- Agent Skills wrapper package and installation docs.

### Changed
- Read-only commands now emit minimal JSON by default (no run/artifact path provenance); exports/downloads still include run history + proof paths.
- Docs and committed examples updated to be Mercury-specific and consistent with “no Mercury writes”.
- Public-facing README, docs index, onboarding, quickstart, safety copy, use cases, and proof docs were rebuilt into the newer user-first Mercury skill pattern, and the README contract test was added.

### Fixed
- JSON output contract for argparse errors (exactly one JSON object; no argparse usage text).

### Removed
