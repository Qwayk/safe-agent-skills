# Authentication

Instantly API v2 uses an API key.

## Where the key lives

- Put the key in your local `.env` file (gitignored).
- Key name: `INSTANTLY_API_KEY`

## How it’s sent

- The CLI sends: `Authorization: Bearer <INSTANTLY_API_KEY>`
- Base URL default: `https://api.instantly.ai/api/v2`

## Smoke test (safe, read-only)

```bash
instantly-api-tool --output json auth check
```
