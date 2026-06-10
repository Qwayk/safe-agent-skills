# Authentication

Plausible uses API keys (no OAuth).

## API key

Create a new API key in Plausible:
- Plausible → Settings → API Keys → New API Key

Then store it locally in `.env` as `PLAUSIBLE_API_KEY`.

This tool never prints the API key value.

## Permissions and owner-only endpoints

- Sites API v1 endpoints (under `/api/v1/sites` and subpaths) require a Bearer token header and use the same `PLAUSIBLE_API_KEY`.
- Some destructive Sites API operations (example: deleting a site or deleting a goal) require the API key to belong to the **owner** of the site.
  If you see permission errors, create/use an owner API key for that site.
