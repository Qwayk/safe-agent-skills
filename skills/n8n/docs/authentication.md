# Authentication

This tool uses n8n public API keys.

Set:

```bash
N8N_BASE_URL=https://your-instance.app.n8n.cloud/api/v1
N8N_API_KEY=your_n8n_api_key
```

The CLI sends the key as `X-N8N-API-KEY`. It never prints the key. Plans and receipts use a short fingerprint so apply can confirm the same key was used after review.

If your n8n plan supports scoped keys, use the narrowest scopes that match the task.
