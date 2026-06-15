# Authentication

Salesforce authentication is the part that decides which account the agent can see and which actions it can even plan. Keep the credential setup local, use the safe check first, and do not paste secrets or token files into chat.

For objects, records, metadata, jobs, and platform API operations, the exact credential path is listed below. When OAuth is required, it means the user approves access through the provider instead of copying a long-lived password into the tool.

A good first auth check is: "Check which Salesforce credential path is configured, run the safe auth check, and stop before any token write or live account change."

## Authentication notes

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
