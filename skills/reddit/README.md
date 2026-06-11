# Reddit

Install slug: `reddit`

Use this skill when you want your AI agent to review Reddit account, post, subreddit, and moderation work with a clearer plan before any live write.

Safe Reddit Data API CLI for agent use.

This tool uses the official Reddit OAuth REST docs at `https://www.reddit.com/dev/api/`, pins that inventory locally, and exposes each pinned operation as an explicit CLI subcommand under `api`.

Important:
- Reddit now requires approval before Data API access.
- Live calls need a proper Reddit-style `User-Agent`.
- Reads need `--live`.
- Writes are dry-run by default and need extra safety flags.

## For non-technical users

Start with:
- [What you can do](docs/use_cases.md)
- [Connect your account](docs/onboarding.md)
- [How live changes stay safer](docs/safety_model.md)

## For technical users

Start with:
- [Quickstart](docs/quickstart.md)
- [Command reference](docs/command_reference.md)
- [API coverage](docs/api_coverage.md)

Minimal commands:

```bash
qwayk-reddit-safe-agent-cli onboarding
qwayk-reddit-safe-agent-cli auth login
qwayk-reddit-safe-agent-cli api ops list --section account
```

## Proof pack

- [Proof pack](docs/proof.md)
- [API coverage](docs/api_coverage.md)
- [Examples](docs/examples/)
