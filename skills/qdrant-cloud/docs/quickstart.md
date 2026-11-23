# List accounts, clusters and backups

[Install the CLI and set up your key](onboarding.md). If you used the virtual environment from setup, activate it before running the examples:

```bash
source .venv/bin/activate
```

When live access is approved, list the accounts that your key can see:

```bash
qdrant-cloud-api-tool --output json --env-file .env --live account-v1 list-accounts
```

Use the account ID from the result for the next reads:

```bash
qdrant-cloud-api-tool --output json --env-file .env --live cluster-v1 list-clusters --account-id ACCOUNT_ID
qdrant-cloud-api-tool --output json --env-file .env --live cluster-backup-v1 list-backups --account-id ACCOUNT_ID
qdrant-cloud-api-tool --output json --env-file .env --live cluster-backup-v1 list-backup-schedules --account-id ACCOUNT_ID
```

If setup used a different file, replace `.env` with that path in each command. [Example commands for quotes and changes](command_reference.md)
