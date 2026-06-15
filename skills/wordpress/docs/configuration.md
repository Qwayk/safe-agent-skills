# Configuration

WordPress configuration is the local setup an agent needs before it can review posts, pages, media, users, comments, and site content. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which WordPress values are required, which ones are optional, and confirm the setup without showing secrets."

## Where settings come from

Env vars:
- `WP_BASE_URL`
- `WP_USERNAME`
- `WP_APP_PASSWORD`

Optional:
- `--env-file` to load from a `.env` file.

## Recommended `.env`

```bash
WP_BASE_URL=https://example.com
WP_USERNAME=your-user
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

## `WP_BASE_URL` rules

- Use the **site root** (example: `https://example.com`).
- If you paste a full API URL like `https://example.com/wp-json/wp/v2`, the tool will normalize it back to `https://example.com`.
