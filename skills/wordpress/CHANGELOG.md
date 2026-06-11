# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Read-only discovery commands: `discover post-types`, `discover statuses`, `discover taxonomies`.
- Read-only expansion commands: `comments` (list/get), `search` (query), `settings` (get), `terms` (list/get), `users` (list/get), `media find`.
- Safer collection reads: pagination guardrails via `--limit`, `--per-page` (<=100), and `--max-pages` (<=100), with explicit JSON truncation signals.
- Safe term assignment write: `post set-terms` (categories/tags) with dry-run plan, explicit apply, and read-back verification.
- Safer bulk local media download: `media download-batch` with dry-run planning, `--apply --yes` gate, and per-file verification.

## [0.1.0] - 2026-01-23

### Added
- Customer-ready proof pack docs under `docs/` (proof, references, API coverage, engineering notes, examples).
- v2 plan/receipt export flags for write-capable commands (`--plan-out`, `--receipt-out`).

### Changed
- In `--output json` mode, emit exactly one JSON object for parse/usage/help/version flows (no argparse usage text).
