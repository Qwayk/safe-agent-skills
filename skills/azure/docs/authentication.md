# Authentication

Authentication means proving to Azure that the request is allowed before the tool reads or changes anything. For Azure, authentication is meant to be local: the bearer token stays on this machine in `.env` or in the local token helper, and the agent should only see the connection result. The rule is simple: do not paste secrets into chat; keep bearer tokens, token JSON files, local `.env` values, and subscription-specific secret values private.

A good first auth check is: run `auth check`, confirm the token is present, confirm the intended management endpoint, note whether data-plane settings are needed, and stop if the target subscription or resource group is not the one you expected.

## Safe check

```bash
qwayk-azure-safe-agent-cli auth check
```

This checks local readiness. It does not prove every Azure permission and it does not make an Azure change.

## Configure `.env`

Set:

- `AZURE_API_TOKEN=<token>`
- `AZURE_MANAGEMENT_ENDPOINT=https://management.azure.com`

The token is used for Azure API calls once a command is executed. Keep the value out of chat and out of Git.

## Token helper

If you use a managed token JSON flow, store it with:

```bash
qwayk-azure-safe-agent-cli auth token set --file token.json
qwayk-azure-safe-agent-cli auth token status
```

The file is stored under `.state/token.json` next to your selected env file.

## Scope limits

- Reads can run with `AZURE_API_TOKEN` in place.
- Data-plane operations need `AZURE_DATA_PLANE_ENDPOINT`.
- `auth check` verifies local readiness and returns `live_verified=false` in this snapshot.
- `live_verified` still needs valid credentials against real targets.

## Safety reminders

- Never share real token values.
- Never paste `.env` or token JSON into chat.
