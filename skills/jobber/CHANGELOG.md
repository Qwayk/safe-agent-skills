# Changelog

All notable changes to this project are documented in this file.

This project follows Semantic Versioning.
The tool is currently in early 0.x development.

## [Unreleased]

### Added
- Added public-facing documentation for Jobber OAuth setup, generated read/write coverage, and webhook helpers.
- Added explicit `--ack-no-snapshot` safety gate for high-risk writes that lack before-state snapshots.
- Added no-snapshot and recovery metadata to write plans and receipts.
- Added wrapper scaffold notes for the public `jobber` skill.
- Added registry-backed CSV job planning for `read.<JobberQuery>` and `write.<JobberMutation>` rows.

### Changed
- Replaced template and demo-only docs with real Jobber-specific documentation in `README.md` and `docs/`.
- Updated docs/limits and examples to match implemented runtime behavior and `docs/api_coverage.md`.
- Changed live write apply to require `--apply --yes --plan-in <reviewed-plan.json>` and validate the saved plan before any mutation execution.
- Reconciled `docs/api_coverage.md` with runtime reality by marking registry-backed reads, writes, and webhook topics as live-unverified where account behavior has not been proven.
- Updated write/job receipts so no-snapshot metadata is explicit and there is no rollback promise for unsupported rollback paths.

### Fixed
- Corrected OAuth authorize URL defaults to avoid sending an undocumented scope value.
- Corrected public examples so global flags appear before subcommands.
- Added tests proving direct `--apply --yes write ...` without `--plan-in` refuses before HTTP and that plan drift refuses before execution.
- Added focused tests for high-risk no-snapshot mutations, including jobs and contract checks for doc examples.

### Removed
- Removed generic template placeholders and demo copy from the public contract docs.
- Removed the leftover template/demo command module and starter ping job examples from the Jobber tool.
