# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- New read-only TheMealDB safe CLI built from the Python API tool template.
- Explicit named commands for the documented free V1 read endpoints.
- Public-key-first onboarding with no secret required for the default setup.
- API coverage ledger, proof docs, references, and customer-ready docs.
- Unit tests for command families, onboarding, output, imports, and auth-path redaction.

### Changed
- Replaced the write-demo template flow with a small read-only TheMealDB command surface.
- Replaced template env vars with `THEMEALDB_*` settings and default free key `1`.

### Fixed
- Custom API key values are redacted from auth-path errors and verbose HTTP output.

### Removed
- OAuth helpers, jobs flows, write-plan files, and other template-only write scaffolding.
