# Qdrant Cloud commands

See [the full command list](official_commands_v1.txt) for the shipped operations. Run a command with `--help` to see its required IDs. Put shared flags such as `--env-file` before the command group.

## Read account data or get a price

```bash
qdrant-cloud-api-tool --output json --live account-v1 list-accounts
qdrant-cloud-api-tool --output json --live account-v1 get-account --account-id ACCOUNT_ID
qdrant-cloud-api-tool --output json --live booking-v1 get-quote --account-id ACCOUNT_ID --request-json quote.json
```

For a GET request, `--request-json` supplies filters and other query parameters. For other HTTP methods, it supplies the request body. Qdrant requires the relevant cluster or backup permission to return a price quote.

## Plan and apply a change

```bash
qdrant-cloud-api-tool --output json --plan-out plan.json account-v1 create-account --request-json request.json
qdrant-cloud-api-tool --output json --live --apply --plan-in plan.json --ack-no-snapshot --receipt-out receipt.json account-v1 create-account --request-json request.json
```

Use the second command after reviewing and approving the saved plan. Add the flags listed in [the approval guide](safety_model.md) for the action you are taking.

## Restore a backup

```bash
qdrant-cloud-api-tool --output json --plan-out restore.json cluster-backup-v1 restore-backup --account-id ACCOUNT_ID --backup-id BACKUP_ID
qdrant-cloud-api-tool --output json --live --apply --yes --ack-irreversible --ack-spend-money --plan-in restore.json --receipt-out receipt.json cluster-backup-v1 restore-backup --account-id ACCOUNT_ID --backup-id BACKUP_ID
qdrant-cloud-api-tool --output json --live cluster-backup-v1 list-backup-restores --account-id ACCOUNT_ID
```

Check the receipt and match the new restore record by backup and time.

## Find plans and receipts

Write commands save run history under `.state/runs/` beside the selected settings file.

- `qdrant-cloud-api-tool runs list --limit 20`
- `qdrant-cloud-api-tool runs show --run-id RUN_ID`

Use `--run-id` to name the run, `--artifacts-dir` to choose where to put its files, or `--no-artifacts` to skip the automatic run files. The saved review plan is still required when applying a write.
