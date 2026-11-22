---
name: hubspot
description: Search HubSpot CRM records, check pipelines and fields, prepare imports and exports, and review supported changes before sending them.
---

# HubSpot

Use `qwayk-hubspot-safe-agent-cli` to work with HubSpot CRM records and their settings. See the command reference and API coverage in the skill’s `docs/` folder for the exact commands and what they support.

1. If setup is missing, run `qwayk-hubspot-safe-agent-cli onboarding` and follow the printed `auth check` command. Keep tokens and token files out of chat.
2. Start with a small read. Show the records or settings you found. If HubSpot denies a read, explain which permission or account feature is missing when the reply tells you.
3. For a change, run the command without `--apply`. Save the plan with `--plan-out` for imports, bulk changes, GDPR deletion, and custom schema hard deletion. Show the exact request and recovery limit and get approval before sending it.
4. Use `--apply --ack-no-snapshot` only after approval. Add `--yes`, `--ack-irreversible`, and `--plan-in` as required. If the connection or request changes, show a fresh plan and ask again. The tool cannot undo changes automatically.
5. Read the receipt or refusal. For an import that is still running, use the printed status and error commands. For a bulk change with errors, check what succeeded before you consider a retry. See `.state/runs/` for the saved records.
