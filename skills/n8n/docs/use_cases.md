# n8n Use Cases

Use this skill when the agent needs to inspect or carefully manage n8n through the public REST API.

## Good first asks

- "Check my n8n connection and show me what can be reviewed safely."
- "List workflows and tell me which ones are active."
- "Find failed executions from the last page of results and summarize what needs attention."
- "Show credential metadata and schemas without revealing secret values."
- "Prepare a plan to move a workflow to a project, but do not apply it."

## Review jobs

- Workflows: list, retrieve, inspect versions, tags, folders, archive state, and activation state.
- Executions: list, retrieve, retry, stop, delete, and manage execution tags.
- Credentials: list metadata, get schemas, test, create, update, delete, and transfer with secret redaction.
- Admin resources: users, roles, projects, folders, variables, tags, data tables, and source-control pull.
- Packages: community packages and beta n8n package import/export when enabled on the instance.

## Change jobs

The agent can prepare plans for workflow updates, activation changes, credential changes, user and project changes, data table edits, source-control pulls, and package operations.

Live changes are intentionally slower. The CLI checks the reviewed plan, target, body, base URL, and API key fingerprint before it applies anything.

## Not for

- Private n8n editor `/rest` endpoints.
- Browsing workflow templates.
- Node documentation or node package authoring.
- Running arbitrary webhook URLs created by a workflow.
- Replacing n8n's own CLI.
