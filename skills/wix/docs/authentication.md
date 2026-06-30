# Authentication

Authentication means proving to the service that this tool is allowed to read or change your account.

Wix supports two official auth paths in this tool:

- App-token path: `WIX_APP_ID`, `WIX_APP_SECRET`, and `WIX_INSTANCE_ID` (OAuth client credentials).
- Account-level API-key path: `WIX_API_KEY` and `WIX_ACCOUNT_ID` for most account-level APIs like `sites`, `domains`, `domain-dns`, `connected-domains`, `site-actions`, `projects`, and `site-folders`.
- Site contributor commands in this boundary use the app-token path too.
- Branch metadata commands in this boundary use the app-token path too and need `Manage Site Branches`.
- AI Credits in this boundary uses `WIX_API_KEY` only and no `wix-account-id` header.

For this boundary, `sites query`, `sites count`, `domains`, `domain-dns`, `connected-domains`, `site-folders`, and the shipped `site-actions bulk-delete`, `site-actions duplicate`, `site-actions publish`, and `projects create-project` commands use the Wix API-key credential family.
`ai-credits get-balance` uses the API-key path too, but it only sends `Authorization` in this tool.
`contributors query`, `contributors remove`, and `contributors change-role` use Wix app or Wix user identity for the installed site in context and need the official `Manage Contributors` permission.
`embedded-scripts get` and `embedded-scripts embed` also use the app-token path in this boundary, while the official docs currently disagree on whether the family is Wix-app-only or also allows Wix user identity on the method page.
`branches get-default`, `branches get`, and `branches query` use the same app-token path in this boundary. The Branches API manages branch metadata only; editing branch content itself is only possible in the editor.
`market-listing search` uses the app-token path in this boundary and is marked Developer Preview in the official method docs.
`editor-deep-link create` uses the same app-token path in this boundary and returns a URL instead of mutating the site directly.
For publish specifically, the live write request uses `wix-site-id` instead of `wix-account-id`.
For project creation specifically, the tool uses `POST /funnel/projects/v1/create` and account headers as below.
`.env` is your private local settings file.

## Auth family matrix

| Command family | Required auth in this tool | Notes |
|---|---|---|
| `onboarding`, `runs *` | no live Wix auth for the local helper itself | local helper path only |
| `auth check` | whichever auth values are configured | read-only validation of the active auth path |
| `auth token create` | `WIX_APP_ID`, `WIX_APP_SECRET`, `WIX_INSTANCE_ID` | app-token client-credentials path |
| `auth token request` | `WIX_APP_ID`, `WIX_APP_SECRET`, plus an authorization code | deprecated custom-auth request flow for existing apps only |
| `auth token refresh` | `WIX_APP_ID`, `WIX_APP_SECRET`, plus a legacy refresh token | deprecated custom-auth refresh flow for existing apps only |
| `auth token inspect` | explicit token, `WIX_ACCESS_TOKEN`, or stored token file | token-info metadata check only |
| `auth token set`, `auth token status` | no live Wix auth for the local helper itself | local token file management only |
| `contacts`, `members`, `app-installations`, `app-instance`, `embedded-scripts`, `site-plugins`, `market-listing`, `editor-deep-link`, `branches`, `files`, `data-items`, `data-collections` | `WIX_APP_ID`, `WIX_APP_SECRET`, `WIX_INSTANCE_ID` or valid `WIX_ACCESS_TOKEN` | app/site context; installed-app scopes still apply |
| `contributors query`, `contributors remove`, `contributors change-role`, `contributors change-contributor-location` | `WIX_APP_ID`, `WIX_APP_SECRET`, `WIX_INSTANCE_ID` or valid `WIX_ACCESS_TOKEN` | site contributor boundary only; live-unverified; `Manage Contributors` for the main contributor methods |
| `sites`, `domains`, `domain-dns`, `connected-domains`, `site-actions`, `site-folders`, `projects create-project` | `WIX_API_KEY` plus `WIX_ACCOUNT_ID` | account-level boundary; some families remain beta-gated or live-unverified |
| `ai-credits get-balance` | `WIX_API_KEY` only | Developer Preview; live-unverified; no `wix-account-id` header |
| `accounts get`, `accounts list-child-accounts` | `WIX_API_KEY` plus `WIX_ACCOUNT_ID` | signed-contract gate in official Wix docs; live-unverified |

## 1) App-token foundation (official Wix flow)

1. Put your Wix app values in `.env`:
   - `WIX_APP_ID`
   - `WIX_APP_SECRET`
   - `WIX_INSTANCE_ID`
2. Run:

```bash
wix-safe-agent-cli auth token create
```

`auth token create` calls `POST /oauth2/token` with `grant_type=client_credentials`,
`client_id`, `client_secret`, and `instance_id`. The tool stores the returned token in `.state/token.json` and keeps it redacted in output.

If you have an older Wix app that still uses the deprecated legacy custom-auth install handshake, you can exchange the temporary authorization code from the Wix redirect:

