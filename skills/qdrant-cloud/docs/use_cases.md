# What you can do with Qdrant Cloud

Use this page when you want ideas for real Qdrant Cloud work to hand to your agent.
If you need setup first, start with [Connect your Qdrant Cloud account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## A good first ask

"Check the Qdrant Cloud skill is configured, list my accounts and clusters, and tell me what is safe to review before we plan any changes."

## Common Qdrant Cloud jobs

### Account and cluster review

- "List my accounts, clusters, and releases so I can review what is running."
- "Show me packages, regions, and quotas before we plan a cluster change."
- "Export a clean inventory of clusters, backups, and backup schedules."

### Backup and recovery review

- "List my backups and backup schedules, then tell me which recovery options exist."
- "Prepare a restore-backup plan for this backup without changing anything yet."
- "Show me whether create-cluster-from-backup is the safer path for this recovery job."

### Access, keys, and permissions

- "Review management keys, database API keys, roles, and account members."
- "List effective permissions for this account before we change access."
- "Check user roles for this account and point out anything surprising."

### Billing and monitoring

- "Show me invoices, discounts, payment methods, and monthly metering for this account."
- "Pull cluster summary metrics, usage metrics, or logs for this cluster."
- "Export cluster events so I can review recent incidents or changes."

### Careful change planning

- "Plan this cluster change first and show me exactly what needs approval."
- "Preview a payment or billing change and tell me if it needs spend approval."
- "Show the refusal path first when a write still has no saved before-state."

## Why this skill is useful

- It gives your agent a safer front door to the Qdrant Cloud control plane than raw API guessing.
- It lets you review infrastructure, access, backups, and billing in one place.
- It keeps ordinary writes in plan-first mode when there is no saved before-state or provider backup yet.

## What you should expect from the agent

For normal review work, the agent should gather the right reads and summarize what matters.

For change work, the agent should:

1. show the dry-run plan first
2. explain whether the change needs `--live`, `--apply`, or extra approval flags
3. tell you when no-snapshot approval is still required
4. keep provider backup and restore workflows separate from ordinary writes
