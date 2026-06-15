# Authentication

Qdrant Cloud authentication is meant to be local and boring: put the required key or token in your `.env` file, keep it out of chat, and run the safe check before asking an agent for real account data.

That matters because clusters, backups, API keys, cloud accounts, and vector database resources can contain account or business data. The auth check should prove the credential works without printing the secret value.

A good first auth check is: "Confirm the required Qdrant Cloud environment values are present, run the safe auth check, and tell me whether the credential works without showing the secret."

## Setup details

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
