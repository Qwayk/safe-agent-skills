# Run your first Azure read

Connect through [the setup guide](onboarding.md). Check the tenant and subscription before listing resource groups.

```bash
qwayk-azure-safe-agent-cli --output json auth check
```

Save this as `read.json` and replace `SUBSCRIPTION_ID`:

```json
{
  "path": {
    "subscriptionId": "SUBSCRIPTION_ID"
  }
}
```

```bash
qwayk-azure-safe-agent-cli resources-management resourcegroups_list_2025-04-01_148560 --input-json read.json
```

Say which subscription you checked and whether the list matched what you expected. If the read is blocked, check the subscription, role and limits. [Find more commands](command_reference.md)

To check the installed package without contacting Azure:

```bash
qwayk-azure-safe-agent-cli --output json --version
qwayk-azure-safe-agent-cli inventory summary
```

For a change, [prepare a plan and wait for approval](safety_model.md).
