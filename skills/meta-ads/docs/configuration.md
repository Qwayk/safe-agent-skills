# Configuration

Meta Ads configuration is the local setup an agent needs before it can review ad accounts, campaigns, ad sets, ads, insights, and creative data. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Meta Ads values are required, which ones are optional, and confirm the setup without showing secrets."

## Where settings come from

Settings can come from:
- OS environment variables (highest priority), and
- an optional env file (`--env-file`, default: `.env`)

## Required

- `META_ADS_ACCESS_TOKEN`
  - OAuth access token for Graph API requests.
  - Never commit this value; never paste it into chat.

## Recommended

- `META_ADS_AD_ACCOUNT_ID`
  - Either a numeric id (`123...`) or `act_<id>`.
  - If you set a numeric id, the tool normalizes it to `act_<id>`.

## Optional

- `META_ADS_BASE_URL`
  - Default: `https://graph.facebook.com`
- `META_ADS_API_VERSION`
  - Default: `v24.0` (see `src/meta_ads_api_tool/config.py`)
- `META_ADS_TIMEOUT_S`
  - Default: `30`
- `META_ADS_MAX_RETRIES`
  - Default: `5` (retries for 429/5xx with backoff)
