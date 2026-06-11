# Configuration

This tool uses a local `.env` file for configuration and a local `.state/token.json` file for OAuth tokens.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/token.json`: OAuth token storage (gitignored; created via `msads-api-tool auth token set`)

By default, `.state/token.json` is stored next to your `--env-file`.

## Environment variables

See `.env.example` for the full list. The key ones are:

- `MSADS_ENVIRONMENT`: `prod` or `sandbox` (default: `prod`)
- `MSADS_TIMEOUT_S`: HTTP timeout seconds (default: `30`)
- `MSADS_DEVELOPER_TOKEN`: required for live API calls (never printed)
- `MSADS_CUSTOMER_ID`, `MSADS_CUSTOMER_ACCOUNT_ID`: optional defaults for SOAP headers
- `MSADS_OAUTH_CLIENT_ID`: required for token refresh (and for interactive OAuth flows outside this tool)
- `MSADS_OAUTH_CLIENT_SECRET`: optional; required for confidential clients (web apps) when refreshing tokens
- `MSADS_OAUTH_TENANT`: token endpoint tenant segment (default: `common`)
- `MSADS_OAUTH_SCOPE`: OAuth scope string (default: `https://ads.microsoft.com/msads.manage offline_access`)

Advanced (optional overrides):
- `MSADS_CAMPAIGN_MANAGEMENT_URL`, `MSADS_BULK_URL`, `MSADS_REPORTING_URL`, `MSADS_AD_INSIGHT_URL`,
  `MSADS_CUSTOMER_MANAGEMENT_URL`

## OS environment override

OS environment variables override values from the env file.
This is useful in CI or when running in containers.
