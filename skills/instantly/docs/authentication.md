# Authentication

Instantly authentication is meant to be local and boring: put the required key or token in your `.env` file, keep it out of chat, and run the safe check before asking an agent for real account data.

That matters because campaigns, leads, accounts, inboxes, analytics, and send-related workflows can contain account or business data. The auth check should prove the credential works without printing the secret value.

A good first auth check is: "Confirm the required Instantly environment values are present, run the safe auth check, and tell me whether the credential works without showing the secret."

## Authentication notes

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
