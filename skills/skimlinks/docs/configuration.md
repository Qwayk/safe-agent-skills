# Configuration

Configuration lives in `.env`, which is gitignored.

OS environment variables override `.env` values.

## Required

- `SKIMLINKS_CLIENT_ID`
- `SKIMLINKS_CLIENT_SECRET`
- `SKIMLINKS_PUBLISHER_ID`

## Required For Product Key

- `SKIMLINKS_PUBLISHER_DOMAIN_ID`, unless `--publisher-domain-id` is passed on the Product Key command.

## Optional

- `SKIMLINKS_LINK_WRAPPER_ID`
- `SKIMLINKS_PRODUCT_CLIENT_ID`
- `SKIMLINKS_PRODUCT_CLIENT_SECRET`
- `SKIMLINKS_TIMEOUT_S`

`SKIMLINKS_PUBLISHER_DOMAIN_ID` is optional only for Merchant commands that support it as a default filter.

## Advanced Overrides

Leave these at the defaults unless Skimlinks changes the official hosts:

- `SKIMLINKS_AUTH_URL`
- `SKIMLINKS_MERCHANT_BASE_URL`
- `SKIMLINKS_REPORTING_BASE_URL`
- `SKIMLINKS_PRODUCT_BASE_URL`
- `SKIMLINKS_LINK_WRAPPER_BASE_URL`

Tracked files must never contain real credentials.
