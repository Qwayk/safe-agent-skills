---
name: bluesky-safe-cli
description: Safe Bluesky agent wrapper for official XRPC operations via explicit commands.
---

This page is the agent-facing rule sheet for the public Bluesky skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safe CLI wrapper for `bluesky-safe-cli`.

Core rules:
- Use only `bluesky-safe-cli` subcommands.
- Never run free-form shell commands.
- Keep config and examples secret-free.
- Prefer `--output json`.

Safety loop:
- Read commands: run a preview first, then call with `--live` when needed.
- API write commands: show a plan first, then call with `--live --apply`.
- This release has no shipped `--plan-in` flow.
- Risky writes need `--yes`.
- Irreversible writes also need `--ack-irreversible`.
- Write apply needs a reviewed plan and `--ack-no-snapshot` when no before-state can be saved. Expect `before_state.status="no_snapshot_available"` before approval and a receipt after supported approved writes.
- Keep refusal output and run paths in the final summary.

Known limits:
- Subscription commands return raw websocket frame captures in command output/receipt.
- Without the required approval, write attempts stop before provider HTTP.

Command examples:
- `bluesky-safe-cli --output json onboarding`
- `bluesky-safe-cli --output json auth check`
- `bluesky-safe-cli --output json api ops list --kind query`
- `bluesky-safe-cli --output json --live api app-bsky-actor-get-profile --query-json '{"actor":"alice.bsky.app"}'`
- `bluesky-safe-cli --output json --live --apply --yes api com-atproto-server-update-account-handle --body-json '{"account":"alice.bsky.app","handle":"alice.new.bsky.app"}'`
- `bluesky-safe-cli --output json runs list`

When to refuse:
- Required arguments are missing.
- Auth is missing or unclear.
- An API write request is asked without `--live --apply`.
- A risky or irreversible write is asked without `--yes` / `--ack-irreversible`.
