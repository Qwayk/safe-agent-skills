# Configuration

Amazon PA-API v5 configuration is the local setup an agent needs before it can look up Amazon products, offers, images, and product metadata. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Amazon PA-API v5 values are required, which ones are optional, and confirm the setup without showing secrets."

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
Use this for CI or container runs.
