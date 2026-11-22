# Changelog

This tool uses Semantic Versioning. Before version 1.0, a minor release can change how commands work.

## Unreleased

- Saved plans now check the Salesforce connection and the full request. Composite writes and bulk ingest changes require a saved plan.
- The tool checks the bulk job type before starting it. Permanent bulk deletes need explicit approval.
- Receipts show when a job is still running or a grouped request had errors.
- Onboarding keeps the selected settings file in the next command. The setup and approval guides now contain the useful details from the overlapping pages.

## Earlier work

### Added
- Initial Salesforce Platform REST API and Bulk API 2.0 command surface.
- Multipart manifest support for documented blob-upload flows.
- Customer-facing docs, proof pack, coverage ledger, and skill wrapper.
- Write dry-run plans now include an explicit `before_state` contract.

### Changed
- Replaced template onboarding, auth, and command references with Salesforce-specific content.
- Removed scaffold leftovers from the shipped command surface and updated environment and job documentation to match the real runtime.
- Salesforce live write apply now requires command-specific before-state capture or explicit no-snapshot approval before provider HTTP.

### Fixed
- JSON-mode argument errors emit exactly one JSON error object.

### Removed
- Archived scaffold docs and non-shipped legacy command modules.
- Generic starter CSV examples that did not reflect Salesforce runtime behavior.