```bash
wix-safe-agent-cli auth token request --code AUTHORIZATION-CODE
```

If you have an older Wix app that still uses the deprecated legacy custom-auth refresh flow, you can refresh from the saved local token file:

```bash
wix-safe-agent-cli auth token refresh
```

You can also pass the refresh token directly:

```bash
wix-safe-agent-cli auth token refresh --refresh-token REFRESH-TOKEN
```

`auth token request` calls `POST /oauth/access` with `grant_type=authorization_code`, `client_id`, `client_secret`, and the temporary authorization code from the Wix install redirect. It stores the returned access and refresh token JSON safely under `.state/token.json`.
`auth token refresh` calls `POST /oauth/access/` with `grant_type=refresh_token`, `client_id`, `client_secret`, and the refresh token. Wix marks these legacy endpoints deprecated for new apps, so they are only here for older custom-auth app setups that still depend on them.

## 2) Manual token mode (optional)

You can use a manual token for testing or one-off runs by setting `WIX_ACCESS_TOKEN` in `.env`.
To store any token JSON you get from another flow:

```bash
wix-safe-agent-cli auth token set --file token.json
```

3. Inspect what token-info says about your token:

```bash
wix-safe-agent-cli auth token inspect
```

It prints only safe metadata like `active`, `subject_type`, `subject_id`, `client_id`, `site_id`, `instance_id`, `exp`, `iat`.

Use `wix-safe-agent-cli auth token status` to confirm the local file is present and ready.

The same token path is used by `contributors query`, `contributors remove`, `contributors change-role`, and `contributors change-contributor-location`.
These commands are for customer access on one site, not account team-member management.
`contributors query`, `contributors remove`, and `contributors change-role` need the Wix `Manage Contributors` permission on the current site context.
For `contributors remove`, this tool also requires `--site-id`, reuses `wix-site-id` on the preflight/readback requests, and only applies after `--apply --yes --ack-irreversible`.
For `contributors change-role`, this tool also requires `--site-id`, reuses `wix-site-id` on the preflight/write/readback requests, requires explicit role GUIDs in `--role-ids-json`, and applies only after `--apply --yes`.
For `contributors change-contributor-location`, this tool also requires `--site-id`, reuses `wix-site-id` on the preflight/write/readback requests, requires explicit location GUIDs in `--location-ids-json`, and applies only after `--apply --yes`.
The nearby `Get Roles Info` discovery API remains beta-gated in Wix docs and is intentionally out of scope for this boundary, so callers must supply role GUIDs directly.
Official Wix docs say location IDs come from the Locations API.
The official `change-contributor-location` method page currently lists permission `SITE_ROLES.CHANGE_LOCATION` with scope text `View SEO Settings: SCOPE.PROMOTE.VIEW-SEO`, and this tool keeps that wording explicit instead of normalizing it.
`embedded-scripts get` and `embedded-scripts embed` use the same token path. The Embedded Scripts family intro currently says to authenticate as a Wix App, but the method pages say Wix app or Wix user identity. This tool keeps that mismatch explicit and stays live-unverified for that reason.
`embedded-scripts embed` is a reviewed-plan write in this CLI, so live apply only runs after a saved dry-run plan is reviewed and passed back with `--plan-in --apply --yes`.
`market-listing search` uses the same app-token path and returns published listings only. It defaults to English and keeps the result limit explicit in the command itself.
`editor-deep-link create` uses the same token path, returns a deep link URL, and keeps the official legacy-custom-element-only limit explicit.

## 3) AI Credits auth path (API-key only in this boundary)

For `ai-credits get-balance`, keep this value in `.env`:

- `WIX_API_KEY`

The tool sends:

- `Authorization: <API_KEY>`
- no `wix-account-id` header

Wix's AI Credits intro says the response can vary by caller access: account-level access returns the account balance, while site-level access scopes the balance to the site in context. This boundary ships the API-key path only and treats the response as account-level coverage.
This command is read-only in this tool.

## 4) Sites and other account-level auth paths (account-level API key)

For most account-level commands in this boundary, keep these values in `.env`:

- `WIX_API_KEY`
- `WIX_ACCOUNT_ID`

The tool sends:
- `Authorization: <API_KEY>`
- `wix-account-id: <ACCOUNT_ID>`

