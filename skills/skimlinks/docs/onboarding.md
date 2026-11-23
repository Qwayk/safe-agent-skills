# Connect your Skimlinks account

## Set up merchant search and reports

1. Run `skimlinks-safe-cli onboarding`. It creates a private `.env` file with spaces for your settings. It leaves an existing file as it is.
2. In Publisher Hub, open Toolbox, APIs, then API Authentication. Enter your Client ID and Client Secret in `SKIMLINKS_CLIENT_ID` and `SKIMLINKS_CLIENT_SECRET`. Enter your Publisher ID in `SKIMLINKS_PUBLISHER_ID`. Keep these values in your local file and out of chat and Git.
3. Run `skimlinks-safe-cli auth check`. On success, Skimlinks issued a temporary token. Run [a small merchant search](quickstart.md) to check that your Publisher ID works.

Merchant and Reporting use the same credentials. The CLI requests a temporary token from `https://authentication.skimapis.com/access_token` using `client_credentials`.

## Use a separate settings file

Keep a file for each account in a private folder. Use the same file for setup and later commands.

```bash
skimlinks-safe-cli --env-file /path/to/account.env onboarding
skimlinks-safe-cli --env-file /path/to/account.env auth check
```

When you pass `--env-file`, the tool takes its settings from that file alone. Command options such as `--publisher-id` still let you choose the target for a single call. Without `--env-file`, shell settings take priority over the default `.env`.

`onboarding --no-write-env` checks which settings are present without creating a file.

## Add Product Key access

Set `SKIMLINKS_PUBLISHER_DOMAIN_ID` or pass `--publisher-domain-id` on a lookup. Merchant commands with that filter can also use the saved value.

If Skimlinks gave you separate Product Key credentials, fill in both `SKIMLINKS_PRODUCT_CLIENT_ID` and `SKIMLINKS_PRODUCT_CLIENT_SECRET`. Leave both blank to try the shared credentials. Run `skimlinks-safe-cli auth check --scope product` to see which credentials got a token. Run one [Product Key lookup](command_reference.md#product-key) to check actual access. Ask Skimlinks to enable Product Key if its API denies access with the right publisher and domain IDs.

## Build links without signing in

In Publisher Hub, open Setup and find the Site ID for the site where you’ll use the link. Set `SKIMLINKS_LINK_WRAPPER_ID` or pass `--id` when you build a link. The tool makes the URL on your computer.

## If a command fails

- **Settings are missing.** Run onboarding with the same settings file, then fill in the fields it lists.
- **Skimlinks rejects the credentials.** Check the Client ID and Client Secret in Publisher Hub. If sign-in works but a merchant search fails, check the Publisher ID on the request.
- **A report fails.** Check the date range and choose fields from that report's dimensions and metrics commands. Keep the HTTP status or the report line number when asking for help.
- **A link will not build.** Check the Site ID and use a full destination address with `http://` or `https://` and a hostname.
- **You need more detail.** `--verbose` shows the request and status without the credentials. `--debug` is for local Python troubleshooting.

For special setups, `SKIMLINKS_TIMEOUT_S` defaults to 30 seconds. Service addresses use the official defaults. The override names are `SKIMLINKS_AUTH_URL`, `SKIMLINKS_MERCHANT_BASE_URL`, `SKIMLINKS_REPORTING_BASE_URL`, `SKIMLINKS_PRODUCT_BASE_URL`, and `SKIMLINKS_LINK_WRAPPER_BASE_URL`.
