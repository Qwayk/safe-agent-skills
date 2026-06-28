---
name: azure
description: Inspect Azure subscriptions, resources, access, exposure, and reviewed change plans with tenant and subscription guardrails.
---

# Skill: Azure

Use this skill when the user wants help with Azure subscriptions, resources, role assignments, storage or network exposure, cost-sensitive areas, or a careful Azure change plan.

Start with a safe read. A good first move is to confirm the tenant and subscription, list a small area the user can recognize, explain the result in normal words, and stop before any live change.

## Core Rules

- Never ask the user to paste Azure tokens, client secrets, tenant secrets, or `.env` contents into chat.
- Confirm the tenant and subscription before reading broad resources or planning changes.
- Prefer narrow reads first: resource groups, role assignments, storage exposure, network exposure, or cost-sensitive resources.
- Writes must start as reviewed plans and require the tool's approval flags before any live change.
- Use receipts, saved plans, and run history when the user needs proof of what happened.

## Good First Ask

```text
Show me what is running in this Azure subscription, flag public exposure and spend risks, and stop before any live change.
```

## Useful Follow-Ups

- "Check role assignments and tell me who has broad access."
- "Review storage accounts and public exposure risk."
- "Prepare a change plan for this resource and wait for approval."
