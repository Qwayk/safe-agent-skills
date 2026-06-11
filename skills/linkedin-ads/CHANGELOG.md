# Changelog

This file documents all notable changes for the LinkedIn Ads safe CLI.

## [Unreleased]

### Added

- Added the Wave 3 before-state reset: LinkedIn write plans now mark before-state as required but unsupported, and live write applies require explicit no-snapshot approval before LinkedIn HTTP when safe before-state capture is not available.
- Require `--ack-irreversible` for every live LinkedIn write and record the irreversible contract in plans and receipts.

### Removed
- Removed final scaffold leftovers from shipped docs and tests while keeping LinkedIn command coverage unchanged.
- Removed scaffold jobs CSV examples (`examples/jobs.csv`, `examples/jobs_with_write.csv`) from the example set.

## [0.1.0] - 2026-05-24

### Added
- LinkedIn Marketing scope CLI command families for ad account, campaign, creative, audience, conversion, and reporting operations.
- Endpoint coverage map in `docs/api_coverage.md` with safe-read and safe-write command shapes.
- Operator safety flow and onboarding updates (`auth check`, plan/refusal flow, and run history) for LinkedIn Ads operations.
- Initial customer examples for `quickstart.md`, `command_reference.md`, and `onboarding.md`.

### Fixed
- Removed scaffold `demo` and `jobs` command modules from shipped CLI surface.
- Replaced template placeholders with LinkedIn Ads-specific runtime text in changelog and maintenance notes.
