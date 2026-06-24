# Jobs and batches

This AWS tool does not ship a separate background worker. Each command runs in one process so the account, region, operation, input, plan, and receipt stay easy to review.

If you need batch work, keep the loop explicit and use named AWS service commands one target at a time. That keeps identity checks, account and region allowlists, dry-run plans, acknowledgement flags, and receipts attached to each action instead of hiding them inside a broad batch runner.

For write-capable commands, local proof still lives under `.state/runs/`. Review those run folders before repeating a change across many resources.
