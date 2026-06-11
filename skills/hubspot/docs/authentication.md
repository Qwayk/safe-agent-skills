# Authentication

This tool supports two auth inputs.

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
