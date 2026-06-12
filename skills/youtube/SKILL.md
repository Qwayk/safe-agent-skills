---
name: youtube-api-safe-cli
description: Run the YouTube Data API v3 Qwayk CLI safely: plan first, use --live for real reads, and require explicit approval for writes.
---

This page is the agent-facing rule sheet for the public YouTube skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safe CLI wrapper for the `youtube-api-tool` command.

## Core rules (do not break)

- Default to **dry-run** for anything that is not clearly read-only.
- Never ask the user to paste secrets into chat (API keys, OAuth tokens, client secrets).
- Do not print secrets (Authorization headers, OAuth tokens, API keys).
- Do not run free-form shell commands. Only run documented `youtube-api-tool` commands.
- For official API reads: default to plan-only and require `--live` to make network calls.
- For non-GET API requests: require `--apply --yes --ack-no-snapshot` when no saved state exists.
- For delete methods: require `--apply --yes --ack-no-snapshot --ack-irreversible` when no saved state exists.
- For media uploads: require `--apply --yes --ack-no-snapshot`, ensure the plan never embeds file bytes (path-only), and verify the receipt or exact refusal reason.
- If a method/target is ambiguous (missing `channelId`, `videoId`, unclear search criteria), stop and ask for clarification.
- For `channels export --live`: refuse if `--out-dir` is not empty unless the user approves `--overwrite`/`--yes` or explicitly requests `--resume`.

## Safety workflow (always)

1) Connect check (read-only): `youtube-api-tool --output json auth check`
2) If OAuth is needed and missing:
   - `auth login` and `auth token set` are planning/refusal flows today. Report setup as blocked unless an existing token file is already present.
3) For any non-GET or upload request:
   - Run the dry-run plan first (no `--apply`).
   - Summarize the plan in plain English.
   - Ask for explicit approval before re-running with `--apply --yes --ack-no-snapshot` (and `--ack-irreversible` for deletes), then verify the receipt or exact refusal reason.
4) After an approved apply attempt:
   - Report the receipt, verification result, or exact refusal reason.

## Command examples (placeholders only)

Read-only (GET):
- `youtube-api-tool --output json api search.list --params-json '{"part":"snippet","q":"<QUERY>","maxResults":5}'`

Resolve a channel (plan-only by default; use `--live` for official reads):
- `youtube-api-tool --output json channels resolve --channel "<CHANNEL_INPUT>"`
- `youtube-api-tool --output json channels resolve --channel "<CHANNEL_INPUT>" --live`
- If multiple candidates are returned: require the user to select one via `--pick N` or by providing an explicit channelId.

Export a channel videos dataset (plan-only by default; writes local files only with `--live`):
- `youtube-api-tool --output json channels export --channel "<CHANNEL_INPUT>" --out-dir "./channel_export"`
- `youtube-api-tool --output json channels export --channel "<CHANNEL_INPUT>" --out-dir "./channel_export" --live`
- Resume: `youtube-api-tool --output json channels export --channel "<CHANNEL_INPUT>" --out-dir "./channel_export" --live --resume`

Write (non-GET; plan then approved apply result):
- `youtube-api-tool --output json api playlists.insert --params-json '{"part":"snippet,status"}' --body-json '{...}'`
- `youtube-api-tool --output json --apply --yes --ack-no-snapshot api playlists.insert --params-json '{"part":"snippet,status"}' --body-json '{...}'`

Delete (irreversible-gated):
- `youtube-api-tool --output json api playlists.delete --params-json '{"id":"<PLAYLIST_ID>"}'`
- `youtube-api-tool --output json --apply --yes --ack-no-snapshot --ack-irreversible api playlists.delete --params-json '{"id":"<PLAYLIST_ID>"}'`

Upload (mediaUpload; plan then approved apply result):
- `youtube-api-tool --output json api videos.insert --params-json '{"part":"snippet,status"}' --body-json '{...}' --upload-file "<VIDEO_PATH>"`
- `youtube-api-tool --output json --apply --yes --ack-no-snapshot api videos.insert --params-json '{"part":"snippet,status"}' --body-json '{...}' --upload-file "<VIDEO_PATH>"`
