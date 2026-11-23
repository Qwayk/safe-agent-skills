# Set up Azure access

Pick the Azure subscription you want to inspect. Sign in on your machine and check the tenant and subscription before making a service request.

## Connect with Azure CLI

```bash
az login
az account show --subscription SUBSCRIPTION_ID
qwayk-azure-safe-agent-cli --output json auth check
```

Set `AZURE_SUBSCRIPTION_ID` in your local settings if you want the tool to use that subscription by default. A command that names an exact subscription uses that value within the configured limits. In the absence of either selection, the tool can use the subscription Azure CLI shows as current. The tool checks the Azure CLI sign-in and requests an access token for the selected service. It does not change the Azure CLI default subscription. [Azure CLI account commands](https://learn.microsoft.com/cli/azure/account)

For a setup that already uses tokens, keep `AZURE_API_TOKEN` in private settings or import a local JSON file. The import supports the `access_token` and `accessToken` fields. Settings tokens take priority over the imported token in `.state/token.json` next to the settings file. If there is no local token, the tool uses Azure CLI.

```bash
qwayk-azure-safe-agent-cli auth token set --file token.json
qwayk-azure-safe-agent-cli auth token status
```

Keep access tokens, refresh tokens, and settings files out of Git and chat. Replace an expired local token or sign in again. [Azure authentication](https://learn.microsoft.com/cli/azure/authenticate-azure-cli)

## Choose a settings file

The setup helper can create a private file for optional settings. It keeps a file that already exists and shows the next command with the same path. Add `--no-write-env` for instructions without creating a file.

```bash
qwayk-azure-safe-agent-cli --env-file "azure settings.env" onboarding
```

| Setting | What it does |
|---|---|
| `AZURE_MANAGEMENT_ENDPOINT` | Sets the Resource Manager endpoint. The default is `https://management.azure.com`. Match it to your Azure cloud. |
| `AZURE_SUBSCRIPTION_ID`, `AZURE_TENANT_ID` | Pick a default subscription and check the expected tenant. |
| `AZURE_DATA_PLANE_ENDPOINT` | Names the HTTPS service endpoint for direct service requests, such as a particular Key Vault. |
| `AZURE_DATA_PLANE_RESOURCE` | Names the Microsoft Entra token resource when Azure CLI needs a token for a service. The tool knows the standard Key Vault and Storage resources. |
| `AZURE_ALLOWED_TENANTS`, `AZURE_ALLOWED_SUBSCRIPTIONS`, `AZURE_ALLOWED_RESOURCE_GROUPS`, `AZURE_ALLOWED_LOCATIONS`, `AZURE_ALLOWED_SERVICES` | Limit the targets or service commands you want this tool to use. Use commas between entries. |
| `AZURE_TIMEOUT_S` | Sets the request timeout in seconds. The default is 30. |

Environment variables take priority over values in the file. A direct service request needs a token for that service. For example, Key Vault uses `https://vault.azure.net`, while Resource Manager has its own token resource. [Key Vault authentication](https://learn.microsoft.com/azure/key-vault/authentication-requests-and-responses)

## Check access and fix problems

Read the connection result from `auth check`. Check the tenant and subscription shown when available, then [read one resource you recognize](quickstart.md). The resource read tells you whether that account can use the service you selected.

| What you see | What to check |
|---|---|
| Azure CLI sign-in or subscription error | Run `az login`, then check the intended subscription with `az account show`. |
| Wrong tenant or subscription | Check the active account, the exact resource ID and the local settings. |
| Access denied | Check the role’s permission for that service and resource. |
| A service token or endpoint error | Check which HTTPS endpoint the command uses and which service the token is for. |
| A target is outside a configured list | Confirm the subscription, resource group, location and service before changing your settings. |
| A write was refused or its result is unclear | Follow [the approval and receipt steps](safety_model.md). |
