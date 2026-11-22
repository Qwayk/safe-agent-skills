# Connect your TikTok ad account

Use an app ID, app secret, and access token from your TikTok for Business app. The token needs access to the ad account you want to use.

From the folder where you want to keep your settings, run:

```bash
tiktok-marketing-api-tool --output json onboarding
```

This creates `.env` if it is missing and tells you which settings still need a value. To use a different file, put `--env-file path/to/settings.env` before the command and pass it again on later commands.

## Add your app and token

In `.env`, fill in `TIKTOK_MARKETING_APP_ID` and `TIKTOK_MARKETING_APP_SECRET`. Put the token in `TIKTOK_MARKETING_ACCESS_TOKEN`. Keep these values on your computer and out of chat and Git.

You can also save a token from an existing local JSON file:

```bash
tiktok-marketing-api-tool --output json auth token set --file token.json
tiktok-marketing-api-tool --output json auth token status
```

The tool uses the token in `.state/token.json` next to your settings file when the environment and settings file provide no token. The status command reports the presence of the saved file without showing the token. If you need to exchange an approval code for a token, see `api ops show --op oauth2-access-token`. Sending that request uses the [same approval steps](safety_model.md) as other writes.

## Choose an ad account

```bash
tiktok-marketing-api-tool --output json auth check
```

This read contacts TikTok directly. Look for the ad account's name and ID in `advertisers`. If the list is empty, check which accounts authorized the app. When several accounts appear, choose the one you want before requesting a report or change.

## Optional settings

The default API address is `https://business-api.tiktok.com` and the request timeout is 30 seconds. Set `TIKTOK_MARKETING_API_BASE_URL` or `TIKTOK_MARKETING_TIMEOUT_S` to change either setting. A shell environment value for a key takes priority over its value in the settings file.

Continue with [your first report](quickstart.md#run-a-seven-day-report) or [check a setup error](troubleshooting.md).
