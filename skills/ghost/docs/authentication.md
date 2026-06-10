# Authentication

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
