# Authentication

Plausible authentication is the part that decides which account the agent can see and which actions it can even plan. Keep the credential setup local, use the safe check first, and do not paste secrets or token files into chat.

For sites, stats, goals, shared links, team members, and account settings, the exact credential path is listed below. When OAuth is required, it means the user approves access through the provider instead of copying a long-lived password into the tool.

A good first auth check is: "Check which Plausible credential path is configured, run the safe auth check, and stop before any token write or live account change."

## API key

Create a new API key in Plausible:
- Plausible → Settings → API Keys → New API Key

Then store it locally in `.env` as `PLAUSIBLE_API_KEY`.

This tool never prints the API key value.

## Permissions and owner-only endpoints

- Sites API v1 endpoints (under `/api/v1/sites` and subpaths) require a Bearer token header and use the same `PLAUSIBLE_API_KEY`.
- Some destructive Sites API operations (example: deleting a site or deleting a goal) require the API key to belong to the **owner** of the site.
  If you see permission errors, create/use an owner API key for that site.
