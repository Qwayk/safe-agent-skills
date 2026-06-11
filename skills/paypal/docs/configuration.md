# Configuration

This tool uses a local `.env` file for PayPal setup.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/`: local run history, plans, receipts, and proof files

## Environment variables

Required for normal use:

- `PAYPAL_ENVIRONMENT`
  - `sandbox` or `live`
- `PAYPAL_CLIENT_ID`
- `PAYPAL_CLIENT_SECRET`

Optional:

- `PAYPAL_API_BASE_URL`
  - Leave blank for the normal PayPal base URL for the selected environment.
- `PAYPAL_ACCESS_TOKEN`
  - Advanced manual override only.
- `PAYPAL_PARTNER_ATTRIBUTION_ID`
- `PAYPAL_AUTH_ASSERTION`
- `PAYPAL_ACCEPT_LANGUAGE`
  - Default: `en_US`
- `PAYPAL_TIMEOUT_S`
  - Default: `30`

Default base URLs:

- Sandbox: `https://api-m.sandbox.paypal.com`
- Live: `https://api-m.paypal.com`

## OS environment override

OS environment variables override values from the env file.
This is useful in CI or when running in containers.
