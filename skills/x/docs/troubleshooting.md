# Troubleshooting

When X stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reading posts, users, timelines, search results, and account-accessible social data, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the X error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## OAuth tokens

- If `auth token status` says the token is missing, run `auth token set` in dry-run first, then apply with `--apply --yes --ack-no-snapshot` after review.
- `auth pkce start` and `auth pkce finish` also plan first and require the same approval before writing PKCE/token state or calling the token endpoint.
- This is intentional until the tool saves real before-state for local auth files.
