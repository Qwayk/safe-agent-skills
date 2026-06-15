# Authentication

Meta Ads authentication is meant to be local and boring: put the required key or token in your `.env` file, keep it out of chat, and run the safe check before asking an agent for real account data.

That matters because ad accounts, campaigns, ad sets, ads, insights, and Graph API inventory can contain account or business data. The auth check should prove the credential works without printing the secret value.

A good first auth check is: "Confirm the required Meta Ads environment values are present, run the safe auth check, and tell me whether the credential works without showing the secret."

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
