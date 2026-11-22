# Changelog

## November 22, 2026

- The source download includes the skill and a fresh install loads all 308 commands.
- Onboarding keeps your settings file. The live connection check reports an error if Klaviyo rejects the key or returns no account.
- Flow status changes require a reviewed plan and confirmation. When you apply a saved upload plan, the file contents still need to match.
- Job receipts show acceptance and how to check progress when there’s a matching status command. A lost write reply leaves a receipt that says to check before retrying.
- Setup, examples, and approval steps live in fewer guides.

All notable changes to this project are documented here.

This tool follows Keep a Changelog style.

All notable changes to this project are documented here.

This tool follows Keep a Changelog style.

## [Unreleased]

### Added
- Added explicit `before_state` status to Klaviyo API operation plans.
- Initial shipped Klaviyo safe CLI now covers `308` stable operations from revision `2026-04-15`.
- Product scope is documented as stable-only, with `87` beta operations excluded by product choice.
- The shipped wrapper `klaviyo-safe-cli` is documented for agent runtimes.
- Added a README public contract test so the source README keeps the publish-ready skill-page shape.

### Changed
- Changed write apply behavior so Klaviyo writes require safe before-state capture or explicit no-snapshot approval before Klaviyo HTTP, and approved supported writes emit receipts with recovery limits.
- Updated docs, examples, proof, and skill guidance to treat Klaviyo writes as plan-first with explicit no-snapshot approval when no saved snapshot is available.
- Rewrote `TEMPLATE_README.md` and `TEMPLATE_GUIDE.md` as Klaviyo-local maintenance notes instead of raw starter text.
- Documented the real command surface: `onboarding`, `auth check`, `api ops list/show`, explicit `api <operation_command>`, and `runs list/show`.
- Documented the real safety gates: dry-run by default, `--live` for real calls, `--apply` for writes, and `--plan-in --yes` for high-impact writes.
- Added a concrete maintenance validation flow with venv recreate, editable install, unit tests, and smoke checks.
- Rebuilt the README, onboarding, quickstart, command reference, safety model, and proof pages into the user-first public skill pattern used by the stronger Qwayk skill pages.

### Fixed
- Fixed the old write apply path that could produce receipts without a before-state snapshot or provider backup.
- Removed local-only runtime folders from the shipped tool tree before final review.
- Replaced stale template changelog text with real Klaviyo tool notes.
