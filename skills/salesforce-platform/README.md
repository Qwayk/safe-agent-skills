# Salesforce

Install slug: `salesforce-platform`

Use this skill when you want your AI agent to review Salesforce platform data, objects, metadata, and Bulk API work with preview before live changes.

Safe CLI for the official Salesforce Platform REST API and Bulk API 2.0.

This tool covers the core Salesforce Platform REST surface documented in the official REST API and Bulk API 2.0 guides, including versions, resources, limits, query, search, sObjects, list views, quick actions, composite, support knowledge, consent, process resources, survey translations, OpenAPI spec generation for sObjects (Beta), and `/services/data/vXX.X/jobs`.

Reads run directly. Write-capable commands produce review plans, and live write apply currently requires explicit no-snapshot approval before Salesforce HTTP when the command cannot save real before-state.

It intentionally does not expand into separate Salesforce product families when the official REST resource table points to other guides, such as Connect/Chatter, Analytics, Metadata, Tooling, Commerce, industry-specific `connect/*` families, or internal-only resources.

## For non-technical users: start here

- [What you can do](docs/use_cases.md)
- [Connect your org](docs/onboarding.md)
- [How live changes stay safer](docs/safety_model.md)

## For technical users: start here

- [Quickstart](docs/quickstart.md)
- [Command reference](docs/command_reference.md)
- [API coverage](docs/api_coverage.md)
- [Proof pack](docs/proof.md)

Minimal examples:

```bash
qwayk-salesforce-platform-safe-agent-cli --output json --version
qwayk-salesforce-platform-safe-agent-cli --output json auth token status
qwayk-salesforce-platform-safe-agent-cli --output json query run --soql "SELECT Id, Name FROM Account LIMIT 5"
```
