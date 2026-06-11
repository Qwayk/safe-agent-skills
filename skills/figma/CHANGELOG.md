# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Customer-ready Figma README, onboarding, command reference, and configuration/auth docs.
- `operations` runtime implementation for explicit operation execution with write dry-run gating.
- OAuth token-file support and token status plumbing for `auth token set` and `auth token status`.

### Changed
- Provider write applies now require explicit no-snapshot approval before Figma token use or provider HTTP when operation-specific before-state support is not available. Write plans include `no_snapshot_available` before_state metadata, and successful write receipts record the no-snapshot approval and recovery limit.
- Reworked docs and command references to ship the actual Figma surface only:
  `onboarding`, `auth check`, `auth token set/status`, `runs list/show`, `operations list/show/<area> <op_key>`.
- Updated safety wording to reflect real probe behavior (`auth check` now marks blocked conditions as failed).
- Updated coverage/proof docs to local-proof status and kept proof outputs as the evidence source.
- Replaced shipped execution surface from an old run-style helper to `operations <area> <op_key> --named-flags ...`.
- Added explicit mention of the `--version-id` alias and updated write verification wording to the explicit no-snapshot approval behavior.

### Fixed
- Removed remaining template framing and scaffold language from shipped docs.
- Removed template-only docs baggage (`TEMPLATE_GUIDE.md`, `TEMPLATE_README.md`, jobs-related surface docs).
- Synced local proof artifacts with command coverage and removed legacy template command artifacts:
  `src/figma_safe_agent_cli/commands/jobs.py`, `src/figma_safe_agent_cli/commands/demo.py`,
  `tests/test_jobs.py`, `examples/jobs.csv`, `examples/jobs_with_write.csv`.
- Synced README and docs start pages to the non-technical-first standard and documented the full shipped CLI flag surface.
- Added coverage for `auth check --skip-live` and irreversible write safety gates.

### Removed
