# Connect your Meta Ads account

Use a Meta access token that can read the ad account. Meta’s `ads_read` permission covers typical reporting reads. Keep the token in your local settings file or shell.

```bash
meta-ads-api-tool onboarding
```

Add the token under `META_ADS_ACCESS_TOKEN`. The default file is `.env`. To use a different file, pass `--env-file` before the command. Onboarding shows the account-check command with that same file. To see the instructions before creating anything, use `onboarding --no-write-env`.

```bash
meta-ads-api-tool --env-file meta.env auth check
meta-ads-api-tool --env-file meta.env ad-accounts list --fields id,name
```

After choosing an account, you can save it as `META_ADS_AD_ACCOUNT_ID`. A numeric ID or the same ID starting with `act_` works. If you pass an account for one command, it takes priority. Shell settings take priority over the settings file.

The default Marketing API version is `v25.0`, and the default host is `https://graph.facebook.com`. The default timeout is 30 seconds, with up to five retries for rate limits and temporary server errors. See [the settings example](../.env.example) for the setting names.

## Common errors

- If the token is missing, check the file you selected and your shell settings.
- If Meta returns OAuth error 190, check whether the token expired and replace it through Meta’s supported token setup.
- If the account is missing, list the accounts this token can read. Check the token’s permissions and account access in Meta before deciding which account to use.
- If a report hits a rate limit, start with a shorter period or fewer fields. Check [report limits](safety_model.md) before using a smaller result to make a decision.
