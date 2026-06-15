# Troubleshooting

When Mercury stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reviewing accounts, transactions, recipients, cards, and banking activity, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Mercury error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## API token issues

- If `auth check` fails, confirm your `.env` has:
  - `MERCURY_API_BASE_URL` (prod or sandbox)
  - `MERCURY_API_TOKEN` (starts with `secret-token:` per Mercury docs)
  - `MERCURY_AUTH_SCHEME` (`bearer` or `basic`)
