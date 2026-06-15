# Configuration

Shopify Admin configuration is the local setup an agent needs before it can review products, orders, customers, collections, and store data. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Shopify Admin values are required, which ones are optional, and confirm the setup without showing secrets."

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/`: local-only run history and artifacts (gitignored; written next to your `--env-file`)

## Environment variables

Required:
- `SHOPIFY_SHOP_DOMAIN` (example: `your-shop.myshopify.com`)
- `SHOPIFY_ADMIN_ACCESS_TOKEN` (custom app Admin API access token)
- `SHOPIFY_ADMIN_API_VERSION` (pinned; example: `2026-01`)

Optional:
- `SHOPIFY_TIMEOUT_S` (default: `30`)

## OS environment override

OS environment variables override values from the env file.
Use this for CI or container runs.
