# Troubleshooting

When Amazon PA-API v5 stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent looking up Amazon products, offers, images, and product metadata, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Amazon PA-API v5 error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no keys).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## Common PA-API errors

- `InvalidSignatureException`: usually wrong region/host, wrong secret key, or a system clock issue.
- `TooManyRequests`: you are throttled; retry later (jobs already retries a little).
