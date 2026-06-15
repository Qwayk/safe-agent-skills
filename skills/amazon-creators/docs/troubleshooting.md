# Troubleshooting

When Amazon Creators stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent checking creator lists, storefront details, and creator-campaign reporting, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Amazon Creators error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## OAuth tokens

- If `auth token status` says the token is missing or expired, the current source tool cannot create or replace the cache automatically yet.
- `auth token fetch` and `auth token set --file token.json` now produce plans; confirmed apply requires explicit no-snapshot approval before token endpoint use or `.state/token.json` writes when no saved snapshot is available.
- Existing cached tokens can still be used by catalog reads.

## Local helper apply refused

This is expected for onboarding env creation and token-cache helpers.
The safe result is `refused=true`, `before_state.status=no_snapshot_available`, and no `.env` or `.state/token.json` write from the blocked flow.
