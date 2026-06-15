# Troubleshooting

When Shopify Admin stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reviewing products, orders, customers, collections, and store data, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Shopify Admin error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## Auth failures

- Verify your custom app has the required access scopes for the operation you’re calling.
- Re-run `shopify-admin-api-tool --output json auth check` (read-only).

## Mutation apply refuses

This is expected today. Shopify mutation dry-runs still create plans, but live apply requires explicit no-snapshot approval before Shopify HTTP until the requested operation has a safe before-state capture path.
