# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added
- NameBright-specific README, quickstart, command reference, safety, and proof documentation.
- Added explicit NameBright configuration contract with `NAMEBRIGHT_CLIENT_ID`, `NAMEBRIGHT_CLIENT_SECRET`, and `NAMEBRIGHT_TIMEOUT_S`.
- Added tracked agent wrapper guidance under `skills/namebright-safe-cli/SKILL.md`.
- Documented and aligned all 61 command entries as implemented and live-unverified.

### Changed
- Removed template examples and placeholders that implied unsupported command modes.
- Marked API coverage as implementation-complete for all documented operations.
- Updated docs to include strict acknowledgment paths for spend, ownership, external message, and destructive actions.

### Fixed
- Clarified no base URL override and fixed-output behavior in docs/configuration and authentication guidance.
- Replaced jobs and demo placeholders with explicit unsupported/placeholder notes for this tool.
- Contact writes now bind redacted plan data to SHA-256 digests of the requested contact fields and complete raw before-state. Apply refuses raw contact drift before a provider write, and contact verification reports only safe field names.
- Replaced ambiguous ownership-transfer wording with NameBright account-push language in user-facing docs.

### Removed
- Template-only `AGENTS.md` scaffolding text and placeholder demo instructions.
