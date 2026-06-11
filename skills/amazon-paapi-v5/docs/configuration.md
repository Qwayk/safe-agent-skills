# Configuration

This tool uses a `.env` file for configuration.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)

## Environment variables

Required:
- `AMAZON_PA_ACCESS_KEY_ID`
- `AMAZON_PA_SECRET_ACCESS_KEY`
- `AMAZON_PA_PARTNER_TAG`

Optional:
- `AMAZON_PA_PARTNER_TYPE` (default: `Associates`)
- `AMAZON_PA_HOST` (default: `webservices.amazon.com`)
- `AMAZON_PA_REGION` (default: `us-east-1`)
- `AMAZON_PA_MARKETPLACE` (default: `www.amazon.com`)
- `AMAZON_PA_TIMEOUT_S` (default: `30`)

## OS environment override

OS environment variables override values from the env file.
This is useful in CI or when running in containers.
