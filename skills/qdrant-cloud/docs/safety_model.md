# Approve a change or restore

Use `--live` only after the user approves access to Qdrant. Listing resources and getting a price quote can run with live access. Every change starts with a dry run. Save its plan with `--plan-out` and show the user the exact target, request, likely effect and recovery options.

## Send the approved request

Use `--live --apply --plan-in plan.json` with the same API address, key, target and request. Make and review a new plan if any of those changed, if the plan was made without a key, or if it predates these checks.

- Use `--yes` for destructive changes and actions that can affect spending.
- Use `--ack-irreversible` for deletes and restores over an existing cluster.
- Use `--ack-spend-money` for payment or billing changes and actions that can affect costs. Examples include creating or resizing clusters, taking backups or setting up a schedule, and restoring a cluster to capacity it had at backup time. Show the relevant cost before approval.
- Use `--ack-no-snapshot` for ordinary changes where the tool has no saved before-state or backup to restore. The three Qdrant recovery commands use their own backup and restore steps.

## Review a backup or restore

Check the account, cluster, backup ID and backup time. Restoring over a cluster takes it offline and can discard data written after the backup. A new cluster from a backup gives you a separate copy and can add cost. [Qdrant’s backup guide](https://qdrant.tech/documentation/cloud/backups/)

After sending a restore, use the receipt’s `list-backup-restores` command and look for a new entry for that backup around the request time. Check whether Qdrant reports that the job is running, succeeded or failed. A reply to the request alone only shows what Qdrant accepted. If the reply was lost or an error occurred, check the result in Qdrant before trying the change again. The tool sends writes once per apply.

Keep plans, receipts, request files and run history private. Check what changed and get approval for any separate recovery action.
