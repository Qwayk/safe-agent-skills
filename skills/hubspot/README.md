# HubSpot

Install slug: `hubspot`

Use this skill when you want your AI agent to review HubSpot CRM records and plan careful CRM changes with preview before live work.

It covers these HubSpot CRM areas:
- objects and search
- associations, labels, and limits
- properties and property groups
- owners
- pipelines and stages
- custom object schemas
- imports and exports
- object-library enablement checks

## For non-technical users: start here

- [What you can do](docs/use_cases.md)
- [Connect your account](docs/onboarding.md)
- [How live changes stay safer](docs/safety_model.md)

Ask your AI agent to:
- connect a HubSpot private app token in `.env`
- run a safe connection check
- read records, properties, and pipelines first
- show a dry-run before any write
- for writes that still lack command-specific snapshots, live `--apply` needs explicit no-snapshot approval before HubSpot HTTP

## For technical users: start here

- [Quickstart](docs/quickstart.md)
- [Command reference](docs/command_reference.md)
- [API coverage](docs/api_coverage.md)
- [Proof pack](docs/proof.md)
- [Docs index](docs/README.md)

Minimal commands:

```bash
qwayk-hubspot-safe-agent-cli --output json --version
qwayk-hubspot-safe-agent-cli onboarding
qwayk-hubspot-safe-agent-cli auth check
```

## Proof pack

- [Proof pack](docs/proof.md)
- [API coverage](docs/api_coverage.md)
- [Examples](docs/examples/)
