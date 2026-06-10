# Configuration

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
