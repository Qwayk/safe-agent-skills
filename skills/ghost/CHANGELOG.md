# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Customer-ready proof pack docs under `docs/` (proof, references, API coverage, engineering notes, examples).
- Admin API coverage expansions: tag create/update; post/page copy; tier and offer CRUD; theme upload/activate; webhook create/update/delete.
- New safety acknowledgements: `--ack-theme-change` (theme activation) and `--ack-no-verify` (webhook changes).
- Read-only Ghost Content API command family: `ghost-api-tool content ...` (posts/pages/tags/authors/tiers/settings).

### Changed
- Docs: `docs/quickstart.md` now shows the minimal customer install first, with dev extras optional.

## [0.1.0] - 2025-12-22

### Added
- Initial Ghost Admin API CLI with safe-by-default write gating (`--apply` / `--yes`), backups, and run artifacts.
