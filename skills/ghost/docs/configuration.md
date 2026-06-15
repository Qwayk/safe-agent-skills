# Configuration

Ghost configuration is the local setup an agent needs before it can review posts, pages, members, tags, and publication data. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Ghost values are required, which ones are optional, and confirm the setup without showing secrets."

## Where settings come from

Environment variables (read from `.env` by default):

- `GHOST_ADMIN_API_URL`: Admin API base URL, must include `/ghost/api/admin/`.
- `GHOST_ADMIN_API_KEY`: `id:secret` (secret is hex).
- `GHOST_ACCEPT_VERSION`: `v{major}.{minor}`.
- `GHOST_TIMEOUT_S`: optional seconds (default 30).

Tip: Use different `.env` files for staging/production:

```bash
ghost-api-tool --env-file .env.staging auth check
```
