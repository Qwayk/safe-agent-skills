# Pipedrive

**Capability:** Read-only

Pipedrive is useful when sales data needs checking before someone changes a real CRM. This skill lets an agent inspect deals, people, organizations, activities, products, notes, pipelines, files, and other records so you can understand the account before making decisions elsewhere.

Use it for questions like "Which deals need review?", "Does this contact already exist?", "What activities are open?", or "Can you pull the records I need for a sales handoff?"

This skill needs a Pipedrive API token, but it is read-only by product choice. It cannot create, update, or delete records. File download checks use metadata-only behavior instead of pulling binary files by default.

A good first ask is: "Connect this Pipedrive read-only skill, check that the token works, and list the deals, people, and activities I should review first."

## Start here first

- Want ideas for real CRM review work? [What you can do with Pipedrive](docs/use_cases.md)
- Need setup? [Connect your Pipedrive account](docs/onboarding.md)
- Want the safety story first? [How this skill stays read-only](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Review deals, leads, people, organizations, products, and activities.
- Search for CRM records before a human or another tool changes anything.
- Pull notes, timelines, files metadata, filters, fields, pipelines, stages, goals, and permissions for review.
- Check whether a token works before using Pipedrive data in a bigger workflow.
- Export clear JSON that another agent can summarize or compare.

## What access this skill needs

- A Pipedrive API token.
- Your Pipedrive company domain or full base URL.
- A local `.env` file for those private values.

Do not paste the token into chat. Keep it in the local `.env` file.

## Install and first run

Install slug: `pipedrive`

Ask your agent to install the `pipedrive` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@pipedrive -g -y
```

Then try a safe first ask like:

```text
Connect this Pipedrive read-only skill, check that the token works, and list the deals, people, and activities I should review first.
```

## How this skill stays safe

- It is read-only by design.
- Only shipped `GET` commands are enabled.
- It does not include create, update, delete, plan, apply, or receipt flows.
- Write-style Pipedrive API operations are excluded on purpose.
- Secrets such as `PIPEDRIVE_API_TOKEN` are never printed.
- File download checks use metadata-only behavior and do not download binary content by default.

## What it covers today

This skill covers the documented public Pipedrive REST read surface that fits the API-token read-only product choice. It includes deal, person, organization, activity, product, file metadata, field, filter, pipeline, stage, goal, permission, project, and search-style reads.

## What happens before live changes

There are no live changes in this skill. It reads CRM data only. If you need to create, update, or delete records, use a different approved workflow.

## What proof it leaves behind

- Normal reads return one JSON object per command.
- The API coverage page maps the documented Pipedrive surface to shipped read commands or explicit exclusions.
- Tests check import behavior, redaction, command coverage, and read-only boundaries.
- The proof pack shows the validation commands and example outputs.

## Limits

- Read-only by product choice.
- Requires a valid Pipedrive API token.
- OAuth-only auth flow is outside this tool's scope.
- File downloads are metadata-only by default.
- It cannot create, update, delete, or repair CRM records.

## Helpful docs

- [Browse all Pipedrive docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
