# What you can do with Qdrant Cloud

Qdrant Cloud is useful when a team needs to understand vector-search infrastructure before changing clusters, backups, access, billing, or recovery settings.

Ask the agent for the control-plane work an infrastructure owner checks before touching live search systems: what clusters exist, what regions and packages are in use, what backups are available, who has access, what it costs, and what recovery path is safest.

## Good questions to ask

- "Which accounts, clusters, and releases exist right now?"
- "Which regions, packages, quotas, and cluster settings should we review?"
- "Can you export a clean inventory of clusters, backups, and backup schedules?"
- "Which backup or restore options exist for this cluster?"
- "Can you prepare a restore-backup plan without changing anything?"
- "Who has access through members, roles, permissions, and API keys?"
- "What billing, invoice, discount, payment, or metering data should we review?"
- "Can you pull cluster metrics, logs, events, or usage before we plan a change?"

## Everyday work this helps with

### Cluster inventory

The agent can list accounts, clusters, releases, packages, regions, quotas, and serverless or hybrid resources so you know what is running before a change.

### Backup and recovery review

Ask the agent to list backups, backup schedules, restore jobs, and create-cluster-from-backup options. It should keep provider backup and restore work separate from ordinary changes.

### Access and key review

The agent can review management keys, database API keys, account members, user roles, and effective permissions so risky access changes are visible before they happen.

### Billing and monitoring checks

For finance or reliability review, ask for invoices, payment methods, discounts, monthly metering, cluster summary metrics, usage metrics, logs, and events.

## What the agent should show you

- The account, cluster, backup, role, key, invoice, metric, or resource it checked.
- The date range or metric scope for monitoring and billing reads.
- A clear summary of infrastructure, access, cost, or recovery risk.
- A review plan before cluster, backup schedule, payment, IAM, hybrid, or serverless changes.
- Whether a change needs live access, apply approval, spend approval, or no-snapshot approval.
- Receipts or run history for approved provider backup, restore, or other change work.

## Good first path

Start with: "Check the Qdrant Cloud skill is configured, list my accounts and clusters, and tell me what is safe to review before we plan changes."

After that, ask one practical follow-up, such as: "Show backup and restore options for this cluster" or "Review account members and API keys before we change access."
