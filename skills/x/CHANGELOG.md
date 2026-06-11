# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Pinned X API v2 OpenAPI snapshot + deterministic operation inventory (`docs/official_operations.txt`) with unit tests.
- Explicit OpenAPI operations: `api ops list` + `api <operationId>` (plan-only by default; explicit `--live`/`--apply --yes` safety gates).
- OAuth2 PKCE helper commands (`auth pkce start/finish`) that now plan/refuse before local PKCE/token state writes.
- Live OAuth smoke check: `x-api-tool --live auth check` (minimal `GET /2/users/me`).
- DM-first workflows: `dm can-send`, `dm send`, and `dm bulk-send` with strict bulk policy refusals + local opt-out ledger.
- Added or updated the customer-ready agent skill prompt.
- Blocked-before-apply write plans/refusals for OpenAPI writes, DMs, auth token/PKCE helpers, demo writes, and write-row jobs.
- A publish-ready README contract test plus a public-doc path-leak guard for the X first-screen docs and proof files.

### Changed
- OpenAPI CLI surface: one explicit `api <operationId>` subcommand per pinned `operationId` (no operationId flag).
- Confirmed write attempts now require explicit no-snapshot approval before provider writes, token exchange, local auth/token writes, stub row writes, or receipt output when real before-state/provider-backup support is not available.
- Rebuilt the README and the first-screen user docs into the public skill pattern so X now starts with a user-first opening, a clearer safe first ask, and honest write-safety wording instead of the old template split.

### Fixed
- Secret-safe HTTP logging and errors (redacts token-like query params and Authorization headers).
- Onboarding docs and `.env.example` redirect URI guidance (loopback default; avoids misleading placeholders).
- References expanded to include DM docs and automation rules used by safety checks.
- Cleaned the remaining Ruff and mypy source-gate issues so the public-ready X source now passes lint, typing, and the full unit test suite before mirror/publish.

### Removed
- Retired the generic bridge: `x-api-tool api call --op <operationId> ...`.
