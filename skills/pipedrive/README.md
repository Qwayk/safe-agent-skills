# Pipedrive

Use Pipedrive to see which deals need attention, find a contact before adding a duplicate, or work out what has changed in a pipeline. Your agent can also pull notes and activities for a sales handoff.

Try asking, “Show me the open deals in this pipeline by stage,” or “Which activities are overdue for this owner?” The agent checks the connection and reads a few records first so you can see that it has the right account.

This tool reads CRM data. It can show a file’s type, size, or download link when Pipedrive provides them. Changes to CRM records and file downloads need a separate workflow.

## Start here first

[Connect your Pipedrive account](docs/onboarding.md), then use the [quickstart](docs/quickstart.md) for your first read.

## What your agent can do

- Review deals, leads, people, organizations, products, and activities.
- Find linked records, notes, and files for a sales review.
- Check pipelines, stages, fields, goals, roles, and permissions.

## What access this tool needs

Use a Pipedrive API token and your company name from the Pipedrive address, or the full address. Your account and token permissions determine which records you can see. Keep the token in your shell or local settings file.

## Install and first run

Ask your agent to install the `pipedrive` skill from `Qwayk/safe-agent-skills`, or run:

```bash
npx skills add Qwayk/safe-agent-skills@pipedrive -g -y
```

Then ask, “Check my Pipedrive connection and show me five open deals.”

## What it covers today

See the [API coverage table](docs/api_coverage.md) for the commands, routes, and reads that require account access. OAuth setup and changes to Pipedrive records are outside this tool.

## Helpful docs

- [Example requests](docs/use_cases.md)
- [Commands and flags](docs/command_reference.md)
- [How reads and file checks work](docs/safety_model.md)
- [What has been tested](docs/proof.md)
