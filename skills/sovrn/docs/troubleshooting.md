# Troubleshooting

When Sovrn stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reviewing publishers, links, reporting, and affiliate performance, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Sovrn error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## Sovrn auth split

- If Commerce report commands fail, check `SOVRN_COMMERCE_SECRET_KEY` first.
- If Link Check, Bid Check, or product recommendation commands fail, check `SOVRN_COMMERCE_SITE_API_KEY`.
- If Advertising commands fail, make sure both `SOVRN_ADVERTISING_API_KEY` and `SOVRN_ADVERTISING_PUBLISHER_ID` are set.
