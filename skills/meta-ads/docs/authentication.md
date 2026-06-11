# Authentication

This tool uses a Meta Graph API **access token** stored locally in your `.env` file.

## Where the token lives

- In your local `.env` file as `META_ADS_ACCESS_TOKEN=...`
- Or provided via OS environment variable `META_ADS_ACCESS_TOKEN`

Never commit `.env`. Never paste the token into chat.

## How the token is sent

The tool sends the token via the `Authorization: Bearer <token>` header.

## Auth check

Run one of:

```bash
meta-ads-api-tool --output json auth check
meta-ads-api-tool --output json --ad-account-id act_<id> auth check
```

If `META_ADS_AD_ACCOUNT_ID` (or `--ad-account-id`) is available, `auth check` prefers an ad-account scoped GET.