For Wix API-key commands, official docs also say you should send either `wix-account-id` or `wix-site-id`, and not both.
`site-actions publish` uses the `wix-site-id` header, not the account header.
For `domains check-availability` and `domains suggest`, the generic API-key docs define `Authorization` plus `wix-account-id` for account-level REST calls. The Domain Search method pages also add a note that these calls do not use the standard auth header wording; this boundary follows the generic API-key contract and keeps the surface explicit.
For `domain-dns get-zone` and `domain-dns preview-zone`, Wix docs also say the family requires an account-level API key and not the standard auth header wording. This boundary keeps those commands read-only and explicit on `Authorization` plus `wix-account-id`.
Wix docs also say Domain DNS keeps up to 50 values per record type, and write methods stay for later because real DNS updates are limited to external domains connected by nameservers to a Wix site.
For `connected-domains list`, `connected-domains get`, `connected-domains get-setup-info`, `connected-domains create`, and `connected-domains delete`, the REST method pages also use `Authorization` plus `wix-account-id` in their examples. SDK examples still show `ApiKeyStrategy`, so this boundary keeps that mismatch documented and stays on the explicit account-header REST contract.
For `connected-domains create`, this tool also requires `--site-id` and sends `wix-site-id` on the live write request so the target site is deterministic and verifiable. Wix docs say the site header is optional, but this tool keeps it explicit.
Connected-domain writes also need the official `DOMAINS.MANAGE_CONNECTED_DOMAINS` permission, can have Premium-plan or registrar-side setup gates in real flows, and do not prove DNS propagation is complete on the first response.

`projects create-project` adds the following boundary guardrails:

- `--name` is a required input in this boundary.
- `--type` is accepted as `WIX` only.
- Optional inputs are `--template-id`, `--folder-id`, and `--apps-json`.
- Success is treated as verified only when the response includes `project.metaSiteId` and `project.siteId`.
- There is no project read command in this boundary, so verification is response-only.

Publish uses a different endpoint:
- `POST /site-publisher/v1/site/publish`
- Success body: `{}` (empty object)

Example:

```bash
wix-safe-agent-cli sites query
```

```bash
wix-safe-agent-cli ai-credits get-balance
```

```bash
wix-safe-agent-cli contributors query
```

```bash
wix-safe-agent-cli contributors query --policy-ids-json '["6600344420111308827"]'
```

```bash
wix-safe-agent-cli --plan-out plan.json contributors remove --account-id "<account_id>" --site-id "<site_id>"
```

```bash
wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json contributors remove --account-id "<account_id>" --site-id "<site_id>" --receipt-out receipt.json
```

```bash
wix-safe-agent-cli --plan-out plan.json contributors change-role --account-id "<account_id>" --site-id "<site_id>" --role-ids-json '["<role_guid>"]'
```

```bash
wix-safe-agent-cli --apply --yes --plan-in plan.json contributors change-role --account-id "<account_id>" --site-id "<site_id>" --role-ids-json '["<role_guid>"]' --receipt-out receipt.json
```

```bash
wix-safe-agent-cli --plan-out plan.json contributors change-contributor-location --account-id "<account_id>" --site-id "<site_id>" --location-ids-json '["<location_guid>"]'
```

```bash
wix-safe-agent-cli --apply --yes --plan-in plan.json contributors change-contributor-location --account-id "<account_id>" --site-id "<site_id>" --location-ids-json '["<location_guid>"]' --receipt-out receipt.json
```

```bash
wix-safe-agent-cli domains check-availability --domain "<domain.tld>"
```

```bash
wix-safe-agent-cli domains suggest --query "<search words>" --tlds-json '["com","net"]'
```

```bash
wix-safe-agent-cli domain-dns get-zone --domain-name "<domain.tld>"
```

```bash
wix-safe-agent-cli domain-dns preview-zone --domain-name "<domain.tld>"
```

```bash
wix-safe-agent-cli connected-domains list --limit 25
```

```bash
wix-safe-agent-cli --plan-out plan.json connected-domains create --domain "<domain.tld>" --site-id "<site_id>"
```

```bash
wix-safe-agent-cli --apply --yes --plan-in plan.json connected-domains create --domain "<domain.tld>" --site-id "<site_id>" --receipt-out receipt.json
```

```bash
wix-safe-agent-cli --plan-out plan.json connected-domains delete --connected-domain-id "<domain.tld>"
```

```bash
wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json connected-domains delete --connected-domain-id "<domain.tld>" --receipt-out receipt.json
```

```bash
wix-safe-agent-cli --plan-out plan.json site-actions bulk-delete --site-ids-json '["<site_id>"]'
```

```bash
wix-safe-agent-cli --plan-out plan.json site-actions publish --site-id "<site_id>"
```

```bash
wix-safe-agent-cli --plan-out plan.json site-actions duplicate --source-site-id "<source_site_id>" --site-display-name "<new site name>"
```

```bash
wix-safe-agent-cli --plan-out plan.json projects create-project --name "<project name>" --type WIX
```

```bash
wix-safe-agent-cli --apply --yes --plan-in plan.json projects create-project --name "<project name>" --type WIX --receipt-out receipt.json
```

```bash
wix-safe-agent-cli --plan-out plan.json projects create-project --name "<project name>" --type WIX --template-id "<template_id>" --apps-json '[{"appDefId":"appId"}]'
```

Tokens are stored under `.state/token.json` next to your `--env-file`.

## Safety reminders

- Never commit `.state/`.
- Never print tokens in logs.
- Never paste keys, tokens, or OAuth files into chat.
