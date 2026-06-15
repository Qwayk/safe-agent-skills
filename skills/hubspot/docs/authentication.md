# Authentication

HubSpot authentication is the part that decides which account the agent can see and which actions it can even plan. Keep the credential setup local, use the safe check first, and do not paste secrets or token files into chat.

For CRM records, owners, pipelines, marketing data, and account resources, the exact credential path is listed below. When OAuth is required, it means the user approves access through the provider instead of copying a long-lived password into the tool.

A good first auth check is: "Check which HubSpot credential path is configured, run the safe auth check, and stop before any token write or live account change."

## 1) HubSpot private app token (default)

Set `HUBSPOT_ACCESS_TOKEN` in your `.env` file.

```bash
HUBSPOT_ACCESS_TOKEN=your_private_app_token
```

Then run:

```bash
qwayk-hubspot-safe-agent-cli --output json auth check
```

Use this path for new setups. It is the default in the shipped tool.

## 2) Stored OAuth token JSON (optional)

If you already have OAuth token JSON, store it once:

```bash
qwayk-hubspot-safe-agent-cli auth token set --file token.json
```

Then check it:

```bash
qwayk-hubspot-safe-agent-cli auth token status
```

If `HUBSPOT_ACCESS_TOKEN` is empty, CLI auth uses the stored token if it is valid.

## Security rules

- Never paste token values into chat.
- Never print token values in logs or output.
