# Onboarding

This tool runs locally and talks to your Salesforce org over the official Platform REST API.

Keep the main rule simple: store secrets only on your machine, never in chat.

## Step 1: Create `.env`

1. Copy `.env.example` to `.env`.
2. Set `SALESFORCE_INSTANCE_URL` to your org URL.
3. Leave `SALESFORCE_API_VERSION=67.0` unless you have a specific reason to change it.

## Step 2: Get an access token

Use one of these paths:

1. Put `SALESFORCE_ACCESS_TOKEN` in `.env`.
2. Or keep the token outside `.env` and store it with:

```bash
qwayk-salesforce-platform-safe-agent-cli auth token set --file token.json
```

Use an External Client App or an existing Connected App that can issue a Salesforce access token for REST API use. Some orgs restrict new Connected App creation, so an admin may need to provide the approved app or token flow.

## Step 3: Check the connection

```bash
qwayk-salesforce-platform-safe-agent-cli --output json auth check
```

If this works, the tool is ready for real read commands and dry-run write plans. Write apply currently requires explicit no-snapshot approval before Salesforce HTTP when before-state capture support is not available.

## Step 4: First safe requests

- Read:
  - `qwayk-salesforce-platform-safe-agent-cli --output json resources list`
  - `qwayk-salesforce-platform-safe-agent-cli --output json query run --soql "SELECT Id, Name FROM Account LIMIT 5"`
- Dry-run write:
  - `qwayk-salesforce-platform-safe-agent-cli --output json composite execute --body-file composite.json`
