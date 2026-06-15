# Configuration

Qdrant Cloud configuration is the local setup an agent needs before it can inspect clusters, collections, keys, and vector database project data. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Qdrant Cloud values are required, which ones are optional, and confirm the setup without showing secrets."

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
Use this for CI or container runs.

If your real env file is not in this tool folder, prefer `--env-file /full/path/to/.env`.
