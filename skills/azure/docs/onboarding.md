# Connect your Azure account

Set up the account connection first, then ask the agent for one safe check before any live change.

Keep the setup files private. Do not paste Azure bearer tokens, local `.env` values, token JSON files, or subscription secrets into chat.

Before you start, decide which Azure subscription or resource group the first check should inspect. If this machine can reach more than one subscription, use the allowlist settings so the tool refuses the wrong target.

## Step 1: Prepare environment file

1. In the tool folder, copy `examples/example.env` to `.env`.
2. Keep `.env` private and never paste token values in chat.
3. Fill required values:

- `AZURE_API_TOKEN`
- `AZURE_MANAGEMENT_ENDPOINT` (default is `https://management.azure.com`)

## Step 2: Confirm data-plane readiness if needed

If your planned work is data-plane command, also set:

- `AZURE_DATA_PLANE_ENDPOINT`

Without this, data-plane commands return:
`Missing AZURE_DATA_PLANE_ENDPOINT for data-plane command`.

## Step 3: What to ask your AI agent (examples)

- "Check which Azure subscription this token can read and stop before any change."
- "List resource groups and flag public or expensive resources."
- "Prepare a plan for this change, but do not apply it."

## Step 4: Optional scoping controls

Set any of these to limit where the CLI can run:

- `AZURE_ALLOWED_TENANTS`
- `AZURE_ALLOWED_SUBSCRIPTIONS`
- `AZURE_ALLOWED_RESOURCE_GROUPS`
- `AZURE_ALLOWED_LOCATIONS`
- `AZURE_ALLOWED_SERVICES`

## Step 5: Check the tool can start

Run:

```bash
qwayk-azure-safe-agent-cli onboarding
qwayk-azure-safe-agent-cli auth check
```

The tool writes no Azure changes for this step. It confirms the local config shape and token presence.

## Step 6: Try read-only discovery

```bash
qwayk-azure-safe-agent-cli inventory summary
```

If this works, you can start with safe read commands for your target service.

## What success looks like

You are ready when:

- `auth check` returns a structured result.
- `inventory summary` shows the pinned Azure scope.
- You can run at least one read command with your `--input-json` payload.

## If something fails first

- Confirm `.env` values and no extra quotes around tokens.
- Confirm `AZURE_MANAGEMENT_ENDPOINT` and, if needed, `AZURE_DATA_PLANE_ENDPOINT` are correct.
- Run `qwayk-azure-safe-agent-cli auth check`, then open [troubleshooting](troubleshooting.md) for common refusal messages.
