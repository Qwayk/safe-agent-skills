# Authentication

Zendesk supports multiple auth approaches. This tool supports:

## Option A (recommended): API token auth (Basic)

Zendesk API token auth uses HTTP Basic auth with a username of `email/token` and a password of your API token.

Set these in your `.env` (gitignored):
- `ZENDESK_SUBDOMAIN` (or `ZENDESK_BASE_URL`)
- `ZENDESK_EMAIL`
- `ZENDESK_API_TOKEN`

Then run:

```bash
zendesk-api-tool --env-file .env --output json auth check
```

To validate the credentials against Zendesk (one safe read request), add `--live`:

```bash
zendesk-api-tool --env-file .env --output json --live auth check
```

## Option B (optional): OAuth access token (Bearer)

If your team uses OAuth, set:
- `ZENDESK_OAUTH_ACCESS_TOKEN`

When `ZENDESK_OAUTH_ACCESS_TOKEN` is set, it takes precedence over API token auth.

## Token helpers (local storage; never prints token values)

These commands store and inspect a token JSON file under `.state/` next to your `--env-file`:

```bash
zendesk-api-tool auth token set --file token.json
zendesk-api-tool auth token status
```

Notes:
- `.state/` is gitignored and must never be committed.
- The tool never prints token values to stdout/stderr.
