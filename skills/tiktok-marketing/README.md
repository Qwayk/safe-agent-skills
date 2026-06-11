# tiktok-marketing-api-tool

Safe, explicit CLI for the official TikTok for Business Marketing API.

This build ships the pinned official command surface as `240` named `api <operation-command>` commands, plus:

- `api ops list`
- `api ops show --op <operation-command>`
- `auth check` backed by `oauth2-advertiser-get`
- plan-first write safety with explicit no-snapshot approval for current writes

## For non-technical users: Start here (no coding)

- `docs/use_cases.md`
- `docs/onboarding.md`
- `docs/safety_model.md`

Example requests you can ask the AI agent:

- "Pull a simple campaign summary for this week."
- "Check which campaign changes are safe before applying any write."
- "Prepare a first draft plan for a new campaign."

## For technical users: Start here (CLI)

- `docs/quickstart.md`
- `docs/command_reference.md`

Short technical examples:

- `tiktok-marketing-api-tool --output json onboarding`
- `tiktok-marketing-api-tool --output json auth check`
- `tiktok-marketing-api-tool --output json api ops list`

Safety rules:

- GET and HEAD operations are plan-only by default. Add `--live` to execute them.
- POST and other write-like operations are plan-first by default. A fully gated apply attempt currently requires explicit no-snapshot approval before provider HTTP when real saved snapshot support is not available.
- There is no raw request bridge.

Current status:

- Implemented and locally tested: manifest loading, parser registration, auth fallback, plan generation, multipart upload planning, write gates, no-snapshot approval flow, wrapper skill, and full coverage ledger.
- Implemented but live-unverified: all live TikTok reads. Current writes require explicit no-snapshot approval before provider HTTP when saved snapshots are not available.

Start here:

- `docs/onboarding.md`
- `docs/command_reference.md`
- `docs/api_coverage.md`
- `docs/proof.md`
- Agent skill prompt and install notes are included with this package.
