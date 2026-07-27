# Jira Cloud

The Jira Cloud API tool for agents helps you understand and manage the work inside your Jira site.

You can ask your agent to find issues, check projects, review boards and backlogs, inspect sprint work, add comments, prepare issue changes, or help with Jira administration.

For example: "Show me overdue bugs in this project," "What is still open in the current sprint?", "Prepare a new issue for this customer problem," or "Check which workflow and permission scheme this project uses."

The agent looks at Jira first and explains what it found. When you ask for a live change, it saves a plan showing the exact Jira site, command, target, and request. Nothing changes until you approve that saved plan. Bigger changes, such as deleting issues, moving sprint work, changing permissions, or editing workflows, need an extra warning and approval.

## Start here first

- Want to try one useful check? [List the Jira projects you can browse](docs/quickstart.md).
- Need to connect your site? [Set up Jira access](docs/onboarding.md).
- Looking for ideas? [See what you can ask your agent](docs/use_cases.md).
- Want to understand approvals? [Read how live changes are protected](docs/safety_model.md).

## What your agent can do

The tool covers the Jira Cloud Platform and Jira Software APIs. That includes everyday issue work, project settings, users and groups, comments and worklogs, dashboards and filters, fields, workflows and schemes, boards, backlogs, epics, and sprints.

It can also inspect the exact fixed command before running it, so your agent does not need a generic request tool or an arbitrary URL escape hatch.

## What happens before live changes

Checks that only read Jira can run after the site and required inputs are validated.

For a write, the agent creates a local plan first. Updates and deletions use a matching Jira read to save before-state when the selected operation has a reliable read at the same path. Other writes show a clear no-snapshot warning and require you to accept that limit. Every approved apply writes a redacted local receipt and attempts a Jira readback when one is available.

The tool does not promise rollback. A receipt records what was requested and what Jira returned; it is not an automatic undo button.

## What access this tool needs

The normal setup uses your `https://your-domain.atlassian.net` Jira Cloud site URL, Atlassian account email, and an Atlassian API token. OAuth 2.0 bearer tokens use only `https://api.atlassian.com/ex/jira/<cloudId>`. Other hosts and paths are refused before credentials can be sent.

Your Jira permissions still decide what the tool can see or change. Forge-only and Connect-only operations fail closed because ordinary API-token and OAuth access cannot call them. Never paste a token into chat; keep it in the local `.env` file.

Every write first saves a private, locally signed plan. Apply reconstructs the request from the selected fixed command and refuses edited request or safety fields before HTTP. Of the 360 writes, 277 destructive, bulk, administrative, permission, membership, workflow, scheme, webhook, attachment, notification, movement, or ranking operations require the extra `--ack-high-risk` approval.

## Install and first run

Install slug: `jira`

Ask your agent to install the `jira` skill from `Qwayk/safe-agent-skills`. If your host cannot install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@jira -g -y
```

Then ask:

```text
Connect to my Jira Cloud site, check the account without changing anything, and list the projects I can browse.
```

## What it covers today

The pinned boundary contains 616 Jira Cloud Platform operations and 105 Jira Software operations. Each of the 721 official method-and-path rows has a fixed command or an exact gated, preview, deprecated, or product-boundary classification.

See [the full operation ledger](docs/api_coverage.md) for every command and [the command guide](docs/command_reference.md) for exact syntax.

## Limits

This tool covers Jira Cloud Platform REST API v3 and Jira Software Cloud REST API. Jira Service Management, Assets, Operations, Confluence, Atlassian organization administration outside the selected descriptions, Jira Data Center and Server, and undocumented endpoints are outside this product.

The source build uses the official pinned descriptions, mocked HTTP behavior, and installed-package checks. It has not used a real Jira credential or made a live Jira request, so real account permissions, tenant settings, rate limits, and provider responses remain unverified.

## Helpful docs

- [Browse the docs by what you need](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Set up Jira access](docs/onboarding.md)
- [Command guide](docs/command_reference.md)
- [Safety and approvals](docs/safety_model.md)
- [Proof and unverified limits](docs/proof.md)
- [Full API coverage](docs/api_coverage.md)
