# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Added Wave 3 before-state reset behavior: write plans now expose `before_state`, and Google Business Profile provider writes require explicit no-snapshot approval before HTTP when per-command before-state capture support is not available.
- Renamed CLI identity to `google-business-profile-safe-cli`.
- Added GBP OAuth installed-app login and token helpers (`auth login`, `auth check`, `auth token set|status`).
- Added onboarding and configuration docs for local Google Business Profile setup.
- Added `account-management accounts create` with dry-run-by-default planning, `--apply` + `--plan-in`, create-payload validation, and read-back verification.
- Added `account-management accounts patch` with required `--update-mask`, dry-run-by-default planning, `--apply` + `--plan-in`, and read-back verification.
- Added `account-management accounts admins create`, `delete`, and `patch` with dry-run-by-default planning, required `--plan-in` + `--yes`, and follow-up verification from `accounts admins list`.
- Added `account-management locations admins create`, `delete`, and `patch` with dry-run-by-default planning, required `--plan-in` + `--yes`, list-based verification, and safe support for either invitee email or `account` identity on create.
- Added `account-management locations transfer` with dry-run-by-default planning, required `--plan-in` + `--yes` + `--ack-irreversible`, and paged source/destination read-back verification through `business-info accounts locations list`.
- Added `legacy-v49 accounts locations reviews list`, `get`, `update-reply`, and `delete-reply` with explicit review read commands, safe reply-file input, and read-back verification for reply writes.
- Added `legacy-v49 accounts locations verifications list` and `complete` with legacy host coverage, `--pin-file`, apply-time `--plan-in`, and list-based follow-up verification for completion.
- Added `legacy-v49 accounts locations transfer` with dry-run-by-default planning, required `--plan-in` + `--yes` + `--ack-irreversible`, deprecated-surface labeling, and strict source/destination read-back verification through `business-info accounts locations list`.

### Changed
- Retired old apply-success tests for provider writes that no longer run without before-state support.
- Removed template `demo` and `jobs` command exposure in favor of identity/auth groundwork.
- Moved OAuth token file to `.state/oauth_credentials.json` and updated env config to `GBP_*`.
- Updated README, proof, wrapper docs, and command docs so the public command surface matches the shipped CLI without outdated startup wording.
- Kept `accounts admins create` and `patch` in a safe shipped subset that supports only `OWNER` and `MANAGER`, and requires the invitee email in `admin` for create.
- Kept `locations admins create` and `patch` in a safe shipped subset that allows exactly one of `admin` or `account`, supports `OWNER`, `MANAGER`, and `SITE_MANAGER`, and rejects `PRIMARY_OWNER`.
- Kept `locations transfer` safe-by-default by requiring distinct source/destination accounts and honest list-based verification instead of trusting the empty transfer response.
- Kept `legacy-v49 accounts locations reviews update-reply` in a safe subset that accepts only `--reply-file` JSON shaped as `{"comment":"..."}` with a non-empty comment of 4096 bytes or fewer.
- Kept `legacy-v49 accounts locations reviews delete-reply` safe-by-default with `--plan-in`, `--yes`, empty-body delete handling, and read-back verification through `reviews get`.
- Kept `legacy-v49 accounts locations verifications complete` secret-safe by requiring `--pin-file`, using fingerprint-only planning, and verifying the final state through `legacy-v49 ... verifications list`.
- Kept `legacy-v49 accounts locations transfer` honest about Google deprecation while still shipping it for official boundary coverage with different-account validation and irreversible-action acknowledgement.
- Synced `docs/official_inventory.json` to the implemented coverage ledger and added a parser-backed test so inventory drift now fails validation immediately.

### Fixed
- CLI template: ensure argument/usage errors in `--output json` mode emit exactly one JSON error object (no argparse usage text).
- Fixed stale account-management patch receipt examples and added honest-failure coverage for create-without-name and patch read-back mismatch paths.
- Fixed the draft account-admin create shape so it no longer treated `admin` like an account resource name, and aligned examples and coverage docs with the real provider shape.
- Fixed the first location-admin draft so `account` identity create works on apply, malformed delete names are refused before planning, and location-admin receipts verify through the correct `locations admins list` request path.
- Fixed the first location-transfer draft so refusal tests match the tool's `ok=true` / `refused=true` shape, success receipts and examples agree on paged verification details, and transfer apply messages use the normal human-readable command wording.
- Fixed the first legacy-v49 reviews draft by rejecting blank and oversized reply comments, proving `--plan-in` mismatch makes no HTTP call, and adding honest verification-failure coverage for both reply update and reply delete.
- Fixed the first legacy-v49 transfer draft by adding same-account refusal, aligning docs/examples/wrapper surface with the shipped command, and proving the deprecated transfer with read-back verification instead of response-only trust.

### Removed
