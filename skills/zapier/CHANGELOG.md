# Changelog

All notable changes are tracked here.

## [0.1.0]

- Replaced template scaffold with a Zapier-safe explicit-operation CLI.
- Added pinned spec artifacts:
  - partner API schema
  - trigger inbox spec
  - promotions spec
  - AI Actions spec
  - docs index snapshot
- Added `docs/api_coverage.md` before implementation and aligned docs with 62 explicit operations.
- Implemented generated command registration for partner, trigger inbox, promotions, and AI Actions.
- Enforced dry-run plans for write operations and strict apply/plan-in/ack gate for high-risk commands.
- Added plan/receipt persistence and local run artifacts.
- Added auth checks and docs/test coverage for import/version/command surface/safety/auth leakage/proof alignment.
