# Changelog

All notable changes are documented here.

This project follows Keep a Changelog and semantic versioning.

## [Unreleased]

### Added
- Public read-only onboarding text and example config keys for Open Library.
- Optional config file support via `--config` for `base_url`, `timeout_s`, `user_agent_app`, `contact`.
- Contact and user-agent app fields are included in run identification.

### Changed
- Rewrote tool docs to match live read-only commands and no-auth behavior.
- Updated command defaults and onboarding output to match Open Library public use.

### Fixed
- Replaced template names and write-only command references in shipped documentation.
- Made the first search work straight from the quickstart without a settings file.
- Added checks for unexpected replies and wrong record IDs. The timeout flag now takes priority over an invalid saved timeout.
