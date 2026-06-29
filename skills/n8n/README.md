# n8n

**Capability:** Review and manage n8n workflows, executions, credentials, users, projects, folders, tags, variables, data tables, source-control pulls, and package operations through the official public REST API.

n8n runs business automations that can touch CRMs, payment tools, support desks, spreadsheets, databases, and internal systems. This skill lets an agent inspect that automation layer, find failed runs, review workflow state, prepare careful changes, and manage admin resources without guessing private endpoints or inventing API calls.

The safe path matters because an n8n change can trigger connected systems or expose credential structure. This CLI only exposes named operations from the official public API inventory. Reads can run directly; writes create a reviewed plan first, require live approval, redact secrets, and save receipts when applied.

A useful first ask is: "Check my n8n connection, list the workflow and execution commands you can use safely, and stop before any live change."

## Start here first

- Need setup? [Connect n8n](docs/onboarding.md)
- Want a first safe result? [Run the quickstart](docs/quickstart.md)
- Want examples of real work? [See n8n use cases](docs/use_cases.md)

## What this skill helps with

- Review workflows, versions, tags, folders, and project placement before editing anything.
- Find recent executions, failed runs, stopped runs, and execution tags.
- Inspect credential metadata and credential schemas without printing credential secrets.
- Prepare workflow, credential, variable, data table, project, folder, user, package, and source-control changes as plans.
- Leave local plans, receipts, and run history for risky work so a user can inspect what happened.

## Why this skill is different

A generic API helper may turn a natural-language request into a raw HTTP call. That is too loose for n8n, where one workflow or credential mistake can affect production automations.

This skill keeps the agent inside the official n8n public REST API. It uses generated named commands from the pinned OpenAPI files, requires exact target IDs for targeted operations, redacts API keys and credential data, and refuses live writes unless the reviewed plan matches the current command, base URL, API key fingerprint, target, and body.

## What access this skill needs

- `N8N_BASE_URL`: your n8n API root, ending with `/api/v1`.
- `N8N_API_KEY`: an n8n API key. Use the narrowest scoped key that can do the job.

For safe review work, a read-focused key is enough. For workflow, credential, user, project, package, source-control, variable, folder, data-table, or execution changes, the key needs the matching n8n scope. Never paste the key into chat.

## Install and first run

Install slug: `n8n`

Ask your agent to install the `n8n` skill from `Qwayk/safe-agent-skills`.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@n8n -g -y
```

Then try:

```text
Connect this n8n skill, run a safe auth check, list the workflow and execution read commands, and stop before any write.
```

## How this skill stays safe

- Reads use official named commands and do not change n8n.
- Writes generate a dry-run plan before live apply.
- Live writes require `--apply --yes --plan-in`.
- No-snapshot writes also require `--ack-no-snapshot`.
- Destructive, permission, production-risk, credential, package, and source-control changes also require `--ack-irreversible`.
- Secrets and credential data are redacted from output, plans, receipts, and audit logs.

## What it covers today

The pinned official inventory covers 80 public REST API operations across audit, community packages, credentials, data tables, discovery, executions, folders, insights, n8n packages, projects, source control, tags, users, variables, and workflows.

Private `/rest` UI endpoints, n8n CLI commands, node documentation, MCP setup, templates, and user-created webhook APIs are outside this tool's boundary.

## What happens before live changes

The agent first produces a plan that names the operation, target IDs, query, redacted body, scope, risk reasons, snapshot status, and verification plan. Applying must reuse that saved plan. If the command, target, body, base URL, or API key fingerprint changed after review, the CLI refuses.

## Limits

- Live behavior is not verified in this repo because no real n8n credentials are stored here.
- Some write operations cannot guarantee a before-state snapshot from the public API, so apply needs explicit no-snapshot approval.
- Credential values are intentionally not surfaced. The public API returns credential metadata and schemas, not secret values.
- The beta n8n package operations are included because they are present in the official public API spec, but they may require instance-side enablement.

## Helpful docs

- [Browse all docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [API coverage](docs/api_coverage.md)
- [Safety model](docs/safety_model.md)
- [Proof and verification](docs/proof.md)
