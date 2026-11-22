# Connect your LinkedIn Ads account

Use an access token issued through an approved LinkedIn app. The app needs access to the LinkedIn product you want to use. The token needs the right permissions, and the signed-in member needs access to the ad account.

From the folder where you want to keep your local settings, run:

```bash
linkedin-ads-api-tool --output json onboarding
```

This creates a `.env` file if one is missing. To use another file, put `--env-file path/to/settings.env` before the command. Keep the settings file and any saved tokens on your computer. Leave their contents out of chat and Git.

## Add your token

Put your token in `LINKEDIN_ADS_TOKEN` in the settings file. The tool checks that key first, then `LINKEDIN_ADS_ACCESS_TOKEN`, then `LINKEDIN_ADS_API_TOKEN`. It skips empty values and uses the shell value first when the same key appears in both places.

If you already have a token JSON file from your app, you can save it with:

```bash
linkedin-ads-api-tool --output json auth token set --file token.json
linkedin-ads-api-tool --output json auth token status
```

The tool looks in `.state/token.json` beside your settings file when the other token settings are empty. It accepts `access_token`, `accessToken`, or `token` in that file. The status command shows information about the saved file without revealing its token.

## Check your access

```bash
linkedin-ads-api-tool --output json auth check
```

The tool asks LinkedIn which ad accounts the signed-in member can access. Check the account ID and role before choosing an account. An empty list gives you no account to use. A successful check here still leaves reporting permissions and access to other products to check separately.

## Optional settings

The default API address is `https://api.linkedin.com/rest`. The tool uses LinkedIn Marketing version `202605`, Rest.li protocol version `2.0.0`, and a 30-second request timeout. You can set `LINKEDIN_ADS_BASE_URL`, `LINKEDIN_ADS_LINKEDIN_VERSION`, `LINKEDIN_ADS_RESTLI_PROTOCOL_VERSION`, or `LINKEDIN_ADS_TIMEOUT_S` to change those values. A shell setting for the same key takes priority over the file.

Continue with [your first campaign report](quickstart.md) or [check a connection error](troubleshooting.md).
