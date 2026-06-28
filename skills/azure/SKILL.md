# azure-safe-cli

**Capability:** Safe Azure reads and controlled writes for agents.

## Install

Install this skill from `Qwayk/safe-agent-skills` and use it with:

```bash
qwayk-azure-safe-agent-cli
```

## Start here first

Use this exact request:

```text
Use this skill to run safe Azure reads first. Give me a short summary and stop before any live changes.
```

## What this skill is for

- Read Azure resources safely from generated ARM/data-plane commands.
- Prepare preview plans before write operations.
- Run write operations only with explicit confirmation and risk acknowledgments.

## Safety guardrails

- Read-first behavior is available for non-destructive inspection.
- Write actions require all of: `--plan-in`, `--apply`, and `--yes`.
- `--ack-no-snapshot` and `--ack-irreversible` are required for matching risk classes.
- Live Azure execution is confirmed only with real credentials and target access.

## Useful prompts

- "Run a read-only check for this subscription and summarize issues." 
- "Generate a write plan for these changes and wait for approval." 
- "Review the plan output and confirm if any irreversible action is present."
