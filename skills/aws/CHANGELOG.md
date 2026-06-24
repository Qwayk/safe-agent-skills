# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- AWS runtime scaffold and pinned Botocore inventory.
- AWS-specific front-door docs, proof pages, and example outputs.
- `aws` skill wrapper and tool-local wrapper rules.
- Live-write receipts now include an honest verification block with checks, read-back status, and limits.
- Generated coverage now records per-operation command status, mode, risk categories, and acknowledgement requirements.

### Changed
- Reworked the AWS docs again after public review so the first-screen copy leads with concrete AWS jobs: IAM access review, EC2 inventory, S3 exposure, CloudTrail/CloudWatch evidence, billing, quotas, and careful change plans.
- Rewrote the AWS public-facing docs around real account, region, IAM, EC2, S3, spend, public exposure, data movement, secrets, no-snapshot, and live-verification concerns.
- Rewrote the README and docs front doors for the shipped AWS runtime.
- Replaced template example env and example plan/receipt files with AWS-specific values.
- Updated the public contract tests to reject the starter copy and placeholder text.
- Strengthened AWS safety classification beyond prefix-only rules for security/identity, secret, spend/quota, messaging, public exposure, data movement, no-snapshot, unknown mutating, and irreversible risk.
- Updated proof, safety, command, prompt, example, and skill-wrapper docs for the stricter live-write gates.
- Polished the source README, use cases, coverage, proof, references, docs hub, and skill wrapper so the source docs read like the future public AWS skill page without build-status wording.

### Fixed
- CLI JSON error handling still emits one JSON object for argument and usage failures.
- Generic live AWS write receipts no longer imply read-back verification happened when only SDK-response verification was possible.
- Generic apply verification now reports `limited`, not `verified`, when `read_back.attempted` is false even if the AWS SDK response is 2xx.
- Generated inventory and committed example outputs no longer include local machine paths.

### Removed
- Template-only wording from the source docs.
