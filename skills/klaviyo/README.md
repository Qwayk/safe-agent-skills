# klaviyo-safe-agent-cli

Safe local CLI for Klaviyo API operations with explicit safety gates. Reads can run live with `--live`; writes generate plans, and live apply needs a saved snapshot or explicit no-snapshot approval before Klaviyo HTTP.

## Start here

- Onboarding: `docs/onboarding.md`
- Quickstart: `docs/quickstart.md`
- Command reference: `docs/command_reference.md`
- API coverage: `docs/api_coverage.md`
- Safety model: `docs/safety_model.md`

## Core command surface

- `klaviyo-safe-agent-cli --version`
- `klaviyo-safe-agent-cli onboarding`
- `klaviyo-safe-agent-cli auth check`
- `klaviyo-safe-agent-cli api ops list`
- `klaviyo-safe-agent-cli api ops show --op <operation_command>`
- `klaviyo-safe-agent-cli api <operation_command> ...`
- `klaviyo-safe-agent-cli runs list|show`

## Agent runtime wrapper

- Skill name: `klaviyo-safe-cli`
- Agent skill prompt and install notes are included with this package.
- Install instructions: copy or symlink the folder into your runtime skills directory.
