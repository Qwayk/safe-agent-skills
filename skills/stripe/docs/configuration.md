# Configuration

This tool uses a local `.env` file for configuration (secrets stay on your machine).

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
This is useful in CI or when running in containers.
