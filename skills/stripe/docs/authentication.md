# Authentication

This tool supports Stripe API key auth (recommended) and a local OAuth token helper (advanced / optional).

## Stripe API key in `.env` (recommended)

Put your Stripe key in `.env` (gitignored). The tool never prints your key and always redacts Authorization headers.

Minimum required config:
- `STRIPE_API_KEY` (secret; never commit)

Optional:
- `STRIPE_TIMEOUT_S` (request timeout in seconds; default `30`)
- `STRIPE_VERSION` (sets the `Stripe-Version` header)
- `STRIPE_ACCOUNT_ALLOWLIST` (comma-separated `acct_...` ids)

## OAuth token helpers (manual copy/paste; optional)

Stripe’s core API is typically used with API keys. If you have a token JSON from an OAuth flow you control, you can store it locally for future use by your agent:

1) Get a token JSON file from an OAuth flow you already run (OAuth app setup is out of scope for this tool).
2) Store it in the tool:

```bash
stripe-api-tool auth token set --file token.json
```

3) Check status (safe; never prints token values):

```bash
stripe-api-tool auth token status
```

Tokens are stored under `.state/token.json` next to your `--env-file`.

Important:
- Never commit `.state/`
- Never print tokens in logs
