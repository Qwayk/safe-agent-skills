# Connect your Awin Advertiser account

Run `awin-advertiser-safe-cli --env-file .env onboarding`. It creates a private settings file if needed and shows what to fill in. Add your Awin API token as `AWIN_API_TOKEN` and your advertiser ID as `AWIN_ADVERTISER_ID`. Use the advertiser ID shown in Awin for the program you want to work on. Keep the token and settings file out of chat and Git.

Run `awin-advertiser-safe-cli --env-file .env auth check`. The result shows the advertiser ID and whether the tool could read its publishers. Use the same `--env-file` for later commands. The file supplies all Awin settings when you name it. If you leave that flag out, shell settings take priority over the default `.env`.

Most users can leave `AWIN_API_BASE_URL` at its default, `https://api.awin.com`. `AWIN_API_TIMEOUT_S` defaults to 30 seconds. You can check setup without creating a file by adding `--no-write-env` to onboarding.

If the check fails, confirm the file path, token, advertiser ID, and your Awin plan and account permissions. Use `--verbose` to see request and response status lines and `--debug` for unexpected Python errors. Share the safe error message, without the token. If a token has been exposed, revoke it in Awin and update your settings file. [Awin API authentication](https://help.awin.com/apidocs/api-authentication)

The tool sends the token in the location each endpoint expects. The connection check uses the publishers endpoint. Conversion orders use the same token in the `x-api-key` header. [Exact authentication by command](api_coverage.md)
