# Authentication

Unsplash authentication is the part that decides which account the agent can see and which actions it can even plan. Keep the credential setup local, use the safe check first, and do not paste secrets or token files into chat.

For photo search, collections, tracked downloads, and local image files, the exact credential path is listed below. When OAuth is required, it means the user approves access through the provider instead of copying a long-lived password into the tool.

A good first auth check is: "Check which Unsplash credential path is configured, run the safe auth check, and stop before any token write or live account change."

## Setup details

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
