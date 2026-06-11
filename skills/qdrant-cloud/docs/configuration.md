# Configuration

This tool uses a `.env` file for configuration.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/`: local run history and audit logs (gitignored)

## Environment variables

Required for live API calls:
- `QDRANT_CLOUD_API_KEY`

If the key contains shell-special characters such as `|`, quote it:

```env
QDRANT_CLOUD_API_KEY='your_real_key_here'
```

Optional:
- `QDRANT_CLOUD_API_BASE_URL` (default: `https://api.cloud.qdrant.io`)
- `QDRANT_CLOUD_TIMEOUT_S` (default: `30`)

## OS environment override

OS environment variables override values from the env file.
This is useful in CI or when running in containers.

If your real env file is not in this tool folder, prefer `--env-file /full/path/to/.env`.
