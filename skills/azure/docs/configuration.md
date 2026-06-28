# Configuration

Configuration means the local settings the CLI reads before it contacts Azure. For Azure, configuration is the place where the tool learns which token, endpoint, subscription limits, resource group limits, and timeout rules it should use. Put private values in `.env` or the `--env-file`, and keep them out of chat and Git. A good first configuration check is: confirm the token setting exists, confirm the management endpoint is the expected Azure endpoint, add allowlists when the machine can reach more than one target, then run `auth check`.

## Files

- Create `.env` locally and keep it private.
- `.env` is private and must not be committed.
- `.state/token.json` is used by token helper commands.

## Required values

- `AZURE_API_TOKEN`

## Optional values

- `AZURE_MANAGEMENT_ENDPOINT` (default: `https://management.azure.com`)
- `AZURE_DATA_PLANE_ENDPOINT`
- `AZURE_TENANT_ID`
- `AZURE_ALLOWED_TENANTS`
- `AZURE_ALLOWED_SUBSCRIPTIONS`
- `AZURE_ALLOWED_RESOURCE_GROUPS`
- `AZURE_ALLOWED_LOCATIONS`
- `AZURE_ALLOWED_SERVICES`
- `AZURE_TIMEOUT_S`

## What each optional field does

- `AZURE_DATA_PLANE_ENDPOINT`: required for data-plane commands.
- `AZURE_TENANT_ID`: added to allowlist checks when tenant appears in path.
- `AZURE_ALLOWED_*`: comma-separated allowlists for safe service scoping.
- `AZURE_TIMEOUT_S`: request timeout in seconds.

## Environment precedence

When the same key is set in both sources, OS environment variables win over `.env` values.
