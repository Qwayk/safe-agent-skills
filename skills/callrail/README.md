# CallRail

Use this skill when you want your AI agent to review calls, texts, forms, companies, trackers, integrations, and webhooks in CallRail, with dry-run-first write paths and clearer review before live changes.

Install slug: `callrail`

## For non-technical users: Start here (no coding)

- [What you can ask the agent to do](docs/use_cases.md)
- [Connect your CallRail account](docs/onboarding.md)
- [How this skill stays safer](docs/safety_model.md)

Example requests you can ask the AI agent:

- "Show me the calls from this week for one company and group them by day."
- "Pull the latest text conversations and search for one customer number."
- "Draft an outbound call request first, and do not place it until I review the plan."
- "Send an MMS reply with one image attachment after showing me the preview first."
- "List integrations for this company and show what is safe to change through the API."

## What happens before live changes

- Reads run without apply flags.
- Writes are dry-run first.
- Live writes need `--apply --yes --ack-no-snapshot` until command-specific snapshots exist.
- `calls create-outbound` and `text-messages send` also need `--ack-irreversible`.
- There is no raw request bridge.

## For technical users: Start here (CLI)

- [Quickstart](docs/quickstart.md)
- [Command reference](docs/command_reference.md)
- [API coverage](docs/api_coverage.md)
- [Proof and verification](docs/proof.md)

## Verification note

The explicit CallRail command families, dry-run plans, live apply gates, receipts, MMS send shapes, and coverage ledger are implemented and locally tested in this repo. Live CallRail reads and writes are still locally tested with mocked provider responses, not with a write-enabled CallRail test account inside this repo.
