# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Full explicit CallRail REST v3 command surface across accounts, calls, tags, companies, form submissions, integrations, integration filters, notifications, outbound caller IDs, page views, SMS threads, text messages, message flows, trackers, users, leads, lead timelines, and summary emails.
- API-key auth check with the official `Authorization: Token token=...` header and optional `Request-From`.
- Dry-run plans, apply receipts, local run history, and a shipped `callrail-safe-agent-cli` skill wrapper.
- Docs and examples aligned to the shipped CallRail surface, plus coverage and proof guards in tests.
- Audited single-resource and extra read-query support for `accounts get`, `calls get`, `companies get`, `integrations get`, `sms-threads get`, `text-messages get`, `trackers get`, `message-flows list`, and `page-views list`.

### Changed
- Generic write commands now require `--apply --yes`, support `--plan-out`, `--plan-in`, and `--receipt-out`, and keep redacted request metadata in outputs.
- `integrations create` and `integrations update` now refuse unsupported payload types and only allow `webhooks` and `custom`.
- Outbound calls and SMS send now require `--ack-irreversible`.
- Docs now explain more clearly that most shipped REST commands are account-scoped and normally need `--account-id` unless `CALLRAIL_DEFAULT_ACCOUNT_ID` is already set.
- Proof, references, and coverage docs were refreshed after the 2026-06-06 CallRail audit recheck.

### Fixed
- `auth check` no longer exposes stale OAuth-token status fields.
- Command docs no longer mention removed `jobs`, `demo`, or token-storage surfaces.

### Removed
- Shipped docs no longer present the old scaffold batch runner or demo command stories as real CallRail behavior.
- Non-REST helper commands were removed from the real parser surface: `tags available-colors`, `integrations configure`, `message-flows configure`, `trackers request-number`, `trackers configure-call-flows`, `trackers session-call-sources`, `trackers source-call-sources`, and `users roles`.
