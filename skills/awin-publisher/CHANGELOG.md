# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Added the explicit publisher command surface for:
  - `accounts list`
  - `programs list`
  - `programs details`
  - `offers list`
  - `transactions list`
  - `transactions by-ids`
  - `transaction-queries list`
  - `reports advertiser`
  - `reports campaign`
  - `reports creative`
  - `linkbuilder generate`
  - `linkbuilder generate-batch`
  - `linkbuilder quota`
  - `feeds enhanced-download`
  - `feeds legacy-list`
  - `feeds legacy-download`
  - `proof-of-purchase orders create`
- Added plan and receipt handling for the proof-of-purchase write flow.
- Added download-to-file helpers for enhanced and legacy feed commands.
- Added example outputs and updated proof references for the shipped command surface.

### Changed
- Updated README, command reference, coverage ledger, references, skill wrapper docs, and tool AGENTS to match the shipped surface.
- `auth check` performs real Awin `GET /accounts` verification using bearer auth and official `accessToken` query validation, and filters to publisher accounts.
- Proof-of-purchase live apply now requires `--plan-in` together with `--apply --yes`.
- Proof-of-purchase docs now say clearly that live use needs Awin-side publisher enablement and advertiser-side CLO enablement.

### Fixed
- Corrected the official program endpoints to `GET /publishers/{publisherId}/programmes` and `GET /publishers/{publisherId}/programmedetails` with `advertiserId` in the query.
- Failing HTTP status paths no longer echo raw provider response bodies, and legacy feed key-in-URL failures now stay redacted in stdout, stderr, and audit logs.
- Removed copied template-only drift and other scaffold leftovers from the generated tool.

### Removed
