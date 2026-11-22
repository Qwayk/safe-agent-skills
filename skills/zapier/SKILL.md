---
name: zapier
description: Check Zapier apps, actions, Zaps, runs, trigger inboxes, and promotions. Prepare changes and check their results after approval.
---

# Zapier

Use this skill to review a Zapier integration or prepare a change to a Zap, action run, inbox, or promotion. Start by checking the profile and listing apps.

```bash
qwayk-zapier-safe-agent-cli --output json auth check
qwayk-zapier-safe-agent-cli --output json partner get-v2-apps
```

If the user chose a settings file, keep `--env-file` in every command. Keep tokens, credentials, and private request data out of chat. The profile check confirms access to that profile. Check a specific read when the task needs Partner or White Label access.

Use the named commands. Before making a change, save a plan, show what would happen, and wait for approval. Apply the same request with `--apply`, `--plan-in`, and the right acknowledgement. When applying without a copy of the previous state, show that risk and use `--ack-no-snapshot` after approval. If the CLI returns `refused=true`, explain the reason before trying again.

Check the receipt after an approved change. An accepted action run may still be waiting. Use the receipt’s follow-up command to check the run. If the answer is unclear, check Zapier before sending the action again.

Zapier retired AI Actions. Point users to [Zapier MCP](https://docs.zapier.com/mcp/quickstart) for that work. Use Zapier’s browser consent flow for account setup and `trigger-inbox listTriggerInboxMessages` for a one-time inbox check.
