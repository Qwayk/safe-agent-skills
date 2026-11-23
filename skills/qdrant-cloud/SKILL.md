---
name: qdrant-cloud
description: Check Qdrant Cloud accounts, clusters, backups, access and costs. Prepare reviewed changes and check recovery results with qdrant-cloud-api-tool.
---

# Qdrant Cloud

Start with `qdrant-cloud-api-tool onboarding` if setup is needed, then `qdrant-cloud-api-tool --output json auth check`. Use the settings path from onboarding throughout the work. Keep keys and settings contents out of chat.

Get approval for live access before using `--live`. Start by listing accounts, then find the exact cluster or backup the user asked about. Price estimates can run as reads.

Before changing anything, save a dry-run plan and show the target, request, effect and recovery options. Send an approved change with `--live --apply --plan-in plan.json`. Add the required flags for spending, irreversible changes and changes with no saved before-state. An in-place restore needs both irreversible and spending approval because it can discard newer data and bring back the old cluster size.

Check the receipt after sending a change. For restores, check the new entry for the backup in restore history before reporting success. If the result is uncertain, check Qdrant before trying again.
