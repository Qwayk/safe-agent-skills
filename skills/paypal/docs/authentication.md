# Authentication

This tool uses PayPal’s official OAuth 2.0 client-credentials flow as the normal auth path.

## Normal path

Put these values in `.env`:

- `PAYPAL_ENVIRONMENT=sandbox` or `live`
- `PAYPAL_CLIENT_ID`
- `PAYPAL_CLIENT_SECRET`

Then run:

```bash
qwayk-paypal-safe-agent-cli auth check
```

`auth check` safely requests an OAuth access token from PayPal and reports non-secret metadata such as the environment, token type, expiry window, and configured partner-header state.

## Optional advanced override

If you already have a short-lived PayPal bearer token outside the tool, you can set:

- `PAYPAL_ACCESS_TOKEN`

That is optional and not the normal setup. The tool prefers client ID plus client secret for regular use.

## Optional partner / on-behalf-of headers

Some PayPal product areas need extra headers:

- `PAYPAL_PARTNER_ATTRIBUTION_ID`
- `PAYPAL_AUTH_ASSERTION`

Leave them blank unless your PayPal integration requires them.

Important:
- Never commit `.env`
- Never paste PayPal secrets into chat
- Keep `sandbox` values separate from `live` values
