# Configuration

Sovrn configuration is the local setup an agent needs before it can review publishers, links, reporting, and affiliate performance. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Sovrn values are required, which ones are optional, and confirm the setup without showing secrets."

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)

## Environment variables

Use these Sovrn-specific variables:
- `SOVRN_COMMERCE_SECRET_KEY`
- `SOVRN_COMMERCE_SITE_API_KEY`
- `SOVRN_ADVERTISING_API_KEY`
- `SOVRN_ADVERTISING_PUBLISHER_ID`
- `SOVRN_TIMEOUT_S` (optional; default is 30)

## Which commands need which auth

- Commerce secret-header commands use `SOVRN_COMMERCE_SECRET_KEY`
- Commerce site-key commands use `SOVRN_COMMERCE_SITE_API_KEY`
- Mixed Commerce flows such as coupons and price comparisons use both Commerce values
- Advertising reporting commands use `SOVRN_ADVERTISING_API_KEY` plus `SOVRN_ADVERTISING_PUBLISHER_ID`

`auth check` is a local config check.
It reports which values are present and which real command bundles are ready.
Use the real endpoint commands for live network proof.

## OS environment override

OS environment variables override values from the env file.
Use this for CI or container runs.
