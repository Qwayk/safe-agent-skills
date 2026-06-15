# Configuration

PayPal configuration is the local setup an agent needs before it can review orders, payments, captures, refunds, subscriptions, and account activity. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which PayPal values are required, which ones are optional, and confirm the setup without showing secrets."

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
Use this for CI or container runs.
