# Authentication

This tool supports two auth modes for the Google Search Console API:

## 1) Installed-app OAuth (recommended)

You create an OAuth client in Google Cloud, download the client secrets JSON, then run an interactive login once.

1) Put the client secrets JSON path in your `.env`:

```bash
GSC_OAUTH_CLIENT_SECRETS_FILE=/absolute/path/to/client_secrets.json
```

2) Run login (opens a browser flow and stores local credentials):

```bash
gsc-api-tool auth login
```

3) Check status (safe; never prints token values):

```bash
gsc-api-tool auth check
```

Credentials are stored under `.state/gsc_oauth_credentials.json` next to your `--env-file`.

Important:
- Never commit `.state/`
- Never print token values (stdout/stderr/audit logs)

## 2) Service account (optional)

If your setup uses a service account, put the JSON path in your `.env`:

```bash
GSC_SERVICE_ACCOUNT_FILE=/absolute/path/to/service_account.json
```

Important:
- The service account email must be granted access to the target Search Console property. In practice, add it as a user (verified owner/user) in Search Console for that property, otherwise calls will fail with a permission error.

Then run:

```bash
gsc-api-tool auth check
```
