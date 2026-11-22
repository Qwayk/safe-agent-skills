# Changelog

## November 22, 2026 local update

- Fresh installs include the command list. The source archive includes the skill and guides.
- Setup keeps the chosen settings file and creates it with owner-only access. A blank token shows up as missing.
- The retired AI Actions, browser consent, and inbox event commands give a clear local message.
- Receipts for new action runs show that Zapier accepted the run and give a command to check the result when Zapier returns a run ID.
- The setup, approval, and engineering guides now include the useful steps from ten smaller pages.

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
