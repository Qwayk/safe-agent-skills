---
name: salesforce-platform
description: Read Salesforce records, fields, and bulk jobs. Preview and review supported changes before sending them.
---

# Salesforce

Use `qwayk-salesforce-platform-safe-agent-cli` with the named commands in the API coverage table. Start with onboarding and the printed `auth check` command if setup is missing. Keep secrets out of chat.

Read a few records first using `--output json`. Confirm the org before proposing changes. Preview writes, save the plan, and show the records, options, and recovery limit before asking for approval.

For approved changes, use `--apply --ack-no-snapshot` and any required `--yes`, `--ack-irreversible`, and `--plan-in` flags. Composite writes, bulk ingest changes, and password changes require `--plan-in`. If the connection or request changes, make a new plan. Permanent bulk deletes need explicit irreversible approval.

Read the receipt before reporting the result. For a bulk job that is still running, check its ID and read the failed rows when they are available. Use `--download-to` for large CSV results. See the setup, approval, and bulk jobs guides for details.
