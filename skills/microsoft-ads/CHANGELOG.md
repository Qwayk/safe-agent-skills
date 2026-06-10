# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Initial Microsoft Ads v13 SafeCLI scaffold.
- Audited operation inventory from official v13 WSDL snapshots (271 operations).
- Explicit CLI command surface for each audited operation.
- Wave 3 before-state reset: write plans mark before-state as required but unsupported, and write apply attempts require explicit no-snapshot approval before SOAP HTTP or stub receipt output when safe before-state capture is not available.

### Changed

### Fixed
- CLI template: ensure argument/usage errors in `--output json` mode emit exactly one JSON error object (no argparse usage text).

### Removed
