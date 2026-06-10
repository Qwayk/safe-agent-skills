# Authentication

This tool supports Mercury API token authentication.

## Configure `.env` (recommended)

Put your Mercury API token in `.env` (gitignored):

- `MERCURY_API_TOKEN=secret-token:...`

Choose an auth scheme (default: bearer):

- `MERCURY_AUTH_SCHEME=bearer` (sends `Authorization: Bearer <token>`)
- `MERCURY_AUTH_SCHEME=basic` (sends HTTP Basic with `username=<token>` and empty password)

Then run a read-only smoke check:

```bash
mercury-api-tool --output json auth check
```

Important:
- Never commit `.env` or any token files.
- Never paste tokens into chat.
