# Troubleshooting

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
