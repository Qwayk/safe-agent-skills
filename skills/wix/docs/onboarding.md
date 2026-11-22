# Connect Wix

Use `wix-safe-agent-cli --env-file .env onboarding` to create a settings file. You can choose another file with `--env-file`. Keep keys, secrets, the file and `.state/token.json` out of Git and chat.

## Choose how to connect

- **To list sites or manage the account**, add `WIX_API_KEY` and `WIX_ACCOUNT_ID`. Start with `auth check` or `sites query --limit 5`. The site list gives you each site’s name and ID.
- **To work on one site**, use an existing app token in `WIX_ACCESS_TOKEN` or supply `WIX_APP_ID`, `WIX_APP_SECRET`, and `WIX_INSTANCE_ID`. Run `auth check` with the same file. The returned site name and ID come from Wix’s app lookup when the app has access to it. Wix can check the token even if the app cannot read those site details. The site owner email has its own permission and is unnecessary for setup. [Wix app instance guide](https://dev.wix.com/docs/api-reference/app-management/app-instance/get-app-instance)

Use `auth token create` to save an app token, `auth token set --file token.json` to import one, and `auth token status` to check the saved file. The legacy `auth token request` and `auth token refresh` commands are for apps still using Wix’s older custom sign-in. Keep codes and tokens local.

Put separate account settings in separate folders if you save tokens. Files in the same folder share `.state/token.json`. A token in `WIX_ACCESS_TOKEN` takes priority over a saved token. Environment variables take priority over settings in the file. `WIX_API_BASE_URL` defaults to `https://www.wixapis.com`, and `WIX_TIMEOUT_S` defaults to 30 seconds.

## Which access each command uses


| Command family | Required auth in this tool | Notes |
|---|---|---|
| `onboarding`, `runs *` | no live Wix auth for the local helper itself | local helper path only |
| `auth check` | a site app connection or an account API key and account ID | checks the app first when both paths are configured |
| `auth token create` | `WIX_APP_ID`, `WIX_APP_SECRET`, `WIX_INSTANCE_ID` | app-token client-credentials path |
| `auth token request` | `WIX_APP_ID`, `WIX_APP_SECRET`, plus an authorization code | deprecated custom-auth request flow for existing apps only |
| `auth token refresh` | `WIX_APP_ID`, `WIX_APP_SECRET`, plus a legacy refresh token | deprecated custom-auth refresh flow for existing apps only |
| `auth token inspect` | explicit token, `WIX_ACCESS_TOKEN`, or stored token file | token-info metadata check only |
| `auth token set`, `auth token status` | no live Wix auth for the local helper itself | local token file management only |
| `contacts`, `members`, `app-installations`, `app-instance`, `embedded-scripts`, `site-plugins`, `market-listing`, `editor-deep-link`, `branches`, `files`, `data-items`, `data-collections` | `WIX_APP_ID`, `WIX_APP_SECRET`, `WIX_INSTANCE_ID` or a valid app token | app/site context; installed-app scopes still apply |
| `contributors query`, `contributors remove`, `contributors change-role`, `contributors change-contributor-location` | `WIX_APP_ID`, `WIX_APP_SECRET`, `WIX_INSTANCE_ID` or a valid app token | site contributor boundary only; live-unverified; `Manage Contributors` for the main contributor methods |
| `sites`, `domains`, `domain-dns`, `connected-domains`, `site-actions`, `site-folders`, `projects create-project` | `WIX_API_KEY` plus `WIX_ACCOUNT_ID` | account-level boundary; some families remain beta-gated or live-unverified |
| `ai-credits get-balance` | `WIX_API_KEY` only | Developer Preview; live-unverified; no `wix-account-id` header |
| `accounts get`, `accounts list-child-accounts` | `WIX_API_KEY` plus `WIX_ACCOUNT_ID` | signed-contract gate in official Wix docs; live-unverified |


Wix uses the account ID header for account reads. The publish call uses the site ID header. Domain DNS reads in this tool cover getting or previewing a zone. Use the Wix editor for branch content. Specific command permissions and limits are in [Commands](command_reference.md) and [API coverage](api_coverage.md). [Wix REST authentication](https://dev.wix.com/docs/api-reference/articles/rest-authentication/rest-api-authentication)

## If connection fails

Check that the follow-up command uses the settings file you chose. For a refused site read, confirm the site, key or app, and the permission Wix requires for that command. To check a saved app token, run `auth token status` and `auth token inspect`. Keep private values out of debug output you share.
