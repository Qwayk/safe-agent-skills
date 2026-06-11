# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no OAuth tokens, no API keys in URLs).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## OAuth tokens

- If `auth token status` says the token is missing, the current write-safe source tool cannot create it automatically yet:
  - `youtube-api-tool auth login --console`
  - (or advanced) `youtube-api-tool auth token set --file token.json`
- Both commands now validate inputs and require explicit no-snapshot approval before writing `.state/token.json` when no saved snapshot is available.
- If your access token already exists and expires, read/live flows may attempt to refresh it when the provider libraries allow it.

## Write apply needs no-snapshot approval

For non-GET API writes, uploads, auth token writes, demo writes, and write jobs, the tool must say when no useful before-state can be saved. Apply then needs explicit no-snapshot approval where the command supports execution. Missing approval, missing credentials, unclear targets, unsupported actions, or failed safety checks still return a safe refusal.

## Channel resolve: “Selection required”

If `channels resolve --live` returns multiple candidates, the tool refuses by default (safe no-op).
Re-run with `--pick N` (1-based) or re-run with an explicit channelId (starts with `UC...`).

## Channel export: out-dir not empty / resume

`channels export --live` writes local dataset files under `--out-dir`.
If the directory is not empty, the tool refuses unless you pass `--overwrite` (or global `--yes`) or use `--resume`.

If an export stops early (example: you used a low `--max-pages`), re-run with `--resume` to continue from `checkpoint.json`.
