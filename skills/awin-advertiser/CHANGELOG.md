# Changelog

## [0.1.1] - 2026-06-09

### Added
- Added shipped command `transactions batch validate --advertiser-id <id> --batch-file <path>` to support batch validation/apply of approve|decline|amend|amendTrackingParameters actions.
- Added local batch validation for: max 40,000 items, required action set, required transaction object, target identity (`transactionId` OR `orderRef` + `transactionDate` + `timezone`), required decline reasons, amend fields/parts, and amend-tracking parameter checks.
- Added deterministic auth behavior for batch endpoint as `Authorization: Bearer <token>` plus `accessToken=<token>` query (explicitly documented as a documented ambiguity choice).
- Added repo-standard customer docs:
  - `docs/use_cases.md`
  - `docs/safety_model.md`
  - `docs/quickstart.md`
- Added regression coverage for HTTP/audit redaction and repo-standard docs structure.

### Changed
- Reworked `README.md` and `docs/README.md` to be non-technical-first and repo-standard ordered.
- Expanded `docs/onboarding.md` with plain-English AI-agent request examples.
- Aligned package version, proof docs, examples, and version outputs to `0.1.1`.
- Updated command reference, API coverage, proof, references, skills wrappers, and tool `SKILL.md` with full batch command and auth notes.
- Added batch plan and receipt example outputs under `docs/examples/outputs`.

### Fixed
- Removed a malformed batch test method signature that could cause unittest invocation failures.
- Hardened HTTP verbose logging, URLs, raised HTTP errors, CLI error output, and audit logging so `AWIN_API_TOKEN`, `accessToken`, `Authorization`, and `x-api-key` values are redacted consistently.

## [0.1.0] - 2026-06-09

### Added
- Initial scaffold copied from Python template and renamed for `awin-advertiser-safe-cli`.
- Added local config keys: `AWIN_API_BASE_URL`, `AWIN_API_TOKEN`, `AWIN_ADVERTISER_ID`, `AWIN_API_TIMEOUT_S`.
- Added live `auth check` implementation using `GET /advertisers/{advertiserId}/publishers` with bearer token + `accessToken` query param.
- Added shipped read command surface: `onboarding`, `auth check`, `runs list`, `runs show`, `publishers list`, `transactions list`, `transactions by-ids`, `transactions jobs list`, `transactions jobs show`, `reports publisher`, and `reports campaign`.
- Added shipped write command surface: `conversion orders create`, `offers create`, and `product-feeds upload` with dry-run-first plan/apply gates.
- Added initial API coverage ledger and updated customer-facing docs for the mapped advertiser surface.
- Updated the customer-ready agent skill prompt.

### Changed
- Reduced CLI surface by removing template and token bridges.
- Switched from scaffold-only docs to endpoint-specific auth notes, proof, and write-plan examples.

### Fixed
- Replaced template naming and stale example/wrapper references.
