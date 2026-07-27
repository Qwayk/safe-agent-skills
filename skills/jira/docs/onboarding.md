# Connect a Jira Cloud site

## Default: email and API token

The normal CLI setup uses the Jira site URL, your Atlassian account email, and an Atlassian API token through Basic authentication.

```bash
.venv/bin/jira-safe onboarding
```

Fill these values in the local `.env` file:

```dotenv
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=you@example.com
JIRA_API_TOKEN=your-local-token
JIRA_TIMEOUT_S=30
```

Do not paste the token into chat or commit `.env`.

Use the site root exactly. The CLI refuses another HTTPS host, an extra `/rest/...` path, or a custom port before it can send credentials.

Check the connection with a read of the current Jira user:

```bash
.venv/bin/jira-safe --env-file .env auth check
```

## Optional: OAuth 2.0 bearer token

For an existing official 3LO setup, run `jira-safe onboarding --auth-mode oauth` and set:

```dotenv
JIRA_BASE_URL=https://api.atlassian.com/ex/jira/YOUR_CLOUD_ID
JIRA_OAUTH_ACCESS_TOKEN=your-local-access-token
```

The tool does not create an OAuth app, open a browser authorization flow, refresh tokens, or accept Atlassian terms. When both auth methods are present, the bearer token takes priority.

The OAuth base must use this exact gateway shape with one cloud ID and no extra path.

## Permissions still apply

Jira returns only the projects, issues, settings, and administration surfaces allowed for the connected user and app scopes. A successful auth check does not prove every command is permitted. Forge-only and Connect-only commands refuse before any request because these credentials cannot call them.
