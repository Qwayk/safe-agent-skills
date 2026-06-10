# Authentication

This tool expects a Salesforce access token plus the org base URL.

## What you need

- `SALESFORCE_INSTANCE_URL`
- one access token source:
  - `SALESFORCE_ACCESS_TOKEN` in `.env`, or
  - `.state/token.json` written by `auth token set`

The tool does not create the OAuth session for you. It assumes you already have a working Salesforce External Client App or Connected App flow outside the CLI.

## Recommended token flow

1. Keep the org URL in `.env`.
2. Keep the access token out of chat.
3. If you have a token JSON file from your OAuth flow, store it locally:

```bash
qwayk-salesforce-platform-safe-agent-cli auth token set --file token.json
```

4. Check safe token status:

```bash
qwayk-salesforce-platform-safe-agent-cli auth token status
```

5. Verify the token against the live org limits endpoint:

```bash
qwayk-salesforce-platform-safe-agent-cli auth check
```

Token files live under `.state/token.json` next to the `--env-file`.
