# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

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
- Agent Skills wrapper package (`skills/meta-ads-api-safe-cli/`) and docs (`docs/skills_wrappers.md`).
- Media-buyer and agent docs packs:
  - `docs/media_buyer_quickstart.md`, `docs/winning_ads_workbook.md`, `docs/agent_recipes.md`
  - new redacted example outputs under `docs/examples/outputs/`

### Fixed
- Keep `--output json` contract for argument/usage errors and remote Graph API errors.
- Redact `access_token` from Graph paging URLs before returning `paging` in stdout JSON.

### Removed
- Removed the generic `graph` bridge command; use explicit read-only commands instead.
