# Asana

The Asana API tool for agents helps you understand what is happening across your workspaces and keep projects moving.

You can ask your agent to review a project, find overdue or blocked work, check goals and portfolios, prepare tasks or status updates, inspect team setup, and explain what needs attention.

For example: "Show me the workspaces I can access," "Review this project for overdue work and blockers," "Prepare a status update from the latest tasks," or "Check whether this team and project are set up correctly."

The agent starts by reading Asana and explaining what it found. If you ask it to create, update, delete, upload, send, administer, or automate something, it saves the proposed change and waits for your approval. Changes with a wider or harder-to-reverse effect require a stronger confirmation.

## Start here first

Ask your agent:

```text
Connect to Asana, show me the workspaces I can access, and explain what you can review without changing anything.
```

This confirms the connection and gives you a useful first result before you choose a project, team, portfolio, or goal to review.

## What your agent can do

- Review workspaces, teams, projects, portfolios, goals, tasks, sections, and status updates.
- Find work that is late, blocked, unassigned, or missing important details.
- Prepare new tasks, projects, goals, updates, comments, memberships, custom fields, and other supported changes for approval.
- Work with time tracking, attachments, webhooks, rules, exports, audit logs, and Asana's newer administration and automation features when your account has access.
- Follow asynchronous exports and jobs without calling a newly accepted request complete too early.

See [realistic asks](docs/use_cases.md) for more ways to use the tool.

## What happens before live changes

Reads can run immediately after the agent confirms the target and connection.

Every write begins as a saved plan. The plan names the command, target, proposed request, available before-state, expected result, and verification method. It is tied to a private key in the tool's local state, so an edited or unsigned plan—and a plan moved without its matching local state—cannot be applied as if it were the one you reviewed. Nothing is sent to Asana until you approve that exact plan.

Deletes, wider changes, administration, memberships, visible collaboration, files, webhooks, exports, rules, agents, budgets, rates, approvals, and similar account-impacting actions require an additional acknowledgement. When Asana does not provide a reliable before-state or readback, the agent says so and asks you to accept that limit instead of promising rollback or verification it cannot provide.

Read [how approval and receipts work](docs/safety_model.md).

## What access this tool needs

The simplest connection uses an Asana personal access token in the `ASANA_ACCESS_TOKEN` environment variable. OAuth access tokens and service-account tokens can use the same bearer-token transport when the chosen operation and Asana account allow them.

The tool does not register OAuth apps, exchange or refresh tokens, create service accounts, or manage SCIM. Keep tokens in your environment or `.env` file and never paste them into chat.

## Install and first run

Install slug: `asana`

Ask your agent to install the `asana` skill from `Qwayk/safe-agent-skills`. If your host cannot install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@asana -g -y
```

Then follow the [short setup guide](docs/onboarding.md) and get a first read with the [Quickstart](docs/quickstart.md).

## What it covers today

The tool ships 248 fixed commands for the official Asana REST specification pinned in this source. That includes normal project work plus access-gated areas such as organization exports, audit logs, AI Studio usage, agents, roles, rules, budgets, rates, and other newer REST families.

The official `POST /batch` operation is listed but intentionally not callable because it would allow arbitrary relative API paths. App Components and SCIM are separate Asana surfaces and are outside this tool. See the [complete operation ledger](docs/api_coverage.md).

The ledger also marks Asana's Project Briefs family as developer preview and the older Project Statuses family as deprecated, so an agent can prefer the current stable path when one exists.

## Limits

- No live Asana credential or account was used during this source build. Mocked behavior, safety, generation, and package checks are documented in [proof and verification](docs/proof.md).
- Account plan, token type, OAuth scopes, service-account status, and permissions still decide which fixed commands Asana will allow.
- The tool does not provide a raw API request, arbitrary batch, SDK pass-through, browser automation, App Component hosting, or SCIM provisioning path.
- Rollback is not promised. A before-state helps review and recovery, but only an operation with a proved restore path can be described as reversible.

## Helpful docs

- [Choose the right guide](docs/README.md)
- [Set up the connection](docs/onboarding.md)
- [Get the first useful result](docs/quickstart.md)
- [Browse exact commands](docs/command_reference.md)
- [Understand approvals and receipts](docs/safety_model.md)
- [Review proof and unverified limits](docs/proof.md)
- [Inspect complete API coverage](docs/api_coverage.md)
