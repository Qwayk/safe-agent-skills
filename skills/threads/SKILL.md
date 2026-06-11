---
name: threads-safe-cli
description: Use this wrapper to run the official Threads Graph API via `threads-api-tool` with safe defaults.
---

This page is the agent-facing rule sheet for the public Threads skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safe CLI wrapper for `threads-api-tool`.

Core rules:
- Use only `threads-api-tool` subcommands listed in `docs/command_reference.md`.
- Keep scope strictly to official Threads Graph API command families in `docs/api_coverage.md`.
- Never include secrets or ask users to paste tokens in chat.
- Refuse requests for non-CLI surfaces: Web Intents links and webhook dashboard setup.

Safety loop:
- Start with read-only checks (`auth check`, `auth token status`).
- For writes, generate a dry-run plan first.
- Without required approval, apply attempts must stop before provider writes, local token writes, demo/job writes, or receipt output. Approved supported writes should continue through the explicit no-snapshot approval gate and produce a receipt.
- For any write, assume irreversible without built-in rollback; require explicit user review of the plan, approval gate, and any exact limitation.
- For deletes, require both `--yes` and `--ack-irreversible`.

Command patterns:
- `threads-api-tool onboarding`
- `threads-api-tool --output json auth check`
- `threads-api-tool --output json auth token status`
- `threads-api-tool --output json auth code exchange --code <code>`
- `threads-api-tool --output json profiles me`
- `threads-api-tool --output json posts list-owned --threads-user-id <id>`
- `threads-api-tool --output json posts list-public --username <handle>`
- `threads-api-tool --output json posts status --threads-container-id <id>`
- `threads-api-tool --output json replies list --threads-media-id <id>`
- `threads-api-tool --output json insights media --threads-media-id <id>`
- `threads-api-tool --output json search keyword --q <term>`
- `threads-api-tool --output json locations search-query --q <query>`
- `threads-api-tool --output json locations get --location-id <id> [--fields <fields>]`
- `threads-api-tool --output json oembed get --url <threads_url>`
- `threads-api-tool --output json replies hide --threads-reply-id <id> --hide <true|false>`
- `threads-api-tool --output json replies pending list --threads-media-id <id>`
- `threads-api-tool --output json replies pending decide --threads-reply-id <id> --approve <true|false>`
- `threads-api-tool --output json --plan-out /tmp/threads.plan.json posts create-text --threads-user-id <id> --text "Draft"`
- `threads-api-tool --output json --apply --ack-no-snapshot posts create-text --threads-user-id <id> --text "Draft"` after review to attempt the approved write path.

When to stop and ask the user:
- Missing or wrong credentials.
- A request targets non-Graph or dashboard-only surfaces.
- Ambiguous object IDs or action types.
- Missing explicit approval for an unsafe write.
