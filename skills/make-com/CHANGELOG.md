# Changelog

## 2026-06-29

- Replaced starter/template prose in `README.md`, `docs/README.md`, and core docs with Make.com-specific customer-ready text.
- Added explicit safe-write flow docs for:
  - `--plan-in --apply --yes` as required confirmation,
  - `--ack-no-snapshot` when snapshot is not guaranteed,
  - `--ack-irreversible` for destructive operations.
- Confirmed documented auth model as `Authorization: Token`.
- Documented official coverage scope as `376` operations across `59` API reference pages.
- Updated `docs/api_coverage.md` and `docs/command_reference.md` to match current command surface.
- Documented the remaining live-verification limit without blocking public publish.
- Redacted raw `--body-json` values and `--body-file` paths from stored command text.
- Added secret-safe credential fingerprints to write plans and apply receipts, and made apply refuse if the current credential differs from the reviewed plan.
- Added regression tests for body command redaction, credential mismatch refusal, and apply receipt safety.
- Redacted secret-looking `--path-param` and `--query` values from stored command text, plan targets, and receipt response URLs.
- Added non-secret target fingerprints so apply still refuses when original path/query inputs differ from the reviewed plan.
- Redacted HTTP verbose URLs, request exception messages, HTTP error messages, and provider error bodies before they reach stderr, stdout, audit logs, run summaries, or run indexes.
