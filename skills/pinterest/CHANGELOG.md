# Changelog

All notable changes to this tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Wave 4 before-state reset for write safety:
  - Remote write dry-run plans now include a blocked before-state contract.
  - Confirmed apply attempts require explicit no-snapshot approval before Pinterest provider writes, local token writes, report receipts/downloads, job output, or successful write receipts when command-specific before-state or provider-backup support is not available.
  - Example plan/receipt files now show the current no-snapshot approval shape.
- Agent Skills wrapper package:
  - `skills/pinterest-api-safe-cli/SKILL.md`
  - `docs/skills_wrappers.md`
- Pinterest Phase B write safety infrastructure:
  - Shared plan/receipt/refusal helpers for write commands (dry-run by default; missing approval refuses before write).
  - Global acknowledgement flags: `--ack-irreversible`, `--ack-spend`, `--ack-volume`.
- Safety-gated Boards plans/refusals: `boards create|update|delete|ensure` (apply attempts require `--apply --yes`; delete also requires `--ack-irreversible`; then refuse before write).
- Safety-gated Board Sections plans/refusals: `board-sections create|update|delete|ensure` (apply attempts require `--apply --yes`; delete also requires `--ack-irreversible`; then refuse before write).
- Safety-gated Pins plans/refusals: `pins create|update|delete|save|ensure` (apply attempts require `--apply --yes`; delete also requires `--ack-irreversible`; then refuse before write).
- v2 “proof pack” docs under `docs/` (`proof.md`, `references.md`, `api_coverage.md`, `engineering_notes.md`, and committed redacted examples).
- Read-only user account discovery commands: `user-account get|businesses|followers|following|following-boards|websites list|websites verification`.
- Read-only Business Access inventory commands: `business-access ... assets|members|partners` plus per-asset/per-member/per-partner relationship lists.
- Read-only resources/lookup commands: `resources ad-account-countries|delivery-metrics|metrics-ready-state|targeting|interest`.
- Read-only Ads commands: `ads accounts`, `ads campaigns`, `ads ad-groups`, `ads ads`.
- Safe-by-default Ads write control plane (dry-run plans by default; apply attempts require `--apply --yes` and then refuse before write):
  - `ads campaigns create|update|pause|resume`
  - `ads ad-groups create|update|pause|resume`
  - `ads ads create|update|pause|resume`
- Safe-by-default Catalogs writes (dry-run plans by default; apply attempts require `--apply --yes` and then refuse before write):
  - `catalogs create`
  - `catalogs feeds create|update|ingest`
- New safety acknowledgement flags:
  - `--ack-spend` (required on apply attempts for spend-affecting Ads writes; pause excluded)
  - `--ack-volume` (required on apply for feed ingest)
- Read-only Ads analytics commands: `ads analytics ad-account|campaigns|ad-groups|ads|pins` (aggregated reporting).
- Read-only Ads upgrades: `ads targeting-analytics ...`, `ads audience-insights`, `ads audiences`.
- Read-only Ads conversions status: `ads conversions ...` (conversion tags + eligibility/status reads).
- Read-only Catalogs commands: `catalogs list`, `catalogs feeds`, `catalogs feed-processing-results`, `catalogs product-groups`.
- Read-only Catalogs reporting commands: `catalogs product-group-products`, `catalogs item-issues`, `catalogs reports list`, `catalogs reports stats`.
- Read-only Catalogs diagnostics commands: `catalogs available-filter-values`, `catalogs product-group-product-counts`, `catalogs items-batch get`.
- `audit snapshot` optional exports: `--include-ads`, `--include-catalogs` (best-effort; warning-only).
- `audit snapshot` optional exports: `--include-user-account`, `--include-business-access --business-id ...`, `--include-resources`, `--include-conversions --ad-account-id ...`.
- Ads async report jobs: `ads reports create|get|run` (`create`/`run` require `--apply --yes --ack-volume`, then refuse before report creation, receipts, downloads, or job output).
- Batch runner: `jobs run` to inspect write workflows from a `.json`/`.csv` job file; remote-write rows now refuse before receipts or summary output.

### Changed

- Customer-first install instructions in `README.md` and `docs/quickstart.md` (minimal editable install first; dev extras optional).
- In `--output json` mode (default), usage/parse errors and `--version` now emit exactly one JSON object to stdout.
- Ads/Catalogs write commands now take JSON bodies via `--body-file` (with `--json` kept as a backwards-compatible alias).

### Fixed

- `docs/safety_model.md` wording to accurately describe the existing write-gated `pins links apply` workflow.
