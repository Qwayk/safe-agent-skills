# Connect to Sovrn

Run `sovrn-safe-cli --env-file .env onboarding`. It creates a private settings file if needed. Add the key for the job you want to do and keep it out of chat and Git.

| What you want to do | What to add to the file |
| --- | --- |
| Check a link, request a bid, or get product suggestions | `SOVRN_COMMERCE_SITE_API_KEY` |
| Read Commerce reports, campaigns, or approved merchants | `SOVRN_COMMERCE_SECRET_KEY` |
| Find coupons or compare product prices | Both Commerce keys |
| Read an Advertising report | `SOVRN_ADVERTISING_API_KEY` and `SOVRN_ADVERTISING_PUBLISHER_ID`. You can also pass the ID to a report with `--publisher-id`. |

Find the Commerce keys in Sovrn's Commerce settings for the site you want to use. For Advertising, look under **Account → API Keys** and use the publisher ID for the report you want. [Commerce keys](https://developer.sovrn.com/docs/authorization) · [Advertising keys](https://developer.sovrn.com/reference/authorization-1)

Run `sovrn-safe-cli --env-file .env auth check`. It checks that the settings are filled in. Run a report or link check to confirm Sovrn accepts them. Repeat the same `--env-file` flag for every command. Naming a file makes the tool read all Sovrn settings from that file. When you leave the flag out, shell settings take priority over the default `.env`.

## If a request fails

- Check the settings path and make sure the key is for the right site or publisher. A Commerce site API key can check a link. It takes a Commerce secret key to read that site's earnings.
- For an empty report, check the publisher or site, date range, and any filters before drawing a conclusion.
- For a request limit error, wait for the time Sovrn gives you. See [the command guide](command_reference.md) for report and merchant list limits.
- Optional settings include `SOVRN_TIMEOUT_S`, which defaults to 30 seconds. Use `--verbose` for request status lines or `onboarding --no-write-env` to check setup without creating a file.
