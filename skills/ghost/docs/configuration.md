# Configuration

Environment variables (read from `.env` by default):

- `GHOST_ADMIN_API_URL`: Admin API base URL, must include `/ghost/api/admin/`.
- `GHOST_ADMIN_API_KEY`: `id:secret` (secret is hex).
- `GHOST_ACCEPT_VERSION`: `v{major}.{minor}`.
- `GHOST_TIMEOUT_S`: optional seconds (default 30).

Tip: Use different `.env` files for staging/production:

```bash
ghost-api-tool --env-file .env.staging auth check
```
