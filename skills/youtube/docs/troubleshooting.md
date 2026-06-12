# Troubleshooting

Use this page when a YouTube command stops before doing the work you expected. Most stops are safe: they mean the tool needs clearer access, a clearer target, or a stronger approval before it can continue.

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no OAuth tokens, no API keys in URLs).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## OAuth tokens

- If `auth token status` says the token is missing, this tool cannot create it automatically yet:
  - `youtube-api-tool auth login --console`
  - (or advanced) `youtube-api-tool auth token set --file token.json`
- Both commands validate inputs and stop at a plan/refusal today. They do not write `.state/token.json` automatically.
- If your access token already exists and expires, read/live flows may attempt to refresh it when the provider libraries allow it.

## Write apply needs saved-state acknowledgement

For non-GET API writes and uploads, the tool must say when no useful saved state exists. Apply then needs `--apply --yes --ack-no-snapshot` where the command supports execution. That final flag means you understand the tool may not have saved state it can restore from. Missing approval, missing credentials, unclear targets, unsupported actions, or failed safety checks still return a safe refusal.

Auth token writes, demo writes, and write jobs are planning/refusal flows today. They are useful for safety proof, but they do not perform real token writes or real YouTube job writes in this build.

## Channel resolve: “Selection required”

If `channels resolve --live` returns multiple candidates, the tool refuses by default (safe no-op).
Re-run with `--pick N` (1-based) or re-run with an explicit channelId (starts with `UC...`).

## Channel export: out-dir not empty / resume

`channels export --live` writes local dataset files under `--out-dir`.
If the directory is not empty, the tool refuses unless you pass `--overwrite` (or global `--yes`) or use `--resume`.

If an export stops early (example: you used a low `--max-pages`), re-run with `--resume` to continue from `checkpoint.json`.
