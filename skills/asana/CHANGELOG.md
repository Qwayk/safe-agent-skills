# Changelog

## [Unreleased]

### Added

- Pinned official Asana REST OpenAPI input and deterministic 249-operation coverage ledger.
- 248 fixed commands with documented parameters, request media types, OAuth scopes, access notes, pagination, async, snapshot, verification, and risk metadata.
- Personal access token default with existing OAuth and service-account bearer-token transport support.
- Official-host-only reads, bounded retries, offset pagination, attachment upload metadata, and file-only handling for unexpected binary output.
- Saved schema-2 write plans with local HMAC-SHA256 integrity, fixed-request reconstruction at apply, content-derived approval IDs, same-target snapshots and drift checks, no-snapshot acknowledgement, stronger risk acknowledgement, readback verification, and receipts.
- Atomic owner-only local state for plans, receipts, signing keys, and audit logs, plus wrapper checks for source and published layouts.
- Public-layout wrapper simulation now resolves either supported wrapper location, so the complete suite runs with only top-level `SKILL.md`.
- Customer-facing docs, technical references, examples, behavior tests, generation checks, and the tracked `asana` skill wrapper.

### Excluded

- App Components, SCIM, OAuth lifecycle, browser automation, private endpoints, raw requests, SDK pass-through, and arbitrary `POST /batch` execution.
