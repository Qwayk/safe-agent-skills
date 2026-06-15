# Authentication

Ghost authentication is meant to be local and boring: put the required key or token in your `.env` file, keep it out of chat, and run the safe check before asking an agent for real account data.

That matters because posts, pages, members, newsletters, offers, themes, and webhooks can contain account or business data. The auth check should prove the credential works without printing the secret value.

A good first auth check is: "Confirm the required Ghost environment values are present, run the safe auth check, and tell me whether the credential works without showing the secret."

## Setup details

`ghost-api-tool` uses Ghost Admin API **token authentication** (JWT).

Config:
- `GHOST_ADMIN_API_URL`
- `GHOST_ADMIN_API_KEY` (`id:secret` where secret is hex)
- `GHOST_ACCEPT_VERSION` (`v{major}.{minor}`)

JWT notes (per Ghost docs):
- HS256
- header: `kid` is the key id
- payload: `aud=/admin/`, `iat`, `exp` (max 5 minutes)

The tool never prints the API key or JWT token.
