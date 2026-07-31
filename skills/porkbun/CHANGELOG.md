# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Complete Porkbun API v3.9 boundary: 53 paths, 66 explicit commands, and 10 families.
- Deterministic inventory and coverage generation from the pinned official specification.
- Review-first runtime for 27 writes, including saved plans, acknowledgements, readback, and receipts.
- Porkbun-specific public docs, tracked `skills/porkbun/SKILL.md`, and redacted examples.

### Changed
- Restricted production requests to Porkbun's two official v3 hosts.
- Moved API credentials to header authentication and kept them out of request files and output.
- Authenticated every saved write plan with a local HMAC key so plan fields cannot be edited and rehashed.
- Made the account invite-status token a file-only `--input` value.

### Fixed
- Enforced billable, terms, destructive, send, secret, and no-snapshot approvals.
- Rebuilt apply acknowledgements from current operation metadata and made billable apply reject missing, malformed, or changed cost signatures.
- Made plan keys, plans, receipts, onboarding env files, and secret results owner-only and atomic from creation; secret destinations are reserved before provider requests.
- Disabled redirects and rejected every `3xx` response before a read or write can succeed.
- Scrubbed configured credentials and sensitive request values from provider, validation, transport, readback, and generic error output.
- Kept secret-bearing results out of normal output and rejected unsafe, directory, unwritable, and symbolic-link output targets.
- Refused plan, receipt, and secret output paths that alias one another or environment, JSON input, and plan input files before provider calls or replacement.
- Made concurrent first-use plan-signing-key initialization converge on one key without overwriting it.
