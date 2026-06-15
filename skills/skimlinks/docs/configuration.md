# Configuration

Skimlinks configuration is the local setup an agent needs before it can review merchants, links, performance, and affiliate reporting. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Skimlinks values are required, which ones are optional, and confirm the setup without showing secrets."

## Setup note

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
