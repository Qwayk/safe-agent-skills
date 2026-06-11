# Configuration

This tool uses a `.env` file for configuration.

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
This is useful in CI or when running in containers.
