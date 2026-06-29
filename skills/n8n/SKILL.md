---
name: n8n
description: Use when an agent needs to inspect or carefully manage n8n through the official public REST API: workflows, executions, credentials, tags, variables, users, projects, folders, data tables, audit, insights, source control, community packages, and beta n8n package operations.
---

# n8n

Use this skill when the user wants help with n8n through the public REST API.

Good tasks:

- check the n8n API connection
- list or inspect workflows, executions, tags, folders, projects, variables, or data tables
- review credential metadata and schemas without revealing credential values
- prepare workflow, credential, user, project, source-control, package, variable, folder, or data-table changes
- explain recent execution problems before changing anything

Do not use this skill for private `/rest` editor endpoints, n8n CLI commands, node docs, MCP setup, workflow templates, or user-created webhook URLs.

## Start Safely

1. Read `README.md`, `docs/quickstart.md`, `docs/safety_model.md`, and `docs/command_reference.md`.
2. If setup may be missing, run:

```bash
n8n-safe-agent-cli onboarding
```

3. For a real account, run the safe read-only check:

```bash
n8n-safe-agent-cli --env-file .env auth check
```

4. To see the official command surface:

```bash
n8n-safe-agent-cli api list
```

## Command Rules

Use only explicit `api <family> <command>` commands from `api list` or `docs/command_reference.md`.

Never invent raw URLs, private endpoints, or generic HTTP calls.

Pass operation input with:

- `--path-param name=value`
- `--query name=value`
- `--body-json ...`
- `--body-file file.json`

## Writes

Reads may run directly.

Writes must start with a dry-run plan:

```bash
n8n-safe-agent-cli --env-file .env --plan-out plan.json api <family> <command> ...
```

Do not apply until the user has reviewed the plan.

Live apply must reuse the reviewed plan:

```bash
n8n-safe-agent-cli --env-file .env --apply --yes --plan-in plan.json api <family> <command> ...
```

If the plan says no before-state snapshot was verified, require:

```bash
--ack-no-snapshot
```

For destructive, permission, credential, package, source-control, execution, workflow activation, or production-risk changes, require:

```bash
--ack-irreversible
```

## Secrets

Never print, paste, summarize, or store API keys, authorization headers, credential values, webhook secrets, execution payload secrets, passwords, tokens, or private customer data.

If a command output includes credential-like fields, treat them as sensitive even if n8n's API usually omits secret values.

## Stop Conditions

Stop and explain the refusal when:

- `.env` or required auth is missing
- the target ID is unclear
- the requested operation is outside the official public API boundary
- the user asks for a live write without a reviewed plan
- the reviewed plan does not match the command being applied
- the user asks to reveal secrets or credential data
