# Troubleshooting

When Threads stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reading profiles, posts, replies, and account media the connected app can access, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Threads error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## OAuth tokens

- If `auth token status` says no file token is present, run:
  - `threads-api-tool --output json auth code exchange --code <code>`
  - `threads-api-tool --output json --apply auth code exchange --code <code>`
- If token checks fail, use:
  - `threads-api-tool --output json auth check`
  - `threads-api-tool --output json auth debug-token [--input-token <token>]`
  - `threads-api-tool --output json auth token status`
