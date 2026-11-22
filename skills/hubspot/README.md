# HubSpot

Use HubSpot to find contacts and companies, check deals and tickets, and see how records are linked. Your agent can also review pipelines and fields, start an export, or show you what an import would change.

Try asking, “Which contacts have no owner?” or “Show me the open deals in this stage and how long they’ve been there.” The agent checks the connection and starts with a small read so you can confirm it has the right account and records.

If you ask for a change, the agent shows you the proposed records, fields, and files first. You decide whether to go ahead.

## Start here first

[Connect your HubSpot account](docs/onboarding.md), then use the [quickstart](docs/quickstart.md) for your first read.

## What your agent can do

- Find and review contacts, companies, deals, tickets, and other records your account supports.
- Check owners, pipelines, fields, and links between records.
- Review custom record types, prepare imports, and start or check export jobs.

## What happens before live changes

Your agent runs a preview and asks you to approve it. Imports, bulk changes, and certain permanent deletions require a saved plan. The tool checks that the connection and request still match it before sending the change. Changing the token, records, or import file means reviewing a new plan. [Approval rules and receipts](docs/safety_model.md)

The tool cannot save a copy of the old data or undo changes for you. Each live write requires you to accept that limit.

## What access this tool needs

Use a HubSpot private app token or an existing OAuth token file. HubSpot decides which actions are available based on the token’s permissions, your account plan, and the record types you’ve turned on. Keep tokens and private files on your computer. [Setup and troubleshooting](docs/onboarding.md)

## Install and first run

Ask your agent to install the `hubspot` skill from `Qwayk/safe-agent-skills`, or run:

```bash
npx skills add Qwayk/safe-agent-skills@hubspot -g -y
```

Then ask, “Check my HubSpot connection and show me ten contacts with no owner.”

## What it covers today

See the [full command list](docs/api_coverage.md) for the HubSpot endpoints, supported actions, and required approvals.

## Limits

HubSpot processes imports and exports in the background. Use the job ID to check progress. HubSpot says completed export download links expire after five minutes.

## Helpful docs

- [Example requests](docs/use_cases.md)
- [Commands and flags](docs/command_reference.md)
- [What has been tested](docs/proof.md)
- [Example output](docs/examples/)
