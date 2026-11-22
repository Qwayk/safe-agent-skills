# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### November 22, 2026

- Use the selected dates for each comparison and label reports that stop early.
- Preserve placement and other breakdowns as separate rows in exports.
- Start on Marketing API v25.0 by default. Use the same settings file in onboarding and the account check.
- Include the skill, setup example, and docs in the source download.

### Earlier work

### Added
- Initial read-only Meta Ads (Marketing API) tool scaffold.
- GET-only Graph client with pagination and token-safe verbose logging (redacts `access_token` in URLs).
- Data-driven built-in presets system (`presets list/show`) for common workflows.
- Snapshot export (`snapshot export`) for analysis-ready packs:
  - stable folder layout with `manifest.json` + normalized `tables/*.jsonl`
  - `manifest.json` includes `schema_version: "1"` plus join keys and request/error inventory
  - per-run `.state/` artifacts (`.state/runs/<run_id>/audit.jsonl` + `.state/runs/index.jsonl`)
  - optional opt-in asset downloads (`--download-assets`) with overwrite controls and an `assets` table
- Read-only command families:
  - `ad-accounts`, `campaigns`, `ad-sets`, `ads`, `creatives`, `images`, `videos`
  - `insights get`
  - `insights compare`
  - `creatives anatomy`
  - `previews get`
- Added customer-ready agent skill packaging and install guidance.
- Added reporting and creative review guides and saved redacted examples under `docs/examples/outputs/`

### Fixed
- Keep `--output json` contract for argument/usage errors and remote Graph API errors.
- Redact `access_token` from Graph paging URLs before returning `paging` in stdout JSON.

### Removed
- Removed the generic `graph` bridge command; use explicit read-only commands instead.
