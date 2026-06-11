# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Before-state capture for supported live writes. Saved files live under `.state/runs/<run_id>/before/`, and JSON output/receipts include `before_state` metadata.

### Changed
- Unsupported live write families now require explicit no-snapshot approval before HTTP when a safe pre-read is not available. This is intentional for create/send/bulk operations where the tool cannot capture a meaningful target state yet.

### Fixed

### Removed

## [0.6.0] - 2026-02-22

### Added
- Emails write coverage:
  - `emails forward` (irreversible; apply requires `--yes --ack-irreversible --plan-in`).
  - `emails patch` (apply-gated; read-back verification).
  - `emails delete` (destructive; apply requires `--yes --plan-in`; best-effort verification expecting 404).

## [0.5.0] - 2026-02-19

### Added
- Phase 5 endpoint coverage expansions:
  - Campaigns: patch/delete, sending status, search-by-contact, share, create-from-export, export, duplicate, count-launched, add-variables.
  - Leads: create/patch/delete, bulk delete, merge, update-interest-status, remove-from-subsequence, bulk-assign, move, move-to-subsequence.
  - Supersearch enrichment: create/get/history/settings patch/run/enrich-leads/AI plus count/preview helpers.
  - Webhooks: get, event-types, resume.
  - Subsequences: sending status, pause/resume, duplicate.
  - Do-not-contact: get/patch.
  - Accounts: mark-fixed, move.

## [0.4.0] - 2026-02-19

### Added
- Phase 4 workspace/admin + sensitive/admin command families:
  - Workspace: patch/create/change-owner/whitelabel domain.
  - Workspace billing: plan + subscription details (read-only).
  - Workspace members and group members: list/get/create/patch/delete (deletes are plan-in required).
  - OAuth init/status: Google + Microsoft OAuth init + session status (does not manage tokens).
  - DFY email account orders: list orders, list accounts (optional secret-bearing passwords), create order, cancel accounts, domain checks.
  - CRM actions: list and delete phone numbers (delete is plan-in required).
  - API keys: list/create/delete with secret-safe local storage for any returned key material (never printed to stdout).

### Changed
- Destructive and irreversible apply requires a reviewed plan file via `--plan-in` where implemented.
- `threads reply` apply requires `--plan-in` in addition to `--yes --ack-irreversible`.
- `webhooks delete` and `do-not-contact delete` apply requires `--plan-in` in addition to `--yes`.

## [0.3.0] - 2026-02-19

### Added
- Phase 3 read-first reporting + deliverability command families:
  - Analytics: account + campaign analytics endpoints.
  - Inbox placement: tests (create/patch/delete are apply-gated; create is irreversible-gated), analytics, and reports.
  - Email verification: create (apply-gated) + status.
  - Audit log: list (raw items hidden by default; use `--include-items --out <path>` for file-only raw output).
  - Webhook events: get + summary endpoints.

## [0.2.0] - 2026-02-19

### Added
- Accounts command family (CRUD + warmup enable/disable + pause/resume + vitals/status), with credential-safe redaction and file-only output for sensitive reads.
- Lead organization families: lead lists, lead labels, custom tags, and custom tag mappings (including tag mapping toggle endpoint).
- Campaign subsequences CRUD.
- Account↔campaign mappings (read-only per official docs).

### Changed
- stdout JSON output is sanitized to redact sensitive keys (password/token/Authorization) across all commands.
- Delete workflows require a reviewed plan file (`--plan-out` then `--apply --yes --plan-in`) where implemented (accounts/lead lists/lead labels/custom tags/subsequences/webhooks/do-not-contact).

## [0.1.0] - 2026-02-18

### Added
- Initial Instantly API v2 safe CLI release.
- Read commands: `whoami`, `health`, and list/get command families for campaigns, leads, webhooks/events, emails, do-not-contact, and background jobs.
- Write commands with plan/apply/verify/receipt workflow:
  - `campaigns create|activate|pause`
  - `leads add-bulk` (bulk injection requires `--apply --yes`)
  - `webhooks create|patch|delete|test` (delete requires `--apply --yes`)
  - `threads mark-as-read`
  - `threads reply` (irreversible; requires `--apply --yes --ack-irreversible`; supports `--plan-in/--plan-out`)
  - `do-not-contact create|delete` (requires `--apply --yes`)
