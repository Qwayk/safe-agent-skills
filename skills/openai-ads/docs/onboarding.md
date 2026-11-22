# Connect your Ads account

Get an Advertiser API key for the account you want to use in Ads Manager. The key is for one ad account. Keep it in a local settings file or in your shell.

Run:

```bash
openai-ads-safe-agent-cli onboarding
```

Add the key as `OPENAI_ADS_API_KEY` in the selected file. The default file is `.env`. If you use another file, pass `--env-file` before the command. Onboarding prints the account check with that same file. Use `onboarding --no-write-env` to see the steps without creating a file.

```bash
openai-ads-safe-agent-cli --env-file ads.env auth check
```

The check reads `GET /ad_account`. Confirm it shows the account you intended. The default Ads API URL is `https://api.ads.openai.com/v1`, and the request timeout is 30 seconds. Shell settings take priority over the file. See [`.env.example`](../.env.example) for the available settings.

## For server-side conversion events

Use `OPENAI_ADS_PIXEL_ID` and the separate `OPENAI_ADS_CONVERSIONS_API_KEY`. The default Conversions API URL is `https://bzr.openai.com/v1`. See [OpenAI’s Conversions API guide](https://developers.openai.com/ads/conversions-api) for event fields and account setup.

## Common errors

- If the CLI says the key is missing, check the selected file and shell settings.
- If OpenAI refuses the account check, check the key’s account and access in Ads Manager. Use the error to see whether billing or verification needs attention.
- If a change is refused, read the reason and review the [approval steps](safety_model.md) before trying again.
