# Authentication

This tool uses an API key in `.env`:

- `QDRANT_CLOUD_API_KEY`
- Requests use the header `Authorization: apikey <KEY>` (never printed).

If the key contains shell-special characters such as `|`, store it like this:

```env
QDRANT_CLOUD_API_KEY='your_real_key_here'
```

If your real `.env` lives outside this tool folder, run the tool with `--env-file /full/path/to/.env`.

Important:
- Never commit `.env` or `.state/`.
- Never paste API keys into chat.
