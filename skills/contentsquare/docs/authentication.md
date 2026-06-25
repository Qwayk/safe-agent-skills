# Authentication

Authentication means proving to Contentsquare that this CLI is allowed to read or change the server-side API areas you ask about.

For this skill, authentication is meant to be local: use Contentsquare server-to-server OAuth credentials, keep the client secret on this machine, and do not paste secrets into chat. In plain English, the CLI uses a client id and client secret from the Contentsquare console to get a short-lived access token.

Authentication is only one part of setup. The credential also needs access to the right API family, and account-level credentials may need a project id before Contentsquare issues the token for the right project.

A good first auth check is: confirm the local OAuth fields are present, get one token without printing secrets, name the API endpoint Contentsquare returns, then run one small read before planning any change.

## Normal path

Run:

```bash
contentsquare-safe-cli auth check
```

`auth check` sends the documented token request body with `client_id`, `client_secret`, `grant_type: client_credentials`, and a default `scope` of `data-export`. You can check a different official scope with `--scope`, for example:

```bash
contentsquare-safe-cli auth check --scope metrics
```

For normal API commands, the CLI chooses the documented OAuth scope for the command family:

- Data Export uses `data-export`
- Metrics uses `metrics`
- Enrichment uses `enrichment`
- Speed Analysis Lab uses `speed-analysis`

Use `--scope` only when you intentionally need an official combined scope such as `data-export metrics`. Do not combine `enrichment` with other scopes, because Contentsquare documents that `enrichment` must stand alone. The CLI refuses combined overrides such as `--scope "data-export enrichment"`.

If your OAuth credentials are account-level, set the target project with:

```bash
CONTENTSQUARE_PROJECT_ID=42
```

You can also override it for one run with:

```bash
contentsquare-safe-cli --oauth-project-id 42 auth check
```

To inspect the credential identity when your account supports it:

```bash
contentsquare-safe-cli auth me
```

`auth me` sends the documented `client_id` and `client_secret` body to `/v1/oauth/me`; it does not first request a bearer token for that identity check.

The CLI never prints the client secret or access token.
