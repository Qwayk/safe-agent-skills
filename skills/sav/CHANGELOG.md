# Changelog

## 0.1.4 — 2026-07-31

- Bumped package docs/runtime versions to `0.1.4`.
- Documented exclusive wrapper layouts for this tool:
  - source checkout uses `skills/sav/SKILL.md`
  - public mirror uses top-level `SKILL.md`
  - resolver requires exactly one layout.
- Added a dedicated test for public-layout wrapper resolution and kept duplicate/missing layout failure behavior explicit.
- Kept command set, runtime behavior, API contract, and safety posture unchanged.

## 0.1.3 — 2026-07-31

- Corrected correction-3 wording so receipts never imply durable outcomes.
- Reported 2xx provider responses as `provider_accepted` without claiming verified lasting account state.
- Removed stale `durable` proof marker and fixed receipt example state to use `receipt_written` as the local persistence signal.
- Kept command set and safety behavior at 12 operations unchanged.

## 0.1.2 — 2026-07-31

- Bumped package/docs references to `0.1.2`.
- Aligned docs with current runtime details:
  - fixed host and redirect behavior,
  - provider failure and non-2xx receipt outcomes,
  - pre-transport request/outcome wording,
  - exact auth/nameserver read validation and timeout constraints,
  - and transfer secret handling from `.state/secrets`.
- Updated onboarding, quickstart, and safety text to match current write-plan flow and `.json` plan-out requirement.
- Updated example JSON to match runtime read and receipt shape.

## 0.1.1 — 2026-07-31

- Align documentation with current plan/receipt contract and state model:
  - plan schema version `2`
  - HMAC-SHA256 plan signing with local `.state/keys/plan-hmac.key`
  - `0700` state directories and `0600` plan/receipt/key file modes with atomic writes
- Clarify transfer dry-run and apply behavior:
  - `--auth-code-file` only
  - one-line mode-`0600` code file requirement
  - apply runs from reviewed plan and does not request transfer secret again
- Update examples to current schema and receipt shapes.
- Tighten safety doc language for malformed/missing state, status redaction behavior, and provider failure receipts.

## 0.1.0 — 2026-07-31

- Initial source build for the SAV fixed-command slice from the pinned Postman collection:
  - read and write command inventory generated into `docs/api_coverage.md`
  - runtime command parser updated from the generated inventory
  - fixed command set includes 4 reads and 8 writes
- Added safety-first docs bundle and agent wrapper for the first release:
  - `README.md`, `docs/quickstart.md`, `docs/onboarding.md`, `docs/command_reference.md`,
    `docs/safety_model.md`, `docs/use_cases.md`, `docs/proof.md`, `docs/references.md`,
    `docs/skills_wrappers.md`, `docs/authentication.md`, `docs/configuration.md`,
    `docs/engineering_notes.md`, and `skills/sav/SKILL.md`.
- Added redacted/parseable examples:
  - `docs/examples/read-active.example.json`
  - `docs/examples/plan.example.json`
  - `docs/examples/receipt.example.json`
