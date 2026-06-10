# Authentication

This tool uses Unsplash **Access Key** (API key) auth via:

- `Authorization: Client-ID YOUR_ACCESS_KEY`
- `Accept-Version: v1`

Configuration options:

1) Set `UNSPLASH_ACCESS_KEY` in your `.env` file (recommended).
2) Or store it locally under `.state/auth.json` with:

```bash
unsplash-api-tool auth key set --file auth.json
```

Notes:
- `.state/` is gitignored and must never be printed.
- OAuth/Bearer token flows are intentionally not implemented in this tool.

