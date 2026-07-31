# Authentication

Porkbun commands use API keys from `.env`:

- `PORKBUN_API_KEY`
- `PORKBUN_SECRET_API_KEY`

Store them in `.env` or environment variables. Never paste them in chat.

## Auth check command

```bash
porkbun --output json auth check
```

`auth check` is a read-only safe verification.

## OAuth and tokens

This tool does not use OAuth token files.
