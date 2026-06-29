# Skill Wrapper

The source skill wrapper lives at `skills/n8n/SKILL.md`.

It should tell an agent to:

- start with onboarding or `auth check`
- use `api list` to discover the explicit official operation commands
- run reads directly when the request is read-only
- create dry-run plans for writes
- refuse live writes unless the user reviewed the plan and supplied the required apply approvals
- never reveal API keys, credential values, webhook secrets, execution payload secrets, or private customer data

The CLI enforces the safety gates. The skill wrapper should not ask an agent to call raw endpoints, private `/rest` endpoints, n8n CLI commands, node docs, MCP setup, templates, or user-created webhook URLs.
