# Changelog

Changes to the LinkedIn Ads CLI and skill.

## [Unreleased]

### Fixed

- Setup accepts the documented token settings even when another token field is blank.
- Reports send account lists and date ranges in LinkedIn's format. Campaign updates send the required partial-update header.
- Receipts show when the tool only checked LinkedIn's HTTP reply.

### Added

- Write plans tell you when the tool cannot save the old settings. Sending the change then requires explicit approval to proceed without a saved copy.
- Require `--ack-irreversible` for every live LinkedIn write and record the irreversible contract in plans and receipts.

### Removed
- Combined the setup, report, and change guides and removed repeated instructions.
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
