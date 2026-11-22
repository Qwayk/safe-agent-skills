# Salesforce

Use Salesforce to check accounts and opportunities, see which fields are available, or find out why a bulk job failed. Your agent can also prepare changes to records and show you what Salesforce would receive.

Try asking, “Show which opportunities changed stage this week,” or “Check this import and tell me which rows failed.” The agent starts with a small read so you can confirm it has the right Salesforce org.

If you ask for a change, review the records, fields, and request options first. The tool can save that preview and check it again before sending the change.

## Start here first

[Connect your Salesforce org](docs/onboarding.md), then [run a first read](docs/quickstart.md).

## What your agent can do

- Review records, fields, layouts, approval information, list views, and limits.
- Run SOQL, the Salesforce query language, to find specific records.
- Check bulk jobs and download results. Preview grouped changes and imports before approving them.

## What happens before live changes

Grouped writes, bulk imports, and password changes require a saved plan. The tool checks that the request and connection match it. When a change has no saved copy to restore, you must approve that limit. Permanent bulk deletes need separate acknowledgment. [Approval steps](docs/safety_model.md)

## What access this tool needs

Use a Salesforce access token and your org address. The token’s permissions and the features available in your org determine what you can read or change. [Account setup](docs/onboarding.md)

## Install and first run

Ask your agent to install the `salesforce-platform` skill from `Qwayk/safe-agent-skills`, or run:

```bash
npx skills add Qwayk/safe-agent-skills@salesforce-platform -g -y
```

Then ask, “Check my Salesforce connection and show me five accounts.”

## What it covers today

See [API coverage](docs/api_coverage.md) for the Salesforce REST and Bulk API 2.0 commands.

## Limits

Salesforce can accept a job while processing is still pending. Check the job ID and failed rows before treating an import as finished. The tool has no automatic undo or saved copy of the old records. [Bulk jobs](docs/jobs_and_batches.md)

## Helpful docs

- [Example requests](docs/use_cases.md)
- [Commands and flags](docs/command_reference.md)
- [What has been tested](docs/proof.md)
- [All Salesforce guides](docs/README.md)
