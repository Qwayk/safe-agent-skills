---
name: zapier
description: Use Zapier APIs through safe named commands for apps, actions, Zaps, action runs, authentications, trigger inboxes, promotions, and AI Actions.
---

# Zapier

Use this skill when a user wants an agent to inspect or prepare Zapier automation work through the official Zapier APIs.

Start with reads:

```bash
qwayk-zapier-safe-agent-cli --output json auth check
qwayk-zapier-safe-agent-cli --output json partner get-v2-apps
qwayk-zapier-safe-agent-cli --output json partner get-actions
```

Good tasks:

- list Zapier apps, categories, actions, inputs, choices, and output fields before choosing a workflow
- review Zaps, Zap runs, action runs, authentications, trigger inboxes, messages, promotions, and AI Actions metadata
- prepare a dry-run plan for creating a Zap, running an action, creating an authentication, changing an inbox, managing a promotion, or creating/executing an AI Action
- read a plan or receipt and explain what it means before anything live happens

Safety rules:

- Never ask the user to paste `ZAPIER_ACCESS_TOKEN`, `ZAPIER_CLIENT_SECRET`, `ZAPIER_JWT`, cookies, app connection secrets, or private action input data into chat.
- Use explicit commands only. Do not invent raw REST calls, arbitrary method/path requests, Zapier MCP setup commands, or Zapier Platform integration-builder commands.
- Reads may run directly.
- Writes and side effects must create a plan first.
- High-risk applies need `--apply --plan-in` plus `--yes`, `--ack-irreversible`, or `--ack-no-snapshot`.
- Save and review receipts after live applies.

Useful first ask:

Check my Zapier account, list apps/actions/Zaps you can see, and prepare a safe plan for the next change without applying it.
