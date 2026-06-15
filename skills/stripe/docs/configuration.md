# Configuration

Stripe configuration is the local setup an agent needs before it can review customers, payments, invoices, subscriptions, disputes, and account data. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Stripe values are required, which ones are optional, and confirm the setup without showing secrets."

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.env`: your real local configuration (gitignored; contains secrets)
- `.state/`: local run artifacts (and optional OAuth token helpers). Always gitignored.

By default, `.state/` lives next to your `--env-file`.

## Environment variables

Required:
- `STRIPE_API_KEY` (secret key or restricted key)

Optional:
- `STRIPE_TIMEOUT_S` (request timeout in seconds; default `30`)
- `STRIPE_VERSION` (sets the `Stripe-Version` header)
- `STRIPE_ACCOUNT_ALLOWLIST` (comma-separated `acct_...` ids; out-of-allowlist values are refused when you pass `--stripe-account`)

## OS environment override

OS environment variables override values from the env file.
Use this for CI or container runs.
