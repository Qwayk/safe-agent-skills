# Troubleshooting

## Auth fails (401/403)
- Confirm `FREEPIK_API_KEY` is correct.
- Confirm you are using Freepik's OpenAPI v1 header:
  - `FREEPIK_AUTH_HEADER=x-freepik-api-key`
  - `FREEPIK_AUTH_PREFIX=` (empty)

## Download fails: "restricted to Premium users" (403)
- You tried to download a `premium` resource with a non-premium API plan.
- Fix options:
  - Search freemium-only resources: `--param 'filters[license][freemium]=1'`
  - Or upgrade your plan, then retry.

## Download refuses: cannot find `license_url` or `download_url`
- The API response shape may differ from our defaults.
- Provide JSONPaths:
  - `--license-url-jsonpath` (resource detail JSON)
  - `--download-url-jsonpath` (download JSON)
  - or set defaults in `.env`

## Search fails with HTTP 400: "filters.content_type must be an array"
Some filters are arrays in Freepik’s API and must be encoded with `[]`.

- ✅ `--param 'filters[content_type][]=photo'`
- ❌ `--param 'filters[content_type]=photo'`

## How to exclude AI-generated results
The Freepik API does not reliably expose an “exclude AI” search filter.

If you want to sanity-check a single result, fetch the detail and look for AI hints (fields may vary by resource type/account):
- `freepik-api-tool resource get --id ID`
- Check for fields like `has_prompt` / `is_ai_generated` in the JSON.

If you want the tool to enforce AI exclusion automatically (slower, because it does extra API calls):
- `freepik-api-tool search images ... --exclude-ai`

Always validate by eye before downloading/licensing.

## Debug requests
Use `--verbose` to see request start/end lines.
Secrets are never printed.

## Debug errors

By default the tool prints a single JSON error message.
If you want the full Python stack trace (developer debugging), add `--debug`.

## Search reliability notes
- Very large `--limit` values can fail or time out (observed during migration). Prefer `--limit <= 100`.
