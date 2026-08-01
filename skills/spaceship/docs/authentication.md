# Authentication

Spaceship External API requests use two headers. The tool reads their values from `SPACESHIP_API_KEY` and `SPACESHIP_API_SECRET` and sends them as `X-API-Key` and `X-API-Secret` only to `https://spaceship.dev/api`.

```bash
qwayk-spaceship-safe-agent-cli --output json auth check
```

This command checks local configuration and reports the fixed host. It does not call Spaceship or prove the credentials' scopes.

Never commit `.env`, put credentials in command arguments, or paste them into chat. Errors, logs, plans, receipts, and JSON output must not contain either value.
